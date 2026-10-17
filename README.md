# Merchandise Vendor Integration Agent

Share a merchandise vendor's API document with this agent (PDF, Word, Postman, OpenAPI/Swagger,
docs site or screenshots). You get back **one Excel workbook** that answers:

1. **Can we integrate?** Yes / Yes on paper / Likely yes / No, decided only by 7 must-haves.
2. **Does the API work?** Based on tests on the vendor's sandbox.

**No Place Order API means No. No balance API is fine.** Everything that is missing but not a
must-have is listed as a gap, with a question for the vendor.

This agent reviews vendors. [merch-sensei](https://github.com/abhishekkxoxo/merch-sensei) builds the
connector once the answer is yes.

## Quick start
```bash
git clone https://github.com/Aditya-xoxoday/merch-vendor-integration-agent.git
cd merch-vendor-integration-agent
pip install -r requirements-dev.txt
claude
```
Then in Claude Code:
```
/merch-vendor-agent
```
Share the vendor doc (file path or link). The workbook appears in `reviews/<vendor>/`.

## The output: one workbook, 4 tabs
| Tab | What's in it |
|---|---|
| **Summary** | The decision, the 7 must-haves (met / open / missing), top vendor questions, security, next steps, and a short summary to paste into Jira or Slack |
| **Vendor questions** | Every question (must-haves first), other gaps, and a ready email draft |
| **Tech** | Endpoints, order field mapping, status flow, failure modes, assumptions to verify, config changes, build notes |
| **All checks** | All 130 checks with the answer, evidence and sandbox result |

See [examples/printstop/Printstop_Review.xlsx](examples/printstop/Printstop_Review.xlsx).

**Only when you ask:**
| Say | You get |
|---|---|
| "full tech spec" | One `<Vendor>_TECH_SPEC.md` for developers: diagrams, class plan, failure modes, test plan, merch-sensei handoff, debug runbook ([example](examples/printstop/Printstop_TECH_SPEC.md)) |
| "postman" / "config draft" / "draft code" | Build files for the sandbox run and the connector |
| "run live" (with sandbox credentials) | Sandbox results added to the same workbook |
| a new version of a doc | What changed, with the workbook updated |

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

How the decision is worked out: [docs/DECISION.md](docs/DECISION.md). All 130 checks: [docs/TEST_CATALOG.md](docs/TEST_CATALOG.md).

## Rules the agent follows
- Evidence or nothing: if the docs say nothing, the answer is "Not available". Nothing is guessed.
- Sandbox only. Production is never called.
- Secrets are never copied, and vendor docs and outputs stay out of git ([SECURITY.md](SECURITY.md)).

## Repository layout
```
.claude/commands/merch-vendor-agent.md   the agent
.claude/skills/merch-vendor-review/      the skill (also works when uploaded to claude.ai)
  references/                            checks, platform contract, reading guides, spec template
  scripts/                               build_review.py (the workbook), scan_secrets.py,
                                         lint_tech_spec.py, build_tech_pack.py
docs/                                    decision rules, architecture, gap analysis, check list
examples/printstop/                      review.json, the workbook, and an optional full tech spec
tests/                                   automated tests (run in CI)
reviews/                                 your reviews (gitignored)
```

## Use on claude.ai
Zip `.claude/skills/merch-vendor-review/` and upload it as a skill.

## Contributing
See [CONTRIBUTING.md](CONTRIBUTING.md). Run `pytest -q tests` before you push.
