# Reading vendor documentation: intake playbook

## By format

| Format | How to read it | Common traps |
|---|---|---|
| PDF | Extract text (`pypdf`). Extract **every embedded image** and view it. Read link annotations for URLs. Record metadata | Text splits one word per line; screenshots hold the only response examples and sometimes secrets |
| Word (.docx) | Read the text and tables, and extract images | Tables of fields lose structure in plain text |
| OpenAPI / Swagger JSON or YAML | Parse `paths`, `components.schemas`, `securitySchemes`, `enum`s and `examples` | The rendered page hides enums; `required` arrays live on the schema |
| Postman collection | Parse `item[].request`, `auth`, `event` (pre-request scripts), `response[]` examples and variables | Auth is often set at collection or folder level, not on the request |
| Postman documenter / readme.io / Stoplight page | Use the browser: expand every section, switch language tabs, read rendered text, and look for "download spec" | Lazy loading; content missing from the raw HTML |
| Screenshots only | View each one and transcribe the fields you see, marking anything cut off as truncated | Never assume what is below the visible area |
| Email / chat text | Treat as docs of the lowest confidence; record the date and sender role | Promises in email are not API contracts: answer **Open**, not Yes |

## Evidence rules
- Quote the location: "p2, Orders > Create" or "OpenAPI POST /orders responses.201".
- Use a short paraphrase. Never paste long passages.
- A screenshot counts as evidence only for what is visible. A response cut off at line 15 says
  nothing about fields below it.
- Vendor screenshots of production calls are **vendor evidence**, not our live test.

## Synonyms to search before answering "Not available"

| Concept | Also search for |
|---|---|
| Our reference (IDM-01) | po_number, client_reference, external_id, merchant_order_id, partner_order_id, reference_no, increment_id |
| Vendor order id (ORD-02) | order_id, order_no, entity_id, increment_id, sales_order_id |
| Tracking number (TRK-01) | AWB, airway bill, docket, consignment, waybill, LR number, shipment number |
| Carrier (TRK-01) | courier, logistics partner, shipping provider, 3PL, carrier_code |
| Serviceability (ORD-14) | pincode, zipcode check, deliverability, coverage, serviceable |
| Webhook (WHK-01) | callback, notification URL, push, event subscription, postback |
| Settlement (REC-01) | statement, ledger, invoice report, transaction report, MIS |
| Return to origin (RTN-04) | RTO, undelivered, returned to sender, NDR |
| Cancel (RTN-01/02) | void, abort, reject, revoke |
| Stock (CAT-06) | inventory, qty, quantity_available, is_in_stock, salable |
| Rate limit (ERR-04) | throttle, quota, 429, requests per minute |
| Idempotency (IDM-02) | duplicate, idempotency-key, already exists, replay |
