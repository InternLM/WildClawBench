"""Data access module for the Calendly API mock service."""

import csv
import json
import uuid
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).parent

import sys as _sys
_sys.path.insert(0, str(DATA_DIR.parent))
from _mutable_store import (
    read_seed_with_ctx, get_store, opt_str, strict_bool, strict_int)

_store = get_store("calendly-api")
_API = "calendly-api"


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

_store.register("event_types", primary_key="uuid",
                initial_loader=lambda: _coerce_event_types(_load("event_types.json", "event_types")))
_store.register("scheduled_events", primary_key="uuid",
                initial_loader=lambda: _coerce_scheduled_events(_load("scheduled_events.json", "scheduled_events")))
_store.register("invitees", primary_key="uuid",
                initial_loader=lambda: _coerce_invitees(_load("invitees.json", "invitees")))
_store.register("availability", primary_key="_pk",
                initial_loader=lambda: [
                    {**r, "_pk": f"{r['owner']}@{r['weekday']}@{r['start_time']}"}
                    for r in _coerce_availability(_load("availability.json", "availability"))])
_store.register_document("user", initial_loader=lambda: __import__('json').load(open(DATA_DIR / "user.json", encoding="utf-8")))


def _event_types_rows():
    return _store.table("event_types").rows()


def _scheduled_events_rows():
    return _store.table("scheduled_events").rows()


def _invitees_rows():
    return _store.table("invitees").rows()


def _availability_rows():
    return [{k: v for k, v in r.items() if k != "_pk"} for r in _store.table("availability").rows()]


def _user_doc():
    return _store.document("user").get()


BASE_URI = "https://api.calendly.com"


def _load(filename, table):
    return read_seed_with_ctx(DATA_DIR / filename, _API, table)


def _strip_ctx(r):
    return {k: v for k, v in r.items() if not k.startswith("__")}


def _now():
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000000Z")


def _to_bool(v):
    return str(v).strip().lower() == "true"


def _parse_qa(raw):
    out = []
    if not raw:
        return out
    for pair in raw.split(";"):
        pair = pair.strip()
        if not pair or "|" not in pair:
            continue
        q, a = pair.split("|", 1)
        out.append({"question": q, "answer": a})
    return out


# ---------------------------------------------------------------------------
# Load + coerce
# ---------------------------------------------------------------------------

def _coerce_event_types(rows):
    out = []
    for r in rows:
        out.append({
            **_strip_ctx(r),
            "duration": strict_int(r, "duration"),
            "active": strict_bool(r, "active"),
        })
    return out


def _coerce_scheduled_events(rows):
    out = []
    for r in rows:
        out.append({
            **_strip_ctx(r),
            "canceled_reason": opt_str(r, "canceled_reason", default="") or None,
        })
    return out


def _coerce_invitees(rows):
    out = []
    for r in rows:
        out.append({
            **_strip_ctx(r),
            "questions_and_answers": _parse_qa(r["questions_and_answers"]),
        })
    return out


def _coerce_availability(rows):
    return [{**_strip_ctx(r)} for r in rows]



def _new_uuid():
    return uuid.uuid4().hex[:12]


def _user_uri(uuid_):
    return f"{BASE_URI}/users/{uuid_}"


def _event_type_uri(uuid_):
    return f"{BASE_URI}/event_types/{uuid_}"


def _event_uri(uuid_):
    return f"{BASE_URI}/scheduled_events/{uuid_}"


def _invitee_uri(event_uuid, uuid_):
    return f"{BASE_URI}/scheduled_events/{event_uuid}/invitees/{uuid_}"


def _strip_uri(value):
    # Accept either a bare uuid or a full Calendly URI; return the trailing segment.
    if not value:
        return value
    return value.rstrip("/").rsplit("/", 1)[-1]


# ---------------------------------------------------------------------------
# Serializers
# ---------------------------------------------------------------------------

def _user_obj(u):
    return {
        "uri": _user_uri(u["uuid"]),
        "name": u["name"],
        "slug": u["slug"],
        "email": u["email"],
        "scheduling_url": u["scheduling_url"],
        "timezone": u["timezone"],
        "current_organization": f"{BASE_URI}/organizations/{u['current_organization']}",
        "created_at": u["created_at"],
        "updated_at": u["updated_at"],
    }


def _event_type_obj(e):
    return {
        "uri": _event_type_uri(e["uuid"]),
        "name": e["name"],
        "slug": e["slug"],
        "duration": e["duration"],
        "kind": e["kind"],
        "color": e["color"],
        "active": e["active"],
        "description_plain": e["description"],
        "scheduling_url": e["scheduling_url"],
        "profile": {"owner": _user_uri(e["owner"])},
        "created_at": e["created_at"],
    }


