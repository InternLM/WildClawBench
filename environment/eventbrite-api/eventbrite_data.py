"""Data access module for the Eventbrite API mock service."""

import csv
import uuid
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).parent

import sys as _sys
_sys.path.insert(0, str(DATA_DIR.parent))
from _mutable_store import (
    read_seed_with_ctx, get_store,
    strict_int,
    strict_float,
    strict_bool,
)

_API = "eventbrite-api"

_store = get_store("eventbrite-api")
_API = "eventbrite-api"



def _store_patch(_table, _row_or_pk, _updates):
    """Persist field updates to a stored row (was: in-place mutation of a copy)."""
    _t = _store.table(_table)
    _pk = _row_or_pk.get(_t.primary_key, _row_or_pk.get("id")) if isinstance(_row_or_pk, dict) else _row_or_pk
    return _t.patch(_pk, _updates)


def _store_delete(_table, _row_or_pk):
    """Persist a row deletion (was: pop/remove on a copy)."""
    _t = _store.table(_table)
    _pk = _row_or_pk.get(_t.primary_key, _row_or_pk.get("id")) if isinstance(_row_or_pk, dict) else _row_or_pk
    return _t.delete(_pk)

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
_store.register("venues", primary_key="id",
                initial_loader=lambda: _coerce_venues(_load("venues.json", "venues")))
_store.register("ticket_classes", primary_key="id",
                initial_loader=lambda: _coerce_ticket_classes(_load("ticket_classes.json", "ticket_classes")))
_store.register("attendees", primary_key="id",
                initial_loader=lambda: _coerce_attendees(_load("attendees.json", "attendees")))
_store.register("organizations", primary_key="id",
                initial_loader=lambda: [_strip_ctx(r) for r in _load("organizations.json", "organizations")])


def _events_rows():
    return _store.table("events").rows()


def _venues_rows():
    return _store.table("venues").rows()


def _ticket_classes_rows():
    return _store.table("ticket_classes").rows()


def _attendees_rows():
    return _store.table("attendees").rows()


def _organizations_rows():
    return _store.table("organizations").rows()



def _load(filename, table):
    return read_seed_with_ctx(DATA_DIR / filename, _API, table)


def _strip_ctx(r):
    return {k: v for k, v in r.items() if not k.startswith("__")}


def _now():
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


def _to_bool(v):
    return str(v).strip().lower() == "true"


def _coerce_events(rows):
    return [{**_strip_ctx(r),
             "capacity": strict_int(r, "capacity"),
             "is_free": strict_bool(r, "is_free"),
             "online_event": strict_bool(r, "online_event")} for r in rows]


def _coerce_venues(rows):
    return [{**_strip_ctx(r),
             "latitude": strict_float(r, "latitude"),
             "longitude": strict_float(r, "longitude")} for r in rows]


def _coerce_ticket_classes(rows):
    return [{**_strip_ctx(r),
             "quantity_total": strict_int(r, "quantity_total"),
             "quantity_sold": strict_int(r, "quantity_sold"),
             "cost": strict_int(r, "cost"),
             "fee": strict_int(r, "fee"),
             "free": strict_bool(r, "free")} for r in rows]


def _coerce_attendees(rows):
    return [{**_strip_ctx(r), "checked_in": strict_bool(r, "checked_in")} for r in rows]








def _new_id(prefix):
    return f"{prefix}-{uuid.uuid4().hex[:8]}"


def _serialize_event(e):
    venue = next((v for v in _venues_rows() if v["id"] == e["venue_id"]), None)
    return {
        **e,
        "name": {"text": e["name"], "html": f"<p>{e['name']}</p>"},
        "summary": e["summary"],
        "start": {"timezone": e["timezone"], "utc": e["start_utc"]},
        "end": {"timezone": e["timezone"], "utc": e["end_utc"]},
        "venue": venue,
    }


# ---------------------------------------------------------------------------
# Organizations
# ---------------------------------------------------------------------------

def list_organizations():
    return {"organizations": _organizations_rows(), "pagination": {"object_count": len(_organizations_rows())}}


def get_organization(org_id):
    for o in _organizations_rows():
        if o["id"] == org_id:
            return o
    return {"error": f"Organization {org_id} not found"}


# ---------------------------------------------------------------------------
# Events
# ---------------------------------------------------------------------------

def list_events(organization_id=None, status=None, q=None, page_size=50):
    results = list(_events_rows())
    if organization_id:
        results = [e for e in results if e["organization_id"] == organization_id]
    if status:
        results = [e for e in results if e["status"].lower() == status.lower()]
    if q:
        ql = q.lower()
        results = [e for e in results if ql in e["name"].lower() or ql in e["summary"].lower()]
    results.sort(key=lambda e: e["start_utc"])
    return {
        "events": [_serialize_event(e) for e in results[:page_size]],
        "pagination": {"object_count": len(results)},
    }


