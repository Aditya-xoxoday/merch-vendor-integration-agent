---
name: xoxoday-merchandise-vendor-review
description: "Reviews and tests a Merchandise vendor's API for Xoxoday/Plum integration readiness. Use this whenever Adi shares a vendor API doc link, Postman collection, Swagger/OpenAPI spec, PDF or screenshots for a merchandise, physical product, e-commerce store (Magento, Shopify, WooCommerce) or dropship vendor and asks for a UAT review, API analysis, vendor questionnaire, integration readiness check, test cases, or go/no-go. Also trigger for 'review this vendor's API', 'is this vendor ready to integrate', 'fill out the vendor questionnaire for X', or 'score this API against our standard'. Runs 130 test cases (doc review plus live staging checks) built from the Plum merchandise platform contract (merch-sensei), scans docs for leaked credentials, and produces a full analysis pack: ANALYSIS.md, a scored REPORT.md, an Excel workbook with a derived Integration Gate, field mapping, vendor email and Jira comment."
---

# Xoxoday Merchandise Vendor API Review (v2.1)

This is the engine behind the `/merch-vendor-agent` command. When you run inside the agent repo,
follow `.claude/commands/merch-vendor-agent.md` (the full 10-phase workflow). When this skill is
used on its own, follow the condensed workflow below. It has the same rules and the same outputs.

## Who this is for
Adi is a PM at Xoxoday/Plum. He reviews and tests vendor APIs and reports findings to his manager
(Piyush Agrawal) and the vendor. He does not make the commercial decision. When the verdict is
Ready, engineering builds with `/merch-sensei`.

## Hard rules
1. **Evidence or nothing.** A docs-silent answer is "Not available". Platform knowledge (what
   Magento usually does) produces questions, never answers.
2. **Every Yes/No has evidence.** The builder refuses to run without it.
3. **Never call production.** Live tests run on staging only. "100% feasible" needs every Live
   test passed.
4. **Secrets:** run `scripts/scan_secrets.py` on every input and look at every image. Never
   reproduce a secret anywhere. A secret found in the doc means SEC-07 = No and a rotation request.
5. **Status map targets:** PENDING, CONFIRMED, SHIPPED, DELIVERED, CANCELED, RETURNED only.
6. **Vendor emails:** short and plain. No numbered sub-points, no em dashes, no internal system names.

## Condensed workflow
1. **Acquire:** read the real contract (see `references/doc_intake.md`). Extract text, every
   image and link annotations. Fingerprint the platform (`references/platform_playbooks.md`).
2. **Security scan:** `python3 scripts/scan_secrets.py <inputs>`.
3. **Coverage map:** list endpoints by lifecycle stage. A missing stage is a blocker.
4. **Answer every test** in `references/test_cases.json`. Every test is worded so that Yes means
   compatible with Plum. Use Yes / No / Not available / NA / Open, and record live as Pass / Fail
   / Not run. Then do a second, adversarial pass: check every Yes against its pass criteria and
   re-search every Not available using synonyms.
5. **Status map and field mapping** (vendor fields mapped to Plum shipping and product fields).
6. **Build:**
   ```bash
   python3 scripts/build_review.py references/test_cases.json answers.json Vendor_Merchandise_Review.xlsx --md REPORT.md
   ```
7. **Write ANALYSIS.md** using `references/templates/ANALYSIS_TEMPLATE.md`, plus the vendor
   email, Jira comment and manager summary from the other templates.
8. **Self-QA:** scan your outputs for secrets, and check that the numbers match across the
   analysis, the report and the workbook.

## Scoring and verdict
- Score: P0=3, P1=2, P2=1, with NA excluded. A live Fail cancels a doc Yes.
- Gate: 9 items **derived from linked tests**, plus a valid status map.
- Feasibility lines (from merch-sensei): OK, CHECK, BLOCKED (a P0 No or a live Fail) or MISSING
  (nothing documented).
- Verdict:
  - gate FAIL gives "Not ready"
  - any Live test not run or failed gives "Doc-ready, live staging verification pending"
  - score of 75 or more with no escalations gives "Ready (100% feasible)"
  - anything else is "Ready with conditions"

## Reference files
- `references/test_cases.json`: 130 tests across 16 sections, the gate, the feasibility map,
  and the `legacy` mapping back to the v1 41 questions.
- `references/platform_contract.md`: why each test exists (the Plum order/status/sync contract).
- `references/doc_intake.md`: how to read each doc format, evidence rules, synonyms.
- `references/platform_playbooks.md`: Magento 2, Shopify and WooCommerce question sets.
- `references/xoxoday_api.md`: the reference Xoxoday 7-endpoint pattern.
- `references/templates/`: analysis, vendor email, Jira comment and manager summary.
- `references/example_answers.json`: a filled fictional example.
- `scripts/build_review.py`: validates the answers, then builds the workbook and the Markdown report.
- `scripts/scan_secrets.py`: finds credentials in docs with the values redacted.
