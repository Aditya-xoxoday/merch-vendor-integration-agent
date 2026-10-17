# Merchandise Vendor Review: JustLounge (Magento 2 Catalog API)

Reviewed on: 2026-10-17  
Source: Justlounge_Magento_2_Catalog_API_information.pdf (2 pages, Google Docs export, title 'Justlounge.com Magento 2 Catalog Data API'), including 2 embedded Postman screenshots  

## Scorecard

| Metric | Value |
|---|---|
| Capability score | 4/100 |
| Rating | 1 / 5 |
| Documentation completeness | 14% |
| Live staging coverage | 0% (0 pass, 0 fail, 25 required) |
| Integration gate | FAIL |
| Engineering escalations | 0 |
| **Verdict** | **Not ready** |

## Integration gate

| Result | Gate item | Why |
|---|---|---|
| NOT MET | Order placement contract is complete: documented request schema, vendor order id in the response, sync/async behaviour stated, and the address schema maps to our shipping fields. | not met: ORD-01, ORD-02, ORD-04, ORD-05 |
| NOT MET | Orders are idempotent: our reference is accepted, a duplicate never creates a second order, and a timed-out order can be looked up by our reference. | not met: IDM-01, IDM-02, IDM-03 |
| NOT MET | Order status is complete and mappable: enumerated statuses, every one maps to our six delivery statuses, an order-details lookup exists, and updates arrive by webhook or polling. | not met: STS-01, STS-02, STS-03; needs one of: WHK-01, POL-01; status_map missing or invalid |
| NOT MET | Shipment tracking (carrier plus tracking number or URL) is returned via API after dispatch. | not met: TRK-01 |
| NOT MET | Serviceability of the regions/pincodes we need is confirmed, with documented behaviour for non-serviceable addresses. | not met: ORD-14 |
| NOT MET | A returns, replacement or refund path exists for damaged, wrong or undelivered items. | not met: RTN-03 |
| NOT MET | A reconciliation source of truth exists that carries our reference per line. | not met: REC-01, REC-02 |
| NOT MET | Catalogue identifiers are stable and accepted unchanged by Place Order. | not met: CAT-03 |
| NOT MET | Transport and authentication are secure and documented. | not met: AUTH-01 |

## Feasibility (merch-sensei lines)

| Line | State | Notes |
|---|---|---|
| AUTH | CHECK | unresolved: AUTH-01, AUTH-02, AUTH-03, AUTH-04; live not run: AUTH-02, AUTH-03, AUTH-04 |
| ORDER | MISSING | unresolved: ORD-01, ORD-02, ORD-03, ORD-04, ORD-11, ORD-12; live not run: ORD-01, ORD-02, ORD-11, ORD-12 |
| IDEMPOTENCY | MISSING | unresolved: IDM-01, IDM-02, IDM-03, IDM-05; live not run: IDM-02, IDM-05 |
| ADDRESS | MISSING | unresolved: ORD-05, ORD-06, ORD-07, ORD-08, ORD-14, ORD-15; live not run: ORD-14 |
| STATUS MAP | MISSING | unresolved: STS-01, STS-02, STS-05 |
| WEBHOOK | MISSING | unresolved: WHK-01, WHK-02, WHK-03, WHK-04, WHK-05, WHK-06 |
| POLLING | MISSING | unresolved: POL-01, POL-02, POL-04; live not run: POL-01 |
| PRE-CONFIRM FAIL | MISSING | unresolved: ORD-13 |
| TRACKING | MISSING | unresolved: TRK-01, TRK-02, TRK-04; live not run: TRK-01 |
| CANCEL/RETURNS | MISSING | unresolved: RTN-01, RTN-03, RTN-04 |
| CATALOG | CHECK | unresolved: CAT-02, CAT-03, CAT-04, CAT-09; live not run: CAT-01, CAT-02, CAT-03, CAT-09 |
| BALANCE | MISSING | unresolved: BAL-01, BAL-03; live not run: BAL-01, BAL-03 |
| RECON | MISSING | unresolved: REC-01, REC-02, REC-05 |
| DOCS | BLOCKED | unresolved: DOC-01, DOC-02, DOC-03 |
| SECURITY | CHECK | unresolved: SEC-03, SEC-07, SEC-08; live not run: SEC-01 |

## Readiness by section

