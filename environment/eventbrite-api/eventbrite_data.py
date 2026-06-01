"""Data access module for the Eventbrite API mock service."""

import csv
import uuid
from copy import deepcopy
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).parent


def _load(filename):
    with open(DATA_DIR / filename, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _now():
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


def _to_bool(v):
    return str(v).strip().lower() == "true"


def _coerce_events(rows):
    return [{**r,
             "capacity": int(r["capacity"]),
             "is_free": _to_bool(r["is_free"]),
             "online_event": _to_bool(r["online_event"])} for r in rows]


def _coerce_venues(rows):
    return [{**r,
             "latitude": float(r["latitude"]),
             "longitude": float(r["longitude"])} for r in rows]


def _coerce_ticket_classes(rows):
    return [{**r,
             "quantity_total": int(r["quantity_total"]),
             "quantity_sold": int(r["quantity_sold"]),
             "cost": int(r["cost"]),
             "fee": int(r["fee"]),
             "free": _to_bool(r["free"])} for r in rows]


def _coerce_attendees(rows):
    return [{**r, "checked_in": _to_bool(r["checked_in"])} for r in rows]


_organizations = _load("organizations.csv")
_events = _coerce_events(_load("events.csv"))
_venues = _coerce_venues(_load("venues.csv"))
_ticket_classes = _coerce_ticket_classes(_load("ticket_classes.csv"))
_attendees = _coerce_attendees(_load("attendees.csv"))

_organizations_store = deepcopy(_organizations)
_events_store = deepcopy(_events)
_venues_store = deepcopy(_venues)
_ticket_classes_store = deepcopy(_ticket_classes)
_attendees_store = deepcopy(_attendees)


def _new_id(prefix):
    return f"{prefix}-{uuid.uuid4().hex[:8]}"


def _serialize_event(e):
    venue = next((v for v in _venues_store if v["id"] == e["venue_id"]), None)
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
    return {"organizations": _organizations_store, "pagination": {"object_count": len(_organizations_store)}}


def get_organization(org_id):
    for o in _organizations_store:
        if o["id"] == org_id:
            return o
    return {"error": f"Organization {org_id} not found"}


# ---------------------------------------------------------------------------
# Events
# ---------------------------------------------------------------------------

def list_events(organization_id=None, status=None, q=None, page_size=50):
    results = list(_events_store)
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
    for e in _events_store:
        if e["id"] == event_id:
            return _serialize_event(e)
    return {"error": f"Event {event_id} not found"}


def create_event(organization_id, name, summary, start_utc, end_utc,
                 timezone="America/Los_Angeles", venue_id=None, capacity=50,
                 is_free=True, online_event=False):
    if not any(o["id"] == organization_id for o in _organizations_store):
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
    _events_store.append(event)
    return _serialize_event(event)


def publish_event(event_id):
    for i, e in enumerate(_events_store):
        if e["id"] == event_id:
            if not any(t["event_id"] == event_id for t in _ticket_classes_store):
                return {"error": "Event needs at least one ticket class before publish"}
            _events_store[i]["status"] = "live"
            return _serialize_event(_events_store[i])
    return {"error": f"Event {event_id} not found"}


def cancel_event(event_id):
    for i, e in enumerate(_events_store):
        if e["id"] == event_id:
            _events_store[i]["status"] = "canceled"
            return _serialize_event(_events_store[i])
    return {"error": f"Event {event_id} not found"}


# ---------------------------------------------------------------------------
# Venues
# ---------------------------------------------------------------------------

def list_venues():
    return {"venues": _venues_store}


def get_venue(venue_id):
    for v in _venues_store:
        if v["id"] == venue_id:
            return v
    return {"error": f"Venue {venue_id} not found"}


# ---------------------------------------------------------------------------
# Ticket classes
# ---------------------------------------------------------------------------

def list_ticket_classes(event_id):
    if not any(e["id"] == event_id for e in _events_store):
        return {"error": f"Event {event_id} not found"}
    classes = [t for t in _ticket_classes_store if t["event_id"] == event_id]
    return {"ticket_classes": classes}


def create_ticket_class(event_id, name, quantity_total, cost=0, free=True):
    if not any(e["id"] == event_id for e in _events_store):
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
    _ticket_classes_store.append(tc)
    return tc


# ---------------------------------------------------------------------------
# Attendees
# ---------------------------------------------------------------------------

def list_attendees(event_id, status=None, checked_in=None):
    if not any(e["id"] == event_id for e in _events_store):
        return {"error": f"Event {event_id} not found"}
    results = [a for a in _attendees_store if a["event_id"] == event_id]
    if status:
        results = [a for a in results if a["status"].lower() == status.lower()]
    if checked_in is not None:
        results = [a for a in results if a["checked_in"] is bool(checked_in)]
    return {"attendees": results, "pagination": {"object_count": len(results)}}


def check_in_attendee(attendee_id):
    for i, a in enumerate(_attendees_store):
        if a["id"] == attendee_id:
            _attendees_store[i]["checked_in"] = True
            return _attendees_store[i]
    return {"error": f"Attendee {attendee_id} not found"}


def register_attendee(event_id, ticket_class_id, name, email):
    if not any(e["id"] == event_id for e in _events_store):
        return {"error": f"Event {event_id} not found"}
    tc = next((t for t in _ticket_classes_store if t["id"] == ticket_class_id), None)
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
    _attendees_store.append(attendee)
    for i, t in enumerate(_ticket_classes_store):
        if t["id"] == ticket_class_id:
            _ticket_classes_store[i]["quantity_sold"] += 1
    return attendee
