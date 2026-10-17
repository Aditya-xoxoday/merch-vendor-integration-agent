"""The secret scanner must catch real-looking credentials and never print them in full."""

FAKE = "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6"


def test_labeled_secret_found_and_redacted(ss):
    found = ss.scan(f"Consumer Key: {FAKE}\nAccess Token Secret: {FAKE[::-1]}")
    assert len(found) == 2
    assert all(FAKE not in v and FAKE[::-1] not in v for _, v in found)


def test_placeholders_ignored(ss):
    assert ss.scan("API Key: <your-api-key-here>\nclient_secret: {{client_secret}}\npassword: xxxxxxxxxxxxxx") == []


def test_truncated_samples_ignored(ss):
    assert ss.scan('"access_token": "eyJhbGciOiJSUzI1NiIsImtpZCI6..."') == []


def test_patterns(ss):
    text = "AKIAABCDEFGHIJKLMNOP eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjM0NTYifQ.abcdefghijklmnop https://u:supersecret@host"
    labels = {label for label, _ in ss.scan(text)}
    assert {"AWS access key", "JWT", "Credential in URL"} <= labels


def test_cli_exit_codes(tmp_path):
    import subprocess, sys
    from conftest import SKILL
    clean, dirty = tmp_path / "c.txt", tmp_path / "d.txt"
    clean.write_text("GET /rest/V1/products")
    dirty.write_text(f"api_key = {FAKE}")
    script = str(SKILL / "scripts" / "scan_secrets.py")
    assert subprocess.run([sys.executable, script, str(clean)], capture_output=True).returncode == 0
    out = subprocess.run([sys.executable, script, str(dirty)], capture_output=True, text=True)
    assert out.returncode == 1 and FAKE not in out.stdout
