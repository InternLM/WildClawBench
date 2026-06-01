"""Data access module for the SendGrid API mock service."""

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
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


def _to_bool(v):
    return str(v).strip().lower() == "true"


def _to_int(v):
    try:
        return int(v)
    except (TypeError, ValueError):
        return 0


# ---------------------------------------------------------------------------
# Load + coerce
# ---------------------------------------------------------------------------

def _coerce_templates(rows):
    out = []
    for r in rows:
        out.append({
            **r,
            "active": _to_bool(r["active"]),
        })
    return out


def _coerce_lists(rows):
    out = []
    for r in rows:
        out.append({
            **r,
            "contact_count": _to_int(r["contact_count"]),
        })
    return out


def _coerce_contacts(rows):
    out = []
    for r in rows:
        out.append({
            **r,
            "list_ids": [x for x in r["list_ids"].split(";") if x],
        })
    return out


def _coerce_sent_log(rows):
    out = []
    for r in rows:
        out.append({
            **r,
            "opens": _to_int(r["opens"]),
            "clicks": _to_int(r["clicks"]),
        })
    return out


def _coerce_stats(rows):
    out = []
    for r in rows:
        out.append({
            "date": r["date"],
            "requests": _to_int(r["requests"]),
            "delivered": _to_int(r["delivered"]),
            "opens": _to_int(r["opens"]),
            "unique_opens": _to_int(r["unique_opens"]),
            "clicks": _to_int(r["clicks"]),
            "unique_clicks": _to_int(r["unique_clicks"]),
            "bounces": _to_int(r["bounces"]),
            "spam_reports": _to_int(r["spam_reports"]),
            "unsubscribes": _to_int(r["unsubscribes"]),
        })
    return out


_templates = _coerce_templates(_load("templates.csv"))
_lists = _coerce_lists(_load("lists.csv"))
_contacts = _coerce_contacts(_load("contacts.csv"))
_sent_log = _coerce_sent_log(_load("sent_log.csv"))
_stats = _coerce_stats(_load("stats.csv"))

_templates_store = deepcopy(_templates)
_lists_store = deepcopy(_lists)
_contacts_store = deepcopy(_contacts)
_sent_log_store = deepcopy(_sent_log)
_stats_store = deepcopy(_stats)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _new_id(prefix):
    return f"{prefix}-{uuid.uuid4().hex[:12]}"


def _serialize_template(t):
    return {
        "id": t["id"],
        "name": t["name"],
        "generation": t["generation"],
        "updated_at": t["updated_at"],
        "versions": [{
            "subject": t["subject"],
            "html_content": t["html_content"],
            "active": 1 if t["active"] else 0,
        }],
    }


def _serialize_contact(c):
    return {
        "id": c["id"],
        "email": c["email"],
        "first_name": c["first_name"],
        "last_name": c["last_name"],
        "country": c["country"],
        "list_ids": c["list_ids"],
        "created_at": c["created_at"],
        "updated_at": c["updated_at"],
    }


# ---------------------------------------------------------------------------
# Mail send
# ---------------------------------------------------------------------------

def send_mail(personalizations, from_email, subject=None, content=None, template_id=None):
    if not personalizations:
        return {"errors": [{"message": "personalizations is required"}], "status": 400}
    if not from_email:
        return {"errors": [{"message": "from.email is required"}], "status": 400}
    if template_id and not any(t["id"] == template_id for t in _templates_store):
        return {"errors": [{"message": f"template {template_id} not found"}], "status": 400}

    created = []
    eff_subject = subject
    if template_id:
        tmpl = next((t for t in _templates_store if t["id"] == template_id), None)
        if tmpl and not eff_subject:
            eff_subject = tmpl["subject"]
    for p in personalizations:
        for to in p.get("to", []):
            entry = {
                "message_id": _new_id("msg"),
                "to_email": to.get("email"),
                "from_email": from_email,
                "subject": eff_subject or p.get("subject") or "",
                "template_id": template_id or "",
                "status": "queued",
                "opens": 0,
                "clicks": 0,
                "sent_at": _now(),
            }
            _sent_log_store.append(entry)
            created.append(entry["message_id"])
    return {"accepted": len(created), "message_ids": created, "status": "queued"}


# ---------------------------------------------------------------------------
# Templates
# ---------------------------------------------------------------------------

def list_templates(generation=None):
    results = list(_templates_store)
    if generation:
        results = [t for t in results if t["generation"] == generation]
    return {"result": [_serialize_template(t) for t in results]}


def get_template(template_id):
    for t in _templates_store:
        if t["id"] == template_id:
            return _serialize_template(t)
    return {"error": f"Template {template_id} not found"}


def create_template(name, generation="dynamic", subject="", html_content=""):
    tmpl = {
        "id": _new_id("d"),
        "name": name,
        "generation": generation,
        "subject": subject,
        "html_content": html_content,
        "active": True,
        "updated_at": _now(),
    }
    _templates_store.append(tmpl)
    return _serialize_template(tmpl)


# ---------------------------------------------------------------------------
# Marketing contacts
# ---------------------------------------------------------------------------

def list_contacts(email=None):
    results = list(_contacts_store)
    if email:
        results = [c for c in results if c["email"] == email]
    return {
        "result": [_serialize_contact(c) for c in results],
        "contact_count": len(_contacts_store),
    }


def upsert_contacts(contacts, list_ids=None):
    list_ids = list_ids or []
    upserted = []
    for c in contacts:
        email = c.get("email")
        if not email:
            continue
        existing = next((x for x in _contacts_store if x["email"] == email), None)
        if existing:
            existing["first_name"] = c.get("first_name", existing["first_name"])
            existing["last_name"] = c.get("last_name", existing["last_name"])
            existing["country"] = c.get("country", existing["country"])
            for lid in list_ids:
                if lid not in existing["list_ids"]:
                    existing["list_ids"].append(lid)
            existing["updated_at"] = _now()
            upserted.append(existing["id"])
        else:
            new_c = {
                "id": _new_id("contact"),
                "email": email,
                "first_name": c.get("first_name", ""),
                "last_name": c.get("last_name", ""),
                "country": c.get("country", ""),
                "list_ids": list(list_ids),
                "created_at": _now(),
                "updated_at": _now(),
            }
            _contacts_store.append(new_c)
            upserted.append(new_c["id"])
    return {"job_id": _new_id("job"), "upserted": len(upserted), "contact_ids": upserted}


# ---------------------------------------------------------------------------
# Lists
# ---------------------------------------------------------------------------

def list_lists():
    return {"result": list(_lists_store)}


# ---------------------------------------------------------------------------
# Stats
# ---------------------------------------------------------------------------

def get_stats(start_date=None, end_date=None):
    rows = list(_stats_store)
    if start_date:
        rows = [r for r in rows if r["date"] >= start_date]
    if end_date:
        rows = [r for r in rows if r["date"] <= end_date]
    out = []
    for r in rows:
        out.append({
            "date": r["date"],
            "stats": [{
                "metrics": {k: v for k, v in r.items() if k != "date"},
            }],
        })
    return out
