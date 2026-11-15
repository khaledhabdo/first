# ManualOps Radar — Project Roadmap

This roadmap tracks the modular evolution of the Apache-2.0 open-source core (`manualops-radar`) while keeping evaluation integrity and commercial validation ahead of feature sprawl.

---

## `v0.1.0` — Open-Source Foundation & Validation Integrity (Current Candidate)
- Zero-dependency Python 3.11+ deterministic detection engine (`fetcher`, `parser`, `classifier`, `renderer`).
- Strict separation between automated heuristic labels (`heuristic_evaluation`) and independent human ground truth (`human_ground_truth`).
- Input/URL security hardening, synthetic test fixtures, offline GitHub Actions CI, Apache-2.0 licensing, and third-party data provenance documentation.

## `v0.2.0` — Ground-Truth Benchmark & Signal Pivot Rules
- Complete independent human labeling on the 50-record Phase 1.5 worksheet (`data/phase1_5_evaluation_worksheet.csv`) and publish measured ground-truth precision/recall baselines.
- Add configurable rule profiles so users can suppress routine frontline sales CRM note-taking and prioritize **Spreadsheet-to-System Migration** and **Named SaaS-Pair Manual Bridge** signals (`Sheets + AppScripts`, `Shopify + QuickBooks`, `HubSpot + NetSuite`).
- Expand rule coverage for high-pain phrases discovered during manual error analysis (`"pulled by hand"`, `"reconciled by eye"`, `"daily data entry"`, `"manual spreadsheet work"`).

## `v0.3.0` — Modular ATS Adapters & Mid-Market Evaluation
- Define a clean `BoardFetcher` protocol in `src/models.py` so additional official public ATS feeds (e.g., Lever, Ashby public boards) can be added as opt-in plugins without changing the classifier.
- Validate signal quality on 10–20 non-tech mid-market companies (logistics, healthcare RCM, property/accounting operations) rather than large cloud-native enterprises.
- Add default company/workflow deduplication views in the static HTML report.

## Future Modular Extensions (Separate from Apache-2.0 Core)
- Because `src/parser.py`, `src/classifier.py`, and `src/prepare_eval_sample.py` expose clean, stateless Python functions and dataclasses, downstream hosted services, scheduling orchestration, or team-collaboration layers can be built separately on top of this Apache-2.0 core without modifying its open-source licensing or offline-first guarantees.
