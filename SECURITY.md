# Security Policy

## Supported Versions

| Version | Supported |
| :--- | :--- |
| `0.1.x` | Yes (current validation release) |

---

## Security & Privacy Design

ManualOps Radar is designed with a minimal attack surface:
1. **Read-Only Public API Access:** Fetches only public JSON from `https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs?content=true` over HTTPS.
2. **Token & Input Validation:** `src/fetcher.py` validates `board_token` against `^[a-zA-Z0-9_-]{1,64}$`, enforces bounded request timeouts (`1..60s`), and caps response payloads at `10 MiB` (`ResponseTooLargeError`).
3. **XSS & URL Scheme Protection:** `src/renderer.py` escapes all rendered text (`html.escape`), restricts `<a href>` attributes strictly to `http://` and `https://` URLs (`sanitize_http_url`), blocks `javascript:`/`data:` schemes, sets `rel="noopener noreferrer"`, and embeds a restrictive `Content-Security-Policy` meta tag in generated HTML reports.
4. **Zero Credentials & Zero PII:** The repository stores no API keys, authentication cookies, or personal contact data.

---

## Reporting a Vulnerability

**Please do not open a public GitHub issue for security vulnerabilities.**

Instead, please report security issues privately using one of the following methods:
1. **GitHub Private Vulnerability Reporting:** Go to the repository's **Security** tab -> **Advisories** -> **Report a vulnerability** (once enabled on GitHub).
2. If private advisories are unavailable, open a minimal issue titled `[SECURITY] Request private contact channel` without disclosing exploit details, and the maintainer will follow up privately.

When reporting, please include:
- Affected file(s) and line number(s)
- Steps to reproduce (preferably using synthetic data)
- Potential impact (e.g., HTML XSS in generated reports, SSRF/path injection in fetcher, DoS via oversized JSON)

We aim to acknowledge security reports within **5 business days** and coordinate a fix before public disclosure.
