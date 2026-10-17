# Xoxoday Merchandise API — grounding reference

Source: developers.xoxoday.com (Rewards API, Merchandise section). Use this as ground truth
for what a *reference* Xoxoday-style integration looks like, so a vendor's own API can be
compared against a known-good pattern rather than judged in a vacuum.

## The 7-endpoint pattern

Every Xoxoday reward category (Gift Card, Lounge, Airmiles, Charity, Merchandise, Mobile Top-Up)
follows the same 7-endpoint shape:

- Get Filter API
- Get Merchandise API
- Get Balance API
- Place Order API
- Get Order Details API
- Get Order History API
- Get Payment Reports API

Authentication is OAuth2/Bearer token based, with a token validate and refresh step.
Orders use a `poNumber`-style client-supplied reference for idempotency and duplicate protection.
Realtime orders are expected to respond within ~120 seconds; anything slower should use webhooks.

## What "good" looks like (from the Xoxoday Place Order API contract)

- A client-supplied unique reference (`poNumber`) is required per order, specifically to avoid
  duplicate orders on retry.
- The order response separates order total, discount, and final amount charged.
- Voucher/asset delivery type is explicit (`code`, `codePin`, `url`, `urlPin` for gift cards).
- Per-product flags exist for special handling, e.g. `isPhoneNumberMandatory`, `orderQuantityLimit`.
- On a 5xx response, the documented recovery path is to call Get Order Details with the same
  reference before deciding whether to retry — never blind-retry a Place Order call.
- A dedicated Payment Report endpoint exists purely for reconciliation, separate from order status.

## Category-specific asset/output

For Merchandise, the thing that must come back to us (not just to the end recipient) is the
**shipment tracking reference** — this is the single most important capability check for this category,
because without it Plum cannot deliver, track, or reconcile the reward ourselves.

## Using this reference

When reviewing a real vendor's documentation, compare their actual endpoints and fields against
this pattern. Where the vendor matches or exceeds it, mark "Yes" with evidence. Where the vendor's
docs are silent, mark "Not available" — never assume the vendor works the same way just because
Xoxoday does. Where the vendor is confirmed to lack something Xoxoday has, mark "No" and flag it
as a gap with a suggested mitigation.
