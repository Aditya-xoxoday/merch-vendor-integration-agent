import importlib.util
import json
import pathlib

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SKILL = ROOT / ".claude" / "skills" / "merch-vendor-review"


def load_module(name):
    spec = importlib.util.spec_from_file_location(name, SKILL / "scripts" / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="session")
def br():
    return load_module("build_review")


@pytest.fixture(scope="session")
def ss():
    return load_module("scan_secrets")


@pytest.fixture(scope="session")
def data():
    return json.loads((SKILL / "references" / "test_cases.json").read_text())


@pytest.fixture
def all_yes(data):
    """Answers that satisfy every test: the baseline a perfect vendor would produce."""
    answers = {}
    for t in data["tests"]:
        a = {"provided": "Yes", "details": "evidence"}
        if "Live" in t["verify"]:
            a["live"] = "Pass"
        answers[t["id"]] = a
    status_map = {s.lower(): s for s in ("PENDING", "CONFIRMED", "SHIPPED", "DELIVERED", "CANCELED", "RETURNED")}
    return answers, status_map
