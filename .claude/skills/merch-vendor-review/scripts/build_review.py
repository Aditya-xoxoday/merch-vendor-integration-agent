#!/usr/bin/env python3
"""
Build the Merchandise vendor review workbook (v2: doc review + live staging verification).

Usage:
    python3 build_review.py <test_cases.json> <answers.json> <output.xlsx> [--md <report.md>]

<test_cases.json> is references/test_cases.json (static, bundled with the skill).

<answers.json> is written during the review:
    {
      "vendor_name": "Example Vendor",
      "reviewed_on": "2026-10-17",
      "doc_sources": ["https://vendor.example/docs"],
      "answers": {
        "ORD-02": {"provided": "Yes", "details": "POST /orders returns data.order_id",
                   "live": "Pass", "live_notes": "200, order_id present"},
        "WHK-05": {"provided": "No", "details": "HMAC-SHA256 X-Signature header is mandatory"}
      },
      "status_map": {"placed": "PENDING", "dispatched": "SHIPPED", "rto": "RETURNED"}
    }

    provided: Yes / No / Not available / NA / Open     (missing id = "Not available")
      Yes            docs confirm it; details MUST carry evidence (endpoint/field/short paraphrase)
      No             docs confirm it is absent; details MUST say where
      Not available  docs are silent (default, never inferred)
      NA             does not apply to this vendor
      Open           partial, needs vendor confirmation
    live: Pass / Fail / Not run / NA   (only for tests whose verify includes "Live")
    status_map: every vendor status -> one of PENDING CONFIRMED SHIPPED DELIVERED CANCELED RETURNED

The script exits non-zero on invalid input (unknown id, bad value, Yes/No without evidence,
invalid status_map target) so a review can never be built on unsupported answers.
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
RESULT_FILL = {"Yes": GREEN, "No": RED, "Open": AMBER, "Not available": AMBER,
               "Pass": GREEN, "Fail": RED, "Not run": AMBER}


def font(**kw):
    return Font(name="Arial", **kw)


def border():
    s = Side(style="thin", color="D9D9D9")
    return Border(left=s, right=s, top=s, bottom=s)


def needs_live(t):
    return "Live" in t["verify"]


# ---------- validation ----------

def validate(tests, payload):
    errors, warnings = [], []
    by_id = {t["id"]: t for t in tests}
    for tid, a in payload.get("answers", {}).items():
        if tid not in by_id:
            errors.append(f"{tid}: unknown test id")
            continue
        p = a.get("provided", "Not available")
        if p not in PROVIDED:
            errors.append(f"{tid}: provided '{p}' not in {PROVIDED}")
        if p in ("Yes", "No") and not a.get("details", "").strip():
            errors.append(f"{tid}: '{p}' needs evidence in details (hard rule: never assume)")
        if p == "Open" and not a.get("details", "").strip():
            warnings.append(f"{tid}: Open without a note on what is unclear")
        live = a.get("live")
        if live is not None:
            if live not in LIVE:
                errors.append(f"{tid}: live '{live}' not in {LIVE}")
            elif not needs_live(by_id[tid]) and live != "NA":
                warnings.append(f"{tid}: live result given for a Doc-only test")
    for status, target in payload.get("status_map", {}).items():
        if target not in DELIVERY_STATUSES:
            errors.append(f"status_map '{status}' -> '{target}': must be one of {DELIVERY_STATUSES}"
                          " (never ORDER_FAILED; failed/rejected map to CANCELED)")
    return errors, warnings


# ---------- evaluation ----------

def evaluate(data, answers, status_map):
    tests = data["tests"]
    weights = data["priority_weights"]

    def ans(tid):
        return answers.get(tid, {})

    def provided(tid):
        a = ans(tid)
        if "provided" not in a and by_id[tid]["verify"] == "Live":
            # Live-only tests are answered by the staging run, not the docs
            return {"Pass": "Yes", "Fail": "No", "NA": "NA"}.get(a.get("live"), "Not available")
        return a.get("provided", "Not available")

    def live(tid):
        t = by_id[tid]
        if not needs_live(t) or provided(tid) == "NA":
            return "NA"
        return ans(tid).get("live", "Not run")

    by_id = {t["id"]: t for t in tests}

    def met(tid):
        return provided(tid) == "Yes" and live(tid) != "Fail"

    applicable = [t for t in tests if provided(t["id"]) != "NA"]
    w_total = sum(weights[t["priority"]] for t in applicable)
    w_yes = sum(weights[t["priority"]] for t in applicable if met(t["id"]))
    score = round(100 * w_yes / w_total) if w_total else 0

    doc_complete = round(100 * sum(provided(t["id"]) != "Not available" for t in tests) / len(tests))

    live_required = [t for t in tests if live(t["id"]) != "NA"]
    live_pass = [t for t in live_required if live(t["id"]) == "Pass"]
    live_fail = [t for t in live_required if live(t["id"]) == "Fail"]
    live_run = [t for t in live_required if live(t["id"]) in ("Pass", "Fail")]
    live_cov = round(100 * len(live_run) / len(live_required)) if live_required else 100

    status_map_ok = bool(status_map) and all(v in DELIVERY_STATUSES for v in status_map.values())

    gate = []
    for g in data["gate"]:
        missing = [tid for tid in g.get("all", []) if not met(tid)]
        any_ids = g.get("any", [])
        any_ok = not any_ids or any(met(tid) for tid in any_ids)
        ok = not missing and any_ok and (status_map_ok if g.get("status_map") else True)
        why = []
        if missing:
            why.append("not met: " + ", ".join(missing))
        if not any_ok:
            why.append("needs one of: " + ", ".join(any_ids))
        if g.get("status_map") and not status_map_ok:
            why.append("status_map missing or invalid")
        gate.append({"item": g["item"], "met": ok, "why": "; ".join(why) or "all linked tests met"})
    gate_pass = all(g["met"] for g in gate)

    feas = []
    for line, ids in data["feasibility"].items():
        vals = [provided(i) for i in ids]
        if all(v == "NA" for v in vals):
            state = "N/A"
        elif any(provided(i) == "No" and by_id[i]["priority"] == "P0" for i in ids) or \
                any(live(i) == "Fail" for i in ids):
            state = "BLOCKED"
        elif all(v in ("Not available", "NA") for v in vals):
            state = "MISSING"
        elif all(met(i) or provided(i) == "NA" for i in ids) and \
                all(live(i) in ("Pass", "NA") for i in ids):
            state = "OK"
        else:
            state = "CHECK"
        unresolved = [i for i in ids if not met(i) and provided(i) != "NA"]
        unrun = [i for i in ids if live(i) == "Not run"]
        note = []
        if unresolved:
            note.append("unresolved: " + ", ".join(unresolved))
        if unrun:
            note.append("live not run: " + ", ".join(unrun))
        feas.append((line, state, "; ".join(note)))
    # webhook OR polling is enough for status updates
    states = {f[0]: f[1] for f in feas}
    if states.get("WEBHOOK") == "OK" or states.get("POLLING") == "OK":
        feas = [(l, "OK (alt)" if l in ("WEBHOOK", "POLLING") and s != "OK" else s, n) for l, s, n in feas]

    escalations = [t for t in tests if t.get("risk") and provided(t["id"]) in ("No", "Open")]
    contradictions = [t for t in tests if provided(t["id"]) == "Yes" and live(t["id"]) == "Fail"]

    rating = 5 if score >= 80 else 4 if score >= 65 else 3 if score >= 50 else 2 if score >= 30 else 1
    if not gate_pass:
        verdict = "Not ready"
    elif live_fail or live_cov < 100:
        verdict = "Doc-ready, live staging verification pending"
    elif score >= 75 and not escalations:
        verdict = "Ready (100% feasible: every live test passed)"
    else:
        verdict = "Ready with conditions"

    return {
        "provided": provided, "live": live, "met": met, "score": score, "rating": rating,
        "doc_complete": doc_complete, "live_cov": live_cov, "live_required": len(live_required),
        "live_pass": len(live_pass), "live_fail": live_fail, "gate": gate, "gate_pass": gate_pass,
        "feas": feas, "escalations": escalations, "contradictions": contradictions,
        "verdict": verdict, "status_map_ok": status_map_ok,
    }


# ---------- sheets ----------

def header(ws, row, labels):
    for c, label in enumerate(labels, 1):
        cell = ws.cell(row=row, column=c, value=label)
        cell.font = font(bold=True, color=WHITE)
        cell.fill = PatternFill("solid", fgColor=NAVY)
        cell.alignment = Alignment(vertical="center", wrap_text=True)
        cell.border = border()


def build_review(wb, data, answers, ev):
    ws = wb.active
    ws.title = "Review"
    cols = [("ID", 9), ("Section", 20), ("Priority", 8), ("Verify", 10), ("Test case", 55),
            ("Pass criteria", 38), ("Platform impact", 42), ("Doc result", 13), ("Evidence", 46),
            ("Live result", 11), ("Live notes", 32)]
    header(ws, 1, [c[0] for c in cols])
    for i, t in enumerate(data["tests"]):
        a = answers.get(t["id"], {})
        p, lv = ev["provided"](t["id"]), ev["live"](t["id"])
        row = [t["id"], t["section"], t["priority"], t["verify"], t["test"], t["pass"],
               t["platform"], p, a.get("details", ""), lv, a.get("live_notes", "")]
        ws.append(row)
        r = ws.max_row
        for c in range(1, len(cols) + 1):
            cell = ws.cell(row=r, column=c)
            cell.font = font(bold=(c == 3 and t["priority"] == "P0"))
            cell.fill = PatternFill("solid", fgColor=GREY if i % 2 else WHITE)
            cell.alignment = Alignment(vertical="top", wrap_text=True)
            cell.border = border()
        for c, v in ((8, p), (10, lv)):
            if v in RESULT_FILL:
                ws.cell(row=r, column=c).fill = PatternFill("solid", fgColor=RESULT_FILL[v])
    for i, (_, w) in enumerate(cols, 1):
        ws.column_dimensions[get_column_letter(i)].width = w
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = f"A1:{get_column_letter(len(cols))}{ws.max_row}"
    ws.sheet_view.showGridLines = False


def build_report(wb, data, answers, payload, ev):
    ws = wb.create_sheet("Report")
    tests = data["tests"]
    row = [1]

    def put(a, b=None, bold=False, fill=None, italic=False):
        ws.cell(row=row[0], column=1, value=a).font = font(bold=bold)
        if b is not None:
            cell = ws.cell(row=row[0], column=2, value=b)
            cell.font = font(bold=bold, italic=italic)
            cell.alignment = Alignment(wrap_text=True, vertical="top")
            if fill:
                cell.fill = PatternFill("solid", fgColor=fill)
        ws.cell(row=row[0], column=1).alignment = Alignment(wrap_text=True, vertical="top")
        row[0] += 1

    def title(text):
        row[0] += 1
        for c in range(1, 4):
            cell = ws.cell(row=row[0], column=c, value=text if c == 1 else None)
            cell.font = font(bold=True, color=WHITE)
            cell.fill = PatternFill("solid", fgColor=NAVY)
        row[0] += 1

    def label(t):
        return f"{t['id']} [{t['priority']}] {t['test']}"

    ws.cell(row=1, column=1, value=f"{data['category']} Vendor Review: {payload.get('vendor_name', 'Vendor')}"
            ).font = font(bold=True, size=14, color=NAVY)
    row[0] = 2
    if payload.get("reviewed_on"):
        put("Reviewed on", payload["reviewed_on"])
    for src in payload.get("doc_sources", []):
        put("Source", src, italic=True)

    title("Scorecard")
    sc = ev["score"]
    put("Capability score (priority weighted, NA excluded)", f"{sc}/100", True,
        GREEN if sc >= 65 else AMBER if sc >= 40 else RED)
    put("Rating", f"{ev['rating']} / 5", True)
    put("Documentation completeness", f"{ev['doc_complete']}%", True)
    put("Live staging coverage", f"{ev['live_cov']}% ({ev['live_pass']} pass, {len(ev['live_fail'])} fail, "
        f"{ev['live_required']} required)", True, GREEN if ev["live_cov"] == 100 and not ev["live_fail"] else AMBER)
    put("Integration gate", "PASS" if ev["gate_pass"] else "FAIL", True, GREEN if ev["gate_pass"] else RED)
    put("Engineering escalations", str(len(ev["escalations"])), True, RED if ev["escalations"] else GREEN)
    put("Verdict", ev["verdict"], True)

    title("Integration gate (derived from test results)")
    for g in ev["gate"]:
        put(f"[{'MET' if g['met'] else 'NOT MET'}] {g['item']}", g["why"], bold=not g["met"],
            fill=GREEN if g["met"] else RED)

    title("Feasibility (merch-sensei lines)")
    fill = {"OK": GREEN, "OK (alt)": GREEN, "CHECK": AMBER, "BLOCKED": RED, "MISSING": RED, "N/A": GREY}
    for line, state, note in ev["feas"]:
        put(f"{line}: {state}", note, bold=True, fill=fill[state])

    title("Readiness by section")
    put("Section", "Yes / No / Open / Not available / NA (of total)", bold=True)
    sections = list(dict.fromkeys(t["section"] for t in tests))
    for s in sections:
        ts = [t for t in tests if t["section"] == s]
        counts = [sum(ev["provided"](t["id"]) == k for t in ts) for k in PROVIDED]
        put(s, f"{counts[0]} / {counts[1]} / {counts[4]} / {counts[2]} / {counts[3]}  (of {len(ts)})")

    if ev["escalations"]:
        title("Engineering escalations (platform gap, raise before building)")
        for t in ev["escalations"]:
            put(label(t), f"{answers.get(t['id'], {}).get('details', '')}  | {t['platform']}", italic=True)

    if ev["contradictions"] or ev["live_fail"]:
        title("Doc vs live contradictions / live failures")
        for t in ev["live_fail"]:
            put(label(t), answers.get(t["id"], {}).get("live_notes", ""), italic=True, fill=RED)

    title("Status map (vendor status -> Plum delivery status)")
    sm = payload.get("status_map", {})
    if not sm:
        put("No status map recorded", "STS-02 cannot pass without it", fill=RED)
    for k, v in sm.items():
        put(k, v, fill=GREEN if v in DELIVERY_STATUSES else RED)

    title("What the vendor has (evidence)")
    for t in tests:
        if ev["provided"](t["id"]) == "Yes":
            put(label(t), answers[t["id"]].get("details", ""), italic=True)

    title("What the vendor does not have")
    for t in tests:
        if ev["provided"](t["id"]) == "No":
            put(label(t), answers[t["id"]].get("details", ""), italic=True)

    title("Prioritized vendor questions (P0 first)")
    order = {"P0": 0, "P1": 1, "P2": 2}
    qs = [t for t in tests if ev["provided"](t["id"]) in ("Not available", "Open")]
    for t in sorted(qs, key=lambda t: order[t["priority"]]):
        put(label(t), answers.get(t["id"], {}).get("details", "") or "Not stated in docs", italic=True)

    ws.column_dimensions["A"].width = 85
    ws.column_dimensions["B"].width = 60
    ws.column_dimensions["C"].width = 4
    ws.sheet_view.showGridLines = False


def build_markdown(data, answers, payload, ev):
    """Plain-text twin of the Report sheet, for PRs, Jira, Confluence and the agent's analysis."""
    tests = data["tests"]
    order = {"P0": 0, "P1": 1, "P2": 2}

    def cell(s):
        return str(s).replace("|", "\\|").replace("\n", " ")

    out = [f"# {data['category']} Vendor Review: {payload.get('vendor_name', 'Vendor')}", ""]
    if payload.get("reviewed_on"):
        out.append(f"Reviewed on: {payload['reviewed_on']}  ")
    for src in payload.get("doc_sources", []):
        out.append(f"Source: {src}  ")
    out += ["", "## Scorecard", "", "| Metric | Value |", "|---|---|",
            f"| Capability score | {ev['score']}/100 |", f"| Rating | {ev['rating']} / 5 |",
            f"| Documentation completeness | {ev['doc_complete']}% |",
            f"| Live staging coverage | {ev['live_cov']}% ({ev['live_pass']} pass, {len(ev['live_fail'])} fail, "
            f"{ev['live_required']} required) |",
            f"| Integration gate | {'PASS' if ev['gate_pass'] else 'FAIL'} |",
            f"| Engineering escalations | {len(ev['escalations'])} |", f"| **Verdict** | **{ev['verdict']}** |",
            "", "## Integration gate", "", "| Result | Gate item | Why |", "|---|---|---|"]
    out += [f"| {'MET' if g['met'] else 'NOT MET'} | {cell(g['item'])} | {cell(g['why'])} |" for g in ev["gate"]]
    out += ["", "## Feasibility (merch-sensei lines)", "", "| Line | State | Notes |", "|---|---|---|"]
    out += [f"| {line} | {state} | {cell(note)} |" for line, state, note in ev["feas"]]
    out += ["", "## Readiness by section", "", "| Section | Yes | No | Open | Not available | NA |",
            "|---|---|---|---|---|---|"]
    for s in dict.fromkeys(t["section"] for t in tests):
        ts = [t for t in tests if t["section"] == s]
        c = {k: sum(ev["provided"](t["id"]) == k for t in ts) for k in PROVIDED}
        out.append(f"| {s} | {c['Yes']} | {c['No']} | {c['Open']} | {c['Not available']} | {c['NA']} |")

    def block(heading, rows):
        nonlocal out
        out += ["", f"## {heading}", ""]
        out += rows or ["None."]

    block("Engineering escalations", [f"- **{t['id']}** {t['test']} Evidence: {answers.get(t['id'], {}).get('details', '')}. "
                                      f"Platform: {t['platform']}" for t in ev["escalations"]])
    block("Live failures", [f"- **{t['id']}** {answers.get(t['id'], {}).get('live_notes', '')}" for t in ev["live_fail"]])
    sm = payload.get("status_map", {})
    block("Status map", [f"- `{k}` -> {v}" for k, v in sm.items()] or
          ["No status map recorded: STS-02 and the status gate cannot pass."])
    block("What the vendor has", [f"- **{t['id']}** {t['test']} Evidence: {answers[t['id']].get('details', '')}"
                                  for t in tests if ev["provided"](t["id"]) == "Yes"])
    block("What the vendor does not have", [f"- **{t['id']}** {t['test']} Evidence: {answers[t['id']].get('details', '')}"
                                            for t in tests if ev["provided"](t["id"]) == "No"])
    qs = sorted([t for t in tests if ev["provided"](t["id"]) in ("Not available", "Open")],
                key=lambda t: order[t["priority"]])
    block("Vendor questions (P0 first)", [f"- [{t['priority']}] **{t['id']}** {t['test']}"
                                          + (f" Note: {answers[t['id']]['details']}" if answers.get(t['id'], {}).get('details') else "")
                                          for t in qs])
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
    sys.argv[1:] = args
    with open(sys.argv[1]) as f:
        data = json.load(f)
    with open(sys.argv[2]) as f:
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
    build_review(wb, data, answers, ev)
    build_report(wb, data, answers, payload, ev)
    wb.save(sys.argv[3])
    print(f"Wrote {sys.argv[3]}")
    if md_path:
        with open(md_path, "w") as f:
            f.write(build_markdown(data, answers, payload, ev))
        print(f"Wrote {md_path}")
    print(f"Score {ev['score']}/100 | gate {'PASS' if ev['gate_pass'] else 'FAIL'} | "
          f"live coverage {ev['live_cov']}% | escalations {len(ev['escalations'])} | {ev['verdict']}")


if __name__ == "__main__":
    main()
