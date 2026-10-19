"""The decision engine: can we integrate, and does the API work."""
import json
import subprocess
import sys

from conftest import SKILL


def run(br, data, answers, status_map=None):
    return br.evaluate(data, answers, status_map or {})


def test_perfect_vendor(br, data, all_yes):
    answers, sm = all_yes
    ev = run(br, data, answers, sm)
    assert ev["decision"] == "Yes, we can integrate"
    assert ev["api_works"].startswith("Works on sandbox")


def test_nothing_documented_is_no(br, data):
    ev = run(br, data, {})
    assert ev["decision"].startswith("No") and ev["counts"]["Missing"] == len(data["must_haves"])


def test_no_place_order_means_no(br, data, all_yes):
    answers, sm = all_yes
    answers["ORD-01"] = {"provided": "Not available", "details": ""}
    assert run(br, data, answers, sm)["decision"].startswith("No")


def test_missing_balance_and_other_nice_to_haves_do_not_block(br, data, all_yes):
    answers, sm = all_yes
    for t in data["tests"]:
        if t["need"] != "Must-have":
            answers[t["id"]] = {"provided": "Not available", "details": ""}
    assert run(br, data, answers, sm)["decision"] == "Yes, we can integrate"


def test_open_must_have_is_likely_yes(br, data, all_yes):
    answers, sm = all_yes
    answers["STS-01"] = {"provided": "Open", "details": "one example only"}
    assert run(br, data, answers, sm)["decision"].startswith("Likely yes")


def test_documented_but_untested_is_yes_on_paper(br, data, all_yes):
    answers, sm = all_yes
    answers["ORD-01"]["live"] = "Not run"
    ev = run(br, data, answers, sm)
    assert ev["decision"].startswith("Yes on paper")
    assert ev["api_works"].startswith("Partly tested")


def test_sandbox_failure_on_must_have_is_no(br, data, all_yes):
    answers, sm = all_yes
    answers["ORD-02"]["live"] = "Fail"
    ev = run(br, data, answers, sm)
    assert ev["decision"].startswith("No") and ev["api_works"].startswith("Problems found")


def test_sandbox_failure_on_alternative_check_still_blocks(br, data, all_yes):
    answers, sm = all_yes
    answers["IDM-02"]["live"] = "Fail"  # duplicates create a second order, even though lookup exists
    assert run(br, data, answers, sm)["decision"].startswith("No")


def test_webhook_or_polling_is_enough(br, data, all_yes):
    answers, sm = all_yes
    answers["WHK-01"] = {"provided": "No", "details": "no webhooks"}
    assert run(br, data, answers, sm)["decision"] == "Yes, we can integrate"
    answers["POL-01"] = {"provided": "Not available", "details": ""}
    assert run(br, data, answers, sm)["decision"].startswith("No")


def test_sandbox_only_checks_use_sandbox_result(br, data):
    ev = run(br, data, {"AUTH-04": {"live": "Pass"}, "ORD-12": {"live": "Fail"}})
    assert ev["provided"]("AUTH-04") == "Yes" and ev["provided"]("ORD-12") == "No"


def test_risk_answer_is_flagged(br, data, all_yes):
    answers, sm = all_yes
    answers["WHK-05"] = {"provided": "No", "details": "signature mandatory"}
    ev = run(br, data, answers, sm)
    assert [t["id"] for t in ev["escalations"]] == ["WHK-05"]
    assert "change on our side" in ev["reason"]


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
    assert "Can we integrate?" in text and "## Must-haves" in text


def test_cli_prints_boxed_report(tmp_path):
    from conftest import ROOT
    r = subprocess.run([sys.executable, str(SKILL / "scripts" / "build_review.py"),
                        str(SKILL / "references" / "test_cases.json"), str(ROOT / "examples" / "printstop" / "review.json"),
                        str(tmp_path / "o.xlsx")], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    assert r.stdout.lstrip().startswith("**")  # short summary comes first
    for label in ("**Context**", "**What their API has**", "**What needs to be done**"):
        assert label in r.stdout
    assert r.stdout.index("**What needs to be done**") < r.stdout.index("VERDICT")
    for label in ("VERDICT", "API TEST", "PLACE ORDER", "SAFE RETRY", "AREAS", "ASK THE VENDOR", "OUTPUT"):
        assert label in r.stdout
    assert "Likely yes" in r.stdout and "—" not in r.stdout
    for label in ("Build Feasibility", "AUTH", "IDEMPOTENCY", "STATUS MAP", "PRE-CONFIRM FAIL", "BUILD FILES", "HANDOFF"):
        assert label in r.stdout


def test_feasibility_derived_without_overrides(br, data, all_yes):
    answers, sm = all_yes
    for tid in ("WHK-01", "WHK-03", "WHK-04", "WHK-05", "BAL-01"):  # no webhooks, no balance API
        answers[tid] = {"provided": "Not available", "details": ""}
    ev = br.evaluate(data, answers, sm)
    rows = {line: icon for line, icon, _ in br.feasibility({"answers": answers}, ev)}
    assert rows["ORDER"] == "✅" and rows["WEBHOOK"] == "➖" and rows["BALANCE"] == "➖"


def test_cli_exits_nonzero_on_invalid(tmp_path):
    answers = tmp_path / "a.json"
    answers.write_text(json.dumps({"answers": {"ORD-02": {"provided": "Yes"}}}))
    r = subprocess.run([sys.executable, str(SKILL / "scripts" / "build_review.py"),
                        str(SKILL / "references" / "test_cases.json"), str(answers), str(tmp_path / "o.xlsx")],
                       capture_output=True, text=True)
    assert r.returncode == 2
