"""Reproducible Evaluation Sample Generator & Ground-Truth Metric Calculator (Phase 1.5).

Key Integrity Guarantees:
1. No predefined/hardcoded evaluation examples: draws deterministically via a fixed seed
   from the live candidate pool across all 5 boards.
2. Strictly separates `heuristic_evaluation` (automated rule output) from
   `human_ground_truth` (independent human annotation fields, initialized to None).
3. Never fabricates or hardcodes precision/recall percentages: ground-truth metrics
   are computed ONLY when `human_ground_truth.human_pain_tier` is populated.
"""

from collections import defaultdict
import csv
import json
from pathlib import Path
import random
from typing import Any

from src.audit_phase1 import (
    classify_commercial_signal_quality,
    normalize_workflow_signature,
)
from src.classifier import classify_statement
from src.fetcher import fetch_board_jobs
from src.models import EvaluatedCandidate
from src.parser import extract_candidate_statements

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CONFIG_PATH = PROJECT_ROOT / "config" / "boards_phase1.json"
DEFAULT_SAMPLE_JSON = PROJECT_ROOT / "data" / "phase1_5_evaluation_sample.json"
DEFAULT_SAMPLE_CSV = PROJECT_ROOT / "data" / "phase1_5_evaluation_worksheet.csv"
DEFAULT_SEED = 20261115


def collect_all_candidates_from_boards(
    config_path: Path = DEFAULT_CONFIG_PATH,
) -> tuple[list[EvaluatedCandidate], list[EvaluatedCandidate]]:
    """Fetches all jobs from configured boards and returns (all_accepted, all_rejected)."""
    with open(config_path, encoding="utf-8") as f:
        config = json.load(f)

    accepted: list[EvaluatedCandidate] = []
    rejected: list[EvaluatedCandidate] = []
    seen_accepted_By_board: dict[str, set[str]] = defaultdict(set)

    for board_entry in config.get("boards", []):
        token = board_entry["board_token"]
        company_name = board_entry["company_name"]
        jobs, _, _ = fetch_board_jobs(token, company_name)
        for job in jobs:
            for stmt in extract_candidate_statements(job.raw_content):
                ev = classify_statement(job, stmt)
                if ev is None:
                    continue
                if ev.classification == "VALID_SIGNAL":
                    norm = ev.exact_evidence.strip().lower()
                    if norm in seen_accepted_By_board[token]:
                        ev.is_regional_duplicate = True
                    else:
                        seen_accepted_By_board[token].add(norm)
                    accepted.append(ev)
                else:
                    rejected.append(ev)

    return accepted, rejected


