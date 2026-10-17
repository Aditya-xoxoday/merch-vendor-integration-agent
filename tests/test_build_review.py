"""Behaviour of the scoring, gate and verdict engine."""
import json
import subprocess
import sys

from conftest import SKILL


def ev_for(br, data, answers, status_map=None):
    return br.evaluate(data, answers, status_map or {})


def test_perfect_vendor_is_ready(br, data, all_yes):
    answers, sm = all_yes
    ev = ev_for(br, data, answers, sm)
    assert ev["score"] == 100 and ev["gate_pass"] and ev["live_cov"] == 100
    assert ev["verdict"].startswith("Ready (100% feasible")


def test_empty_answers_not_ready(br, data):
    ev = ev_for(br, data, {})
    assert ev["score"] == 0 and not ev["gate_pass"] and ev["verdict"] == "Not ready"


def test_na_is_excluded_from_score(br, data, all_yes):
    answers, sm = all_yes
    p2 = next(t["id"] for t in data["tests"] if t["priority"] == "P2")
    answers[p2] = {"provided": "NA", "details": "n/a"}
    assert ev_for(br, data, answers, sm)["score"] == 100


def test_live_fail_cancels_doc_yes_and_fails_gate(br, data, all_yes):
    answers, sm = all_yes
    answers["IDM-02"]["live"] = "Fail"
    ev = ev_for(br, data, answers, sm)
    assert not ev["gate_pass"]
    assert any(t["id"] == "IDM-02" for t in ev["contradictions"])


def test_live_not_run_keeps_verdict_pending(br, data, all_yes):
    answers, sm = all_yes
    answers["ORD-01"]["live"] = "Not run"
    assert ev_for(br, data, answers, sm)["verdict"] == "Doc-ready, live staging verification pending"


def test_webhook_or_polling_is_enough(br, data, all_yes):
    answers, sm = all_yes
    answers["WHK-01"] = {"provided": "No", "details": "no webhooks"}
    gate = ev_for(br, data, answers, sm)["gate"]
    assert gate[2]["met"]
    answers["POL-01"] = {"provided": "Not available", "details": ""}
    assert not ev_for(br, data, answers, sm)["gate"][2]["met"]


def test_status_gate_needs_status_map(br, data, all_yes):
    answers, _ = all_yes
    assert not ev_for(br, data, answers, {})["gate"][2]["met"]


def test_live_only_tests_answered_by_live_result(br, data):
    ev = ev_for(br, data, {"AUTH-04": {"live": "Pass"}, "ORD-12": {"live": "Fail"}})
    assert ev["provided"]("AUTH-04") == "Yes" and ev["provided"]("ORD-12") == "No"


def test_risk_answer_creates_escalation(br, data, all_yes):
    answers, sm = all_yes
    answers["WHK-05"] = {"provided": "No", "details": "HMAC mandatory"}
    ev = ev_for(br, data, answers, sm)
    assert [t["id"] for t in ev["escalations"]] == ["WHK-05"]
    assert ev["verdict"] == "Ready with conditions"


def test_missing_feasibility_line(br, data):
    feas = {line: state for line, state, _ in ev_for(br, data, {})["feas"]}
    assert feas["ORDER"] == "MISSING"


def test_validation_rejects_bad_input(br, data):
    errors, _ = br.validate(data["tests"], {
        "answers": {"ORD-02": {"provided": "Yes"}, "FOO-1": {"provided": "Yes", "details": "x"},
                    "ORD-04": {"provided": "Maybe", "details": "x"}, "ORD-01": {"provided": "No", "details": "x", "live": "Done"}},
        "status_map": {"failed": "ORDER_FAILED"}})
    joined = " ".join(errors)
    for needle in ("ORD-02", "FOO-1", "ORD-04", "Done", "ORDER_FAILED"):
        assert needle in joined


def test_cli_builds_xlsx_and_markdown(tmp_path):
    answers = tmp_path / "a.json"
    answers.write_text(json.dumps({"vendor_name": "T", "answers": {"ORD-02": {"provided": "Yes", "details": "order_id"}}}))
    xlsx, md = tmp_path / "o.xlsx", tmp_path / "o.md"
    r = subprocess.run([sys.executable, str(SKILL / "scripts" / "build_review.py"),
                        str(SKILL / "references" / "test_cases.json"), str(answers), str(xlsx), "--md", str(md)],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
    assert xlsx.stat().st_size > 0
    text = md.read_text()
    assert "## Integration gate" in text and "ORD-02" in text


def test_cli_exits_nonzero_on_invalid(tmp_path):
    answers = tmp_path / "a.json"
    answers.write_text(json.dumps({"answers": {"ORD-02": {"provided": "Yes"}}}))
    r = subprocess.run([sys.executable, str(SKILL / "scripts" / "build_review.py"),
                        str(SKILL / "references" / "test_cases.json"), str(answers), str(tmp_path / "o.xlsx")],
                       capture_output=True, text=True)
    assert r.returncode == 2
