"""Data access module for the Mailchimp Marketing API mock service.

Models email-marketing objects: lists (audiences), members, campaigns and
reports. A member's ``id`` is the Mailchimp ``subscriber_hash`` = MD5 of the
lowercased email address, so lookups accept either the hash or the raw email.
"""

import csv
import hashlib
import uuid
from copy import deepcopy
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).parent


def _load(filename):
    with open(DATA_DIR / filename, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


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


# ---------------------------------------------------------------------------
# Load + coerce
# ---------------------------------------------------------------------------

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
            "member_count": _to_int(r["member_count"]),
            "unsubscribe_count": _to_int(r["unsubscribe_count"]),
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
            "member_rating": _to_int(r["member_rating"]),
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
            "emails_sent": _to_int(r["emails_sent"]),
            "send_time": r["send_time"] or None,
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
    out = {}
    for r in rows:
        out[r["campaign_id"]] = {
            "id": r["campaign_id"],
            "emails_sent": _to_int(r["emails_sent"]),
            "opens": {
                "opens_total": _to_int(r["opens_total"]),
                "unique_opens": _to_int(r["unique_opens"]),
                "open_rate": _to_float(r["open_rate"]),
            },
            "clicks": {
                "clicks_total": _to_int(r["clicks_total"]),
                "unique_clicks": _to_int(r["unique_clicks"]),
                "click_rate": _to_float(r["click_rate"]),
            },
            "unsubscribed": _to_int(r["unsubscribed"]),
            "bounces": {"hard_bounces": _to_int(r["bounces"])},
        }
    return out


_lists_store = deepcopy(_coerce_lists(_load("lists.csv")))
_members_store = deepcopy(_coerce_members(_load("members.csv")))
_campaigns_store = deepcopy(_coerce_campaigns(_load("campaigns.csv")))
_reports_store = deepcopy(_coerce_reports(_load("reports.csv")))


# ---------------------------------------------------------------------------
# Lists / audiences
# ---------------------------------------------------------------------------

def list_lists():
    return {"lists": deepcopy(_lists_store), "total_items": len(_lists_store)}


def get_list(list_id):
    for lst in _lists_store:
        if lst["id"] == list_id:
            return deepcopy(lst)
    return {"error": f"List {list_id} not found"}


# ---------------------------------------------------------------------------
# Members
# ---------------------------------------------------------------------------

def list_members(list_id, status=None):
    if not any(lst["id"] == list_id for lst in _lists_store):
        return {"error": f"List {list_id} not found"}
    members = [m for m in _members_store if m["list_id"] == list_id]
    if status:
        members = [m for m in members if m["status"] == status]
    return {
        "members": deepcopy(members),
        "list_id": list_id,
        "total_items": len(members),
    }


def _resolve_member(list_id, subscriber_hash):
    # subscriber_hash may be the md5 hash or the raw email address.
    candidate = _subscriber_hash(subscriber_hash) if "@" in subscriber_hash else subscriber_hash
    for m in _members_store:
        if m["list_id"] == list_id and m["id"] == candidate:
            return m
    return None


def get_member(list_id, subscriber_hash):
    member = _resolve_member(list_id, subscriber_hash)
    if member:
        return deepcopy(member)
    return {"error": f"Member {subscriber_hash} not found in list {list_id}"}


def create_member(list_id, email_address, status="subscribed", full_name="", member_rating=0):
    lst = next((l for l in _lists_store if l["id"] == list_id), None)
    if not lst:
        return {"error": f"List {list_id} not found"}
    sub_hash = _subscriber_hash(email_address)
    existing = next((m for m in _members_store if m["list_id"] == list_id and m["id"] == sub_hash), None)
    if existing:
        return {"error": f"Member {email_address} already exists in list {list_id}"}
    member = {
        "id": sub_hash,
        "list_id": list_id,
        "email_address": email_address,
        "full_name": full_name,
        "status": status,
        "timestamp_signup": _now(),
        "member_rating": _to_int(member_rating),
    }
    _members_store.append(member)
    lst["member_count"] += 1
    return deepcopy(member)


def update_member(list_id, subscriber_hash, status=None, full_name=None, member_rating=None):
    member = _resolve_member(list_id, subscriber_hash)
    if not member:
        return {"error": f"Member {subscriber_hash} not found in list {list_id}"}
    if status is not None:
        member["status"] = status
    if full_name is not None:
        member["full_name"] = full_name
    if member_rating is not None:
        member["member_rating"] = _to_int(member_rating)
    return deepcopy(member)


# ---------------------------------------------------------------------------
# Campaigns
# ---------------------------------------------------------------------------

def list_campaigns(status=None):
    campaigns = list(_campaigns_store)
    if status:
        campaigns = [c for c in campaigns if c["status"] == status]
    return {"campaigns": deepcopy(campaigns), "total_items": len(campaigns)}


def get_campaign(campaign_id):
    for c in _campaigns_store:
        if c["id"] == campaign_id:
            return deepcopy(c)
    return {"error": f"Campaign {campaign_id} not found"}


def create_campaign(list_id, subject_line, from_name, reply_to, title, type_="regular"):
    if not any(l["id"] == list_id for l in _lists_store):
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
    _campaigns_store.append(campaign)
    return deepcopy(campaign)


def send_campaign(campaign_id):
    for c in _campaigns_store:
        if c["id"] == campaign_id:
            if c["status"] == "sent":
                return {"error": f"Campaign {campaign_id} has already been sent"}
            lst = next((l for l in _lists_store if l["id"] == c["list_id"]), None)
            recipients = lst["member_count"] if lst else 0
            c["status"] = "sent"
            c["emails_sent"] = recipients
            c["send_time"] = _now()
            _reports_store.setdefault(campaign_id, {
                "id": campaign_id,
                "emails_sent": recipients,
                "opens": {"opens_total": 0, "unique_opens": 0, "open_rate": 0.0},
                "clicks": {"clicks_total": 0, "unique_clicks": 0, "click_rate": 0.0},
                "unsubscribed": 0,
                "bounces": {"hard_bounces": 0},
            })
            return {"id": campaign_id, "status": "sent", "emails_sent": recipients}
    return {"error": f"Campaign {campaign_id} not found"}


# ---------------------------------------------------------------------------
# Reports
# ---------------------------------------------------------------------------

def get_report(campaign_id):
    if campaign_id in _reports_store:
        return deepcopy(_reports_store[campaign_id])
    if any(c["id"] == campaign_id for c in _campaigns_store):
        return {"error": f"No report available for campaign {campaign_id}"}
    return {"error": f"Campaign {campaign_id} not found"}
