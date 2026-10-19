# Merchandise Vendor Integration Agent

Share a merchandise vendor's API document with this agent (PDF, Word, Postman, OpenAPI/Swagger,
docs site or screenshots). You get back **two boxed reports in chat** (the decision and a merch-sensei style build feasibility) and **one Excel workbook**. Together they answer:

1. **Can we integrate?** Yes / Yes on paper / Likely yes / No, decided only by 7 must-haves.
2. **Does the API work?** Based on tests on the vendor's sandbox.

**No Place Order API means No. No balance API is fine.** Everything that is missing but not a
must-have is listed as a gap, with a question for the vendor.

This agent reviews vendors. [merch-sensei](https://github.com/abhishekkxoxo/merch-sensei) builds the
connector once the answer is yes.

## Quick start
```bash
git clone https://github.com/Aditya-xoxoday/merch-vendor-integration-agent.git
cd merch-vendor-integration-agent
pip install -r requirements-dev.txt
claude
```
Then in Claude Code:
```
/merch-vendor-agent
```
Share the vendor doc (file path or link). You get both boxes in chat, and the workbook in `reviews/<vendor>/`.

## What you see in chat: two boxes
Every review replies with **both**:
1. **🛒 Merch Vendor Review**: the decision, for everyone.
2. **🛠️ Build Feasibility (merch-sensei format)**: the build view, for developers.

Example (Printstop):
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🛒 Merch Vendor Review: Printstop / Mandaala
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
VERDICT         ⚠️ Likely yes, after the vendor answers a few points
                   2 must-haves only partly documented
API TEST        ⚠️ Not tested yet (no sandbox run)
SECURITY        ✅ No credentials in the document (placeholders only; the sample token is cut off).

MUST-HAVES (5/7 met · 2 open · 0 missing)
PLACE ORDER     ✅ POST method=order with documented fields returns orders_id.
ADDRESS         ✅ Name, email, mobile, address lines, city, state, pincode and country all map.
                   Recipient name and phone go in the profile (shipping has no name).
PRODUCT ID      ✅ product_id from the catalogue (plus size_id from product details) is what the
                   order takes.
ORDER STATUS    ⚠️ order_status returns status and tracking, and we can poll it. But only 1 status
                   value is documented (In Production), so the rest cannot be mapped yet.
TRACKING        ✅ tracking_number, tracking_url and shipping_company once dispatched.
SAFE RETRY      ⚠️ reference_number is optional, never returned and not searchable. The 409
                   duplicate works per user, not per reference. After a timeout we cannot check if
                   the order exists.
SECURE LOGIN    ✅ JWT token plus client-id and client-secret headers, HTTPS, with examples.

AREAS (checks answered Yes / applicable)
Documentation Quality              ❌ 0/4
Access & Authentication            ⚠️ 2/6
Environments & Onboarding          ⚠️ 1/6
Catalogue & Product Sync           ⚠️ 5/16
Pricing, Currency & Balance        ❌ 0/8
Order Placement & Address          ⚠️ 5/18
Idempotency & Duplicates           ❌ 0/5
Order Status & Lifecycle           ⚠️ 1/9
Webhooks                           ❌ 0/12
Polling                            ⚠️ 2/4
Shipment Tracking                  ⚠️ 3/6
Cancellation, Returns & Refunds    ❌ 0/7
Reconciliation & Settlement        ❌ 0/7
Errors, Rate Limits & Reliability  ⚠️ 3/8
Security, Data & Compliance        ⚠️ 3/8
Support & Versioning               ❌ 0/5
GAPS            Important 15/89 covered · Nice-to-have 2/27 (never block)

ASK THE VENDOR (top 5)
 1. [Must-have] Full list of order statuses (orders_status_id and orders_status) with meanings,
                including on hold, cancelled, dispatched, delivered and returned.
 2. [Must-have] Is reference_number unique per store, with a 409 returning the existing order on
                reuse? Can order_status look up an order by reference_number?
 3. [Important] How is our store set up: per-user order limit, approval step, or must each recipient
                exist as a user first? (Recipient name and phone go in the profile, which the
                duplicate rule checks.)
 4. [Important] Is one order always one item, or is there a quantity field?
 5. [Important] Exact price per product and size, currency, and whether GST and shipping are
                included.

NEXT STEPS
 1. Check whether a Printstop connector already exists (karma has PRINTSTPMERCHANDISE_VENDOR_ID)
    (Dev)
 2. Send the vendor questions (Us)
 3. Get sandbox credentials and run the sandbox checks (LIVE mode) (Printstop / Us)
 4. Re-review with the answers (DIFF mode), then hand off to merch-sensei (Us)

OUTPUT          examples/printstop/Printstop_Review.xlsx
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🛠️ Build Feasibility (merch-sensei format): Printstop
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
AUTH              ⚠️ JWT via GET generate_token → tokens table (credentials under one key
                     "printstop"). TTL not documented. Every call also needs client-id and client-
                     secret headers.
ORDER             ✅ POST method=order → orders_id. Async (In Production after) →
                     iswebhookConfiration true. code/apiOrderId/addedBy contract OK.
IDEMPOTENCY       ⚠️ reference_number optional, not echoed, not searchable. 409 is keyed on the
                     user, so never auto-link via callVendorRefetch.
ADDRESS           ✅ shipping_* fields map. Recipient name/phone go in profile (shipping has no
                     name). company_name, corporate_id constants. Country 99 = India only.
STATUS MAP        ⚠️ Only "in production" → CONFIRMED known. Full list needed.
WEBHOOK           ➖ None. Polling only; nothing to add in plumAuth.
POLLING           ✅ order_status returns top-level orders_status (the field the base reads). Add id
                     to merchandiseOrderTrackingVendorIds.
PRE-CONFIRM FAIL  ⚠️ Not documented whether an accepted order can be rejected (approval workflow
                     exists in create_user).
TRACKING          ✅ tracking_number, tracking_url, shipping_company, orders_due_date,
                     actual_delivery_date.
CANCEL/RETURNS    ⚠️ No cancel or returns API (outbound cancel unsupported on our side anyway).
CATALOG           ⚠️ product_listing (total, no paging) + product_details per product (selector
                     undocumented). No price, brand or stock. sku = {product_id}_{size_id}.
BALANCE           ➖ None. No karma_reports module needed.
SANDBOX RUN          0/25 sandbox checks run; 0 failed
COMPLEXITY           Medium-High: nested order body, token plus 2 static headers, one details call
                     per product, amounts entered by hand (fixedSku), recipient-as-profile, no safe
                     retry.

RISKS
 • Timeout or 5xx after the order was created: no lookup by reference, so manual reconcile.
 • 409 returns another reward's order for the same user: never link automatically.
 • Status list incomplete: unmapped statuses never finish, so polling continues forever.
 • Suspected base bug re-sends status emails on every poll (polling-only vendor).
 • Token lifetime unknown.

BUILD FILES (vendor-integrations, tracked)
 • src/vendors/integratedVendors/Printstop.ts                   [NEW, or DIFF if a connector exists]
 • src/vendors/vendorTemplates/printstopTypes.ts                [NEW, if needed]
 • src/configs/baseConfigs.json.sample                          [UPDATE mapping + tracking ids]
 • tests/vendors/printstop.*.test.ts + fixtures                 [NEW]
LOCAL / DEPLOY CONFIG (gitignored, never in a PR)
 • src/configs/vendorConfigs/Printstop.json, baseConfigs.json mappings (per env)
CHECKLIST (outside VI)
 • OPMS integratedVendors (string id), schedulers (token, sync, tracking)
 • DB: vendor, vendor_to_model, product_api_model_names, printstop_merchandise_products
 • karma admin page, menu, routes, permissions (check what already exists)

NOTES
 • Check first: karma already defines PRINTSTPMERCHANDISE_VENDOR_ID, so a connector may exist.
 • Status checks need no override: their field is orders_status, which our polling already reads.
 • No webhooks: nothing to add in plumAuth. No balance API: no karma_reports module.
 • Full developer spec: Printstop_TECH_SPEC.md.

HANDOFF              /merch-sensei ONBOARD: after the open must-haves are answered
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## The output file: one workbook, 4 tabs
| Tab | What's in it |
|---|---|
| **Summary** | The answer in big letters (can we integrate? does the API work?), the 7 must-haves (Yes / Partly / No), blockers, next steps. One page. |
| **Ask the vendor** | Numbered questions (must-haves first) and a ready email draft |
| **Tech** | Build feasibility (Ready / Check / Blocked), endpoints, field and status mapping, what can go wrong, assumptions, setup changes |
| **All checks** | Every check with its result and what we found, must-haves first, filterable |

See [examples/printstop/Printstop_Review.xlsx](examples/printstop/Printstop_Review.xlsx).

**Only when you ask:**
| Say | You get |
|---|---|
| "full tech spec" | One `<Vendor>_TECH_SPEC.md` for developers: diagrams, class plan, failure modes, test plan, merch-sensei handoff, debug runbook ([example](examples/printstop/Printstop_TECH_SPEC.md)) |
| "postman" / "config draft" / "draft code" | Build files for the sandbox run and the connector |
| "run live" (with sandbox credentials) | Sandbox results added to the same workbook |
| a new version of a doc | What changed, with the workbook updated |

## The 7 must-haves
| # | Must-have |
|---|---|
| 1 | Place an order and get an order ID back |
| 2 | Our address fields fit their order format |
| 3 | The product ID from their catalogue is what the order takes |
| 4 | Get the order status (status list, lookup, and webhook or polling) |
| 5 | Get courier and tracking number after dispatch |
| 6 | Retry safely without creating duplicate orders |
| 7 | Secure login that works |

How the decision is worked out: [docs/DECISION.md](docs/DECISION.md). All 130 checks: [docs/TEST_CATALOG.md](docs/TEST_CATALOG.md).

## Rules the agent follows
- Evidence or nothing: if the docs say nothing, the answer is "Not available". Nothing is guessed.
- Sandbox only. Production is never called.
- Secrets are never copied, and vendor docs and outputs stay out of git ([SECURITY.md](SECURITY.md)).

## Repository layout
```
.claude/commands/merch-vendor-agent.md   the agent
.claude/skills/merch-vendor-review/      the skill (also works when uploaded to claude.ai)
  references/                            checks, platform contract, reading guides, spec template
  scripts/                               build_review.py (the workbook), scan_secrets.py,
                                         lint_tech_spec.py, build_tech_pack.py
docs/                                    decision rules, architecture, gap analysis, check list
examples/printstop/                      review.json, the workbook, and an optional full tech spec
tests/                                   automated tests (run in CI)
reviews/                                 your reviews (gitignored)
```

## Use on claude.ai
Zip `.claude/skills/merch-vendor-review/` and upload it as a skill.

## Contributing
See [CONTRIBUTING.md](CONTRIBUTING.md). Run `pytest -q tests` before you push.
