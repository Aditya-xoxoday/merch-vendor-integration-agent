# Security

Vendor documents often contain live credentials (the JustLounge PDF did). This repo is built so
that they never leave the reviewer's machine.

- **Never commit vendor docs or outputs.** Everything lives in `reviews/`, which is gitignored.
  `examples/` holds only redacted, reviewed samples.
- **Never reproduce a secret.** Not in answers.json, reports, workbooks, emails, tickets, commits
  or chat. `scan_secrets.py` prints only the first 4 characters.
- **Never call production.** Live tests run only against a vendor staging/sandbox, with staging
  credentials kept in a Postman environment file outside the repo.
- **CI guard:** `tests/test_examples.py::test_repo_has_no_secrets` scans every tracked text file.
- **If a secret reaches git:** treat it as compromised. Ask the vendor to rotate it, then remove
  it from history. Removing the commit alone is not enough.
