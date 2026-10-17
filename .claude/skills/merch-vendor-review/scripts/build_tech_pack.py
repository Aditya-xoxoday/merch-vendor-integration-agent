#!/usr/bin/env python3
"""
Build the machine-readable part of a tech pack from a reviewed tech.json.

Usage:
    python3 build_tech_pack.py <tech.json> <out_dir>

Writes to <out_dir>:
    vendor_config.draft.json                      merch-sensei vendorConfigs shape, placeholder credentials
    <ClassName>.postman_collection.json           Postman v2.1, every endpoint + negative cases, with tests
    <ClassName>.postman_environment.template.json placeholders only; copy outside the repo and fill in

tech.json shape (see examples/printstop/tech/tech.json):
    {
      "vendor":  {"className": "Printstop", "model": "printstop_merchandise", "vendorId": "<vendorId>",
                  "vendorType": "fixedSku", "async": true, "sandboxBaseUrl": "https://sandbox.example"},
      "credentials": {"<tokenKey>": {"clientId": "{{client_id}}", ...}},  # placeholders ONLY; one key per token
      "token":   {"method": "GET", "path": "...", "query": {...}, "headers": {...},
                  "tokenField": "access_token"} | null,
      "headers": {"Authorization": "Bearer {{access_token}}", ...},  # business-call headers
      "redactHeaders": ["client-secret", ...],
      "endpoints": [{"key": "placeOrder", "name": "...", "method": "POST", "path": "...", "query": {...},
                     "body": {...} | null,   # "{{int:var}}" = numeric Postman variable
                     "expectStatus": 200, "expectFields": ["orders_id"],
                     "saveVar": {"orders_id": "orders_id"},
                     "negatives": [{"name": "...", "query": {...}, "body": {...}, "headers": {...},
                                    "expectStatus": 409, "expectFields": ["orders"]}]}],
      "polling": {"endpoint": "orderStatus", "statusField": "orders_status"} | null,
      "status_map": {"in production": "CONFIRMED"}
    }

Exits 2 if a credential is not a placeholder, a status target is invalid, or the base URL is not
marked as sandbox (contains 'staging', 'sandbox', 'test' or 'uat').
"""
import copy
import json
import os
import re
import sys

DELIVERY_STATUSES = ("PENDING", "CONFIRMED", "SHIPPED", "DELIVERED", "CANCELED", "RETURNED")
PLACEHOLDER = re.compile(r"^(\{\{[a-z0-9_]+\}\}|<[^>]+>)$", re.I)
SANDBOX_HINT = re.compile(r"staging|sandbox|test|uat", re.I)
VAR = re.compile(r"\{\{(?:int:)?([a-z0-9_]+)\}\}", re.I)
INT_VAR = re.compile(r'"\{\{int:([a-z0-9_]+)\}\}"', re.I)


def _leaves(obj, prefix):
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield from _leaves(v, f"{prefix}.{k}")
    else:
        yield prefix, obj


def validate(t):
    errors = []
    creds = t.get("credentials", {})
    for path, v in _leaves(creds, "credentials"):
        if not PLACEHOLDER.match(str(v)):
            errors.append(f"{path} must be a placeholder like {{{{name}}}}, never a real value")
    if t.get("token"):
        # /vendor/updateAccessToken calls fetchAccessToken once PER KEY of configs.credentials,
        # so a token vendor needs exactly one key per token, each holding an object of fields.
        bad = [k for k, v in creds.items() if not isinstance(v, dict)]
        if bad:
            errors.append(f"token vendor: credentials must be {{<tokenKey>: {{fields}}}}; flat keys {bad} would each "
                          "trigger a separate fetchAccessToken call")
    for s, target in t.get("status_map", {}).items():
        if target not in DELIVERY_STATUSES:
            errors.append(f"status_map '{s}' -> '{target}' must be one of {DELIVERY_STATUSES}")
        if s != s.lower():
            errors.append(f"status_map key '{s}' must be lowercase (the base class lowercases statuses)")
    if not SANDBOX_HINT.search(t["vendor"].get("sandboxBaseUrl", "")):
        errors.append("vendor.sandboxBaseUrl must be a sandbox/staging host (never production)")
    keys = [e["key"] for e in t["endpoints"]]
    if len(keys) != len(set(keys)):
        errors.append("endpoint keys must be unique")
    if t.get("polling") and t["polling"]["endpoint"] not in keys:
        errors.append("polling.endpoint must be one of the endpoint keys")
    return errors


def vendor_config(t):
    v = t["vendor"]
    ep = {e["key"]: e for e in t["endpoints"]}

    def url(e):
        q = "&".join(f"{k}={val}" for k, val in (e.get("query") or {}).items())
        # Postman {{var}} -> {var}: in VI these values are filled in by the class (e.g. getRefetchOrderReqOptions)
        return VAR.sub(r"{\1}", e["path"] + (("?" + q) if q else ""))

    cfg = {
        "vendorData": {"vendorId": v["vendorId"], "vendorType": v["vendorType"], "name": v["className"],
                       "model": v["model"], "merchandiseVendor": True, "iswebhookConfiration": bool(v["async"])},
        "vendorTableMapping": {"table": f"{v['model']}_products", "extraInfo": False,
                               "countryColumn": "", "currencyColumn": ""},
        "placeOrderReqConfigs": {"url": url(ep["placeOrder"]), "method": ep["placeOrder"]["method"], "body": {}},
        "webhookConfigs": {"isDataEncrypted": False, "orderStatus": {k: v2 for k, v2 in t["status_map"].items()}},
        "configs": {"baseUrl": v["sandboxBaseUrl"], "maxApiAtaTime": 1, "maxCardsPerRequest": 1,
                    "pickConfigCustomerInfo": False, "credentials": t["credentials"]},
    }
    if v["vendorType"] == "fixedSku":
        cfg["vendorTableMapping"]["skuTable"] = f"{v['model']}_product_to_denominations"
    if t.get("polling"):
        e = ep[t["polling"]["endpoint"]]
        cfg["refetchOrderReqConfigs"] = {"url": url(e), "method": e["method"]}
    if t.get("token"):
        tk = t["token"]
        cfg["accessTokenConfigs"] = {"url": url(tk), "method": tk["method"]}
    if "productListing" in ep:
        cfg["productListingConfigs"] = {"method": ep["productListing"]["method"], "getProducts": url(ep["productListing"])}
    order = ["vendorData", "vendorTableMapping", "placeOrderReqConfigs", "refetchOrderReqConfigs",
             "accessTokenConfigs", "webhookConfigs", "productListingConfigs", "configs"]
    return {str(v["vendorId"]): {k: cfg[k] for k in order if k in cfg}}


