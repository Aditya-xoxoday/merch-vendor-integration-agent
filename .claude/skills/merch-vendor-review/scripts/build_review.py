#!/usr/bin/env python3
"""
Build the merchandise vendor review: answers "can we integrate?" and "does the API work?".

Usage:
    python3 build_review.py <test_cases.json> <answers.json> <output.xlsx> [--md <report.md>]

<answers.json>:
    {
      "vendor_name": "Example Vendor",
      "reviewed_on": "2026-10-18",
      "doc_sources": ["https://vendor.example/docs"],
      "answers": {
        "ORD-02": {"provided": "Yes", "details": "Response field orders_id",
                   "live": "Pass", "live_notes": "200, orders_id present"},
        "WHK-05": {"provided": "No", "details": "Signature header is mandatory"}
      },
      "status_map": {"in production": "CONFIRMED", "dispatched": "SHIPPED"}
    }

    provided: Yes / No / Not available / NA / Open      (missing = "Not available")
      Yes            docs confirm it; details MUST say where (endpoint, field, short paraphrase)
      No             docs confirm it is absent; details MUST say where
      Not available  docs are silent (the default; never guessed)
      NA             does not apply to this vendor
      Open           partly answered; needs the vendor to confirm
    live: Pass / Fail / Not run / NA    (sandbox result, only for checks marked Live)
    status_map: vendor status -> PENDING / CONFIRMED / SHIPPED / DELIVERED / CANCELED / RETURNED

Decision (from the Must-have checks only; Important and Nice-to-have never block):
    No             a must-have is missing, confirmed absent, or failed on sandbox
    Likely yes     no must-have is missing, but some are only partly answered (vendor to confirm)
    Yes on paper   every must-have is confirmed in the docs; sandbox test still to run
    Yes            every must-have is confirmed and passed on sandbox

Exits 2 on invalid input (unknown id, bad value, Yes/No without evidence, bad status target).
"""
import json
import sys
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

NAVY, GREY, WHITE = "1F3864", "F2F2F2", "FFFFFF"
GREEN, AMBER, RED = "C6E0B4", "FFE699", "F8CBAD"
PROVIDED = ("Yes", "No", "Not available", "NA", "Open")
LIVE = ("Pass", "Fail", "Not run", "NA")
DELIVERY_STATUSES = ("PENDING", "CONFIRMED", "SHIPPED", "DELIVERED", "CANCELED", "RETURNED")
NEEDS = ("Must-have", "Important", "Nice-to-have")
FILL = {"Yes": GREEN, "Pass": GREEN, "Met": GREEN, "No": RED, "Fail": RED, "Missing": RED,
        "Open": AMBER, "Not available": AMBER, "Not run": AMBER}


def font(**kw):
    return Font(name="Arial", **kw)


def border():
    s = Side(style="thin", color="D9D9D9")
    return Border(left=s, right=s, top=s, bottom=s)


def has_live(t):
    return "Live" in t["verify"]


# ---------- validation ----------

def validate(tests, payload):
    errors, warnings = [], []
    by_id = {t["id"]: t for t in tests}
    for tid, a in payload.get("answers", {}).items():
        if tid not in by_id:
            errors.append(f"{tid}: unknown check id")
            continue
        p = a.get("provided", "Not available")
        if p not in PROVIDED:
            errors.append(f"{tid}: provided '{p}' not in {PROVIDED}")
        if p in ("Yes", "No") and not a.get("details", "").strip():
            errors.append(f"{tid}: '{p}' needs evidence in details (never assume)")
        if p == "Open" and not a.get("details", "").strip():
            warnings.append(f"{tid}: Open without a note on what is unclear")
        live = a.get("live")
        if live is not None:
            if live not in LIVE:
                errors.append(f"{tid}: live '{live}' not in {LIVE}")
            elif not has_live(by_id[tid]) and live != "NA":
                warnings.append(f"{tid}: sandbox result given for a docs-only check")
    for status, target in payload.get("status_map", {}).items():
        if target not in DELIVERY_STATUSES:
            errors.append(f"status_map '{status}' -> '{target}': must be one of {DELIVERY_STATUSES}"
                          " (failed/rejected map to CANCELED)")
    return errors, warnings


# ---------- evaluation ----------

