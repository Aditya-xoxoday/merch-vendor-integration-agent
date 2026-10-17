# Printstop / Mandaala: technical spec

Source: Printstop/Mandaala API Reference (reviewed 2026-10-18). Contract per
`references/connector_reference.md` (merch-sensei, vendor-integrations `canvas`, Oct 2026).
**Code wins over this file**: re-read `vendorBaseClass.ts`, `vendorMerchandiseClass.ts` and
`Dpanda.ts` on the target branch before building.

> **Check first:** our system already knows a Printstop merchandise vendor. karma has
> `define('PRINTSTPMERCHANDISE_VENDOR_ID', …)` (merch-sensei Phase 3C anchors on it), and
> merch-sensei says "Printstop and Sharaf DG follow the same pattern" as DPanda. Before writing a
> new class, run `git grep -in printstop` in vendor-integrations, karma and order-process-ms. If a
> connector exists, this spec becomes a **diff against it** (new duplicate 409 behaviour,
> `order_status` fields), not a new build.

## 1. Feasibility

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Printstop: feasibility (docs only, sandbox not run)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
AUTH            ⚠️ JWT via generate_token (GET) → tokens table via /vendor/updateAccessToken.
                   TTL not documented. Every call also needs client-id + client-secret headers.
ORDER           ✅ POST method=order → orders_id. Async (In Production after) → iswebhookConfiration true.
                   code/apiOrderId/addedBy contract OK.
IDEMPOTENCY     ⚠️ 409 + orders[] only on one-order-per-user stores. reference_number optional, not echoed,
                   no lookup by it. A timeout on a normal store cannot be resolved safely.
ADDRESS         ✅ shipping_* map cleanly. company_name + corporate_id are constants. country → 99 (India only).
STATUS MAP      ⚠️ Only "In Production" (10) documented. Full list needed before go-live.
WEBHOOK         ➖ None. Polling only.
POLLING         ✅ order_status returns top-level `orders_status`, the field the base polling loop reads.
                   Add the id to merchandiseOrderTrackingVendorIds.
PRE-CONFIRM FAIL ⚠️ Not documented whether an accepted order can be rejected. If so, it must surface as
                   a cancel status (map to CANCELED).
TRACKING        ✅ tracking_number, tracking_url, shipping_company, orders_due_date, actual_delivery_date.
CANCEL/RETURNS  ⚠️ No outbound cancel (platform limit anyway); no returns process documented.
CATALOG         ⚠️ product_listing (no paging, has total) + product_details per product. product_details
                   has no documented product selector. No exact price, no brand, no stock.
BALANCE         ➖ None. No karma_reports module.
SANDBOX RUN     0/12 requests run (no credentials yet).
COMPLEXITY      Medium (nested order body, token + 2 static headers, N+1 catalogue, fixedSku amounts set by hand)
RISKS           duplicate-order false match (see §6.1), unknown token TTL, unmapped statuses, price source
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## 2. Endpoints (all `POST {baseUrl}/services/api.php?method=…` unless noted)

| Op | Method + query | Headers | Body | Success | Errors |
|---|---|---|---|---|---|
| Token | `GET ?method=generate_token&corporate_id={corporateId}` | Content-Type, client-secret, client-id, user-name | none | `{success:"true", status:200, access_token}` | 401 bad credentials |
| Place order | `?method=order` | Authorization: Bearer, client-secret, client-id | profile, product, template?, shipping/billing | `{success:"true", status:200, orders_id}` | 400, 401, 409 `{success:false, status:409, message, orders:[id]}`, 500 |
| Track order | `?method=order_status&orders_id={apiOrderId}` | same | none | orders_id, orders_status_id, orders_status, orders_due_date, actual_delivery_date, tracking_number, tracking_url, shipping_company, orders_date_finished, email_id, internal_notes | 400/401/500 (unknown id not documented) |
| Categories | `?method=category_listing` | same | none | `{total, data:[{category_id, parent_id, category_name, status, …}]}` | |
| Products | `?method=product_listing` | same | none | `{total, data:[{product_id, name, status}]}` | |
| Product details | `?method=product_details` (**selector undocumented**; assume `&product_id=`) | same | "None" | `product_details{product_size[], templates[], product_images[], tax_details, product_hsn, visible, …}` | |
| Create user | `?method=create_user&…` (all in query) | same | none | `{user_id, email}` | not needed unless orders require an existing user (ask) |

Quirks: `success` is the string `"true"` on success and boolean `false` on error, so branch on the
HTTP status, never on `success`. All operations share one path, so call logs must record the
`method` query param to be readable.

## 3. Class plan: `src/vendors/integratedVendors/Printstop.ts`

