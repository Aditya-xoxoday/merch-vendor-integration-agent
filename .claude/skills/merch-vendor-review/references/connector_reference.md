# Connector reference: how a review turns into a build

This file has the depth needed to write a tech pack that `/merch-sensei` can build from directly.
It is condensed from [merch-sensei](https://github.com/abhishekkxoxo/merch-sensei) (vendor-integrations
`canvas`, Oct 2026). **Code wins over this file.** Line numbers are hints; re-read the code on the
target branch. Abbreviations: **BC** = `vendorBaseClass.ts`, **MC** = `vendorMerchandiseClass.ts`,
**VI** = vendor-integrations, **OPMS** = order-process-ms.

## 1. Lifecycle (where each vendor endpoint plugs in)

```
OPMS __autoProcureVendorProducts
  └─ vendor_id ∈ vendorIntegration.integratedVendors (STRING) → VI POST /vendor/procure_voucher (hash header)
VI procureVoucherFromVendor
  ├─ merchandiseVendor = true → duplicate guard (BC ~:225, OPM00063) + processMerchandiseOrderResponses (BC ~:346)
  │     → merchandise_vendor_order_details row
  ├─ iswebhookConfiration = true → egift row later, on confirmed/shipped; false → egift row now
  └─ formatOrderResponse MUST return a truthy `code` (BC ~:488 throws otherwise)
Vendor webhook → plumAuth POST /webhook/orderUpdate/<name-lowercase>
  └─ api.integratedVendors.<name> = <vendorId> → VI /vendor/webhookOrderStatusUpdate (rawPayload wraps {data: body})
VI webhookOrderStatusUpdate (MC) → formatWebhookOrderStatusResponse → status lowercased
  → webhookConfigs.orderStatus → {pending, confirmed, shipped, delivered, canceled, returned}
  → courier_tracking, order_product status, order, email; canceled → refund_ms
  → unmapped status → tracking only ("<name>: unmapped webhook status…")
Polling: POST /vendor/merchandiseOrderTracking {vendorId} (ids in merchandiseOrderTrackingVendorIds; external scheduler)
  → rows with status NOT IN (3,5) → getRefetchOrderReqOptions(<DB row>) → reads res["orders_status"]
  → webhookOrderStatusUpdate(raw polling response)
Product sync: POST /vendor/sync_products {vendorId} → TRUNCATE + insert → vanished SKUs DISABLED
```

`merchandise_vendor_order_details.status`: 1 pending/confirmed, 2 shipped, 3 delivered, 5 canceled, 10 returned.

## 2. Class contract (`extends VendorMerchandiseClass`)

| Method | When | Contract |
|---|---|---|
| `getReqHeaders(data, reqOptions?)` | always | Static key from `this.config.configs.credentials[...]`, or `getAccessTokenFromDb(vendorId, tokenType?)` |
| `fetchAccessToken(credentialKey)` | token vendors | Called per key of `configs.credentials` by `/vendor/updateAccessToken`; stored in `tokens` |
| `getPlaceOrderReqOptions(data)` | nested bodies | Build the body from OPMS shipping fields; private helpers ≤120 lines each |
| `formatOrderResponse(response, data)` | always | `{ code: \`${model}_vendor_${apiOrderId}\`, pin: "", validity: "", apiOrderId: String(id), addedBy: \`${name} API\` }`; no id → `throw response`; `addedBy` must match exactly |
| `getVoucherValidity` | always | return `""` |
| `formatWebhookOrderStatusResponse(data)` | always | `{externalOrderId, status, statusCode, apiOrderId, trackingId, link, courier_name, dispatched_date, delivery_date}`; must accept webhook AND polling shapes; unknown status → return raw (tracking only); throw only on structurally invalid payloads |
| `formatWebhookProductResponse` | always | No-op `{sku: '', status: 2}` allowed if no product webhook |
| `getVendorProducts` / `formatProductResponse` | catalogue API | **Any page failure must throw**; sku deterministic and reversible; inactive → `status: 0`; populate `brand` |
| `fetchTrackingDetailsFromVendor` | any order-detail API | Called when cached tracking > 1 day; returns `[{orderProductId, trackingDetails:{trackingId,trackingUrl,courierName,estimatedDelivery}, status}]` |
| `getRefetchOrderReqOptions` / `formatRefetchOrderRes` | polling/refetch | Handle the DB row (`insert_id`, `api_order_id`) AND `voucherReqDataFormat` (`externalOrderId`) |
| `errorHandler(error, data)` | vendor-specific codes | Base handles 400/401/403/404/500/502/503/504; "order already exists" → `return await this.callVendorRefetch(data)`; reuse `OPM000xx` from `src/utils/errors.ts` |

OPMS shipping fields: `shipping_firstname`, `shipping_lastname`, `shipping_address_1`, `shipping_address_2`,
`shipping_city`, `shipping_zone`, `shipping_country`, `shipping_country_id`, `shipping_postcode`,
`shipping_contact_no`, `recipientMobileNumber`.

Reference vendors: `Dpanda.ts` (newest, fixedSku), `verdical.ts` / `lakee.ts` (simple token), `amazonIndia.ts` (tracking + stock).

## 3. Vendor config (`src/configs/vendorConfigs/{ClassName}.json`, gitignored)

