# Security

Vendor documents sometimes contain real credentials. This repo keeps them off GitHub.

- **Vendor docs and review outputs stay out of git.** Work in `reviews/`, which is gitignored.
  `examples/` holds only reviewed, safe samples.
- **Never copy a secret** into answers, reports, workbooks, emails, tickets, commits or chat.
  `scan_secrets.py` prints only the first 4 characters.
- **Never call production.** Sandbox only, with credentials in a Postman environment file outside the repo.
- **CI guard:** `tests/test_examples.py::test_repo_has_no_secrets` scans every text file.
- **If a secret reaches git:** treat it as leaked, ask the vendor to rotate it, and remove it from
  history (deleting the file is not enough).
