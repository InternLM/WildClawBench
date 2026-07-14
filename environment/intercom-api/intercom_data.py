"""Data access module for the Intercom API mock service.

Models customer-messaging objects: contacts (role user/lead), companies,
conversations (state open/closed) and their conversation parts (messages,
replies, and admin actions such as assign/close).
"""

import csv
import uuid
from copy import deepcopy
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).parent

import sys as _sys
_sys.path.insert(0, str(DATA_DIR.parent))
from _mutable_store import (
    read_seed_with_ctx, get_store, opt_float, opt_int, opt_str, strict_bool)
_store = get_store("intercom-api")
_API = "intercom-api"


def _load(filename, table):
    return read_seed_with_ctx(DATA_DIR / filename, _API, table)


def _strip_ctx(r):
    return {k: v for k, v in r.items() if not k.startswith("__")}


def _now():
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000Z")


def _epoch():
    return int(datetime.utcnow().timestamp())


def _to_bool(v):
    return str(v).strip().lower() == "true"


def _to_int(v, default=0):
    try:
        return int(v)
    except (TypeError, ValueError):
        return default


def _to_float(v, default=0.0):
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


def _coerce_contacts(rows):
    out = []
    for r in rows:
        out.append({
            "id": r["id"],
            "role": r["role"],
            "name": r["name"],
            "email": opt_str(r, "email", default="") or None,
            "phone": opt_str(r, "phone", default="") or None,
            "company_id": opt_str(r, "company_id", default="") or None,
            "created_at": r["created_at"],
            "last_seen_at": opt_str(r, "last_seen_at", default="") or None,
        })
    return out


def _coerce_companies(rows):
    out = []
    for r in rows:
        out.append({
            "id": r["id"],
            "company_id": r["company_id"],
            "name": r["name"],
            "plan": r["plan"],
            "monthly_spend": opt_float(r, "monthly_spend", default=0.0),
            "user_count": opt_int(r, "user_count", default=0),
            "industry": r["industry"],
            "created_at": r["created_at"],
        })
    return out


def _coerce_conversations(rows):
    out = []
    for r in rows:
        out.append({
            "id": r["id"],
            "contact_id": r["contact_id"],
            "state": r["state"],
            "title": r["title"],
            "created_at": r["created_at"],
            "updated_at": r["updated_at"],
            "assignee_id": opt_str(r, "assignee_id", default="") or None,
            "open": strict_bool(r, "open"),
        })
    return out


def _coerce_parts(rows):
    out = []
    for r in rows:
        out.append({
            "id": r["id"],
            "conversation_id": r["conversation_id"],
            "part_type": r["part_type"],
            "author_type": r["author_type"],
            "author_id": r["author_id"],
            "body": opt_str(r, "body", default="") or None,
            "created_at": r["created_at"],
        })
    return out


_store.register("contacts", primary_key="id",
                initial_loader=lambda: _coerce_contacts(_load("contacts.json", "contacts")))
_store.register("companies", primary_key="id",
                initial_loader=lambda: _coerce_companies(_load("companies.json", "companies")))
_store.register("conversations", primary_key="id",
                initial_loader=lambda: _coerce_conversations(_load("conversations.json", "conversations")))
_store.register("parts", primary_key="id",
                initial_loader=lambda: _coerce_parts(_load("conversation_parts.json", "parts")))


def _contacts_rows(): return _store.table("contacts").rows()
def _companies_rows(): return _store.table("companies").rows()
def _conversations_rows(): return _store.table("conversations").rows()
def _parts_rows(): return _store.table("parts").rows()


def _new_id(prefix):
    return f"{prefix}-{uuid.uuid4().hex[:12]}"


def _conversation_obj(conv, with_parts=False):
    obj = {
        "type": "conversation",
        "id": conv["id"],
        "state": conv["state"],
        "open": conv["open"],
        "title": conv["title"],
        "created_at": conv["created_at"],
        "updated_at": conv["updated_at"],
        "contact_id": conv["contact_id"],
        "admin_assignee_id": conv["assignee_id"],
    }
    if with_parts:
        parts = [p for p in _parts_rows() if p["conversation_id"] == conv["id"]]
        parts = sorted(parts, key=lambda p: p["created_at"])
        obj["conversation_parts"] = {
            "type": "conversation_part.list",
            "total_count": len(parts),
            "conversation_parts": [deepcopy(p) for p in parts],
        }
    return obj


