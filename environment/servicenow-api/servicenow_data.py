"""Data access module for the ServiceNow Table API mock service.

Mirrors a subset of the ServiceNow Table API. Records are keyed by ``sys_id``
(stable string IDs). Mutations (created/updated incidents) are held in process
memory and reset on container restart. Responses are wrapped by the server in
``{"result": ...}``.
"""

import csv
import uuid
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).parent

import sys as _sys
_sys.path.insert(0, str(DATA_DIR.parent))
from _mutable_store import (  # noqa: E402
    read_seed_with_ctx, get_store,
    strict_bool,
)

_store = get_store("servicenow-api")
_API = "servicenow-api"


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

_store.register("incidents", primary_key="sys_id",
                initial_loader=lambda: _coerce_incidents(_load("incident.json", "incidents")))
_store.register("changes", primary_key="sys_id",
                initial_loader=lambda: _coerce_changes(_load("change_request.json", "changes")))
_store.register("problems", primary_key="sys_id",
                initial_loader=lambda: _coerce_problems(_load("problem.json", "problems")))
_store.register("users", primary_key="sys_id",
                initial_loader=lambda: _coerce_users(_load("sys_user.json", "users")))


def _incidents_rows():
    return _store.table("incidents").rows()


def _changes_rows():
    return _store.table("changes").rows()


def _problems_rows():
    return _store.table("problems").rows()


def _users_rows():
    return _store.table("users").rows()


# state numeric codes used by the incident table
INCIDENT_STATES = {"1": "New", "2": "In Progress", "3": "On Hold", "6": "Resolved", "7": "Closed"}


def _load(filename, table):
    return read_seed_with_ctx(DATA_DIR / filename, _API, table)


def _strip_ctx(r):
    return {k: v for k, v in r.items() if not k.startswith("__")}


def _now():
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


def _to_bool(v):
    return str(v).strip().lower() == "true"


# ---------------------------------------------------------------------------
# Load + coerce
# ---------------------------------------------------------------------------

def _coerce_incidents(rows):
    return [_strip_ctx(r) for r in rows]


def _coerce_changes(rows):
    return [_strip_ctx(r) for r in rows]


def _coerce_problems(rows):
    return [_strip_ctx(r) for r in rows]


def _coerce_users(rows):
    out = []
    for r in rows:
        d = _strip_ctx(r)
        d["active"] = strict_bool(r, "active")
        out.append(d)
    return out










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
    return _apply_query(_incidents_rows(), sysparm_query, sysparm_limit)


def get_incident(sys_id):
    rec = _find(_incidents_rows(), sys_id)
    if not rec:
        return {"error": f"Incident {sys_id} not found"}
    return rec


def create_incident(short_description, description=None, priority="3", impact="3",
                    urgency="3", category="inquiry", assigned_to=None, opened_by=None):
    if not short_description:
        return {"error": "short_description is required"}
    now = _now()
    seq = 1001 + len(_incidents_rows())
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
    _store_insert("incidents", rec)
    return rec


def update_incident(sys_id, **fields):
    rec = _find(_incidents_rows(), sys_id)
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
    return _apply_query(_changes_rows(), sysparm_query, sysparm_limit)


def get_change_request(sys_id):
    rec = _find(_changes_rows(), sys_id)
    if not rec:
        return {"error": f"Change request {sys_id} not found"}
    return rec


# ---------------------------------------------------------------------------
# Problems
# ---------------------------------------------------------------------------

def list_problems(sysparm_query=None, sysparm_limit=None):
    return _apply_query(_problems_rows(), sysparm_query, sysparm_limit)


def get_problem(sys_id):
    rec = _find(_problems_rows(), sys_id)
    if not rec:
        return {"error": f"Problem {sys_id} not found"}
    return rec


# ---------------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------------

def list_users(sysparm_query=None, sysparm_limit=None):
    return _apply_query(_users_rows(), sysparm_query, sysparm_limit)


def get_user(sys_id):
    rec = _find(_users_rows(), sys_id)
    if not rec:
        return {"error": f"User {sys_id} not found"}
    return rec

_store.eager_load()
