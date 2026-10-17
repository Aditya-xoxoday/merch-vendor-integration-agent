# Changelog

## 3.1.0 (2026-10-18)
- Developer tech pack at merch-sensei depth, produced by every review (MODE: TECH). It contains:
  - TECH_SPEC (feasibility block, endpoints, class plan, order body mapping, config, risks)
  - vendor config draft
  - Postman collection with negative cases
  - test plan (sandbox + Jest)
  - debug runbook
  - merch-sensei handoff
  - fixtures
- `build_tech_pack.py`: validates placeholders, sandbox-only URLs and status targets; generates
  the config draft and Postman files.
- `connector_reference.md`: lifecycle, class contract, config rules, platform limits, debug signals.
- The scanner ignores code references such as `creds.clientSecret`.
- Printstop example gains a full `tech/` pack.

## 3.0.0 (2026-10-18)
- The decision now answers "Can we integrate?" from 7 must-haves only, and "Does the API work?"
  from sandbox tests. The 0-100 score is gone. A missing balance API (now Nice-to-have) no longer
  pulls the result down; a missing Place Order API means No.
- Checks are tagged Must-have / Important / Nice-to-have instead of P0/P1/P2.
- Plain wording throughout; no role names.
- Workbook sheets are now Summary and Checks. A short summary template is added.
- The secret scanner ignores cut-off sample tokens such as "eyJhbGci...".
- Example review: Printstop / Mandaala. The earlier example was removed.

## 2.1.0 (2026-10-17)
- Added the `/merch-vendor-agent` command: 5 modes (ANALYZE, LIVE, COMMS, HANDOFF, DIFF) and a 10-phase analysis with self-QA.
- 13 new tests (130 total, 16 sections). These cover documentation quality (DOC-01..04),
  credentials in docs (SEC-07), least privilege (SEC-08), sandbox orders not shipped (ENV-06),
  incremental sync (CAT-15), attribute mapping (CAT-16), address change (ORD-17), peak volume
  (ORD-18), webhook replay (WHK-12) and transit liability (RTN-07).
- `scan_secrets.py`: a redacting credential scanner.
- `build_review.py --md`: a Markdown report; a MISSING feasibility state.
- References: platform contract, doc intake playbook, Magento/Shopify/WooCommerce question sets,
  analysis, email, Jira and summary templates.
- pytest suite and CI.

## 2.0.0 (2026-10-17)
- Merged the v1 41-question merchandise review skill with the merch-sensei platform contract into
  117 test cases.
- The gate is derived from test results. NA is excluded from the score. Evidence is enforced. Live
  staging results are added. Feasibility lines come from merch-sensei.

## 1.0.0
- 41-question merchandise vendor review skill with a manual gate.
