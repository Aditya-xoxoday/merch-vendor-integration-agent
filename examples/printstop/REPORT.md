# Printstop / Mandaala: merchandise API review

Reviewed on: 2026-10-18  
Source: https://deq64r0ss2hgl.cloudfront.net/images/printstop-api-docs.html (Printstop/Mandaala API Reference, single HTML page)  

## Decision

**Can we integrate?** Likely yes, after the vendor answers a few points (2 must-have(s) only partly documented).  
**Does the API work?** Not tested yet (no sandbox run).  
**Must-haves:** 5 met, 2 open, 0 missing (of 7).  
**Other checks covered:** Important 15 of 89, Nice-to-have 2 of 27.

## Must-haves

| | Must-have | Evidence |
|---|---|---|
| Met | Place an order and get an order ID back | ORD-01: POST method=order with profile, product, template, shipping/billing objects; required/optional flags and types in tables; full example body.; ORD-02: Success response: {success, status: 200, orders_id: 6777648}. |
| Met | Our address fields fit their order format | ORD-05: profile: first_name, last_name, email, mobile_number (+ company_name, corporate_id we can fill as constants); shipping: address_line_1, address_line_2, city, state, pincode, country. All derivable from our shipping fields. |
| Met | The product ID from their catalogue (or product list) is what the order takes | CAT-03: Place Order product.product_id is 'ID of the product to be ordered (from Catalog API)'; size_id from Product Details. |
| Open | Get the order status (full status list, a status lookup, and updates by webhook or polling) | STS-01: Track Order returns orders_status_id and orders_status, but only one example value is given (10, 'In Production'). Full list needed.; STS-03: POST method=order_status&orders_id=... returns status, due date, delivery date and tracking fields.; POL-01: Track Order (method=order_status) can be called on a schedule per order. |
| Met | Get courier and tracking number after dispatch | TRK-01: Track Order: tracking_number and shipping_company, blank until dispatched. |
| Open | Retry safely without creating duplicate orders | IDM-01: profile.reference_number 'Unique reference number for the order', but Optional, and not returned by Track Order. Order lookup is only by orders_id.; IDM-02: Duplicate returns HTTP 409 with existing orders [ids], but only for 'one order per user' stores; not keyed on our reference_number.; IDM-03: Retry guidance: 'call Track Order, or rely on the 409'. Track Order needs orders_id, which we do not have after a timeout, so this only works on one-order-per-user stores. |
| Met | Secure login that works (auth method documented, HTTPS) | AUTH-01: Authentication section: JWT via Firebase OAuth 2.0. Every call sends Authorization: Bearer <token> plus client-id and client-secret headers; curl examples given.; SEC-01: All URLs https://www.psstaging.in/... |

## Status mapping

- `in production` -> CONFIRMED

## Important gaps (do not block)

