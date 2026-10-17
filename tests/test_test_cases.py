"""Integrity of the check list itself."""
import collections


def test_ids_unique(data):
    ids = [t["id"] for t in data["tests"]]
    assert not [i for i, c in collections.Counter(ids).items() if c > 1]


def test_required_fields_and_values(data):
    for t in data["tests"]:
        assert {"id", "section", "need", "verify", "test", "pass", "platform"} <= set(t), t["id"]
        assert t["need"] in ("Must-have", "Important", "Nice-to-have"), t["id"]
        assert t["verify"] in ("Doc", "Live", "Doc+Live"), t["id"]
        assert t["test"].strip() and t["pass"].strip() and t["platform"].strip(), t["id"]


def test_every_v1_question_still_covered(data):
    legacy = {q for t in data["tests"] for q in t.get("legacy", [])}
    assert set(range(1, 42)) <= legacy


def test_must_have_tier_matches_must_have_groups(data):
    in_groups = {i for g in data["must_haves"] for i in g.get("all", []) + g.get("any", [])}
    tier = {t["id"] for t in data["tests"] if t["need"] == "Must-have"}
    assert in_groups == tier


def test_place_order_is_must_and_balance_is_not(data):
    need = {t["id"]: t["need"] for t in data["tests"]}
    assert need["ORD-01"] == need["ORD-02"] == "Must-have"
    assert all(need[i] == "Nice-to-have" for i in ("BAL-01", "BAL-02", "BAL-03", "BAL-04"))


def test_risk_checks(data):
    assert {t["id"] for t in data["tests"] if t.get("risk")} == {"ORD-13", "WHK-04", "WHK-05", "WHK-06"}