```typescript
import VendorMerchandiseClass from "@vendors/integratedVendors/vendorMerchandiseClass";
export default class Printstop extends VendorMerchandiseClass implements VendorBaseInterface, VendorMerchandiseInterface { … }
```
Registry key = exported class name `Printstop` (`vendorClassIdMapping`). Reference: `Dpanda.ts`
(fixedSku, token), `amazonIndia.ts` (tracking fetch).

| Method | Printstop implementation |
|---|---|
| `fetchAccessToken(key)` | `GET {baseUrl}/services/api.php?method=generate_token&corporate_id={credentials.corporateId}` with headers `client-secret`, `client-id`, `user-name` from `credentials`. Return `access_token`. Unknown TTL: schedule `/vendor/updateAccessToken` conservatively (for example every 30 min) until Printstop confirms. |
| `getReqHeaders(data)` | `{ Authorization: \`Bearer ${await getAccessTokenFromDb(vendorId)}\`, "client-secret": creds.clientSecret, "client-id": creds.clientId, "Content-Type": "application/json" }` |
| `getPlaceOrderReqOptions(data)` | Override (nested body). Private helpers: `buildProfile`, `buildProduct`, `buildShipping` (each ≤120 lines). See §4. |
| `formatOrderResponse(res, data)` | `const id = res?.orders_id; if (!id) throw res;` → `{ code: \`${model}_vendor_${id}\`, pin: "", validity: "", apiOrderId: String(id), addedBy: "Printstop API" }` |
| `getVoucherValidity` | `""` |
| `errorHandler(err, data)` | HTTP 409 with `orders[]` → **see §6.1 before calling `callVendorRefetch`**. 401 → token refresh then retry once (base 401 handling). Others → base. |
| `getRefetchOrderReqOptions(row)` | `POST …?method=order_status&orders_id=${row.api_order_id}`. From `voucherReqDataFormat` (only `externalOrderId`): **no lookup by reference exists**, so throw a clear error (`Printstop: refetch needs api_order_id`) instead of guessing. |
| `formatWebhookOrderStatusResponse(d)` | Polling shape only. `{ externalOrderId: "", apiOrderId: String(d.orders_id), status: d.orders_status, statusCode: String(d.orders_status_id), trackingId: d.tracking_number \|\| "", link: d.tracking_url \|\| "", courier_name: d.shipping_company \|\| "", dispatched_date: "", delivery_date: parseDate(d.actual_delivery_date) }`. Unknown status → return raw (base stores tracking only). Throw only if `orders_id` is missing. |
| `fetchTrackingDetailsFromVendor` | Call order_status per order product. Return `[{orderProductId, trackingDetails:{trackingId: tracking_number, trackingUrl: tracking_url, courierName: shipping_company, estimatedDelivery: parseDate(orders_due_date)}, status}]` |
| `getVendorProducts()` | `product_listing` → assert `data.length === total` (else throw) → `product_details` for each `product_id` (throw on any failure: sync truncates the table). Skip products whose `templates` need an image block (we cannot supply one), or flag them. |
| `formatProductResponse(p)` | One row per `product_size` entry: `sku = \`${product_id}_${size_id}\`` (no sizes → `\`${product_id}\``). `name = product_name + " - " + size_title`; `status = visible === "Active" && size.visible === "Active" ? 1 : 0`; `description = product_long_des`; `image = product_image` with `{cdnurl}` replaced (base URL to confirm); `categories = category_id`; `brand = ""` (not provided; karma listing needs the column); `denominations` = **manual** (no price in API; amounts go in `printstop_merchandise_product_to_denominations` via the karma product form). |
| `formatWebhookProductResponse` | documented no-op `{ sku: "", status: 2 }` (no product webhook) |

Dates arrive as `"17 Jul, 2024"`: parse with an explicit format (`DD MMM, YYYY`). Timezone is
unknown, so treat it as IST and note that.

## 4. Order body mapping (`getPlaceOrderReqOptions`)

```jsonc
{
  "profile": {
    "first_name": data.shipping_firstname,
    "last_name": data.shipping_lastname || data.shipping_firstname,   // required on their side
    "email": data.email,                                              // see §6.1
    "mobile_number": data.shipping_contact_no || data.recipientMobileNumber,
    "company_name": creds.companyName,                                // constant
    "corporate_id": Number(creds.corporateId),
    "reference_number": String(data.voucherInsertId),                 // our externalOrderId
    "department_id": 0
  },
  "product": { "product_id": Number(sku.split("_")[0]), "size_id": Number(sku.split("_")[1]) /* omit if absent */ },
  "shipping": {
    "address_line_1": data.shipping_address_1, "address_line_2": data.shipping_address_2 || "",
    "city": data.shipping_city, "state": data.shipping_zone, "pincode": data.shipping_postcode,
    "country": countryCode(data.shipping_country_id)                  // 99 = India; reject others until confirmed
  },
  "corporate_billing_id": Number(creds.corporateBillingId)           // or copy shipping into "billing"
}
```
No `quantity` field exists: one order product means one vendor order (`maxCardsPerRequest: 1`).
Products with `templates` need `template_id` plus each `blockN_name`. We have no personalisation
input, so exclude those products from sync or send defaults agreed with Printstop.

