"""Committed examples must stay valid and secret-free."""
import json
import pathlib

from conftest import ROOT, SKILL


def test_example_answers_validate(br, data):
    for path in [SKILL / "references" / "example_answers.json", *ROOT.glob("examples/*/answers.json")]:
        errors, _ = br.validate(data["tests"], json.loads(path.read_text()))
        assert not errors, (path, errors)


def test_repo_has_no_secrets(ss):
    skip = {".git", "reviews", "__pycache__"}
    for p in ROOT.rglob("*"):
        if p.is_file() and not skip & set(p.parts) and p.suffix in {".md", ".json", ".txt", ".py", ".yml"}:
            if p.name in {"test_scan_secrets.py", "scan_secrets.py"}:
                continue
            assert ss.scan(p.read_text(errors="replace")) == [], p


def test_catalog_doc_in_sync(data):
    import importlib.util
    spec = importlib.util.spec_from_file_location("gen", ROOT / "tools" / "gen_test_catalog.py")
    gen = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gen)
    assert (ROOT / "docs" / "TEST_CATALOG.md").read_text() == gen.render(data), "run python3 tools/gen_test_catalog.py"
