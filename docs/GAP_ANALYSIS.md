# What was missing before, and how it is covered now

## Missing in merch-sensei (it builds connectors; it was not made to review vendors)
| # | Missing | Covered by |
|---|---|---|
| 1 | Settlement / reconciliation questions | REC-01..07 |
| 2 | Pincode / serviceability check | ORD-14 |
| 3 | Returns, return-to-origin, transit damage | RTN-03, RTN-04, RTN-07 |
| 4 | Price meaning: landed cost, currency, tax, price changes | PRC-01..04 |
| 5 | Uptime, support contact, versioning | ERR-06, SUP-01..04 |
| 6 | Personal data, least-privilege keys, keys inside docs, customs | SEC-02..08 |
| 7 | A clear yes/no on "can we integrate" | 7 must-haves and a decision |
| 8 | Checking that the doc covers the full order flow | DOC-01..04 |
| 9 | Scanning vendor docs for leaked keys | `scan_secrets.py`, SEC-07 |
| 10 | Checking that sandbox orders are not shipped or billed | ENV-01, ENV-06 |
| 11 | Peak volume for big campaigns | ORD-18 |
| 12 | Ready-to-send vendor email, Jira comment, summary | templates |
| 13 | Reading screenshots inside docs | rule 4 |
| 14 | Rule list numbered out of order (11, 12 before 6) | report upstream |

## Missing in our first skill (41 questions)
| # | Missing | Covered by |
|---|---|---|
| 1 | NA answers counted against the vendor | NA is now Met |
| 2 | Gate filled in by hand, could contradict the answers | Must-haves worked out from the answers |
| 3 | "Yes" accepted with no evidence | Builder refuses it |
| 4 | Docs only, no testing | Sandbox results |
| 5 | Order ID in response, full status list, status mapping | ORD-02, STS-01, STS-02 |
| 6 | Webhook format, signing, encryption | WHK-02..06 |
| 7 | Address format and field mapping | ORD-05..08, field mapping file |
| 8 | Product ID reuse, catalogue paging, silent failures | CAT-02, CAT-03, CAT-09 |
| 9 | Order failing before confirmation, multi-package, polling field | ORD-13, TRK-04, POL-02 |
| 10 | Gift card wording copied in | Reworded |
| 11 | Duplicate questions | Merged |
| 12 | Spreadsheet had no clear answer or vendor-ready content | One workbook: Summary (decision), Vendor questions (with email), Tech, All checks |
| 13 | A 0-100 score that punished missing extras | Decision from must-haves only |
| 14 | No tests for the tools | Test suite and CI |

## Known limits
- `scan_secrets.py` does not read images, so the agent must look at every image.
- "Does the API work?" needs the vendor's sandbox and the Postman CLI.
- `platform_contract.md` reflects our code as of Oct 2026. Update it when the code changes.
