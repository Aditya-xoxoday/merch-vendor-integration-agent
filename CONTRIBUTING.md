# Contributing

## Adding or changing a check
1. Edit `.claude/skills/merch-vendor-review/references/test_cases.json`. Word the check so that
   **Yes = works for us**, fill "pass" (what counts as yes), and add a short tech note.
2. Set `need`:
   - **Must-have** only if we truly cannot integrate without it (then add it to a `must_haves` group)
   - **Important** if it matters but can be handled another way
   - **Nice-to-have** otherwise
3. Set `risk: true` only if a No/Open needs a change on our side before building.
4. Run `python3 tools/gen_test_catalog.py`, then `pytest -q tests`.
5. Add a line to `CHANGELOG.md`.

## When our code changes
Update `references/platform_contract.md` and the affected checks together.

## Learn from every review
If a review finds something the checks missed, add a check.
