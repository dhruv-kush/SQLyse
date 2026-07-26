"""
Central configuration. Everything sensitive/environment-specific comes from
.env (see .env.example) - nothing is hard-coded here.
"""
import os
from dotenv import load_dotenv

load_dotenv()  # reads .env in the working directory if present


def _bool(name: str, default: str = "false") -> bool:
    return os.getenv(name, default).strip().lower() in ("1", "true", "yes", "on")


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me")

    CORS_ORIGINS = [
        origin.strip()
        for origin in os.getenv("CORS_ORIGINS", "*").split(",")
        if origin.strip()
    ]

    # If true, /api/scans uses the fake adapter (scanner/mock_adapter.py) instead
    # of Dhruv's real crawler+scanner. Flip to false once crawler.py/scanner.py
    # are wired in and tested.
    USE_MOCK_SCANNER = _bool("USE_MOCK_SCANNER", "true")

    MAX_CONCURRENT_SCANS = int(os.getenv("MAX_CONCURRENT_SCANS", "3"))
    REQUEST_TIMEOUT_SECONDS = int(os.getenv("REQUEST_TIMEOUT_SECONDS", "10"))
    MAX_PAGES_PER_SCAN = int(os.getenv("MAX_PAGES_PER_SCAN", "25"))

    # Hard cap on how many bytes of any single HTTP response body the crawler
    # or scanner will read, so a huge or malicious response can't exhaust
    # memory mid-scan. Default 2MB is generous for HTML pages.
    MAX_RESPONSE_BYTES = int(os.getenv("MAX_RESPONSE_BYTES", str(2 * 1024 * 1024)))

    AI_API_KEY = os.getenv("AI_API_KEY", "")
