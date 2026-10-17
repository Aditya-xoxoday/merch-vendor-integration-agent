"""The tech pack generator: placeholders only, sandbox only, merch-sensei config shape."""
import copy
import json
import subprocess
import sys

import pytest

from conftest import ROOT, SKILL, load_module

TECH = json.loads((ROOT / "tests" / "fixtures" / "printstop_tech.json").read_text())


@pytest.fixture(scope="module")
def tp():
    return load_module("build_tech_pack")


def test_example_is_valid(tp):
    assert tp.validate(TECH) == []


def test_real_credential_rejected(tp):
    t = copy.deepcopy(TECH)
    t["credentials"]["printstop"]["clientSecret"] = "a1b2c3d4e5f6g7h8"
    assert any("clientSecret" in e for e in tp.validate(t))


def test_flat_credentials_rejected_for_token_vendor(tp):
    t = copy.deepcopy(TECH)
    t["credentials"] = {"clientId": "{{client_id}}", "clientSecret": "{{client_secret}}"}
    assert any("fetchAccessToken" in e for e in tp.validate(t))


def test_production_url_rejected(tp):
    t = copy.deepcopy(TECH)
    t["vendor"]["sandboxBaseUrl"] = "https://api.vendor.com"
    assert any("sandbox" in e for e in tp.validate(t))


def test_bad_status_target_and_case_rejected(tp):
    t = copy.deepcopy(TECH)
    t["status_map"] = {"Failed": "ORDER_FAILED"}
    errs = " ".join(tp.validate(t))
    assert "ORDER_FAILED" in errs and "lowercase" in errs


def test_vendor_config_shape(tp):
    cfg = next(iter(tp.vendor_config(TECH).values()))
    vd = cfg["vendorData"]
    assert vd["merchandiseVendor"] is True and vd["iswebhookConfiration"] is True and vd["vendorType"] == "fixedSku"
    assert "skuTable" in cfg["vendorTableMapping"]
    assert {"baseUrl", "maxApiAtaTime", "maxCardsPerRequest"} <= set(cfg["configs"])
    assert "{{" not in json.dumps({k: v for k, v in cfg.items() if k != "configs"})  # class-filled vars rendered {x}
    assert set(cfg["webhookConfigs"]["orderStatus"].values()) <= {"PENDING", "CONFIRMED", "SHIPPED", "DELIVERED", "CANCELED", "RETURNED"}


def test_collection_covers_every_endpoint_and_negative(tp):
    coll, _ = tp.collection(TECH)
    expected = 2 + sum(1 + len(e.get("negatives", [])) for e in TECH["endpoints"])
    assert len(coll["item"]) == expected
    order = next(i for i in coll["item"] if i["name"].endswith("Place order"))
    assert '"corporate_id": {{corporate_id}}' in order["request"]["body"]["raw"]  # numeric var unquoted


def test_cli_writes_three_files(tmp_path):
    r = subprocess.run([sys.executable, str(SKILL / "scripts" / "build_tech_pack.py"),
                        str(ROOT / "tests" / "fixtures" / "printstop_tech.json"), str(tmp_path)],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
    names = {p.name for p in tmp_path.iterdir()}
    assert names == {"vendor_config.draft.json", "Printstop.postman_collection.json",
                     "Printstop.postman_environment.template.json"}
    env = json.loads((tmp_path / "Printstop.postman_environment.template.json").read_text())
    assert all(v["value"].startswith(("<fill in", "https://")) for v in env["values"])
