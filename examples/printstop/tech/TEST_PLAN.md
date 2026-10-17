# Printstop: test plan

Two steps, in order: prove the vendor behaves as documented, then prove our code handles what it returns.

## Step 1: Sandbox contract tests (Postman CLI)
Collection: `Printstop.postman_collection.json` (generated from `tech.json`).
Environment: copy `Printstop.postman_environment.template.json` **outside the repo**, fill it in, then:
```bash
postman collection run Printstop.postman_collection.json -e /path/outside/repo/printstop.env.json
```

| # | Request | Asserts | Closes |
|---|---|---|---|
| 00 | Auth: get token | 200; `access_token` present (saved to `{{access_token}}`) | AUTH-02 |
| 00 | Auth: bad secret | 401 | AUTH-04 |
| 01 | Category listing | 200; `success`, `total`, `data` | CAT-01 |
| 02 | Product listing | 200; `total` equals `data.length` (check manually); `product_id`, `name`, `status` | CAT-01, CAT-02 |
| 03 | Product details | 200; `product_details.product_size[]`, `templates[]`. Confirms the undocumented `product_id` selector | CAT-03, CAT-05 |
| 04 | Place order | 200; `orders_id` (saved to `{{orders_id}}`) | ORD-01, ORD-02 |
| 04 | Same reference again | 409; `orders` contains the first id. **If it returns 200, there is no duplicate protection on our store** | IDM-02 |
| 04 | Invalid product | 400 | ORD-12 |
| 04 | Missing address | 400 | ORD-12 |
| 04 | Expired token | 401 | AUTH-03 |
| 05 | Track order | 200; all 8 fields present; `orders_status` is a string | STS-03, POL-02, TRK-01 |
| 05 | Unknown order | 4xx, not 500 | STS-08 |

Also do by hand: time the order call (ORD-11, must be ≤120 s), place two orders for two different
references with the **same email** (checks the §6.1 risk), and ask Printstop to move the test order
to dispatched so tracking fields fill in (ENV-03). Save redacted responses over `fixtures/`.

## Step 2: Unit tests (Jest, vendor-integrations)
A ready skeleton is in `code/Printstop.test.ts` (16 tests). It covers the rows below, including the
409 never-auto-link rule, sku without size, non-India rejection and partial-catalogue throws.
File: `tests/vendors/printstop.*.test.ts`. Patterns: `tests/vendors/oglobalidr.webhookOrderStatusUpdate.test.ts`,
`vendorMerchandiseClass.updateOrderProductStatus*.test.ts`. Mock first:
```ts
jest.mock("@plum-xoxo/correlation-logger/logger", () => ({ logger: { info: jest.fn(), error: jest.fn(), warn: jest.fn(), debug: jest.fn() } }));
jest.mock("@utils/db");
```

| # | Unit | Cases |
|---|---|---|
| 1 | `formatOrderResponse` | `printstopOrder.json` → `code = printstop_merchandise_vendor_6777648`, `apiOrderId "6777648"`, `addedBy "Printstop API"`; no `orders_id` → throws |
| 2 | `errorHandler` | `printstopOrderDuplicate.json` (409) → behaviour agreed in TECH_SPEC §6.1 (refetch only if reference-keyed, else fail); 401 → refresh path |
| 3 | `formatWebhookOrderStatusResponse` | `printstopStatusInProduction.json` → status "In Production", apiOrderId, empty tracking; dispatched sample (after LIVE) → trackingId, link, courier_name; unknown status → returned raw, not thrown; missing `orders_id` → throws |
| 4 | `webhookConfigs.orderStatus` | every value ∈ PENDING/CONFIRMED/SHIPPED/DELIVERED/CANCELED/RETURNED; keys lowercase; no ORDER_FAILED |
| 5 | `formatProductResponse` | `printstopProductDetails.json` → sku `8093_14513`, status 1, brand `""`, `{cdnurl}` replaced; inactive size → status 0 |
| 6 | `getVendorProducts` | listing `total` ≠ `data.length` → throws; a failing details call → throws |
| 7 | `getPlaceOrderReqOptions` | full mapping; empty last name → first name; empty contact → recipientMobileNumber; sku without size → no `size_id`; non-India country → rejected; no credentials in the body or logs |
| 8 | `getRefetchOrderReqOptions` | DB row → `orders_id=<api_order_id>`; only `externalOrderId` → clear error |
| 9 | `getReqHeaders` | Bearer + client-id + client-secret present |
| 10 | `fetchAccessToken` | reads `credentials.printstop`; called once (one credentials key) |
| 11 | polling loop | one 4xx on order_status does not stop the other orders (F11; verify the base loop) |
| 12 | status emails | a second poll with the same status sends no second email (F12 suspected base bug) |

Report: sandbox `x/12 requests, y/z assertions`; unit `x/y`. Classify each failure as vendor
behaviour, our bug, or a wrong test assumption.
