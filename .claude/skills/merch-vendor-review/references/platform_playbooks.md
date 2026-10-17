# E-commerce platform playbooks: for QUESTIONS only

Many merchandise vendors run a standard e-commerce platform and share a slice of its API. Use this
file to ask **sharper vendor questions**. **Never use it to answer a test.** A capability the
platform *can* have is not a capability this vendor *has exposed to us*.

## Magento 2 / Adobe Commerce (`/rest/V1/`)
Fingerprint: `/rest/V1/products?searchCriteria[...]`, OAuth 1.0a integration tokens, `entity_id`,
`increment_id`, `extension_attributes`, `custom_attributes`.

What to ask the vendor to enable or confirm:
- **Ordering as B2B partner:** will they create orders for us through the REST API (for example
  a cart/quote flow then place order, or a custom partner endpoint)? Which payment method is used
  for prepaid partner orders? Can our reference be stored on the order and returned?
- **Order status:** their order `status` / `state` values (for example pending, processing,
  complete, canceled, closed, holded) and any custom statuses. Ask for the full list.
- **Shipments and tracking:** will shipment tracks (carrier code, title, track number) be
  exposed to us through the API, and is the timing of shipment creation stated?
- **Webhooks:** core Magento has none. Ask whether they have an extension or middleware that
  pushes status. Otherwise we poll.
- **Catalogue:** `searchCriteria[currentPage]` plus `total_count` for paging. The
  `custom_attributes` codes for brand, image, description and categories (CAT-16). Stock via
  `extension_attributes.stock_item` or MSI salable qty. Configurable vs simple products for
  variants. The meaning of `status` (1 enabled / 2 disabled) and `visibility` (1 to 4). The
  currency of `price`.
- **Credentials:** an integration user scoped to the needed resources only (SEC-08), a separate
  staging store, and tokens sent over a secure channel (SEC-07). Do OAuth params go in the header?

## Shopify (`/admin/api/<version>/` or Storefront GraphQL)
Fingerprint: `X-Shopify-Access-Token`, `/admin/api/2024-xx/`, GraphQL `gid://shopify/...`.
Ask about:
- draft orders vs orders for partner placement
- fulfillment orders and fulfillments with `tracking_info`
- webhook topics (`orders/updated`, `fulfillments/create`) and the HMAC
  (`X-Shopify-Hmac-Sha256`: signed, so WHK-05 risk)
- API version deprecation (quarterly, so SUP-03)
- leaky-bucket rate limits

## WooCommerce (`/wp-json/wc/v3/`)
Fingerprint: consumer key/secret (`ck_`, `cs_`), Basic auth over HTTPS or OAuth 1.0a over HTTP.
Ask about:
- order statuses (pending, processing, on-hold, completed, cancelled, refunded, failed, plus
  custom ones)
- shipment tracking plugins (the core has no tracking)
- webhooks (signed with `X-WC-Webhook-Signature`, so WHK-05 risk)
- `meta_data` for our reference
- staging site availability

## Custom / proprietary
No assumptions. Every section of the test cases is a question.
