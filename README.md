# ManualOps Radar — Phase 1: Real Data Validation Prototype

Cloud-first proof-of-concept for discovering repetitive manual operational workflows from public Greenhouse job descriptions using deterministic rules before any AI.

## Core Principles
1. **Deterministic Rules Before AI:** Zero paid APIs, zero LLMs, 100% reproducible regex and linguistic structure rules.
2. **Three-Way Distinction:**
   - **General Software Skills (`REJECTED: GENERAL_SOFTWARE_SKILL`):** e.g., *"Proficiency in Excel and Salesforce"*, *"Experience with CRM systems"*.
   - **Explicit Evidence of Repetitive Manual Work (`VALID_SIGNAL`):** Split into `DIRECT_MANUAL_EXECUTION` (hiring a human operator to execute the manual workflow) and `INTERNAL_AUTOMATION_MANDATE` (confirming manual pain while chartering the hire to automate it in-house).
   - **Actual Buying Intent (`NO DIRECT BUYING INTENT`):** Never inferred from hiring alone.
3. **Strict Privacy & Compliance Guardrails:** Uses only the official public Greenhouse Job Board API (`https://boards-api.greenhouse.io/v1/boards/{token}/jobs?content=true`). No scraping of restricted sources, no personal contact harvesting, no database, and no automated outreach.

## Running Phase 1 Validation

```bash
# Run unit tests
python3 -m unittest discover -s tests -v

# Execute live Phase 1 validation across the 5 verified Greenhouse boards
python3 -m src.run_phase1
```

## Outputs
- `data/phase1_results.json`: Exact metrics, board-by-board summary, all validated signals, and representative rejected matches.
- `reports/phase1_validation_report.html`: Self-contained static HTML report with interactive filtering for both valid signals and rejected false positives.
