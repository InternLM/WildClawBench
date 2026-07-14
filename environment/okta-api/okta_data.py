"""Data access module for the Okta API mock service."""

import csv
import uuid
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).parent

import sys as _sys
_sys.path.insert(0, str(DATA_DIR.parent))
from _mutable_store import read_seed_with_ctx, get_store, opt_str  # noqa: E402

_store = get_store("okta-api")
_API = "okta-api"


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

_store.register("users", primary_key="id",
                initial_loader=lambda: _coerce_users(_load("users.json", "users")))
_store.register("groups", primary_key="id",
                initial_loader=lambda: [_strip_ctx(r) for r in _load("groups.json", "groups")])
_store.register("memberships", primary_key="_pk",
                initial_loader=lambda: [{**_strip_ctx(r), "_pk": f"{r['group_id']}@{r['user_id']}"} for r in _load("group_memberships.json", "memberships")])
_store.register("apps", primary_key="id",
                initial_loader=lambda: [_strip_ctx(r) for r in _load("apps.json", "apps")])
_store.register("app_assignments", primary_key="_pk",
                initial_loader=lambda: [{**_strip_ctx(r), "_pk": f"{r['app_id']}@{r['user_id']}"} for r in _load("app_assignments.json", "app_assignments")])


def _users_rows():
    return _store.table("users").rows()


def _groups_rows():
    return _store.table("groups").rows()


def _memberships_rows():
    return [{k: v for k, v in r.items() if k != "_pk"} for r in _store.table("memberships").rows()]


def _apps_rows():
    return _store.table("apps").rows()


def _app_assignments_rows():
    return [{k: v for k, v in r.items() if k != "_pk"} for r in _store.table("app_assignments").rows()]



def _load(filename, table):
    return read_seed_with_ctx(DATA_DIR / filename, _API, table)


def _strip_ctx(r):
    return {k: v for k, v in r.items() if not k.startswith("__")}


def _now():
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000Z")


# ---------------------------------------------------------------------------
# Load
# ---------------------------------------------------------------------------

def _coerce_users(rows):
    out = []
    for r in rows:
        out.append({
            **_strip_ctx(r),
            "activated": opt_str(r, "activated", default="") or None,
            "last_login": opt_str(r, "last_login", default="") or None,
        })
    return out












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
    return next((u for u in _users_rows() if u["id"] == user_id), None)


def _find_group(group_id):
    return next((g for g in _groups_rows() if g["id"] == group_id), None)


# ---------------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------------

def list_users(status=None, q=None):
    results = list(_users_rows())
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
    _store_insert("users", user)
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
    results = list(_groups_rows())
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
    member_ids = [m["user_id"] for m in _memberships_rows() if m["group_id"] == group_id]
    return [_serialize_user(u) for u in _users_rows() if u["id"] in member_ids]


# ---------------------------------------------------------------------------
# Apps
# ---------------------------------------------------------------------------

def list_apps(status=None):
    results = list(_apps_rows())
    if status:
        results = [a for a in results if a["status"] == status]
    return [_serialize_app(a) for a in results]

_store.eager_load()
