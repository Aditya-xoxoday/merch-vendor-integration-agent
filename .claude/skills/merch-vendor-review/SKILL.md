---
name: xoxoday-merchandise-vendor-review
description: "Checks whether a Merchandise vendor's API can be integrated with Xoxoday/Plum and whether it works. Use whenever someone shares a vendor API doc link, Postman collection, Swagger/OpenAPI spec, PDF or screenshots for a merchandise, physical product, e-commerce store (Magento, Shopify, WooCommerce) or dropship vendor and asks to review, analyse or test it, fill the vendor questionnaire, or decide go/no-go. 7 must-haves (place order with order ID, address fit, product ID, order status, tracking, safe retry, secure login) decide 'can we integrate'. Everything else, like a balance API, is a gap that never blocks. Produces ONE Excel workbook (Summary, Vendor questions, Tech, All checks). A full developer tech spec, a Postman collection or draft code are made only on request."
---

# Merchandise Vendor API Review

Answers two questions about a vendor's API, in **one workbook**:
1. **Can we integrate?** Decided only by the 7 must-haves.
2. **Does the API work?** Decided by tests on the vendor's sandbox.

The full workflow is in `.claude/commands/merch-vendor-agent.md`. The short version is below.

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

**Decision:**
- **No**: a must-have is missing or failed on sandbox
- **Likely yes**: none missing, some only partly documented
- **Yes on paper**: all documented, sandbox not run
- **Yes**: all documented and passed on sandbox

## Rules
1. Evidence or nothing: docs silent means "Not available". Never guess from what a platform usually does.
2. Every Yes/No needs evidence. The builder refuses without it.
3. Never call production. Never copy a secret (`scripts/scan_secrets.py`; look at every image).
4. Status mapping uses only PENDING, CONFIRMED, SHIPPED, DELIVERED, CANCELED, RETURNED.
5. Clean output: plain words, no em dashes; the vendor email has no numbered sub-points and no internal names.

## Steps
1. Read the docs: text, every image, links (`references/doc_intake.md`).
2. `python3 scripts/scan_secrets.py <files>`.
3. Answer every check in `references/test_cases.json`, then do a second pass.
4. Write `review.json` (shape in the `scripts/build_review.py` docstring; example in `references/example_review.json`):
   answers, status_map, security, must_have_notes, blockers, api_note, questions, vendor_email, next_steps, and `tech`
   (endpoints, order mapping, status flow, failure modes, assumptions, config, build notes).
5. Build the one output:
   ```bash
   python3 scripts/build_review.py references/test_cases.json review.json <Vendor>_Review.xlsx
   ```
6. Reply with BOTH boxes the builder prints, inside one code block: the review (VERDICT, MUST-HAVES,
   AREAS, ASK THE VENDOR, NEXT STEPS) and the build feasibility in merch-sensei format (AUTH, ORDER,
   IDEMPOTENCY, ... BUILD FILES, HANDOFF). Then link the workbook.

**On request only:**
- Full tech spec (`references/templates/TECH_SPEC_TEMPLATE.md`, checked by `scripts/lint_tech_spec.py`)
- Postman collection and config draft (`scripts/build_tech_pack.py`)
- Draft code (`references/connector_reference.md`)

## Files
- `references/test_cases.json`: 130 checks (14 must-have, 89 important, 27 nice-to-have) and the 7 groups.
- `references/platform_contract.md`, `references/connector_reference.md`: what our system needs, at build depth.
- `references/doc_intake.md`, `references/platform_playbooks.md`: how to read docs; extra vendor questions.
- `scripts/build_review.py`: checks review.json, decides, writes the workbook.
- `scripts/scan_secrets.py`, `scripts/lint_tech_spec.py`, `scripts/build_tech_pack.py`: secret scan, spec gate, build files.
