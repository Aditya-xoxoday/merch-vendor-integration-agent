# Merchandise Vendor Integration Agent

When someone shares a merchandise vendor's API doc (file or link) or asks whether a vendor can be
integrated, run the `/merch-vendor-agent` workflow in `.claude/commands/merch-vendor-agent.md`.

- The output is ONE workbook: `reviews/<vendor>/<Vendor>_Review.xlsx` (plus its `review.json`).
  Make extra files (full tech spec, Postman, draft code) only when asked.
- Only the 7 must-haves decide "can we integrate". A missing balance API never blocks.
- Never call production, never copy a secret, never guess an answer the docs don't give.
- `reviews/` is gitignored. Do not commit vendor docs or review outputs.
- Before changing scripts or checks: `pip install -r requirements-dev.txt && pytest -q tests`.
