"""Static HTML report generator for ManualOps Radar Phase 1 Validation."""

import html
from typing import Any


def render_phase1_html_report(report_data: dict[str, Any]) -> str:
    """
    Generates a self-contained, human-readable HTML report containing:
    - Exact scan metrics (jobs scanned, valid signals, false positives, errors)
    - Distinction between General Software Skills, Explicit Manual Work, and Buying Intent
    - All valid workflow signals with original URL, company, title, dates, and evidence
    - Representative & filterable rejected matches with explicit rejection reasons
    - Limitations and commercial recommendation (GO / IMPROVE / STOP)
    """
    summary = report_data["summary"]
    boards = report_data["boards"]
    valid_signals = report_data["valid_signals"]
    rejected_samples = report_data["rejected_samples"]
    rejection_counts = summary["rejected_by_reason"]
    category_counts = summary["valid_by_category"]
    subtype_counts = summary["valid_by_subtype"]

    heuristic_rejected_count = summary.get(
        "heuristic_rejected_candidates_count",
        summary.get("rejected_false_positives_count", 0),
    )
    heuristic_rejection_rate = summary.get(
        "heuristic_rejection_rate_pct",
        summary.get("false_positive_rate_pct", 0.0),
    )
    heuristic_clusters_count = summary.get("heuristic_workflow_clusters_count", "N/A")
    ground_truth_eval = summary.get(
        "ground_truth_evaluation",
        {"status": "PENDING_INDEPENDENT_HUMAN_LABELS", "human_labeled_count": 0},
    )

    board_rows_html = []
    for b in boards:
        status_badge = (
            f'<span class="badge badge-ok">HTTP {b["http_status"]}</span>'
            if b["error_message"] is None
            else f'<span class="badge badge-err">{html.escape(str(b["error_message"]))}</span>'
        )
        board_rows_html.append(
            f"""
            <tr>
                <td><strong>{html.escape(b["company_name"])}</strong> <code>({html.escape(b["board_token"])})</code></td>
                <td>{status_badge}</td>
                <td>{b["jobs_fetched"]:,}</td>
                <td>{b["candidate_sentences_evaluated"]:,}</td>
                <td><strong>{b["valid_signals_count"]}</strong> <span class="muted">({b["unique_valid_signals_count"]} unique)</span></td>
                <td>{b["rejected_count"]:,}</td>
            </tr>
            """
        )

    valid_rows_html = []
    for idx, item in enumerate(valid_signals, start=1):
        subtype_badge = (
            '<span class="badge badge-manual">Direct Manual Execution</span>'
            if item["signal_subtype"] == "DIRECT_MANUAL_EXECUTION"
            else '<span class="badge badge-auto">Internal Automation Mandate</span>'
        )
        dup_badge = (
            ' <span class="badge badge-dup" title="Identical bullet in multi-region posting">Regional Duplicate</span>'
            if item.get("is_regional_duplicate")
            else ""
        )
        pub_date = (item.get("first_published") or "N/A")[:10]
        upd_date = (item.get("updated_at") or "N/A")[:10]
        valid_rows_html.append(
            f"""
            <tr data-category="{html.escape(item["workflow_category"])}" data-subtype="{html.escape(item["signal_subtype"])}">
                <td>{idx}</td>
                <td>
                    <strong>{html.escape(item["company_name"])}</strong><br/>
                    <span class="muted">{html.escape(item["department"])}</span>
                </td>
                <td>
                    <a href="{html.escape(item["source_url"])}" target="_blank" rel="noopener noreferrer">
                        {html.escape(item["job_title"])}
                    </a><br/>
                    <span class="muted">{html.escape(item["location"])}</span>
                </td>
                <td>
                    <span class="badge badge-cat">{html.escape(item["workflow_category"])}</span><br/>
                    {subtype_badge}{dup_badge}
                </td>
                <td class="evidence-cell">"{html.escape(item["exact_evidence"])}"</td>
                <td class="date-cell">
                    <div><strong>Published:</strong> {html.escape(pub_date)}</div>
                    <div><strong>Updated:</strong> {html.escape(upd_date)}</div>
                </td>
                <td class="intent-cell">
                    <div class="intent-warning">{html.escape(item["buying_intent_assessment"])}</div>
                </td>
            </tr>
            """
        )

    rejected_rows_html = []
    for idx, item in enumerate(rejected_samples, start=1):
        pub_date = (item.get("first_published") or "N/A")[:10]
        upd_date = (item.get("updated_at") or "N/A")[:10]
        rejected_rows_html.append(
            f"""
            <tr data-reason="{html.escape(str(item["rejection_reason"]))}">
                <td>{idx}</td>
                <td><strong>{html.escape(item["company_name"])}</strong></td>
                <td>
                    <a href="{html.escape(item["source_url"])}" target="_blank" rel="noopener noreferrer">
                        {html.escape(item["job_title"])}
                    </a>
                </td>
                <td><span class="badge badge-cat">{html.escape(item["workflow_category"])}</span></td>
                <td><span class="badge badge-rej">{html.escape(str(item["rejection_reason"]))}</span></td>
                <td class="evidence-cell">"{html.escape(item["exact_evidence"])}"</td>
                <td>{html.escape(item["explanation"])}</td>
                <td class="date-cell">
                    <div>Pub: {html.escape(pub_date)}</div>
                    <div>Upd: {html.escape(upd_date)}</div>
                </td>
            </tr>
            """
        )

    reason_summary_items = "".join(
        f"<li><code>{html.escape(reason)}</code>: <strong>{count:,}</strong> rejected statements</li>"
        for reason, count in sorted(rejection_counts.items(), key=lambda x: x[1], reverse=True)
    )
    category_summary_items = "".join(
        f"<li><strong>{html.escape(cat)}</strong>: {count} valid signals</li>"
        for cat, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True)
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>ManualOps Radar — Phase 1 Real Data Validation Report</title>
    <style>
        :root {{
            --bg: #f8fafc;
            --card: #ffffff;
            --text: #0f172a;
            --muted: #475569;
            --border: #e2e8f0;
            --accent: #2563eb;
            --ok-bg: #dcfce7;
            --ok-text: #166534;
            --warn-bg: #fef3c7;
            --warn-text: #92400e;
            --rej-bg: #fee2e2;
            --rej-text: #991b1b;
            --cat-bg: #e0e7ff;
            --cat-text: #1e40af;
        }}
        * {{ box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: var(--bg);
            color: var(--text);
            margin: 0;
            padding: 24px;
            line-height: 1.5;
        }}
        .container {{ max-width: 1380px; margin: 0 auto; }}
        header {{
            background: var(--card);
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 24px;
            margin-bottom: 20px;
        }}
        h1 {{ margin: 0 0 8px 0; font-size: 1.65rem; }}
        h2 {{ margin-top: 0; font-size: 1.25rem; border-bottom: 1px solid var(--border); padding-bottom: 8px; }}
        .banner-warning {{
            background: var(--warn-bg);
            color: var(--warn-text);
            border-left: 5px solid #d97706;
            padding: 14px 16px;
            border-radius: 6px;
            margin-top: 14px;
            font-size: 0.95rem;
        }}
        .grid-cards {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
            gap: 14px;
            margin-bottom: 20px;
        }}
        .card {{
            background: var(--card);
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 18px;
        }}
        .metric-value {{ font-size: 1.8rem; font-weight: 700; margin: 4px 0; }}
        .metric-label {{ font-size: 0.85rem; color: var(--muted); text-transform: uppercase; letter-spacing: 0.04em; }}
        .section {{
            background: var(--card);
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
            overflow-x: auto;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.88rem;
        }}
        th, td {{
            border-bottom: 1px solid var(--border);
            padding: 10px 12px;
            text-align: left;
            vertical-align: top;
        }}
        th {{ background: #f1f5f9; font-weight: 600; }}
        .badge {{
            display: inline-block;
            padding: 2px 8px;
            border-radius: 999px;
            font-size: 0.75rem;
            font-weight: 600;
            margin: 2px 0;
        }}
        .badge-ok {{ background: var(--ok-bg); color: var(--ok-text); }}
        .badge-err {{ background: var(--rej-bg); color: var(--rej-text); }}
        .badge-cat {{ background: var(--cat-bg); color: var(--cat-text); }}
        .badge-manual {{ background: var(--ok-bg); color: var(--ok-text); }}
        .badge-auto {{ background: var(--warn-bg); color: var(--warn-text); }}
        .badge-dup {{ background: #f1f5f9; color: #475569; border: 1px solid #cbd5e1; }}
        .badge-rej {{ background: var(--rej-bg); color: var(--rej-text); }}
        .muted {{ color: var(--muted); font-size: 0.8rem; }}
        .evidence-cell {{ max-width: 420px; font-style: italic; color: #1e293b; }}
        .intent-cell {{ max-width: 300px; font-size: 0.82rem; color: #78350f; }}
        .date-cell {{ white-space: nowrap; font-size: 0.8rem; color: var(--muted); }}
        .controls {{ margin-bottom: 12px; display: flex; gap: 10px; flex-wrap: wrap; align-items: center; }}
        select {{ padding: 6px 10px; border-radius: 6px; border: 1px solid var(--border); font-size: 0.88rem; }}
        a {{ color: var(--accent); text-decoration: none; font-weight: 500; }}
        a:hover {{ text-decoration: underline; }}
    </style>
</head>
<body>
<div class="container">
    <header>
        <h1>ManualOps Radar — Phase 1: Real Data Validation Report</h1>
        <div class="muted">
            Generated at: <strong>{html.escape(report_data["generated_at"])}</strong> |
            Source: Official Greenhouse Public Job Board API (5 Verified Companies)
        </div>
        <div class="banner-warning">
            <strong>Critical Product Rule (Job Posting &ne; Buying Intent):</strong>
            Explicit mentions of manual spreadsheets, reconciliations, reporting, data entry, or CRM maintenance prove
            <em>workflow existence</em>, never software buying intent. In fact, real data below shows companies either
            (a) allocate headcount budget to execute the manual process or (b) hire internal staff to automate it in-house.
        </div>
    </header>

    <div class="grid-cards">
        <div class="card">
            <div class="metric-label">Verified Boards Scanned</div>
            <div class="metric-value">{summary["boards_scanned"]} / {summary["boards_configured"]}</div>
            <div class="muted">API Errors: {summary["api_errors_count"]} (Measured)</div>
        </div>
        <div class="card">
            <div class="metric-label">Total Jobs Scanned</div>
            <div class="metric-value">{summary["total_jobs_scanned"]:,}</div>
            <div class="muted">100% live public postings (Measured)</div>
        </div>
        <div class="card">
            <div class="metric-label">Candidate Matches Evaluated</div>
            <div class="metric-value">{summary["total_candidates_evaluated"]:,}</div>
            <div class="muted">Broad keyword hits across 5 categories</div>
        </div>
        <div class="card">
            <div class="metric-label">Heuristic-Accepted Signals</div>
            <div class="metric-value" style="color: #166534;">{summary["valid_signals_count"]}</div>
            <div class="muted">{summary["unique_valid_signals_count"]} unique strings ({heuristic_clusters_count} heuristic groupings)</div>
        </div>
        <div class="card">
            <div class="metric-label">Heuristic-Rejected Candidates</div>
            <div class="metric-value" style="color: #991b1b;">{heuristic_rejected_count:,}</div>
            <div class="muted">{heuristic_rejection_rate}% heuristic filter rejection rate (unverified without ground truth)</div>
        </div>
        <div class="card">
            <div class="metric-label">Recommendation</div>
            <div class="metric-value" style="color: #b45309; font-size: 1.25rem;">{html.escape(report_data["recommendation"]["verdict"])}</div>
            <div class="muted">Ground Truth: {html.escape(str(ground_truth_eval.get("status", "PENDING")))}</div>
        </div>
    </div>

    <div class="section">
        <h2>1. Board-by-Board Validation Summary (Measured API &amp; Heuristic Counts)</h2>
        <table>
            <thead>
                <tr>
                    <th>Company (Verified Token)</th>
                    <th>API Status</th>
                    <th>Jobs Scanned</th>
                    <th>Candidate Sentences</th>
                    <th>Heuristic-Accepted Signals</th>
                    <th>Heuristic-Rejected Candidates</th>
                </tr>
            </thead>
            <tbody>
                {"".join(board_rows_html)}
            </tbody>
        </table>
    </div>

    <div class="section">
        <h2>2. Heuristic Signal Breakdown: Skills vs. Manual Work vs. Buying Intent</h2>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 16px;">
            <div>
                <h3>Heuristic-Accepted Signals by Category ({summary["valid_signals_count"]} total)</h3>
                <ul>{category_summary_items}</ul>
                <p class="muted">
                    <strong>Direct Manual Execution (Heuristic):</strong> {subtype_counts.get("DIRECT_MANUAL_EXECUTION", 0)} signals<br/>
                    <strong>Internal Automation Mandate (Heuristic):</strong> {subtype_counts.get("INTERNAL_AUTOMATION_MANDATE", 0)} signals
                </p>
            </div>
            <div>
                <h3>Heuristic-Rejected Candidates by Rule ({heuristic_rejected_count:,} total)</h3>
                <ul>{reason_summary_items}</ul>
            </div>
        </div>
    </div>

    <div class="section">
        <h2>3. All Heuristic-Accepted Manual Workflow Signals ({len(valid_signals)} Real Matches)</h2>
        <div class="controls">
            <label for="catFilter"><strong>Filter by Category:</strong></label>
            <select id="catFilter" onchange="filterValidSignals()">
                <option value="ALL">All Categories</option>
                <option value="Reconciliation">Reconciliation</option>
                <option value="CRM Operations">CRM Operations</option>
                <option value="Reporting">Reporting</option>
                <option value="Data Entry">Data Entry</option>
                <option value="Spreadsheets">Spreadsheets</option>
            </select>
            <label for="subFilter"><strong>Filter by Subtype:</strong></label>
            <select id="subFilter" onchange="filterValidSignals()">
                <option value="ALL">All Subtypes</option>
                <option value="DIRECT_MANUAL_EXECUTION">Direct Manual Execution</option>
                <option value="INTERNAL_AUTOMATION_MANDATE">Internal Automation Mandate</option>
            </select>
        </div>
        <table id="validTable">
            <thead>
                <tr>
                    <th>#</th>
                    <th>Company &amp; Dept</th>
                    <th>Posting Title &amp; Original URL</th>
                    <th>Category &amp; Subtype</th>
                    <th>Exact Verbatim Evidence</th>
                    <th>Publication / Update Dates</th>
                    <th>Buying Intent &amp; Uncertainty Assessment</th>
                </tr>
            </thead>
            <tbody>
                {"".join(valid_rows_html)}
            </tbody>
        </table>
    </div>

    <div class="section">
        <h2>4. Heuristic-Rejected Candidates Audit Log (Showing {len(rejected_samples)} Representative Real Rejections across All {heuristic_rejected_count:,} Filtered Statements)</h2>
        <p class="muted">
            Deterministic rules filtered out <strong>{heuristic_rejection_rate}%</strong> of broad keyword hits (heuristic filter rejection rate, not a ground-truth false-positive rate).
            Below are real rejected statements demonstrating how heuristic rules separate general software skills,
            English idioms ("excel in"), product marketing copy, and software engineering roles from candidate workflow statements.
        </p>
        <div class="controls">
            <label for="rejFilter"><strong>Filter by Rejection Reason:</strong></label>
            <select id="rejFilter" onchange="filterRejected()">
                <option value="ALL">All Rejection Reasons</option>
                <option value="GENERAL_SOFTWARE_SKILL">GENERAL_SOFTWARE_SKILL</option>
                <option value="VERB_EXCEL_OR_IDIOM">VERB_EXCEL_OR_IDIOM</option>
                <option value="PRODUCT_PITCH_OR_CUSTOMER_FEATURE">PRODUCT_PITCH_OR_CUSTOMER_FEATURE</option>
                <option value="ENGINEERING_INFRA_OR_SYSTEMS_BUILD">ENGINEERING_INFRA_OR_SYSTEMS_BUILD</option>
                <option value="GENERIC_MENTION_WITHOUT_MANUAL_WORKFLOW">GENERIC_MENTION_WITHOUT_MANUAL_WORKFLOW</option>
            </select>
        </div>
        <table id="rejectedTable">
            <thead>
                <tr>
                    <th>#</th>
                    <th>Company</th>
                    <th>Posting Title &amp; URL</th>
                    <th>Triggered Category</th>
                    <th>Rejection Reason</th>
                    <th>Exact Verbatim Statement</th>
                    <th>Automated Filter Explanation</th>
                    <th>Dates</th>
                </tr>
            </thead>
            <tbody>
                {"".join(rejected_rows_html)}
            </tbody>
        </table>
    </div>

    <div class="section">
        <h2>5. Evaluation Integrity, Heuristic Groupings &amp; Commercial Recommendation</h2>
        <ul>
            <li><strong>Separation of Heuristic Classifications vs. Human Ground-Truth Labels:</strong> All counts above ({summary["total_jobs_scanned"]:,} jobs scanned, {summary["total_candidates_evaluated"]:,} candidate statements, {summary["valid_signals_count"]} heuristic-accepted signals, {heuristic_rejected_count:,} heuristic-rejected candidates) are <strong>automated heuristic outputs</strong>. Independent human ground-truth evaluation status is <code>{html.escape(str(ground_truth_eval.get("status")))}</code> ({ground_truth_eval.get("human_labeled_count", 0)} of {ground_truth_eval.get("total_sample_size", 50)} sampled records independently labeled in <code>data/phase1_5_evaluation_worksheet.csv</code>).</li>
            <li><strong>Heuristic Rejection Rate &ne; Ground-Truth False-Positive Rate:</strong> The <strong>{heuristic_rejection_rate}%</strong> heuristic rejection rate measures the share of broad keyword matches filtered out by deterministic rules; true precision and false-negative rates require completing independent human labeling per <code>docs/LABELING_GUIDELINES.md</code>.</li>
            <li><strong>Heuristic Company/Workflow Groupings:</strong> Automated keyword clustering groups the {summary["valid_signals_count"]} accepted signals into <strong>{heuristic_clusters_count} heuristic company/workflow groupings</strong>. These are text-similarity approximations, not verified distinct internal business processes.</li>
            <li><strong>Recommendation — {html.escape(report_data["recommendation"]["verdict"])}:</strong> {html.escape(report_data["recommendation"]["summary"])}</li>
        </ul>
    </div>
</div>

<script>
function filterValidSignals() {{
    const cat = document.getElementById('catFilter').value;
    const sub = document.getElementById('subFilter').value;
    const rows = document.querySelectorAll('#validTable tbody tr');
    rows.forEach(row => {{
        const matchCat = (cat === 'ALL' || row.getAttribute('data-category') === cat);
        const matchSub = (sub === 'ALL' || row.getAttribute('data-subtype') === sub);
        row.style.display = (matchCat && matchSub) ? '' : 'none';
    }});
}}
function filterRejected() {{
    const reason = document.getElementById('rejFilter').value;
    const rows = document.querySelectorAll('#rejectedTable tbody tr');
    rows.forEach(row => {{
        const matchReason = (reason === 'ALL' || row.getAttribute('data-reason') === reason);
        row.style.display = matchReason ? '' : 'none';
    }});
}}
</script>
</body>
</html>
"""
