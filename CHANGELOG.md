# Changelog

## 2.1.0 (2026-10-17)
- Added the `/merch-vendor-agent` command: 5 modes (ANALYZE, LIVE, COMMS, HANDOFF, DIFF) and a 10-phase analysis with self-QA.
- 13 new tests (130 total, 16 sections). These cover documentation quality (DOC-01..04),
  credentials in docs (SEC-07), least privilege (SEC-08), sandbox orders not shipped (ENV-06),
  incremental sync (CAT-15), attribute mapping (CAT-16), address change (ORD-17), peak volume
  (ORD-18), webhook replay (WHK-12) and transit liability (RTN-07).
- `scan_secrets.py`: a redacting credential scanner.
- `build_review.py --md`: a Markdown report; a MISSING feasibility state.
- References: platform contract, doc intake playbook, Magento/Shopify/WooCommerce question sets,
  analysis/email/Jira/manager templates.
- Example: the JustLounge (Magento 2) full analysis pack.
- pytest suite and CI.

## 2.0.0 (2026-10-17)
- Merged the v1 41-question merchandise review skill with the merch-sensei platform contract into
  117 test cases.
- The gate is derived from test results. NA is excluded from the score. Evidence is enforced. Live
  staging results are added. Feasibility lines come from merch-sensei.

## 1.0.0
- 41-question merchandise vendor review skill with a manual gate.
