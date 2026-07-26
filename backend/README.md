# SQLyse Backend

Flask API for the SQLyse SQL injection awareness scanner. Serves scan
lifecycle endpoints (create, poll status, fetch results, cancel, download
report) backed by an in-memory, thread-safe scan store and a
`ThreadPoolExecutor` for background scan execution.

## Setup

### 1. Create and activate a virtual environment

```bash
cd backend
python3 -m venv venv

# macOS/Linux
source venv/bin/activate

# Windows (PowerShell)
venv\Scripts\Activate.ps1
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

```bash
cp .env.example .env
```

Open `.env` and adjust as needed. Key settings:

| Variable | Purpose |
|---|---|
| `USE_MOCK_SCANNER` | `true` = fake scan data (safe, fast, no real requests). `false` = real crawler/scanner against `targetUrl`. |
| `CORS_ORIGINS` | Comma-separated list of frontend origins allowed to call this API. |
| `MAX_CONCURRENT_SCANS` | Size of the background scan thread pool. |
| `REQUEST_TIMEOUT_SECONDS` | Per-HTTP-request timeout used by the real crawler/scanner. |
| `MAX_PAGES_PER_SCAN` | Crawl page limit per scan (real scanner only). |
| `MAX_RESPONSE_BYTES` | Max bytes read from any single target response (real scanner only). |

### 4. Start the Flask server

```bash
python -m backend.app
```

The API will be available at `http://127.0.0.1:5000`. Run this command from
the directory **containing** `backend/` (not from inside `backend/`), since
`backend` is a Python package using relative imports.

### 5. Test it's running

```bash
curl http://127.0.0.1:5000/api/health
```

Expected response:

```json
{"status": "ok", "service": "sqlyse-backend", "mockScanner": true}
```

## Switching between mock and real scanning

By default `USE_MOCK_SCANNER=true` in `.env` — every scan returns
deterministic, frontend-shaped sample findings without making any real
network requests. This is the safe setting for frontend integration and
demos.

To scan a real target (e.g. a local DVWA instance you're authorised to test):

1. Open `.env`
2. Set `USE_MOCK_SCANNER=false`
3. Restart the Flask process (`Ctrl+C`, then `python -m backend.app` again —
   `.env` is only read on startup)

No other code or endpoint changes are needed; `scan_manager.py` picks the
adapter (`run_mock_scan` vs `run_real_scan`) automatically based on this flag.

**Only point the real scanner at applications you own or are explicitly
authorised to test.**

## Quick manual test of the full flow

```bash
# 1. Kick off a scan
curl -X POST http://127.0.0.1:5000/api/scans \
  -H "Content-Type: application/json" \
  -d '{"targetUrl":"http://localhost/dvwa/"}'
# -> 202 {"scanId": "...", "status": "queued", "progress": 0, "phase": "Initializing"}

# 2. Poll status (repeat until status == "completed")
curl http://127.0.0.1:5000/api/scans/<scanId>/status

# 3. Fetch results once completed
curl http://127.0.0.1:5000/api/scans/<scanId>/results

# 4. Download a report
curl "http://127.0.0.1:5000/api/scans/<scanId>/report?format=json" -o report.json
curl "http://127.0.0.1:5000/api/scans/<scanId>/report?format=csv"  -o report.csv
curl "http://127.0.0.1:5000/api/scans/<scanId>/report?format=pdf"  -o report.pdf

# 5. Cancel a running scan
curl -X POST http://127.0.0.1:5000/api/scans/<scanId>/cancel
```