def build_reproducible_evaluation_sample(
    accepted: list[EvaluatedCandidate],
    rejected: list[EvaluatedCandidate],
    accepted_sample_size: int = 25,
    rejected_sample_size: int = 25,
    seed: int = DEFAULT_SEED,
) -> list[dict[str, Any]]:
    """
    Draws a deterministic, reproducible stratified sample of accepted and rejected
    statements using `random.Random(seed)`.

    Each record cleanly separates `heuristic_evaluation` from `human_ground_truth`.
    """
    rng = random.Random(seed)

    # Deduplicate by (board_token, normalized_evidence) before sampling so reviewers don't label identical strings twice
    unique_accepted: list[EvaluatedCandidate] = []
    seen_acc: set[tuple[str, str]] = set()
    for item in accepted:
        key = (item.board_token, item.exact_evidence.strip().lower())
        if key not in seen_acc:
            seen_acc.add(key)
            unique_accepted.append(item)

    sampled_accepted = (
        rng.sample(unique_accepted, k=min(accepted_sample_size, len(unique_accepted)))
        if unique_accepted
        else []
    )

    # Stratified sampling across rejection reasons for rejected candidates
    rejected_by_reason: dict[str, list[EvaluatedCandidate]] = defaultdict(list)
    seen_rej: set[tuple[str, str]] = set()
    for item in rejected:
        key = (item.board_token, item.exact_evidence.strip().lower())
        if key not in seen_rej:
            seen_rej.add(key)
            reason = item.rejection_reason or "UNSPECIFIED"
            rejected_by_reason[reason].append(item)

    reasons = sorted(rejected_by_reason.keys())
    per_reason_quota = max(1, rejected_sample_size // max(1, len(reasons)))
    sampled_rejected: list[EvaluatedCandidate] = []
    leftover_pool: list[EvaluatedCandidate] = []

    for reason in reasons:
        bucket = rejected_by_reason[reason]
        k = min(per_reason_quota, len(bucket))
        chosen = rng.sample(bucket, k=k)
        sampled_rejected.extend(chosen)
        chosen_set = {id(x) for x in chosen}
        leftover_pool.extend(x for x in bucket if id(x) not in chosen_set)

    if len(sampled_rejected) < rejected_sample_size and leftover_pool:
        needed = min(rejected_sample_size - len(sampled_rejected), len(leftover_pool))
        sampled_rejected.extend(rng.sample(leftover_pool, k=needed))

    records: list[dict[str, Any]] = []
    for idx, item in enumerate(sampled_accepted + sampled_rejected, start=1):
        sig_dict = item.to_dict()
        _, heuristic_cluster = normalize_workflow_signature(sig_dict)
        heuristic_quality = (
            classify_commercial_signal_quality(sig_dict)
            if item.classification == "VALID_SIGNAL"
            else {
                "audit_label": "HEURISTIC_REJECTED_CANDIDATE",
                "operational_evidence": "FILTERED_OUT_BY_RULE",
                "buying_or_outsourcing_intent": "NONE_DETECTED",
                "audit_rationale": item.explanation,
            }
        )

        records.append(
            {
                "sample_id": f"EVAL-{idx:03d}",
                "board_token": item.board_token,
                "company_name": item.company_name,
                "job_id": item.job_id,
                "job_title": item.job_title,
                "department": item.department,
                "location": item.location,
                "source_url": item.source_url,
                "first_published": item.first_published,
                "updated_at": item.updated_at,
                "exact_evidence": item.exact_evidence,
                "heuristic_evaluation": {
                    "is_automated_heuristic": True,
                    "heuristic_decision": (
                        "HEURISTIC_ACCEPTED"
                        if item.classification == "VALID_SIGNAL"
                        else "HEURISTIC_REJECTED"
                    ),
                    "heuristic_workflow_category": item.workflow_category,
                    "heuristic_matched_trigger": item.matched_trigger,
                    "heuristic_signal_subtype": item.signal_subtype,
                    "heuristic_rejection_code": item.rejection_reason,
                    "heuristic_workflow_cluster_guess": heuristic_cluster,
                    "heuristic_pain_tier_guess": heuristic_quality["audit_label"],
                    "heuristic_rationale": heuristic_quality["audit_rationale"],
                },
                "human_ground_truth": {
                    "is_independently_human_reviewed": False,
                    "human_pain_tier": None,  # Allowed: GENUINE_AUTOMATION_PAIN | ROUTINE_JOB_RESPONSIBILITY | NOT_A_WORKFLOW_FALSE_POSITIVE
                    "human_buying_or_outsourcing_intent": None,  # Allowed: EXPLICIT_EXTERNAL_INTENT | INTERNAL_BUILD_OR_HIRE_ONLY | NONE
                    "human_agency_fit": None,  # Allowed: HIGH_FIT | LOW_FIT | NO_FIT
                    "reviewer_id": None,
                    "reviewed_at": None,
                    "reviewer_notes": "",
                },
            }
        )

    return records


def compute_ground_truth_metrics(sample_records: list[dict[str, Any]]) -> dict[str, Any]:
    """
    Computes ground-truth evaluation metrics strictly from human-labeled records.
    If no records have `is_independently_human_reviewed == True` (or non-null `human_pain_tier`),
    returns status="PENDING_INDEPENDENT_HUMAN_LABELS" with None for all precision/error rates.
    """
    labeled = [
        r
        for r in sample_records
        if r.get("human_ground_truth", {}).get("human_pain_tier") is not None
    ]
    total_sample = len(sample_records)
    if not labeled:
        return {
            "status": "PENDING_INDEPENDENT_HUMAN_LABELS",
            "total_sample_size": total_sample,
            "human_labeled_count": 0,
            "verified_task_precision_pct": None,
            "verified_commercial_pain_precision_pct": None,
            "verified_false_positive_rate_on_accepted_pct": None,
            "verified_false_negative_rate_on_rejected_pct": None,
            "note": (
                "No independent human ground-truth labels have been submitted yet. "
                "All classification counts in this report are automated heuristic outputs, not verified ground-truth precision/recall."
            ),
        }

    labeled_accepted = [
        r
        for r in labeled
        if r["heuristic_evaluation"]["heuristic_decision"] == "HEURISTIC_ACCEPTED"
    ]
    labeled_rejected = [
        r
        for r in labeled
        if r["heuristic_evaluation"]["heuristic_decision"] == "HEURISTIC_REJECTED"
    ]

    pain_in_acc = sum(
        1
        for r in labeled_accepted
        if r["human_ground_truth"]["human_pain_tier"] == "GENUINE_AUTOMATION_PAIN"
    )
    routine_in_acc = sum(
        1
        for r in labeled_accepted
        if r["human_ground_truth"]["human_pain_tier"] == "ROUTINE_JOB_RESPONSIBILITY"
    )
    fp_in_acc = sum(
        1
        for r in labeled_accepted
        if r["human_ground_truth"]["human_pain_tier"] == "NOT_A_WORKFLOW_FALSE_POSITIVE"
    )

    fn_in_rej = sum(
        1
        for r in labeled_rejected
        if r["human_ground_truth"]["human_pain_tier"] == "GENUINE_AUTOMATION_PAIN"
    )

    acc_denom = len(labeled_accepted)
    rej_denom = len(labeled_rejected)

    return {
        "status": "PARTIAL_OR_COMPLETE_HUMAN_LABELS" if len(labeled) < total_sample else "COMPLETE_HUMAN_LABELS",
        "total_sample_size": total_sample,
        "human_labeled_count": len(labeled),
        "human_labeled_accepted_count": acc_denom,
        "human_labeled_rejected_count": rej_denom,
        "verified_task_precision_pct": (
            round((pain_in_acc + routine_in_acc) / acc_denom * 100.0, 1) if acc_denom else None
        ),
        "verified_commercial_pain_precision_pct": (
            round(pain_in_acc / acc_denom * 100.0, 1) if acc_denom else None
        ),
        "verified_false_positive_rate_on_accepted_pct": (
            round(fp_in_acc / acc_denom * 100.0, 1) if acc_denom else None
        ),
        "verified_false_negative_rate_on_rejected_pct": (
            round(fn_in_rej / rej_denom * 100.0, 1) if rej_denom else None
        ),
    }


def export_evaluation_sample_files(
    records: list[dict[str, Any]],
    json_path: Path = DEFAULT_SAMPLE_JSON,
    csv_path: Path = DEFAULT_SAMPLE_CSV,
    seed: int = DEFAULT_SEED,
) -> dict[str, Any]:
    """Writes the reproducible evaluation sample to both JSON and CSV worksheet formats."""
    json_path.parent.mkdir(parents=True, exist_ok=True)
    csv_path.parent.mkdir(parents=True, exist_ok=True)

    payload = {
        "sampling_seed": seed,
        "instructions_path": "docs/LABELING_GUIDELINES.md",
        "ground_truth_metrics": compute_ground_truth_metrics(records),
        "sample_records": records,
    }
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)

    fieldnames = [
        "sample_id",
        "company_name",
        "job_title",
        "source_url",
        "exact_evidence",
        "heuristic_decision",
        "heuristic_workflow_category",
        "heuristic_rejection_code",
        "heuristic_pain_tier_guess",
        "HUMAN_PAIN_TIER (Fill: GENUINE_AUTOMATION_PAIN | ROUTINE_JOB_RESPONSIBILITY | NOT_A_WORKFLOW_FALSE_POSITIVE)",
        "HUMAN_BUYING_INTENT (Fill: EXPLICIT_EXTERNAL_INTENT | INTERNAL_BUILD_OR_HIRE_ONLY | NONE)",
        "HUMAN_AGENCY_FIT (Fill: HIGH_FIT | LOW_FIT | NO_FIT)",
        "REVIEWER_ID",
        "REVIEWER_NOTES",
    ]
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in records:
            h = r["heuristic_evaluation"]
            g = r["human_ground_truth"]
            writer.writerow(
                {
                    "sample_id": r["sample_id"],
                    "company_name": r["company_name"],
                    "job_title": r["job_title"],
                    "source_url": r["source_url"],
                    "exact_evidence": r["exact_evidence"],
                    "heuristic_decision": h["heuristic_decision"],
                    "heuristic_workflow_category": h["heuristic_workflow_category"],
                    "heuristic_rejection_code": h["heuristic_rejection_code"] or "",
                    "heuristic_pain_tier_guess": h["heuristic_pain_tier_guess"],
                    "HUMAN_PAIN_TIER (Fill: GENUINE_AUTOMATION_PAIN | ROUTINE_JOB_RESPONSIBILITY | NOT_A_WORKFLOW_FALSE_POSITIVE)": g["human_pain_tier"] or "",
                    "HUMAN_BUYING_INTENT (Fill: EXPLICIT_EXTERNAL_INTENT | INTERNAL_BUILD_OR_HIRE_ONLY | NONE)": g["human_buying_intent"] if "human_buying_intent" in g else (g["human_buying_or_outsourcing_intent"] or ""),
                    "HUMAN_AGENCY_FIT (Fill: HIGH_FIT | LOW_FIT | NO_FIT)": g["human_agency_fit"] or "",
                    "REVIEWER_ID": g["reviewer_id"] or "",
                    "REVIEWER_NOTES": g["reviewer_notes"] or "",
                }
            )

    return payload


if __name__ == "__main__":
    acc, rej = collect_all_candidates_from_boards()
    sample = build_reproducible_evaluation_sample(acc, rej)
    out = export_evaluation_sample_files(sample)
    print(f"Exported {len(sample)} reproducible evaluation records (seed={DEFAULT_SEED}).")
    print("Ground truth metrics status:", out["ground_truth_metrics"]["status"])
