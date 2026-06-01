"""Data access module for the Calendly API mock service."""

import csv
import json
import uuid
from copy import deepcopy
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).parent

BASE_URI = "https://api.calendly.com"


def _load(filename):
    with open(DATA_DIR / filename, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


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
            **r,
            "duration": int(r["duration"]),
            "active": _to_bool(r["active"]),
        })
    return out


def _coerce_scheduled_events(rows):
    out = []
    for r in rows:
        out.append({
            **r,
            "canceled_reason": r["canceled_reason"] or None,
        })
    return out


def _coerce_invitees(rows):
    out = []
    for r in rows:
        out.append({
            **r,
            "questions_and_answers": _parse_qa(r["questions_and_answers"]),
        })
    return out


def _coerce_availability(rows):
    return [{**r} for r in rows]


with open(DATA_DIR / "user.json", encoding="utf-8") as _f:
    _user = json.load(_f)

_event_types = _coerce_event_types(_load("event_types.csv"))
_scheduled_events = _coerce_scheduled_events(_load("scheduled_events.csv"))
_invitees = _coerce_invitees(_load("invitees.csv"))
_availability = _coerce_availability(_load("availability.csv"))

_user_store = deepcopy(_user)
_event_types_store = deepcopy(_event_types)
_scheduled_events_store = deepcopy(_scheduled_events)
_invitees_store = deepcopy(_invitees)
_availability_store = deepcopy(_availability)


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
    return {"resource": _user_obj(_user_store)}


# ---------------------------------------------------------------------------
# Event types
# ---------------------------------------------------------------------------

def list_event_types(user=None):
    owner = _strip_uri(user) if user else None
    items = _event_types_store
    if owner:
        items = [e for e in items if e["owner"] == owner]
    return {"collection": [_event_type_obj(e) for e in items],
            "pagination": {"count": len(items), "next_page": None}}


def get_event_type(uuid_):
    uuid_ = _strip_uri(uuid_)
    for e in _event_types_store:
        if e["uuid"] == uuid_:
            return {"resource": _event_type_obj(e)}
    return {"error": f"event type {uuid_} not found"}


# ---------------------------------------------------------------------------
# Scheduled events
# ---------------------------------------------------------------------------

def list_scheduled_events(user=None, status=None):
    owner = _strip_uri(user) if user else None
    items = _scheduled_events_store
    if owner:
        items = [ev for ev in items if ev["owner"] == owner]
    if status:
        items = [ev for ev in items if ev["status"] == status]
    return {"collection": [_event_obj(ev) for ev in items],
            "pagination": {"count": len(items), "next_page": None}}


def get_scheduled_event(uuid_):
    uuid_ = _strip_uri(uuid_)
    for ev in _scheduled_events_store:
        if ev["uuid"] == uuid_:
            return {"resource": _event_obj(ev)}
    return {"error": f"scheduled event {uuid_} not found"}


def list_invitees(event_uuid):
    event_uuid = _strip_uri(event_uuid)
    if not any(ev["uuid"] == event_uuid for ev in _scheduled_events_store):
        return {"error": f"scheduled event {event_uuid} not found"}
    items = [inv for inv in _invitees_store if inv["event"] == event_uuid]
    return {"collection": [_invitee_obj(inv) for inv in items],
            "pagination": {"count": len(items), "next_page": None}}


def book_event(payload):
    event_type = _strip_uri(payload.get("event_type"))
    et = next((e for e in _event_types_store if e["uuid"] == event_type), None)
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
    _scheduled_events_store.append(event)

    invitee = payload.get("invitee") or {}
    if invitee.get("email"):
        _invitees_store.append({
            "uuid": f"inv-{_new_uuid()}",
            "event": uuid_,
            "name": invitee.get("name", ""),
            "email": invitee["email"],
            "status": "active",
            "timezone": invitee.get("timezone", _user_store["timezone"]),
            "created_at": now,
            "questions_and_answers": [],
        })
    return {"resource": _event_obj(event)}


def cancel_event(uuid_, reason=None):
    uuid_ = _strip_uri(uuid_)
    for ev in _scheduled_events_store:
        if ev["uuid"] == uuid_:
            ev["status"] = "canceled"
            ev["canceled_reason"] = reason or "Canceled by host"
            for inv in _invitees_store:
                if inv["event"] == uuid_:
                    inv["status"] = "canceled"
            return {"resource": {
                "canceled_by": _user_store["name"],
                "reason": ev["canceled_reason"],
                "canceler_type": "host",
            }}
    return {"error": f"scheduled event {uuid_} not found"}
