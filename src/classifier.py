"""Deterministic rules engine for ManualOps Radar Phase 1 Validation.

Distinguishes clearly between:
1. General software skills & qualifications mentioned in job descriptions (REJECTED: GENERAL_SOFTWARE_SKILL)
2. Idioms, product pitches, or engineering/IT builds (REJECTED: specific reason)
3. Explicit evidence of repetitive manual workflows (VALID_SIGNAL)
4. Actual buying intent (Never inferred from hiring alone; explicitly assessed per signal)
"""

import re
from src.models import EvaluatedCandidate, JobPosting

# ---------------------------------------------------------------------------
# Stage 1: Broad Candidate Trigger Patterns (5 Target Categories)
# ---------------------------------------------------------------------------
CATEGORY_TRIGGERS: list[tuple[str, re.Pattern[str]]] = [
    (
        "Data Entry",
        re.compile(
            r"\b(?:data\s+entry|manual\s+journal\s+entr(?:y|ies)|manual\s+invoicing|"
            r"enter(?:ing)?\s+[^.]{1,60}\bmanually|manual(?:ly)?\s+enter(?:ing)?|"
            r"key(?:ing)?\s+in\s+(?:data|billing|invoices?|records?|adjustments?))\b",
            flags=re.IGNORECASE,
        ),
    ),
    (
        "Reconciliation",
        re.compile(
            r"\b(?:reconcil(?:e|es|ed|ing|iation|iations))\b",
            flags=re.IGNORECASE,
        ),
    ),
    (
        "Spreadsheets",
        re.compile(
            r"\b(?:excel|google\s+sheets?|spreadsheets?|vlookup\w*|pivot\s+tables?)\b",
            flags=re.IGNORECASE,
        ),
    ),
    (
        "CRM Operations",
        re.compile(
            r"\b(?:salesforce|hubspot|sfdc|crm)\b",
            flags=re.IGNORECASE,
        ),
    ),
    (
        "Reporting",
        re.compile(
            r"\b(?:manual\s+report(?:s|ing)?|"
            r"reporting\s+(?:deliverables|packages|overhead|processes|cadence|packs|cycles|skills)|"
            r"(?:weekly|monthly|quarterly|internal\s+management|executive|financial|regulatory)\s+reporting|"
            r"reduce\s+manual\s+reporting|automated\s+reports\s+and\s+dashboards|"
            r"automate\s+recurring,\s+manual\s+steps\s+in\s+the\s+close\s+process|"
            r"manual,\s+repetitive\s+tasks\s+across\s+[^.]{1,40}\breporting|"
            r"reporting\s+to\s+(?:the|our|a)\b)\b",
            flags=re.IGNORECASE,
        ),
    ),
]

# ---------------------------------------------------------------------------
# Stage 2: Automated False-Positive Filters
# ---------------------------------------------------------------------------

# 1. Verb "excel" or non-operational idioms ("reporting to the VP", "reconciling perspectives")
REAL_SPREADSHEET_NOUN_PATTERN = re.compile(
    r"\b(?:ms\s+excel|microsoft\s+excel|google\s+sheets?|spreadsheets?|vlookup\w*|pivot\s+tables?|"
    r"excel\s+(?:or|and|/)\s+google\s+sheets?|google\s+sheets?\s+(?:or|and|/)\s+excel|"
    r"excel\s+(?:models?|modeling|spreadsheets?|trackers?|files?|macros?|skills?|proficiency|formulas?)|"
    r"(?:in|with|using|within)\s+excel)\b",
    flags=re.IGNORECASE,
)

METAPHORICAL_RECONCILE_PATTERN = re.compile(
    r"\breconcil(?:e|ing)\s+(?:multiple\s+)?(?:stakeholder|competing|different|imperfect|ambiguous|perspectives|priorities|views\s+in\s+writing)",
    flags=re.IGNORECASE,
)

ORG_REPORTING_LINE_PATTERN = re.compile(
    r"\breporting\s+(?:directly\s+)?to\s+(?:the|our|a|an)\b",
    flags=re.IGNORECASE,
)

