# ManualOps Radar

**A deterministic, zero-dependency Python engine for auditing manual operational workflow mentions in public Greenhouse job descriptions — without inferring buying intent.**

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](pyproject.toml)

> **Status (`v0.1.0` — Alpha Validation Release):** ManualOps Radar is an early-stage open-source research and signal-auditing toolkit. It uses 100% deterministic rules and the Python Standard Library (zero paid APIs, zero LLMs, zero databases).

---

## Why ManualOps Radar Exists

Naive keyword searches on job boards (e.g., searching for `"Excel"`, `"Salesforce"`, `"reporting"`, or `"reconciliation"`) produce extreme noise:
- Candidate qualifications (*"Proficiency in Excel and Salesforce is a plus"*)
- English idioms (*"excel in a fast-paced environment"*, *"reporting to the Director"*)
- Product marketing descriptions (*"helping customers eliminate manual invoicing"*)
- Routine sales hygiene (*"Update Salesforce with detailed call notes"*)

Even when a genuine manual workflow exists, **a job posting proves task existence — never software buying intent**. In our Phase 1 validation across 5 public tech boards (1,977 postings), companies addressed manual workflows via internal headcount or internal AI/ERP builds rather than expressing external vendor buying intent.

ManualOps Radar separates **technical signal extraction** from **evaluation integrity** and **commercial validation**.

---

## Architecture & Modular Design

The core engine under [`src/`](src/) is organized into independent, composable modules using Python dataclasses so any downstream tool, CLI, or separately hosted service can import individual stages cleanly:

```text
config/boards_phase1.json
        │
        ▼
 [1] src/fetcher.py           ──► Validated Greenhouse Public API client
        │                         (slug validation, bounded timeouts, 10 MiB response cap)
        ▼
 [2] src/parser.py            ──► Double-HTML unescaper & bullet/sentence splitter
        │
        ▼
 [3] src/classifier.py        ──► Deterministic 5-gate rules & false-positive filter
        │                         (Spreadsheets, Reporting, Reconciliation, Data Entry, CRM)
        ├──► [4a] src/prepare_eval_sample.py ──► Stratified reproducible sample + ground-truth calculator
        ├──► [4b] src/audit_phase1.py        ──► Heuristic company/workflow grouping & audit helpers
        └──► [4c] src/renderer.py            ──► XSS-hardened static HTML report with CSP & URL checks
```

### Key Design Boundaries
- **Pure Python Standard Library:** `src/` imports only stdlib modules (`json`, `re`, `html`, `urllib`, `csv`, `dataclasses`, `pathlib`, `random`).
- **Modular Core vs. Hosted Extensions:** The Apache-2.0 open-source core handles public-board fetching, parsing, deterministic classification, reproducible evaluation sampling, and static report rendering. Any future hosted dashboards, multi-ATS connectors, or paid SaaS features can depend on this modular engine independently without restricting the Apache-2.0 core.

---

## Quick Start

### 1. Prerequisites
- Python **3.11** or higher (no `pip install` required; zero third-party runtime dependencies).

### 2. Run the Offline Unit & Security Test Suite
All unit tests run completely offline using synthetic fixtures ([`tests/fixtures/synthetic_board.json`](tests/fixtures/synthetic_board.json)) and mocked responses — they never hit live APIs or mutate tracked files in `data/`:

```bash
python3 -m unittest discover -s tests -v
```

### 3. Use the Modular Engine Programmatically (Offline Example)
```python
from src.classifier import classify_statement
from src.models import JobPosting
from src.parser import extract_candidate_statements

job = JobPosting(
    board_token="acme_ops",
    company_name="Acme Logistics",
    job_id=101,
    job_title="Accounts Payable Specialist",
    source_url="https://example.com/jobs/101",
    updated_at="2026-11-15T00:00:00Z",
    first_published="2026-11-01T00:00:00Z",
    location="Remote",
    department="Finance",
    raw_content="&lt;ul&gt;&lt;li&gt;Manually enter carrier invoices into NetSuite.&lt;/li&gt;&lt;li&gt;Proficiency in Excel required.&lt;/li&gt;&lt;/ul&gt;",
)

for stmt in extract_candidate_statements(job.raw_content):
    result = classify_statement(job, stmt)
    if result:
        print(result.classification, "|", result.rejection_reason or result.signal_subtype, "|", result.exact_evidence)
```