def list_contacts(role=None):
    contacts = _contacts_rows()
    if role:
        contacts = [c for c in contacts if c["role"] == role]
    return {
        "type": "list",
        "data": contacts,
        "total_count": len(contacts),
    }


def get_contact(contact_id):
    c = _store.table("contacts").get(contact_id)
    if c:
        return {"type": "contact", **c}
    return {"error": f"Contact {contact_id} not found"}


def create_contact(role="user", name="", email=None, phone=None, company_id=None):
    contact = {
        "id": _new_id("contact"),
        "role": role,
        "name": name,
        "email": email,
        "phone": phone,
        "company_id": company_id,
        "created_at": _now(),
        "last_seen_at": None,
    }
    _store.table("contacts").upsert(contact)
    return {"type": "contact", **contact}


def list_companies():
    rows = _companies_rows()
    return {
        "type": "list",
        "data": rows,
        "total_count": len(rows),
    }


def get_company(company_id):
    for c in _companies_rows():
        if c["id"] == company_id or c["company_id"] == company_id:
            return {"type": "company", **c}
    return {"error": f"Company {company_id} not found"}


def list_conversations(state=None):
    convs = _conversations_rows()
    if state:
        convs = [c for c in convs if c["state"] == state]
    return {
        "type": "conversation.list",
        "conversations": [_conversation_obj(c) for c in convs],
        "total_count": len(convs),
    }


def get_conversation(conversation_id):
    c = _store.table("conversations").get(conversation_id)
    if c:
        return _conversation_obj(c, with_parts=True)
    return {"error": f"Conversation {conversation_id} not found"}


def create_conversation(contact_id, body, title=""):
    if not _store.table("contacts").get(contact_id):
        return {"error": f"Contact {contact_id} not found"}
    now = _now()
    conv = {
        "id": _new_id("conv"),
        "contact_id": contact_id,
        "state": "open",
        "title": title or (body[:60] if body else "New conversation"),
        "created_at": now,
        "updated_at": now,
        "assignee_id": None,
        "open": True,
    }
    _store.table("conversations").upsert(conv)
    part = {
        "id": _new_id("part"),
        "conversation_id": conv["id"],
        "part_type": "comment",
        "author_type": "user",
        "author_id": contact_id,
        "body": body,
        "created_at": now,
    }
    _store.table("parts").upsert(part)
    return _conversation_obj(conv, with_parts=True)


def _find_conversation(conversation_id):
    return _store.table("conversations").get(conversation_id)


def reply_conversation(conversation_id, body, author_type="admin", author_id="admin-jonas"):
    conv = _find_conversation(conversation_id)
    if not conv:
        return {"error": f"Conversation {conversation_id} not found"}
    now = _now()
    part = {
        "id": _new_id("part"),
        "conversation_id": conversation_id,
        "part_type": "comment",
        "author_type": author_type,
        "author_id": author_id,
        "body": body,
        "created_at": now,
    }
    _store.table("parts").upsert(part)
    _store.table("conversations").patch(conversation_id, {"updated_at": now})
    conv = _find_conversation(conversation_id) or conv
    return _conversation_obj(conv, with_parts=True)


def add_part(conversation_id, message_type, body=None, author_id="admin-jonas", assignee_id=None):
    """Add an admin part: a note, an assignment, or a close action.

    ``message_type`` is one of: comment / note / assignment / close / open.
    """
    conv = _find_conversation(conversation_id)
    if not conv:
        return {"error": f"Conversation {conversation_id} not found"}
    now = _now()
    part = {
        "id": _new_id("part"),
        "conversation_id": conversation_id,
        "part_type": message_type,
        "author_type": "admin",
        "author_id": author_id,
        "body": body,
        "created_at": now,
    }
    _store.table("parts").upsert(part)

    patch: dict = {"updated_at": now}
    if message_type == "close":
        patch["state"] = "closed"
        patch["open"] = False
    elif message_type == "open":
        patch["state"] = "open"
        patch["open"] = True
    elif message_type == "assignment":
        patch["assignee_id"] = assignee_id or author_id
    _store.table("conversations").patch(conversation_id, patch)
    conv = _find_conversation(conversation_id) or conv
    return _conversation_obj(conv, with_parts=True)

_store.eager_load()
