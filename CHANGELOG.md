# Changelog

All notable changes to **ManualOps Radar** are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-11-15 (Release Candidate)

### Added
- **Open-Source Governance & Licensing:** Added Apache-2.0 `LICENSE`, `NOTICE` (clarifying third-party job excerpt ownership), `docs/DATA_PROVENANCE.md`, `CONTRIBUTING.md`, `SECURITY.md`, `ROADMAP.md`, and `pyproject.toml`.
- **Security Hardening & Regression Tests:**
  - Strict Greenhouse `board_token` slug validation (`^[a-zA-Z0-9_-]{1,64}$`), bounded timeouts (`1..60s`), and a `10 MiB` response payload cap in `src/fetcher.py`.
  - Strict `http://`/`https://` URL scheme sanitization (`sanitize_http_url`) and an embedded `Content-Security-Policy` header in `src/renderer.py` to block `javascript:`/`data:` XSS links.
  - Synthetic offline board fixture (`tests/fixtures/synthetic_board.json`) and security regression suite (`tests/test_security.py`).
- **Offline CI Workflow:** Added `.github/workflows/ci.yml` running offline unit and security tests on Python 3.11 and 3.12 with `permissions: contents: read`.
- **Phase 1.5 Evaluation Integrity:** Reproducible 50-record stratified evaluation sample (`src/prepare_eval_sample.py`), independent human labeling guide (`docs/LABELING_GUIDELINES.md`), commercial agency validation study (`docs/PHASE1_5_COMMERCIAL_VALIDATION.md`), and dynamic ground-truth metric computation without hardcoded percentages.
- **Phase 1 Core Prototype:** Zero-dependency Greenhouse API fetcher (`src/fetcher.py`), double-escaped HTML cleaner (`src/parser.py`), deterministic 5-category workflow classifier (`src/classifier.py`), and static HTML report renderer (`src/renderer.py`).

### Fixed
- Isolated `tests/test_audit.py` using `tempfile.TemporaryDirectory()` so running unit tests never mutates tracked files in `data/`.
