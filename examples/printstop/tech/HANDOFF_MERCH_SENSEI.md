# Printstop: merch-sensei onboarding pre-fill

Paste into `/merch-sensei` (ONBOARD) after `start`. UNKNOWN items list the check that closes them.
Detail is in `TECH_SPEC.md`; config draft in `vendor_config.draft.json`; Postman collection in
`Printstop.postman_collection.json`.

> First run `git grep -in printstop` in vendor-integrations, karma and order-process-ms. karma
> already defines `PRINTSTPMERCHANDISE_VENDOR_ID`. If a connector exists, treat this as a change
> to it.

## Batch 1/7: Identity
1. Class name `Printstop`; model `printstop_merchandise` (confirm against the existing karma/product model).
2. Vendor id per env: UNKNOWN (reuse `PRINTSTPMERCHANDISE_VENDOR_ID` values). Check the central `vendor` and `vendor_to_model` rows exist.
3. Countries/currencies: India only (country code 99); INR assumed from "Rs." text. UNKNOWN for others (ENV-05, PRC-02).
4. Base URLs: staging `https://www.psstaging.in`; production UNKNOWN ("shared at go-live").
5. `fixedSku`: no price in the API, so amounts are entered per sku in karma (Variant B).

## Batch 2/7: Authentication
1. JWT via `GET /services/api.php?method=generate_token&corporate_id=…`, headers `client-secret`, `client-id`, `user-name`. Token in `access_token`. TTL UNKNOWN (AUTH-02).
2. Custom headers on every call: `client-secret`, `client-id` (plus `user-name` on the token call), all into `vendorCallLogger.mongo.redactHeaders`.
   Credentials go under **one key** (`credentials.printstop.{clientId, clientSecret, userName, corporateId, companyName, corporateBillingId, orderEmail}`), because updateAccessToken calls `fetchAccessToken` once per key. tokenType `printstop`.
3. Expired token: 401.

## Batch 3/7: Order placement and shipping
1. `POST /services/api.php?method=order`; body `profile`, `product`, `shipping` (or `corporate_shipping_id`), `corporate_billing_id` or `billing`; `template` for personalised products.
2. Address: address_line_1/2, city, state (name), pincode (string), country (numeric, 99 = India). Max lengths and phone format UNKNOWN (ORD-06, ORD-07).
   **The shipping block has no name or phone.** Recipient name/phone go in `profile`. profile.email = our constant `orderEmail` (TECH_SPEC §5.2 Model A), pending Q3.
3. Vendor order id: `orders_id`.
4. Async: returns `orders_id`, then statuses via Track Order (In Production …) → `iswebhookConfiration: true`.
5. Idempotency: `reference_number` (optional, not echoed, not searchable). Duplicate → HTTP 409 `{orders:[ids]}`, keyed on the **user**. Never auto-link via callVendorRefetch (false match, TECH_SPEC §11.2); a timeout goes to manual review (§11.1).
6. Errors: 400, 401, 409, 500; shape `{success:false, status, message, orders?}`; `success` is the string "true" on success.
7. Pre-confirmation failure: UNKNOWN (ORD-13).

## Batch 4/7: Status tracking
1. Polling only (no webhooks).
2. n/a (no webhooks).
3. Status values: only `In Production` (id 10) documented. Full list UNKNOWN (STS-01). Map so far: `"in production": "CONFIRMED"`. RETURNED is not terminal for polling; verify the suspected email re-send bug (MC ~:1040) because this vendor is polling-only.
4. Polling: `POST /services/api.php?method=order_status&orders_id=<api_order_id>`; status field `orders_status` (matches the base `res["orders_status"]`); tracking `tracking_number`, `tracking_url`, `shipping_company`; dates `orders_due_date`, `actual_delivery_date` (format "17 Jul, 2024").

## Batch 5/7: Catalog
1. `POST ?method=product_listing` → `{total, data:[{product_id, name, status}]}`; no paging documented (CAT-02).
2. Fields (details): product_name, product_long_des, product_image (`{cdnurl}` prefix, base UNKNOWN), category_id, visible ("Active"). No price, currency or brand.
3. Variants: `product_size[]` (`size_id`). Order needs `product_id` + `size_id`, so sku = `${product_id}_${size_id}`.
4. Stock: none documented (CAT-06).
5. Product webhooks: none, so `formatWebhookProductResponse` is a no-op.

## Batch 6/7: Lifecycle
1. Outbound cancel: none (platform has none anyway).
2. Returns: not documented (RTN-03). RETURNED gives no refund on our side.
3. Per-order tracking URL: yes (`tracking_url`).

## Batch 7/7: Edge cases
1. Rate limits: UNKNOWN (ERR-04).
2. Webhook retries/duplicates: n/a.
3. Staging quirks: single path with `?method=`; `product_details` selector undocumented; `success` string vs boolean; personalised templates.
4. Prepaid balance endpoint: none, so no karma_reports module.
