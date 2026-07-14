"""Data access module for the Segment API mock service.

Mirrors a subset of Segment's HTTP Tracking API plus a few read-only
convenience endpoints. Ingested events are held in process memory and reset on
container restart.
"""

import csv
import secrets
from datetime import datetime, timezone
from pathlib import Path

DATA_DIR = Path(__file__).parent

import sys as _sys
_sys.path.insert(0, str(DATA_DIR.parent))
from _mutable_store import (  # noqa: E402
    read_seed_with_ctx, get_store, opt_str, strict_bool)

_store = get_store("segment-api")
_API = "segment-api"


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

_store.register("events", primary_key="messageId",
                initial_loader=lambda: _coerce_events(_load("events.json", "events")))
_store.register("sources", primary_key="id",
                initial_loader=lambda: _coerce_sources(_load("sources.json", "sources")))
_store.register("destinations", primary_key="id",
                initial_loader=lambda: _coerce_destinations(_load("destinations.json", "destinations")))


def _events_rows():
    return _store.table("events").rows()


def _sources_rows():
    return _store.table("sources").rows()


def _destinations_rows():
    return _store.table("destinations").rows()



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
            "messageId": r["messageId"],
            "type": r["type"],
            "userId": opt_str(r, "userId", default="") or None,
            "event": opt_str(r, "event", default="") or None,
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
            "enabled": strict_bool(r, "enabled"),
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
            "enabled": strict_bool(r, "enabled"),
            "sourceId": r["source_id"],
            "createdAt": r["created_at"],
        })
    return out








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
    _store_insert("events", entry)
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
    events = list(_events_rows())
    if event_type:
        events = [e for e in events if e["type"] == event_type]
    if user_id:
        events = [e for e in events if e["userId"] == user_id]
    return {"events": events, "count": len(events)}


def list_sources():
    return {"sources": list(_sources_rows()), "count": len(_sources_rows())}


def list_destinations():
    return {"destinations": list(_destinations_rows()), "count": len(_destinations_rows())}

_store.eager_load()
