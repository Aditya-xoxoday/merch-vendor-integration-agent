# Changelog

## 4.3.0 (2026-10-19)
- Cleaner workbook, one question per tab:
  - **Summary:** the answer in big letters, must-haves as Yes / Partly / No, blockers, next steps
  - **Ask the vendor:** questions and the email
  - **Tech:** Ready / Check / Blocked words instead of emoji
  - **All checks:** 6 columns, must-haves first
- Titles and headings span the full width; check IDs are gone from the Summary.
- New optional review.json fields: `blockers`, `api_note`.

## 4.2.0 (2026-10-18)
- Every review now replies with **two boxes**:
  - the review (decision for everyone)
  - **Build Feasibility in merch-sensei format**: AUTH, ORDER, IDEMPOTENCY, ADDRESS, STATUS MAP,
    WEBHOOK, POLLING, PRE-CONFIRM FAIL, TRACKING, CANCEL/RETURNS, CATALOG, BALANCE, then sandbox run,
    complexity, risks, build files, checklist, notes, handoff
- Feasibility lines come from `tech.feasibility` when given, otherwise from the checks (webhook or
  polling is enough; a missing balance API is shown as not needed).
- The Tech tab starts with the same feasibility table.

## 4.1.0 (2026-10-18)
- The chat reply is now a boxed report in merch-sensei style, printed by `build_review.py`:
  - VERDICT, API TEST, SECURITY
  - one line per must-have with ✅/⚠️/❌
  - areas with counts and gaps
  - top vendor questions, next steps, output path
- The 7 must-have groups have short labels (PLACE ORDER, ADDRESS, PRODUCT ID, ORDER STATUS,
  TRACKING, SAFE RETRY, SECURE LOGIN).

## 4.0.0 (2026-10-18)
- **One output per review:** `<Vendor>_Review.xlsx` with 4 tabs:
  - Summary: decision, must-haves, top questions, security, next steps, copy-paste summary
  - Vendor questions: all questions and the email draft
  - Tech: endpoints, mapping, status flow, failure modes, assumptions, config, build notes
  - All checks
- It is built from a single `review.json`. This replaces the 9 separate files: ANALYSIS, REPORT,
  inventory, mapping, email, Jira, summary, handoff, test plan and runbook.
- Full tech spec, Postman, config draft and draft code are made only on request. The tech spec is
  one file and now includes the test plan, merch-sensei handoff and debug runbook.
- `must_have_notes` gives short, plain lines on the Summary tab.
- Added `CLAUDE.md` so the agent works for anyone who clones the repo. Simpler README with a quick start.
- Removed unused templates; Printstop example reduced to review.json, the workbook and the optional spec.

## 3.2.0 (2026-10-18)
- **Fixed:** the vendor config draft put token credentials as flat keys. `/vendor/updateAccessToken`
  calls `fetchAccessToken` once per key, so this would have fetched one token per field.
  Credentials now nest under one key, and `build_tech_pack.py` rejects the flat shape.
- **Elite TECH mode:**
  - existing-connector check
  - quirk hunt checklist
  - walking orders through our code paths
  - 4 independent reviewers in parallel (architecture, failure hunter, security and data, ops and money)
  - assumption ledger
  - a hard quality gate
- `lint_tech_spec.py` checks for:
  - all 21 sections
  - 4 or more mermaid diagrams
  - 12 or more failure modes
  - 6 or more assumptions, each with how to verify it
  - every open must-have and every risk mentioned
  - no secrets
- TECH_SPEC template rewritten (21 sections).
- connector_reference.md adds:
  - the credentials shape
  - RETURNED is not terminal for polling
  - the suspected email re-send bug
  - `allowMerchandiseEmailClientIds`
  - the Dpanda refetch caveat
- Printstop pack rebuilt:
  - 548-line spec
  - recipient-as-profile finding (no name or phone in shipping)
  - 409 false-match and ghost-order designs
  - draft `code/Printstop.ts` and `code/Printstop.test.ts` (16 tests)
  - updated handoff, test plan, runbook and vendor email

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
