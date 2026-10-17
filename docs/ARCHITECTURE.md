# Architecture

```
vendor doc(s) ──► /merch-vendor-agent (ANALYZE)
                    │
  Phase 0-1  intake, extract text + images + links, platform fingerprint ──► 00_doc_inventory.md
  Phase 2    scan_secrets.py (+ look at images) ──────────────────────────► SEC-07
  Phase 3    lifecycle coverage map ───────────────────────────────────────► 01_coverage_map.md
  Phase 4    130 test cases, 2 passes (fill, adversarial) ─────────────────► answers.json
  Phase 5    status map + field mapping ───────────────────────────────────► 02_field_mapping.md
  Phase 6    LIVE: Postman CLI on staging only ────────────────────────────► live results + fixtures
  Phase 7    build_review.py (validate → score → gate → feasibility) ──────► .xlsx + REPORT.md
  Phase 8    principal-engineer write-up ──────────────────────────────────► ANALYSIS.md
  Phase 9    COMMS ────────────────────────────────────────────────────────► VENDOR_EMAIL / JIRA / MANAGER
  Phase 10   self-QA (secrets, numbers, blockers, git)
                    │
                    ▼ verdict Ready / Ready with conditions
                 HANDOFF_MERCH_SENSEI.md ──► /merch-sensei ONBOARD (engineering builds)
```

## Components
| Path | Role |
|---|---|
| `.claude/commands/merch-vendor-agent.md` | The agent: modes, phases, rules, deliverables |
| `.claude/skills/merch-vendor-review/SKILL.md` | Skill entry point (also works standalone / uploaded to claude.ai) |
| `references/test_cases.json` | Single source of truth: tests, gate, feasibility map |
| `references/platform_contract.md` | Why each test exists (Plum code contract) |
| `references/doc_intake.md` | How to read each doc format; synonyms |
| `references/platform_playbooks.md` | Magento/Shopify/WooCommerce question sets |
| `references/templates/` | Output templates |
| `scripts/build_review.py` | Validation + scoring + workbook + Markdown |
| `scripts/scan_secrets.py` | Redacting secret scanner |
| `tools/gen_test_catalog.py` | Generates `docs/TEST_CATALOG.md` |
| `tests/` | pytest suite (CI) |
| `examples/` | Redacted reference reviews |
