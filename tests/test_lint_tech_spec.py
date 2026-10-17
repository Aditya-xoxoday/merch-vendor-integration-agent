"""The tech spec quality gate."""
import json
import subprocess
import sys

from conftest import ROOT, SKILL, load_module

SPEC = ROOT / "examples" / "printstop" / "Printstop_TECH_SPEC.md"


def test_printstop_spec_passes(data):
    lt = load_module("lint_tech_spec")
    answers = json.loads((ROOT / "examples" / "printstop" / "review.json").read_text())
    assert lt.lint(SPEC.read_text(), answers, data) == []


def test_shallow_spec_fails():
    lt = load_module("lint_tech_spec")
    problems = lt.lint("# X\n\n## 1. Feasibility\nAUTH ok\n")
    assert any("missing section" in p for p in problems) and any("mermaid" in p for p in problems)


def test_open_must_have_must_be_mentioned(data):
    lt = load_module("lint_tech_spec")
    text = SPEC.read_text().replace("STS-01", "STS-XX")
    answers = json.loads((ROOT / "examples" / "printstop" / "review.json").read_text())
    assert any("STS-01" in p for p in lt.lint(text, answers, data))


def test_cli_exit_code():
    r = subprocess.run([sys.executable, str(SKILL / "scripts" / "lint_tech_spec.py"), str(SPEC)],
                       capture_output=True, text=True)
    assert r.returncode == 0 and "TECH_SPEC OK" in r.stdout
