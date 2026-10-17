# Draft code (not compiled here)

`Printstop.ts` and `Printstop.test.ts` are **drafts** written from the API doc and the class contract
in `references/connector_reference.md`. They have not been compiled against vendor-integrations.
Before use:
1. Do the TECH_SPEC §1 check (a Printstop connector may already exist).
2. Open `vendorBaseClass.ts`, `vendorMerchandiseClass.ts`, `interfaces/vendorBase.ts`,
   `interfaces/vendorMerchandise.ts` and `Dpanda.ts` on the target branch. Fix import paths, method
   signatures and helper names marked `VERIFY`.
3. Copy to `src/vendors/integratedVendors/Printstop.ts` and `tests/vendors/printstop.test.ts`, then run
   `npx tsc && npm run lint && npx jest tests/vendors/printstop`.