def evaluate(data, answers, status_map):
    tests = data["tests"]
    by_id = {t["id"]: t for t in tests}

    def provided(tid):
        a = answers.get(tid, {})
        if "provided" not in a and by_id[tid]["verify"] == "Live":
            # sandbox-only checks are answered by the sandbox run
            return {"Pass": "Yes", "Fail": "No", "NA": "NA"}.get(a.get("live"), "Not available")
        return a.get("provided", "Not available")

    def live(tid):
        if not has_live(by_id[tid]) or provided(tid) == "NA":
            return "NA"
        return answers.get(tid, {}).get("live", "Not run")

    def met(tid):
        return provided(tid) == "Yes" and live(tid) != "Fail"

    def state(tid):  # Met / Open / Missing
        if met(tid) or provided(tid) == "NA":
            return "Met"
        if provided(tid) == "Open" and live(tid) != "Fail":
            return "Open"
        return "Missing"

    must = []
    for g in data["must_haves"]:
        all_states = {tid: state(tid) for tid in g.get("all", [])}
        any_ids = g.get("any", [])
        any_states = {tid: state(tid) for tid in any_ids}
        if "Missing" in all_states.values() or (any_ids and set(any_states.values()) == {"Missing"}):
            s = "Missing"
        elif "Open" in all_states.values() or (any_ids and "Met" not in any_states.values()):
            s = "Open"
        else:
            s = "Met"
        ids = list(all_states) + any_ids
        evidence = "; ".join(f"{tid}: {answers.get(tid, {}).get('details', '') or provided(tid)}"
                             for tid in ids if provided(tid) != "Not available" or tid in all_states)
        must.append({"item": g["item"], "state": s, "ids": ids, "evidence": evidence})

    counts = {s: sum(m["state"] == s for m in must) for s in ("Met", "Open", "Missing")}

    live_needed = [t for t in tests if live(t["id"]) != "NA"]
    live_pass = [t for t in live_needed if live(t["id"]) == "Pass"]
    live_fail = [t for t in live_needed if live(t["id"]) == "Fail"]
    must_ids = {i for m in must for i in m["ids"]}
    must_live_open = [t for t in live_needed if t["id"] in must_ids and met(t["id"]) and live(t["id"]) != "Pass"]
    if not live_pass and not live_fail:
        api_works = "Not tested yet (no sandbox run)"
    elif live_fail:
        api_works = f"Problems found: {len(live_fail)} failed on sandbox ({', '.join(t['id'] for t in live_fail)})"
    elif len(live_pass) == len(live_needed):
        api_works = f"Works on sandbox: all {len(live_pass)} sandbox checks passed"
    else:
        api_works = f"Partly tested: {len(live_pass)} of {len(live_needed)} sandbox checks passed, none failed"

    escalations = [t for t in tests if t.get("risk") and provided(t["id"]) in ("No", "Open")]

    if counts["Missing"]:
        decision = "No, we cannot integrate yet"
        reason = f"{counts['Missing']} must-have(s) missing"
    elif counts["Open"]:
        decision = "Likely yes, after the vendor answers a few points"
        reason = f"{counts['Open']} must-have(s) only partly documented"
    elif must_live_open:
        decision = "Yes on paper, confirm with a sandbox test"
        reason = "every must-have is documented; sandbox test still to run"
    else:
        decision = "Yes, we can integrate"
        reason = "every must-have is documented and passed on sandbox"
    if escalations and not counts["Missing"]:
        reason += f"; {len(escalations)} item(s) need a change on our side first"

    def gaps(need):
        return [t for t in tests if t["need"] == need and state(t["id"]) != "Met"]

    return {
        "provided": provided, "live": live, "state": state, "must": must, "counts": counts,
        "decision": decision, "reason": reason, "api_works": api_works, "live_fail": live_fail,
        "escalations": escalations, "gaps": {n: gaps(n) for n in NEEDS},
        "covered": {n: (sum(state(t["id"]) == "Met" for t in tests if t["need"] == n),
                        sum(t["need"] == n for t in tests)) for n in NEEDS},
    }


# ---------- workbook ----------

def header(ws, row, labels):
    for c, label in enumerate(labels, 1):
        cell = ws.cell(row=row, column=c, value=label)
        cell.font = font(bold=True, color=WHITE)
        cell.fill = PatternFill("solid", fgColor=NAVY)
        cell.alignment = Alignment(vertical="center", wrap_text=True)
        cell.border = border()