# 2. Product Pitch / Customer-Facing Feature Descriptions
PRODUCT_PITCH_PATTERN = re.compile(
    r"\b(?:our\s+platform\s+computes|save\s+them\s+days\s+of|saving\s+them\s+hours\s+of|"
    r"stripe[’']s\s+revenue\s+&\s+financial\s+management\s+group\s+is\s+building\s+new\s+products|"
    r"right\s+now\s+this\s+includes\s+products\s+like\s+billing,\s+invoicing,\s+revenue\s+recognition,\s+reconciliation|"
    r"we[’']re\s+looking\s+for\s+a\s+product\s+manager\s+to\s+build|"
    r"how\s+global\s+businesses\s+and\s+platforms\s+manage\s+currencies|"
    r"finance\s+teams\s+must\s+decide\s+what\s+to\s+hold|"
    r"we[’']re\s+hiring\s+seasoned\s+engineers\s+to\s+join\s+our\s+teams\s+that\s+work\s+on\s+the\s+financial\s+backbone|"
    r"financial\s+data\s+is\s+the\s+system\s+of\s+record\s+for\s+the\s+money\s+itself|"
    r"help\s+customers\s+automate|for\s+our\s+customers\s+by\s+eliminating)\b",
    flags=re.IGNORECASE,
)

# 3. Core Engineering / Infrastructure / Security / IT Controls Build
ENGINEERING_JOB_TITLE_PATTERN = re.compile(
    r"\b(?:software\s+engineer|staff\s+engineer|principal\s+engineer|backend\s+engineer|"
    r"full\s+stack\s+engineer|frontend\s+engineer|site\s+reliability\s+engineer|"
    r"security\s+engineer|enterprise\s+systems\s+developer|director\s+of\s+engineering|"
    r"engineering\s+manager|it\s+internal\s+controls|internal\s+auditor|internal\s+audit)\b",
    flags=re.IGNORECASE,
)

ENGINEERING_OR_ITGC_BUILD_PATTERN = re.compile(
    r"\b(?:build\s+reconciliation\s+and\s+anomaly\s+detection|"
    r"build\s+reconciliation\s+at\s+gusto|"
    r"improve\s+reconciliation,\s+observability,\s+alerting,\s+slos|"
    r"maintain\s+and\s+improve\s+integrations\s+between\s+our\s+tools,\s+salesforce|"
    r"building\s+and\s+managing\s+integrations\s+with\s+leading\s+ecommerce,\s+crm|"
    r"developing\s+and\s+maintaining\s+a\s+set\s+of\s+connectors\s+and\s+integrations|"
    r"scalable\s+apex\s+solutions\s+on\s+the\s+salesforce\s+platform|"
    r"apply\s+salesforce\s+platform\s+architecture|"
    r"working\s+knowledge\s+of\s+apis\s+and\s+how\s+sales\s+tools\s+connect\s+to\s+crm|"
    r"scale\s+it\s+general\s+controls\s+\(itgcs\)|"
    r"segregation\s+of\s+duties\s+\(sod\)\s+design\s+and\s+remediation\s+across\s+erp,\s+hris,\s+and\s+crm|"
    r"drive\s+sod\s+strategy\s+across\s+erp,\s+hris,\s+and\s+crm|"
    r"endpoint\s+validation,\s+eval\s+runs,\s+catalog\s+and\s+pricing\s+reconciliation|"
    r"diagnose\s+and\s+fix\s+the\s+data\s+issues,\s+jurisdiction\s+mapping,\s+tax\s+id\s+reconciliation|"
    r"evaluation\s+and\s+testing\s+of\s+governance,\s+risk\s+management,\s+internal\s+controls)\b",
    flags=re.IGNORECASE,
)

# 4. General Software Skills / Candidate Qualifications (No explicit recurring manual workflow)
GENERAL_SKILL_PATTERN = re.compile(
    r"(?:^\s*(?:proficiency|proficient|experience|familiar(?:ity)?|comfortable|comfort|"
    r"strong|advanced?|basic|intermediate|knowledge|solid\s+understanding|deep\s+understanding|"
    r"ability\s+to\s+quickly\s+learn|ability\s+to\s+manage|ability\s+to\s+work\s+with|"
    r"proven\s+ability\s+to|sql\s+and\s+data:\s+strong\s+sql|"
    r"is\s+numerate\s+and\s+confident|data\s+analytics\s*\(|crm\s+knowledge|track\s+record\s+of|"
    r"demonstrated\s+ability\s+to|you\s+bring\s+strong|deeply\s+data-driven)\b|"
    r"\b(?:\d+\+?\s+years?\s+of\s+experience|"
    r"is\s+a\s+(?:great\s+)?plus|preferred|required|skills\s+in\s+excel|"
    r"skills,\s+including\s+(?:vlookups?|proficiency\s+in\s+excel|comfort\s+using\s+spreadsheets)|"
    r"proficiency\s+(?:in|with)\s+(?:using\s+)?(?:salesforce|excel|google\s+sheets|structured\s+query\s+language|hr\s+software)|"
    r"experience\s+(?:with|in|using|working)\s+(?:outreach|saas/cloud|salesforce|google\s+sheets|customer\s+support\s+platforms|usage-based\s+billing|a\s+human\s+resources\s+information\s+system|day-to-day\s+with\s+marketing\s+automation)|"
    r"familiar(?:ity)?\s+with\s+(?:accounting\s+and\s+financial\s+reconciliation|reconciliation,\s+idempotency|saas/cloud\s+and\s+salesforce)|"
    r"exposure\s+to\s+financial\s+systems,\s+deal\s+desk,\s+or\s+procurement|"
    r"expertise\s*--\s*deep\s+experience\s+working\s+with\s+salesforce|"
    r"skilled\s+in\s+excel\s+or\s+google\s+sheets)\b)",
    flags=re.IGNORECASE,
)

