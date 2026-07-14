"""Offline audit shim — auto-loaded by pytest as `conftest.py`.

Drop this next to `test_outputs.py` + `agent_state.json` (the retest harness
does this for you). Before any test runs, it redirects the test module's HTTP
calls to the SAVED audit diary in `agent_state.json`, so the suite runs fully
offline — no live mock stack, no Docker.

It serves the two endpoints the suites query:
  * GET /audit/summary  -> {"total_requests", "endpoints"}   (counts)
  * GET /audit/requests -> {"total", "requests": [...]}        (full diary)

`/audit/summary` is derived from the saved diary when only `requests` were
persisted, so it works whether the run saved counts, the full diary, or both.

Limitation: only endpoints the agent actually hit during the original run are in
the diary. A test asking about a call that never happened cannot be answered
offline (it raises URLError, surfacing as an ERROR — never a false PASS).

Delete this file to restore live-network behavior unchanged.
"""
from __future__ import annotations

import json
from pathlib import Path
from urllib.error import URLError

import test_outputs as _T

_STATE = Path(__file__).with_name("agent_state.json")
try:
    _AUDIT = json.loads(_STATE.read_text(encoding="utf-8")).get("audit", {}) if _STATE.is_file() else {}
except (OSError, json.JSONDecodeError):
    _AUDIT = {}


def _svc_from_const(name: str) -> str:
    # SENTRY_API_URL -> sentry-api ; GOOGLE_CALENDAR_API_URL -> google-calendar-api
    core = name[: -len("_API_URL")]
    return core.lower().replace("_", "-") + "-api"


# Map every base URL the test module knows -> its audit service key.
_URL2SVC: dict[str, str] = {}
for _name in dir(_T):
    if _name.endswith("_API_URL"):
        _val = getattr(_T, _name)
        if isinstance(_val, str) and _val:
            _URL2SVC[_val.rstrip("/")] = _svc_from_const(_name)


def _summary_for(blob: dict) -> dict:
    """Return a /audit/summary-shaped dict, deriving counts from the diary if
    only `requests` were saved."""
    if not isinstance(blob, dict):
        return {"total_requests": 0, "endpoints": {}}
    if blob.get("endpoints"):
        return {
            "total_requests": blob.get("total_requests", 0),
            "endpoints": blob.get("endpoints", {}),
        }
    eps: dict[str, dict] = {}
    reqs = blob.get("requests") or []
    for r in reqs:
        key = f"{r.get('method', '')} {r.get('path', '')}".strip()
        e = eps.setdefault(key, {"count": 0, "statuses": {}})
        e["count"] += 1
        st = str(r.get("status_code", "") or "")
        if st:
            e["statuses"][st] = e["statuses"].get(st, 0) + 1
    return {"total_requests": len(reqs), "endpoints": eps}


def _serve(svc: str, endpoint: str):
    blob = _AUDIT.get(svc, {})
    if endpoint.startswith("/audit/summary"):
        return _summary_for(blob)
    if endpoint.startswith("/audit/requests"):
        reqs = blob.get("requests") if isinstance(blob, dict) else None
        reqs = reqs or []
        return {"total": len(reqs), "requests": reqs}
    raise URLError(f"offline: no saved data for {svc}{endpoint}")


def _fake_request(method, url, data=None):
    for base, svc in _URL2SVC.items():
        if url.startswith(base):
            return _serve(svc, url[len(base):])
    raise URLError(f"offline: unknown service URL {url}")


# Swap the network primitive in the test module for the offline one. `api_get`
# (and any api_post/api_delete) call `_request`, so this one patch covers them.
_T._request = _fake_request
