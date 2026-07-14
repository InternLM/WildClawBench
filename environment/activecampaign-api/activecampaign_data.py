"""Data access module for the ActiveCampaign API mock service (v3).

Mirrors a subset of the ActiveCampaign API v3: contacts (list/get/create),
lists, campaigns, and deals. List responses use ActiveCampaign's convention of
a top-level plural key plus a `meta` block containing the total count.
"""

import csv
from datetime import datetime, timezone
from pathlib import Path

DATA_DIR = Path(__file__).parent

import sys as _sys
_sys.path.insert(0, str(DATA_DIR.parent))
from _mutable_store import read_seed_with_ctx, get_store  # noqa: E402

_store = get_store("activecampaign-api")
_API = "activecampaign-api"


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

_store.register("contacts", primary_key="id",
                initial_loader=lambda: _coerce_contacts(_load("contacts.json", "contacts")))
_store.register("lists", primary_key="id",
                initial_loader=lambda: _coerce_lists(_load("lists.json", "lists")))
_store.register("campaigns", primary_key="id",
                initial_loader=lambda: _coerce_campaigns(_load("campaigns.json", "campaigns")))
_store.register("deals", primary_key="id",
                initial_loader=lambda: _coerce_deals(_load("deals.json", "deals")))


def _contacts_rows():
    return _store.table("contacts").rows()


def _lists_rows():
    return _store.table("lists").rows()


def _campaigns_rows():
    return _store.table("campaigns").rows()


def _deals_rows():
    return _store.table("deals").rows()



def _load(filename, table):
    return read_seed_with_ctx(DATA_DIR / filename, _API, table)


def _strip_ctx(r):
    return {k: v for k, v in r.items() if not k.startswith("__")}


def _now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00")


# ---------------------------------------------------------------------------
# Load + coerce
# ---------------------------------------------------------------------------

def _coerce_contacts(rows):
    out = []
    for r in rows:
        out.append({
            "id": r["id"],
            "email": r["email"],
            "first_name": r["first_name"],
            "last_name": r["last_name"],
            "phone": r["phone"],
            "status": r["status"],
            "created_timestamp": r["created_timestamp"],
            "updated_timestamp": r["updated_timestamp"],
        })
    return out


def _coerce_lists(rows):
    out = []
    for r in rows:
        out.append({
            "id": r["id"],
            "name": r["name"],
            "stringid": r["stringid"],
            "subscriber_count": r["subscriber_count"],
            "sender_url": r["sender_url"],
            "sender_reminder": r["sender_reminder"],
            "created_timestamp": r["created_timestamp"],
        })
    return out


def _coerce_campaigns(rows):
    out = []
    for r in rows:
        out.append({
            "id": r["id"],
            "name": r["name"],
            "type": r["type"],
            "status": r["status"],
            "list_id": r["list_id"],
            "subject": r["subject"],
            "send_amt": r["send_amt"],
            "opens": r["opens"],
            "clicks": r["clicks"],
            "sdate": r["sdate"],
            "created_timestamp": r["created_timestamp"],
        })
    return out


def _coerce_deals(rows):
    out = []
    for r in rows:
        out.append({
            "id": r["id"],
            "title": r["title"],
            "contact_id": r["contact_id"],
            "value": r["value"],
            "currency": r["currency"],
            "status": r["status"],
            "stage": r["stage"],
            "owner": r["owner"],
            "created_timestamp": r["created_timestamp"],
            "updated_timestamp": r["updated_timestamp"],
        })
    return out










# ---------------------------------------------------------------------------
# Serializers
# ---------------------------------------------------------------------------

def _serialize_contact(c):
    return {
        "id": c["id"],
        "email": c["email"],
        "firstName": c["first_name"],
        "lastName": c["last_name"],
        "phone": c["phone"],
        "status": c["status"],
        "cdate": c["created_timestamp"],
        "udate": c["updated_timestamp"],
        "links": {
            "contactLists": f"/api/3/contacts/{c['id']}/contactLists",
            "deals": f"/api/3/contacts/{c['id']}/deals",
        },
    }


