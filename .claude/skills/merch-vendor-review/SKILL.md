---
name: xoxoday-merchandise-vendor-review
description: "Checks whether a Merchandise vendor's API can be integrated with Xoxoday/Plum and whether it works. Use whenever someone shares a vendor API doc link, Postman collection, Swagger/OpenAPI spec, PDF or screenshots for a merchandise, physical product, e-commerce store (Magento, Shopify, WooCommerce) or dropship vendor and asks to review it, analyse it, test it, fill the vendor questionnaire, or decide go/no-go. Runs 130 checks (docs plus sandbox tests). 7 must-haves (place order, order ID, address fit, product ID, order status, tracking, safe retry, secure login) decide 'can we integrate'. Everything else, such as a balance API, is reported as a gap and never blocks. Also scans docs for leaked credentials. Outputs ANALYSIS.md, REPORT.md, an Excel workbook, field mapping, a vendor email, a Jira comment, and a developer tech pack at merch-sensei depth (tech spec, class plan, vendor config draft, Postman collection, unit test plan, debug runbook, merch-sensei handoff)."
---

# Merchandise Vendor API Review (v3)

Answers two questions about a vendor's API:
1. **Can we integrate?** This is decided only by the 7 must-haves.
2. **Does the API work?** This is decided by tests on the vendor's sandbox.

Everything else (balance API, returns process, settlement report, rate limits...) is listed as an
Important or Nice-to-have gap. Gaps go to the vendor as questions, but they never stop the integration.

The full step-by-step workflow is in `.claude/commands/merch-vendor-agent.md`. The short
version is below.

## The 7 must-haves
| # | Must-have | Checks |
|---|---|---|
| 1 | Place an order and get an order ID back | ORD-01, ORD-02 |
| 2 | Our address fields fit their order format | ORD-05 |
| 3 | The product ID from their catalogue is what the order takes | CAT-03 |
| 4 | Get the order status (status list, lookup, and webhook or polling) | STS-01, STS-03, WHK-01 or POL-01 |
| 5 | Get courier and tracking number after dispatch | TRK-01 |
| 6 | Retry safely without duplicate orders | IDM-01, plus IDM-02 or IDM-03 |
| 7 | Secure login that works | AUTH-01, SEC-01 |

## Decision
| Result | When |
|---|---|
| **No, we cannot integrate yet** | any must-have is missing, confirmed absent, or failed on sandbox |
| **Likely yes, after the vendor answers a few points** | nothing missing, but some must-haves are only partly documented |
| **Yes on paper, confirm with a sandbox test** | every must-have is documented; sandbox not run yet |
| **Yes, we can integrate** | every must-have is documented and passed on sandbox |

If a check marked `risk` comes back No or Open (signed webhooks, non-JSON webhooks, unsupported
encryption, or an order failing before confirmation), the result notes that it needs a change on
our side first.

## Rules
1. **Evidence or nothing.** If the docs say nothing, the answer is "Not available". Never guess
   from what the platform (Magento, Shopify...) usually does. Platform knowledge only becomes
   questions for the vendor.
2. **Every Yes/No needs evidence** (endpoint, field or short paraphrase). The builder refuses without it.
3. **Never call production.** Sandbox only.
4. **Never copy a secret.** Run `scripts/scan_secrets.py` on every input and look at every image.
   If credentials are found, ask the vendor to rotate them.
5. **Status mapping** uses only PENDING, CONFIRMED, SHIPPED, DELIVERED, CANCELED, RETURNED.
6. **Vendor emails:** short and plain. No numbered sub-points, no em dashes, no internal system names.

## Short workflow
1. Read the real docs (see `references/doc_intake.md`): text, every image, links.
2. Scan for secrets: `python3 scripts/scan_secrets.py <files>`.
3. List the endpoints by stage (login, catalogue, order, status, tracking...).
4. Answer every check in `references/test_cases.json` with Yes / No / Not available / NA / Open,
   plus the sandbox result (Pass / Fail / Not run) where the check has one. Then do a second pass:
   check every Yes against "what counts as yes" and search again for every "Not available".
5. Map the vendor statuses and fields.
6. Build:
   ```bash
   python3 scripts/build_review.py references/test_cases.json answers.json Vendor_Review.xlsx --md REPORT.md
   ```
7. Write ANALYSIS.md, the vendor email, the Jira comment and a summary from `references/templates/`.
8. Write the developer tech pack (`tech/`) at elite depth (see MODE: TECH in the agent), using `references/connector_reference.md`:
   `tech.json` → `python3 scripts/build_tech_pack.py tech.json tech/` (vendor config draft + Postman
   collection), plus TECH_SPEC.md (21 sections), draft `code/` (class + Jest), TEST_PLAN.md, DEBUG_RUNBOOK.md,
   HANDOFF_MERCH_SENSEI.md and fixtures. Gate: `python3 scripts/lint_tech_spec.py tech/TECH_SPEC.md answers.json references/test_cases.json`.
9. Before replying: scan your outputs for secrets and check that the numbers match everywhere.

## Files
- `references/test_cases.json`: 130 checks (14 must-have, 89 important, 27 nice-to-have) and the 7 must-have groups.
- `references/platform_contract.md`: what our system needs from a vendor, and why.
- `references/connector_reference.md`: build-level detail (lifecycle, class contract, config rules, debug signals).
- `references/doc_intake.md`: how to read each doc type, plus search synonyms.
- `references/platform_playbooks.md`: questions to ask Magento, Shopify and WooCommerce vendors.
- `references/templates/`: analysis, vendor email, Jira comment, summary.
- `references/example_answers.json`: a filled example (fictional vendor).
- `scripts/build_review.py`: checks the answers, then builds the workbook and REPORT.md.
- `scripts/scan_secrets.py`: finds credentials in docs and prints them redacted.
- `scripts/build_tech_pack.py`: tech.json → vendor config draft, Postman collection, environment template.
- `scripts/lint_tech_spec.py`: quality gate for TECH_SPEC.md (sections, diagrams, depth, open items, secrets).
