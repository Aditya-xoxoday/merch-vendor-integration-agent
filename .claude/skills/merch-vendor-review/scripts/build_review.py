#!/usr/bin/env python3
"""
Build the ONE output of a review: a single workbook that answers "can we integrate?" and
"does the API work?".

Usage:
    python3 build_review.py <test_cases.json> <review.json> <Vendor>_Review.xlsx [--md <report.md>]

Workbook tabs:
    Summary           decision, must-haves, what we need from the vendor, security, next steps,
                      and a short copy-paste summary for Jira/Slack
    Vendor questions  numbered questions (must-haves first), other gaps, and the email draft
    Tech              endpoints, order field mapping, status flow, failure modes, assumptions,
                      config changes, build notes (only when review.json has "tech")
    All checks        every check with answer, evidence and sandbox result

<review.json>:
    {
      "vendor_name": "Example Vendor",
      "reviewed_on": "2026-10-18",
      "doc_sources": ["https://vendor.example/docs"],
      "answers": {
        "ORD-02": {"provided": "Yes", "details": "Response field orders_id",
                   "live": "Pass", "live_notes": "200, orders_id present"},
        "WHK-05": {"provided": "No", "details": "Signature header is mandatory"}
      },
      "status_map": {"in production": "CONFIRMED", "dispatched": "SHIPPED"},
      "security": "No credentials found in the document.",                 # optional
      "must_have_notes": {"1": "orders_id returned", "4": "Only 1 status documented"},  # optional, by must-have #
      "questions": [{"q": "Full list of order statuses?", "need": "Must-have", "checks": "STS-01"}],  # optional
      "vendor_email": "Subject: ...\n\nHi ...",                              # optional
      "next_steps": [{"step": "Send questions", "who": "Us"}],             # optional
      "tech": {                                                            # optional
        "api_summary": "...",
        "endpoints": [{"operation": "", "call": "", "notes": ""}],
        "order_mapping": [{"their_field": "", "our_source": "", "rule": ""}],
        "status_flow": [{"their_status": "", "our_status": "", "effect": ""}],
        "failure_modes": [{"failure": "", "handling": "", "severity": ""}],
        "assumptions": [{"assumption": "", "verify": ""}],
        "config": [{"where": "", "change": ""}],
        "build_notes": ["..."]
      }
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

def plural(n, word):
    return f"{n} {word}{'' if n == 1 else 's'}"


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
        failed = [tid for tid in list(all_states) + any_ids if live(tid) == "Fail"]
        if failed or "Missing" in all_states.values() or (any_ids and set(any_states.values()) == {"Missing"}):
            s = "Missing"  # a sandbox failure on any must-have check (even an alternative) blocks
        elif "Open" in all_states.values() or (any_ids and "Met" not in any_states.values()):
            s = "Open"
        else:
            s = "Met"
        ids = list(all_states) + any_ids
        evidence = "\n".join(f"{tid}: {answers.get(tid, {}).get('details', '') or provided(tid)}"
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
        reason = f"{plural(counts['Missing'], 'must-have')} missing"
    elif counts["Open"]:
        decision = "Likely yes, after the vendor answers a few points"
        reason = f"{plural(counts['Open'], 'must-have')} only partly documented"
    elif must_live_open:
        decision = "Yes on paper, confirm with a sandbox test"
        reason = "every must-have is documented; sandbox test still to run"
    else:
        decision = "Yes, we can integrate"
        reason = "every must-have is documented and passed on sandbox"
    if escalations and not counts["Missing"]:
        reason += f"; {plural(len(escalations), 'item')} need a change on our side first"

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

TECH_SECTIONS = [  # key, title, [(field, column label, width)]
    ("endpoints", "Endpoints", [("operation", "Operation"), ("call", "Call"), ("notes", "Notes")]),
    ("order_mapping", "Order field mapping", [("their_field", "Their field"), ("our_source", "Our source"),
                                              ("rule", "Rule")]),
    ("status_flow", "Status flow", [("their_status", "Their status"), ("our_status", "Our status"),
                                    ("effect", "What happens")]),
    ("failure_modes", "Failure modes", [("failure", "Failure"), ("handling", "Handling"), ("severity", "Severity")]),
    ("assumptions", "Assumptions to verify", [("assumption", "Assumption"), ("verify", "How to verify")]),
    ("config", "Config changes", [("where", "Where"), ("change", "Change")]),
]


class Sheet:
    """Small helper that writes clean, consistently styled blocks top to bottom."""

    def __init__(self, ws, widths):
        self.ws, self.row = ws, 1
        for i, w in enumerate(widths, 1):
            ws.column_dimensions[get_column_letter(i)].width = w
        self.ncols = len(widths)
        ws.sheet_view.showGridLines = False

    def title(self, text, sub=None):
        self.ws.cell(row=self.row, column=1, value=text).font = font(bold=True, size=15, color=NAVY)
        self.row += 1
        if sub:
            self.ws.cell(row=self.row, column=1, value=sub).font = font(italic=True, color="595959")
            self.row += 1

    def heading(self, text):
        self.row += 1
        for c in range(1, self.ncols + 1):
            cell = self.ws.cell(row=self.row, column=c, value=text if c == 1 else None)
            cell.font = font(bold=True, color=WHITE)
            cell.fill = PatternFill("solid", fgColor=NAVY)
        self.row += 1

    def table(self, labels, rows, fills=None):
        for c, label in enumerate(labels, 1):
            cell = self.ws.cell(row=self.row, column=c, value=label)
            cell.font = font(bold=True)
            cell.fill = PatternFill("solid", fgColor="D9E1F2")
            cell.border = border()
        self.row += 1
        for i, values in enumerate(rows):
            for c, v in enumerate(values, 1):
                cell = self.ws.cell(row=self.row, column=c, value=v)
                cell.font = font()
                cell.alignment = Alignment(wrap_text=True, vertical="top", horizontal="left")
                cell.border = border()
                if i % 2:
                    cell.fill = PatternFill("solid", fgColor=GREY)
            if fills and fills[i]:
                cell = self.ws.cell(row=self.row, column=1)
                cell.fill = PatternFill("solid", fgColor=fills[i])
                cell.font = font(bold=True)
            self.row += 1

    def pair(self, label, value, fill=None):
        a = self.ws.cell(row=self.row, column=1, value=label)
        a.font = font(bold=True)
        a.alignment = Alignment(vertical="top")
        b = self.ws.cell(row=self.row, column=2, value=value)
        b.font = font(bold=True)
        b.alignment = Alignment(wrap_text=True, vertical="top")
        if self.ncols > 2:
            self.ws.merge_cells(start_row=self.row, start_column=2, end_row=self.row, end_column=self.ncols)
        if fill:
            b.fill = PatternFill("solid", fgColor=fill)
        self.row += 1

    def text(self, value, height=None):
        cell = self.ws.cell(row=self.row, column=1, value=value)
        cell.font = font()
        cell.alignment = Alignment(wrap_text=True, vertical="top")
        self.ws.merge_cells(start_row=self.row, start_column=1, end_row=self.row, end_column=self.ncols)
        if height:
            self.ws.row_dimensions[self.row].height = height
        self.row += 1


def vendor_questions(data, payload, ev):
    """Questions from review.json, else generated from open/missing checks (must-haves first)."""
    if payload.get("questions"):
        return [(q.get("need", ""), q["q"], q.get("checks", "")) for q in payload["questions"]]
    rows = []
    for m in ev["must"]:
        if m["state"] != "Met":
            ids = [i for i in m["ids"] if ev["state"](i) != "Met"]
            rows.append(("Must-have", m["item"], ", ".join(ids)))
    for t in ev["gaps"]["Important"]:
        rows.append(("Important", t["test"], t["id"]))
    return rows


def short_summary(payload, ev):
    c = ev["counts"]
    open_items = [m["item"] for m in ev["must"] if m["state"] != "Met"]
    lines = [f"{payload.get('vendor_name', 'Vendor')}: {ev['decision']}.",
             f"Must-haves: {c['Met']} met, {c['Open']} open, {c['Missing']} missing (of {len(ev['must'])}).",
             f"API test: {ev['api_works']}."]
    if open_items:
        lines.append("Open: " + "; ".join(open_items) + ".")
    if payload.get("security"):
        lines.append(f"Security: {payload['security']}")
    steps = payload.get("next_steps") or []
    if steps:
        lines.append(f"Next: {steps[0]['step']}.")
    return "\n".join(lines)


def build_summary(wb, data, payload, ev):
    ws = wb.active
    ws.title = "Summary"
    s = Sheet(ws, [22, 52, 70])
    sub = " | ".join(x for x in [f"Reviewed {payload['reviewed_on']}" if payload.get("reviewed_on") else "",
                                  *payload.get("doc_sources", [])] if x)
    s.title(f"{payload.get('vendor_name', 'Vendor')}: merchandise API review", sub or None)
    c = ev["counts"]
    s.heading("Decision")
    s.pair("Can we integrate?", f"{ev['decision']} ({ev['reason']})",
           RED if c["Missing"] else AMBER if c["Open"] or ev["escalations"] else GREEN)
    s.pair("Does the API work?", ev["api_works"],
           RED if ev["live_fail"] else AMBER if not ev["api_works"].startswith("Works") else GREEN)
    s.pair("Must-haves", f"{c['Met']} met, {c['Open']} open, {c['Missing']} missing (of {len(ev['must'])})")
    if payload.get("security"):
        s.pair("Security", payload["security"])

    s.heading("Must-haves")
    notes = payload.get("must_have_notes", {})
    s.table(["Status", "Must-have", "What we found"],
            [(m["state"], m["item"], notes.get(str(i), m["evidence"])) for i, m in enumerate(ev["must"], 1)],
            fills=[FILL[m["state"]] for m in ev["must"]])

    if ev["escalations"]:
        s.heading("Needs a change on our side first")
        s.table(["Check", "Issue", "Evidence"],
                [(t["id"], t["test"], payload["answers"].get(t["id"], {}).get("details", "")) for t in ev["escalations"]])

    qs = vendor_questions(data, payload, ev)
    if qs:
        s.heading("What we need from the vendor (top 5; full list on 'Vendor questions')")
        s.table(["Need", "Question", "Checks"], qs[:5])

    steps = payload.get("next_steps") or []
    if steps:
        s.heading("Next steps")
        s.table(["#", "Step", "Who"], [(i, x["step"], x.get("who", "")) for i, x in enumerate(steps, 1)])

    s.heading("Short summary (copy for Jira / Slack)")
    s.text(short_summary(payload, ev), height=95)
    ws.freeze_panes = "A3"


def build_questions(wb, data, payload, ev):
    ws = wb.create_sheet("Vendor questions")
    s = Sheet(ws, [6, 14, 80, 22])
    s.title("Vendor questions", "Must-haves first. Important and nice-to-have gaps never block the integration.")
    qs = vendor_questions(data, payload, ev)
    s.heading("Questions to send")
    s.table(["#", "Need", "Question", "Checks"], [(i, *q) for i, q in enumerate(qs, 1)])
    for need in ("Important", "Nice-to-have"):
        gaps = ev["gaps"][need]
        if gaps:
            s.heading(f"{need} gaps (do not block)")
            s.table(["#", "Check", "Gap", "Answer"],
                    [(i, t["id"], t["test"], ev["provided"](t["id"])) for i, t in enumerate(gaps, 1)])
    if payload.get("vendor_email"):
        s.heading("Email draft")
        s.text(payload["vendor_email"], height=max(150, 15 * payload["vendor_email"].count("\n")))


def build_tech(wb, payload):
    tech = payload.get("tech")
    if not tech:
        return
    ws = wb.create_sheet("Tech")
    s = Sheet(ws, [34, 46, 64])
    s.title("Tech", "Build-level detail for developers. Full spec (if produced): <Vendor>_TECH_SPEC.md")
    if tech.get("api_summary"):
        s.heading("What the API does")
        s.text(tech["api_summary"], height=60)
    sm = payload.get("status_map", {})
    for key, title, cols in TECH_SECTIONS:
        rows = tech.get(key) or []
        if key == "status_flow" and not rows and sm:
            rows = [{"their_status": k, "our_status": v, "effect": ""} for k, v in sm.items()]
        if not rows:
            continue
        s.heading(title)
        labels = [label for _, label in cols]
        s.table(labels + [""] * (3 - len(labels)), [[r.get(f, "") for f, _ in cols] for r in rows])
    if tech.get("build_notes"):
        s.heading("Build notes")
        for note in tech["build_notes"]:
            s.text(f"- {note}")


def build_checks(wb, data, answers, ev):
    ws = wb.create_sheet("All checks")
    cols = [("ID", 9), ("Area", 20), ("Need", 13), ("Checked by", 11), ("Check", 55),
            ("What counts as yes", 38), ("Answer", 13), ("Evidence", 46), ("Sandbox", 11),
            ("Sandbox notes", 30), ("Tech note", 40)]
    for c, (label, w) in enumerate(cols, 1):
        cell = ws.cell(row=1, column=c, value=label)
        cell.font = font(bold=True, color=WHITE)
        cell.fill = PatternFill("solid", fgColor=NAVY)
        cell.alignment = Alignment(vertical="center", wrap_text=True)
        cell.border = border()
        ws.column_dimensions[get_column_letter(c)].width = w
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
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = f"A1:{get_column_letter(len(cols))}{ws.max_row}"
    ws.sheet_view.showGridLines = False


# ---------- markdown (optional) ----------

def build_markdown(data, answers, payload, ev):
    def cell(v):
        return str(v).replace("|", "\\|").replace("\n", " ")

    c = ev["counts"]
    out = [f"# {payload.get('vendor_name', 'Vendor')}: merchandise API review", ""]
    if payload.get("reviewed_on"):
        out.append(f"Reviewed on: {payload['reviewed_on']}  ")
    for src in payload.get("doc_sources", []):
        out.append(f"Source: {src}  ")
    out += ["", "## Decision", "", f"**Can we integrate?** {ev['decision']} ({ev['reason']}).  ",
            f"**Does the API work?** {ev['api_works']}.  ",
            f"**Must-haves:** {c['Met']} met, {c['Open']} open, {c['Missing']} missing (of {len(ev['must'])})."]
    if payload.get("security"):
        out.append(f"  \n**Security:** {payload['security']}")
    out += ["", "## Must-haves", "", "| Status | Must-have | What we found |", "|---|---|---|"]
    out += [f"| {m['state']} | {cell(m['item'])} | {cell(m['evidence'])} |" for m in ev["must"]]
    qs = vendor_questions(data, payload, ev)
    out += ["", "## Vendor questions", ""] + [f"{i}. [{q[0]}] {q[1]} ({q[2]})" for i, q in enumerate(qs, 1)]
    for need in ("Important", "Nice-to-have"):
        out += ["", f"## {need} gaps (do not block)", ""]
        out += [f"- **{t['id']}** {t['test']}" for t in ev["gaps"][need]] or ["None."]
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
    tests_path, review_path, out_path = args[:3]
    with open(tests_path) as f:
        data = json.load(f)
    with open(review_path) as f:
        payload = json.load(f)
    payload.setdefault("answers", {})
    errors, warnings = validate(data["tests"], payload)
    for w in warnings:
        print(f"WARN  {w}")
    if errors:
        for e in errors:
            print(f"ERROR {e}")
        sys.exit(2)
    answers = payload["answers"]
    ev = evaluate(data, answers, payload.get("status_map", {}))
    wb = Workbook()
    build_summary(wb, data, payload, ev)
    build_questions(wb, data, payload, ev)
    build_tech(wb, payload)
    build_checks(wb, data, answers, ev)
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
