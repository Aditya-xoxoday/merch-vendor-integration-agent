# Merchandise Vendor Integration Agent

Give it a merchandise vendor's API document (PDF, Word, Postman, OpenAPI/Swagger, docs site or
screenshots) and it answers two questions:

1. **Can we integrate?** Yes / Yes on paper / Likely yes / No, decided only by 7 must-haves.
2. **Does the API work?** Based on tests on the vendor's sandbox.

Anything else that is missing (balance API, settlement report, rate limits...) is listed as a gap
with a question for the vendor. Those gaps never block on their own. **No Place Order API means
No. No balance API is fine.**

This agent reviews vendors. [merch-sensei](https://github.com/abhishekkxoxo/merch-sensei)
builds the connector once the answer is yes.

## The 7 must-haves
| # | Must-have |
|---|---|
| 1 | Place an order and get an order ID back |
| 2 | Our address fields fit their order format |
| 3 | The product ID from their catalogue is what the order takes |
| 4 | Get the order status (status list, lookup, and webhook or polling) |
| 5 | Get courier and tracking number after dispatch |
| 6 | Retry safely without creating duplicate orders |
| 7 | Secure login that works |

See [docs/DECISION.md](docs/DECISION.md) for exactly how the result is worked out.

## Modes
| Mode | Say | You get |
|---|---|---|
| **ANALYZE** (default) | share a doc and say "analyze" | Full review pack |
| **LIVE** | "run live" with sandbox credentials | Sandbox test results added |
| **COMMS** | "vendor email", "jira comment", "summary" | Ready-to-send messages |
| **HANDOFF** | "hand off" (when the answer is yes) | Build brief for merch-sensei |
| **DIFF** | a new version of a reviewed doc | What changed, new decision |

## What a review produces
| File | Contents |
|---|---|
| `ANALYSIS.md` | Decision, must-haves, what we need from the vendor, other gaps, build notes, next steps |
| `REPORT.md` | The same decision plus every gap and coverage by area |
| `<Vendor>_Review.xlsx` | Summary sheet, and a Checks sheet with all 130 checks, evidence and sandbox results |
| `00_doc_inventory.md` | Every source, endpoint, image and hidden hint |
| `01_field_mapping.md` | Vendor fields mapped to our order and product fields |
| `VENDOR_EMAIL.md`, `JIRA_COMMENT.md`, `SUMMARY.md` | Short, plain messages |
| `HANDOFF_MERCH_SENSEI.md` | Build brief (handoff mode) |

Example: [examples/printstop/ANALYSIS.md](examples/printstop/ANALYSIS.md).

## Repository layout
```
merch-vendor-integration-agent/
├── .claude/
│   ├── commands/merch-vendor-agent.md     # the agent
│   └── skills/merch-vendor-review/        # the skill (also works on claude.ai)
│       ├── SKILL.md
│       ├── references/
│       │   ├── test_cases.json            # 130 checks + 7 must-have groups
│       │   ├── platform_contract.md       # what our system needs, and why
│       │   ├── doc_intake.md              # how to read each doc type; synonyms
│       │   ├── platform_playbooks.md      # Magento / Shopify / WooCommerce questions
│       │   ├── xoxoday_api.md
│       │   ├── example_answers.json
│       │   └── templates/                 # analysis, vendor email, Jira, summary
│       └── scripts/
│           ├── build_review.py            # decision + workbook + REPORT.md
│           └── scan_secrets.py            # finds leaked credentials (redacted)
├── docs/  DECISION.md  ARCHITECTURE.md  GAP_ANALYSIS.md  TEST_CATALOG.md
├── examples/printstop/                    # full example review
├── tests/                                 # automated tests (CI)
├── tools/gen_test_catalog.py
├── .github/workflows/ci.yml
├── SECURITY.md  CONTRIBUTING.md  CHANGELOG.md  requirements-dev.txt
└── reviews/                               # your work (gitignored)
```

## The checks
130 checks in 16 areas: 14 must-have, 89 important and 27 nice-to-have. The areas are:
documentation, login, environments, catalogue, pricing and balance, order placement, duplicates,
order status, webhooks, polling, tracking, returns, reconciliation, errors and limits, security,
and support. Full list: [docs/TEST_CATALOG.md](docs/TEST_CATALOG.md).

## Install
**Claude Code:** clone this repo (or copy `.claude/` into your project) and run
`/merch-vendor-agent`.

**claude.ai:** zip `.claude/skills/merch-vendor-review/` and upload it as a skill.

**Tests:**
```bash
pip install -r requirements-dev.txt
pytest -q tests
```

## Rules
- Evidence or nothing: if the docs say nothing, the answer is "Not available". Nothing is guessed.
- Sandbox only. Production is never called.
- Secrets are never copied, and vendor docs never go into git ([SECURITY.md](SECURITY.md)).

## Related
[merch-sensei](https://github.com/abhishekkxoxo/merch-sensei) ·
[akatsuki-gift-cards](https://github.com/abhishekkxoxo/akatsuki-gift-cards) ·
[topup-sensei](https://github.com/abhishekkxoxo/topup-sensei)
