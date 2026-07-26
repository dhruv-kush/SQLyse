"""
In-memory scan store + background execution.

Deliberately no SQLite yet (per instructions): a dict protected by a lock is
enough for the first working version of the API and for testing frontend
integration. Swap this module's internals for a database-backed version later
without touching routes.py, since routes.py only calls the functions below.
"""
import threading
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone

from .config import Config
from .scanner_engine.mock_adapter import run_mock_scan
from .scanner_engine.real_adapter import run_real_scan

VALID_STATUSES = {"queued", "running", "completed", "cancelled", "failed"}

_lock = threading.Lock()
_scans = {}  # scan_id -> scan record (dict)
_cancel_events = {}  # scan_id -> threading.Event

_executor = ThreadPoolExecutor(
    max_workers=Config.MAX_CONCURRENT_SCANS, thread_name_prefix="sqlyse-scan",
)


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


def _new_scan_id():
    return f"SQLYSE-{datetime.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:6].upper()}"


def create_scan(target_url: str) -> dict:
    """Registers a new scan in the 'queued' state and submits it to the
    thread pool. Returns the initial scan record (safe to serialize)."""
    scan_id = _new_scan_id()
    now = _now_iso()

    record = {
        "scanId": scan_id,
        "targetUrl": target_url,
        "status": "queued",
        "progress": 0,
        "phase": "Initializing",
        "createdAt": now,
        "startedAt": None,
        "completedAt": None,
        "logs": [],
        "error": None,
        "result": None,
    }

    with _lock:
        _scans[scan_id] = record
        _cancel_events[scan_id] = threading.Event()
        # Snapshot BEFORE submitting to the pool. Worker threads can start
        # executing (and mutate status/progress) the instant submit() is
        # called, so the copy must happen first or the response we return
        # can already show "running"/5 instead of the true initial
        # "queued"/0 state.
        initial_record = dict(record)

    _executor.submit(_run_scan, scan_id)

    return initial_record


def _update(scan_id: str, **fields):
    with _lock:
        record = _scans.get(scan_id)
        if record is None:
            return
        record.update(fields)


def _append_log(scan_id: str, log_type: str, message: str):
    with _lock:
        record = _scans.get(scan_id)
        if record is None:
            return
        record["logs"].append({
            "type": log_type,
            "message": message,
            "timestamp": _now_iso(),
        })


def _is_cancelled(scan_id: str) -> bool:
    event = _cancel_events.get(scan_id)
    return event.is_set() if event else False


def _run_scan(scan_id: str):
    """Runs on a ThreadPoolExecutor worker. Never lets an exception escape -
    any failure in the adapter is caught and stored as a clean 'failed'
    state instead of crashing the worker thread (and, if unhandled at this
    layer, potentially the process)."""
    with _lock:
        record = _scans.get(scan_id)
        if record is None:
            return
        target_url = record["targetUrl"]

    _update(scan_id, status="running", startedAt=_now_iso())

    def on_progress(percent, phase):
        _update(scan_id, progress=percent, phase=phase)

    def on_log(log_type, message):
        _append_log(scan_id, log_type, message)

    def is_cancelled():
        return _is_cancelled(scan_id)

    try:
        adapter = run_mock_scan if Config.USE_MOCK_SCANNER else run_real_scan
        result = adapter(scan_id, target_url, on_progress, on_log, is_cancelled)

        if is_cancelled():
            _update(scan_id, status="cancelled", completedAt=_now_iso(),
                     phase="Cancelled")
            return

        if result is None:
            _update(
                scan_id, status="failed", completedAt=_now_iso(),
                error="Scan engine returned no result",
                phase="Failed",
            )
            return

        if Config.USE_MOCK_SCANNER:
            result = {
                "isMockData": True,
                "disclaimer": "Mock scan data for development/testing. Not a real security assessment.",
                **result,
            }

        completed_at = _now_iso()
        with _lock:
            started_at = _scans[scan_id]["startedAt"]
        duration_seconds = round(
            (datetime.fromisoformat(completed_at) - datetime.fromisoformat(started_at)).total_seconds(),
            1,
        )
        result = {
            **result,
            "startedAt": started_at,
            "completedAt": completed_at,
            "durationSeconds": duration_seconds,
        }

        _update(
            scan_id, status="completed", completedAt=completed_at,
            progress=100, phase="Scan Complete", result=result,
        )
    except Exception as exc:  # noqa: BLE001 - intentionally broad: this is
        # the last line of defense between a buggy/failing scanner adapter
        # and a crashed worker thread. Anything goes wrong here, the scan
        # is marked failed and the API keeps responding normally.
        _append_log(scan_id, "error", f"Scan failed: {exc}")
        _update(
            scan_id, status="failed", completedAt=_now_iso(),
            error=str(exc), phase="Failed",
        )
    finally:
        with _lock:
            _cancel_events.pop(scan_id, None)


def get_scan(scan_id: str):
    """Returns a shallow copy of the scan record, or None if unknown."""
    with _lock:
        record = _scans.get(scan_id)
        return dict(record) if record is not None else None


def cancel_scan(scan_id: str):
    """
    Signals cancellation via a thread-safe Event. Returns:
        (ok: bool, record_or_error: dict)
    ok is False if the scan doesn't exist or is already in a terminal state.
    """
    with _lock:
        record = _scans.get(scan_id)
        if record is None:
            return False, {"error": "Scan not found"}

        if record["status"] in ("completed", "cancelled", "failed"):
            return False, {"error": f"Scan already {record['status']}, cannot cancel"}

        event = _cancel_events.get(scan_id)

    if event is not None:
        event.set()

    _update(scan_id, status="cancelled", completedAt=_now_iso(), phase="Cancelled")
    return True, get_scan(scan_id)


def elapsed_seconds(record: dict) -> float:
    """Computed on read, not stored, so it's always accurate for in-progress
    scans and stable once completed/cancelled/failed."""
    started = record.get("startedAt") or record.get("createdAt")
    if not started:
        return 0.0
    start_dt = datetime.fromisoformat(started)
    end = record.get("completedAt")
    end_dt = datetime.fromisoformat(end) if end else datetime.now(timezone.utc)
    return max(0.0, (end_dt - start_dt).total_seconds())
