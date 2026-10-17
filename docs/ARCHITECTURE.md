# How it fits together

```
vendor doc(s)
   │
   ▼  /merch-vendor-agent (ANALYZE)
   1 read docs: text, every image, links
   2 secret scan
   3 quirk hunt
   4 answer 130 checks, then a second pass
   5 4 independent reviewers (architecture, failures, security, ops/money)
   6 review.json ──► build_review.py ──► <Vendor>_Review.xlsx   ◄── the one output
                                         Summary | Vendor questions | Tech | All checks
On request:
   "full tech spec"   ──► <Vendor>_TECH_SPEC.md (checked by lint_tech_spec.py)
   "postman"/"config" ──► build_tech_pack.py ──► build/ files
   "run live"         ──► sandbox results into the same workbook
   yes decision       ──► /merch-sensei builds the connector
```

| Path | Role |
|---|---|
| `.claude/commands/merch-vendor-agent.md` | The agent: modes, steps, rules |
| `.claude/skills/merch-vendor-review/SKILL.md` | The skill (also works on its own or uploaded to claude.ai) |
| `references/test_cases.json` | All checks and the 7 must-have groups |
| `references/platform_contract.md` | What our system needs from a vendor, and why |
| `references/doc_intake.md` | How to read each doc type; synonyms |
| `references/platform_playbooks.md` | Extra questions for Magento / Shopify / WooCommerce vendors |
| `references/templates/` | Tech spec template |
| `scripts/build_review.py` | Checks review.json, makes the decision, builds the one workbook |
| `scripts/scan_secrets.py` | Finds credentials, prints them redacted |
| `scripts/build_tech_pack.py` | tech.json → vendor config draft, Postman collection, env template |
| `references/connector_reference.md` | Build depth: lifecycle, class contract, config rules, limits, debug signals |
| `tools/gen_test_catalog.py` | Builds `docs/TEST_CATALOG.md` |
| `tests/` | Automated tests (run in CI) |
| `examples/printstop/` | Example: review.json, the workbook, optional full tech spec |