# ---------------------------------------------------------------------------
# Stage 3: Category-Specific Explicit Manual / Operational Workflow Patterns
# ---------------------------------------------------------------------------

CATEGORY_WORKFLOW_PATTERNS: dict[str, re.Pattern[str]] = {
    "Data Entry": re.compile(
        r"\b(?:careful\s+data\s+entry|manual\s+data\s+entry|manual\s+journal\s+entr(?:y|ies)|"
        r"enter(?:ing)?\s+[^.]{1,60}\bmanually|key(?:ing)?\s+in\s+(?:data|billing|invoices?|records?|adjustments?))\b",
        flags=re.IGNORECASE,
    ),
    "Reconciliation": re.compile(
        r"\b(?:(?:prepare|perform|own|drive|lead|oversee|execute|manage|support|automate|speed\s+up)\b[^.]{0,120}\b"
        r"(?:account\s+reconciliations?|balance[- ]sheet\s+reconciliations?|reconciliations?|"
        r"billing\s+reconciliation|reconcil(?:e|ing)\s+(?:vendor\s+accounts|data|settlement\s+files|against\s+crm|discrepancies))|"
        r"reconcil(?:e|ing)\s+(?:vendor\s+accounts|data|settlement\s+files|against\s+crm\s+and\s+billing\s+data|discrepancies\s+across\s+systems)|"
        r"reconciliation\s+of\s+attendee\s+and\s+non-attendee\s+data|"
        r"automated\s+reconciliation\s+workflows|"
        r"quality-control\s+and\s+reconciliation\s+checks|"
        r"partner\s+with\s+[^.]{1,60}\bon\s+accurate\s+reporting,\s+billing\s+reconciliation)\b",
        flags=re.IGNORECASE,
    ),
    "Spreadsheets": re.compile(
        r"\b(?:improve\s+recurring\s+workflows\s+using\s+spreadsheets|"
        r"analyze\s+large\s+financial\s+and\s+operational\s+datasets\s+using\s+google\s+sheets|"
        r"(?:maintain|consolidate|update|prepare)\s+[^.]{0,60}\b(?:spreadsheets?|excel\s+trackers?|google\s+sheets?)|"
        r"manage\s+and\s+maintain\s+centralized\s+tools\s+\(including\s+spreadsheet\s+models)\b",
        flags=re.IGNORECASE,
    ),
    "CRM Operations": re.compile(
        r"\b(?:(?:maintain|keep)\s+(?:accurate|up-to-date|organized|client\s+interaction\s+logs)[^.]{0,80}\b(?:in\s+(?:the\s+)?(?:salesforce|crm|hubspot)|crm\s+(?:records|data|and\s+sales\s+activity))|"
        r"keep\s+crm\s+activity\s+and\s+pipeline\s+current|"
        r"update\s+(?:salesforce|crm|hubspot)\s+with\s+detailed\s+(?:call\s+)?notes|"
        r"manage,\s+track,\s+and\s+(?:accurately\s+)?report\s+(?:on\s+)?all\s+(?:prospecting\s+)?activities\s+and\s+(?:pipeline|results)\s+(?:in|using)\s+salesforce|"
        r"use\s+salesforce\s+and\s+our\s+partner\s+management\s+tools\s+to\s+track\s+pipeline|"
        r"pull\s+and\s+analyze\s+salesforce\s+and\s+lms\s+data\s+to\s+track\s+performance)\b",
        flags=re.IGNORECASE,
    ),
    "Reporting": re.compile(
        r"\b(?:producing\s+internal\s+management\s+reporting|"
        r"executive\s+reporting\s+packages|financial\s+reporting\s+deliverables|"
        r"reduce\s+manual\s+reporting\s+overhead|"
        r"develop\s+scalable,\s+automated\s+reports\s+and\s+dashboards\s+[^.]{0,80}\breduce\s+manual\s+effort|"
        r"identify\s+manual,\s+repetitive\s+tasks\s+across\s+[^.]{0,40}\breporting|"
        r"automate\s+recurring,\s+manual\s+steps\s+in\s+the\s+close\s+process)\b",
        flags=re.IGNORECASE,
    ),
}

