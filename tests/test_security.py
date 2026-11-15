"""Security regression tests for fetcher validation, limits, and HTML XSS/URL safety."""

import json
from pathlib import Path
import unittest
from unittest.mock import MagicMock, patch

from src.classifier import classify_statement
from src.fetcher import fetch_board_jobs, validate_board_token
from src.models import JobPosting
from src.parser import extract_candidate_statements
from src.renderer import render_phase1_html_report, sanitize_http_url

FIXTURE_PATH = Path(__file__).resolve().parent / "fixtures" / "synthetic_board.json"


class TestSecurityControls(unittest.TestCase):
    def test_validate_board_token_blocks_path_and_query_injection(self) -> None:
        self.assertEqual(validate_board_token("stripe"), "stripe")
        self.assertEqual(validate_board_token("acme_corp-1"), "acme_corp-1")

        bad_tokens = [
            "",
            "   ",
            "../admin",
            "stripe/jobs",
            "stripe?content=false",
            "stripe#fragment",
            "stripe@evil.com",
            "a" * 65,
        ]
        for token in bad_tokens:
            with self.assertRaises(ValueError, msg=f"Should reject token: {token!r}"):
                validate_board_token(token)

            jobs, status, err = fetch_board_jobs(token, "BadCorp")
            self.assertEqual(jobs, [])
            self.assertIsNone(status)
            self.assertIsNotNone(err)

    def test_fetch_board_jobs_enforces_response_size_limit(self) -> None:
        oversized_payload = b'{"jobs": []}' + (b" " * 2048)
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.read.return_value = oversized_payload[:1025]
        mock_cm = MagicMock()
        mock_cm.__enter__.return_value = mock_response
        mock_cm.__exit__.return_value = False

        with patch("src.fetcher.urllib.request.urlopen", return_value=mock_cm):
            jobs, status, err = fetch_board_jobs(
                "acme_test",
                "Acme",
                timeout_seconds=5,
                max_response_bytes=1024,
            )

        self.assertEqual(jobs, [])
        self.assertEqual(status, 200)
        self.assertIsNotNone(err)
        assert err is not None
        self.assertIn("ResponseTooLargeError", err)

    def test_fetch_board_jobs_rejects_non_positive_timeout_and_handles_timeout(self) -> None:
        jobs, status, err = fetch_board_jobs("acme_test", "Acme", timeout_seconds=0)
        self.assertEqual(jobs, [])
        self.assertIsNone(status)
        self.assertIn("Invalid timeout_seconds", str(err))

        with patch("src.fetcher.urllib.request.urlopen", side_effect=TimeoutError("timed out")):
            jobs, status, err = fetch_board_jobs("acme_test", "Acme", timeout_seconds=120)
        self.assertEqual(jobs, [])
        self.assertIsNone(status)
        self.assertIn("TimeoutError after 60s", str(err))

    def test_sanitize_http_url_blocks_xss_schemes(self) -> None:
        self.assertEqual(
            sanitize_http_url("https://boards.greenhouse.io/stripe/jobs/123"),
            "https://boards.greenhouse.io/stripe/jobs/123",
        )
        self.assertEqual(
            sanitize_http_url("http://example.com/job"),
            "http://example.com/job",
        )
        unsafe_urls = [
            "javascript:alert(1)",
            "JAVASCRIPT:alert(document.cookie)",
            "data:text/html,<script>alert(1)</script>",
            "vbscript:msgbox(1)",
            "file:///etc/passwd",
            "/relative/path",
            "",
            None,
        ]
        for bad in unsafe_urls:
            self.assertIsNone(sanitize_http_url(bad), f"Should block {bad!r}")

    def test_renderer_escapes_html_and_blocks_unsafe_urls_with_synthetic_fixture(self) -> None:
        fixture_bytes = FIXTURE_PATH.read_bytes()
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.read.return_value = fixture_bytes
        mock_cm = MagicMock()
        mock_cm.__enter__.return_value = mock_response
        mock_cm.__exit__.return_value = False

        with patch("src.fetcher.urllib.request.urlopen", return_value=mock_cm):
            jobs, status, err = fetch_board_jobs("acme_synthetic", "Acme Logistics")

        self.assertEqual(status, 200)
        self.assertIsNone(err)
        self.assertEqual(len(jobs), 2)

        valid = []
        rejected = []
        for job in jobs:
            for stmt in extract_candidate_statements(job.raw_content):
                res = classify_statement(job, stmt)
                if res is None:
                    continue
                if res.classification == "VALID_SIGNAL":
                    valid.append(res.to_dict())
                else:
                    rejected.append(res.to_dict())

        # Job 90001 has 2 valid (Data Entry + Reconciliation) and 2 rejected (Skill + Verb excel)
        # Job 90002 has 1 valid (CRM Operations) with an unsafe javascript: URL
        self.assertEqual(len(valid), 3)
        self.assertEqual(len(rejected), 2)

        # Inject a malicious script tag into a title to verify escaping
        valid[0]["job_title"] = '<script>alert("xss")</script>'
        report_data = {
            "generated_at": "2026-11-15T00:00:00Z",
            "summary": {
                "boards_configured": 1,
                "boards_scanned": 1,
                "api_errors_count": 0,
                "total_jobs_scanned": 2,
                "total_candidates_evaluated": 5,
                "valid_signals_count": len(valid),
                "unique_valid_signals_count": len(valid),
                "regional_duplicates_count": 0,
                "heuristic_workflow_clusters_count": 3,
                "heuristic_rejected_candidates_count": len(rejected),
                "heuristic_rejection_rate_pct": 40.0,
                "valid_by_category": {"Data Entry": 1, "Reconciliation": 1, "CRM Operations": 1},
                "valid_by_subtype": {"DIRECT_MANUAL_EXECUTION": 3},
                "rejected_by_reason": {"GENERAL_SOFTWARE_SKILL": 1, "VERB_EXCEL_OR_IDIOM": 1},
                "ground_truth_evaluation": {
                    "status": "PENDING_INDEPENDENT_HUMAN_LABELS",
                    "human_labeled_count": 0,
                    "total_sample_size": 50,
                },
            },
            "recommendation": {"verdict": "HOLD", "summary": "Synthetic test payload."},
            "boards": [
                {
                    "board_token": "acme_synthetic",
                    "company_name": "Acme Logistics (Synthetic)",
                    "http_status": 200,
                    "jobs_fetched": 2,
                    "candidate_sentences_evaluated": 5,
                    "valid_signals_count": 3,
                    "unique_valid_signals_count": 3,
                    "rejected_count": 2,
                    "error_message": None,
                }
            ],
            "valid_signals": valid,
            "rejected_samples": rejected,
        }

        html_out = render_phase1_html_report(report_data)
        self.assertIn("Content-Security-Policy", html_out)
        self.assertNotIn('href="javascript:alert(1)"', html_out)
        self.assertIn("[unsafe/invalid URL blocked]", html_out)
        self.assertNotIn('<script>alert("xss")</script>', html_out)
        self.assertIn('&lt;script&gt;alert(&quot;xss&quot;)&lt;/script&gt;', html_out)


if __name__ == "__main__":
    unittest.main()
