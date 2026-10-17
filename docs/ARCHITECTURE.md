# How it fits together

```
vendor doc(s) ──► /merch-vendor-agent
  1 read docs: text, images, links ─────────────► 00_doc_inventory.md
  2 secret scan (scan_secrets.py + images)
  3 answer 130 checks, then a second pass ──────► answers.json
  4 status and field mapping ───────────────────► 01_field_mapping.md
  5 sandbox tests (Postman CLI, sandbox only) ──► sandbox results
  6 build_review.py ────────────────────────────► workbook + REPORT.md
  7 write-up ───────────────────────────────────► ANALYSIS.md
  8 messages ───────────────────────────────────► VENDOR_EMAIL / JIRA_COMMENT / SUMMARY
  9 final checks
                    │ decision Yes / Yes on paper
                    ▼
            HANDOFF_MERCH_SENSEI.md ──► /merch-sensei builds the connector
```

| Path | Role |
|---|---|
| `.claude/commands/merch-vendor-agent.md` | The agent: modes, steps, rules |
| `.claude/skills/merch-vendor-review/SKILL.md` | The skill (also works on its own or uploaded to claude.ai) |
| `references/test_cases.json` | All checks and the 7 must-have groups |
| `references/platform_contract.md` | What our system needs from a vendor, and why |
| `references/doc_intake.md` | How to read each doc type; synonyms |
| `references/platform_playbooks.md` | Extra questions for Magento / Shopify / WooCommerce vendors |
| `references/templates/` | Output templates |
| `scripts/build_review.py` | Checks answers, makes the decision, builds the workbook and REPORT.md |
| `scripts/scan_secrets.py` | Finds credentials, prints them redacted |
| `tools/gen_test_catalog.py` | Builds `docs/TEST_CATALOG.md` |
| `tests/` | Automated tests (run in CI) |
| `examples/printstop/` | A complete example review |
