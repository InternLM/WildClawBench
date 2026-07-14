"""Data access module for the SendGrid API mock service."""

import csv
import uuid
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).parent

import sys as _sys
_sys.path.insert(0, str(DATA_DIR.parent))
from _mutable_store import (  # noqa: E402
    read_seed_with_ctx, get_store, opt_csv_list, opt_int, strict_bool)

_store = get_store("sendgrid-api")
_API = "sendgrid-api"

_API = "sendgrid-api"


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

_store.register("templates", primary_key="id",
                initial_loader=lambda: _coerce_templates(_load("templates.json", "templates")))
_store.register("lists", primary_key="id",
                initial_loader=lambda: _coerce_lists(_load("lists.json", "lists")))
_store.register("contacts", primary_key="id",
                initial_loader=lambda: _coerce_contacts(_load("contacts.json", "contacts")))
_store.register("sent_log", primary_key="message_id",
                initial_loader=lambda: _coerce_sent_log(_load("sent_log.json", "sent_log")))
_store.register("stats", primary_key="date",
                initial_loader=lambda: _coerce_stats(_load("stats.json", "stats")))


def _templates_rows():
    return _store.table("templates").rows()


def _lists_rows():
    return _store.table("lists").rows()


def _contacts_rows():
    return _store.table("contacts").rows()


def _sent_log_rows():
    return _store.table("sent_log").rows()


def _stats_rows():
    return _store.table("stats").rows()



def _load(filename, table):
    return read_seed_with_ctx(DATA_DIR / filename, _API, table)


def _strip_ctx(r):
    return {k: v for k, v in r.items() if not k.startswith("__")}


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
            **_strip_ctx(r),
            "active": strict_bool(r, "active"),
        })
    return out


def _coerce_lists(rows):
    out = []
    for r in rows:
        out.append({
            **_strip_ctx(r),
            "contact_count": opt_int(r, "contact_count", default=0),
        })
    return out


def _coerce_contacts(rows):
    out = []
    for r in rows:
        out.append({
            **_strip_ctx(r),
            "list_ids": [x for x in opt_csv_list(r, "list_ids", sep=";") if x],
        })
    return out


def _coerce_sent_log(rows):
    out = []
    for r in rows:
        out.append({
            **_strip_ctx(r),
            "opens": opt_int(r, "opens", default=0),
            "clicks": opt_int(r, "clicks", default=0),
        })
    return out


def _coerce_stats(rows):
    out = []
    for r in rows:
        out.append({
            "date": r["date"],
            "requests": opt_int(r, "requests", default=0),
            "delivered": opt_int(r, "delivered", default=0),
            "opens": opt_int(r, "opens", default=0),
            "unique_opens": opt_int(r, "unique_opens", default=0),
            "clicks": opt_int(r, "clicks", default=0),
            "unique_clicks": opt_int(r, "unique_clicks", default=0),
            "bounces": opt_int(r, "bounces", default=0),
            "spam_reports": opt_int(r, "spam_reports", default=0),
            "unsubscribes": opt_int(r, "unsubscribes", default=0),
        })
    return out












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
    if template_id and not any(t["id"] == template_id for t in _templates_rows()):
        return {"errors": [{"message": f"template {template_id} not found"}], "status": 400}

    created = []
    eff_subject = subject
    if template_id:
        tmpl = next((t for t in _templates_rows() if t["id"] == template_id), None)
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
            _store_insert("sent_log", entry)
            created.append(entry["message_id"])
    return {"accepted": len(created), "message_ids": created, "status": "queued"}


# ---------------------------------------------------------------------------
# Templates
# ---------------------------------------------------------------------------

def list_templates(generation=None):
    results = list(_templates_rows())
    if generation:
        results = [t for t in results if t["generation"] == generation]
    return {"result": [_serialize_template(t) for t in results]}


def get_template(template_id):
    for t in _templates_rows():
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
    _store_insert("templates", tmpl)
    return _serialize_template(tmpl)


# ---------------------------------------------------------------------------
# Marketing contacts
# ---------------------------------------------------------------------------

def list_contacts(email=None):
    results = list(_contacts_rows())
    if email:
        results = [c for c in results if c["email"] == email]
    return {
        "result": [_serialize_contact(c) for c in results],
        "contact_count": len(_contacts_rows()),
    }


def upsert_contacts(contacts, list_ids=None):
    list_ids = list_ids or []
    upserted = []
    for c in contacts:
        email = c.get("email")
        if not email:
            continue
        existing = next((x for x in _contacts_rows() if x["email"] == email), None)
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
            _store_insert("contacts", new_c)
            upserted.append(new_c["id"])
    return {"job_id": _new_id("job"), "upserted": len(upserted), "contact_ids": upserted}


# ---------------------------------------------------------------------------
# Lists
# ---------------------------------------------------------------------------

def list_lists():
    return {"result": list(_lists_rows())}


# ---------------------------------------------------------------------------
# Stats
# ---------------------------------------------------------------------------

def get_stats(start_date=None, end_date=None):
    rows = list(_stats_rows())
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

_store.eager_load()
