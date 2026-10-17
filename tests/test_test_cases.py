"""Integrity of the test-case catalogue itself."""
import collections

SECTIONS_MIN = 16


def test_ids_unique(data):
    ids = [t["id"] for t in data["tests"]]
    assert not [i for i, c in collections.Counter(ids).items() if c > 1]


def test_required_fields_and_values(data):
    for t in data["tests"]:
        assert {"id", "section", "priority", "verify", "test", "pass", "platform"} <= set(t), t["id"]
        assert t["priority"] in data["priority_weights"], t["id"]
        assert t["verify"] in ("Doc", "Live", "Doc+Live"), t["id"]
        assert t["test"].strip() and t["pass"].strip() and t["platform"].strip(), t["id"]


def test_every_v1_question_still_covered(data):
    legacy = {q for t in data["tests"] for q in t.get("legacy", [])}
    assert set(range(1, 42)) <= legacy


def test_gate_and_feasibility_reference_real_tests(data):
    ids = {t["id"] for t in data["tests"]}
    for g in data["gate"]:
        assert set(g.get("all", [])) | set(g.get("any", [])) <= ids, g["item"]
    for line, refs in data["feasibility"].items():
        assert set(refs) <= ids, line


def test_gate_tests_are_p0(data):
    by_id = {t["id"]: t for t in data["tests"]}
    for g in data["gate"]:
        for tid in g.get("all", []) + g.get("any", []):
            assert by_id[tid]["priority"] == "P0", tid


def test_risk_tests_exist(data):
    assert {t["id"] for t in data["tests"] if t.get("risk")} == {"ORD-13", "WHK-04", "WHK-05", "WHK-06"}


def test_section_count(data):
    assert len({t["section"] for t in data["tests"]}) >= SECTIONS_MIN
