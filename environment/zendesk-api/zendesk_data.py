"""Data access module for the Zendesk Support API mock service.

Mirrors a subset of the Zendesk Ticketing API v2. IDs are integers (assigned
sequentially for new records). Mutations (created/updated tickets, comments)
are held in process memory and reset on container restart.
"""

import csv
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).parent

import sys as _sys
_sys.path.insert(0, str(DATA_DIR.parent))
from _mutable_store import (  # noqa: E402
    read_seed_with_ctx, get_store, opt_csv_list, opt_int, strict_bool)

_store = get_store("zendesk-api")
_API = "zendesk-api"

_API = "zendesk-api"


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
_store.register("organizations", primary_key="id",
                initial_loader=lambda: _coerce_orgs(_load("organizations.json", "organizations")))
_store.register("tickets", primary_key="id",
                initial_loader=lambda: _coerce_tickets(_load("tickets.json", "tickets")))
_store.register("comments", primary_key="id",
                initial_loader=lambda: _coerce_comments(_load("comments.json", "comments")))


def _users_rows():
    return _store.table("users").rows()


def _organizations_rows():
    return _store.table("organizations").rows()


def _tickets_rows():
    return _store.table("tickets").rows()


def _comments_rows():
    return _store.table("comments").rows()


VALID_STATUS = {"new", "open", "pending", "hold", "solved", "closed"}
VALID_PRIORITY = {"low", "normal", "high", "urgent"}


def _load(filename, table):
    return read_seed_with_ctx(DATA_DIR / filename, _API, table)


def _strip_ctx(r):
    return {k: v for k, v in r.items() if not k.startswith("__")}


def _now():
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


def _to_bool(v):
    return str(v).strip().lower() == "true"


def _to_int(v, default=None):
    if v is None or str(v).strip() == "":
        return default
    try:
        return int(v)
    except (TypeError, ValueError):
        return default


# ---------------------------------------------------------------------------
# Load + coerce
# ---------------------------------------------------------------------------

def _coerce_users(rows):
    return [{
        "id": opt_int(r, "id", default=None),
        "name": r["name"],
        "email": r["email"],
        "role": r["role"],
        "organization_id": opt_int(r, "organization_id", default=None),
        "active": strict_bool(r, "active"),
        "created_at": r["created_at"],
    } for r in rows]


def _coerce_orgs(rows):
    return [{
        "id": opt_int(r, "id", default=None),
        "name": r["name"],
        "domain_names": [d for d in opt_csv_list(r, "domain_names", sep=";") if d],
        "created_at": r["created_at"],
    } for r in rows]


def _coerce_tickets(rows):
    return [{
        "id": opt_int(r, "id", default=None),
        "subject": r["subject"],
        "description": r["description"],
        "status": r["status"],
        "priority": r["priority"],
        "type": r["type"],
        "requester_id": opt_int(r, "requester_id", default=None),
        "assignee_id": opt_int(r, "assignee_id", default=None),
        "organization_id": opt_int(r, "organization_id", default=None),
        "tags": [t for t in opt_csv_list(r, "tags", sep=";") if t],
        "created_at": r["created_at"],
        "updated_at": r["updated_at"],
    } for r in rows]


def _coerce_comments(rows):
    return [{
        "id": opt_int(r, "id", default=None),
        "ticket_id": opt_int(r, "ticket_id", default=None),
        "author_id": opt_int(r, "author_id", default=None),
        "body": r["body"],
        "public": strict_bool(r, "public"),
        "created_at": r["created_at"],
    } for r in rows]










# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _next_id(store):
    return (max((x["id"] for x in store), default=None) + 1) if store else 1


def _find(store, obj_id):
    obj_id = _to_int(obj_id)
    return next((x for x in store if x["id"] == obj_id), None)


# ---------------------------------------------------------------------------
# Tickets
# ---------------------------------------------------------------------------

def list_tickets(status=None, priority=None, assignee_id=None):
    results = list(_tickets_rows())
    if status:
        results = [t for t in results if t["status"] == status]
    if priority:
        results = [t for t in results if t["priority"] == priority]
    if assignee_id is not None:
        results = [t for t in results if t["assignee_id"] == _to_int(assignee_id)]
    results.sort(key=lambda t: t["id"])
    return {"tickets": results, "count": len(results)}


