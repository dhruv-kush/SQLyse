"""
Refactored from Dhruv's crawler.py / pra.py.

Original scripts used input() and just printed forms - fine for testing by
hand, but not importable. This version does the exact same job (find forms +
their inputs on a page) as plain functions, plus a light same-domain crawl so
we're not stuck testing a single page.

Dhruv: your detection logic is untouched - I only moved it into functions and
added the multi-page loop. If you improve form/input detection later, this is
the only file that needs to change.
"""
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

from ..config import Config


def get_forms(url: str, timeout: int = None, session: requests.Session = None):
    """
    Same logic as crawler.py: fetch a page, find every <form>, and pull out
    its action, method, and input names/types/values. Returns a list of dicts:
        {"action": str, "method": "GET"/"POST",
         "inputs": [{"name":.., "type":.., "value":..}]}

    The observed "value" is kept (not discarded) so hidden fields and CSRF
    tokens can be sent back unchanged by the scanner instead of being
    overwritten with a test value or payload.
    """
    timeout = timeout or Config.REQUEST_TIMEOUT_SECONDS
    max_bytes = getattr(Config, "MAX_RESPONSE_BYTES", 2_000_000)
    requester = session or requests

    response = requester.get(url, timeout=timeout, stream=True)
    content = b""
    for chunk in response.iter_content(chunk_size=8192):
        content += chunk
        if len(content) >= max_bytes:
            break
    response.close()

    soup = BeautifulSoup(content, "html.parser")

    forms = []
    for form in soup.find_all("form"):
        action = form.get("action") or url
        method = (form.get("method") or "GET").upper()

        inputs = []
        for input_tag in form.find_all(["input", "textarea", "select"]):
            name = input_tag.get("name")
            if not name:
                continue
            inputs.append({
                "name": name,
                "type": input_tag.get("type", "text"),
                "value": input_tag.get("value", ""),
            })

        forms.append({
            "page_url": url,
            "action": urljoin(url, action),
            "method": method,
            "inputs": inputs,
        })

    return forms, soup


def get_links(soup: BeautifulSoup, base_url: str):
    """Same-domain links only, so the crawl doesn't wander off-site."""
    base_domain = urlparse(base_url).netloc
    links = set()
    for tag in soup.find_all("a", href=True):
        full_url = urljoin(base_url, tag["href"])
        if urlparse(full_url).netloc == base_domain:
            links.add(full_url.split("#")[0])
    return links


def crawl(start_url: str, max_pages: int = None, session: requests.Session = None):
    """
    Breadth-first crawl of the same domain, collecting every form found along
    the way. Returns list of form dicts (see get_forms) and the set of pages
    actually visited (used for the "pages scanned" stat).

    If a session is passed in, it's reused for every request during the
    crawl (and should be the same session later used by scanner.test_form),
    so cookies set by the target persist from discovery through testing.
    """
    max_pages = max_pages or Config.MAX_PAGES_PER_SCAN
    requester = session or requests

    visited = set()
    to_visit = {start_url}
    all_forms = []

    while to_visit and len(visited) < max_pages:
        url = to_visit.pop()
        if url in visited:
            continue
        visited.add(url)

        try:
            forms, soup = get_forms(url, session=session)
        except requests.RequestException:
            continue

        all_forms.extend(forms)
        to_visit.update(get_links(soup, start_url) - visited)

    return all_forms, visited
