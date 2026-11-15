"""Greenhouse Public Job Board API Fetcher."""

import json
import re
import urllib.request
from urllib.error import HTTPError, URLError

from src.models import JobPosting

GREENHOUSE_API_TEMPLATE = "https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs?content=true"
USER_AGENT = "ManualOpsRadar/0.1.0"
BOARD_TOKEN_PATTERN = re.compile(r"^[a-zA-Z0-9_-]{1,64}$")
DEFAULT_TIMEOUT_SECONDS = 15
MAX_TIMEOUT_SECONDS = 60
MAX_RESPONSE_BYTES = 10 * 1024 * 1024  # 10 MiB hard cap against oversized responses


def validate_board_token(board_token: str) -> str:
    """
    Validates that a Greenhouse board token contains only safe slug characters.
    Prevents URL path injection, query-parameter tampering, and SSRF-style redirects.
    """
    if not isinstance(board_token, str):
        raise ValueError("board_token must be a string")
    cleaned = board_token.strip()
    if not BOARD_TOKEN_PATTERN.fullmatch(cleaned):
        raise ValueError(
            "Invalid board_token: must be 1-64 characters matching ^[a-zA-Z0-9_-]+$"
        )
    return cleaned


def extract_department_name(job_payload: dict) -> str:
    """Safely extracts the primary department name from a Greenhouse job payload."""
    departments = job_payload.get("departments")
    if isinstance(departments, list) and departments:
        first_dept = departments[0]
        if isinstance(first_dept, dict):
            return str(first_dept.get("name") or "Unspecified")
    return "Unspecified"


def extract_location_name(job_payload: dict) -> str:
    """Safely extracts the location string from a Greenhouse job payload."""
    loc = job_payload.get("location")
    if isinstance(loc, dict):
        return str(loc.get("name") or "Unspecified")
    return "Unspecified"


def fetch_board_jobs(
    board_token: str,
    default_company_name: str,
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
    max_response_bytes: int = MAX_RESPONSE_BYTES,
) -> tuple[list[JobPosting], int | None, str | None]:
    """
    Fetches public job postings for a given Greenhouse board_token.

    Enforces:
    - Strict board_token slug validation (`^[a-zA-Z0-9_-]{1,64}$`)
    - Bounded request timeout (1..60 seconds)
    - Hard response size limit (`max_response_bytes`, default 10 MiB)

    Returns:
        (jobs_list, http_status_code, error_message)
    """
    try:
        safe_token = validate_board_token(board_token)
    except ValueError as exc:
        return [], None, str(exc)

    if timeout_seconds <= 0:
        return [], None, "Invalid timeout_seconds: must be positive"
    bounded_timeout = min(int(timeout_seconds), MAX_TIMEOUT_SECONDS)

    if max_response_bytes <= 0:
        return [], None, "Invalid max_response_bytes: must be positive"

    url = GREENHOUSE_API_TEMPLATE.format(board_token=safe_token)
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})

    try:
        with urllib.request.urlopen(req, timeout=bounded_timeout) as response:
            status_code = getattr(response, "status", 200)
            raw_bytes = response.read(max_response_bytes + 1)
            if len(raw_bytes) > max_response_bytes:
                return (
                    [],
                    status_code,
                    f"ResponseTooLargeError: payload exceeded {max_response_bytes} bytes limit",
                )
            payload = json.loads(raw_bytes.decode("utf-8"))
    except HTTPError as exc:
        return [], exc.code, f"HTTPError {exc.code}: {exc.reason}"
    except URLError as exc:
        return [], None, f"URLError: {exc.reason}"
    except TimeoutError:
        return [], None, f"TimeoutError after {bounded_timeout}s"
    except Exception as exc:  # noqa: BLE001
        return [], None, f"Unexpected error: {exc}"

    if not isinstance(payload, dict):
        return [], status_code, "Invalid payload format: root JSON is not an object"

    raw_jobs = payload.get("jobs", [])
    if not isinstance(raw_jobs, list):
        return [], status_code, "Invalid payload format: 'jobs' is not a list"

    postings: list[JobPosting] = []
    for item in raw_jobs:
        if not isinstance(item, dict):
            continue
        company = str(item.get("company_name") or default_company_name)
        postings.append(
            JobPosting(
                board_token=safe_token,
                company_name=company,
                job_id=int(item.get("id", 0)),
                job_title=str(item.get("title") or "Untitled Role").strip(),
                source_url=str(item.get("absolute_url") or "").strip(),
                updated_at=item.get("updated_at"),
                first_published=item.get("first_published"),
                location=extract_location_name(item),
                department=extract_department_name(item),
                raw_content=str(item.get("content") or ""),
            )
        )

    return postings, status_code, None
