# JustLounge Merchandise API Analysis

**Verdict: Not ready.** The document describes a read-only product catalogue on the live Magento 2
storefront. It has no way to place, track, return or reconcile an order.

| Score | Gate | Live coverage | Escalations | Doc completeness |
|---|---|---|---|---|
| 4/100 (1/5) | FAIL (0 of 9 met) | 0% (25 live tests, none run) | 0 | 14% |

> **Security alert.** The PDF and both screenshots contain four live OAuth credentials for the
> production store (consumer key, consumer secret, access token, token secret). Anyone with the
> PDF can read their catalogue API, and possibly more, depending on the integration's permissions.
> Ask JustLounge to rotate them. We did not use them and have not reproduced them anywhere.

## 1. What this API is
- **Platform:** Magento 2 REST (`/rest/V1/`). The host is `justlounge.com`, the public
  storefront. No sandbox or staging host is given.
- **Endpoints:** two variants of `GET /rest/V1/products`, one filtered by category id and one
  with page size 10.
- **Auth:** OAuth 1.0a, HMAC-SHA1, using a pre-issued access token. Where the OAuth parameters go
  is not stated. The screenshot's Postman setting allows them in the URL.
- **What it can do:** list products with sku, name, price, status, type and timestamps.
- **What it cannot do (per the doc):** stock, currency, images, brand, serviceability, orders,
  status, tracking, returns, balance and settlement.

## 2. Lifecycle coverage
Only the catalogue stage is partially covered. Every stage that moves money or a parcel is missing.
See `01_coverage_map.md`.

| Stage | Status |
|---|---|
| Auth | Partial |
| Catalogue | Partial |
| Stock/price, serviceability, place order, idempotency, status, webhook/poll, tracking, returns, balance, reconciliation | Missing |

## 3. Top blockers (P0 first)
1. **DOC-01 / ORD-01: no order API.** Impact: Plum cannot place a reward order. Every order
   would be manual. Ask: an order creation endpoint for partner orders, with our reference stored
   on the order (IDM-01) and duplicate protection (IDM-02).
2. **STS-01 / STS-03 / WHK-01 / POL-01: no order status, no status updates.** Impact: we cannot
   tell recipients where their order is, and we cannot trigger refunds on cancellation. Ask: the
   full order status list, an order lookup by our reference, and webhooks if they have them.
3. **TRK-01: no shipment tracking.** Impact: the Merchandise category's key capability is
   absent, so there is no courier or tracking number for the recipient. Ask: shipment tracks
   (carrier and tracking number/URL) exposed through the API.
4. **REC-01 / REC-02: no reconciliation source.** Impact: finance cannot match vendor charges to
   our orders. Ask: a statement or settlement report per order with our reference.
5. **ENV-01 + SEC-07: production-only access, with credentials leaked in the doc.** Impact: we
   cannot test safely, and the current keys must be treated as compromised. Ask: a staging store
   and fresh per-environment credentials sent securely.

Also missing at P0: serviceability (ORD-14), returns process (RTN-03), currency and landed price
(PRC-01), and the meaning of `status`/`visibility` values (DOC-03).

## 4. Security
| Finding | Test | Action |
|---|---|---|
| 4 live OAuth secrets in the PDF text and both screenshots | SEC-07 = No | Vendor rotates them now; new credentials go through a secure channel, per environment |
| Integration scope unknown (Magento integration tokens can carry admin-level access) | SEC-08 | Ask for least-privilege scope: products read, plus orders/shipments only as needed |
| OAuth params may travel in the URL query | SEC-03 | Ask the vendor to confirm the Authorization header is supported; we will send it in the header |
| HTTPS only | SEC-01 = Yes (doc) | none |

## 5. Engineering view
- **Integration pattern:** unknown. With no order API, sync vs async cannot be decided. Magento
  core has no webhooks, so expect **polling** unless the vendor has an extension.
- **merch-sensei build complexity:** High if the vendor adds Magento order endpoints. That means
  an OAuth 1.0a signer in `getReqHeaders`, a cart/quote-then-order flow or a custom endpoint in
  `getPlaceOrderReqOptions`, a polling override because the status field is not `orders_status`,
  and a tracking fetch from shipments.
- **Escalations:** none raised yet. The webhook risks (WHK-04/05/06) cannot be assessed until
  webhooks are described.
- **Buildable today:** only a catalogue sync, and even that is incomplete: no paging control, no
  stock, no brand/image mapping, no currency. **Blocked:** everything from order placement onward.

## 6. Risks and mitigations
| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Leaked credentials misused before rotation | Medium | High | Rotate now; ask for least-privilege scope |
| Vendor cannot expose order APIs (storefront built for B2C only) | Medium | High | Ask early; fall back to a manual or hybrid model, or another vendor |
| Testing against production creates real orders or charges | High if attempted | High | No live tests until a staging store exists (ENV-01, ENV-06) |
| Catalogue sync disables products on a bad page | Medium | Medium | Need paging and total_count, and errors as non-2xx (CAT-02, CAT-09) |
| Price/currency ambiguity erodes margin | Medium | Medium | Confirm buy price, currency and tax/shipping rules (PRC-01..04) |

## 7. Options and recommendation
| Option | What it takes | Pros | Cons |
|---|---|---|---|
| A. Ask JustLounge to expose partner order, status, shipment and statement APIs, plus a staging store | Vendor dev work; re-review with this agent | Full automation; fits the platform | Timeline depends on the vendor |
| B. Hybrid: sync catalogue by API, place orders manually or by file, update tracking by ops | Ops process, no new code beyond catalogue | Quick start | Manual cost per order; no automated refunds or tracking; error-prone at scale |
| C. Choose a different merchandise vendor | Sourcing | Avoids the gap | Loses this assortment |

**Recommendation:** Option A. Send the vendor questions now (see `VENDOR_EMAIL.md`) and treat
JustLounge as **Not ready** until the order, status, tracking and reconciliation APIs are
documented and pass on staging. Use option B only if commercially necessary, and only after the
credential rotation and with ops sign-off on the manual workload.

## 8. Next steps
| # | Action | Owner | Closes |
|---|---|---|---|
| 1 | Send the security and API-gap email | Adi | SEC-07, DOC-01 |
| 2 | Vendor rotates credentials and provides a staging store with scoped credentials | JustLounge | SEC-07, SEC-08, ENV-01 |
| 3 | Vendor documents the order, status, shipment/tracking, returns and statement APIs, plus the Postman collection | JustLounge | ORD-*, STS-*, TRK-*, RTN-*, REC-*, SUP-05 |
| 4 | Re-run `/merch-vendor-agent` in DIFF mode on the new docs | Adi | All |
| 5 | Live staging run of the 25 Live tests | Adi / engineering | Live coverage |
| 6 | Handoff to `/merch-sensei` once the gate passes | Engineering | Build |

Appendix: `REPORT.md` (full scored report), `JustLounge_Merchandise_Review.xlsx`,
`00_doc_inventory.md`, `01_coverage_map.md`, `02_field_mapping.md`.
