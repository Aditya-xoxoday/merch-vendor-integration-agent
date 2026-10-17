# {Vendor}: technical spec

Source: {doc, date}. Contract per `references/connector_reference.md`. **Code wins over this file.**

> **Check first:** does a connector already exist? `git grep -in {vendor}` in vendor-integrations,
> karma and order-process-ms. If yes, this spec is a diff against it.

## 1. Feasibility
```
AUTH            ✅/⚠️/❌ {type} → {static header / tokens table via updateAccessToken}; TTL {..}
ORDER           ✅/⚠️/❌ {path} → {id field}; sync/async → iswebhookConfiration {true/false}
IDEMPOTENCY     ✅/⚠️/❌ {reference field; duplicate behaviour; lookup by reference?}
ADDRESS         ✅/⚠️/❌ {shipping_* mapping; constants; country/state/phone formats}
STATUS MAP      ✅/⚠️/❌ {n} statuses → six targets
WEBHOOK         ✅/⚠️/❌/➖ {JSON? data key? signed? encrypted? our id carried?}
POLLING         ✅/⚠️/❌/➖ {endpoint; status field = orders_status? (else override)}
PRE-CONFIRM FAIL ✅/⚠️ {can an accepted order fail before confirm?}
TRACKING        ✅/⚠️/❌ {fields}
CANCEL/RETURNS  ⚠️ {outbound cancel unsupported; returns process}
CATALOG         ✅/⚠️/❌ {paging; sku format; brand; stock; fails loudly}
BALANCE         ✅/➖ {karma_reports module or none}
SANDBOX RUN     {n}/{n} requests · {x}/{y} assertions
COMPLEXITY      Low / Medium / High ({why})
RISKS           {list}
```

## 2. Endpoints
| Op | Method + path | Headers | Body | Success | Errors |
|---|---|---|---|---|---|
Quirks: {...}

## 3. Class plan: `src/vendors/integratedVendors/{ClassName}.ts`
| Method | Implementation for this vendor |
|---|---|
| fetchAccessToken / getReqHeaders / getPlaceOrderReqOptions / formatOrderResponse / getVoucherValidity / errorHandler / getRefetchOrderReqOptions / formatWebhookOrderStatusResponse / fetchTrackingDetailsFromVendor / getVendorProducts / formatProductResponse / formatWebhookProductResponse | {exact fields} |

## 4. Order body mapping
```jsonc
{ /* vendor body, each field annotated with the OPMS source field or constant */ }
```

## 5. Config and registration
vendorConfigs ({link to vendor_config.draft.json}), baseConfigs (vendorClassIdMapping, tracking ids,
redactHeaders), OPMS, plumAuth, schedulers, DB, karma, karma_reports.

## 6. Risks (with mitigation)
### 6.1 {risk} ({severity})

## 7. Open questions for the vendor (blocking first)

## 8. Done means
Sandbox {n}/{n}; unit tests green; `npm run merge-configs && npx tsc && npm run lint && npx jest tests/vendors/{vendor}`; staging smoke 1 → 2 → 3.
