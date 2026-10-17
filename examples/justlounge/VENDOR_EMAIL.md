Subject: JustLounge API integration: information needed

Hi JustLounge team,

Thank you for sharing the Magento 2 catalogue API details. We reviewed them for integration with our rewards platform and need a few more things before we can proceed.

First, on security: the document includes live API credentials for your production store, both in the text and in the screenshots. Please rotate these credentials as soon as possible. When you share new ones, please send sandbox and production credentials separately through a secure channel. Please also scope them to only the resources we need.

The current document covers product listing only. To fulfil reward orders automatically, we need APIs for placing an order with our own order reference, checking order status by that reference, and getting shipment details (courier name and tracking number or link) once an order is dispatched. Please share the full list of order statuses and their meanings. Please also let us know whether you can send status updates to a URL we provide.

For the catalogue, could you confirm how to page through all products and how we know we have reached the last page? Please also confirm the currency of the price field, whether that price is what we will be charged (including tax and shipping), how stock is shown, which attributes hold the brand, image and description, and what the status and visibility values mean.

We also need your serviceable regions or a pincode check, your returns and replacement process for damaged or undelivered items, and a statement or settlement report that includes our order reference for reconciliation.

Finally, could you provide a sandbox or staging store where test orders are not shipped or charged, the Postman collection you used, and a technical contact for the integration? Happy to set up a short call if that is easier.

Regards,
Adi