| Section | Yes | No | Open | Not available | NA |
|---|---|---|---|---|---|
| Documentation Quality | 0 | 4 | 0 | 0 | 0 |
| Access & Authentication | 1 | 0 | 2 | 4 | 0 |
| Environments & Onboarding | 0 | 0 | 0 | 6 | 0 |
| Catalogue & Product Sync | 2 | 0 | 4 | 10 | 0 |
| Pricing, Currency & Balance | 0 | 0 | 0 | 8 | 0 |
| Order Placement & Address | 0 | 0 | 0 | 18 | 0 |
| Idempotency & Duplicates | 0 | 0 | 0 | 5 | 0 |
| Order Status & Lifecycle | 0 | 0 | 0 | 9 | 0 |
| Webhooks | 0 | 0 | 0 | 12 | 0 |
| Polling | 0 | 0 | 0 | 4 | 0 |
| Shipment Tracking | 0 | 0 | 0 | 6 | 0 |
| Cancellation, Returns & Refunds | 0 | 0 | 0 | 7 | 0 |
| Reconciliation & Settlement | 0 | 0 | 0 | 7 | 0 |
| Errors, Rate Limits & Reliability | 0 | 0 | 0 | 8 | 0 |
| Security, Data & Compliance | 1 | 1 | 1 | 5 | 0 |
| Support & Versioning | 0 | 0 | 2 | 3 | 0 |

## Engineering escalations

None.

## Live failures

None.

## Status map

No status map recorded: STS-02 and the status gate cannot pass.

## What the vendor has

- **AUTH-05** If requests are signed (HMAC), the algorithm, exact string-to-sign, timestamp/nonce tolerance and a worked example are documented. NA if not used. Evidence: Signing is standard OAuth 1.0 (RFC 5849) HMAC-SHA1, named on both pages; Postman screenshots show the exact configuration producing 200 OK.
- **CAT-01** A product list endpoint exists with method, path and filter parameters (country, category, currency). Evidence: GET /rest/V1/products with searchCriteria filter on category_id (example category 23); GET /rest/V1/products?searchCriteria[pageSize]=10 for all products.
- **CAT-11** Pricing model is stated: fixed price per SKU or open amount. Evidence: Each SKU carries a single fixed price (e.g. price: 910). Fixed price per SKU.
- **SEC-01** All endpoints are HTTPS only (TLS 1.2+). Evidence: Both endpoints are https://justlounge.com/rest/V1/...

## What the vendor does not have

- **DOC-01** The documentation covers the full order lifecycle the integration needs: catalogue, place order, order status/details, tracking and reconciliation. A catalogue-only doc fails. Evidence: Doc covers only 2 catalogue GETs (category-wise products, all products). No order, status, tracking, returns or reconciliation endpoint anywhere.
- **DOC-02** Every endpoint has a complete request and response example, not a truncated screenshot. Evidence: No request/response examples in text; only Postman screenshots cut off at line 15 of the response (extension_attributes.website_ids).
- **DOC-03** Enumerated and coded fields are explained (for example status 1/2, visibility 1-4, type_id values). Evidence: Response shows status: 1, visibility: 4, type_id: simple, attribute_set_id: 4 with no explanation of values.
- **DOC-04** The document is dated, versioned and names an owner. Evidence: No date, version or owner in the doc. PDF metadata only gives the title.
- **SEC-07** Credentials are delivered through a secure channel per environment and are NOT embedded in the API document or screenshots. Evidence: The PDF and both screenshots contain all four live OAuth values (consumer key/secret, access token/secret) in plain text for the production store. Found by scan_secrets.py; values deliberately not reproduced here.

## Vendor questions (P0 first)