def get_event(event_id):
    for e in _events_rows():
        if e["id"] == event_id:
            return _serialize_event(e)
    return {"error": f"Event {event_id} not found"}


def create_event(organization_id, name, summary, start_utc, end_utc,
                 timezone="America/Los_Angeles", venue_id=None, capacity=50,
                 is_free=True, online_event=False):
    if not any(o["id"] == organization_id for o in _organizations_rows()):
        return {"error": f"Organization {organization_id} not found"}
    event = {
        "id": _new_id("evt"),
        "organization_id": organization_id,
        "name": name,
        "summary": summary,
        "status": "draft",
        "start_utc": start_utc,
        "end_utc": end_utc,
        "timezone": timezone,
        "venue_id": venue_id or "",
        "capacity": int(capacity),
        "is_free": bool(is_free),
        "online_event": bool(online_event),
        "url": "",
        "created": _now(),
    }
    _store_insert("events", event)
    return _serialize_event(event)


def publish_event(event_id):
    for e in _events_rows():
        if e["id"] == event_id:
            if not any(t["event_id"] == event_id for t in _ticket_classes_rows()):
                return {"error": "Event needs at least one ticket class before publish"}
            _changes = {"status": "live"}
            e.update(_changes)
            _store_patch("events", e, _changes)
            return _serialize_event(e)
    return {"error": f"Event {event_id} not found"}


def cancel_event(event_id):
    for e in _events_rows():
        if e["id"] == event_id:
            _changes = {"status": "canceled"}
            e.update(_changes)
            _store_patch("events", e, _changes)
            return _serialize_event(e)
    return {"error": f"Event {event_id} not found"}


# ---------------------------------------------------------------------------
# Venues
# ---------------------------------------------------------------------------

def list_venues():
    return {"venues": _venues_rows()}


def get_venue(venue_id):
    for v in _venues_rows():
        if v["id"] == venue_id:
            return v
    return {"error": f"Venue {venue_id} not found"}


# ---------------------------------------------------------------------------
# Ticket classes
# ---------------------------------------------------------------------------

def list_ticket_classes(event_id):
    if not any(e["id"] == event_id for e in _events_rows()):
        return {"error": f"Event {event_id} not found"}
    classes = [t for t in _ticket_classes_rows() if t["event_id"] == event_id]
    return {"ticket_classes": classes}


def create_ticket_class(event_id, name, quantity_total, cost=0, free=True):
    if not any(e["id"] == event_id for e in _events_rows()):
        return {"error": f"Event {event_id} not found"}
    tc = {
        "id": _new_id("tc"),
        "event_id": event_id,
        "name": name,
        "quantity_total": int(quantity_total),
        "quantity_sold": 0,
        "cost": int(cost),
        "fee": int(cost * 0.10) if cost else 0,
        "free": bool(free) or cost == 0,
        "sales_start": _now(),
        "sales_end": _now(),
    }
    _store_insert("ticket_classes", tc)
    return tc


# ---------------------------------------------------------------------------
# Attendees
# ---------------------------------------------------------------------------

def list_attendees(event_id, status=None, checked_in=None):
    if not any(e["id"] == event_id for e in _events_rows()):
        return {"error": f"Event {event_id} not found"}
    results = [a for a in _attendees_rows() if a["event_id"] == event_id]
    if status:
        results = [a for a in results if a["status"].lower() == status.lower()]
    if checked_in is not None:
        results = [a for a in results if a["checked_in"] is bool(checked_in)]
    return {"attendees": results, "pagination": {"object_count": len(results)}}


def check_in_attendee(attendee_id):
    for a in _attendees_rows():
        if a["id"] == attendee_id:
            _changes = {"checked_in": True}
            a.update(_changes)
            _store_patch("attendees", a, _changes)
            return a
    return {"error": f"Attendee {attendee_id} not found"}


def register_attendee(event_id, ticket_class_id, name, email):
    if not any(e["id"] == event_id for e in _events_rows()):
        return {"error": f"Event {event_id} not found"}
    tc = next((t for t in _ticket_classes_rows() if t["id"] == ticket_class_id), None)
    if not tc or tc["event_id"] != event_id:
        return {"error": f"Ticket class {ticket_class_id} not found for event {event_id}"}
    if tc["quantity_sold"] >= tc["quantity_total"]:
        return {"error": "Ticket class is sold out"}
    attendee = {
        "id": _new_id("att"),
        "event_id": event_id,
        "ticket_class_id": ticket_class_id,
        "name": name,
        "email": email,
        "status": "attending",
        "checked_in": False,
        "created": _now(),
    }
    _store_insert("attendees", attendee)
    for t in _ticket_classes_rows():
        if t["id"] == ticket_class_id:
            _changes = {"quantity_sold": t["quantity_sold"] + 1}
            t.update(_changes)
            _store_patch("ticket_classes", t, _changes)
    return attendee

_store.eager_load()