```json
{
  "{vendorId}": {
    "vendorData": { "vendorId": 0, "vendorType": "fixedSku", "name": "{ClassName}", "model": "{model}",
                    "merchandiseVendor": true, "iswebhookConfiration": true },
    "vendorTableMapping": { "table": "{model}_products", "skuTable": "{model}_product_to_denominations",
                            "extraInfo": false, "countryColumn": "", "currencyColumn": "" },
    "placeOrderReqConfigs": { "url": "...", "method": "POST", "body": {} },
    "refetchOrderReqConfigs": { "url": "...", "method": "GET" },
    "accessTokenConfigs": { "url": "...", "method": "POST" },
    "webhookConfigs": { "isDataEncrypted": false, "orderStatus": { "<vendor status lowercase>": "CONFIRMED" } },
    "productListingConfigs": { "method": "GET", "getProducts": "..." },
    "configs": { "baseUrl": "...", "maxApiAtaTime": 1, "maxCardsPerRequest": 1, "pickConfigCustomerInfo": false,
                 "credentials": { "<key>": "<placeholder>" } }
  }
}
```
**Credentials shape:** `/vendor/updateAccessToken` calls `fetchAccessToken(credentialKey)` once **per
key** of `configs.credentials`. A token vendor with one login must nest every field under one key,
`{"<tokenKey>": {"clientId": …, "clientSecret": …}}`. Flat keys would trigger one token call per field.

Rules: `merchandiseVendor` MUST be true (else no merch row and the first status update crashes);
`orderStatus` values only the six (single-L CANCELED, never ORDER_FAILED); `fixedSku` requires
`skuTable`; `baseUrl`, `maxApiAtaTime`, `maxCardsPerRequest` truthy; no `null` in `vendorData`;
include refetch/accessToken/productListing blocks only when used. Register `"{ClassName}": "{vendorId}"`
in `vendorClassIdMapping`; polling vendors go in `merchandiseOrderTrackingVendorIds`; custom auth
headers in `vendorCallLogger.mongo.redactHeaders`; then `npm run merge-configs` (never hand-edit `config.json`).

## 4. Outside VI (handoff checklist items)
- OPMS `config_voucher_process.json`: `vendorIntegration.integratedVendors += "{vendorId}"` (string), `vendorIdsWithName`.
- plumAuth: `api.integratedVendors.<name>` (+ `rawPayload` if no top-level `data`) for webhooks.
- Schedulers: `/vendor/updateAccessToken`, `/vendor/sync_products`, `/vendor/merchandiseOrderTracking`.
- DB: `vendor` row (category_type, supports_currency_in_api, default_product_currency), `vendor_to_model`,
  `product_api_model_names`, `{model}_products` (+ `_product_to_denominations` for fixedSku).
- karma: `{CONST}_VENDOR_ID` define in every env's real `config.php`, listing page, `getRoutes`, header menu,
  User Group permission; fixedSku adds `FIXED_SKU_VENDORS` and the product-form SKU tab.
- karma_reports balance module only if a balance endpoint exists.

## 5. Platform limits
No outbound cancel. RETURNED (10) emails but does not refund, and it is not terminal for polling
(the loop only skips 3 and 5), so returned orders are polled forever. Async failure before confirmation has
no base path. Signed webhooks, non-JSON webhooks and non-AES encryption need a base change. One bad
order aborts a vendor's polling loop. plumAuth accepts webhooks even if VI fails downstream.
Suspected base bug (merch-sensei): `order.order_Product_Id` casing at MC ~:1040 may re-send status
emails on every poll. Polling-only vendors are most exposed, so verify it before go-live.
Status emails for Plum Pro (store 4) clients need `allowMerchandiseEmailClientIds`. Dpanda caveat: its
refetch reads only `data.insert_id`; use `data.insert_id ?? data.externalOrderId`.

## 6. Debug signals (for the vendor runbook)
| Symptom | Signal |
|---|---|
| Order never sent | id missing from OPMS `integratedVendors`; `Error while procuring voucher from vendor integration ms` |
| VI 400 on procure | OPMS hashKey/hashSalt ≠ VI voucherProcure |
| Product lookup | OPM00001 (status/model), OPM00002 (api_product_name / sku amount), OPM00003 (sku not in vendor table) |
| Vendor row | OPM00075 no `vendor` row; OPM00073/74/76/77 currency |
| Duplicate guard | OPM00063 |
| Response rejected | `formatOrderResponse` returned no `code` |
| Status stuck | `<name>: unmapped webhook status`; `No order ids found for releasing vouchers` (addedBy / api_order_id mismatch) |
| Polling | `Error while Merchandise order tracking`; ORDER_FAILED crashes the loop; field must be `orders_status`; id in `merchandiseOrderTrackingVendorIds` |
| Tracking | `No courier tracking found`; stale cache without `fetchTrackingDetailsFromVendor` throws |
| Sync | `received N products` vs `Formatted N products`; OPM00014 empty list; OPM00055 no products with this model; OPM00015 no token row |

Useful SQL: `merchandise_vendor_order_details` (api_order_id, insert_id, status), `egift_voucher_details`
(api_order_id, added_by), `courier_tracking`, `order_history`, `tokens` (never select `info`).
Raw vendor I/O: Mongo `vendor_call_logs.calls` (placeOrder, refetch, orderStatus only).
