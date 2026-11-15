"""Unit tests for src/renderer.py."""

import unittest
from src.renderer import render_phase1_html_report


class TestRenderer(unittest.TestCase):
    def test_html_report_renders_valid_and_rejected_sections_with_escaping(self) -> None:
        sample_payload = {
            "generated_at": "2026-11-15T04:20:00Z",
            "summary": {
                "boards_configured": 5,
                "boards_scanned": 5,
                "api_errors_count": 0,
                "total_jobs_scanned": 1974,
                "total_candidates_evaluated": 856,
                "valid_signals_count": 1,
                "unique_valid_signals_count": 1,
                "regional_duplicates_count": 0,
                "rejected_false_positives_count": 1,
                "false_positive_rate_pct": 50.0,
                "valid_by_category": {"Reconciliation": 1},
                "valid_by_subtype": {"DIRECT_MANUAL_EXECUTION": 1},
                "rejected_by_reason": {"GENERAL_SOFTWARE_SKILL": 1},
            },
            "recommendation": {
                "verdict": "IMPROVE",
                "summary": "Improve target board selection before Phase 2.",
            },
            "boards": [
                {
                    "board_token": "stripe",
                    "company_name": "Stripe",
                    "http_status": 200,
                    "jobs_fetched": 785,
                    "candidate_sentences_evaluated": 300,
                    "valid_signals_count": 1,
                    "unique_valid_signals_count": 1,
                    "rejected_count": 299,
                    "error_message": None,
                }
            ],
            "valid_signals": [
                {
                    "company_name": "Stripe",
                    "department": "Finance & <Accounting>",
                    "job_title": "Controller",
                    "location": "Remote",
                    "source_url": "https://boards.greenhouse.io/stripe/jobs/1",
                    "workflow_category": "Reconciliation",
                    "signal_subtype": "DIRECT_MANUAL_EXECUTION",
                    "exact_evidence": "Perform monthly balance sheet reconciliations.",
                    "first_published": "2026-11-01T00:00:00Z",
                    "updated_at": "2026-11-14T00:00:00Z",
                    "buying_intent_assessment": "NO DIRECT BUYING INTENT: Hiring proves task existence only.",
                    "is_regional_duplicate": False,
                }
            ],
            "rejected_samples": [
                {
                    "company_name": "Stripe",
                    "job_title": "BDR",
                    "source_url": "https://boards.greenhouse.io/stripe/jobs/2",
                    "workflow_category": "CRM Operations",
                    "rejection_reason": "GENERAL_SOFTWARE_SKILL",
                    "exact_evidence": "Proficiency in Salesforce is a plus.",
                    "explanation": "General candidate qualification only.",
                    "first_published": "2026-11-02T00:00:00Z",
                    "updated_at": "2026-11-14T00:00:00Z",
                }
            ],
        }
        html_out = render_phase1_html_report(sample_payload)
        self.assertIn("ManualOps Radar — Phase 1: Real Data Validation Report", html_out)
        self.assertIn("Perform monthly balance sheet reconciliations.", html_out)
        self.assertIn("GENERAL_SOFTWARE_SKILL", html_out)
        self.assertIn("Proficiency in Salesforce is a plus.", html_out)
        self.assertIn("Finance &amp; &lt;Accounting&gt;", html_out)


if __name__ == "__main__":
    unittest.main()