def pm_request(name, method, path, query, headers, body, expect_status, expect_fields, save=None):
    query = query or {}
    raw = "{{baseUrl}}" + path + (("?" + "&".join(f"{k}={v}" for k, v in query.items())) if query else "")
    tests = [f"pm.test('HTTP {expect_status}', () => pm.response.to.have.status({expect_status}));"]
    if expect_fields:
        tests.append("const j = pm.response.json();")
        tests += [f"pm.test('has {f}', () => pm.expect(j).to.have.property('{f}'));" for f in expect_fields]
    for var, field in (save or {}).items():
        tests.append(f"if (pm.response.code === {expect_status}) pm.collectionVariables.set('{var}', pm.response.json()['{field}']);")
    req = {"method": method, "header": [{"key": k, "value": v} for k, v in headers.items()],
           "url": {"raw": raw, "host": ["{{baseUrl}}"], "path": [p for p in path.split("/") if p],
                   "query": [{"key": k, "value": str(v)} for k, v in query.items()]}}
    if body is not None:
        raw_body = INT_VAR.sub(r"{{\1}}", json.dumps(body, indent=2))  # "{{int:x}}" -> {{x}} (unquoted number)
        req["body"] = {"mode": "raw", "raw": raw_body, "options": {"raw": {"language": "json"}}}
    return {"name": name, "event": [{"listen": "test", "script": {"type": "text/javascript", "exec": tests}}],
            "request": req}


def collection(t):
    v = t["vendor"]
    items = []
    if t.get("token"):
        tk = t["token"]
        items.append(pm_request("00 Auth: get token", tk["method"], tk["path"], tk.get("query"), tk.get("headers", {}),
                                None, 200, [tk["tokenField"]], {"access_token": tk["tokenField"]}))
        bad = {k: ("{{bad_" + k.lower().replace("-", "_") + "}}" if "secret" in k.lower() else val)
               for k, val in tk.get("headers", {}).items()}
        items.append(pm_request("00 Auth: bad secret -> 401", tk["method"], tk["path"], tk.get("query"), bad, None, 401, []))
    for i, e in enumerate(t["endpoints"], 1):
        headers = {**t.get("headers", {}), **e.get("headers", {})}
        if e.get("body") is not None:
            headers.setdefault("Content-Type", "application/json")
        items.append(pm_request(f"{i:02d} {e['name']}", e["method"], e["path"], e.get("query"), headers, e.get("body"),
                                e.get("expectStatus", 200), e.get("expectFields", []), e.get("saveVar")))
        for n in e.get("negatives", []):
            body = copy.deepcopy(n["body"]) if "body" in n else e.get("body")
            items.append(pm_request(f"{i:02d} {e['name']}: {n['name']}", e["method"], e["path"],
                                    {**(e.get("query") or {}), **n.get("query", {})}, {**headers, **n.get("headers", {})},
                                    body, n["expectStatus"], n.get("expectFields", [])))
    used = set()
    for it in items:
        used |= set(VAR.findall(json.dumps(it)))
    return {"info": {"name": f"{v['className']} sandbox contract tests",
                     "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"},
            "item": items,
            "variable": [{"key": k, "value": ""} for k in sorted(used) if k in ("access_token", "orders_id")]}, used


def environment(t, used):
    values = [{"key": "baseUrl", "value": t["vendor"]["sandboxBaseUrl"], "enabled": True}]
    for k in sorted(used - {"baseUrl", "access_token", "orders_id"}):
        values.append({"key": k, "value": f"<fill in outside the repo: {k}>", "enabled": True})
    return {"name": f"{t['vendor']['className']} sandbox (TEMPLATE: copy outside the repo before filling)", "values": values}


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    with open(sys.argv[1]) as f:
        t = json.load(f)
    errors = validate(t)
    if errors:
        for e in errors:
            print(f"ERROR {e}")
        sys.exit(2)
    out = sys.argv[2]
    os.makedirs(out, exist_ok=True)
    name = t["vendor"]["className"]
    coll, used = collection(t)
    files = {
        "vendor_config.draft.json": vendor_config(t),
        f"{name}.postman_collection.json": coll,
        f"{name}.postman_environment.template.json": environment(t, used),
    }
    for fn, obj in files.items():
        with open(os.path.join(out, fn), "w") as f:
            json.dump(obj, f, indent=2)
            f.write("\n")
        print(f"Wrote {os.path.join(out, fn)}")
    print(f"{len(coll['item'])} Postman requests. Run: postman collection run {name}.postman_collection.json "
          f"-e <filled env outside the repo>")


if __name__ == "__main__":
    main()
