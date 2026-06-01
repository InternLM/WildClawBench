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


def _load(filename):
    with open(DATA_DIR / filename, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


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


# ---------------------------------------------------------------------------
# Load + coerce
# ---------------------------------------------------------------------------

def _coerce_contacts(rows):
    out = []
    for r in rows:
        out.append({
            "id": r["id"],
            "role": r["role"],
            "name": r["name"],
            "email": r["email"] or None,
            "phone": r["phone"] or None,
            "company_id": r["company_id"] or None,
            "created_at": r["created_at"],
            "last_seen_at": r["last_seen_at"] or None,
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
            "monthly_spend": _to_float(r["monthly_spend"]),
            "user_count": _to_int(r["user_count"]),
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
            "assignee_id": r["assignee_id"] or None,
            "open": _to_bool(r["open"]),
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
            "body": r["body"] or None,
            "created_at": r["created_at"],
        })
    return out


_contacts_store = deepcopy(_coerce_contacts(_load("contacts.csv")))
_companies_store = deepcopy(_coerce_companies(_load("companies.csv")))
_conversations_store = deepcopy(_coerce_conversations(_load("conversations.csv")))
_parts_store = deepcopy(_coerce_parts(_load("conversation_parts.csv")))


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

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
        parts = [p for p in _parts_store if p["conversation_id"] == conv["id"]]
        parts = sorted(parts, key=lambda p: p["created_at"])
        obj["conversation_parts"] = {
            "type": "conversation_part.list",
            "total_count": len(parts),
            "conversation_parts": [deepcopy(p) for p in parts],
        }
    return obj


# ---------------------------------------------------------------------------
# Contacts
# ---------------------------------------------------------------------------

def list_contacts(role=None):
    contacts = list(_contacts_store)
    if role:
        contacts = [c for c in contacts if c["role"] == role]
    return {
        "type": "list",
        "data": deepcopy(contacts),
        "total_count": len(contacts),
    }


def get_contact(contact_id):
    for c in _contacts_store:
        if c["id"] == contact_id:
            return {"type": "contact", **deepcopy(c)}
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
    _contacts_store.append(contact)
    return {"type": "contact", **deepcopy(contact)}


# ---------------------------------------------------------------------------
# Companies
# ---------------------------------------------------------------------------

def list_companies():
    return {
        "type": "list",
        "data": deepcopy(_companies_store),
        "total_count": len(_companies_store),
    }


def get_company(company_id):
    for c in _companies_store:
        if c["id"] == company_id or c["company_id"] == company_id:
            return {"type": "company", **deepcopy(c)}
    return {"error": f"Company {company_id} not found"}


# ---------------------------------------------------------------------------
# Conversations
# ---------------------------------------------------------------------------

def list_conversations(state=None):
    convs = list(_conversations_store)
    if state:
        convs = [c for c in convs if c["state"] == state]
    return {
        "type": "conversation.list",
        "conversations": [_conversation_obj(c) for c in convs],
        "total_count": len(convs),
    }


def get_conversation(conversation_id):
    for c in _conversations_store:
        if c["id"] == conversation_id:
            return _conversation_obj(c, with_parts=True)
    return {"error": f"Conversation {conversation_id} not found"}


def create_conversation(contact_id, body, title=""):
    if not any(c["id"] == contact_id for c in _contacts_store):
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
    _conversations_store.append(conv)
    part = {
        "id": _new_id("part"),
        "conversation_id": conv["id"],
        "part_type": "comment",
        "author_type": "user",
        "author_id": contact_id,
        "body": body,
        "created_at": now,
    }
    _parts_store.append(part)
    return _conversation_obj(conv, with_parts=True)


def _find_conversation(conversation_id):
    return next((c for c in _conversations_store if c["id"] == conversation_id), None)


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
    _parts_store.append(part)
    conv["updated_at"] = now
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
    _parts_store.append(part)

    if message_type == "close":
        conv["state"] = "closed"
        conv["open"] = False
    elif message_type == "open":
        conv["state"] = "open"
        conv["open"] = True
    elif message_type == "assignment":
        conv["assignee_id"] = assignee_id or author_id
    conv["updated_at"] = now
    return _conversation_obj(conv, with_parts=True)
