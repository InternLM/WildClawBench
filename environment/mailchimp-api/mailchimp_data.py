"""Data access module for the Mailchimp Marketing API mock service.

Models email-marketing objects: lists (audiences), members, campaigns and
reports. A member's ``id`` is the Mailchimp ``subscriber_hash`` = MD5 of the
lowercased email address, so lookups accept either the hash or the raw email.
"""

import csv
import hashlib
import uuid
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).parent

import sys as _sys
_sys.path.insert(0, str(DATA_DIR.parent))
from _mutable_store import (
    read_seed_with_ctx, get_store, opt_float, opt_int, opt_str)
_store = get_store("mailchimp-api")
_API = "mailchimp-api"


def _load(filename, table):
    return read_seed_with_ctx(DATA_DIR / filename, _API, table)


def _strip_ctx(r):
    return {k: v for k, v in r.items() if not k.startswith("__")}


def _now():
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S+00:00")


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


def _subscriber_hash(email):
    return hashlib.md5(email.strip().lower().encode("utf-8")).hexdigest()


def _coerce_lists(rows):
    out = []
    for r in rows:
        out.append({
            "id": r["id"],
            "name": r["name"],
            "company": r["company"],
            "from_name": r["from_name"],
            "from_email": r["from_email"],
            "subject": r["subject"],
            "member_count": opt_int(r, "member_count", default=0),
            "unsubscribe_count": opt_int(r, "unsubscribe_count", default=0),
            "date_created": r["date_created"],
        })
    return out


def _coerce_members(rows):
    out = []
    for r in rows:
        email = r["email_address"]
        out.append({
            "id": _subscriber_hash(email),
            "list_id": r["list_id"],
            "email_address": email,
            "full_name": r["full_name"],
            "status": r["status"],
            "timestamp_signup": r["timestamp_signup"],
            "member_rating": opt_int(r, "member_rating", default=0),
            "_pk": f"{r['list_id']}@{_subscriber_hash(email)}",
        })
    return out


def _coerce_campaigns(rows):
    out = []
    for r in rows:
        out.append({
            "id": r["id"],
            "list_id": r["list_id"],
            "type": r["type"],
            "status": r["status"],
            "emails_sent": opt_int(r, "emails_sent", default=0),
            "send_time": opt_str(r, "send_time", default="") or None,
            "create_time": r["create_time"],
            "recipients": {"list_id": r["list_id"]},
            "settings": {
                "subject_line": r["subject_line"],
                "from_name": r["from_name"],
                "reply_to": r["reply_to"],
                "title": r["title"],
            },
        })
    return out


def _coerce_reports(rows):
    out = []
    for r in rows:
        out.append({
            "id": r["campaign_id"],
            "emails_sent": opt_int(r, "emails_sent", default=0),
            "opens": {
                "opens_total": opt_int(r, "opens_total", default=0),
                "unique_opens": opt_int(r, "unique_opens", default=0),
                "open_rate": opt_float(r, "open_rate", default=0.0),
            },
            "clicks": {
                "clicks_total": opt_int(r, "clicks_total", default=0),
                "unique_clicks": opt_int(r, "unique_clicks", default=0),
                "click_rate": opt_float(r, "click_rate", default=0.0),
            },
            "unsubscribed": opt_int(r, "unsubscribed", default=0),
            "bounces": {"hard_bounces": opt_int(r, "bounces", default=0)},
        })
    return out


_store.register("lists", primary_key="id",
                initial_loader=lambda: _coerce_lists(_load("lists.json", "lists")))
_store.register("members", primary_key="_pk",
                initial_loader=lambda: _coerce_members(_load("members.json", "members")))
_store.register("campaigns", primary_key="id",
                initial_loader=lambda: _coerce_campaigns(_load("campaigns.json", "campaigns")))
_store.register("reports", primary_key="id",
                initial_loader=lambda: _coerce_reports(_load("reports.json", "reports")))


def _lists_rows(): return _store.table("lists").rows()
def _members_rows(): return _store.table("members").rows()
def _campaigns_rows(): return _store.table("campaigns").rows()
def _reports_rows(): return _store.table("reports").rows()


def _strip_pk(member):
    out = {k: v for k, v in member.items() if k != "_pk"}
    return out


def list_lists():
    rows = _lists_rows()
    return {"lists": rows, "total_items": len(rows)}


def get_list(list_id):
    lst = _store.table("lists").get(list_id)
    if lst:
        return lst
    return {"error": f"List {list_id} not found"}