INTERNAL_AUTOMATION_MANDATE_PATTERN = re.compile(
    r"\b(?:automate|automation|automated|streamline|reduce\s+manual|replace\s+manual|"
    r"ai[- ]driven|ai\s+tools|agentic|speed\s+up\s+reconciliations|"
    r"centralized\s+tools\s+\(including\s+spreadsheet\s+models)\b",
    flags=re.IGNORECASE,
)


def detect_category_and_trigger(statement: str) -> tuple[str, str] | None:
    """Returns (workflow_category, matched_substring) if the statement triggers any target category."""
    for category, pattern in CATEGORY_TRIGGERS:
        match = pattern.search(statement)
        if match:
            return category, match.group(0)
    return None


def classify_statement(job: JobPosting, statement: str) -> EvaluatedCandidate | None:
    """
    Evaluates a single statement from a job description.
    Returns None if the statement does not mention any target domain keywords.
    Otherwise returns an EvaluatedCandidate (either VALID_SIGNAL or REJECTED_FALSE_POSITIVE).
    """
    detected = detect_category_and_trigger(statement)
    if not detected:
        return None

    category, trigger_text = detected

    # Check 1A: If triggered by "Spreadsheets" via the word "excel", verify it is actually spreadsheet-related
    if category == "Spreadsheets" and not REAL_SPREADSHEET_NOUN_PATTERN.search(statement):
        return _build_rejected(
            job=job,
            category=category,
            statement=statement,
            trigger=trigger_text,
            reason="VERB_EXCEL_OR_IDIOM",
            explanation=(
                "Uses the word 'excel' as an English verb (e.g., 'excel in a fast-paced environment') "
                "rather than referring to Microsoft Excel or spreadsheets."
            ),
        )

    # Check 1B: Organizational reporting line ("Reporting to the Director of...")
    if ORG_REPORTING_LINE_PATTERN.search(statement) and not re.search(
        r"\b(?:reconcil\w+|manual\s+report\w*|spreadsheets?|data\s+entry)\b", statement, re.I
    ):
        return _build_rejected(
            job=job,
            category=category,
            statement=statement,
            trigger=trigger_text,
            reason="VERB_EXCEL_OR_IDIOM",
            explanation=(
                "Refers to organizational hierarchy ('Reporting to...') rather than operational report preparation."
            ),
        )

    # Check 1C: Metaphorical reconciliation ("reconciling stakeholder perspectives")
    if category == "Reconciliation" and METAPHORICAL_RECONCILE_PATTERN.search(statement):
        return _build_rejected(
            job=job,
            category=category,
            statement=statement,
            trigger=trigger_text,
            reason="VERB_EXCEL_OR_IDIOM",
            explanation=(
                "Uses 'reconcile' figuratively (reconciling stakeholder viewpoints or ambiguity) "
                "rather than financial or data reconciliation."
            ),
        )

    # Check 2: Product Pitch / Customer-facing marketing copy
    if PRODUCT_PITCH_PATTERN.search(statement):
        return _build_rejected(
            job=job,
            category=category,
            statement=statement,
            trigger=trigger_text,
            reason="PRODUCT_PITCH_OR_CUSTOMER_FEATURE",
            explanation=(
                "Describes the company's commercial software product or customer pain points, "
                "not an internal manual workflow performed by this role."
            ),
        )

    # Check 3: Core Software / Infrastructure / Security / ITGC Engineering Build
    if ENGINEERING_OR_ITGC_BUILD_PATTERN.search(statement) or (
        ENGINEERING_JOB_TITLE_PATTERN.search(job.job_title)
        and category != "Data Entry"
    ):
        return _build_rejected(
            job=job,
            category=category,
            statement=statement,
            trigger=trigger_text,
            reason="ENGINEERING_INFRA_OR_SYSTEMS_BUILD",
            explanation=(
                "Describes software engineering, enterprise system integrations, or IT security/audit controls "
                f"for an engineering/audit role ('{job.job_title}') rather than repetitive manual business operations."
            ),
        )

    # Check 4: General Software Skills / Qualifications
    if GENERAL_SKILL_PATTERN.search(statement):
        return _build_rejected(
            job=job,
            category=category,
            statement=statement,
            trigger=trigger_text,
            reason="GENERAL_SOFTWARE_SKILL",
            explanation=(
                "Lists tool proficiency, familiarity, or prior experience (e.g., Excel, Salesforce, CRM, reporting skills) "
                "as a candidate qualification without describing a repetitive manual workflow."
            ),
        )

    # Check 5: Category-specific explicit operational action/workflow evidence
    workflow_pattern = CATEGORY_WORKFLOW_PATTERNS.get(category)
    if workflow_pattern and workflow_pattern.search(statement):
        is_automation_mandate = bool(INTERNAL_AUTOMATION_MANDATE_PATTERN.search(statement))
        subtype = (
            "INTERNAL_AUTOMATION_MANDATE"
            if is_automation_mandate
            else "DIRECT_MANUAL_EXECUTION"
        )
        if is_automation_mandate:
            explanation = (
                "Explicitly confirms an existing manual/recurring workflow in this domain AND tasks the new hire "
                "with automating or streamlining it internally."
            )
            buying_intent = (
                "NO DIRECT BUYING INTENT: While this confirms internal process pain, the company is actively hiring "
                "internal talent (and referencing internal AI/ERP tooling) to automate this workflow in-house."
            )
            uncertainties = [
                "Role is explicitly chartered to build/drive internal automation using existing AI or ERP tools.",
                "Internal build mandate often competes directly with purchasing third-party point solutions.",
                "Job posting proves workflow pain exists, NOT external software budget or buying intent.",
            ]
        else:
            explanation = (
                "Explicitly describes recurring operational execution (e.g., reconciliations, manual data/journal entry, "
                "periodic reporting deliverables, or ongoing CRM record maintenance)."
            )
            buying_intent = (
                "NO DIRECT BUYING INTENT: Hiring a human operator/analyst to execute this recurring process indicates "
                "the team currently addresses the workload via headcount rather than external software procurement."
            )
            uncertainties = [
                "Company allocated headcount budget to perform the process, which may reduce near-term software urgency.",
                "Some manual steps (e.g., monthly close sign-offs or sales call notes) require human judgment or audit compliance.",
                "Job posting proves process existence, NOT buying intent.",
            ]

        return EvaluatedCandidate(
            board_token=job.board_token,
            company_name=job.company_name,
            job_id=job.job_id,
            job_title=job.job_title,
            department=job.department,
            location=job.location,
            source_url=job.source_url,
            first_published=job.first_published,
            updated_at=job.updated_at,
            workflow_category=category,
            exact_evidence=statement,
            matched_trigger=trigger_text,
            classification="VALID_SIGNAL",
            signal_subtype=subtype,
            rejection_reason=None,
            explanation=explanation,
            buying_intent_assessment=buying_intent,
            uncertainty_factors=uncertainties,
        )

    # Fallback: Generic mention of a tool/keyword without manual workflow evidence
    return _build_rejected(
        job=job,
        category=category,
        statement=statement,
        trigger=trigger_text,
        reason="GENERIC_MENTION_WITHOUT_MANUAL_WORKFLOW",
        explanation=(
            "Mentions a target tool or keyword in passing (e.g., list of enterprise tools or cross-functional context) "
            "without explicit evidence of a repetitive manual workflow."
        ),
    )


def _build_rejected(
    job: JobPosting,
    category: str,
    statement: str,
    trigger: str,
    reason: str,
    explanation: str,
) -> EvaluatedCandidate:
    return EvaluatedCandidate(
        board_token=job.board_token,
        company_name=job.company_name,
        job_id=job.job_id,
        job_title=job.job_title,
        department=job.department,
        location=job.location,
        source_url=job.source_url,
        first_published=job.first_published,
        updated_at=job.updated_at,
        workflow_category=category,
        exact_evidence=statement,
        matched_trigger=trigger,
        classification="REJECTED_FALSE_POSITIVE",
        signal_subtype="NONE",
        rejection_reason=reason,
        explanation=explanation,
        buying_intent_assessment="NONE (Rejected candidate match; no operational workflow signal).",
        uncertainty_factors=[],
    )
