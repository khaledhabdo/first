"""Greenhouse Public Job Board API Fetcher."""

import json
import urllib.request
from urllib.error import HTTPError, URLError

from src.models import JobPosting

GREENHOUSE_API_TEMPLATE = "https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs?content=true"
USER_AGENT = "ManualOpsRadar-Phase1Validation/1.0"


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
    timeout_seconds: int = 20,
) -> tuple[list[JobPosting], int | None, str | None]:
    """
    Fetches public job postings for a given Greenhouse board_token.

    Returns:
        (jobs_list, http_status_code, error_message)
    """
    url = GREENHOUSE_API_TEMPLATE.format(board_token=board_token)
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})

    try:
        with urllib.request.urlopen(req, timeout=timeout_seconds) as response:
            status_code = getattr(response, "status", 200)
            payload = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        return [], exc.code, f"HTTPError {exc.code}: {exc.reason}"
    except URLError as exc:
        return [], None, f"URLError: {exc.reason}"
    except TimeoutError:
        return [], None, f"TimeoutError after {timeout_seconds}s"
    except Exception as exc:  # noqa: BLE001
        return [], None, f"Unexpected error: {exc}"

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
                board_token=board_token,
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
