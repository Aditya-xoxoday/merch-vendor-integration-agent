# Printstop / Mandaala: doc inventory

| Source | Detail |
|---|---|
| Page | https://deq64r0ss2hgl.cloudfront.net/images/printstop-api-docs.html |
| Title | Printstop/Mandaala API Reference (single HTML page, about 52 KB) |
| Images | 1 logo (printstop-mandaala.png), no screenshots |
| Secrets | None. Placeholders only ([Client Secret], [Client ID]); the sample token is cut off |
| Date / version | Not given |

## Environments
| Environment | Base URL |
|---|---|
| Sandbox | https://www.psstaging.in |
| Production | "TBD (shared at go-live)" |

Every call goes to `/services/api.php`, and the operation is chosen with `?method=`.

## Endpoints
| # | Method | method= | Purpose |
|---|---|---|---|
| 1 | GET | generate_token (+ corporate_id) | Get a JWT access token (headers: client-secret, client-id, user-name) |
| 2 | POST | order | Place an order; returns `orders_id`. Duplicate on one-order-per-user stores gives HTTP 409 with existing order IDs |
| 3 | POST | order_status (+ orders_id) | Status, due date, delivery date, tracking number, tracking URL, courier |
| 4 | POST | category_listing | Categories (with total) |
| 5 | POST | product_listing | Products: product_id, name, status (with total) |
| 6 | POST | product_details | Sizes, templates, images, GST/HSN, production days |
| 7 | POST | create_user (query params) | Create a store user |

Every business call sends `Authorization: Bearer <token>`, `client-id` and `client-secret`.

## Things noticed
- Product Details says "Body: None", but there is no product_id parameter. It is unclear how
  you choose which product to fetch.
- `success` is the string "true" on success and boolean `false` on error.
- Order body takes one `product` object with no quantity field.
- `reference_number` is optional and is not returned by Track Order.
- Personalised products need template fields (name, employee number, image) per order.