### 4. Run Live Validation Against Approved Greenhouse Boards (Optional)
Reads [`config/boards_phase1.json`](config/boards_phase1.json), queries Greenhouse's public Job Board API (`https://boards-api.greenhouse.io/v1/boards/{token}/jobs?content=true`), regenerates JSON/HTML outputs, and exports a reproducible 50-record evaluation worksheet:

```bash
python3 -m src.run_phase1
```

---

## Evaluation Integrity & Actual Capabilities

In **Phase 1.5**, we enforced strict separation between automated heuristics and verified human ground truth:
- **Heuristic Outputs (`heuristic_evaluation`):** Automated rule hits, heuristic rejection rate (share of keyword matches filtered out by rules), and heuristic company/workflow groupings.
- **Human Ground Truth (`human_ground_truth`):** Initialized to `null` inside [`data/phase1_5_evaluation_sample.json`](data/phase1_5_evaluation_sample.json) and [`data/phase1_5_evaluation_worksheet.csv`](data/phase1_5_evaluation_worksheet.csv). Precision, false-positive, and false-negative rates remain `PENDING_INDEPENDENT_HUMAN_LABELS` until labeled independently using [`docs/LABELING_GUIDELINES.md`](docs/LABELING_GUIDELINES.md).

---

## Known Limitations

1. **Greenhouse-Only Ingestion:** Currently supports only official public Greenhouse job boards listed in an approved config file.
2. **Sample Bias in Phase 1 Benchmarks:** The initial 5 boards (`stripe`, `cloudflare`, `gitlab`, `datadog`, `gusto`) are large cloud-native tech companies with strong internal engineering/AI teams. See [`docs/PHASE1_5_COMMERCIAL_VALIDATION.md`](docs/PHASE1_5_COMMERCIAL_VALIDATION.md) for why mid-market non-tech companies behave differently.
3. **No Buying-Intent Detection:** Job descriptions rarely state software budgets or vendor-evaluation intent; every valid signal includes an explicit `NO DIRECT BUYING INTENT` warning.
4. **English Regex Scope:** Rules target English operational phrasing and miss implicit manual work phrased outside current patterns.

---

## Repository Structure

```text
manualops-radar/
├── .github/workflows/ci.yml          # Offline unit-test & security CI (contents: read)
├── config/boards_phase1.json         # Manually approved Phase 1 Greenhouse board tokens
├── data/                             # Preserved Phase 1/1.5 JSON/CSV validation snapshots
├── docs/
│   ├── DATA_PROVENANCE.md            # Audit & licensing boundary for tracked data/reports
│   ├── LABELING_GUIDELINES.md        # Independent human ground-truth annotation guide
│   └── PHASE1_5_COMMERCIAL_VALIDATION.md  # Agency market research & 5 verified briefs
├── reports/                          # Preserved self-contained static HTML reports
├── src/                              # Apache-2.0 modular Python package (stdlib only)
├── tests/                            # Offline unit & security regression tests + fixtures
├── CHANGELOG.md
├── CONTRIBUTING.md
├── LICENSE                           # Apache License 2.0
├── NOTICE                            # Code vs. third-party excerpt attribution notice
├── pyproject.toml
├── ROADMAP.md
└── SECURITY.md
```

---

## Licensing & Third-Party Data Notice

- **Software & Original Documentation:** Licensed under the **Apache License 2.0** ([`LICENSE`](LICENSE)).
- **Third-Party Excerpts:** Tracked research snapshots in `data/` and `reports/` contain short verbatim excerpts from public employer job postings for research auditability. Those excerpts remain the intellectual property of their respective employers and are **not** licensed under Apache-2.0. See [`NOTICE`](NOTICE) and [`docs/DATA_PROVENANCE.md`](docs/DATA_PROVENANCE.md) for full provenance and reuse limitations.

---

## Contributing & Security

- Read [`CONTRIBUTING.md`](CONTRIBUTING.md) before opening a pull request.
- Report security issues privately following [`SECURITY.md`](SECURITY.md).
- See [`ROADMAP.md`](ROADMAP.md) for upcoming milestones.