def get_ticket(ticket_id):
    t = _find(_tickets_rows(), ticket_id)
    if not t:
        return {"error": f"Ticket {ticket_id} not found"}
    return {"ticket": t}


def create_ticket(subject, description=None, priority="normal", ticket_type="question",
                  requester_id=None, assignee_id=None, organization_id=None,
                  tags=None, comment_body=None):
    if not subject:
        return {"error": "subject is required"}
    if priority and priority not in VALID_PRIORITY:
        return {"error": f"Invalid priority: {priority}"}
    now = _now()
    ticket_id = _next_id(_tickets_rows())
    ticket = {
        "id": ticket_id,
        "subject": subject,
        "description": description or (comment_body or ""),
        "status": "new",
        "priority": priority or "normal",
        "type": ticket_type or "question",
        "requester_id": _to_int(requester_id),
        "assignee_id": _to_int(assignee_id),
        "organization_id": _to_int(organization_id),
        "tags": tags or [],
        "created_at": now,
        "updated_at": now,
    }
    _store_insert("tickets", ticket)
    body = comment_body or description
    if body:
        _store_insert("comments", {
            "id": _next_id(_comments_rows()),
            "ticket_id": ticket_id,
            "author_id": _to_int(requester_id),
            "body": body,
            "public": True,
            "created_at": now,
        })
    return {"ticket": ticket}


def update_ticket(ticket_id, status=None, priority=None, assignee_id=None,
                  ticket_type=None, tags=None, comment_body=None,
                  comment_public=True, comment_author_id=None):
    t = _find(_tickets_rows(), ticket_id)
    if not t:
        return {"error": f"Ticket {ticket_id} not found"}
    if status is not None:
        if status not in VALID_STATUS:
            return {"error": f"Invalid status: {status}"}
        t["status"] = status
    if priority is not None:
        if priority not in VALID_PRIORITY:
            return {"error": f"Invalid priority: {priority}"}
        t["priority"] = priority
    if assignee_id is not None:
        t["assignee_id"] = _to_int(assignee_id)
    if ticket_type is not None:
        t["type"] = ticket_type
    if tags is not None:
        t["tags"] = tags
    if comment_body:
        _store_insert("comments", {
            "id": _next_id(_comments_rows()),
            "ticket_id": t["id"],
            "author_id": _to_int(comment_author_id) if comment_author_id is not None else t["assignee_id"],
            "body": comment_body,
            "public": bool(comment_public),
            "created_at": _now(),
        })
    t["updated_at"] = _now()
    return {"ticket": t}


# ---------------------------------------------------------------------------
# Comments
# ---------------------------------------------------------------------------

def list_comments(ticket_id):
    if not _find(_tickets_rows(), ticket_id):
        return {"error": f"Ticket {ticket_id} not found"}
    tid = _to_int(ticket_id)
    comments = [c for c in _comments_rows() if c["ticket_id"] == tid]
    comments.sort(key=lambda c: c["created_at"])
    return {"comments": comments, "count": len(comments)}


def create_comment(ticket_id, body, author_id=None, public=True):
    t = _find(_tickets_rows(), ticket_id)
    if not t:
        return {"error": f"Ticket {ticket_id} not found"}
    if not body:
        return {"error": "comment body is required"}
    comment = {
        "id": _next_id(_comments_rows()),
        "ticket_id": t["id"],
        "author_id": _to_int(author_id) if author_id is not None else t["assignee_id"],
        "body": body,
        "public": bool(public),
        "created_at": _now(),
    }
    _store_insert("comments", comment)
    t["updated_at"] = _now()
    return {"comment": comment}


# ---------------------------------------------------------------------------
# Users / Organizations
# ---------------------------------------------------------------------------

def list_users(role=None):
    results = list(_users_rows())
    if role:
        results = [u for u in results if u["role"] == role]
    return {"users": results, "count": len(results)}


def get_user(user_id):
    u = _find(_users_rows(), user_id)
    if not u:
        return {"error": f"User {user_id} not found"}
    return {"user": u}


def list_organizations():
    return {"organizations": list(_organizations_rows()), "count": len(_organizations_rows())}

_store.eager_load()
