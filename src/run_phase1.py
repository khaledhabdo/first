"""Main runner for ManualOps Radar Phase 1: Real Data Validation."""

from collections import Counter, defaultdict
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any

from src.audit_phase1 import (
    classify_commercial_signal_quality,
    normalize_workflow_signature,
)
from src.classifier import classify_statement
from src.fetcher import fetch_board_jobs
from src.models import BoardScanResult, EvaluatedCandidate
from src.parser import extract_candidate_statements
from src.prepare_eval_sample import (
    build_reproducible_evaluation_sample,
    compute_ground_truth_metrics,
    export_evaluation_sample_files,
)
from src.renderer import render_phase1_html_report

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CONFIG_PATH = PROJECT_ROOT / "config" / "boards_phase1.json"
DEFAULT_JSON_OUT = PROJECT_ROOT / "data" / "phase1_results.json"
DEFAULT_HTML_OUT = PROJECT_ROOT / "reports" / "phase1_validation_report.html"


def select_representative_rejections(
    rejected_list: list[EvaluatedCandidate],
    max_per_reason: int = 15,
) -> list[dict[str, Any]]:
    """
    Selects a diverse, deduplicated sample of heuristic-rejected candidates across all
    rejection codes and companies for display in the HTML audit table.
    """
    by_reason: dict[str, list[EvaluatedCandidate]] = defaultdict(list)
    seen_evidence: set[tuple[str, str]] = set()

    for item in rejected_list:
        key = (item.board_token, item.exact_evidence.lower())
        if key in seen_evidence:
            continue
        seen_evidence.add(key)
        reason = item.rejection_reason or "UNKNOWN"
        if len(by_reason[reason]) < max_per_reason:
            by_reason[reason].append(item)

    ordered_reasons = [
        "GENERAL_SOFTWARE_SKILL",
        "VERB_EXCEL_OR_IDIOM",
        "PRODUCT_PITCH_OR_CUSTOMER_FEATURE",
        "ENGINEERING_INFRA_OR_SYSTEMS_BUILD",
        "GENERIC_MENTION_WITHOUT_MANUAL_WORKFLOW",
    ]
    selected: list[dict[str, Any]] = []
    for reason in ordered_reasons:
        for candidate in by_reason.get(reason, []):
            selected.append(candidate.to_dict())
    return selected


