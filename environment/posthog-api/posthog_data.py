"""Data access module for the PostHog API mock service.

Mirrors a subset of PostHog: the capture endpoint, the project events /
persons / feature flags read APIs, and the /decide flag-evaluation endpoint.
Captured events are held in process memory and reset on container restart.
"""

import csv
from datetime import datetime, timezone
from pathlib import Path

DATA_DIR = Path(__file__).parent

import sys as _sys
_sys.path.insert(0, str(DATA_DIR.parent))
from _mutable_store import (
    read_seed_with_ctx, get_store,
    strict_int,
    strict_bool,
)

_store = get_store("posthog-api")
_API = "posthog-api"


def _store_insert(_table, _row):
    """Persist a newly-created row into the shared store (drift/injection-safe).

    Synthesizes the table's registered primary key from the row's ``id`` field
    when the row doesn't already carry it, so creates work regardless of whether
    the table was registered with primary_key="id" or a domain-specific key.
    """
    _t = _store.table(_table)
    if _t.primary_key not in _row and "id" in _row:
        _row = {**_row, _t.primary_key: _row["id"]}
    return _t.upsert(_row)

_store.register("events", primary_key="id",
                initial_loader=lambda: _coerce_events(_load("events.json", "events")))
_store.register("flags", primary_key="id",
                initial_loader=lambda: _coerce_flags(_load("feature_flags.json", "flags")))
_store.register("persons", primary_key="id",
                initial_loader=lambda: _coerce_persons(_load("persons.json", "persons")))


def _events_rows():
    return _store.table("events").rows()


def _flags_rows():
    return _store.table("flags").rows()


def _persons_rows():
    return _store.table("persons").rows()



def _load(filename, table):
    return read_seed_with_ctx(DATA_DIR / filename, _API, table)


def _strip_ctx(r):
    return {k: v for k, v in r.items() if not k.startswith("__")}


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
            "project_id": strict_int(r, "project_id"),
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
            "project_id": strict_int(r, "project_id"),
            "key": r["key"],
            "name": r["name"],
            "active": strict_bool(r, "active"),
            "rollout_percentage": strict_int(r, "rollout_percentage"),
        })
    return out


def _coerce_persons(rows):
    out = []
    for r in rows:
        out.append({
            "id": r["id"],
            "project_id": strict_int(r, "project_id"),
            "distinct_id": r["distinct_id"],
            "name": r["name"],
            "email": r["email"],
            "created_at": r["created_at"],
        })
    return out








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
    _store_insert("events", {
        "id": f"evt_{len(_events_rows()) + 1:05d}",
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
    events = [e for e in _events_rows() if e["project_id"] == int(project_id)]
    if event:
        events = [e for e in events if e["event"] == event]
    if distinct_id:
        events = [e for e in events if e["distinct_id"] == distinct_id]
    return {"results": events, "count": len(events)}


def list_feature_flags(project_id):
    flags = [f for f in _flags_rows() if f["project_id"] == int(project_id)]
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
    persons = [p for p in _persons_rows() if p["project_id"] == int(project_id)]
    results = [_serialize_person(p) for p in persons]
    return {"results": results, "count": len(results)}


# ---------------------------------------------------------------------------
# Decide (flag evaluation)
# ---------------------------------------------------------------------------

def decide(payload):
    distinct_id = payload.get("distinct_id")
    project_id = int(payload.get("project_id") or 1)
    flags = [f for f in _flags_rows() if f["project_id"] == project_id]
    enabled = {}
    for f in flags:
        enabled[f["key"]] = bool(f["active"] and f["rollout_percentage"] > 0)
    return {
        "featureFlags": enabled,
        "distinctId": distinct_id,
    }

_store.eager_load()