def build_checks_sheet(wb, data, answers, ev):
    ws = wb.active
    ws.title = "Checks"
    cols = [("ID", 9), ("Area", 20), ("Need", 13), ("Checked by", 11), ("Check", 55),
            ("What counts as yes", 38), ("Answer", 13), ("Evidence", 46), ("Sandbox", 11),
            ("Sandbox notes", 32), ("Tech note", 42)]
    header(ws, 1, [c[0] for c in cols])
    for i, t in enumerate(data["tests"]):
        a = answers.get(t["id"], {})
        p, lv = ev["provided"](t["id"]), ev["live"](t["id"])
        ws.append([t["id"], t["section"], t["need"], t["verify"].replace("Doc", "Docs").replace("Live", "Sandbox"),
                   t["test"], t["pass"], p, a.get("details", ""), lv, a.get("live_notes", ""), t["platform"]])
        r = ws.max_row
        for c in range(1, len(cols) + 1):
            cell = ws.cell(row=r, column=c)
            cell.font = font(bold=(c == 3 and t["need"] == "Must-have"))
            cell.fill = PatternFill("solid", fgColor=GREY if i % 2 else WHITE)
            cell.alignment = Alignment(vertical="top", wrap_text=True)
            cell.border = border()
        for c, v in ((7, p), (9, lv)):
            if v in FILL:
                ws.cell(row=r, column=c).fill = PatternFill("solid", fgColor=FILL[v])
    for i, (_, w) in enumerate(cols, 1):
        ws.column_dimensions[get_column_letter(i)].width = w
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = f"A1:{get_column_letter(len(cols))}{ws.max_row}"
    ws.sheet_view.showGridLines = False


def build_summary_sheet(wb, data, answers, payload, ev):
    ws = wb.create_sheet("Summary", 0)
    row = [1]

    def put(a, b=None, bold=False, fill=None):
        ws.cell(row=row[0], column=1, value=a).font = font(bold=bold)
        ws.cell(row=row[0], column=1).alignment = Alignment(wrap_text=True, vertical="top")
        if b is not None:
            cell = ws.cell(row=row[0], column=2, value=b)
            cell.font = font(bold=bold)
            cell.alignment = Alignment(wrap_text=True, vertical="top")
            if fill:
                cell.fill = PatternFill("solid", fgColor=fill)
        row[0] += 1

    def title(text):
        row[0] += 1
        for c in (1, 2):
            cell = ws.cell(row=row[0], column=c, value=text if c == 1 else None)
            cell.font = font(bold=True, color=WHITE)
            cell.fill = PatternFill("solid", fgColor=NAVY)
        row[0] += 1

    ws.cell(row=1, column=1, value=f"{payload.get('vendor_name', 'Vendor')}: merchandise API review"
            ).font = font(bold=True, size=14, color=NAVY)
    row[0] = 2
    if payload.get("reviewed_on"):
        put("Reviewed on", payload["reviewed_on"])
    for src in payload.get("doc_sources", []):
        put("Source", src)

    c = ev["counts"]
    title("Decision")
    put("Can we integrate?", f"{ev['decision']} ({ev['reason']})", True,
        RED if c["Missing"] else AMBER if c["Open"] or ev["escalations"] else GREEN)
    put("Does the API work?", ev["api_works"], True, RED if ev["live_fail"] else AMBER if "Not tested" in ev["api_works"] else GREEN)
    put("Must-haves", f"{c['Met']} met, {c['Open']} open, {c['Missing']} missing (of {len(ev['must'])})", True)
    for n in ("Important", "Nice-to-have"):
        have, total = ev["covered"][n]
        put(f"{n} checks covered", f"{have} of {total}")

    title("Must-haves")
    for m in ev["must"]:
        put(f"[{m['state'].upper()}] {m['item']}", m["evidence"], bold=m["state"] != "Met", fill=FILL[m["state"]])

    if ev["escalations"]:
        title("Needs a change on our side first")
        for t in ev["escalations"]:
            put(f"{t['id']} {t['test']}", answers.get(t["id"], {}).get("details", ""))

    if ev["live_fail"]:
        title("Failed on sandbox")
        for t in ev["live_fail"]:
            put(f"{t['id']} {t['test']}", answers.get(t["id"], {}).get("live_notes", ""), fill=RED)

    title("Status mapping")
    sm = payload.get("status_map", {})
    if not sm:
        put("No status list documented yet", "")
    for k, v in sm.items():
        put(k, v)

    for n in ("Important", "Nice-to-have"):
        title(f"{n} gaps (do not block)")
        for t in ev["gaps"][n]:
            put(f"{t['id']} {t['test']}", answers.get(t["id"], {}).get("details", "") or ev["provided"](t["id"]))

    ws.column_dimensions["A"].width = 80
    ws.column_dimensions["B"].width = 70
    ws.sheet_view.showGridLines = False


