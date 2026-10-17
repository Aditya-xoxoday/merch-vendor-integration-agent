# Plum merchandise platform contract (what a vendor API must feed)

This is distilled from merch-sensei (vendor-integrations `canvas`, Oct 2026). It explains *why*
each test case exists. **Code wins over this file.** Re-read the code on the target branch before building.

## Order flow

```
OPMS __autoProcureVendorProducts
  -> VI POST /vendor/procure_voucher            (only if vendor id is in integratedVendors, STRING id)
VI procureVoucherFromVendor
  -> vendor Place Order                          ORD-01..ORD-05, IDM-01
  -> formatOrderResponse must return a truthy code = {model}_vendor_{apiOrderId}   ORD-02
  -> merchandise_vendor_order_details row        (merchandiseVendor = true)
  -> sync vendor: egift row now / async vendor: egift row on confirmed/shipped     ORD-04
Vendor webhook -> plumAuth /webhook/orderUpdate/<name> -> VI webhookOrderStatusUpdate   WHK-*
  -> status lowercased -> webhookConfigs.orderStatus -> one of 6 delivery statuses      STS-01/02
  -> courier_tracking, order_product status, email; CANCELED -> refund queue            TRK-01, RTN-01
Polling: /vendor/merchandiseOrderTracking reads res["orders_status"]                    POL-01/02
Product sync: /vendor/sync_products -> TRUNCATE + insert; vanished SKUs disabled         CAT-02, CAT-09
```

## Hard platform facts (each one appears in at least one test)

| Fact | Consequence | Tests |
|---|---|---|
| Only 6 delivery statuses: PENDING, CONFIRMED, SHIPPED, DELIVERED, CANCELED, RETURNED | Every vendor status must map. ORDER_FAILED crashes polling | STS-01, STS-02 |
| The vendor order id is mandatory in the order response | Without it the order is treated as failed | ORD-02 |
| Our reference (externalOrderId = voucher_insert_id) is used to find orders | The vendor must accept it and echo it back | IDM-01, WHK-03, REC-02 |
| "Already exists" errors are resolved by refetch | A lookup by our reference is needed | IDM-02, IDM-03 |
| Async failure before confirmation has no base-class path | Needs a change on our side before building | ORD-13 |
| plumAuth accepts any webhook, even if VI fails downstream | The vendor will not retry, so we need refetch/poll as a backstop | WHK-08, POL-01 |
| Signed webhooks are unsupported | Needs a change on our side | WHK-05 |
| Non-JSON webhooks need a new route | Needs a change on our side | WHK-04 |
| Only AES (null IV, base64) decryption is supported | Anything else needs a change on our side | WHK-06 |
| Polling base reads `orders_status` | A different field needs an override | POL-02 |
| Catalogue sync truncates the table first | A silent empty page disables everything | CAT-02, CAT-09 |
| sku must be reversible into the order ids | Variants need deterministic SKUs | CAT-03, CAT-05 |
| `brand` column is needed by the karma listing | The catalogue must expose brand | CAT-04 |
| There is no outbound cancel | A cancel API is nice-to-have only | RTN-02 |
| RETURNED sets status 10 and emails, but does not refund | Returns must be handled by ops/finance | RTN-03, RTN-04 |
| Tracking needs trackingId or link | Otherwise "No courier tracking found" | TRK-01, TRK-02, WHK-11 |
| Custom auth headers must be redacted in Mongo logs | Header names are needed up front | AUTH-01 |
| Balance endpoint means a karma_reports module | Optional | BAL-01 |
| Missing central `vendor` row gives OPM00075 | Countries and currencies are needed | ENV-05, PRC-02 |

## Shipping fields OPMS sends
`shipping_firstname`, `shipping_lastname`, `shipping_address_1`, `shipping_address_2`,
`shipping_city`, `shipping_zone`, `shipping_country`, `shipping_country_id`, `shipping_postcode`,
`shipping_contact_no`, `recipientMobileNumber`. The vendor's address schema must be fillable from
these fields (ORD-05).
