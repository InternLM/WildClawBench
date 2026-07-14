"""Data access module for the Outlook (Microsoft Graph mail/calendar) mock service.

Mirrors a subset of the Microsoft Graph v1.0 API for the signed-in user's
mailbox: messages, calendar events, and contacts, plus sendMail. Graph wraps
collections as {"value": [...]}. Sent mail is appended to an in-memory store
that resets on restart.
"""

import csv
import secrets
import time
from pathlib import Path

DATA_DIR = Path(__file__).parent

import sys as _sys
_sys.path.insert(0, str(DATA_DIR.parent))
from _mutable_store import (
    read_seed_with_ctx, get_store, opt_csv_list, strict_bool)

_store = get_store("outlook-api")
_API = "outlook-api"


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

_store.register("messages", primary_key="id",
                initial_loader=lambda: _coerce_messages(_load("messages.json", "messages")))
_store.register("events", primary_key="id",
                initial_loader=lambda: _coerce_events(_load("events.json", "events")))
_store.register("contacts", primary_key="id",
                initial_loader=lambda: _coerce_contacts(_load("contacts.json", "contacts")))


def _messages_rows():
    return _store.table("messages").rows()


def _events_rows():
    return _store.table("events").rows()


def _contacts_rows():
    return _store.table("contacts").rows()



def _load(filename, table):
    return read_seed_with_ctx(DATA_DIR / filename, _API, table)


def _strip_ctx(r):
    return {k: v for k, v in r.items() if not k.startswith("__")}


def _to_bool(v):
    return str(v).strip().lower() == "true"


# The signed-in user (the "me").
_ME_NAME = "Alex Carter"
_ME_ADDRESS = "alex.carter@contoso.com"


# ---------------------------------------------------------------------------
# Load + coerce
# ---------------------------------------------------------------------------

def _coerce_messages(rows):
    out = []
    for r in rows:
        out.append({
            "id": r["id"],
            "subject": r["subject"],
            "from_name": r["from_name"],
            "from_address": r["from_address"],
            "to_name": r["to_name"],
            "to_address": r["to_address"],
            "bodyPreview": r["body_preview"],
            "contentType": r["content_type"],
            "isRead": strict_bool(r, "is_read"),
            "importance": r["importance"],
            "receivedDateTime": r["received_date"],
        })
    return out


def _coerce_events(rows):
    out = []
    for r in rows:
        out.append({
            "id": r["id"],
            "subject": r["subject"],
            "organizer_name": r["organizer_name"],
            "organizer_address": r["organizer_address"],
            "location": r["location"],
            "start": r["start_date"],
            "end": r["end_date"],
            "isAllDay": strict_bool(r, "is_all_day"),
            "isOnlineMeeting": strict_bool(r, "is_online"),
            "attendees": [x for x in opt_csv_list(r, "attendees", sep=";") if x],
        })
    return out


def _coerce_contacts(rows):
    out = []
    for r in rows:
        out.append({
            "id": r["id"],
            "displayName": r["display_name"],
            "givenName": r["given_name"],
            "surname": r["surname"],
            "email": r["email"],
            "jobTitle": r["job_title"],
            "companyName": r["company"],
            "mobilePhone": r["mobile_phone"],
        })
    return out








# ---------------------------------------------------------------------------
# Serializers (Graph resource shapes)
# ---------------------------------------------------------------------------

def _serialize_message(m):
    return {
        "id": m["id"],
        "subject": m["subject"],
        "bodyPreview": m["bodyPreview"],
        "importance": m["importance"],
        "isRead": m["isRead"],
        "receivedDateTime": m["receivedDateTime"],
        "from": {
            "emailAddress": {"name": m["from_name"], "address": m["from_address"]}
        },
        "toRecipients": [
            {"emailAddress": {"name": m["to_name"], "address": m["to_address"]}}
        ],
        "body": {"contentType": m["contentType"], "content": m["bodyPreview"]},
    }


def _serialize_event(e):
    return {
        "id": e["id"],
        "subject": e["subject"],
        "isAllDay": e["isAllDay"],
        "isOnlineMeeting": e["isOnlineMeeting"],
        "start": {"dateTime": e["start"], "timeZone": "UTC"},
        "end": {"dateTime": e["end"], "timeZone": "UTC"},
        "location": {"displayName": e["location"]},
        "organizer": {
            "emailAddress": {
                "name": e["organizer_name"],
                "address": e["organizer_address"],
            }
        },
        "attendees": [
            {"emailAddress": {"address": a}, "type": "required"}
            for a in e["attendees"]
        ],
    }


def _serialize_contact(c):
    return {
        "id": c["id"],
        "displayName": c["displayName"],
        "givenName": c["givenName"],
        "surname": c["surname"],
        "emailAddresses": [{"address": c["email"], "name": c["displayName"]}],
        "jobTitle": c["jobTitle"],
        "companyName": c["companyName"],
        "mobilePhone": c["mobilePhone"],
    }


# ---------------------------------------------------------------------------
# Messages
# ---------------------------------------------------------------------------

def list_messages(is_read=None):
    msgs = list(_messages_rows())
    if is_read is not None:
        msgs = [m for m in msgs if m["isRead"] == is_read]
    msgs = sorted(msgs, key=lambda m: m["receivedDateTime"], reverse=True)
    return {"value": [_serialize_message(m) for m in msgs]}


def get_message(message_id):
    for m in _messages_rows():
        if m["id"] == message_id:
            return _serialize_message(m)
    return {"error": "message not found", "message": f"Message {message_id} not found"}


def send_mail(subject, content, to_recipients, content_type="HTML"):
    if not to_recipients:
        return {"error": "invalid request", "message": "message.toRecipients is required"}
    to_address = to_recipients[0]
    msg = {
        "id": "AAMkAGsent" + secrets.token_hex(6),
        "subject": subject or "(no subject)",
        "from_name": _ME_NAME,
        "from_address": _ME_ADDRESS,
        "to_name": to_address,
        "to_address": to_address,
        "bodyPreview": (content or "")[:255],
        "contentType": (content_type or "HTML").lower(),
        "isRead": True,
        "importance": "normal",
        "receivedDateTime": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    _store_insert("messages", msg)
    return {"status": "accepted", "id": msg["id"]}


# ---------------------------------------------------------------------------
# Events
# ---------------------------------------------------------------------------

def list_events():
    events = sorted(_events_rows(), key=lambda e: e["start"])
    return {"value": [_serialize_event(e) for e in events]}


# ---------------------------------------------------------------------------
# Contacts
# ---------------------------------------------------------------------------

def list_contacts():
    contacts = sorted(_contacts_rows(), key=lambda c: c["displayName"])
    return {"value": [_serialize_contact(c) for c in contacts]}

_store.eager_load()
