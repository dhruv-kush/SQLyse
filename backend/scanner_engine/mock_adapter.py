"""
Fake scan engine. Used while USE_MOCK_SCANNER=true so the frontend and API
contract can be finished before Dhruv's real crawler/scanner are plugged in.

IMPORTANT: the shape of what run_mock_scan() returns is deliberately identical
to the frontend's `mockScanResult` object in app.js (findings[], evidence{},
recommendations[], etc). Once real_adapter.py is ready, it must return the
exact same shape so nothing downstream (report.py, frontend) needs to change.
"""
import random
import time

PHASES = [
    ("Initializing", 5, "info", "Initializing scan engine"),
    ("Crawling Target", 20, "success", "Target connection established"),
    ("Discovering Inputs", 40, "info", "Crawling application routes"),
    ("Testing Parameters", 60, "success", "Forms discovered"),
    ("Analyzing Responses", 80, "info", "Testing input parameters"),
    ("Building Findings", 95, "warning", "Comparing response behaviour"),
    ("Scan Complete", 100, "success", "Findings analysis complete"),
]

_SAMPLE_FINDINGS = [
    {
        "id": "SQL-F-001",
        "title": "Possible error-based SQL injection",
        "endpoint": "/account/login",
        "parameter": "username",
        "detection": "Database error signature",
        "severity": "High",
        "confidence": 92,
        "status": "Requires Review",
        "httpMethod": "POST",
        "responseStatusComparison": "200 OK → 500 Internal Server Error",
        "responseLengthDifference": "+1.8 KB",
        "databaseErrorFamily": "Generic SQL syntax error family",
        "observed": (
            "A modified username value was followed by an application error "
            "response containing a sanitised database parsing pattern."
        ),
        "risk": (
            "Detailed database parsing errors can indicate that user-controlled "
            "input is reaching a SQL interpreter without sufficient separation."
        ),
        "impact": (
            "If manually confirmed, an attacker could potentially influence "
            "database queries or access data outside the intended application flow."
        ),
        "verification": (
            "Reproduce the behaviour in an authorised test environment and review "
            "the server-side query construction before classifying this as confirmed."
        ),
        "analysis": (
            "The application returned behaviour consistent with a possible SQL "
            "parsing error after the username parameter was modified. This should "
            "be manually verified before being treated as a confirmed vulnerability."
        ),
        "evidence": {
            "baselineStatus": "200 OK",
            "modifiedStatus": "500 Internal Server Error",
            "baselineLength": "4.2 KB",
            "modifiedLength": "6.0 KB",
            "excerpt": (
                "[sanitised] The application response contained a generic database "
                "parsing error pattern. Request values and server identifiers were removed."
            ),
        },
        "recommendations": [
            {"title": "Use parameterised queries", "explanation": "Bind user-controlled values separately from SQL command text using prepared statements.", "priority": "High"},
            {"title": "Remove string concatenation", "explanation": "Avoid constructing SQL commands by joining request values into query strings.", "priority": "High"},
            {"title": "Validate input server-side", "explanation": "Apply type, length and format constraints before values reach the data layer.", "priority": "High"},
            {"title": "Return generic errors", "explanation": "Keep database errors in protected server logs and return neutral application messages.", "priority": "Medium"},
        ],
    },
    {
        "id": "SQL-F-002",
        "title": "Suspicious boolean-response difference",
        "endpoint": "/catalog/search",
        "parameter": "query",
        "detection": "Response behaviour anomaly",
        "severity": "Medium",
        "confidence": 84,
        "status": "Requires Review",
        "httpMethod": "GET",
        "responseStatusComparison": "200 OK → 200 OK",
        "responseLengthDifference": "+640 bytes",
        "databaseErrorFamily": "Not observed",
        "observed": (
            "Two controlled variations of the search parameter produced repeatable "
            "differences in response structure while keeping the same HTTP status."
        ),
        "risk": (
            "A stable response difference may indicate that input is changing a "
            "backend query condition, although normal application branching can "
            "produce similar behaviour."
        ),
        "impact": (
            "If verified, query manipulation could reveal records or alter the "
            "intended filtering behaviour of the search endpoint."
        ),
        "verification": (
            "Compare server-side query logs and repeat the test against a "
            "controlled dataset before escalating this finding."
        ),
        "analysis": (
            "The search endpoint returned a repeatable response difference after "
            "the query parameter was modified. The behaviour is suspicious but may "
            "also result from normal application logic and requires manual review."
        ),
        "evidence": {
            "baselineStatus": "200 OK",
            "modifiedStatus": "200 OK",
            "baselineLength": "18.4 KB",
            "modifiedLength": "19.0 KB",
            "excerpt": (
                "[sanitised] The modified response contained an additional result "
                "region. Query values, session data and response headers were excluded."
            ),
        },
        "recommendations": [
            {"title": "Use parameterised queries", "explanation": "Pass search values through query parameters rather than embedding them in SQL text.", "priority": "High"},
            {"title": "Validate input server-side", "explanation": "Constrain search length and accepted character patterns according to product requirements.", "priority": "Medium"},
            {"title": "Return generic errors", "explanation": "Prevent backend implementation details from entering client responses.", "priority": "Medium"},
        ],
    },
]


def run_mock_scan(scan_id: str, target_url: str, on_progress, on_log, is_cancelled):
    """
    Simulates a scan. Calls on_progress(percent, stage) and on_log(type, message)
    as it goes, checking is_cancelled() between phases so /cancel works.

    Returns a result dict shaped exactly like the frontend's mockScanResult,
    minus the isMockData/disclaimer fields which the route layer adds back in
    only when USE_MOCK_SCANNER is true.
    """
    for stage, percent, log_type, message in PHASES:
        if is_cancelled():
            return None
        on_progress(percent, stage)
        on_log(log_type, message)
        time.sleep(0.6)  # simulate work; keep short so demos feel snappy

    findings = _SAMPLE_FINDINGS
    severities = [f["severity"] for f in findings]
    overall_risk = (
        "High" if "High" in severities else "Medium" if "Medium" in severities else "Low"
    )

    return {
        "scanId": scan_id,
        "targetUrl": target_url,
        "pagesScanned": random.randint(8, 15),
        "formsDiscovered": len({f["endpoint"] for f in findings}) + 2,
        "parametersTested": len(findings) + random.randint(4, 8),
        "findingsCount": len(findings),
        "overallRisk": overall_risk,
        "findings": findings,
    }
