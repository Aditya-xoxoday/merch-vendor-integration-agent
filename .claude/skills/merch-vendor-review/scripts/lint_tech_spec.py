#!/usr/bin/env python3
"""
Quality gate for TECH_SPEC.md: a spec that fails this is not finished.

Usage:
    python3 lint_tech_spec.py <TECH_SPEC.md> [<answers.json> <test_cases.json>]

Checks:
  - all 21 required sections exist as "## " headings (order free, keyword match)
  - at least 4 mermaid diagrams (token, order, polling/webhook, catalogue sync)
  - the failure-mode table has >= 12 rows; the assumption ledger has >= 6 rows
  - every row of the assumption ledger names how to verify it (last column not empty)
  - with answers: every must-have check that is not met, and every risk check answered No/Open,
    is mentioned by ID in the spec (so nothing open is silently dropped)
  - no secrets (uses scan_secrets.py)
Exits 1 with a list of problems, 0 when clean.
"""
import importlib.util
import json
import pathlib
import re
import sys

REQUIRED = [
    "Summary", "Check first", "Feasibility", "Architecture", "Endpoint contracts", "Data mapping",
    "State machine", "Class plan", "Config and registration", "Data model", "Failure modes",
    "Idempotency and retry", "Security and PII", "Performance and limits", "Observability",
    "Test strategy", "Rollout and rollback", "Effort", "Assumption ledger", "Open questions", "Done means",
]
MIN_MERMAID, MIN_FMEA, MIN_ASSUMPTIONS = 4, 12, 6
HERE = pathlib.Path(__file__).resolve().parent


def sections(text):
    out, current = {}, None
    for line in text.splitlines():
        if line.startswith("## "):
            current = line[3:].strip()
            out[current] = []
        elif current:
            out[current].append(line)
    return out


def table_rows(lines):
    rows = [l for l in lines if l.strip().startswith("|")]
    return [r for r in rows[2:] if not re.match(r"^\|\s*-", r.strip())]  # drop header + separator


def find(secs, keyword):
    return next((k for k in secs if keyword.lower() in k.lower()), None)


def lint(text, answers=None, data=None):
    problems = []
    secs = sections(text)
    for req in REQUIRED:
        if not find(secs, req):
            problems.append(f"missing section: '## … {req}'")
    n = text.count("```mermaid")
    if n < MIN_MERMAID:
        problems.append(f"only {n} mermaid diagrams (need {MIN_MERMAID}: token, order, status updates, catalogue sync)")
    fm = find(secs, "Failure modes")
    if fm and len(table_rows(secs[fm])) < MIN_FMEA:
        problems.append(f"failure-mode table has {len(table_rows(secs[fm]))} rows (need {MIN_FMEA})")
    al = find(secs, "Assumption ledger")
    if al:
        rows = table_rows(secs[al])
        if len(rows) < MIN_ASSUMPTIONS:
            problems.append(f"assumption ledger has {len(rows)} rows (need {MIN_ASSUMPTIONS})")
        for r in rows:
            cells = [c.strip() for c in r.strip().strip("|").split("|")]
            if not cells or not cells[-1]:
                problems.append(f"assumption without a way to verify: {r.strip()[:80]}")
    if answers is not None and data is not None:
        spec = importlib.util.spec_from_file_location("br", HERE / "build_review.py")
        br = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(br)
        ev = br.evaluate(data, answers.get("answers", {}), answers.get("status_map", {}))
        must_open = {t["id"] for t in data["tests"] if t["need"] == "Must-have" and ev["state"](t["id"]) != "Met"}
        # "any" groups: a missing alternative is fine when another one is met
        for g in data["must_haves"]:
            if any(ev["state"](i) == "Met" for i in g.get("any", [])):
                must_open -= set(g.get("any", []))
        risky = {t["id"] for t in ev["escalations"]}
        for tid in sorted(must_open | risky):
            if tid not in text:
                problems.append(f"{tid} is open/missing (or a risk) but never mentioned in the spec")
    ss_spec = importlib.util.spec_from_file_location("ss", HERE / "scan_secrets.py")
    ss = importlib.util.module_from_spec(ss_spec)
    ss_spec.loader.exec_module(ss)
    for label, value in ss.scan(text):
        problems.append(f"possible secret in spec: {label} {value}")
    return problems


def main():
    if len(sys.argv) not in (2, 4):
        print(__doc__)
        sys.exit(2)
    text = pathlib.Path(sys.argv[1]).read_text()
    answers = data = None
    if len(sys.argv) == 4:
        answers = json.loads(pathlib.Path(sys.argv[2]).read_text())
        data = json.loads(pathlib.Path(sys.argv[3]).read_text())
    problems = lint(text, answers, data)
    for p in problems:
        print(f"FAIL  {p}")
    print("TECH_SPEC OK" if not problems else f"{len(problems)} problem(s)")
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