- **DOC-01** The documentation covers the full order lifecycle the integration needs: catalogue, place order, order status/details, tracking and reconciliation. A catalogue-only doc fails. (Covers login, catalogue, place order, duplicate handling and order tracking (with courier). No returns, settlement report or balance.)
- **DOC-02** Every endpoint has a complete request and response example, not a truncated screenshot. (Full request/response examples for every endpoint; Product Details example is marked 'abridged'.)
- **DOC-03** Enumerated and coded fields are explained (for example status 1/2, visibility 1-4, type_id values). (orders_status_id / orders_status: only one example value (10, 'In Production'); the full list is not given.)
- **AUTH-02** For token auth: token endpoint, grant type, request body and token lifetime (expiry field) are documented and work on staging. NA for static keys. (GET method=generate_token&corporate_id=... with client-secret, client-id, user-name headers returns access_token. Token lifetime is not stated.)
- **AUTH-04** Invalid credentials return a documented error (4xx JSON), not 200 with an error body or an HTML page.
- **AUTH-07** IP allowlisting requirement (if any) and how to submit our egress IPs per environment are documented.
- **ENV-02** Sandbox catalogue is representative of production (same fields, comparable products and pricing), and test products are listed.
- **ENV-03** Sandbox can drive an order through every lifecycle status (confirm, ship, deliver, cancel, return) or trigger test webhooks. (No way to move a sandbox order through statuses is described.)
- **ENV-05** Supported countries and currencies are listed. (Country is a numeric code; only 99 = India is listed. Prices shown in Rs. Other countries/currencies not stated.)
- **ENV-06** Sandbox/test orders are never physically shipped or billed, and the way to mark or cancel a test order in production is documented.
- **CAT-02** Pagination method (page, offset or cursor) is documented with a reliable end-of-list signal (total count or next cursor). (Listings return 'total' and a data array; no page or limit parameters are documented.)
- **CAT-04** Product response schema documents name, price, currency, image, description, brand and an active flag with its active value. (Product Details: product_name, product_long_des, product_images, category_id, visible. No exact price field, no currency field, no brand field.)
- **CAT-06** Stock or availability is returned per item/variant, or a stock-check endpoint exists. (No stock field or endpoint.)
- **CAT-07** Availability freshness is stated, and an out-of-stock-at-order-time failure has its own documented error.
- **CAT-08** Catalogue changes (new items, delistings, price changes) are pushed by webhook, or the recommended polling frequency is stated.
- **CAT-09** A failing catalogue page returns a non-2xx status, never an empty 200 that looks like the end of the list.
- **CAT-11** Pricing model is stated: fixed price per SKU or open amount. (price_defining_method 'Range Based With Multiplication'; short description 'Ranging from Rs. 925 to Rs. 1075'. Exact price per size is not returned.)
- **CAT-14** Per-product order constraints are documented: max quantity, mandatory recipient fields (phone, email), region restrictions. (Some stores allow one order per user (see Duplicate Order Handling); create_user has numorders. No max quantity per product.)
- **PRC-01** The catalogue price is the amount we are charged, or the breakdown (tax, shipping, handling, discount) is documented. (Only a price range in HTML text; tax rates given separately (CGST/SGST/IGST). The amount we will be charged per order is not stated.)
- **PRC-02** Currency codes are ISO 4217 and map to our wallet currency without manual conversion. (Prices shown as 'Rs.' in text; no currency code field.)
- **PRC-03** Price change policy is stated: notice period, and what happens if the price changed between sync and order (reject, or charge new price).
- **PRC-04** Shipping charges and taxes (GST/VAT) per order are documented: included in price or charged separately per region. (GST rates and HSN per product are returned; shipping charges not mentioned.)
- **ORD-04** Sync vs async is stated: is the order confirmed in the response, or pending and confirmed later by webhook/poll? (Returns orders_id immediately, then statuses like 'In Production' via Track Order. Not stated whether the order is confirmed at placement.)
- **ORD-06** Formats are stated for country (ISO2/ISO3/name), state (code/name), phone (E.164 or local) and postcode. (Country = numeric code (99 India), state as name, pincode as string. Phone format not stated.)
- **ORD-07** Max length per address field and the behaviour on overflow (truncate or reject) are documented. (No max lengths.)
- **ORD-08** Optional fields are stated: empty last name, empty address line 2, optional email. (last_name and company_name marked Required; address_line_2 optionality not stated.)
- **ORD-09** Quantity > 1 and multi-line orders are documented, including whether the vendor order id is per order or per line. (product is a single object with no quantity field: looks like one item per order. Needs confirmation.)
- **ORD-10** Recipient communications are documented: whether the vendor emails/SMSes the recipient, and if it can be disabled or white-labelled.
- **ORD-11** Maximum synchronous response time is documented and is 120 seconds or less; slower processing is async.
- **ORD-12** Invalid SKU, out-of-stock item and invalid address each return a distinct documented error.
- **ORD-13** It is stated whether an accepted order can later fail BEFORE confirmation, and how that is signalled. Yes = it cannot, or it is signalled as a cancel status.
- **ORD-14** Serviceability is checkable before or at order time (pincode check endpoint or immediate rejection), and the regions we need are covered. (No pincode check.)
- **ORD-15** Responsibility for address validation is stated (vendor validates vs our responsibility), with the error returned for a bad address.
- **ORD-18** Peak volume capacity is stated (orders per day/hour for bulk reward campaigns).
- **IDM-04** Reference constraints are stated: uniqueness scope (account/global, time window), max length and allowed characters.
- **IDM-05** An order is retrievable by our reference immediately after placement (or the consistency delay is documented).
- **STS-02** Every vendor status maps unambiguously to PENDING, CONFIRMED, SHIPPED, DELIVERED, CANCELED or RETURNED (failed/rejected -> CANCELED). (Only 'In Production' can be mapped so far (to CONFIRMED).)
- **STS-04** An order-history endpoint lists orders over a date range with pagination.
- **STS-05** Terminal statuses are defined, and the maximum time an order can stay pending/processing (or an auto-cancel rule) is stated. (Terminal statuses not defined; orders_due_date gives a committed date.)
- **STS-06** Partial or split shipments are documented: line-level vs order-level status.
- **STS-07** Allowed status transitions are documented, including whether a status can move backwards.
- **STS-08** An unknown order id returns a documented not-found response (404 or code), not a 500.
- **WHK-02** A sample webhook payload is documented for each status event.
- **WHK-03** The webhook carries our reference and/or the vendor order id.
- **WHK-04** Webhook is a JSON POST body. Note whether it has a top-level 'data' key.
- **WHK-05** Webhook authenticity does not depend on a vendor signature we must verify (unsigned, IP allowlist, or signing optional).
- **WHK-06** Payload is plain, or encrypted with AES over base64 with a null IV (the only supported scheme).
- **WHK-07** Webhook URL registration is documented (self-serve or via vendor, per environment).
- **WHK-08** Retry policy on non-2xx (count, backoff) and the response the vendor expects are documented.
- **WHK-09** Duplicate and out-of-order delivery is addressed (event id or event timestamp provided).
- **WHK-11** The shipped event includes tracking fields (carrier, tracking number, tracking URL).
- **POL-03** Allowed polling rate is stated, and a bulk status endpoint exists for many orders. (Single-order lookup only; no bulk status endpoint; allowed polling rate not stated.)
- **POL-04** Polling and webhook payloads share a shape, or both shapes are documented.
- **TRK-04** Multi-package shipments are represented (multiple tracking numbers, package/shipment ids).
- **TRK-05** Shipping SLA (days to dispatch, days to deliver) is documented per region. (product_production_days per size; delivery days after dispatch not stated.)
- **RTN-01** Vendor-side cancellation is signalled through a status (webhook/poll).
- **RTN-03** Returns/replacement/refund process for damaged, wrong or undelivered items is documented with a window.
- **RTN-04** Undeliverable / return-to-origin (RTO) handling is documented: status sent, re-delivery attempts, and credit back to us.
- **RTN-05** Refund mechanism and timeline are stated (credit to prepaid balance or credit note).
- **RTN-07** Liability for items lost or damaged in transit is stated (who bears the cost, claim window).
- **REC-01** A settlement/payment report or transaction ledger exists (API or scheduled file).
- **REC-02** Each report line carries our reference and the vendor order id.
- **REC-03** Report granularity and amount fields are documented: charged amount, tax, shipping, discount, currency, date.
- **REC-04** The delay between order completion and appearing in the report is stated.
- **REC-05** Refunds, cancellations, RTO and partial fulfilment appear in the same report, linked to the original order.
- **REC-06** Tax invoices (GST-compliant where applicable) are provided per order or per period, with a download/API.
- **ERR-02** Error responses use one consistent JSON structure across all endpoints. (Error shape {success, status, message, orders}; success is the string "true" on success but boolean false on error.)
- **ERR-04** Rate limits per endpoint and the over-limit response (429 + Retry-After) are documented.
- **ERR-07** Recommended client timeouts per endpoint are stated.
- **SEC-02** Recipient PII handling is documented: retention, purpose limitation, deletion on request; DPA available. (create_user sends email, phone and address as URL query parameters; no data-handling policy stated.)
- **SEC-08** The integration credential is least-privilege (scoped to the resources we call), not an admin-level token.
- **SUP-01** A named integration/technical contact and escalation matrix exist.
- **SUP-02** Production incident response time is documented.
- **SUP-03** API versioning (URL or header) and a deprecation notice period are documented. (Mentions 'feature flag or versioned behaviour' for the 401-to-409 change; no versioning or deprecation policy.)

