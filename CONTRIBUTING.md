# Contributing

## Adding or changing a test case
1. Edit `.claude/skills/merch-vendor-review/references/test_cases.json`. Word the test so that
   **Yes = compatible with Plum**, give the `pass` criteria, and say which part of the platform
   consumes it (`platform`).
2. Use P0 only if missing it makes the integration impossible or unsafe. Gate tests must be P0.
3. Set `risk: true` only if a No/Open needs an engineering (base class / routing) change.
4. Regenerate the catalogue: `python3 tools/gen_test_catalog.py`.
5. Run `pytest -q tests`.
6. Add a line to `CHANGELOG.md`.

## Changing platform facts
`references/platform_contract.md` mirrors merch-sensei and the vendor-integrations code. When
the code changes, update the contract and the affected tests in the same PR.

## Lessons from real reviews
Every vendor review that exposes something the tests missed must add a test. That is how
DOC-01 and SEC-07 came from JustLounge.
