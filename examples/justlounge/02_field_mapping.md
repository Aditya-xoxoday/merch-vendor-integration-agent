# JustLounge: field mapping

## Product (catalogue) -> Plum product columns

| Plum column | Vendor field (visible in screenshot) | Mapping |
|---|---|---|
| sku | `sku` (e.g. FR25846371H) | Direct |
| name | `name` | Direct |
| denominations / price | `price` (910) | Direct, but **currency unknown** (PRC-02) and buy vs retail price unknown (PRC-01) |
| currency | none | **Missing** |
| status | `status` (1) | Transform: meaning of 1/2 not documented (DOC-03). Magento convention suggests 1 = enabled; confirm with vendor |
| image | not visible (likely inside `custom_attributes` or `media_gallery_entries`, truncated) | **Unknown** (CAT-16) |
| description | not visible | **Unknown** |
| brand | not visible | **Unknown**. Required by the karma listing |
| categories | filter by `category_id` exists; per-item categories not visible | **Unknown** |
| country | none | **Missing** |
| variant link | `type_id` = simple; configurable parents not described | **Unknown** (CAT-05) |
| stock | none visible | **Missing** (CAT-06) |

## Order request -> Plum shipping fields
No order API is documented, so no mapping is possible. Every `shipping_*` field is **unmapped**.
