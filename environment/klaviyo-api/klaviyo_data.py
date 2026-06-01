"""Data access module for the Klaviyo marketing mock service.

Mirrors a subset of the Klaviyo API (JSON:API style): profiles, lists, and
campaigns. Responses use the JSON:API envelope, e.g.
{"data": [{"type": "profile", "id": ..., "attributes": {...}}]}. Creating a
profile appends to an in-memory store that resets on restart.
"""

import csv
import secrets
import string
import time
from copy import deepcopy
from pathlib import Path

DATA_DIR = Path(__file__).parent


def _load(filename):
    with open(DATA_DIR / filename, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _to_int(v):
    try:
        return int(v)
    except (TypeError, ValueError):
        return 0


# ---------------------------------------------------------------------------
# Load + coerce
# ---------------------------------------------------------------------------

def _coerce_profiles(rows):
    out = []
    for r in rows:
        out.append({
            "id": r["id"],
            "email": r["email"],
            "phone_number": r["phone_number"],
            "first_name": r["first_name"],
            "last_name": r["last_name"],
            "organization": r["organization"],
            "title": r["title"],
            "city": r["city"],
            "region": r["region"],
            "country": r["country"],
            "created": r["created"],
            "updated": r["updated"],
        })
    return out


def _coerce_lists(rows):
    out = []
    for r in rows:
        out.append({
            "id": r["id"],
            "name": r["name"],
            "profile_count": _to_int(r["profile_count"]),
            "created": r["created"],
            "updated": r["updated"],
        })
    return out


def _coerce_campaigns(rows):
    out = []
    for r in rows:
        out.append({
            "id": r["id"],
            "name": r["name"],
            "status": r["status"],
            "channel": r["channel"],
            "subject": r["subject"],
            "from_email": r["from_email"],
            "from_label": r["from_label"],
            "list_id": r["list_id"],
            "send_time": r["send_time"] or None,
            "created": r["created"],
            "updated": r["updated"],
        })
    return out


_profiles = _coerce_profiles(_load("profiles.csv"))
_lists = _coerce_lists(_load("lists.csv"))
_campaigns = _coerce_campaigns(_load("campaigns.csv"))

_profiles_store = deepcopy(_profiles)
_lists_store = deepcopy(_lists)
_campaigns_store = deepcopy(_campaigns)


# ---------------------------------------------------------------------------
# Serializers (JSON:API resource objects)
# ---------------------------------------------------------------------------

def _serialize_profile(p):
    return {
        "type": "profile",
        "id": p["id"],
        "attributes": {
            "email": p["email"],
            "phone_number": p["phone_number"],
            "first_name": p["first_name"],
            "last_name": p["last_name"],
            "organization": p["organization"],
            "title": p["title"],
            "location": {
                "city": p["city"],
                "region": p["region"],
                "country": p["country"],
            },
            "created": p["created"],
            "updated": p["updated"],
        },
    }


def _serialize_list(l):
    return {
        "type": "list",
        "id": l["id"],
        "attributes": {
            "name": l["name"],
            "profile_count": l["profile_count"],
            "created": l["created"],
            "updated": l["updated"],
        },
    }


def _serialize_campaign(c):
    return {
        "type": "campaign",
        "id": c["id"],
        "attributes": {
            "name": c["name"],
            "status": c["status"],
            "channel": c["channel"],
            "subject": c["subject"],
            "from_email": c["from_email"],
            "from_label": c["from_label"],
            "send_time": c["send_time"],
            "created": c["created"],
            "updated": c["updated"],
        },
        "relationships": {
            "list": {"data": {"type": "list", "id": c["list_id"]}}
        },
    }


# ---------------------------------------------------------------------------
# Profiles
# ---------------------------------------------------------------------------

def list_profiles(email=None):
    profiles = list(_profiles_store)
    if email:
        profiles = [p for p in profiles if p["email"].lower() == email.lower()]
    return {"data": [_serialize_profile(p) for p in profiles]}


def get_profile(profile_id):
    for p in _profiles_store:
        if p["id"] == profile_id:
            return {"data": _serialize_profile(p)}
    return {"error": "profile not found", "message": f"Profile {profile_id} not found"}


def _new_id():
    alphabet = string.ascii_uppercase + string.digits
    return "01HZPROF" + "".join(secrets.choice(alphabet) for _ in range(18))


def create_profile(email, first_name="", last_name="", phone_number="",
                   organization="", title="", city="", region="", country=""):
    if not email:
        return {"error": "invalid request", "message": "attributes.email is required"}
    if any(p["email"].lower() == email.lower() for p in _profiles_store):
        return {"error": "duplicate profile", "message": f"Profile with email {email} already exists"}
    now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    profile = {
        "id": _new_id(),
        "email": email,
        "phone_number": phone_number or "",
        "first_name": first_name or "",
        "last_name": last_name or "",
        "organization": organization or "",
        "title": title or "",
        "city": city or "",
        "region": region or "",
        "country": country or "",
        "created": now,
        "updated": now,
    }
    _profiles_store.append(profile)
    return {"data": _serialize_profile(profile)}


# ---------------------------------------------------------------------------
# Lists
# ---------------------------------------------------------------------------

def list_lists():
    return {"data": [_serialize_list(l) for l in _lists_store]}


# ---------------------------------------------------------------------------
# Campaigns
# ---------------------------------------------------------------------------

def list_campaigns(status=None, channel=None):
    campaigns = list(_campaigns_store)
    if status:
        campaigns = [c for c in campaigns if c["status"].lower() == status.lower()]
    if channel:
        campaigns = [c for c in campaigns if c["channel"].lower() == channel.lower()]
    return {"data": [_serialize_campaign(c) for c in campaigns]}