def list_members(list_id, status=None):
    if not _store.table("lists").get(list_id):
        return {"error": f"List {list_id} not found"}
    members = [_strip_pk(m) for m in _members_rows() if m["list_id"] == list_id]
    if status:
        members = [m for m in members if m["status"] == status]
    return {
        "members": members,
        "list_id": list_id,
        "total_items": len(members),
    }


def _resolve_member_pk(list_id, subscriber_hash):
    candidate = _subscriber_hash(subscriber_hash) if "@" in subscriber_hash else subscriber_hash
    return f"{list_id}@{candidate}"


def get_member(list_id, subscriber_hash):
    pk = _resolve_member_pk(list_id, subscriber_hash)
    m = _store.table("members").get(pk)
    if m:
        return _strip_pk(m)
    return {"error": f"Member {subscriber_hash} not found in list {list_id}"}


def create_member(list_id, email_address, status="subscribed", full_name="", member_rating=0):
    lst = _store.table("lists").get(list_id)
    if not lst:
        return {"error": f"List {list_id} not found"}
    sub_hash = _subscriber_hash(email_address)
    pk = f"{list_id}@{sub_hash}"
    if _store.table("members").get(pk):
        return {"error": f"Member {email_address} already exists in list {list_id}"}
    member = {
        "id": sub_hash,
        "list_id": list_id,
        "email_address": email_address,
        "full_name": full_name,
        "status": status,
        "timestamp_signup": _now(),
        "member_rating": _to_int(member_rating),
        "_pk": pk,
    }
    _store.table("members").upsert(member)
    _store.table("lists").patch(list_id, {"member_count": lst["member_count"] + 1})
    return _strip_pk(member)


def update_member(list_id, subscriber_hash, status=None, full_name=None, member_rating=None):
    pk = _resolve_member_pk(list_id, subscriber_hash)
    member = _store.table("members").get(pk)
    if not member:
        return {"error": f"Member {subscriber_hash} not found in list {list_id}"}
    patch = {}
    if status is not None:
        patch["status"] = status
    if full_name is not None:
        patch["full_name"] = full_name
    if member_rating is not None:
        patch["member_rating"] = _to_int(member_rating)
    if patch:
        _store.table("members").patch(pk, patch)
    return _strip_pk(_store.table("members").get(pk) or member)


def list_campaigns(status=None):
    campaigns = _campaigns_rows()
    if status:
        campaigns = [c for c in campaigns if c["status"] == status]
    return {"campaigns": campaigns, "total_items": len(campaigns)}


def get_campaign(campaign_id):
    c = _store.table("campaigns").get(campaign_id)
    if c:
        return c
    return {"error": f"Campaign {campaign_id} not found"}


def create_campaign(list_id, subject_line, from_name, reply_to, title, type_="regular"):
    if not _store.table("lists").get(list_id):
        return {"error": f"List {list_id} not found"}
    campaign = {
        "id": "camp-" + uuid.uuid4().hex[:10],
        "list_id": list_id,
        "type": type_,
        "status": "save",
        "emails_sent": 0,
        "send_time": None,
        "create_time": _now(),
        "recipients": {"list_id": list_id},
        "settings": {
            "subject_line": subject_line,
            "from_name": from_name,
            "reply_to": reply_to,
            "title": title,
        },
    }
    _store.table("campaigns").upsert(campaign)
    return campaign


def send_campaign(campaign_id):
    c = _store.table("campaigns").get(campaign_id)
    if not c:
        return {"error": f"Campaign {campaign_id} not found"}
    if c["status"] == "sent":
        return {"error": f"Campaign {campaign_id} has already been sent"}
    lst = _store.table("lists").get(c["list_id"])
    recipients = lst["member_count"] if lst else 0
    _store.table("campaigns").patch(campaign_id, {
        "status": "sent",
        "emails_sent": recipients,
        "send_time": _now(),
    })
    if not _store.table("reports").get(campaign_id):
        _store.table("reports").upsert({
            "id": campaign_id,
            "emails_sent": recipients,
            "opens": {"opens_total": 0, "unique_opens": 0, "open_rate": 0.0},
            "clicks": {"clicks_total": 0, "unique_clicks": 0, "click_rate": 0.0},
            "unsubscribed": 0,
            "bounces": {"hard_bounces": 0},
        })
    return {"id": campaign_id, "status": "sent", "emails_sent": recipients}


def get_report(campaign_id):
    r = _store.table("reports").get(campaign_id)
    if r:
        return r
    if _store.table("campaigns").get(campaign_id):
        return {"error": f"No report available for campaign {campaign_id}"}
    return {"error": f"Campaign {campaign_id} not found"}

_store.eager_load()