def run_validation(
    config_path: Path = DEFAULT_CONFIG_PATH,
    json_out_path: Path = DEFAULT_JSON_OUT,
    html_out_path: Path = DEFAULT_HTML_OUT,
) -> dict[str, Any]:
    """Executes Phase 1/1.5 real data validation across the 5 verified Greenhouse boards."""
    with open(config_path, encoding="utf-8") as f:
        config = json.load(f)

    boards_cfg = config.get("boards", [])
    board_results: list[BoardScanResult] = []
    all_valid: list[EvaluatedCandidate] = []
    all_rejected: list[EvaluatedCandidate] = []
    api_errors: list[dict[str, Any]] = []

    for board_entry in boards_cfg:
        token = board_entry["board_token"]
        company_name = board_entry["company_name"]
        jobs, status_code, error_msg = fetch_board_jobs(token, company_name)

        if error_msg is not None:
            api_errors.append(
                {
                    "board_token": token,
                    "company_name": company_name,
                    "http_status": status_code,
                    "error": error_msg,
                }
            )

        board_valid: list[EvaluatedCandidate] = []
        board_rejected: list[EvaluatedCandidate] = []
        seen_board_valid_evidence: set[str] = set()

        for job in jobs:
            statements = extract_candidate_statements(job.raw_content)
            for stmt in statements:
                evaluated = classify_statement(job, stmt)
                if evaluated is None:
                    continue
                if evaluated.classification == "VALID_SIGNAL":
                    norm_ev = evaluated.exact_evidence.strip().lower()
                    if norm_ev in seen_board_valid_evidence:
                        evaluated.is_regional_duplicate = True
                    else:
                        seen_board_valid_evidence.add(norm_ev)
                    board_valid.append(evaluated)
                    all_valid.append(evaluated)
                else:
                    board_rejected.append(evaluated)
                    all_rejected.append(evaluated)

        board_results.append(
            BoardScanResult(
                board_token=token,
                company_name=company_name,
                http_status=status_code,
                jobs_fetched=len(jobs),
                candidate_sentences_evaluated=len(board_valid) + len(board_rejected),
                valid_signals_count=len(board_valid),
                unique_valid_signals_count=len(seen_board_valid_evidence),
                rejected_count=len(board_rejected),
                error_message=error_msg,
            )
        )

    total_jobs = sum(b.jobs_fetched for b in board_results)
    total_candidates = len(all_valid) + len(all_rejected)
    unique_valid_count = sum(1 for v in all_valid if not v.is_regional_duplicate)
    regional_dup_count = sum(1 for v in all_valid if v.is_regional_duplicate)
    heuristic_rejection_rate = (
        round((len(all_rejected) / total_candidates * 100.0), 1) if total_candidates else 0.0
    )

    valid_by_cat = dict(Counter(v.workflow_category for v in all_valid))
    valid_by_subtype = dict(Counter(v.signal_subtype for v in all_valid))
    rejected_by_reason = dict(Counter(str(r.rejection_reason) for r in all_rejected))

    # Dynamically compute heuristic company/workflow groupings and heuristic commercial tiers
    heuristic_clusters = {
        normalize_workflow_signature(v.to_dict()) for v in all_valid
    }
    heuristic_pain_tiers = dict(
        Counter(
            classify_commercial_signal_quality(v.to_dict())["audit_label"]
            for v in all_valid
        )
    )

    # Prepare reproducible evaluation sample with blank human_ground_truth fields
    eval_sample_records = build_reproducible_evaluation_sample(all_valid, all_rejected)
    export_evaluation_sample_files(eval_sample_records)
    ground_truth_eval = compute_ground_truth_metrics(eval_sample_records)

    report_payload: dict[str, Any] = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "phase": "Phase 1.5: Evaluation Integrity & Commercial Validation",
        "summary": {
            "boards_configured": len(boards_cfg),
            "boards_scanned": sum(1 for b in board_results if b.error_message is None),
            "api_errors_count": len(api_errors),
            "total_jobs_scanned": total_jobs,
            "total_candidates_evaluated": total_candidates,
            "valid_signals_count": len(all_valid),
            "unique_valid_signals_count": unique_valid_count,
            "regional_duplicates_count": regional_dup_count,
            "heuristic_workflow_clusters_count": len(heuristic_clusters),
            "heuristic_rejected_candidates_count": len(all_rejected),
            "heuristic_rejection_rate_pct": heuristic_rejection_rate,
            "valid_by_category": valid_by_cat,
            "valid_by_subtype": valid_by_subtype,
            "heuristic_pain_tier_breakdown": heuristic_pain_tiers,
            "rejected_by_reason": rejected_by_reason,
            "ground_truth_evaluation": ground_truth_eval,
        },
        "recommendation": {
            "verdict": "PIVOT_SEGMENT_BEFORE_BUILDING",
            "summary": (
                "Technical extraction is fast and free, but heuristic signal counts do not equal commercial demand. "
                "Wait for independent human labeling on the 50-row evaluation sample and validate whether small "
                "automation agencies will pay for mid-market operational workflow briefs before building Phase 2."
            ),
        },
        "boards": [b.to_dict() for b in board_results],
        "api_errors": api_errors,
        "valid_signals": [v.to_dict() for v in all_valid],
        "rejected_samples": select_representative_rejections(all_rejected, max_per_reason=16),
    }

    json_out_path.parent.mkdir(parents=True, exist_ok=True)
    html_out_path.parent.mkdir(parents=True, exist_ok=True)

    with open(json_out_path, "w", encoding="utf-8") as f:
        json.dump(report_payload, f, indent=2, ensure_ascii=False)

    html_content = render_phase1_html_report(report_payload)
    with open(html_out_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    return report_payload


if __name__ == "__main__":
    result = run_validation()
    s = result["summary"]
    print(f"Phase 1.5 Validation Complete at {result['generated_at']}")
    print(f"  Boards scanned: {s['boards_scanned']}/{s['boards_configured']} (API errors: {s['api_errors_count']})")
    print(f"  Total jobs scanned: {s['total_jobs_scanned']}")
    print(f"  Candidate statements evaluated: {s['total_candidates_evaluated']}")
    print(f"  Heuristic accepted signals: {s['valid_signals_count']} ({s['unique_valid_signals_count']} unique strings, {s['heuristic_workflow_clusters_count']} heuristic clusters)")
    print(f"  Heuristic rejected candidates: {s['heuristic_rejected_candidates_count']} ({s['heuristic_rejection_rate_pct']}% heuristic filter rejection rate)")
    print(f"  Ground-truth human evaluation status: {s['ground_truth_evaluation']['status']}")
    print(f"  Recommendation: {result['recommendation']['verdict']}")

