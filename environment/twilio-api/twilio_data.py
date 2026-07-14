"""Data access module for the Twilio API mock service."""

import csv
import json
import uuid
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).parent

import sys as _sys
_sys.path.insert(0, str(DATA_DIR.parent))
from _mutable_store import (
    read_seed_with_ctx, get_store, opt_float, opt_int, opt_str, strict_bool, strict_int)

_store = get_store("twilio-api")
_API = "twilio-api"


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

_store.register("phone_numbers", primary_key="sid",
                initial_loader=lambda: _coerce_phone_numbers(_load("phone_numbers.json", "phone_numbers")))
_store.register("messages", primary_key="sid",
                initial_loader=lambda: _coerce_messages(_load("messages.json", "messages")))
_store.register("calls", primary_key="sid",
                initial_loader=lambda: _coerce_calls(_load("calls.json", "calls")))
_store.register_document("account", initial_loader=lambda: __import__('json').load(open(DATA_DIR / "account.json", encoding="utf-8")))


def _phone_numbers_rows():
    return _store.table("phone_numbers").rows()


def _messages_rows():
    return _store.table("messages").rows()


def _calls_rows():
    return _store.table("calls").rows()


def _account_doc():
    return _store.document("account").get()



def _load(filename, table):
    return read_seed_with_ctx(DATA_DIR / filename, _API, table)


def _strip_ctx(r):
    return {k: v for k, v in r.items() if not k.startswith("__")}


def _now():
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


def _to_bool(v):
    return str(v).strip().lower() == "true"


def _to_float(v):
    if v is None or str(v).strip() == "":
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


# ---------------------------------------------------------------------------
# Load + coerce
# ---------------------------------------------------------------------------

def _coerce_phone_numbers(rows):
    out = []
    for r in rows:
        out.append({
            **_strip_ctx(r),
            "sms_enabled": strict_bool(r, "sms_enabled"),
            "voice_enabled": strict_bool(r, "voice_enabled"),
            "mms_enabled": strict_bool(r, "mms_enabled"),
            "capabilities_fax": strict_bool(r, "capabilities_fax"),
        })
    return out


def _coerce_messages(rows):
    out = []
    for r in rows:
        out.append({
            **_strip_ctx(r),
            "num_segments": strict_int(r, "num_segments"),
            "price": opt_float(r, "price", default=None),
            "error_code": opt_int(r, "error_code", default=None),
            "date_sent": opt_str(r, "date_sent", default="") or None,
        })
    return out


def _coerce_calls(rows):
    out = []
    for r in rows:
        out.append({
            **_strip_ctx(r),
            "duration": strict_int(r, "duration"),
            "price": opt_float(r, "price", default=None),
            "answered_by": opt_str(r, "answered_by", default="") or None,
            "start_time": opt_str(r, "start_time", default="") or None,
            "end_time": opt_str(r, "end_time", default="") or None,
        })
    return out






# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _new_sid(prefix):
    return f"{prefix}{uuid.uuid4().hex}"


def _account_sid():
    return _account_doc()["sid"]


def _serialize_message(m):
    return {
        "sid": m["sid"],
        "account_sid": _account_sid(),
        "from": m["from_number"],
        "to": m["to_number"],
        "body": m["body"],
        "status": m["status"],
        "direction": m["direction"],
        "num_segments": str(m["num_segments"]),
        "price": str(m["price"]) if m["price"] is not None else None,
        "price_unit": m["price_unit"],
        "error_code": m["error_code"],
        "date_sent": m["date_sent"],
        "date_created": m["date_created"],
        "uri": f"/2010-04-01/Accounts/{_account_sid()}/Messages/{m['sid']}.json",
    }


def _serialize_call(c):
    return {
        "sid": c["sid"],
        "account_sid": _account_sid(),
        "from": c["from_number"],
        "to": c["to_number"],
        "status": c["status"],
        "direction": c["direction"],
        "duration": str(c["duration"]),
        "price": str(c["price"]) if c["price"] is not None else None,
        "price_unit": c["price_unit"],
        "answered_by": c["answered_by"],
        "start_time": c["start_time"],
        "end_time": c["end_time"],
        "date_created": c["date_created"],
        "uri": f"/2010-04-01/Accounts/{_account_sid()}/Calls/{c['sid']}.json",
    }


