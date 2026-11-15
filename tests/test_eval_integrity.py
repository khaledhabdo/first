"""Unit tests for Phase 1.5 Evaluation Integrity (src/prepare_eval_sample.py)."""

import copy
import unittest
from src.models import EvaluatedCandidate
from src.prepare_eval_sample import (
    build_reproducible_evaluation_sample,
    compute_ground_truth_metrics,
)


def _make_candidate(
    idx: int,
    classification: str,
    rejection_reason: str | None = None,
) -> EvaluatedCandidate:
    return EvaluatedCandidate(
        board_token="stripe",
        company_name="Stripe",
        job_id=1000 + idx,
        job_title=f"Role {idx}",
        department="Finance",
        location="Remote",
        source_url=f"https://boards.greenhouse.io/stripe/jobs/{1000 + idx}",
        first_published="2026-11-01T00:00:00Z",
        updated_at="2026-11-14T00:00:00Z",
        workflow_category="Reconciliation",
        exact_evidence=f"Sample candidate statement number {idx} for reconciliation testing.",
        matched_trigger="reconciliation",
        classification=classification,
        signal_subtype="DIRECT_MANUAL_EXECUTION" if classification == "VALID_SIGNAL" else "NONE",
        rejection_reason=rejection_reason,
        explanation="Heuristic explanation",
        buying_intent_assessment="NO DIRECT BUYING INTENT",
        uncertainty_factors=[],
    )


class TestEvaluationIntegrity(unittest.TestCase):
    def test_sample_is_reproducible_and_separates_heuristic_from_human_labels(self) -> None:
        accepted = [_make_candidate(i, "VALID_SIGNAL") for i in range(10)]
        rejected = [
            _make_candidate(100 + i, "REJECTED_FALSE_POSITIVE", "GENERAL_SOFTWARE_SKILL")
            for i in range(10)
        ]

        sample_a = build_reproducible_evaluation_sample(
            accepted, rejected, accepted_sample_size=5, rejected_sample_size=5, seed=42
        )
        sample_b = build_reproducible_evaluation_sample(
            accepted, rejected, accepted_sample_size=5, rejected_sample_size=5, seed=42
        )

        self.assertEqual(sample_a, sample_b)
        self.assertEqual(len(sample_a), 10)
        for rec in sample_a:
            self.assertIn("heuristic_evaluation", rec)
            self.assertIn("human_ground_truth", rec)
            self.assertTrue(rec["heuristic_evaluation"]["is_automated_heuristic"])
            self.assertFalse(rec["human_ground_truth"]["is_independently_human_reviewed"])
            self.assertIsNone(rec["human_ground_truth"]["human_pain_tier"])

    def test_unlabeled_sample_reports_pending_and_no_hardcoded_percentages(self) -> None:
        accepted = [_make_candidate(i, "VALID_SIGNAL") for i in range(4)]
        rejected = [
            _make_candidate(100 + i, "REJECTED_FALSE_POSITIVE", "GENERAL_SOFTWARE_SKILL")
            for i in range(4)
        ]
        sample = build_reproducible_evaluation_sample(
            accepted, rejected, accepted_sample_size=2, rejected_sample_size=2, seed=99
        )
        metrics = compute_ground_truth_metrics(sample)
        self.assertEqual(metrics["status"], "PENDING_INDEPENDENT_HUMAN_LABELS")
        self.assertEqual(metrics["human_labeled_count"], 0)
        self.assertIsNone(metrics["verified_task_precision_pct"])
        self.assertIsNone(metrics["verified_commercial_pain_precision_pct"])
        self.assertIsNone(metrics["verified_false_positive_rate_on_accepted_pct"])
        self.assertIsNone(metrics["verified_false_negative_rate_on_rejected_pct"])

    def test_ground_truth_metrics_compute_strictly_from_human_labels(self) -> None:
        accepted = [_make_candidate(i, "VALID_SIGNAL") for i in range(4)]
        rejected = [
            _make_candidate(100 + i, "REJECTED_FALSE_POSITIVE", "GENERAL_SOFTWARE_SKILL")
            for i in range(4)
        ]
        sample = build_reproducible_evaluation_sample(
            accepted, rejected, accepted_sample_size=2, rejected_sample_size=2, seed=99
        )
        labeled_sample = copy.deepcopy(sample)
        # 2 heuristic-accepted: 1 genuine pain, 1 false positive -> 50% precision, 50% FP
        labeled_sample[0]["human_ground_truth"]["human_pain_tier"] = "GENUINE_AUTOMATION_PAIN"
        labeled_sample[1]["human_ground_truth"]["human_pain_tier"] = "NOT_A_WORKFLOW_FALSE_POSITIVE"
        # 2 heuristic-rejected: 1 missed pain, 1 true negative -> 50% FN
        labeled_sample[2]["human_ground_truth"]["human_pain_tier"] = "GENUINE_AUTOMATION_PAIN"
        labeled_sample[3]["human_ground_truth"]["human_pain_tier"] = "NOT_A_WORKFLOW_FALSE_POSITIVE"

        metrics = compute_ground_truth_metrics(labeled_sample)
        self.assertEqual(metrics["status"], "COMPLETE_HUMAN_LABELS")
        self.assertEqual(metrics["human_labeled_count"], 4)
        self.assertEqual(metrics["verified_commercial_pain_precision_pct"], 50.0)
        self.assertEqual(metrics["verified_false_positive_rate_on_accepted_pct"], 50.0)
        self.assertEqual(metrics["verified_false_negative_rate_on_rejected_pct"], 50.0)


if __name__ == "__main__":
    unittest.main()
