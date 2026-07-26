"""
Real scan engine: wires crawler.py -> scanner.py -> analyzer.py together.

Has the EXACT same function signature and return shape as mock_adapter.py's
run_mock_scan, so routes.py can switch between them with one config flag
(Config.USE_MOCK_SCANNER) and nothing else has to change.
"""
import requests

from .analyzer import analyze_cases
from .crawler import crawl
from .scanner import test_form


def run_real_scan(scan_id: str, target_url: str, on_progress, on_log, is_cancelled):
    on_progress(5, "Initializing")
    on_log("info", "Initializing scan engine")

    if is_cancelled():
        return None

    # One Session for the whole scan: crawling and form-testing share cookies
    # (session IDs, CSRF cookies) exactly as a real browser would.
    session = requests.Session()

    try:
        on_progress(20, "Crawling Target")
        on_log("success", "Target connection established")
        forms, visited_pages = crawl(target_url, session=session)

        if is_cancelled():
            return None

        on_progress(40, "Discovering Inputs")
        on_log("info", f"Crawling application routes ({len(visited_pages)} pages visited)")
        on_log("success", f"Forms discovered: {len(forms)}")

        if not forms:
            on_progress(100, "Scan Complete")
            on_log("warning", "No forms with inputs were found on this target")
            return {
                "scanId": scan_id,
                "targetUrl": target_url,
                "pagesScanned": len(visited_pages),
                "formsDiscovered": 0,
                "parametersTested": 0,
                "findingsCount": 0,
                "overallRisk": "Low",
                "findings": [],
            }

        on_progress(60, "Testing Parameters")
        on_log("info", "Testing input parameters")

        all_cases = []
        total_params = 0
        for form in forms:
            if is_cancelled():
                return None
            cases = test_form(form, session=session, is_cancelled=is_cancelled)
            all_cases.extend(cases)
            total_params += len(form["inputs"])
            if is_cancelled():
                return None

        if is_cancelled():
            return None

        on_progress(80, "Analyzing Responses")
        on_log("info", "Comparing baseline and modified responses")

        findings = analyze_cases(all_cases)

        on_progress(95, "Building Findings")
        on_log("warning" if findings else "success",
               f"{len(findings)} potential issue(s) found" if findings else "No issues found")

        severities = [f["severity"] for f in findings]
        overall_risk = (
            "High" if "High" in severities else "Medium" if "Medium" in severities else "Low"
        )

        on_progress(100, "Scan Complete")
        on_log("success", "Findings analysis complete")

        return {
            "scanId": scan_id,
            "targetUrl": target_url,
            "pagesScanned": len(visited_pages),
            "formsDiscovered": len(forms),
            "parametersTested": total_params,
            "findingsCount": len(findings),
            "overallRisk": overall_risk,
            "findings": findings,
        }
    finally:
        session.close()