def _serialize_phone_number(p):
    return {
        "sid": p["sid"],
        "account_sid": _account_sid(),
        "phone_number": p["phone_number"],
        "friendly_name": p["friendly_name"],
        "iso_country": p["iso_country"],
        "capabilities": {
            "sms": p["sms_enabled"],
            "voice": p["voice_enabled"],
            "mms": p["mms_enabled"],
            "fax": p["capabilities_fax"],
        },
        "date_created": p["date_created"],
    }


# ---------------------------------------------------------------------------
# Messages
# ---------------------------------------------------------------------------

def list_messages(to=None, from_=None, status=None, page_size=50):
    results = list(_messages_rows())
    if to:
        results = [m for m in results if m["to_number"] == to]
    if from_:
        results = [m for m in results if m["from_number"] == from_]
    if status:
        results = [m for m in results if m["status"] == status]
    results.sort(key=lambda m: m["date_created"], reverse=True)
    results = results[:page_size]
    return {
        "messages": [_serialize_message(m) for m in results],
        "page": 0,
        "page_size": page_size,
        "uri": f"/2010-04-01/Accounts/{_account_sid()}/Messages.json",
    }


def get_message(sid):
    for m in _messages_rows():
        if m["sid"] == sid:
            return _serialize_message(m)
    return {"error": f"Message {sid} not found", "code": 20404, "status": 404}


def create_message(to, from_, body):
    if not to or not from_:
        return {"error": "Both 'To' and 'From' are required", "code": 21604, "status": 400}
    segments = max(1, (len(body) + 159) // 160) if body else 1
    msg = {
        "sid": _new_sid("SM"),
        "from_number": from_,
        "to_number": to,
        "body": body or "",
        "status": "queued",
        "direction": "outbound-api",
        "num_segments": segments,
        "price": None,
        "price_unit": "USD",
        "error_code": None,
        "date_sent": None,
        "date_created": _now(),
    }
    _store_insert("messages", msg)
    return _serialize_message(msg)


# ---------------------------------------------------------------------------
# Calls
# ---------------------------------------------------------------------------

def list_calls(to=None, from_=None, status=None, page_size=50):
    results = list(_calls_rows())
    if to:
        results = [c for c in results if c["to_number"] == to]
    if from_:
        results = [c for c in results if c["from_number"] == from_]
    if status:
        results = [c for c in results if c["status"] == status]
    results.sort(key=lambda c: c["date_created"], reverse=True)
    results = results[:page_size]
    return {
        "calls": [_serialize_call(c) for c in results],
        "page": 0,
        "page_size": page_size,
        "uri": f"/2010-04-01/Accounts/{_account_sid()}/Calls.json",
    }


def get_call(sid):
    for c in _calls_rows():
        if c["sid"] == sid:
            return _serialize_call(c)
    return {"error": f"Call {sid} not found", "code": 20404, "status": 404}


def create_call(to, from_):
    if not to or not from_:
        return {"error": "Both 'To' and 'From' are required", "code": 21604, "status": 400}
    call = {
        "sid": _new_sid("CA"),
        "from_number": from_,
        "to_number": to,
        "status": "queued",
        "direction": "outbound-api",
        "duration": 0,
        "price": None,
        "price_unit": "USD",
        "answered_by": None,
        "start_time": None,
        "end_time": None,
        "date_created": _now(),
    }
    _store_insert("calls", call)
    return _serialize_call(call)


# ---------------------------------------------------------------------------
# Incoming phone numbers
# ---------------------------------------------------------------------------

def list_phone_numbers(phone_number=None, page_size=50):
    results = list(_phone_numbers_rows())
    if phone_number:
        results = [p for p in results if p["phone_number"] == phone_number]
    results = results[:page_size]
    return {
        "incoming_phone_numbers": [_serialize_phone_number(p) for p in results],
        "page": 0,
        "page_size": page_size,
        "uri": f"/2010-04-01/Accounts/{_account_sid()}/IncomingPhoneNumbers.json",
    }


# ---------------------------------------------------------------------------
# Lookup
# ---------------------------------------------------------------------------

def lookup(phone_number):
    owned = next((p for p in _phone_numbers_rows() if p["phone_number"] == phone_number), None)
    country = owned["iso_country"] if owned else ("GB" if phone_number.startswith("+44") else "US")
    return {
        "phone_number": phone_number,
        "national_format": phone_number,
        "country_code": country,
        "valid": phone_number.startswith("+") and len(phone_number) >= 8,
        "caller_name": owned["friendly_name"] if owned else None,
        "url": f"/v1/PhoneNumbers/{phone_number}",
    }

_store.eager_load()