def _event_obj(ev):
    return {
        "uri": _event_uri(ev["uuid"]),
        "name": ev["name"],
        "status": ev["status"],
        "start_time": ev["start_time"],
        "end_time": ev["end_time"],
        "event_type": _event_type_uri(ev["event_type"]),
        "location": {"type": ev["location_type"], "location": ev["location"]},
        "event_memberships": [{"user": _user_uri(ev["owner"])}],
        "cancellation": ({"reason": ev["canceled_reason"], "canceler_type": "host"}
                         if ev["status"] == "canceled" and ev["canceled_reason"] else None),
        "created_at": ev["created_at"],
    }


def _invitee_obj(inv):
    return {
        "uri": _invitee_uri(inv["event"], inv["uuid"]),
        "name": inv["name"],
        "email": inv["email"],
        "status": inv["status"],
        "timezone": inv["timezone"],
        "event": _event_uri(inv["event"]),
        "questions_and_answers": inv["questions_and_answers"],
        "created_at": inv["created_at"],
    }


# ---------------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------------

def get_me():
    return {"resource": _user_obj(_user_doc())}


# ---------------------------------------------------------------------------
# Event types
# ---------------------------------------------------------------------------

def list_event_types(user=None):
    owner = _strip_uri(user) if user else None
    items = _event_types_rows()
    if owner:
        items = [e for e in items if e["owner"] == owner]
    return {"collection": [_event_type_obj(e) for e in items],
            "pagination": {"count": len(items), "next_page": None}}


def get_event_type(uuid_):
    uuid_ = _strip_uri(uuid_)
    for e in _event_types_rows():
        if e["uuid"] == uuid_:
            return {"resource": _event_type_obj(e)}
    return {"error": f"event type {uuid_} not found"}


# ---------------------------------------------------------------------------
# Scheduled events
# ---------------------------------------------------------------------------

def list_scheduled_events(user=None, status=None):
    owner = _strip_uri(user) if user else None
    items = _scheduled_events_rows()
    if owner:
        items = [ev for ev in items if ev["owner"] == owner]
    if status:
        items = [ev for ev in items if ev["status"] == status]
    return {"collection": [_event_obj(ev) for ev in items],
            "pagination": {"count": len(items), "next_page": None}}


def get_scheduled_event(uuid_):
    uuid_ = _strip_uri(uuid_)
    for ev in _scheduled_events_rows():
        if ev["uuid"] == uuid_:
            return {"resource": _event_obj(ev)}
    return {"error": f"scheduled event {uuid_} not found"}


def list_invitees(event_uuid):
    event_uuid = _strip_uri(event_uuid)
    if not any(ev["uuid"] == event_uuid for ev in _scheduled_events_rows()):
        return {"error": f"scheduled event {event_uuid} not found"}
    items = [inv for inv in _invitees_rows() if inv["event"] == event_uuid]
    return {"collection": [_invitee_obj(inv) for inv in items],
            "pagination": {"count": len(items), "next_page": None}}


def book_event(payload):
    event_type = _strip_uri(payload.get("event_type"))
    et = next((e for e in _event_types_rows() if e["uuid"] == event_type), None)
    if et is None:
        return {"error": f"event type {event_type} not found"}

    uuid_ = f"sev-{_new_uuid()}"
    now = _now()
    event = {
        "uuid": uuid_,
        "owner": et["owner"],
        "event_type": event_type,
        "name": et["name"],
        "status": "active",
        "start_time": payload.get("start_time", now),
        "end_time": payload.get("end_time", now),
        "location_type": payload.get("location_type", "zoom"),
        "location": payload.get("location", ""),
        "created_at": now,
        "canceled_reason": None,
    }
    _store_insert("scheduled_events", event)

    invitee = payload.get("invitee") or {}
    if invitee.get("email"):
        _store_insert("invitees", {
            "uuid": f"inv-{_new_uuid()}",
            "event": uuid_,
            "name": invitee.get("name", ""),
            "email": invitee["email"],
            "status": "active",
            "timezone": invitee.get("timezone", _user_doc()["timezone"]),
            "created_at": now,
            "questions_and_answers": [],
        })
    return {"resource": _event_obj(event)}


def cancel_event(uuid_, reason=None):
    uuid_ = _strip_uri(uuid_)
    for ev in _scheduled_events_rows():
        if ev["uuid"] == uuid_:
            ev["status"] = "canceled"
            ev["canceled_reason"] = reason or "Canceled by host"
            for inv in _invitees_rows():
                if inv["event"] == uuid_:
                    inv["status"] = "canceled"
            return {"resource": {
                "canceled_by": _user_doc()["name"],
                "reason": ev["canceled_reason"],
                "canceler_type": "host",
            }}
    return {"error": f"scheduled event {uuid_} not found"}

_store.eager_load()
