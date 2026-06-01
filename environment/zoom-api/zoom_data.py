"""Data access module for the Zoom API mock service."""

import csv
import json
import random
from copy import deepcopy
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).parent


def _load(filename):
    with open(DATA_DIR / filename, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _now():
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


def _to_int(v):
    try:
        return int(v)
    except (TypeError, ValueError):
        return 0


# ---------------------------------------------------------------------------
# Load + coerce
# ---------------------------------------------------------------------------

def _coerce_meetings(rows):
    out = []
    for r in rows:
        out.append({
            **r,
            "id": int(r["id"]),
            "type": int(r["type"]),
            "duration": int(r["duration"]),
            "agenda": r["agenda"] or "",
        })
    return out


def _coerce_recordings(rows):
    out = []
    for r in rows:
        out.append({
            **r,
            "meeting_id": int(r["meeting_id"]),
            "file_size": int(r["file_size"]),
        })
    return out


def _coerce_registrants(rows):
    out = []
    for r in rows:
        out.append({
            **r,
            "meeting_id": int(r["meeting_id"]),
            "join_time": r["join_time"] or None,
        })
    return out


_meetings = _coerce_meetings(_load("meetings.csv"))
_recordings = _coerce_recordings(_load("recordings.csv"))
_registrants = _coerce_registrants(_load("registrants.csv"))

with open(DATA_DIR / "user.json", encoding="utf-8") as _f:
    _user = json.load(_f)

_meetings_store = deepcopy(_meetings)
_recordings_store = deepcopy(_recordings)
_registrants_store = deepcopy(_registrants)
_user_store = deepcopy(_user)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _new_meeting_id():
    existing = {m["id"] for m in _meetings_store}
    while True:
        mid = random.randint(80000000000, 89999999999)
        if mid not in existing:
            return mid


def _serialize_meeting(m):
    return {
        "id": m["id"],
        "host_id": m["host_id"],
        "topic": m["topic"],
        "type": m["type"],
        "status": m["status"],
        "start_time": m["start_time"],
        "duration": m["duration"],
        "timezone": m["timezone"],
        "agenda": m["agenda"],
        "join_url": m["join_url"],
        "created_at": m["created_at"],
    }


# ---------------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------------

def get_me():
    return _user_store


# ---------------------------------------------------------------------------
# Meetings
# ---------------------------------------------------------------------------

def list_meetings(user_id, meeting_type="scheduled", page_size=30):
    if user_id != "me" and user_id != _user_store["id"]:
        return {"error": f"User {user_id} not found"}
    host = _user_store["id"]
    meetings = [m for m in _meetings_store if m["host_id"] == host]
    if meeting_type == "scheduled":
        meetings = [m for m in meetings if m["status"] == "waiting"]
    elif meeting_type == "previous_meetings":
        meetings = [m for m in meetings if m["status"] == "finished"]
    meetings = sorted(meetings, key=lambda m: m["start_time"])
    meetings = meetings[:page_size]
    return {
        "page_count": 1,
        "page_size": page_size,
        "total_records": len(meetings),
        "meetings": [_serialize_meeting(m) for m in meetings],
    }


def get_meeting(meeting_id):
    for m in _meetings_store:
        if m["id"] == meeting_id:
            return _serialize_meeting(m)
    return {"error": f"Meeting {meeting_id} not found", "code": 3001}


def create_meeting(user_id, topic, start_time=None, duration=60, timezone="UTC",
                   agenda="", meeting_type=2):
    if user_id != "me" and user_id != _user_store["id"]:
        return {"error": f"User {user_id} not found"}
    mid = _new_meeting_id()
    meeting = {
        "id": mid,
        "host_id": _user_store["id"],
        "topic": topic,
        "type": meeting_type,
        "status": "waiting",
        "start_time": start_time or _now(),
        "duration": duration,
        "timezone": timezone,
        "agenda": agenda or "",
        "join_url": f"https://zoom.us/j/{mid}",
        "created_at": _now(),
    }
    _meetings_store.append(meeting)
    return _serialize_meeting(meeting)


def update_meeting(meeting_id, topic=None, start_time=None, duration=None,
                   agenda=None, timezone=None):
    for i, m in enumerate(_meetings_store):
        if m["id"] == meeting_id:
            if topic is not None:
                _meetings_store[i]["topic"] = topic
            if start_time is not None:
                _meetings_store[i]["start_time"] = start_time
            if duration is not None:
                _meetings_store[i]["duration"] = duration
            if agenda is not None:
                _meetings_store[i]["agenda"] = agenda
            if timezone is not None:
                _meetings_store[i]["timezone"] = timezone
            return _serialize_meeting(_meetings_store[i])
    return {"error": f"Meeting {meeting_id} not found", "code": 3001}


def delete_meeting(meeting_id):
    for i, m in enumerate(_meetings_store):
        if m["id"] == meeting_id:
            _meetings_store.pop(i)
            return {"deleted": True, "id": meeting_id}
    return {"error": f"Meeting {meeting_id} not found", "code": 3001}


# ---------------------------------------------------------------------------
# Recordings
# ---------------------------------------------------------------------------

def get_recordings(meeting_id):
    meeting = next((m for m in _meetings_store if m["id"] == meeting_id), None)
    if not meeting:
        return {"error": f"Meeting {meeting_id} not found", "code": 3001}
    files = [r for r in _recordings_store if r["meeting_id"] == meeting_id]
    if not files:
        return {"error": f"No recordings for meeting {meeting_id}", "code": 3301}
    total = sum(f["file_size"] for f in files)
    return {
        "id": meeting_id,
        "uuid": f"uuid-{meeting_id}",
        "host_id": meeting["host_id"],
        "topic": meeting["topic"],
        "start_time": meeting["start_time"],
        "duration": meeting["duration"],
        "total_size": total,
        "recording_count": len(files),
        "recording_files": files,
    }


# ---------------------------------------------------------------------------
# Registrants
# ---------------------------------------------------------------------------

def list_registrants(meeting_id, status="approved"):
    if not any(m["id"] == meeting_id for m in _meetings_store):
        return {"error": f"Meeting {meeting_id} not found", "code": 3001}
    regs = [r for r in _registrants_store if r["meeting_id"] == meeting_id]
    if status:
        regs = [r for r in regs if r["status"] == status]
    return {
        "page_count": 1,
        "page_size": len(regs),
        "total_records": len(regs),
        "registrants": regs,
    }
