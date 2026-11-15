# Data Provenance, Attribution & Reuse Limitations

This document audits all tracked files under `data/`, `reports/`, and `docs/` so contributors and downstream users clearly understand what is original Apache-2.0 project work versus third-party sourced material.

---

## 1. Licensing Boundary (Code vs. Third-Party Excerpts)

- **Covered by Apache-2.0 (`LICENSE`):** All Python source code (`src/`), unit tests and synthetic test fixtures (`tests/`), CI configuration (`.github/`), packaging (`pyproject.toml`), and original documentation authored for this repository.
- **NOT Covered by Apache-2.0:** Verbatim job posting excerpts, job titles, and public URLs retrieved from third-party company job boards on Greenhouse (`data/`, `reports/`, and quoted excerpts in `docs/PHASE1_5_COMMERCIAL_VALIDATION.md`). These remain the intellectual property of their respective employers/publishers.

---

## 2. File-by-File Audit of Tracked Data, Reports, and Docs

| Path | Content Type | Source / Provenance | Personal Data (PII) | Reuse & Retention Notes |
| :--- | :--- | :--- | :--- | :--- |
| `data/phase1_results.json` | Current Phase 1.5 JSON output | Live Greenhouse Public Job Board API (`stripe`, `cloudflare`, `gitlab`, `datadog`, `gusto`) retrieved `2026-11-15` | None (`0` emails/contacts) | Preserves `source_url`, `first_published`, and `updated_at` per excerpt. Stored for reproducibility of Phase 1.5 metrics; do not redistribute as a commercial lead database. |
| `data/phase1_audit_results.json` | Heuristic commercial audit & groupings | Derived from `data/phase1_results.json` plus 25 documented rejected excerpts | None (`0` emails/contacts) | Preserved as historical Phase 1 audit artifact. |
| `data/phase1_5_evaluation_sample.json` | Reproducible 50-record evaluation sample (`seed=20261115`) | Stratified sample from the 5 Greenhouse boards; blank `human_ground_truth` fields | None (`0` emails/contacts) | Intended for independent human labeling per `docs/LABELING_GUIDELINES.md`. |
| `data/phase1_5_evaluation_worksheet.csv` | Spreadsheet worksheet for human labeling | Exported from `data/phase1_5_evaluation_sample.json` | None (`0` emails/contacts) | Same provenance as above. |
| `data/phase1_v1_results.json` | Preserved Phase 1 v1 snapshot | Snapshot before Phase 1.5 evaluation-integrity refactor (`2026-11-15`) | None (`0` emails/contacts) | Historical comparison baseline; preserved intact per Phase 1.5 instructions. |
| `data/phase1_v1_audit_results.json` | Preserved Phase 1 v1 audit snapshot | Snapshot before Phase 1.5 refactor (`2026-11-15`) | None (`0` emails/contacts) | Historical comparison baseline; preserved intact. |
| `reports/phase1_validation_report.html` | Self-contained Phase 1.5 static HTML report | Rendered from `data/phase1_results.json` | None (`0` emails/contacts) | Contains interactive JS filters and third-party job excerpts with source links. |
| `reports/phase1_v1_validation_report.html` | Preserved Phase 1 v1 HTML report | Rendered from `data/phase1_v1_results.json` | None (`0` emails/contacts) | Preserved for transparent before/after comparison of evaluation integrity fixes. |
| `docs/LABELING_GUIDELINES.md` | Original annotation protocol | Authored for this project (uses short illustrative examples) | None | Covered by Apache-2.0. |
| `docs/PHASE1_5_COMMERCIAL_VALIDATION.md` | Commercial validation research memo | Public agency pages/directories + 5 public Greenhouse API briefs (`zocdoc`, `flexport`, `faire`, `cloudflare`) verified `2026-11-15` | None (`0` emails/contacts) | Quoted excerpts and agency profiles remain attributed to their public URLs; verification date recorded. |

---

## 3. Guidelines for Open-Source Testing & Future Releases

- **Unit tests must stay offline and synthetic:** All tests in `tests/` run on synthetic fixtures (`tests/fixtures/synthetic_board.json`) or in-memory test objects and must never make live HTTP requests or mutate tracked files in `data/` or `reports/`.
- **No personal contact harvesting:** Never commit recruiter names, personal emails, phone numbers, or scraped private/authenticated pages.
- **Historical artifacts:** `data/phase1_v1_*` and `reports/phase1_v1_*` are kept on `chore/oss-readiness` for full auditability. Any future cleanup of large historical JSON/HTML snapshots from git should be done only after maintainer approval.