# ---------- markdown ----------

def build_markdown(data, answers, payload, ev):
    def cell(s):
        return str(s).replace("|", "\\|").replace("\n", " ")

    c = ev["counts"]
    out = [f"# {payload.get('vendor_name', 'Vendor')}: merchandise API review", ""]
    if payload.get("reviewed_on"):
        out.append(f"Reviewed on: {payload['reviewed_on']}  ")
    for src in payload.get("doc_sources", []):
        out.append(f"Source: {src}  ")
    out += ["", "## Decision", "",
            f"**Can we integrate?** {ev['decision']} ({ev['reason']}).  ",
            f"**Does the API work?** {ev['api_works']}.  ",
            f"**Must-haves:** {c['Met']} met, {c['Open']} open, {c['Missing']} missing (of {len(ev['must'])}).  ",
            "**Other checks covered:** " + ", ".join(
                f"{n} {ev['covered'][n][0]} of {ev['covered'][n][1]}" for n in ("Important", "Nice-to-have")) + ".",
            "", "## Must-haves", "", "| | Must-have | Evidence |", "|---|---|---|"]
    out += [f"| {m['state']} | {cell(m['item'])} | {cell(m['evidence'])} |" for m in ev["must"]]

    def block(heading, rows):
        nonlocal out
        out += ["", f"## {heading}", ""] + (rows or ["None."])

    if ev["escalations"]:
        block("Needs a change on our side first",
              [f"- **{t['id']}** {t['test']} ({answers.get(t['id'], {}).get('details', '')})" for t in ev["escalations"]])
    if ev["live_fail"]:
        block("Failed on sandbox", [f"- **{t['id']}** {answers.get(t['id'], {}).get('live_notes', '')}" for t in ev["live_fail"]])
    sm = payload.get("status_map", {})
    block("Status mapping", [f"- `{k}` -> {v}" for k, v in sm.items()] or ["No status list documented yet."])
    for n in ("Important", "Nice-to-have"):
        block(f"{n} gaps (do not block)",
              [f"- **{t['id']}** {t['test']}" + (f" ({answers[t['id']]['details']})"
                                                if answers.get(t['id'], {}).get('details') else "")
               for t in ev["gaps"][n]])
    out += ["", "## Coverage by area", "", "| Area | Yes | No | Open | Not available | NA |", "|---|---|---|---|---|---|"]
    tests = data["tests"]
    for s in dict.fromkeys(t["section"] for t in tests):
        ts = [t for t in tests if t["section"] == s]
        k = {v: sum(ev["provided"](t["id"]) == v for t in ts) for v in PROVIDED}
        out.append(f"| {s} | {k['Yes']} | {k['No']} | {k['Open']} | {k['Not available']} | {k['NA']} |")
    return "\n".join(out) + "\n"


def main():
    args = sys.argv[1:]
    md_path = None
    if "--md" in args:
        i = args.index("--md")
        md_path = args[i + 1]
        del args[i:i + 2]
    if len(args) < 3:
        print(__doc__)
        sys.exit(1)
    tests_path, answers_path, out_path = args[:3]
    with open(tests_path) as f:
        data = json.load(f)
    with open(answers_path) as f:
        payload = json.load(f)
    errors, warnings = validate(data["tests"], payload)
    for w in warnings:
        print(f"WARN  {w}")
    if errors:
        for e in errors:
            print(f"ERROR {e}")
        sys.exit(2)
    answers = payload.get("answers", {})
    ev = evaluate(data, answers, payload.get("status_map", {}))
    wb = Workbook()
    build_checks_sheet(wb, data, answers, ev)
    build_summary_sheet(wb, data, answers, payload, ev)
    wb.save(out_path)
    print(f"Wrote {out_path}")
    if md_path:
        with open(md_path, "w") as f:
            f.write(build_markdown(data, answers, payload, ev))
        print(f"Wrote {md_path}")
    c = ev["counts"]
    print(f"{ev['decision']} | must-haves {c['Met']} met, {c['Open']} open, {c['Missing']} missing | {ev['api_works']}")


if __name__ == "__main__":
    main()