def _serialize_list(l):
    return {
        "id": l["id"],
        "name": l["name"],
        "stringid": l["stringid"],
        "subscriber_count": l["subscriber_count"],
        "sender_url": l["sender_url"],
        "sender_reminder": l["sender_reminder"],
        "cdate": l["created_timestamp"],
    }


def _serialize_campaign(c):
    return {
        "id": c["id"],
        "name": c["name"],
        "type": c["type"],
        "status": c["status"],
        "listid": c["list_id"],
        "subject": c["subject"],
        "send_amt": c["send_amt"],
        "opens": c["opens"],
        "linkclicks": c["clicks"],
        "sdate": c["sdate"],
        "cdate": c["created_timestamp"],
    }


def _serialize_deal(d):
    return {
        "id": d["id"],
        "title": d["title"],
        "contact": d["contact_id"],
        "value": d["value"],
        "currency": d["currency"],
        "status": d["status"],
        "stage": d["stage"],
        "owner": d["owner"],
        "cdate": d["created_timestamp"],
        "mdate": d["updated_timestamp"],
    }


def _meta(total, offset=0, limit=20):
    return {"total": str(total), "page_input": {"offset": offset, "limit": limit}}


# ---------------------------------------------------------------------------
# Contacts
# ---------------------------------------------------------------------------

def list_contacts(email=None, status=None, limit=20, offset=0):
    contacts = _contacts_rows()
    if email:
        contacts = [c for c in contacts if c["email"].lower() == email.lower()]
    if status is not None:
        contacts = [c for c in contacts if c["status"] == str(status)]
    total = len(contacts)
    window = contacts[offset:offset + limit]
    return {
        "contacts": [_serialize_contact(c) for c in window],
        "meta": _meta(total, offset=offset, limit=limit),
    }


def get_contact(contact_id):
    c = next((x for x in _contacts_rows() if x["id"] == str(contact_id)), None)
    if not c:
        return {"error": "not_found", "message": f"Contact {contact_id} not found"}
    return {"contact": _serialize_contact(c)}


def create_contact(email, first_name="", last_name="", phone="", status="1"):
    if not email:
        return {"error": "validation", "message": "email is required"}
    existing = next((c for c in _contacts_rows() if c["email"].lower() == email.lower()), None)
    if existing:
        return {"error": "duplicate", "message": f"Contact with email {email} already exists"}
    now = _now_iso()
    new_id = str(max((int(c["id"]) for c in _contacts_rows()), default=0) + 1)
    contact = {
        "id": new_id,
        "email": email,
        "first_name": first_name or "",
        "last_name": last_name or "",
        "phone": phone or "",
        "status": str(status),
        "created_timestamp": now,
        "updated_timestamp": now,
    }
    _store_insert("contacts", contact)
    return {"contact": _serialize_contact(contact)}


# ---------------------------------------------------------------------------
# Lists
# ---------------------------------------------------------------------------

def list_lists(limit=20, offset=0):
    total = len(_lists_rows())
    window = _lists_rows()[offset:offset + limit]
    return {
        "lists": [_serialize_list(l) for l in window],
        "meta": _meta(total, offset=offset, limit=limit),
    }


# ---------------------------------------------------------------------------
# Campaigns
# ---------------------------------------------------------------------------

def list_campaigns(limit=20, offset=0):
    total = len(_campaigns_rows())
    window = _campaigns_rows()[offset:offset + limit]
    return {
        "campaigns": [_serialize_campaign(c) for c in window],
        "meta": _meta(total, offset=offset, limit=limit),
    }


# ---------------------------------------------------------------------------
# Deals
# ---------------------------------------------------------------------------

def list_deals(limit=20, offset=0):
    total = len(_deals_rows())
    window = _deals_rows()[offset:offset + limit]
    return {
        "deals": [_serialize_deal(d) for d in window],
        "meta": _meta(total, offset=offset, limit=limit),
    }

_store.eager_load()
