"""Data access module for the PagerDuty API mock service."""

import csv
import uuid
from copy import deepcopy
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).parent

VALID_STATUSES = {"triggered", "acknowledged", "resolved"}


def _load(filename):
    with open(DATA_DIR / filename, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _now_iso():
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


# ---------------------------------------------------------------------------
# Load + coerce
# ---------------------------------------------------------------------------

def _coerce_users(rows):
    return [dict(r) for r in rows]


def _coerce_services(rows):
    out = []
    for r in rows:
        out.append({
            **r,
            "auto_resolve_timeout": int(r["auto_resolve_timeout"]),
        })
    return out


def _coerce_incidents(rows):
    out = []
    for r in rows:
        out.append({
            **r,
            "incident_number": int(r["incident_number"]),
            "assigned_to": r["assigned_to"] or None,
            "resolved_at": r["resolved_at"] or None,
        })
    return out


def _coerce_policies(rows):
    out = []
    for r in rows:
        out.append({
            **r,
            "num_loops": int(r["num_loops"]),
        })
    return out


def _coerce_schedules(rows):
    return [dict(r) for r in rows]


_users = _coerce_users(_load("users.csv"))
_services = _coerce_services(_load("services.csv"))
_incidents = _coerce_incidents(_load("incidents.csv"))
_policies = _coerce_policies(_load("escalation_policies.csv"))
_schedules = _coerce_schedules(_load("schedules.csv"))

_users_store = deepcopy(_users)
_services_store = deepcopy(_services)
_incidents_store = deepcopy(_incidents)
_policies_store = deepcopy(_policies)
_schedules_store = deepcopy(_schedules)
_notes_store = {}  # incident_id -> [note]


def _new_id(prefix):
    return f"{prefix}-{uuid.uuid4().hex[:10]}"


# ---------------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------------

def list_users():
    return {"users": deepcopy(_users_store)}


def _get_user(user_id):
    return next((u for u in _users_store if u["user_id"] == user_id), None)


# ---------------------------------------------------------------------------
# Services
# ---------------------------------------------------------------------------

def list_services():
    return {"services": deepcopy(_services_store)}


def get_service(service_id):
    for s in _services_store:
        if s["service_id"] == service_id:
            return s
    return {"error": f"Service {service_id} not found"}


# ---------------------------------------------------------------------------
# Incidents
# ---------------------------------------------------------------------------

def list_incidents(statuses=None, service_id=None, urgency=None):
    results = list(_incidents_store)
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
    for i in _incidents_store:
        if i["incident_id"] == incident_id:
            return i
    return {"error": f"Incident {incident_id} not found"}


def create_incident(title, service_id, urgency="high", assigned_to=None):
    service = next((s for s in _services_store if s["service_id"] == service_id), None)
    if not service:
        return {"error": f"Service {service_id} not found"}
    if assigned_to and not _get_user(assigned_to):
        return {"error": f"User {assigned_to} not found"}
    incident_number = max((i["incident_number"] for i in _incidents_store), default=1000) + 1
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
    _incidents_store.append(incident)
    return incident


def update_incident(incident_id, status=None, assigned_to=None):
    for i, inc in enumerate(_incidents_store):
        if inc["incident_id"] == incident_id:
            if status is not None:
                if status.lower() not in VALID_STATUSES:
                    return {"error": f"Invalid status '{status}'"}
                _incidents_store[i]["status"] = status.lower()
                if status.lower() == "resolved":
                    _incidents_store[i]["resolved_at"] = _now_iso()
                else:
                    _incidents_store[i]["resolved_at"] = None
            if assigned_to is not None:
                if not _get_user(assigned_to):
                    return {"error": f"User {assigned_to} not found"}
                _incidents_store[i]["assigned_to"] = assigned_to
            return _incidents_store[i]
    return {"error": f"Incident {incident_id} not found"}


# ---------------------------------------------------------------------------
# Notes
# ---------------------------------------------------------------------------

def list_notes(incident_id):
    if not any(i["incident_id"] == incident_id for i in _incidents_store):
        return {"error": f"Incident {incident_id} not found"}
    return {"notes": _notes_store.get(incident_id, [])}


def create_note(incident_id, content, user_id=None):
    if not any(i["incident_id"] == incident_id for i in _incidents_store):
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
    for sch in _schedules_store:
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
    return {"schedules": deepcopy(_schedules_store)}


def list_escalation_policies():
    return {"escalation_policies": deepcopy(_policies_store)}
