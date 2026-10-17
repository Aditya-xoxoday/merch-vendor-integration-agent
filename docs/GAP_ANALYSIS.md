# Gap analysis: merch-sensei vs our v1 skill vs this agent

## What merch-sensei (abhishekkxoxo/merch-sensei) misses

merch-sensei is an excellent **build** agent. These gaps are about **vendor evaluation**, which
it was not designed for.

| # | Gap | Why it matters | Closed by |
|---|---|---|---|
| 1 | No reconciliation/settlement questions | Finance cannot match vendor charges to orders | REC-01..07 |
| 2 | No serviceability/pincode check | Orders fail after placement and need refunds | ORD-14 |
| 3 | No returns/replacement process or window, no RTO, no transit liability | Recipient damage/loss has no path | RTN-03, RTN-04, RTN-07 |
| 4 | No pricing semantics (landed cost, currency, tax, price-change policy) | Margin leakage | PRC-01..04 |
| 5 | No SLA, uptime, support contact, versioning/deprecation | Ops risk after go-live | ERR-06, SUP-01..04 |
| 6 | No PII/DPA, least privilege, credentials-in-docs, cross-border/customs | Legal and security exposure | SEC-02..08 |
| 7 | No scoring, gate or go/no-go output for PM/management | Cannot compare vendors or justify a decision | Scorecard + derived gate |
| 8 | No documentation-quality check | Catalogue-only docs look "fine" batch by batch | DOC-01..04 |
| 9 | No secret scanning of vendor docs | Leaked production keys get copied around | `scan_secrets.py`, SEC-07 |
| 10 | Assumes a sandbox exists; no check that sandbox orders are not shipped/billed | A staging run could ship real goods | ENV-01, ENV-06 |
| 11 | No peak/bulk campaign capacity question | Reward campaigns spike volume | ORD-18 |
| 12 | No vendor-facing outputs (email, Jira, manager summary) | PM rewrites findings by hand | templates + COMMS mode |
| 13 | Rule list numbered out of order (11, 12 before 6) | Readability | n/a (report upstream) |
| 14 | Image/screenshot reading not called out | Response examples and secrets often live only in images | Phase 1 + rule 4 |

## What our v1 skill missed

| # | Gap | Closed by |
|---|---|---|
| 1 | NA counted as a failure in the score | NA excluded from the denominator |
| 2 | Gate filled in by hand, could contradict answers | Gate derived from linked tests |
| 3 | "Yes" accepted with no evidence | Builder rejects Yes/No without details |
| 4 | Doc-only: no live verification | Live column, live coverage, contradiction flags |
| 5 | No vendor order id / status enumeration / status mapping to our 6 statuses | ORD-02, STS-01, STS-02, `status_map` validation |
| 6 | No webhook format checks (JSON, `data` key, signing, encryption, our reference) | WHK-02..06 |
| 7 | No address schema mapping, formats, max lengths | ORD-05..08, field mapping file |
| 8 | No SKU reversibility, catalogue paging, silent-failure check | CAT-02, CAT-03, CAT-09 |
| 9 | No pre-confirmation failure, multi-package, polling field checks | ORD-13, TRK-04, POL-02 |
| 10 | Gift-card wording copied in (denominations, recipient) | Reworded for merchandise |
| 11 | Duplicate questions (Q2, Q4, Q9) | Merged into ENV-01/ENV-02 |
| 12 | Gate demanded returns without noting the platform does not auto-refund | RTN-03 platform note |
| 13 | Output was only a spreadsheet | ANALYSIS.md, REPORT.md, coverage map, field mapping, comms |
| 14 | No tests for the tooling itself | pytest suite + CI |

## Known limits of this agent (honest list)
- `scan_secrets.py` does not OCR images, so the agent must view every image (rule 4).
- The live phase needs the vendor's staging environment and the Postman CLI. Without them, the
  verdict can never go past "Doc-ready".
- `platform_contract.md` mirrors code as of Oct 2026. When vendor-integrations changes, update it.
- Scores compare vendors fairly only within the same test-catalogue version.
