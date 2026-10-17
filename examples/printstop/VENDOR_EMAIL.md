Subject: Printstop API integration: a few questions

Hi Printstop team,

Thank you for the API reference. We reviewed it for integration with our rewards platform. Ordering, tracking and the catalogue look good, and we have a few questions before we start.

Could you share the full list of order statuses (orders_status_id and orders_status) with their meaning? We only see "In Production" in the document, and we need the rest, including cancelled, dispatched, delivered and returned.

For safe retries, will reference_number be unique for every store, so that a repeated reference is rejected with the existing order ID? Can Track Order also look up an order by reference_number? This lets us confirm an order after a timeout without placing it twice.

On ordering, please confirm whether one order is always one item or whether there is a quantity field. Please also confirm how Product Details selects a product, since the document shows no product ID parameter.

On the catalogue, could you share the exact price per product and size, the currency, and whether GST and shipping are included? Please also tell us how to page through the product list, how stock is shown, and the base URL for the {cdnurl} image placeholder.

It would also help to know your returns and replacement process, whether a settlement or invoice report is available, your supported countries, and any rate limits.

Finally, could you share sandbox credentials, and confirm that sandbox orders are not shipped or billed?

Regards,
Adi
