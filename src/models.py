"""Data models for ManualOps Radar Phase 1 Validation."""

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class JobPosting:
    """Represents a single public job posting retrieved from the Greenhouse Job Board API."""

    board_token: str
    company_name: str
    job_id: int
    job_title: str
    source_url: str
    updated_at: str | None
    first_published: str | None
    location: str
    department: str
    raw_content: str


@dataclass
class EvaluatedCandidate:
    """Represents a candidate sentence evaluated by the deterministic rules engine."""

    board_token: str
    company_name: str
    job_id: int
    job_title: str
    department: str
    location: str
    source_url: str
    first_published: str | None
    updated_at: str | None
    workflow_category: str
    exact_evidence: str
    matched_trigger: str
    classification: str  # "VALID_SIGNAL" or "REJECTED_FALSE_POSITIVE"
    signal_subtype: str  # "DIRECT_MANUAL_EXECUTION", "INTERNAL_AUTOMATION_MANDATE", or "NONE"
    rejection_reason: str | None  # e.g., "GENERAL_SOFTWARE_SKILL", "VERB_EXCEL_OR_IDIOM", etc.
    explanation: str
    buying_intent_assessment: str
    uncertainty_factors: list[str] = field(default_factory=list)
    is_regional_duplicate: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class BoardScanResult:
    """Summary of scanning a single Greenhouse board."""

    board_token: str
    company_name: str
    http_status: int | None
    jobs_fetched: int
    candidate_sentences_evaluated: int
    valid_signals_count: int
    unique_valid_signals_count: int
    rejected_count: int
    error_message: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
