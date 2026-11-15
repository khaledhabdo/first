# Contributing to ManualOps Radar

Thank you for your interest in contributing to **ManualOps Radar**!

Because this project analyzes public job descriptions and emphasizes scientific evaluation integrity, all contributions must follow our technical, ethical, and licensing standards below.

---

## 1. Ethical & Data Guardrails (Non-Negotiable)

Pull requests will be rejected if they introduce:
- Scraping of authenticated, private, or rate-limit-bypassed sources (only official public APIs such as Greenhouse's public Job Board API are permitted).
- Personal contact harvesting (emails, phone numbers, LinkedIn profiles of recruiters/hiring managers).
- Automated outreach, email sending, or spam workflows.
- Paid API dependencies or mandatory LLM API keys inside the open-source core.

---

## 2. Local Development Setup

ManualOps Radar uses **Python 3.11+** and the **Python Standard Library only** (zero external runtime packages).

```bash
# 1. Clone the repository and switch to a feature branch
git checkout -b feat/your-change

# 2. Run the full offline unit & security test suite
python3 -m unittest discover -s tests -v

# 3. Verify Python syntax compilation
python3 -m compileall src tests
```

---

## 3. Coding & Evaluation Integrity Standards

1. **Deterministic Rules Before AI:** New signal rules in `src/classifier.py` must be deterministic, readable, and accompanied by both **positive tests** (true operational workflow) and **negative/false-positive tests** (general skill, idiom, product pitch, engineering role).
2. **Never Hardcode Evaluation Metrics:** Do not hardcode precision, recall, or false-positive percentages in `src/`. Ground-truth metrics must only be computed from independent human annotations via `src/prepare_eval_sample.py`.
3. **Keep Tests Offline and Side-Effect Free:**
   - Tests in `tests/` must **never** issue live HTTP requests (mock `urllib.request.urlopen` or use `tests/fixtures/`).
   - Tests must **never** overwrite tracked files in `data/` or `reports/` (use `tempfile.TemporaryDirectory()`).
4. **Security Hygiene:**
   - Validate any new external input slugs/tokens.
   - Escape all untrusted strings before rendering HTML and sanitize all external URLs to `http://` or `https://` only.
5. **Licensing & Fixtures:**
   - Use synthetic fixtures (e.g., `tests/fixtures/synthetic_board.json`) for unit tests instead of copying large third-party job descriptions.

---

## 4. Pull Request Checklist

Before submitting a PR:
- [ ] `python3 -m unittest discover -s tests -v` passes with 0 errors.
- [ ] `git status` shows no unintended changes to `data/` or `reports/`.
- [ ] New rules include synthetic test cases covering false positives.
- [ ] No credentials, tokens, or personal data are included.
- [ ] All contributions are submitted under the [Apache-2.0 License](LICENSE).
