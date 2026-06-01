"""Data access module for the Segment API mock service.

Mirrors a subset of Segment's HTTP Tracking API plus a few read-only
convenience endpoints. Ingested events are held in process memory and reset on
container restart.
"""

import csv
import secrets
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
            "messageId": r["messageId"],
            "type": r["type"],
            "userId": r["userId"] or None,
            "event": r["event"] or None,
            "timestamp": r["timestamp"],
            "properties": _parse_props(r["properties"]),
        })
    return out


def _coerce_sources(rows):
    out = []
    for r in rows:
        out.append({
            "id": r["id"],
            "name": r["name"],
            "slug": r["slug"],
            "enabled": _to_bool(r["enabled"]),
            "type": r["type"],
            "createdAt": r["created_at"],
        })
    return out


def _coerce_destinations(rows):
    out = []
    for r in rows:
        out.append({
            "id": r["id"],
            "name": r["name"],
            "slug": r["slug"],
            "enabled": _to_bool(r["enabled"]),
            "sourceId": r["source_id"],
            "createdAt": r["created_at"],
        })
    return out


_events = _coerce_events(_load("events.csv"))
_sources = _coerce_sources(_load("sources.csv"))
_destinations = _coerce_destinations(_load("destinations.csv"))

_events_store = deepcopy(_events)
_sources_store = deepcopy(_sources)
_destinations_store = deepcopy(_destinations)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _new_message_id():
    return "msg_" + secrets.token_hex(8)


def _ingest(event_type, payload):
    entry = {
        "messageId": payload.get("messageId") or _new_message_id(),
        "type": event_type,
        "userId": payload.get("userId") or payload.get("anonymousId"),
        "event": payload.get("event"),
        "timestamp": payload.get("timestamp") or _now_iso(),
        "properties": payload.get("properties") or payload.get("traits") or {},
    }
    if event_type == "page" and payload.get("name"):
        entry["properties"].setdefault("name", payload["name"])
    _events_store.append(entry)
    return entry


# ---------------------------------------------------------------------------
# Tracking API (writes)
# ---------------------------------------------------------------------------

def track(payload):
    _ingest("track", payload)
    return {"success": True}


def identify(payload):
    _ingest("identify", payload)
    return {"success": True}


def page(payload):
    _ingest("page", payload)
    return {"success": True}


def batch(payload):
    items = payload.get("batch") or []
    for item in items:
        _ingest(item.get("type") or "track", item)
    return {"success": True, "ingested": len(items)}


# ---------------------------------------------------------------------------
# Read-only convenience endpoints
# ---------------------------------------------------------------------------

def list_events(event_type=None, user_id=None):
    events = list(_events_store)
    if event_type:
        events = [e for e in events if e["type"] == event_type]
    if user_id:
        events = [e for e in events if e["userId"] == user_id]
    return {"events": events, "count": len(events)}


def list_sources():
    return {"sources": list(_sources_store), "count": len(_sources_store)}


def list_destinations():
    return {"destinations": list(_destinations_store), "count": len(_destinations_store)}
