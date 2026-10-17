# Printstop: debug runbook (read-only)

Never print credentials, tokens or recipient PII. Collect first: vendorId, order_id,
order_product_id, api_order_id (= Printstop `orders_id`), environment, time window.

## Wiring sanity
- VI `vendorClassIdMapping."Printstop"` = vendorId (else `Unknown vendor ID`).
- `config.json.vendorConfigs["<vendorId>"]` exists after `merge-configs`; `merchandiseVendor: true`.
- OPMS `integratedVendors` has the id as a **string**.
- vendorId in `merchandiseOrderTrackingVendorIds` (polling).
- `tokens` row exists for the vendor (`SELECT vendor_id, token_type, date_modified FROM tokens WHERE vendor_id = :vid`, never `info`).

## Symptoms
| Symptom | Likely cause | Check |
|---|---|---|
| Every call 401 | token expired / scheduler not running / wrong user-name | `tokens.date_modified`; re-seed with `/vendor/updateAccessToken`; OPM00015 if no row |
| 401 only on business calls | missing `client-id`/`client-secret` headers (needed besides Bearer) | `getReqHeaders`; Mongo `vendor_call_logs` (headers redacted) |
| Order fails with 409 | duplicate for this user (one-order-per-user store) | response `orders[]`. **Do not auto-link** to that order unless the reference matches (TECH_SPEC §6.1) |
| Order fails with 400 | missing required field (last_name, company_name, address) or bad product/size | request body in `vendor_call_logs` (apiType placeOrder) |
| Order placed but "no code" error | `formatOrderResponse` saw no `orders_id` (e.g. `success:"true"` without id) | raw response in Mongo |
| Timeout on place order | order may exist at Printstop, and we cannot look it up by reference | ask Printstop by reference_number / email; manual reconcile; never blind-retry |
| Status stuck at 1 | unmapped `orders_status` value | log `Printstop: unmapped webhook status`; add the lowercase key to `webhookConfigs.orderStatus` |
| Polling stops for all Printstop orders | one bad response aborts the loop; or the id is missing from `merchandiseOrderTrackingVendorIds` | `Error while Merchandise order tracking` / Teams card |
| No tracking shown | not dispatched yet (fields blank until dispatch) or formatter mapping | order_status response: `tracking_number`, `tracking_url`, `shipping_company` |
| Products all disabled after sync | partial catalogue fetch (details call failed silently) | `received N products` vs `Formatted N products`; the formatter must throw |
| Product shows no image | `{cdnurl}` not replaced | formatProductResponse |

## SQL
```sql
SELECT id, order_id, order_product_id, api_order_id, insert_id, status, date_updated
  FROM merchandise_vendor_order_details WHERE vendor_id = :vid AND (order_id = :oid OR api_order_id = :api);
SELECT egift_voucher_detail_id, order_id, api_order_id, added_by, status FROM egift_voucher_details WHERE api_order_id = :api;  -- added_by = 'Printstop API'
SELECT * FROM courier_tracking WHERE order_id = :oid;
SELECT comment, date_added FROM order_history WHERE order_id = :oid ORDER BY order_history_id DESC;
```

## Output
```
DIAGNOSIS: <one line>
EVIDENCE: <log line / SQL row / file:line>
LAYER: OPMS config | VI config | VI Printstop class | VI base (needs change) | DB seed | karma | Printstop side
FIX: <file + change>, or "ask Printstop: <question>"
```