## Nice-to-have gaps (do not block)

- **DOC-04** The document is dated, versioned and names an owner. (No date, version or owner on the page.)
- **AUTH-06** Credential rotation process is documented, ideally with two keys valid at once for zero-downtime rotation.
- **ENV-04** Onboarding prerequisites (contract, KYB, deposit) and lead time to production keys are documented.
- **CAT-10** Catalogue size and maximum page size are stated.
- **CAT-13** Image URLs are HTTPS, stable and publicly reachable (no expiring signed URLs).
- **CAT-15** Incremental sync is supported (filter by updated_at or a changes feed).
- **BAL-01** A balance endpoint exists and returns the real-time prepaid balance. Not needed to integrate. NA if the account is postpaid/credit.
- **BAL-02** Balance scope (global vs per currency/market) is stated and matches how we fund the account.
- **BAL-03** An order with insufficient balance is rejected up front with a specific documented error, before any fulfilment.
- **BAL-04** Funding model (prepaid, credit line, invoice) and low-balance alerts are documented.
- **ORD-17** Address or recipient changes after placement are supported or explicitly not supported.
- **STS-09** Dispatch and delivery timestamps are returned in a documented format and timezone. (Dates like '17 Jul, 2024' (orders_date_finished, orders_due_date, actual_delivery_date); timezone not stated.)
- **WHK-10** Webhook source IPs are published.
- **WHK-12** Missed webhooks can be replayed or resent on request.
- **TRK-06** Proof of delivery (delivered timestamp, POD, receiver name) is available for disputes. (actual_delivery_date only; no proof of delivery.)
- **RTN-02** A client-initiated cancel API exists, with the allowed window.
- **RTN-06** Replacements are linked to the original order (same id or a documented link).
- **REC-07** Report format (JSON/CSV), date-range filters and timezone are documented.
- **ERR-06** Uptime SLA, status page and maintenance notification process are published.
- **ERR-08** Responses include a request/correlation id for support tickets.
- **SEC-04** Cross-border orders: customs, duties, HS codes and who pays are documented. NA if domestic only.
- **SEC-05** Orders are fully prepaid: no cash-on-delivery or payment collection from the recipient.
- **SEC-06** Restricted items (batteries, liquids, regulated goods) and their shipping restrictions by region are documented.
- **SUP-04** A changelog is published.
- **SUP-05** A Postman collection or OpenAPI spec is provided. (Only an HTML page; no Postman collection or OpenAPI file linked.)

