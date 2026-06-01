"""Data access module for the ServiceNow Table API mock service.

Mirrors a subset of the ServiceNow Table API. Records are keyed by ``sys_id``
(stable string IDs). Mutations (created/updated incidents) are held in process
memory and reset on container restart. Responses are wrapped by the server in
``{"result": ...}``.
"""

import csv
import uuid
from copy import deepcopy
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).parent

# state numeric codes used by the incident table
INCIDENT_STATES = {"1": "New", "2": "In Progress", "3": "On Hold", "6": "Resolved", "7": "Closed"}


def _load(filename):
    with open(DATA_DIR / filename, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _now():
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


def _to_bool(v):
    return str(v).strip().lower() == "true"


# ---------------------------------------------------------------------------
# Load + coerce
# ---------------------------------------------------------------------------

def _coerce_incidents(rows):
    return [dict(r) for r in rows]


def _coerce_changes(rows):
    return [dict(r) for r in rows]


def _coerce_problems(rows):
    return [dict(r) for r in rows]


def _coerce_users(rows):
    out = []
    for r in rows:
        d = dict(r)
        d["active"] = _to_bool(r["active"])
        out.append(d)
    return out


_incidents = _coerce_incidents(_load("incident.csv"))
_changes = _coerce_changes(_load("change_request.csv"))
_problems = _coerce_problems(_load("problem.csv"))
_users = _coerce_users(_load("sys_user.csv"))

_incidents_store = deepcopy(_incidents)
_changes_store = deepcopy(_changes)
_problems_store = deepcopy(_problems)
_users_store = deepcopy(_users)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _new_sys_id():
    return uuid.uuid4().hex


def _find(store, sys_id):
    return next((r for r in store if r["sys_id"] == sys_id), None)


def _parse_query(sysparm_query):
    """Parse a ServiceNow encoded query like ``state=2^priority=1``.

    Supports the ``^`` (AND) separator and ``field=value`` equality. Unknown
    operators are ignored gracefully. Returns a list of (field, value) tuples.
    """
    conditions = []
    if not sysparm_query:
        return conditions
    for clause in sysparm_query.split("^"):
        clause = clause.strip()
        if not clause or "=" not in clause:
            continue
        field, _, value = clause.partition("=")
        conditions.append((field.strip(), value.strip()))
    return conditions


def _apply_query(rows, sysparm_query, sysparm_limit=None):
    conditions = _parse_query(sysparm_query)
    results = list(rows)
    for field, value in conditions:
        results = [r for r in results if str(r.get(field, "")) == value]
    if sysparm_limit is not None:
        try:
            limit = int(sysparm_limit)
            results = results[:limit]
        except (TypeError, ValueError):
            pass
    return results


# ---------------------------------------------------------------------------
# Incidents
# ---------------------------------------------------------------------------

def list_incidents(sysparm_query=None, sysparm_limit=None):
    return _apply_query(_incidents_store, sysparm_query, sysparm_limit)


def get_incident(sys_id):
    rec = _find(_incidents_store, sys_id)
    if not rec:
        return {"error": f"Incident {sys_id} not found"}
    return rec


def create_incident(short_description, description=None, priority="3", impact="3",
                    urgency="3", category="inquiry", assigned_to=None, opened_by=None):
    if not short_description:
        return {"error": "short_description is required"}
    now = _now()
    seq = 1001 + len(_incidents_store)
    rec = {
        "sys_id": _new_sys_id(),
        "number": f"INC{seq:07d}",
        "short_description": short_description,
        "description": description or "",
        "state": "1",
        "priority": str(priority),
        "impact": str(impact),
        "urgency": str(urgency),
        "category": category or "inquiry",
        "assigned_to": assigned_to or "",
        "opened_by": opened_by or "",
        "opened_at": now,
        "updated_at": now,
    }
    _incidents_store.append(rec)
    return rec


def update_incident(sys_id, **fields):
    rec = _find(_incidents_store, sys_id)
    if not rec:
        return {"error": f"Incident {sys_id} not found"}
    for key in ("short_description", "description", "state", "priority", "impact",
                "urgency", "category", "assigned_to"):
        val = fields.get(key)
        if val is not None:
            rec[key] = str(val)
    rec["updated_at"] = _now()
    return rec


# ---------------------------------------------------------------------------
# Change requests
# ---------------------------------------------------------------------------

def list_change_requests(sysparm_query=None, sysparm_limit=None):
    return _apply_query(_changes_store, sysparm_query, sysparm_limit)


def get_change_request(sys_id):
    rec = _find(_changes_store, sys_id)
    if not rec:
        return {"error": f"Change request {sys_id} not found"}
    return rec


# ---------------------------------------------------------------------------
# Problems
# ---------------------------------------------------------------------------

def list_problems(sysparm_query=None, sysparm_limit=None):
    return _apply_query(_problems_store, sysparm_query, sysparm_limit)


def get_problem(sys_id):
    rec = _find(_problems_store, sys_id)
    if not rec:
        return {"error": f"Problem {sys_id} not found"}
    return rec


# ---------------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------------

def list_users(sysparm_query=None, sysparm_limit=None):
    return _apply_query(_users_store, sysparm_query, sysparm_limit)


def get_user(sys_id):
    rec = _find(_users_store, sys_id)
    if not rec:
        return {"error": f"User {sys_id} not found"}
    return rec
