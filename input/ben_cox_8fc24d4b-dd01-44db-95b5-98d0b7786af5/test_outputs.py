import json
import os
import subprocess
import sqlite3
from urllib.request import Request, urlopen

try:
    import pytest
except ImportError:
    pytest = None

DOCUSIGN_API_URL = os.environ.get("DOCUSIGN_API_URL", "http://localhost:8001")
AIRTABLE_API_URL = os.environ.get("AIRTABLE_API_URL", "http://localhost:8002")
GMAIL_API_URL = os.environ.get("GMAIL_API_URL", "http://localhost:8003")
OUTLOOK_API_URL = os.environ.get("OUTLOOK_API_URL", "http://localhost:8004")
QUICKBOOKS_API_URL = os.environ.get("QUICKBOOKS_API_URL", "http://localhost:8005")
XERO_API_URL = os.environ.get("XERO_API_URL", "http://localhost:8006")

_INFRA_PREFIXES = ("/audit", "/health", "/docs", "/openapi", "/redoc", "/favicon")


def _request(method, url, data=None):
    body = None
    headers = {"Accept": "application/json"}
    if data is not None:
        body = json.dumps(data).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = Request(url, data=body, method=method, headers=headers)
    with urlopen(req, timeout=10) as resp:
        raw = resp.read().decode("utf-8")
    if not raw:
        return {}
    return json.loads(raw)


def api_get(base_url, endpoint):
    return _request("GET", f"{base_url}{endpoint}")


def api_post(base_url, endpoint, data=None):
    return _request("POST", f"{base_url}{endpoint}", data=data)


def _get(url):
    return _request("GET", url)


def _post(url, data=None):
    return _request("POST", url, data=data)


def read_file(path):
    with open(path) as f:
        return f.read()


def file_exists(path):
    return os.path.exists(path)


def _audit_requests(base_url):
    try:
        audit = api_get(base_url, "/audit/requests")
    except Exception:
        return []
    if isinstance(audit, dict):
        requests = audit.get("requests", [])
        return requests if isinstance(requests, list) else []
    if isinstance(audit, list):
        return audit
    return []


def _normalize_path(path):
    if not isinstance(path, str):
        return ""
    p = path.split("?", 1)[0].strip().lower()
    if len(p) > 1 and p.endswith("/"):
        p = p.rstrip("/")
    return p


def _is_infra_path(path):
    p = _normalize_path(path)
    if p == "" or p == "/":
        return True
    for prefix in _INFRA_PREFIXES:
        if p == prefix or p.startswith(prefix + "/") or p.startswith(prefix + "."):
            return True
    return False


def _business_entries(entries, include_methods=None, exclude_methods=None):
    out = []
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        if _is_infra_path(entry.get("path", "")):
            continue
        method = str(entry.get("method", "")).upper()
        if include_methods is not None and method not in include_methods:
            continue
        if exclude_methods is not None and method in exclude_methods:
            continue
        out.append(entry)
    return out


def _business_get_count(base_url):
    return len(_business_entries(_audit_requests(base_url), include_methods=("GET",)))


def _business_any_count(base_url):
    return len(_business_entries(_audit_requests(base_url)))


class TestOutcomeSourceBreadth:
    """Verifies the agent reached every independent source service outside the Outlook/QuickBooks pair."""

    def test_breadth_all_sources_consulted(self):
        docusign_reads = _business_get_count(DOCUSIGN_API_URL)
        airtable_reads = _business_get_count(AIRTABLE_API_URL)
        gmail_reads = _business_get_count(GMAIL_API_URL)
        assert docusign_reads > 0 and airtable_reads > 0 and gmail_reads > 0, (
            "expected business GET reads on all three independent sources; got "
            f"docusign={docusign_reads}, airtable={airtable_reads}, gmail={gmail_reads}"
        )


class TestBehavioralSourceConsultation:
    """Verifies each individual load-bearing source service was queried, via its audit log."""

    def test_docusign_envelopes_read(self):
        count = _business_get_count(DOCUSIGN_API_URL)
        assert count > 0, f"expected at least one DocuSign business GET, got {count}"

    def test_airtable_records_read(self):
        count = _business_get_count(AIRTABLE_API_URL)
        assert count > 0, f"expected at least one Airtable business GET, got {count}"

    def test_gmail_messages_read(self):
        count = _business_get_count(GMAIL_API_URL)
        assert count > 0, f"expected at least one Gmail business GET, got {count}"


class TestNegativeWeightGuardrails:
    """Detects the forbidden behavior of touching the Xero distractor service."""

    def test_xero_distractor_touched(self):
        """Negative test: passes when the forbidden behavior is detected; its negative weight contributes as a penalty. Fires when the agent made any business call to the Xero distractor service."""
        count = _business_any_count(XERO_API_URL)
        assert count > 0, f"xero distractor was touched ({count} business calls detected)"
