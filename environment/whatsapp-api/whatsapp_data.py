"""Data access module for the WhatsApp Cloud API mock service."""

import csv
import json
import uuid
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).parent

import sys as _sys
_sys.path.insert(0, str(DATA_DIR.parent))
from _mutable_store import (
    read_seed_with_ctx, get_store,
    strict_bool,
)

_store = get_store("whatsapp-api")
_API = "whatsapp-api"

_API = "whatsapp-api"



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

_store.register("contacts", primary_key="wa_id",
                initial_loader=lambda: _coerce_contacts(_load("contacts.json", "contacts")))
_store.register("conversations", primary_key="conversation_id",
                initial_loader=lambda: _coerce_conversations(_load("conversations.json", "conversations")))
_store.register("templates", primary_key="name",
                initial_loader=lambda: [_strip_ctx(r) for r in _load("templates.json", "templates")])
_store.register("messages", primary_key="message_id",
                initial_loader=lambda: [_strip_ctx(r) for r in _load("messages.json", "messages")])
_store.register_document("business", initial_loader=lambda: __import__('json').load(open(DATA_DIR / "business.json", encoding="utf-8")))


def _contacts_rows():
    return _store.table("contacts").rows()


def _conversations_rows():
    return _store.table("conversations").rows()


def _templates_rows():
    return _store.table("templates").rows()


def _messages_rows():
    return _store.table("messages").rows()


def _business_doc():
    return _store.document("business").get()



def _load(filename, table):
    return read_seed_with_ctx(DATA_DIR / filename, _API, table)


def _strip_ctx(r):
    return {k: v for k, v in r.items() if not k.startswith("__")}


def _now():
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


def _to_bool(v):
    return str(v).strip().lower() == "true"


def _coerce_contacts(rows):
    return [{**_strip_ctx(r), "opted_in": strict_bool(r, "opted_in")} for r in rows]


def _coerce_conversations(rows):
    return [{**_strip_ctx(r), "within_24h_window": strict_bool(r, "within_24h_window")} for r in rows]






def _new_message_id():
    return f"wamid.{uuid.uuid4().hex[:24].upper()}"


# ---------------------------------------------------------------------------
# Business / phone numbers
# ---------------------------------------------------------------------------

def get_business():
    return _business_doc()


# ---------------------------------------------------------------------------
# Contacts
# ---------------------------------------------------------------------------

def list_contacts(opted_in_only=False):
    results = list(_contacts_rows())
    if opted_in_only:
        results = [c for c in results if c["opted_in"]]
    return {"data": results}


def get_contact(wa_id):
    for c in _contacts_rows():
        if c["wa_id"] == wa_id:
            return c
    return {"error": f"Contact {wa_id} not found"}


# ---------------------------------------------------------------------------
# Templates
# ---------------------------------------------------------------------------

def list_templates(status=None):
    results = list(_templates_rows())
    if status:
        results = [t for t in results if t["status"].upper() == status.upper()]
    return {"data": results}


def get_template(name):
    for t in _templates_rows():
        if t["name"] == name:
            return t
    return {"error": f"Template {name} not found"}


# ---------------------------------------------------------------------------
# Conversations / messages
# ---------------------------------------------------------------------------

def list_conversations(wa_id=None):
    results = list(_conversations_rows())
    if wa_id:
        results = [c for c in results if c["wa_id"] == wa_id]
    results.sort(key=lambda c: c["last_message_at"], reverse=True)
    return {"data": results}


def list_messages(conversation_id=None, wa_id=None, limit=20):
    results = list(_messages_rows())
    if conversation_id:
        results = [m for m in results if m["conversation_id"] == conversation_id]
    elif wa_id:
        conv_ids = {c["conversation_id"] for c in _conversations_rows() if c["wa_id"] == wa_id}
        results = [m for m in results if m["conversation_id"] in conv_ids]
    results.sort(key=lambda m: m["sent_at"], reverse=True)
    return {"data": results[:limit]}


def send_text(to_wa_id, body):
    contact = next((c for c in _contacts_rows() if c["wa_id"] == to_wa_id), None)
    if not contact:
        return {"error": f"Contact {to_wa_id} not found"}
    if not contact["opted_in"]:
        return {"error": "Recipient has not opted in to messages"}
    conv = next((c for c in _conversations_rows() if c["wa_id"] == to_wa_id), None)
    if not conv or not conv["within_24h_window"]:
        return {"error": "Outside 24-hour customer service window; use a template message"}

    msg_id = _new_message_id()
    now = _now()
    msg = {
        "message_id": msg_id,
        "conversation_id": conv["conversation_id"],
        "direction": "outbound",
        "from_wa_id": _business_doc()["phone_number_id"].replace("PNI-", ""),
        "to_wa_id": to_wa_id,
        "type": "text",
        "text": body,
        "template_name": "",
        "status": "sent",
        "sent_at": now,
    }
    _store_insert("messages", msg)
    for c in _conversations_rows():
        if c["conversation_id"] == conv["conversation_id"]:
            _changes = {"last_message_at": now}
            c.update(_changes)
            _store_patch("conversations", c, _changes)
    return {"messages": [{"id": msg_id, "message_status": "accepted"}]}


def send_template(to_wa_id, template_name, components=None):
    contact = next((c for c in _contacts_rows() if c["wa_id"] == to_wa_id), None)
    if not contact:
        return {"error": f"Contact {to_wa_id} not found"}
    template = next((t for t in _templates_rows() if t["name"] == template_name), None)
    if not template:
        return {"error": f"Template {template_name} not found"}
    if template["status"].upper() != "APPROVED":
        return {"error": f"Template {template_name} is not approved (status: {template['status']})"}

    conv = next((c for c in _conversations_rows() if c["wa_id"] == to_wa_id), None)
    if not conv:
        conv = {
            "conversation_id": f"conv-{uuid.uuid4().hex[:6]}",
            "wa_id": to_wa_id,
            "started_at": _now(),
            "last_message_at": _now(),
            "origin": "business_initiated",
            "within_24h_window": True,
        }
        _store_insert("conversations", conv)

    msg_id = _new_message_id()
    now = _now()
    msg = {
        "message_id": msg_id,
        "conversation_id": conv["conversation_id"],
        "direction": "outbound",
        "from_wa_id": _business_doc()["phone_number_id"].replace("PNI-", ""),
        "to_wa_id": to_wa_id,
        "type": "template",
        "text": "",
        "template_name": template_name,
        "status": "sent",
        "sent_at": now,
    }
    _store_insert("messages", msg)
    for c in _conversations_rows():
        if c["conversation_id"] == conv["conversation_id"]:
            _changes = {"last_message_at": now}
            c.update(_changes)
            _store_patch("conversations", c, _changes)
    return {"messages": [{"id": msg_id, "message_status": "accepted"}]}


def mark_read(message_id):
    for m in _messages_rows():
        if m["message_id"] == message_id:
            _changes = {"status": "read"}
            m.update(_changes)
            _store_patch("messages", m, _changes)
            return {"success": True, "message_id": message_id}
    return {"error": f"Message {message_id} not found"}

_store.eager_load()
