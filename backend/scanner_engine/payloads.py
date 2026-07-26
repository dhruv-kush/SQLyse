"""
Thin wrapper around Dhruv's payload.py so the rest of the backend imports
from one stable place, and so we can trim the payload list for speed without
touching his file.
"""
from .payload import payloads as _all_payloads

# Running all ~45 payloads against every input on every form gets slow fast
# (forms x inputs x payloads requests). For a live demo, a representative
# subset is plenty; swap get_payloads() to return _all_payloads for a full run.
_QUICK_SUBSET = [
    "'",
    "' OR '1'='1",
    "' OR '1'='1'--",
    "\" OR \"1\"=\"1",
    "' OR 1=1 --",
    "admin' --",
    "' UNION SELECT NULL --",
]


def get_payloads(full: bool = False):
    return _all_payloads if full else _QUICK_SUBSET
