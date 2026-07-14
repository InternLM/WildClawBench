"""Data access module for the Zoom API mock service."""

import csv
import json
import random
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).parent

import sys as _sys
_sys.path.insert(0, str(DATA_DIR.parent))
from _mutable_store import (
    read_seed_with_ctx, get_store, opt_str, strict_int)

_store = get_store("zoom-api")
_API = "zoom-api"



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

_store.register("meetings", primary_key="id",
                initial_loader=lambda: _coerce_meetings(_load("meetings.json", "meetings")))
_store.register("recordings", primary_key="id",
                initial_loader=lambda: _coerce_recordings(_load("recordings.json", "recordings")))
_store.register("registrants", primary_key="id",
                initial_loader=lambda: _coerce_registrants(_load("registrants.json", "registrants")))
_store.register_document("user", initial_loader=lambda: __import__('json').load(open(DATA_DIR / "user.json", encoding="utf-8")))


def _meetings_rows():
    return _store.table("meetings").rows()


def _recordings_rows():
    return _store.table("recordings").rows()


def _registrants_rows():
    return _store.table("registrants").rows()


def _user_doc():
    return _store.document("user").get()



def _load(filename, table):
    return read_seed_with_ctx(DATA_DIR / filename, _API, table)


def _strip_ctx(r):
    return {k: v for k, v in r.items() if not k.startswith("__")}


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
            **_strip_ctx(r),
            "id": strict_int(r, "id"),
            "type": strict_int(r, "type"),
            "duration": strict_int(r, "duration"),
            "agenda": r["agenda"] or "",
        })
    return out


def _coerce_recordings(rows):
    out = []
    for r in rows:
        out.append({
            **_strip_ctx(r),
            "meeting_id": strict_int(r, "meeting_id"),
            "file_size": strict_int(r, "file_size"),
        })
    return out


def _coerce_registrants(rows):
    out = []
    for r in rows:
        out.append({
            **_strip_ctx(r),
            "meeting_id": strict_int(r, "meeting_id"),
            "join_time": opt_str(r, "join_time", default="") or None,
        })
    return out






# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _new_meeting_id():
    existing = {m["id"] for m in _meetings_rows()}
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
    return _user_doc()


# ---------------------------------------------------------------------------
# Meetings
# ---------------------------------------------------------------------------

def list_meetings(user_id, meeting_type="scheduled", page_size=30):
    if user_id != "me" and user_id != _user_doc()["id"]:
        return {"error": f"User {user_id} not found"}
    host = _user_doc()["id"]
    meetings = [m for m in _meetings_rows() if m["host_id"] == host]
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
    for m in _meetings_rows():
        if m["id"] == meeting_id:
            return _serialize_meeting(m)
    return {"error": f"Meeting {meeting_id} not found", "code": 3001}


def create_meeting(user_id, topic, start_time=None, duration=60, timezone="UTC",
                   agenda="", meeting_type=2):
    if user_id != "me" and user_id != _user_doc()["id"]:
        return {"error": f"User {user_id} not found"}
    mid = _new_meeting_id()
    meeting = {
        "id": mid,
        "host_id": _user_doc()["id"],
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
    _store_insert("meetings", meeting)
    return _serialize_meeting(meeting)


def update_meeting(meeting_id, topic=None, start_time=None, duration=None,
                   agenda=None, timezone=None):
    for m in _meetings_rows():
        if m["id"] == meeting_id:
            _changes = {}
            if topic is not None:
                _changes["topic"] = topic
            if start_time is not None:
                _changes["start_time"] = start_time
            if duration is not None:
                _changes["duration"] = duration
            if agenda is not None:
                _changes["agenda"] = agenda
            if timezone is not None:
                _changes["timezone"] = timezone
            m.update(_changes)
            _store_patch("meetings", m, _changes)
            return _serialize_meeting(m)
    return {"error": f"Meeting {meeting_id} not found", "code": 3001}


def delete_meeting(meeting_id):
    for m in _meetings_rows():
        if m["id"] == meeting_id:
            _store_delete("meetings", m)
            return {"deleted": True, "id": meeting_id}
    return {"error": f"Meeting {meeting_id} not found", "code": 3001}


# ---------------------------------------------------------------------------
# Recordings
# ---------------------------------------------------------------------------

def get_recordings(meeting_id):
    meeting = next((m for m in _meetings_rows() if m["id"] == meeting_id), None)
    if not meeting:
        return {"error": f"Meeting {meeting_id} not found", "code": 3001}
    files = [r for r in _recordings_rows() if r["meeting_id"] == meeting_id]
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
    if not any(m["id"] == meeting_id for m in _meetings_rows()):
        return {"error": f"Meeting {meeting_id} not found", "code": 3001}
    regs = [r for r in _registrants_rows() if r["meeting_id"] == meeting_id]
    if status:
        regs = [r for r in regs if r["status"] == status]
    return {
        "page_count": 1,
        "page_size": len(regs),
        "total_records": len(regs),
        "registrants": regs,
    }

_store.eager_load()
