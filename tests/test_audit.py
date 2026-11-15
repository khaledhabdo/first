"""Unit tests for Phase 1 Signal Quality Audit & Company/Workflow Deduplication."""

import json
from pathlib import Path
import tempfile
import unittest
from src.audit_phase1 import (
    build_documented_rejected_audit,
    classify_commercial_signal_quality,
    normalize_workflow_signature,
    run_signal_quality_audit,
)


class TestSignalQualityAudit(unittest.TestCase):
    def test_company_workflow_deduplication_collapses_bdr_crm_hygiene(self) -> None:
        sig1 = {
            "board_token": "gitlab",
            "workflow_category": "CRM Operations",
            "job_title": "Business Development Representative, German Speaking",
            "exact_evidence": "Manage, track, and accurately report all prospecting activities and pipeline in Salesforce.",
        }
        sig2 = {
            "board_token": "gitlab",
            "workflow_category": "CRM Operations",
            "job_title": "Sales Development Representative",
            "exact_evidence": "Manage, track, and report on all activities and results using Salesforce",
        }
        self.assertEqual(normalize_workflow_signature(sig1), normalize_workflow_signature(sig2))

    def test_distinguishes_routine_responsibility_from_genuine_automation_pain(self) -> None:
        routine_crm = {
            "workflow_category": "CRM Operations",
            "exact_evidence": "Update Salesforce with detailed call notes, track opportunities, and plan follow-up actions.",
        }
        genuine_pain = {
            "workflow_category": "Data Entry",
            "exact_evidence": (
                "Maintain the accuracy and integrity of our HR Information System (Workday) "
                "by accurately entering employee change transactions manually and through bulk data uploads."
            ),
        }
        remaining_fp = {
            "workflow_category": "Reconciliation",
            "exact_evidence": "Lead independent discussions with TechOps, Engineering and XFN Partners to unblock complex reconciliation issues.",
        }
        self.assertEqual(
            classify_commercial_signal_quality(routine_crm)["audit_label"],
            "ROUTINE_JOB_RESPONSIBILITY",
        )
        self.assertEqual(
            classify_commercial_signal_quality(genuine_pain)["audit_label"],
            "GENUINE_AUTOMATION_PAIN",
        )
        self.assertEqual(
            classify_commercial_signal_quality(remaining_fp)["audit_label"],
            "REMAINING_FALSE_POSITIVE",
        )

    def test_audit_runs_in_isolation_with_synthetic_signals(self) -> None:
        rejected_audit = build_documented_rejected_audit()
        self.assertGreaterEqual(len(rejected_audit), 20)

        synthetic_signals = [
            {
                "company_name": "Acme Corp",
                "board_token": "acmecorp",
                "job_title": f"Ops Specialist {i}",
                "department": "Operations",
                "source_url": f"https://example.com/jobs/{i}",
                "first_published": "2026-11-01T00:00:00Z",
                "updated_at": "2026-11-10T00:00:00Z",
                "workflow_category": "Data Entry" if i % 2 == 0 else "CRM Operations",
                "signal_subtype": "DIRECT_MANUAL_EXECUTION",
                "exact_evidence": (
                    f"Manually enter vendor batch {i} into NetSuite."
                    if i % 2 == 0
                    else f"Update Salesforce with detailed call notes for territory {i}."
                ),
            }
            for i in range(1, 25)
        ]

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            in_json = tmp_path / "synthetic_phase1.json"
            out_json = tmp_path / "synthetic_audit.json"
            in_json.write_text(json.dumps({"valid_signals": synthetic_signals}), encoding="utf-8")

            audit_res = run_signal_quality_audit(
                phase1_json_path=in_json,
                audit_json_path=out_json,
            )
            metrics = audit_res["verified_metrics"]
            self.assertTrue(out_json.exists())
            self.assertGreaterEqual(metrics["manually_reviewed_accepted_sample_size"], 20)
            self.assertGreaterEqual(metrics["manually_reviewed_rejected_sample_size"], 20)
            self.assertEqual(metrics["external_buying_or_outsourcing_intent_in_accepted_pct"], 0.0)


if __name__ == "__main__":
    unittest.main()
