"""Data access module for the Google Calendar API mock service."""

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
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000Z")


def _to_bool(v):
    return str(v).strip().lower() == "true"


def _coerce_calendars(rows):
    return [{**r, "primary": _to_bool(r["primary"])} for r in rows]


def _coerce_events(rows):
    return [{**r, "all_day": _to_bool(r["all_day"]),
             "recurrence": [r["recurrence"]] if r["recurrence"] else []}
            for r in rows]


def _coerce_attendees(rows):
    out = {}
    for r in rows:
        out.setdefault(r["event_id"], []).append({
            "email": r["email"],
            "displayName": r["display_name"],
            "responseStatus": r["response_status"],
            "optional": _to_bool(r["optional"]),
            "organizer": _to_bool(r["organizer"]),
        })
    return out


_calendars = _coerce_calendars(_load("calendars.csv"))
_events = _coerce_events(_load("events.csv"))
_attendees = _coerce_attendees(_load("event_attendees.csv"))

_calendars_store = deepcopy(_calendars)
_events_store = deepcopy(_events)
_attendees_store = deepcopy(_attendees)


def _new_event_id():
    return f"evt-{uuid.uuid4().hex[:10]}"


def _serialize_event(e):
    out = dict(e)
    out["start"] = {"dateTime": e["start"], "timeZone": "America/Los_Angeles"} if not e["all_day"] \
        else {"date": e["start"][:10]}
    out["end"] = {"dateTime": e["end"], "timeZone": "America/Los_Angeles"} if not e["all_day"] \
        else {"date": e["end"][:10]}
    out["attendees"] = _attendees_store.get(e["id"], [])
    return out


# ---------------------------------------------------------------------------
# Calendars
# ---------------------------------------------------------------------------

def list_calendars():
    return {"kind": "calendar#calendarList", "items": _calendars_store}


def get_calendar(calendar_id):
    if calendar_id == "primary":
        calendar_id = next((c["id"] for c in _calendars_store if c["primary"]), None)
    for c in _calendars_store:
        if c["id"] == calendar_id:
            return c
    return {"error": f"Calendar {calendar_id} not found"}


# ---------------------------------------------------------------------------
# Events
# ---------------------------------------------------------------------------

def _resolve_calendar(calendar_id):
    if calendar_id == "primary":
        return next((c["id"] for c in _calendars_store if c["primary"]), None)
    return calendar_id


def list_events(calendar_id, time_min=None, time_max=None, q=None,
                single_events=True, order_by="startTime", max_results=25, page_token=None):
    resolved = _resolve_calendar(calendar_id)
    if not resolved or not any(c["id"] == resolved for c in _calendars_store):
        return {"error": f"Calendar {calendar_id} not found"}
    results = [e for e in _events_store if e["calendar_id"] == resolved]
    if time_min:
        results = [e for e in results if e["end"] >= time_min]
    if time_max:
        results = [e for e in results if e["start"] <= time_max]
    if q:
        ql = q.lower()
        results = [e for e in results
                   if ql in e["summary"].lower() or ql in (e["description"] or "").lower()
                   or ql in (e["location"] or "").lower()]
    if order_by == "startTime":
        results.sort(key=lambda e: e["start"])
    elif order_by == "updated":
        results.sort(key=lambda e: e.get("updated", e["start"]), reverse=True)
    try:
        offset = int(page_token or 0)
    except ValueError:
        offset = 0
    page = results[offset: offset + max_results]
    next_token = str(offset + max_results) if offset + max_results < len(results) else None
    return {
        "kind": "calendar#events",
        "items": [_serialize_event(e) for e in page],
        "nextPageToken": next_token,
    }


def get_event(calendar_id, event_id):
    resolved = _resolve_calendar(calendar_id)
    for e in _events_store:
        if e["calendar_id"] == resolved and e["id"] == event_id:
            return _serialize_event(e)
    return {"error": f"Event {event_id} not found"}


def create_event(calendar_id, payload):
    resolved = _resolve_calendar(calendar_id)
    if not any(c["id"] == resolved for c in _calendars_store):
        return {"error": f"Calendar {calendar_id} not found"}
    start = payload.get("start") or {}
    end = payload.get("end") or {}
    all_day = "date" in start
    event = {
        "id": _new_event_id(),
        "calendar_id": resolved,
        "summary": payload.get("summary", ""),
        "description": payload.get("description", ""),
        "location": payload.get("location", ""),
        "start": start.get("dateTime") or start.get("date") or _now(),
        "end": end.get("dateTime") or end.get("date") or _now(),
        "all_day": all_day,
        "status": "confirmed",
        "creator": payload.get("creator", "amelia@orbit-labs.com"),
        "organizer": payload.get("organizer", "amelia@orbit-labs.com"),
        "recurrence": payload.get("recurrence", []) or [],
        "visibility": payload.get("visibility", "default"),
    }
    _events_store.append(event)
    if payload.get("attendees"):
        _attendees_store[event["id"]] = [{
            "email": a.get("email"),
            "displayName": a.get("displayName", ""),
            "responseStatus": a.get("responseStatus", "needsAction"),
            "optional": bool(a.get("optional", False)),
            "organizer": bool(a.get("organizer", False)),
        } for a in payload["attendees"]]
    return _serialize_event(event)


def update_event(calendar_id, event_id, payload):
    resolved = _resolve_calendar(calendar_id)
    for i, e in enumerate(_events_store):
        if e["calendar_id"] == resolved and e["id"] == event_id:
            for field in ("summary", "description", "location", "status", "visibility"):
                if field in payload:
                    _events_store[i][field] = payload[field]
            if "start" in payload:
                s = payload["start"]
                _events_store[i]["start"] = s.get("dateTime") or s.get("date") or e["start"]
                _events_store[i]["all_day"] = "date" in s
            if "end" in payload:
                en = payload["end"]
                _events_store[i]["end"] = en.get("dateTime") or en.get("date") or e["end"]
            if "attendees" in payload:
                _attendees_store[event_id] = [{
                    "email": a.get("email"),
                    "displayName": a.get("displayName", ""),
                    "responseStatus": a.get("responseStatus", "needsAction"),
                    "optional": bool(a.get("optional", False)),
                    "organizer": bool(a.get("organizer", False)),
                } for a in payload["attendees"]]
            return _serialize_event(_events_store[i])
    return {"error": f"Event {event_id} not found"}


def delete_event(calendar_id, event_id):
    resolved = _resolve_calendar(calendar_id)
    for i, e in enumerate(_events_store):
        if e["calendar_id"] == resolved and e["id"] == event_id:
            _events_store.pop(i)
            _attendees_store.pop(event_id, None)
            return {"deleted": True, "id": event_id}
    return {"error": f"Event {event_id} not found"}


# ---------------------------------------------------------------------------
# Free/busy
# ---------------------------------------------------------------------------

def freebusy(time_min, time_max, calendar_ids):
    calendars_block = {}
    for raw_id in calendar_ids:
        cid = _resolve_calendar(raw_id)
        if not cid or not any(c["id"] == cid for c in _calendars_store):
            calendars_block[raw_id] = {"errors": [{"reason": "notFound"}], "busy": []}
            continue
        busy = []
        for e in _events_store:
            if e["calendar_id"] != cid:
                continue
            if e["status"] != "confirmed":
                continue
            if e["end"] < time_min or e["start"] > time_max:
                continue
            busy.append({"start": e["start"], "end": e["end"]})
        calendars_block[raw_id] = {"busy": busy}
    return {"kind": "calendar#freeBusy", "timeMin": time_min, "timeMax": time_max,
            "calendars": calendars_block}
