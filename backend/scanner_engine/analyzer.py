"""
Compares baseline vs payload ("modified") responses and decides whether a
test case looks like a SQL injection. Produces finding dicts in the exact
shape the frontend expects (see mock_adapter.py / app.js mockScanResult).
"""
import re

SQL_ERROR_SIGNATURES = [
    (r"sql syntax.*mysql", "MySQL syntax error family"),
    (r"warning.*mysql_", "MySQL syntax error family"),
    (r"unclosed quotation mark", "Generic SQL syntax error family"),
    (r"quoted string not properly terminated", "Oracle/Generic syntax error family"),
    (r"sqlite3?\.(operationalerror|error)", "SQLite Error"),
    (r"sqlite_error", "SQLite Error"),
    (r"pg_query\(\)|postgresql.*error", "PostgreSQL Error"),
    (r"ora-\d{5}", "Oracle Error"),
    (r"microsoft ole db provider|odbc.*sql server", "MSSQL Error"),
    (r"supplied argument is not a valid", "PHP/SQL binding error"),
    (r"unterminated string literal", "Generic SQL syntax error family"),
]

_ID_COUNTER = 0


def _next_id():
    global _ID_COUNTER
    _ID_COUNTER += 1
    return f"SQL-F-{_ID_COUNTER:03d}"


def _find_sql_error(text: str):
    lowered = text.lower()
    for pattern, family in SQL_ERROR_SIGNATURES:
        if re.search(pattern, lowered):
            return family
    return None


def _format_bytes(n: int) -> str:
    if n < 1024:
        return f"{n} bytes"
    return f"{n / 1024:.1f} KB"


def analyze_case(case: dict):
    """
    Returns a finding dict if the case looks vulnerable, else None.
    Two detection strategies (mirrors Phase 6/7 in Member.pdf):
      1. Error-based: an SQL error signature appears only in the modified response.
      2. Behavioural: status code changed, or response length differs a lot,
         between baseline and modified, for the same field/payload.
    """
    baseline = case["baseline"]
    modified = case["modified"]

    if modified["error"]:
        return None  # request itself failed (timeout etc.) - not a finding

    baseline_error = _find_sql_error(baseline["text"])
    modified_error = _find_sql_error(modified["text"])

    length_diff = modified["length"] - baseline["length"]
    status_changed = baseline["status_code"] != modified["status_code"]
    big_length_diff = baseline["length"] > 0 and abs(length_diff) / baseline["length"] > 0.15

    if modified_error and not baseline_error:
        severity, confidence, detection = "High", 92, "Database error signature"
    elif status_changed and modified["status_code"] and modified["status_code"] >= 500:
        severity, confidence, detection = "High", 85, "Server error triggered by payload"
    elif big_length_diff:
        severity, confidence, detection = "Medium", 70, "Response behaviour anomaly"
    else:
        return None

    form = case["form"]
    return {
        "id": _next_id(),
        "title": (
            "Possible error-based SQL injection" if detection == "Database error signature"
            else "Suspicious boolean-response difference"
        ),
        "endpoint": form["action"],
        "parameter": case["parameter"],
        "detection": detection,
        "severity": severity,
        "confidence": confidence,
        "status": "Requires Review",
        "httpMethod": form["method"],
        "responseStatusComparison": f"{baseline['status_code']} → {modified['status_code']}",
        "responseLengthDifference": f"{'+' if length_diff >= 0 else ''}{_format_bytes(length_diff)}",
        "databaseErrorFamily": modified_error or "Not observed",
        "observed": (
            f"Submitting payload into '{case['parameter']}' changed the "
            f"application's response compared to a normal baseline value."
        ),
        "risk": (
            "This behaviour can indicate that user-controlled input is reaching "
            "a SQL interpreter without sufficient separation between code and data."
        ),
        "impact": (
            "If manually confirmed, an attacker could potentially influence "
            "database queries or access data outside the intended application flow."
        ),
        "verification": (
            "Reproduce this in an authorised test environment and review "
            "server-side query construction before treating it as confirmed."
        ),
        "analysis": (
            f"The endpoint returned different behaviour after '{case['parameter']}' "
            f"was set to a SQL injection probe payload. This should be manually "
            f"verified before being treated as a confirmed vulnerability."
        ),
        "evidence": {
            "baselineStatus": str(baseline["status_code"]),
            "modifiedStatus": str(modified["status_code"]),
            "baselineLength": _format_bytes(baseline["length"]),
            "modifiedLength": _format_bytes(modified["length"]),
            "excerpt": "[sanitised] Response excerpt withheld; see server logs for full detail.",
        },
        "recommendations": [
            {"title": "Use parameterised queries", "explanation": "Bind user-controlled values separately from SQL command text using prepared statements.", "priority": "High"},
            {"title": "Remove string concatenation", "explanation": "Avoid constructing SQL commands by joining request values into query strings.", "priority": "High"},
            {"title": "Validate input server-side", "explanation": "Apply type, length and format constraints before values reach the data layer.", "priority": "High"},
            {"title": "Return generic errors", "explanation": "Keep database errors in protected server logs and return neutral application messages.", "priority": "Medium"},
        ],
    }


def analyze_cases(cases: list):
    """Runs analyze_case over every test case, deduping so one (endpoint,
    parameter) pair only produces its single highest-confidence finding."""
    best_by_key = {}
    for case in cases:
        finding = analyze_case(case)
        if finding is None:
            continue
        key = (finding["endpoint"], finding["parameter"])
        if key not in best_by_key or finding["confidence"] > best_by_key[key]["confidence"]:
            best_by_key[key] = finding

    return list(best_by_key.values())
