# {Vendor}: technical spec

| | |
|---|---|
| Source | {doc, date} |
| Contract | `references/connector_reference.md` (code wins) |
| Status | {docs reviewed / sandbox run x/y} |
| Companion files | tech.json, vendor_config.draft.json, Postman collection, code/, TEST_PLAN, DEBUG_RUNBOOK, HANDOFF, fixtures |

All 21 sections are required (`lint_tech_spec.py` checks them). Example: `examples/printstop/tech/TECH_SPEC.md`.

## 0. Summary
Decision in one line, then the 3 design-level issues (table: issue, why it matters, check IDs).

## 1. Check first: existing connector
`git grep` commands + SQL, and a finding → action table (diff vs new build).

## 2. Feasibility
merch-sensei block: AUTH, ORDER, IDEMPOTENCY, ADDRESS, STATUS MAP, WEBHOOK, POLLING, PRE-CONFIRM FAIL,
TRACKING, CANCEL/RETURNS, CATALOG, BALANCE, SANDBOX RUN, COMPLEXITY.

## 3. Architecture and flows
4 mermaid sequence diagrams: token, place order (happy / timeout / duplicate), status updates, catalogue sync.

## 4. Endpoint contracts
Per endpoint: method + query, headers, body field table (path, type, required, notes), response field
table, errors. Then cross-cutting quirks.

## 5. Data mapping
Order body (vendor field ← our source, rule), recipient identity decision, status/tracking/date
mapping, product mapping to table columns.

## 6. State machine
Vendor status → deliveryStatus → mvod.status → side effects (egift row, email, refund, polling stops?).
Mark undocumented rows.

## 7. Class plan
Method table: behaviour, throws-when. Lint rules. Link to `code/`.

## 8. Config and registration
Table: where, change, tracked? (VI vendor config with the credentials shape, baseConfigs, OPMS,
plumAuth, schedulers, DB, karma, karma_reports).

## 9. Data model
Tables and columns used.

## 10. Failure modes
At least 12 rows: step, failure, detection, handling, severity.

## 11. Idempotency and retry
Timeout path, duplicate path, our own guard.

## 12. Security and PII
Secrets, redaction, PII sent and returned, query strings, transport, DPA.

## 13. Performance and limits
Call volumes (order, polling, sync), rate limits, concurrency settings.

## 14. Observability
Signal, source, alert.

## 15. Test strategy
Sandbox (Postman) and unit (Jest) summary; link TEST_PLAN.

## 16. Rollout and rollback
Staging → UAT → limited prod → full; rollback steps.

## 17. Effort
Work item and estimate, with what the estimate assumes.

## 18. Assumption ledger
At least 6 rows: assumption, risk if wrong, how to verify.

## 19. Open questions
Question, what it blocks, check IDs.

## 20. Done means
Checklist.
