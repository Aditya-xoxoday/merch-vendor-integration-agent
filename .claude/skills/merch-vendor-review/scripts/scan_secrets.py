#!/usr/bin/env python3
"""
Scan vendor documentation for embedded credentials (feeds test SEC-07).

Usage:
    python3 scan_secrets.py <file> [<file> ...]

Accepts .txt/.md/.json (Postman collections, OpenAPI) and .pdf (needs `pypdf`).
Prints findings with values REDACTED (first 4 chars only) and exits 1 if anything is found,
0 if clean. Never prints a full secret: the output is safe to paste into a report.

Screenshots inside PDFs are not OCR'd: the agent must still look at every image itself.
"""
import json
import re
import sys

LABELED = re.compile(
    r"(?i)\b(consumer[\s_-]*key|consumer[\s_-]*secret|access[\s_-]*token(?:[\s_-]*secret)?|token[\s_-]*secret|"
    r"client[\s_-]*secret|client[\s_-]*id|api[\s_-]*key|secret[\s_-]*key|password|passwd|bearer|"
    r"authorization|x-api-key|private[\s_-]*key)\b\s*[:=\"']+\s*\"?([A-Za-z0-9_\-\.\/+=]{12,})")
PATTERNS = {
    "AWS access key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "JWT": re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b"),
    "Basic auth header": re.compile(r"(?i)\bBasic\s+([A-Za-z0-9+/]{16,}={0,2})"),
    "Private key block": re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    "Credential in URL": re.compile(r"https?://[^\s/:@]+:([^\s/@]{6,})@"),
}
PLACEHOLDER = re.compile(r"(?i)^(x+|\*+|<.*>|\{\{.*\}\}|your|example|placeholder|changeme|test)")


def read_text(path):
    if path.lower().endswith(".pdf"):
        from pypdf import PdfReader  # optional dependency
        reader = PdfReader(path)
        # PDF text often has a newline between every word; collapse whitespace
        return re.sub(r"\s+", " ", " ".join(p.extract_text() or "" for p in reader.pages))
    with open(path, encoding="utf-8", errors="replace") as f:
        text = f.read()
    if path.lower().endswith(".json"):
        try:
            text += "\n" + json.dumps(json.loads(text), indent=0)  # flatten Postman auth arrays
        except ValueError:
            pass
    return text


def redact(value):
    return value[:4] + "*" * 8 + f" ({len(value)} chars)"


def scan(text):
    found = []
    for m in LABELED.finditer(text):
        value = m.group(2)
        if not PLACEHOLDER.match(value):
            found.append((m.group(1).strip(), redact(value)))
    for name, rx in PATTERNS.items():
        for m in rx.finditer(text):
            value = m.group(1) if rx.groups else m.group(0)
            found.append((name, redact(value)))
    seen, unique = set(), []
    for f in found:
        if f not in seen:
            seen.add(f)
            unique.append(f)
    return unique


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    total = 0
    for path in sys.argv[1:]:
        findings = scan(read_text(path))
        total += len(findings)
        print(f"{path}: {len(findings)} possible secret(s)")
        for label, value in findings:
            print(f"  - {label}: {value}")
    if total:
        print("SEC-07 = No. Ask the vendor to rotate these and send per-environment credentials "
              "through a secure channel. Do not copy them into any file, ticket or chat.")
    sys.exit(1 if total else 0)


if __name__ == "__main__":
    main()
