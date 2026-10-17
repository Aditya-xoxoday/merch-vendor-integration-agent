# Printstop / Mandaala: merchandise API analysis

**Can we integrate?** Likely yes, after the vendor answers 2 points.
**Does the API work?** Not tested yet. A sandbox exists (psstaging.in); we need sandbox credentials.
**Must-haves:** 5 met, 2 open, 0 missing (of 7).

No credentials were found in the document.

## What the API does
A single endpoint (`/services/api.php?method=...`) with a sandbox and a production host (shared
at go-live). Login is a JWT token, plus client-id and client-secret headers on every call. You can
get a token, place an order, track it (with courier and tracking number), list categories and
products, get product details (sizes, images, GST, personalisation templates), and create store
users. Webhooks, returns, a settlement report and a balance API are not covered.

## Must-haves
| | Must-have | What we found |
|---|---|---|
| Met | Place an order and get an order ID back | `method=order` with documented fields; response returns `orders_id` |
| Met | Our address fields fit their order format | Name, email, mobile, address lines, city, state, pincode, country all map. company_name and corporate_id are fixed values; country needs their code (99 = India) |
| Met | Product ID from their catalogue is what the order takes | `product.product_id` comes from the Catalog API; `size_id` from Product Details |
| **Open** | Get the order status | `method=order_status` returns status and dates, and we can poll it. **But only one status value is documented** ("In Production", id 10), so we cannot map the rest yet |
| Met | Get courier and tracking number | `tracking_number`, `tracking_url` and `shipping_company` in Track Order |
| **Open** | Retry safely without duplicate orders | `reference_number` exists but is optional and is never returned. The duplicate 409 works only on "one order per user" stores. After a timeout we have no `orders_id`, so we cannot look the order up |
| Met | Secure login that works | JWT plus headers over HTTPS, with examples |

## What we need from the vendor
1. **The full list of order statuses** (`orders_status_id` and `orders_status`) with meanings,
   including cancelled, dispatched, delivered and returned.
2. **Safe retry:** will `reference_number` be unique and rejected on reuse (409 with the existing
   order ID) for every store? Can Track Order look an order up by `reference_number`?
3. Quantity: is one order always one item, or is there a quantity field?
4. The exact price per product and size (only a range is shown), currency, and whether GST and
   shipping are included.
5. How Product Details picks a product (the doc says "Body: None"), and the base for `{cdnurl}` in image URLs.
6. Paging for the product list, and stock or availability.
7. Sandbox credentials. Are sandbox orders never shipped or billed?

## Other gaps (do not block)
- No webhooks (polling works instead), no bulk status call, and no polling rate limit stated.
- No returns or replacement process, no return-to-origin handling.
- No settlement report or invoice API (we will need one for monthly reconciliation).
- No balance API (fine; not needed).
- No pincode or serviceability check, no rate limits, no uptime or support contact.
- `success` is "true" (text) on success and `false` (boolean) on error.
- create_user sends email, phone and address in the URL.
- Only India (country code 99) is listed.

## Build notes
- Flow: place the order, then poll Track Order (no webhooks).
- Their status field is called `orders_status`. That is the field our polling already reads, so
  no override is needed.
- Our system already lists Printstop as a merchandise vendor (merch-sensei mentions a Printstop
  admin page). Check the existing connector before building a new one.
- Nothing needs a change on our side, as long as polling is used.
- What we can build now: login, catalogue sync (without price/stock), order placement, polling
  and tracking. Status mapping waits for the full status list.

## Next steps
| # | Step | Who | Closes |
|---|---|---|---|
| 1 | Send the vendor questions | Us | STS-01, IDM-01/02, ORD-09, PRC-01 |
| 2 | Share sandbox credentials | Printstop | sandbox tests |
| 3 | Run the 25 sandbox checks (`/merch-vendor-agent` LIVE mode) | Us | Does the API work? |
| 4 | Re-review the answers (DIFF mode) | Us | final decision |
| 5 | Hand off to merch-sensei | Us | build |

Appendix: REPORT.md, Printstop_Merchandise_Review.xlsx, 00_doc_inventory.md, 01_field_mapping.md.
