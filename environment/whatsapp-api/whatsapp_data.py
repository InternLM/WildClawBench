"""Data access module for the WhatsApp Cloud API mock service."""

import csv
import json
import uuid
from copy import deepcopy
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).parent


def _load(filename):
    with open(DATA_DIR / filename, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _now():
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


def _to_bool(v):
    return str(v).strip().lower() == "true"


def _coerce_contacts(rows):
    return [{**r, "opted_in": _to_bool(r["opted_in"])} for r in rows]


def _coerce_conversations(rows):
    return [{**r, "within_24h_window": _to_bool(r["within_24h_window"])} for r in rows]


_contacts = _coerce_contacts(_load("contacts.csv"))
_templates = _load("templates.csv")
_conversations = _coerce_conversations(_load("conversations.csv"))
_messages = _load("messages.csv")

with open(DATA_DIR / "business.json", encoding="utf-8") as _f:
    _business = json.load(_f)

_contacts_store = deepcopy(_contacts)
_templates_store = deepcopy(_templates)
_conversations_store = deepcopy(_conversations)
_messages_store = deepcopy(_messages)
_business_store = deepcopy(_business)


def _new_message_id():
    return f"wamid.{uuid.uuid4().hex[:24].upper()}"


# ---------------------------------------------------------------------------
# Business / phone numbers
# ---------------------------------------------------------------------------

def get_business():
    return _business_store


# ---------------------------------------------------------------------------
# Contacts
# ---------------------------------------------------------------------------

def list_contacts(opted_in_only=False):
    results = list(_contacts_store)
    if opted_in_only:
        results = [c for c in results if c["opted_in"]]
    return {"data": results}


def get_contact(wa_id):
    for c in _contacts_store:
        if c["wa_id"] == wa_id:
            return c
    return {"error": f"Contact {wa_id} not found"}


# ---------------------------------------------------------------------------
# Templates
# ---------------------------------------------------------------------------

def list_templates(status=None):
    results = list(_templates_store)
    if status:
        results = [t for t in results if t["status"].upper() == status.upper()]
    return {"data": results}


def get_template(name):
    for t in _templates_store:
        if t["name"] == name:
            return t
    return {"error": f"Template {name} not found"}


# ---------------------------------------------------------------------------
# Conversations / messages
# ---------------------------------------------------------------------------

def list_conversations(wa_id=None):
    results = list(_conversations_store)
    if wa_id:
        results = [c for c in results if c["wa_id"] == wa_id]
    results.sort(key=lambda c: c["last_message_at"], reverse=True)
    return {"data": results}


def list_messages(conversation_id=None, wa_id=None, limit=20):
    results = list(_messages_store)
    if conversation_id:
        results = [m for m in results if m["conversation_id"] == conversation_id]
    elif wa_id:
        conv_ids = {c["conversation_id"] for c in _conversations_store if c["wa_id"] == wa_id}
        results = [m for m in results if m["conversation_id"] in conv_ids]
    results.sort(key=lambda m: m["sent_at"], reverse=True)
    return {"data": results[:limit]}


def send_text(to_wa_id, body):
    contact = next((c for c in _contacts_store if c["wa_id"] == to_wa_id), None)
    if not contact:
        return {"error": f"Contact {to_wa_id} not found"}
    if not contact["opted_in"]:
        return {"error": "Recipient has not opted in to messages"}
    conv = next((c for c in _conversations_store if c["wa_id"] == to_wa_id), None)
    if not conv or not conv["within_24h_window"]:
        return {"error": "Outside 24-hour customer service window; use a template message"}

    msg_id = _new_message_id()
    now = _now()
    msg = {
        "message_id": msg_id,
        "conversation_id": conv["conversation_id"],
        "direction": "outbound",
        "from_wa_id": _business_store["phone_number_id"].replace("PNI-", ""),
        "to_wa_id": to_wa_id,
        "type": "text",
        "text": body,
        "template_name": "",
        "status": "sent",
        "sent_at": now,
    }
    _messages_store.append(msg)
    for i, c in enumerate(_conversations_store):
        if c["conversation_id"] == conv["conversation_id"]:
            _conversations_store[i]["last_message_at"] = now
    return {"messages": [{"id": msg_id, "message_status": "accepted"}]}


def send_template(to_wa_id, template_name, components=None):
    contact = next((c for c in _contacts_store if c["wa_id"] == to_wa_id), None)
    if not contact:
        return {"error": f"Contact {to_wa_id} not found"}
    template = next((t for t in _templates_store if t["name"] == template_name), None)
    if not template:
        return {"error": f"Template {template_name} not found"}
    if template["status"].upper() != "APPROVED":
        return {"error": f"Template {template_name} is not approved (status: {template['status']})"}

    conv = next((c for c in _conversations_store if c["wa_id"] == to_wa_id), None)
    if not conv:
        conv = {
            "conversation_id": f"conv-{uuid.uuid4().hex[:6]}",
            "wa_id": to_wa_id,
            "started_at": _now(),
            "last_message_at": _now(),
            "origin": "business_initiated",
            "within_24h_window": True,
        }
        _conversations_store.append(conv)

    msg_id = _new_message_id()
    now = _now()
    msg = {
        "message_id": msg_id,
        "conversation_id": conv["conversation_id"],
        "direction": "outbound",
        "from_wa_id": _business_store["phone_number_id"].replace("PNI-", ""),
        "to_wa_id": to_wa_id,
        "type": "template",
        "text": "",
        "template_name": template_name,
        "status": "sent",
        "sent_at": now,
    }
    _messages_store.append(msg)
    for i, c in enumerate(_conversations_store):
        if c["conversation_id"] == conv["conversation_id"]:
            _conversations_store[i]["last_message_at"] = now
    return {"messages": [{"id": msg_id, "message_status": "accepted"}]}


def mark_read(message_id):
    for i, m in enumerate(_messages_store):
        if m["message_id"] == message_id:
            _messages_store[i]["status"] = "read"
            return {"success": True, "message_id": message_id}
    return {"error": f"Message {message_id} not found"}
