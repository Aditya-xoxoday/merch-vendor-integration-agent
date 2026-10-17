# JustLounge: document inventory

| Source | Detail |
|---|---|
| File | Justlounge_Magento_2_Catalog_API_information.pdf |
| Pages | 2 |
| Metadata | Title "Justlounge.com Magento 2 Catalog Data API"; producer Google Docs renderer; no date, version or author |
| Link annotations | 3, all pointing to the two product URLs below |
| Embedded images | 2 Postman screenshots (one per page) |
| Secrets | 4 live OAuth values in the text and both screenshots (consumer key, consumer secret, access token, token secret). Redacted everywhere. |

## Endpoints found

| # | Method | Path | Purpose | Source |
|---|---|---|---|---|
| 1 | GET | /rest/V1/products?searchCriteria[filter_groups][0][filters][0][field]=category_id&...[value]=23 | Products by category (23 is an example category id) | p1 text + screenshot 1 |
| 2 | GET | /rest/V1/products?searchCriteria[pageSize]=10 | All products, page size 10 | p2 text + screenshot 2 |

Host: `https://justlounge.com`, which is the live storefront domain. No sandbox host is given.
Auth: OAuth 1.0, signature HMAC-SHA1, with four values (consumer key/secret, access token/secret).

## Images

| Image | Shows |
|---|---|
| p1 screenshot | Postman request 1 with the auth tab filled in (all 4 secrets visible), "Add authorization data to: Request Body / Request URL", 200 OK, 766 ms, 37.32 KB. Response is visible to line 15: items[0] id 12, sku, name "Nuvola Shoulder Bag", attribute_set_id 4, price 910, status 1, visibility 4, type_id simple, created_at, updated_at, extension_attributes.website_ids (cut off) |
| p2 screenshot | Postman request 2, same auth (secrets visible), 200 OK, same first item. Tabs also visible: "POST Get Token Based on OA..." (an undocumented token call) |

## Undocumented hints
- A Postman "Get Token" POST request exists in the vendor's workspace but is not in the doc.
- The Postman workspace is named "RESTful API Basics #blueprint". The collection was not shared.
- Platform fingerprint: **Magento 2** (`/rest/V1/`, `searchCriteria`, `extension_attributes`).
