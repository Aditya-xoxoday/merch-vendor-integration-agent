# JustLounge: lifecycle coverage map

| Stage | Endpoint in doc | Status | Tests |
|---|---|---|---|
| Auth | OAuth 1.0 HMAC-SHA1 (method only) | Partial | AUTH-01..07 |
| Catalogue | GET /rest/V1/products (by category, by page size) | Partial: no paging control, truncated schema | CAT-01..16 |
| Stock / price | none (price only, no currency, no stock) | Missing | CAT-06, PRC-01..04 |
| Serviceability | none | **Missing** | ORD-14 |
| Place order | none | **Missing** | ORD-01..18 |
| Idempotency | none | **Missing** | IDM-01..05 |
| Order status | none | **Missing** | STS-01..09 |
| Webhooks / polling | none | **Missing** | WHK-01..12, POL-01..04 |
| Tracking | none | **Missing** | TRK-01..06 |
| Cancel / returns | none | **Missing** | RTN-01..07 |
| Balance | none | Missing (optional) | BAL-01..04 |
| Reconciliation | none | **Missing** | REC-01..07 |

**1 of 12 stages partially covered. 0 of the stages that move an order are covered.**
