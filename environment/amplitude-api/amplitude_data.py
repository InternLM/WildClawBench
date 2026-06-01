"""Data access module for the Amplitude API mock service.

Mirrors a subset of Amplitude: the HTTP V2 event-upload API, the event
segmentation chart API, and the user-activity stream. Uploaded events are held
in process memory and reset on container restart.
"""

import csv
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path

DATA_DIR = Path(__file__).parent


def _load(filename):
    with open(DATA_DIR / filename, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


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
            "event_id": r["event_id"],
            "user_id": r["user_id"],
            "device_id": r["device_id"],
            "event_type": r["event_type"],
            "event_time": r["event_time"],
            "event_properties": _parse_props(r["event_properties"]),
        })
    return out


def _coerce_users(rows):
    out = []
    for r in rows:
        out.append({
            "user_id": r["user_id"],
            "device_id": r["device_id"],
            "country": r["country"],
            "platform": r["platform"],
            "version": r["version"],
            "first_seen": r["first_seen"],
            "last_seen": r["last_seen"],
        })
    return out


def _coerce_segmentation(rows):
    out = []
    for r in rows:
        out.append({
            "event_type": r["event_type"],
            "date": r["date"],
            "count": int(r["count"]),
        })
    return out


_events = _coerce_events(_load("events.csv"))
_users = _coerce_users(_load("users.csv"))
_segmentation = _coerce_segmentation(_load("segmentation.csv"))

_events_store = deepcopy(_events)
_users_store = deepcopy(_users)
_segmentation_store = deepcopy(_segmentation)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ---------------------------------------------------------------------------
# HTTP V2 event upload
# ---------------------------------------------------------------------------

def ingest(payload):
    raw_events = payload.get("events") or []
    ingested = 0
    for ev in raw_events:
        _events_store.append({
            "event_id": ev.get("insert_id") or f"ev_{len(_events_store) + 1:06d}",
            "user_id": ev.get("user_id"),
            "device_id": ev.get("device_id"),
            "event_type": ev.get("event_type") or "unknown",
            "event_time": ev.get("time") or _now_iso(),
            "event_properties": ev.get("event_properties") or {},
        })
        ingested += 1
    return {"code": 200, "events_ingested": ingested, "server_upload_time": _now_iso()}


# ---------------------------------------------------------------------------
# Event segmentation
# ---------------------------------------------------------------------------

def segmentation(event=None, start=None, end=None):
    rows = list(_segmentation_store)
    if event:
        rows = [r for r in rows if r["event_type"] == event]
    if start:
        rows = [r for r in rows if r["date"] >= start]
    if end:
        rows = [r for r in rows if r["date"] <= end]
    by_event = {}
    for r in rows:
        by_event.setdefault(r["event_type"], []).append(r)
    series = []
    series_labels = []
    xvalues = sorted({r["date"] for r in rows})
    for et in sorted(by_event):
        by_date = {r["date"]: r["count"] for r in by_event[et]}
        series.append([by_date.get(d, 0) for d in xvalues])
        series_labels.append(et)
    return {
        "data": {
            "series": series,
            "seriesLabels": series_labels,
            "xValues": xvalues,
        }
    }


# ---------------------------------------------------------------------------
# User activity
# ---------------------------------------------------------------------------

def user_activity(user):
    matched = next((u for u in _users_store if u["user_id"] == user), None)
    if not matched:
        return {"error": f"User {user} not found"}
    user_events = [e for e in _events_store if e["user_id"] == user]
    user_events = sorted(user_events, key=lambda e: e["event_time"])
    return {
        "userData": matched,
        "events": user_events,
    }
