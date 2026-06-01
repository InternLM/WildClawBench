"""Data access module for the PostHog API mock service.

Mirrors a subset of PostHog: the capture endpoint, the project events /
persons / feature flags read APIs, and the /decide flag-evaluation endpoint.
Captured events are held in process memory and reset on container restart.
"""

import csv
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path

DATA_DIR = Path(__file__).parent


def _load(filename):
    with open(DATA_DIR / filename, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _to_bool(v):
    return str(v).strip().lower() == "true"


def _parse_props(raw):
    props = {}
    for pair in (raw or "").split(";"):
        if not pair:
            continue
        key, _, val = pair.partition("=")
        props[key] = val
    return props


# ---------------------------------------------------------------------------
# Load + coerce
# ---------------------------------------------------------------------------

def _coerce_events(rows):
    out = []
    for r in rows:
        out.append({
            "id": r["id"],
            "project_id": int(r["project_id"]),
            "distinct_id": r["distinct_id"],
            "event": r["event"],
            "timestamp": r["timestamp"],
            "properties": _parse_props(r["properties"]),
        })
    return out


def _coerce_flags(rows):
    out = []
    for r in rows:
        out.append({
            "id": r["id"],
            "project_id": int(r["project_id"]),
            "key": r["key"],
            "name": r["name"],
            "active": _to_bool(r["active"]),
            "rollout_percentage": int(r["rollout_percentage"]),
        })
    return out


def _coerce_persons(rows):
    out = []
    for r in rows:
        out.append({
            "id": r["id"],
            "project_id": int(r["project_id"]),
            "distinct_id": r["distinct_id"],
            "name": r["name"],
            "email": r["email"],
            "created_at": r["created_at"],
        })
    return out


_events = _coerce_events(_load("events.csv"))
_flags = _coerce_flags(_load("feature_flags.csv"))
_persons = _coerce_persons(_load("persons.csv"))

_events_store = deepcopy(_events)
_flags_store = deepcopy(_flags)
_persons_store = deepcopy(_persons)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _serialize_flag(f):
    return {
        "id": f["id"],
        "key": f["key"],
        "name": f["name"],
        "active": f["active"],
        "rollout_percentage": f["rollout_percentage"],
    }


def _serialize_person(p):
    return {
        "id": p["id"],
        "distinct_ids": [p["distinct_id"]],
        "name": p["name"],
        "properties": {"email": p["email"], "name": p["name"]},
        "created_at": p["created_at"],
    }


# ---------------------------------------------------------------------------
# Capture (write)
# ---------------------------------------------------------------------------

def capture(payload):
    _events_store.append({
        "id": f"evt_{len(_events_store) + 1:05d}",
        "project_id": int(payload.get("project_id") or 1),
        "distinct_id": payload.get("distinct_id"),
        "event": payload.get("event") or "$pageview",
        "timestamp": payload.get("timestamp") or _now_iso(),
        "properties": payload.get("properties") or {},
    })
    return {"status": 1}


# ---------------------------------------------------------------------------
# Project reads
# ---------------------------------------------------------------------------

def list_events(project_id, event=None, distinct_id=None):
    events = [e for e in _events_store if e["project_id"] == int(project_id)]
    if event:
        events = [e for e in events if e["event"] == event]
    if distinct_id:
        events = [e for e in events if e["distinct_id"] == distinct_id]
    return {"results": events, "count": len(events)}


def list_feature_flags(project_id):
    flags = [f for f in _flags_store if f["project_id"] == int(project_id)]
    results = [
        {
            "id": f["id"],
            "key": f["key"],
            "name": f["name"],
            "active": f["active"],
            "rollout_percentage": f["rollout_percentage"],
        }
        for f in flags
    ]
    return {"results": results, "count": len(results)}


def list_persons(project_id):
    persons = [p for p in _persons_store if p["project_id"] == int(project_id)]
    results = [_serialize_person(p) for p in persons]
    return {"results": results, "count": len(results)}


# ---------------------------------------------------------------------------
# Decide (flag evaluation)
# ---------------------------------------------------------------------------

def decide(payload):
    distinct_id = payload.get("distinct_id")
    project_id = int(payload.get("project_id") or 1)
    flags = [f for f in _flags_store if f["project_id"] == project_id]
    enabled = {}
    for f in flags:
        enabled[f["key"]] = bool(f["active"] and f["rollout_percentage"] > 0)
    return {
        "featureFlags": enabled,
        "distinctId": distinct_id,
    }
