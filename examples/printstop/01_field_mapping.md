# Printstop / Mandaala: field mapping

## Order: our fields -> Printstop
| Our field | Printstop field | How |
|---|---|---|
| shipping_firstname | profile.first_name | Direct |
| shipping_lastname | profile.last_name (required) | Direct; use first name if empty |
| email | profile.email | Direct |
| shipping_contact_no / recipientMobileNumber | profile.mobile_number | Direct (format not stated) |
| (fixed value) | profile.company_name (required) | Constant, e.g. our company name |
| (fixed value) | profile.corporate_id | Constant from Printstop |
| our order reference | profile.reference_number | Direct (optional on their side) |
| shipping_address_1 | shipping.address_line_1 | Direct |
| shipping_address_2 | shipping.address_line_2 | Direct |
| shipping_city | shipping.city | Direct |
| shipping_zone | shipping.state | State name |
| shipping_postcode | shipping.pincode | Direct |
| shipping_country | shipping.country | Convert to their code (99 = India; others not listed) |
| product sku | product.product_id (+ size_id) | sku should carry both, e.g. `8093_14513` |
| (personalisation) | template.* | Only for personalised products |
| billing | billing object or corporate_billing_id | Constant location code, or copy shipping |

## Product: Printstop -> our product fields
| Our field | Printstop field | How |
|---|---|---|
| sku | product_id + size_id | Combine |
| name | product_name | Direct |
| image | product_image / product_images[].image_url | Replace `{cdnurl}` (base not documented) |
| description | product_long_des / product_short_des | Direct (HTML) |
| category | category_id (+ category_listing) | Lookup |
| status | visible ("Active") | Active = 1 |
| price | not returned (only a range in text) | **Missing** |
| currency | not returned ("Rs." in text) | **Missing** (assume INR only after confirming) |
| brand | not returned | **Missing** |
| stock | not returned | **Missing** |

## Status mapping (so far)
| Printstop status | Ours |
|---|---|
| In Production (id 10) | CONFIRMED |
| (rest of the list not documented) | ask vendor |