- [P0] **AUTH-01** Authentication method is documented (API key, Basic, OAuth2, HMAC, JWT or session) with the exact header name, format and an example request. Note: OAuth 1.0 with HMAC-SHA1 and four values (consumer key/secret, access token/secret) stated. Where the OAuth params go (Authorization header vs URL) is not stated; the Postman screenshot uses 'Request Body / Request URL'.
- [P0] **AUTH-02** For token auth: token endpoint, grant type, request body and token lifetime (expiry field) are documented and work on staging. NA for static keys. Note: A pre-issued access token is handed over; its lifetime is not stated. A Postman tab 'Get Token Based on OA...' is visible in the screenshot but not documented.
- [P0] **ENV-01** Separate staging/sandbox and production base URLs and credentials exist and are clearly separated. Note: Only https://justlounge.com (the live storefront) is given. No sandbox/staging URL or separate credentials.
- [P0] **CAT-02** Pagination method (page, offset or cursor) is documented with a reliable end-of-list signal (total count or next cursor). Note: Only searchCriteria[pageSize]=10 is shown. Page selection (currentPage) and the end-of-list signal (total_count) are not documented.
- [P0] **CAT-03** Each sellable item has a stable unique identifier (SKU or variant id) that Place Order accepts unchanged. Note: Each item has id and sku (e.g. FR25846371H), but there is no order API, so we cannot confirm the sku is what an order would take.
- [P0] **CAT-04** Product response schema documents name, price, currency, image, description, brand and an active flag with its active value. Note: Visible: id, sku, name, price, status, type_id, created_at, updated_at. Not shown: currency, image, description, brand (screenshot truncated).
- [P0] **PRC-01** The catalogue price is the amount we are charged, or the breakdown (tax, shipping, handling, discount) is documented. Note: price 910 shown with no statement whether it is our buy price, retail price, tax-inclusive, or includes shipping.
- [P0] **ORD-01** Place Order is documented with method, path and the full request schema: required/optional flags, types and max lengths. Note: No order endpoint documented.
- [P0] **ORD-02** A successful order response contains the vendor order id in a named field.
- [P0] **ORD-03** The full success response schema is documented (every field we must store), not only a happy-path example.
- [P0] **ORD-04** Sync vs async is stated: is the order confirmed in the response, or pending and confirmed later by webhook/poll?
- [P0] **ORD-05** Every vendor-required address/recipient field can be filled from our shipping fields (first/last name, address 1/2, city, state/zone, country, postcode, contact number, email). Note: No address schema.
- [P0] **ORD-11** Maximum synchronous response time is documented and is 120 seconds or less; slower processing is async.
- [P0] **ORD-13** It is stated whether an accepted order can later fail BEFORE confirmation, and how that is signalled. Yes = it cannot, or it is signalled as a cancel status.
- [P0] **ORD-14** Serviceability is checkable before or at order time (pincode check endpoint or immediate rejection), and the regions we need are covered. Note: No serviceability/pincode check.
- [P0] **IDM-01** A client reference (PO number) field is accepted on Place Order and returned in order details, webhooks and reports.
- [P0] **IDM-02** Re-sending the same reference never creates a second order; it returns the original order or a specific duplicate error.
- [P0] **IDM-03** After a timeout or 5xx on Place Order, a documented way exists to check if the order was created (lookup by our reference) before retrying.
- [P0] **STS-01** The complete list of order status values is documented with the meaning of each. Note: No order status values documented.
- [P0] **STS-02** Every vendor status maps unambiguously to PENDING, CONFIRMED, SHIPPED, DELIVERED, CANCELED or RETURNED (failed/rejected -> CANCELED). Note: Cannot build a status map.
- [P0] **STS-03** An order-details endpoint returns current status (and tracking) by vendor order id and/or our reference.
- [P0] **STS-05** Terminal statuses are defined, and the maximum time an order can stay pending/processing (or an auto-cancel rule) is stated.
- [P0] **WHK-01** Push status webhooks exist. (Gate needs this or POL-01.)
- [P0] **WHK-02** A sample webhook payload is documented for each status event.
- [P0] **WHK-03** The webhook carries our reference and/or the vendor order id.
- [P0] **WHK-04** Webhook is a JSON POST body. Note whether it has a top-level 'data' key.
- [P0] **WHK-05** Webhook authenticity does not depend on a vendor signature we must verify (unsigned, IP allowlist, or signing optional).
- [P0] **POL-01** A status endpoint is suitable for scheduled polling (single or bulk). (Gate needs this or WHK-01.)
- [P0] **TRK-01** Carrier name and tracking number are returned via API after dispatch (not only on a portal or email).
- [P0] **RTN-03** Returns/replacement/refund process for damaged, wrong or undelivered items is documented with a window.
- [P0] **REC-01** A settlement/payment report or transaction ledger exists (API or scheduled file).
- [P0] **REC-02** Each report line carries our reference and the vendor order id.
- [P0] **ERR-01** An error catalogue lists HTTP status, error code and meaning per endpoint. Note: No error responses documented.
- [P1] **AUTH-03** Expired or revoked token response is documented (401, 403 or a custom code) and refresh behaviour is stated.
- [P1] **AUTH-04** Invalid credentials return a documented error (4xx JSON), not 200 with an error body or an HTML page.
- [P1] **AUTH-07** IP allowlisting requirement (if any) and how to submit our egress IPs per environment are documented.
- [P1] **ENV-02** Sandbox catalogue is representative of production (same fields, comparable products and pricing), and test products are listed.
- [P1] **ENV-03** Sandbox can drive an order through every lifecycle status (confirm, ship, deliver, cancel, return) or trigger test webhooks.
- [P1] **ENV-05** Supported countries and currencies are listed. Note: No country or currency stated anywhere; price field has no currency.
- [P1] **ENV-06** Sandbox/test orders are never physically shipped or billed, and the way to mark or cancel a test order in production is documented.
- [P1] **CAT-05** Variants (size, colour) structure is documented and it is clear which ids the order API needs for a variant. Note: Only a type_id 'simple' item is shown; configurable products/variants not described.
- [P1] **CAT-06** Stock or availability is returned per item/variant, or a stock-check endpoint exists. Note: No stock field or stock endpoint documented.
- [P1] **CAT-07** Availability freshness is stated, and an out-of-stock-at-order-time failure has its own documented error.
- [P1] **CAT-08** Catalogue changes (new items, delistings, price changes) are pushed by webhook, or the recommended polling frequency is stated.
- [P1] **CAT-09** A failing catalogue page returns a non-2xx status, never an empty 200 that looks like the end of the list.
- [P1] **CAT-14** Per-product order constraints are documented: max quantity, mandatory recipient fields (phone, email), region restrictions.
- [P1] **CAT-16** Custom attributes (brand, image, description, category) are mapped to named fields, or the attribute codes to read are listed. Note: Brand, image and description attribute codes are not listed.
- [P1] **PRC-02** Currency codes are ISO 4217 and map to our wallet currency without manual conversion. Note: No currency code in the response or doc.
- [P1] **PRC-03** Price change policy is stated: notice period, and what happens if the price changed between sync and order (reject, or charge new price).
- [P1] **PRC-04** Shipping charges and taxes (GST/VAT) per order are documented: included in price or charged separately per region.
- [P1] **BAL-01** A balance endpoint exists and returns the real-time prepaid balance. NA if the account is postpaid/credit.
- [P1] **BAL-03** An order with insufficient balance is rejected up front with a specific documented error, before any fulfilment.
- [P1] **ORD-06** Formats are stated for country (ISO2/ISO3/name), state (code/name), phone (E.164 or local) and postcode.
- [P1] **ORD-07** Max length per address field and the behaviour on overflow (truncate or reject) are documented.
- [P1] **ORD-08** Optional fields are stated: empty last name, empty address line 2, optional email.
- [P1] **ORD-09** Quantity > 1 and multi-line orders are documented, including whether the vendor order id is per order or per line.
- [P1] **ORD-10** Recipient communications are documented: whether the vendor emails/SMSes the recipient, and if it can be disabled or white-labelled.
- [P1] **ORD-12** Invalid SKU, out-of-stock item and invalid address each return a distinct documented error.
- [P1] **ORD-15** Responsibility for address validation is stated (vendor validates vs our responsibility), with the error returned for a bad address.
- [P1] **ORD-18** Peak volume capacity is stated (orders per day/hour for bulk reward campaigns).
- [P1] **IDM-04** Reference constraints are stated: uniqueness scope (account/global, time window), max length and allowed characters.
- [P1] **IDM-05** An order is retrievable by our reference immediately after placement (or the consistency delay is documented).
- [P1] **STS-04** An order-history endpoint lists orders over a date range with pagination.
- [P1] **STS-06** Partial or split shipments are documented: line-level vs order-level status.
- [P1] **STS-07** Allowed status transitions are documented, including whether a status can move backwards.
- [P1] **STS-08** An unknown order id returns a documented not-found response (404 or code), not a 500.
- [P1] **WHK-06** Payload is plain, or encrypted with AES over base64 with a null IV (the only supported scheme).
- [P1] **WHK-07** Webhook URL registration is documented (self-serve or via vendor, per environment).
- [P1] **WHK-08** Retry policy on non-2xx (count, backoff) and the response the vendor expects are documented.
- [P1] **WHK-09** Duplicate and out-of-order delivery is addressed (event id or event timestamp provided).
- [P1] **WHK-11** The shipped event includes tracking fields (carrier, tracking number, tracking URL).
- [P1] **POL-02** The status field name and response shape for polling are documented.
- [P1] **POL-03** Allowed polling rate is stated, and a bulk status endpoint exists for many orders.
- [P1] **POL-04** Polling and webhook payloads share a shape, or both shapes are documented.
- [P1] **TRK-02** A per-order customer tracking URL is returned.
- [P1] **TRK-03** Estimated delivery date is returned.
- [P1] **TRK-04** Multi-package shipments are represented (multiple tracking numbers, package/shipment ids).
- [P1] **TRK-05** Shipping SLA (days to dispatch, days to deliver) is documented per region.
- [P1] **RTN-01** Vendor-side cancellation is signalled through a status (webhook/poll).
- [P1] **RTN-04** Undeliverable / return-to-origin (RTO) handling is documented: status sent, re-delivery attempts, and credit back to us.
- [P1] **RTN-05** Refund mechanism and timeline are stated (credit to prepaid balance or credit note).
- [P1] **RTN-07** Liability for items lost or damaged in transit is stated (who bears the cost, claim window).
- [P1] **REC-03** Report granularity and amount fields are documented: charged amount, tax, shipping, discount, currency, date.
- [P1] **REC-04** The delay between order completion and appearing in the report is stated.
- [P1] **REC-05** Refunds, cancellations, RTO and partial fulfilment appear in the same report, linked to the original order.
- [P1] **REC-06** Tax invoices (GST-compliant where applicable) are provided per order or per period, with a download/API.
- [P1] **ERR-02** Error responses use one consistent JSON structure across all endpoints.
- [P1] **ERR-03** Failures use proper HTTP status codes (no 200 with success:false), or that pattern is explicitly documented.
- [P1] **ERR-04** Rate limits per endpoint and the over-limit response (429 + Retry-After) are documented.
- [P1] **ERR-05** Retry/backoff guidance is given, including which errors are safe to retry.
- [P1] **ERR-07** Recommended client timeouts per endpoint are stated.
- [P1] **SEC-02** Recipient PII handling is documented: retention, purpose limitation, deletion on request; DPA available.
- [P1] **SEC-03** Credentials are sent in headers, never in query strings. Note: OAuth 1.0 parameters may be sent in the URL (screenshot setting 'Request Body / Request URL'); header-only not stated.
- [P1] **SEC-08** The integration credential is least-privilege (scoped to the resources we call), not an admin-level token. Note: Scope of the Magento integration user is not stated. A Magento integration token can carry admin-level resource access.
- [P1] **SUP-01** A named integration/technical contact and escalation matrix exist.
- [P1] **SUP-02** Production incident response time is documented.
- [P1] **SUP-03** API versioning (URL or header) and a deprecation notice period are documented. Note: Paths use Magento /rest/V1/ versioning; no deprecation policy stated.
- [P2] **AUTH-06** Credential rotation process is documented, ideally with two keys valid at once for zero-downtime rotation.
- [P2] **ENV-04** Onboarding prerequisites (contract, KYB, deposit) and lead time to production keys are documented.
- [P2] **CAT-10** Catalogue size and maximum page size are stated.
- [P2] **CAT-12** Category, warranty/T&C, usage notes and country of availability are provided per product. Note: Category filtering by category_id exists; per-product category, T&C, usage and country fields not shown.
- [P2] **CAT-13** Image URLs are HTTPS, stable and publicly reachable (no expiring signed URLs).
- [P2] **CAT-15** Incremental sync is supported (filter by updated_at or a changes feed). Note: updated_at is present on items, but filtering by it is not documented.
- [P2] **BAL-02** Balance scope (global vs per currency/market) is stated and matches how we fund the account.
- [P2] **BAL-04** Funding model (prepaid, credit line, invoice) and low-balance alerts are documented.
- [P2] **ORD-16** Gift handling is supported: price-free packing slip/invoice, gift message.
- [P2] **ORD-17** Address or recipient changes after placement are supported or explicitly not supported.
- [P2] **STS-09** Dispatch and delivery timestamps are returned in a documented format and timezone.
- [P2] **WHK-10** Webhook source IPs are published.
- [P2] **WHK-12** Missed webhooks can be replayed or resent on request.
- [P2] **TRK-06** Proof of delivery (delivered timestamp, POD, receiver name) is available for disputes.
- [P2] **RTN-02** A client-initiated cancel API exists, with the allowed window.
- [P2] **RTN-06** Replacements are linked to the original order (same id or a documented link).
- [P2] **REC-07** Report format (JSON/CSV), date-range filters and timezone are documented.
- [P2] **ERR-06** Uptime SLA, status page and maintenance notification process are published.
- [P2] **ERR-08** Responses include a request/correlation id for support tickets.
- [P2] **SEC-04** Cross-border orders: customs, duties, HS codes and who pays are documented. NA if domestic only.
- [P2] **SEC-05** Orders are fully prepaid: no cash-on-delivery or payment collection from the recipient.
- [P2] **SEC-06** Restricted items (batteries, liquids, regulated goods) and their shipping restrictions by region are documented.
- [P2] **SUP-04** A changelog is published.
- [P2] **SUP-05** A Postman collection or OpenAPI spec is provided. Note: Postman was used (screenshots of workspace 'RESTful API Basics #blueprint'), but the collection itself was not shared.