## 5. Config and registration
- `src/configs/vendorConfigs/Printstop.json`: generated draft in `vendor_config.draft.json`. Add
  credential keys `companyName` and `corporateBillingId` (placeholders) for §4. Staging values stay
  local (gitignored).
- `baseConfigs.json` (+ `.sample`): `vendorClassIdMapping."Printstop" = "<vendorId>"`;
  `merchandiseOrderTrackingVendorIds += <vendorId>`; `vendorCallLogger.mongo.redactHeaders +=
  ["client-secret", "client-id", "user-name"]`. Then `npm run merge-configs`.
- `webhookConfigs.orderStatus` (lowercase keys): `"in production": "CONFIRMED"` plus the rest once
  Printstop shares the list. Expected shape (to confirm): placed/approved → PENDING or CONFIRMED,
  dispatched/shipped → SHIPPED, delivered → DELIVERED, cancelled/rejected → CANCELED, returned/RTO →
  RETURNED. Never `ORDER_FAILED`.
- No plumAuth webhook route (no webhooks). No karma_reports balance module (no balance API).
- OPMS: `vendorIntegration.integratedVendors += "<vendorId>"` (string) if not already present.
- karma: **already has** `PRINTSTPMERCHANDISE_VENDOR_ID`. Verify the listing page, `getRoutes`,
  header menu and (fixedSku) `FIXED_SKU_VENDORS` entry exist on every env branch, and do not add
  duplicates.

## 6. Risks (with mitigation)

### 6.1 Duplicate-order false match (high)
The 409 fires when **the same user** already has an order on a one-order-per-user store. It is not
keyed on our reference. If two different rewards go to the same recipient email, the second order
gets a 409 that returns the **first** order's id. A naive `errorHandler → callVendorRefetch` would
then attach reward #2 to order #1, so the recipient receives one item and we record two as fulfilled.
**Mitigation:** confirm with Printstop that our corporate store has no per-user limit. In
`errorHandler`, treat 409 as "already exists" **only** if Printstop confirms `reference_number`
uniqueness. Otherwise fail the order (OPM existing error) for manual review.

### 6.2 Timeout without an order id (high)
No lookup by `reference_number`. After a timeout we cannot tell whether the order exists.
**Mitigation:** ask Printstop for lookup by reference (or a 409 keyed on reference). Until then,
fail to manual review, and never blind-retry.

### 6.3 Unknown token TTL (medium)
Refresh conservatively. 401 at runtime → refresh and retry once.

### 6.4 Status list incomplete (medium)
Unmapped statuses update tracking only. Orders could sit at status 1 forever (polling never stops
for status NOT IN (3,5)). Get the full list before go-live.

### 6.5 Price source (medium)
No price in the API. Amounts are set by hand per sku in karma (fixedSku Variant B). A price change
at Printstop would be silent, so ask for a price field or a price-change notice.

### 6.6 N+1 catalogue (low)
One details call per product. Check catalogue size and rate limits; consider `VendorBatchSyncClass`
if large.

## 7. Open questions for Printstop (blocking first)
1. Full `orders_status_id` / `orders_status` list with meanings.
2. Is `reference_number` unique per store with a 409 on reuse? Can `order_status` look up by `reference_number`?
3. Does our store have a one-order-per-user limit? Must the recipient exist as a user (`create_user`) first?
4. Quantity: always 1 per order?
5. How does `product_details` select the product? What is `{cdnurl}`?
6. Exact price per product/size, currency, GST/shipping included?
7. Token lifetime; rate limits; paging for `product_listing`.
8. Can an accepted order be rejected before production, and with which status?

## 8. Done means
- Sandbox: all 12 Postman requests pass (`Printstop.postman_collection.json`).
- Unit: the minimum Jest set in `TEST_PLAN.md` passes.
- `npm run merge-configs && npx tsc && npm run lint && npx jest tests/vendors/printstop` is green.
- Staging smoke: order → poll → `merchandise_vendor_order_details` 1 → 2 → 3, `courier_tracking` row present.
