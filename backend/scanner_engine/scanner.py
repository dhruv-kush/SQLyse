"""
Sends the baseline request (normal values) and payload requests for every
input on every form Dhruv's crawler found, and hands the raw responses to
analyzer.py. This is the backend's own scanner - separate from Dhruv's
scanner.py stub (which currently just prints the payload list), so his file
isn't touched.
"""
import requests

from ..config import Config
from .payloads import get_payloads

# Hidden/CSRF-style fields must never be overwritten with "test" or a
# payload - doing so breaks the request (invalid token -> guaranteed
# rejection) and produces false positives/negatives. We preserve whatever
# value the crawler observed for these instead.
_PRESERVED_INPUT_TYPES = {"hidden"}
_PRESERVED_NAME_HINTS = ("csrf", "token", "_token", "authenticity", "nonce", "viewstate")


def _is_preserved_field(field: dict) -> bool:
    if field.get("type", "").lower() in _PRESERVED_INPUT_TYPES:
        return True
    name = (field.get("name") or "").lower()
    return any(hint in name for hint in _PRESERVED_NAME_HINTS)


def _fill_form_data(form: dict, override_name: str = None, override_value: str = None):
    """Builds a data dict for the form: harmless defaults for every field,
    except override_name which gets override_value (the payload, or a
    baseline probe value). Hidden/CSRF-style fields always keep the actual
    value the crawler saw on the page, never "test" and never the payload,
    since substituting them just breaks the request instead of testing it."""
    data = {}
    for field in form["inputs"]:
        if _is_preserved_field(field):
            data[field["name"]] = field.get("value", "")
        elif field["name"] == override_name:
            data[field["name"]] = override_value
        else:
            data[field["name"]] = "test"
    return data


def _send(session: requests.Session, form: dict, data: dict):
    timeout = Config.REQUEST_TIMEOUT_SECONDS
    max_bytes = Config.MAX_RESPONSE_BYTES
    try:
        if form["method"] == "POST":
            resp = session.post(form["action"], data=data, timeout=timeout,
                                 allow_redirects=True, stream=True)
        else:
            resp = session.get(form["action"], params=data, timeout=timeout,
                                allow_redirects=True, stream=True)

        # Read the body ourselves so we can cap it - a malicious/huge
        # response shouldn't be allowed to exhaust memory mid-scan.
        content = b""
        for chunk in resp.iter_content(chunk_size=8192):
            content += chunk
            if len(content) >= max_bytes:
                break
        text = content.decode(resp.encoding or "utf-8", errors="replace")

        return {
            "status_code": resp.status_code,
            "length": len(content),
            "text": text,
            "redirected": resp.url != form["action"],
            "final_url": resp.url,
            "error": None,
        }
    except requests.RequestException as exc:
        return {"status_code": None, "length": 0, "text": "", "redirected": False,
                "final_url": form["action"], "error": str(exc)}
    finally:
        try:
            resp.close()
        except Exception:
            pass


def test_form(form: dict, session: requests.Session = None, full_payloads: bool = False,
               is_cancelled=None):
    """
    For each input field on the form, sends one baseline request and one
    request per payload, substituted into that field only. Hidden/CSRF-style
    fields are always sent with their real observed value (see
    _fill_form_data), never overwritten.

    A single requests.Session is used for every call so cookies set by the
    target application (session IDs, CSRF cookies, etc.) persist across the
    baseline and payload requests, matching real browser behaviour. If no
    session is passed in, one is created for just this form's tests - callers
    testing multiple forms on the same scan should share one Session across
    all test_form() calls instead.

    If is_cancelled is provided, it's checked before every individual
    request (baseline and each payload) so a cancellation lands within a
    single request's worth of delay instead of waiting for the whole form
    (which, with dozens of payloads, could otherwise take a while to stop).

    Returns a list of test cases:
        {"form": form, "parameter": name, "payload": str,
         "baseline": response_dict, "modified": response_dict}
    """
    owns_session = session is None
    if owns_session:
        session = requests.Session()

    def _cancelled():
        return is_cancelled() if is_cancelled is not None else False

    try:
        cases = []
        payload_list = get_payloads(full=full_payloads)

        testable_fields = [f for f in form["inputs"] if not _is_preserved_field(f)]

        for field in testable_fields:
            if _cancelled():
                return cases

            baseline_data = _fill_form_data(form, field["name"], "test123")
            baseline = _send(session, form, baseline_data)

            for payload in payload_list:
                if _cancelled():
                    return cases

                modified_data = _fill_form_data(form, field["name"], payload)
                modified = _send(session, form, modified_data)
                cases.append({
                    "form": form,
                    "parameter": field["name"],
                    "payload": payload,
                    "baseline": baseline,
                    "modified": modified,
                })

        return cases
    finally:
        if owns_session:
            session.close()