## Coverage by area

| Area | Yes | No | Open | Not available | NA |
|---|---|---|---|---|---|
| Documentation Quality | 0 | 1 | 2 | 1 | 0 |
| Access & Authentication | 2 | 0 | 1 | 3 | 1 |
| Environments & Onboarding | 1 | 0 | 1 | 4 | 0 |
| Catalogue & Product Sync | 5 | 0 | 4 | 7 | 0 |
| Pricing, Currency & Balance | 0 | 0 | 3 | 5 | 0 |
| Order Placement & Address | 5 | 0 | 4 | 9 | 0 |
| Idempotency & Duplicates | 0 | 0 | 3 | 2 | 0 |
| Order Status & Lifecycle | 1 | 0 | 3 | 5 | 0 |
| Webhooks | 0 | 0 | 0 | 12 | 0 |
| Polling | 2 | 0 | 1 | 1 | 0 |
| Shipment Tracking | 3 | 0 | 2 | 1 | 0 |
| Cancellation, Returns & Refunds | 0 | 0 | 0 | 7 | 0 |
| Reconciliation & Settlement | 0 | 0 | 0 | 7 | 0 |
| Errors, Rate Limits & Reliability | 3 | 0 | 1 | 4 | 0 |
| Security, Data & Compliance | 3 | 0 | 1 | 4 | 0 |
| Support & Versioning | 0 | 1 | 1 | 3 | 0 |
