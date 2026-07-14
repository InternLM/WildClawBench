"""Data access module for the PagerDuty API mock service."""

import csv
from copy import deepcopy
import uuid
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).parent

import sys as _sys
_sys.path.insert(0, str(DATA_DIR.parent))
from _mutable_store import (
    read_seed_with_ctx, get_store, opt_str, strict_int)

_store = get_store("pagerduty-api")
_API = "pagerduty-api"



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

_store.register("users", primary_key="user_id",
                initial_loader=lambda: _coerce_users(_load("users.json", "users")))
_store.register("services", primary_key="service_id",
                initial_loader=lambda: _coerce_services(_load("services.json", "services")))
_store.register("incidents", primary_key="incident_id",
                initial_loader=lambda: _coerce_incidents(_load("incidents.json", "incidents")))
_store.register("policies", primary_key="escalation_policy_id",
                initial_loader=lambda: _coerce_policies(_load("escalation_policies.json", "policies")))
_store.register("schedules", primary_key="schedule_id",
                initial_loader=lambda: _coerce_schedules(_load("schedules.json", "schedules")))


def _users_rows():
    return _store.table("users").rows()


def _services_rows():
    return _store.table("services").rows()


def _incidents_rows():
    return _store.table("incidents").rows()


def _policies_rows():
    return _store.table("policies").rows()


def _schedules_rows():
    return _store.table("schedules").rows()


VALID_STATUSES = {"triggered", "acknowledged", "resolved"}


def _load(filename, table):
    return read_seed_with_ctx(DATA_DIR / filename, _API, table)


def _strip_ctx(r):
    return {k: v for k, v in r.items() if not k.startswith("__")}


def _now_iso():
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


# ---------------------------------------------------------------------------
# Load + coerce
# ---------------------------------------------------------------------------

def _coerce_users(rows):
    return [_strip_ctx(r) for r in rows]


def _coerce_services(rows):
    out = []
    for r in rows:
        out.append({
            **_strip_ctx(r),
            "auto_resolve_timeout": strict_int(r, "auto_resolve_timeout"),
        })
    return out


def _coerce_incidents(rows):
    out = []
    for r in rows:
        out.append({
            **_strip_ctx(r),
            "incident_number": strict_int(r, "incident_number"),
            "assigned_to": opt_str(r, "assigned_to", default="") or None,
            "resolved_at": opt_str(r, "resolved_at", default="") or None,
        })
    return out


def _coerce_policies(rows):
    out = []
    for r in rows:
        out.append({
            **_strip_ctx(r),
            "num_loops": strict_int(r, "num_loops"),
        })
    return out


def _coerce_schedules(rows):
    return [_strip_ctx(r) for r in rows]












_notes_store = {}  # incident_id -> [note]


def _new_id(prefix):
    return f"{prefix}-{uuid.uuid4().hex[:10]}"


# ---------------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------------

def list_users():
    return {"users": deepcopy(_users_rows())}


def _get_user(user_id):
    return next((u for u in _users_rows() if u["user_id"] == user_id), None)


# ---------------------------------------------------------------------------
# Services
# ---------------------------------------------------------------------------

def list_services():
    return {"services": deepcopy(_services_rows())}


def get_service(service_id):
    for s in _services_rows():
        if s["service_id"] == service_id:
            return s
    return {"error": f"Service {service_id} not found"}


# ---------------------------------------------------------------------------
# Incidents
# ---------------------------------------------------------------------------

def list_incidents(statuses=None, service_id=None, urgency=None):
    results = list(_incidents_rows())
    if statuses:
        wanted = {s.lower() for s in statuses}
        results = [i for i in results if i["status"].lower() in wanted]
    if service_id:
        results = [i for i in results if i["service_id"] == service_id]
    if urgency:
        results = [i for i in results if i["urgency"].lower() == urgency.lower()]
    results.sort(key=lambda i: i["created_at"], reverse=True)
    return {"incidents": results, "total": len(results)}


def get_incident(incident_id):
    for i in _incidents_rows():
        if i["incident_id"] == incident_id:
            return i
    return {"error": f"Incident {incident_id} not found"}


def create_incident(title, service_id, urgency="high", assigned_to=None):
    service = next((s for s in _services_rows() if s["service_id"] == service_id), None)
    if not service:
        return {"error": f"Service {service_id} not found"}
    if assigned_to and not _get_user(assigned_to):
        return {"error": f"User {assigned_to} not found"}
    incident_number = max((i["incident_number"] for i in _incidents_rows()), default=1000) + 1
    incident = {
        "incident_id": _new_id("PI"),
        "incident_number": incident_number,
        "title": title,
        "status": "triggered",
        "urgency": urgency,
        "service_id": service_id,
        "escalation_policy_id": service["escalation_policy_id"],
        "assigned_to": assigned_to,
        "created_at": _now_iso(),
        "resolved_at": None,
    }
    _store_insert("incidents", incident)
    return incident


def update_incident(incident_id, status=None, assigned_to=None):
    for inc in _incidents_rows():
        if inc["incident_id"] == incident_id:
            _changes = {}
            if status is not None:
                if status.lower() not in VALID_STATUSES:
                    return {"error": f"Invalid status '{status}'"}
                _changes["status"] = status.lower()
                if status.lower() == "resolved":
                    _changes["resolved_at"] = _now_iso()
                else:
                    _changes["resolved_at"] = None
            if assigned_to is not None:
                if not _get_user(assigned_to):
                    return {"error": f"User {assigned_to} not found"}
                _changes["assigned_to"] = assigned_to
            inc.update(_changes)
            _store_patch("incidents", inc, _changes)
            return inc
    return {"error": f"Incident {incident_id} not found"}


# ---------------------------------------------------------------------------
# Notes
# ---------------------------------------------------------------------------

def list_notes(incident_id):
    if not any(i["incident_id"] == incident_id for i in _incidents_rows()):
        return {"error": f"Incident {incident_id} not found"}
    return {"notes": _notes_store.get(incident_id, [])}


def create_note(incident_id, content, user_id=None):
    if not any(i["incident_id"] == incident_id for i in _incidents_rows()):
        return {"error": f"Incident {incident_id} not found"}
    note = {
        "note_id": _new_id("NOTE"),
        "incident_id": incident_id,
        "content": content,
        "user_id": user_id,
        "created_at": _now_iso(),
    }
    _notes_store.setdefault(incident_id, []).append(note)
    return note


# ---------------------------------------------------------------------------
# On-call / schedules / escalation policies
# ---------------------------------------------------------------------------

def list_oncalls(escalation_policy_id=None):
    results = []
    for sch in _schedules_rows():
        if escalation_policy_id and sch["escalation_policy_id"] != escalation_policy_id:
            continue
        user = _get_user(sch["current_oncall_user_id"])
        results.append({
            "schedule_id": sch["schedule_id"],
            "schedule_name": sch["name"],
            "escalation_policy_id": sch["escalation_policy_id"],
            "user": {"user_id": user["user_id"], "name": user["name"]} if user else None,
            "start": sch["oncall_start"],
            "end": sch["oncall_end"],
        })
    return {"oncalls": results}


def list_schedules():
    return {"schedules": deepcopy(_schedules_rows())}


def list_escalation_policies():
    return {"escalation_policies": deepcopy(_policies_rows())}

_store.eager_load()
