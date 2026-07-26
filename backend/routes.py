"""
All HTTP endpoints for the SQLyse API. Business logic (scan lifecycle,
threading, cancellation) lives in scan_manager.py; report byte-generation
lives in report.py. This file is just request parsing, validation, and
response shaping.
"""
from urllib.parse import urlparse

from flask import Blueprint, Response, jsonify, request

from . import report, scan_manager
from .config import Config

api = Blueprint("api", __name__, url_prefix="/api")

SUPPORTED_REPORT_FORMATS = ("json", "csv", "pdf")


def _error(message: str, status: int):
    return jsonify({"error": message}), status


def _is_valid_url(url: str) -> bool:
    try:
        parsed = urlparse(url)
        return parsed.scheme in ("http", "https") and bool(parsed.netloc)
    except Exception:
        return False


@api.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "service": "sqlyse-backend",
        "mockScanner": Config.USE_MOCK_SCANNER,
    })


@api.route("/scans", methods=["POST"])
def create_scan():
    payload = request.get_json(silent=True)
    if payload is None:
        return _error("Request body must be valid JSON", 400)
    if not isinstance(payload, dict):
        return _error("Request body must be a JSON object", 400)

    target_url = payload.get("targetUrl")
    if not isinstance(target_url, str):
        return _error("Field 'targetUrl' is required", 400)
    target_url = target_url.strip()
    if not target_url:
        return _error("Field 'targetUrl' is required", 400)
    if not _is_valid_url(target_url):
        return _error("Field 'targetUrl' must be a valid http(s) URL", 400)

    record = scan_manager.create_scan(target_url)

    return jsonify({
        "scanId": record["scanId"],
        "status": record["status"],
        "progress": record["progress"],
        "phase": record["phase"],
    }), 202


@api.route("/scans/<scan_id>/status", methods=["GET"])
def scan_status(scan_id):
    record = scan_manager.get_scan(scan_id)
    if record is None:
        return _error("Unknown scan ID", 404)

    return jsonify({
        "scanId": record["scanId"],
        "status": record["status"],
        "progress": record["progress"],
        "phase": record["phase"],
        "elapsedSeconds": round(scan_manager.elapsed_seconds(record), 1),
        "logs": record["logs"],
        "error": record["error"],
    })


@api.route("/scans/<scan_id>/results", methods=["GET"])
def scan_results(scan_id):
    record = scan_manager.get_scan(scan_id)
    if record is None:
        return _error("Unknown scan ID", 404)

    if record["status"] != "completed":
        return jsonify({
            "error": "Scan is not finished yet",
            "status": record["status"],
            "progress": record["progress"],
            "phase": record["phase"],
        }), 409

    return jsonify(record["result"])


@api.route("/scans/<scan_id>/cancel", methods=["POST"])
def cancel_scan(scan_id):
    ok, body = scan_manager.cancel_scan(scan_id)
    if not ok:
        status_code = 404 if body.get("error") == "Scan not found" else 409
        return jsonify(body), status_code

    return jsonify({
        "scanId": body["scanId"],
        "status": body["status"],
        "progress": body["progress"],
        "phase": body["phase"],
    })


@api.route("/scans/<scan_id>/report", methods=["GET"])
def scan_report(scan_id):
    fmt = (request.args.get("format") or "").strip().lower()
    if fmt not in SUPPORTED_REPORT_FORMATS:
        return _error(
            f"Unsupported report format '{fmt or ''}'. Use one of: "
            f"{', '.join(SUPPORTED_REPORT_FORMATS)}",
            400,
        )

    record = scan_manager.get_scan(scan_id)
    if record is None:
        return _error("Unknown scan ID", 404)

    if record["status"] != "completed":
        return jsonify({
            "error": "Scan is not finished yet",
            "status": record["status"],
        }), 409

    content, mimetype, filename = report.generate(record["result"], fmt)
    return Response(
        content, mimetype=mimetype,
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
