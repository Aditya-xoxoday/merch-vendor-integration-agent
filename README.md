# Merchandise Vendor Integration Agent

A Claude Code agent that takes **any merchandise vendor API document** (PDF, Word, Postman,
OpenAPI/Swagger, docs site, screenshots) and produces an enterprise-grade integration analysis
for the Xoxoday/Plum platform. The analysis is evidence-based, scored against 130 test cases,
gated, security-scanned and live-verified on staging. Its output is ready for PM, engineering,
management and the vendor.

It is the **evaluation** front end to [merch-sensei](https://github.com/abhishekkxoxo/merch-sensei),
which **builds** the connector. This agent decides whether and how a vendor can be integrated, and
it hands merch-sensei a pre-filled onboarding brief.

| Mode | Say | You get |
|---|---|---|
| **ANALYZE** (default) | drop a doc + "analyze" | Full analysis pack (below) |
| **LIVE** | "run live" + staging credentials | Postman CLI run on staging, merged into the review |
| **COMMS** | "vendor email" / "jira comment" / "summary for Piyush" | Ready-to-send messages |
| **HANDOFF** | "hand off" (when Ready) | `HANDOFF_MERCH_SENSEI.md` for engineering |
| **DIFF** | a revised doc for a vendor already reviewed | What changed, and the new verdict |

## What one analysis produces

| File | For | Contents |
|---|---|---|
| `ANALYSIS.md` | PM, EM, management | Verdict, coverage, top blockers, security, engineering view, risks, options, next steps |
| `REPORT.md` | everyone | Scorecard, derived gate, merch-sensei feasibility lines, section readiness, evidence, vendor questions |
| `<Vendor>_Merchandise_Review.xlsx` | PM / audit | Review sheet (130 tests with evidence and live results) and Report sheet |
| `00_doc_inventory.md` | reviewer | Every source, endpoint, image and hidden hint |
| `01_coverage_map.md` | engineering | Endpoints by lifecycle stage; holes |
| `02_field_mapping.md` | engineering | Vendor fields mapped to Plum shipping and product fields |
| `VENDOR_EMAIL.md`, `JIRA_COMMENT.md`, `MANAGER_SUMMARY.md` | comms | House style: plain, no em dashes |
| `HANDOFF_MERCH_SENSEI.md` | engineering | merch-sensei Batch 1-7 answers |

See the full worked example: [examples/justlounge/ANALYSIS.md](examples/justlounge/ANALYSIS.md).

## Repository structure

```
merch-vendor-integration-agent/
├── .claude/
│   ├── commands/
│   │   └── merch-vendor-agent.md        # the agent: 5 modes, 10 phases, rules, self-QA
│   └── skills/
│       └── merch-vendor-review/         # the engine (also usable standalone / on claude.ai)
│           ├── SKILL.md
│           ├── references/
│           │   ├── test_cases.json      # 130 tests, gate, feasibility map (single source of truth)
│           │   ├── platform_contract.md # Plum merchandise code contract (from merch-sensei)
│           │   ├── doc_intake.md        # how to read each format; evidence rules; synonyms
│           │   ├── platform_playbooks.md# Magento 2 / Shopify / WooCommerce question sets
│           │   ├── xoxoday_api.md       # reference 7-endpoint pattern
│           │   ├── example_answers.json
│           │   └── templates/           # analysis, vendor email, Jira, manager summary
│           └── scripts/
│               ├── build_review.py      # validate → score → gate → xlsx + Markdown
│               └── scan_secrets.py      # redacting credential scanner
├── docs/
│   ├── ARCHITECTURE.md
│   ├── SCORING.md
│   ├── GAP_ANALYSIS.md                  # what merch-sensei and v1 missed, and how it is closed
│   └── TEST_CATALOG.md                  # generated, human-readable list of all 130 tests
├── examples/justlounge/                 # complete, redacted analysis pack
├── tests/                               # pytest: catalogue integrity, engine, scanner, examples
├── tools/gen_test_catalog.py
├── .github/workflows/ci.yml
├── SECURITY.md  CONTRIBUTING.md  CHANGELOG.md  requirements-dev.txt
└── reviews/                             # your working output (gitignored, never committed)
```

## Coverage: 130 tests in 16 sections
Documentation Quality, Access & Authentication, Environments & Onboarding, Catalogue & Product
Sync, Pricing/Currency/Balance, Order Placement & Address, Idempotency & Duplicates, Order
Status & Lifecycle, Webhooks, Polling, Shipment Tracking, Cancellation/Returns/Refunds,
Reconciliation & Settlement, Errors/Rate Limits/Reliability, Security/Data/Compliance, Support &
Versioning. Every test has a priority, a verification type (Doc / Live / Doc+Live), pass criteria
and the platform component it feeds. See [docs/TEST_CATALOG.md](docs/TEST_CATALOG.md).

## Install

**In Claude Code (recommended):** copy the `.claude/` folder into the project where you review
vendors (or clone this repo and work inside it), then:
```
/merch-vendor-agent
```
Drop the vendor doc and say "analyze".

**On claude.ai / Cowork:** zip `.claude/skills/merch-vendor-review/` as `merch-vendor-review.skill`
and upload it as a skill. The skill runs the condensed workflow with the same rules and outputs.

**Tooling:**
```bash
pip install -r requirements-dev.txt
pytest -q tests
```

## Non-negotiables
- Evidence or nothing: docs silent means "Not available". Platform knowledge only produces questions.
- Never call production. "100% feasible" only after every Live test passes on staging.
- Secrets are never reproduced, and vendor docs and outputs never enter git (see [SECURITY.md](SECURITY.md)).
- A gate FAIL is "Not ready", whatever the score.

## Related
- [merch-sensei](https://github.com/abhishekkxoxo/merch-sensei): builds the merchandise connector (engineering)
- [akatsuki-gift-cards](https://github.com/abhishekkxoxo/akatsuki-gift-cards), [topup-sensei](https://github.com/abhishekkxoxo/topup-sensei)
