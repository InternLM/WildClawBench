"""Data access module for the Google Calendar API mock service."""

import csv
import uuid
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).parent

import sys as _sys
_sys.path.insert(0, str(DATA_DIR.parent))
from _mutable_store import (
    read_seed_with_ctx, # noqa: E402
    get_store,
    strict_bool,
    strict_str,
    opt_str,
)

_store = get_store("google-calendar-api")
_API = "google-calendar-api"

_store.register("calendars", primary_key="id",
                initial_loader=lambda: _coerce_calendars(_load("calendars.json", "calendars")))
_store.register("events", primary_key="id",
                initial_loader=lambda: _coerce_events(_load("events.json", "events")))
_store.register_document("attendees", initial_loader=lambda: _coerce_attendees(_load("event_attendees.json", "event_attendees")))


def _calendars_rows():
    return _store.table("calendars").rows()


def _events_rows():
    return _store.table("events").rows()


def _attendees_doc():
    return _store.document("attendees").get()



def _load(filename, table):
    return read_seed_with_ctx(DATA_DIR / filename, _API, table)


def _strip_ctx(r):
    return {k: v for k, v in r.items() if not k.startswith("__")}


def _now():
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000Z")


def _coerce_calendars(rows):
    return [{**_strip_ctx(r), "primary": strict_bool(r, "primary")} for r in rows]


def _coerce_events(rows):
    out = []
    for r in rows:
        recurrence = opt_str(r, "recurrence", default="")
        out.append({
            **_strip_ctx(r),
            "all_day": strict_bool(r, "all_day"),
            "recurrence": [recurrence] if recurrence else [],
        })
    return out


def _coerce_attendees(rows):
    out = {}
    for r in rows:
        out.setdefault(strict_str(r, "event_id"), []).append({
            "email": strict_str(r, "email"),
            "displayName": strict_str(r, "display_name"),
            "responseStatus": strict_str(r, "response_status"),
            "optional": strict_bool(r, "optional"),
            "organizer": strict_bool(r, "organizer"),
        })
    return out








def _new_event_id():
    return f"evt-{uuid.uuid4().hex[:10]}"


def _serialize_event(e):
    out = dict(e)
    out["start"] = {"dateTime": e["start"], "timeZone": "America/Los_Angeles"} if not e["all_day"] \
        else {"date": e["start"][:10]}
    out["end"] = {"dateTime": e["end"], "timeZone": "America/Los_Angeles"} if not e["all_day"] \
        else {"date": e["end"][:10]}
    out["attendees"] = _attendees_doc().get(e["id"], [])
    return out


# ---------------------------------------------------------------------------
# Calendars
# ---------------------------------------------------------------------------

def list_calendars():
    return {"kind": "calendar#calendarList", "items": _calendars_rows()}


def get_calendar(calendar_id):
    if calendar_id == "primary":
        calendar_id = next((c["id"] for c in _calendars_rows() if c["primary"]), None)
    for c in _calendars_rows():
        if c["id"] == calendar_id:
            return c
    return {"error": f"Calendar {calendar_id} not found"}


# ---------------------------------------------------------------------------
# Events
# ---------------------------------------------------------------------------

def _resolve_calendar(calendar_id):
    if calendar_id == "primary":
        return next((c["id"] for c in _calendars_rows() if c["primary"]), None)
    return calendar_id


def list_events(calendar_id, time_min=None, time_max=None, q=None,
                single_events=True, order_by="startTime", max_results=25, page_token=None):
    resolved = _resolve_calendar(calendar_id)
    if not resolved or not any(c["id"] == resolved for c in _calendars_rows()):
        return {"error": f"Calendar {calendar_id} not found"}
    results = [e for e in _events_rows() if e["calendar_id"] == resolved]
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
    for e in _events_rows():
        if e["calendar_id"] == resolved and e["id"] == event_id:
            return _serialize_event(e)
    return {"error": f"Event {event_id} not found"}


def create_event(calendar_id, payload):
    resolved = _resolve_calendar(calendar_id)
    if not any(c["id"] == resolved for c in _calendars_rows()):
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
    _events_rows().append(event)
    if payload.get("attendees"):
        _attendees_doc()[event["id"]] = [{
            "email": a.get("email"),
            "displayName": a.get("displayName", ""),
            "responseStatus": a.get("responseStatus", "needsAction"),
            "optional": bool(a.get("optional", False)),
            "organizer": bool(a.get("organizer", False)),
        } for a in payload["attendees"]]
    return _serialize_event(event)


def update_event(calendar_id, event_id, payload):
    resolved = _resolve_calendar(calendar_id)
    for i, e in enumerate(_events_rows()):
        if e["calendar_id"] == resolved and e["id"] == event_id:
            for field in ("summary", "description", "location", "status", "visibility"):
                if field in payload:
                    _events_rows()[i][field] = payload[field]
            if "start" in payload:
                s = payload["start"]
                _events_rows()[i]["start"] = s.get("dateTime") or s.get("date") or e["start"]
                _events_rows()[i]["all_day"] = "date" in s
            if "end" in payload:
                en = payload["end"]
                _events_rows()[i]["end"] = en.get("dateTime") or en.get("date") or e["end"]
            if "attendees" in payload:
                _attendees_doc()[event_id] = [{
                    "email": a.get("email"),
                    "displayName": a.get("displayName", ""),
                    "responseStatus": a.get("responseStatus", "needsAction"),
                    "optional": bool(a.get("optional", False)),
                    "organizer": bool(a.get("organizer", False)),
                } for a in payload["attendees"]]
            return _serialize_event(_events_rows()[i])
    return {"error": f"Event {event_id} not found"}


def delete_event(calendar_id, event_id):
    resolved = _resolve_calendar(calendar_id)
    for i, e in enumerate(_events_rows()):
        if e["calendar_id"] == resolved and e["id"] == event_id:
            _events_rows().pop(i)
            _attendees_doc().pop(event_id, None)
            return {"deleted": True, "id": event_id}
    return {"error": f"Event {event_id} not found"}


# ---------------------------------------------------------------------------
# Free/busy
# ---------------------------------------------------------------------------

def freebusy(time_min, time_max, calendar_ids):
    calendars_block = {}
    for raw_id in calendar_ids:
        cid = _resolve_calendar(raw_id)
        if not cid or not any(c["id"] == cid for c in _calendars_rows()):
            calendars_block[raw_id] = {"errors": [{"reason": "notFound"}], "busy": []}
            continue
        busy = []
        for e in _events_rows():
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


_store.eager_load()
