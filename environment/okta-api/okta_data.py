"""Data access module for the Okta API mock service."""

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


# ---------------------------------------------------------------------------
# Load
# ---------------------------------------------------------------------------

def _coerce_users(rows):
    out = []
    for r in rows:
        out.append({
            **r,
            "activated": r["activated"] or None,
            "last_login": r["last_login"] or None,
        })
    return out


_users = _coerce_users(_load("users.csv"))
_groups = _load("groups.csv")
_memberships = _load("group_memberships.csv")
_apps = _load("apps.csv")
_app_assignments = _load("app_assignments.csv")

_users_store = deepcopy(_users)
_groups_store = deepcopy(_groups)
_memberships_store = deepcopy(_memberships)
_apps_store = deepcopy(_apps)
_app_assignments_store = deepcopy(_app_assignments)


# ---------------------------------------------------------------------------
# Serializers
# ---------------------------------------------------------------------------

def _serialize_user(u):
    return {
        "id": u["id"],
        "status": u["status"],
        "created": u["created"],
        "activated": u["activated"],
        "lastLogin": u["last_login"],
        "profile": {
            "firstName": u["first_name"],
            "lastName": u["last_name"],
            "email": u["email"],
            "login": u["login"],
        },
    }


def _serialize_group(g):
    return {
        "id": g["id"],
        "type": g["type"],
        "created": g["created"],
        "profile": {
            "name": g["name"],
            "description": g["description"],
        },
    }


def _serialize_app(a):
    return {
        "id": a["id"],
        "name": a["name"],
        "label": a["label"],
        "status": a["status"],
        "signOnMode": a["sign_on_mode"],
        "created": a["created"],
    }


def _find_user(user_id):
    return next((u for u in _users_store if u["id"] == user_id), None)


def _find_group(group_id):
    return next((g for g in _groups_store if g["id"] == group_id), None)


# ---------------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------------

def list_users(status=None, q=None):
    results = list(_users_store)
    if status:
        results = [u for u in results if u["status"] == status]
    if q:
        ql = q.lower()
        results = [u for u in results
                   if ql in u["first_name"].lower()
                   or ql in u["last_name"].lower()
                   or ql in u["email"].lower()]
    return [_serialize_user(u) for u in results]


def get_user(user_id):
    u = _find_user(user_id)
    if not u:
        return {"error": f"User {user_id} not found"}
    return _serialize_user(u)


def create_user(first_name, last_name, email, login=None, activate=True):
    user = {
        "id": f"00u{uuid.uuid4().hex[:9]}",
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "login": login or email,
        "status": "ACTIVE" if activate else "STAGED",
        "created": _now(),
        "activated": _now() if activate else None,
        "last_login": None,
    }
    _users_store.append(user)
    return _serialize_user(user)


def _set_user_status(user_id, status, set_activated=False):
    u = _find_user(user_id)
    if not u:
        return {"error": f"User {user_id} not found"}
    u["status"] = status
    if set_activated and not u["activated"]:
        u["activated"] = _now()
    return _serialize_user(u)


def activate_user(user_id):
    u = _find_user(user_id)
    if not u:
        return {"error": f"User {user_id} not found"}
    if u["status"] not in ("STAGED", "PROVISIONED", "DEPROVISIONED"):
        return {"error": f"User {user_id} cannot be activated from status {u['status']}"}
    return _set_user_status(user_id, "ACTIVE", set_activated=True)


def suspend_user(user_id):
    u = _find_user(user_id)
    if not u:
        return {"error": f"User {user_id} not found"}
    if u["status"] != "ACTIVE":
        return {"error": f"User {user_id} cannot be suspended from status {u['status']}"}
    return _set_user_status(user_id, "SUSPENDED")


def deactivate_user(user_id):
    u = _find_user(user_id)
    if not u:
        return {"error": f"User {user_id} not found"}
    return _set_user_status(user_id, "DEPROVISIONED")


# ---------------------------------------------------------------------------
# Groups
# ---------------------------------------------------------------------------

def list_groups(q=None):
    results = list(_groups_store)
    if q:
        ql = q.lower()
        results = [g for g in results if ql in g["name"].lower()]
    return [_serialize_group(g) for g in results]


def get_group(group_id):
    g = _find_group(group_id)
    if not g:
        return {"error": f"Group {group_id} not found"}
    return _serialize_group(g)


def list_group_users(group_id):
    g = _find_group(group_id)
    if not g:
        return {"error": f"Group {group_id} not found"}
    member_ids = [m["user_id"] for m in _memberships_store if m["group_id"] == group_id]
    return [_serialize_user(u) for u in _users_store if u["id"] in member_ids]


# ---------------------------------------------------------------------------
# Apps
# ---------------------------------------------------------------------------

def list_apps(status=None):
    results = list(_apps_store)
    if status:
        results = [a for a in results if a["status"] == status]
    return [_serialize_app(a) for a in results]
