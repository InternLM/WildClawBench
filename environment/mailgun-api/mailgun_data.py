"""Data access module for the Mailgun API mock service.

Mirrors a subset of the Mailgun Email API (api.mailgun.net/v3): sending
messages, querying delivery events, total stats, and mailing-list members.
"""

import csv
import secrets
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path

DATA_DIR = Path(__file__).parent


def _load(filename):
    with open(DATA_DIR / filename, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _to_bool(v):
    return str(v).strip().lower() == "true"


# ---------------------------------------------------------------------------
# Load + coerce
# ---------------------------------------------------------------------------

def _coerce_messages(rows):
    out = []
    for r in rows:
        out.append({
            "id": r["id"],
            "domain": r["domain"],
            "sender": r["sender"],
            "recipient": r["recipient"],
            "subject": r["subject"],
            "body": r["body"],
            "timestamp": r["timestamp"],
        })
    return out


def _coerce_events(rows):
    out = []
    for r in rows:
        out.append({
            "id": r["id"],
            "domain": r["domain"],
            "message_id": r["message_id"],
            "event": r["event"],
            "recipient": r["recipient"],
            "timestamp": r["timestamp"],
            "reason": r["reason"] or None,
        })
    return out


def _coerce_members(rows):
    out = []
    for r in rows:
        out.append({
            "list_address": r["list_address"],
            "address": r["address"],
            "name": r["name"],
            "subscribed": _to_bool(r["subscribed"]),
            "vars": r["vars"],
        })
    return out


_messages = _coerce_messages(_load("messages.csv"))
_events = _coerce_events(_load("events.csv"))
_members = _coerce_members(_load("list_members.csv"))

_messages_store = deepcopy(_messages)
_events_store = deepcopy(_events)
_members_store = deepcopy(_members)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _new_message_id(domain):
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    return f"{stamp}.{secrets.token_hex(6).upper()}@{domain}"


# ---------------------------------------------------------------------------
# Messages (send)
# ---------------------------------------------------------------------------

def send_message(domain, sender, to, subject, text):
    if not sender or not to:
        return {"error": "from and to are required"}
    msg_id = _new_message_id(domain)
    message = {
        "id": msg_id,
        "domain": domain,
        "sender": sender,
        "recipient": to,
        "subject": subject or "",
        "body": text or "",
        "timestamp": _now_iso(),
    }
    _messages_store.append(message)
    _events_store.append({
        "id": f"ev_{secrets.token_hex(4)}",
        "domain": domain,
        "message_id": msg_id,
        "event": "accepted",
        "recipient": to,
        "timestamp": message["timestamp"],
        "reason": None,
    })
    return {"id": f"<{msg_id}>", "message": "Queued. Thank you."}


# ---------------------------------------------------------------------------
# Events
# ---------------------------------------------------------------------------

def get_events(domain, event=None, recipient=None, limit=300):
    items = [e for e in _events_store if e["domain"] == domain]
    if event:
        wanted = {x.strip().lower() for x in event.split(" OR ")}
        items = [e for e in items if e["event"].lower() in wanted]
    if recipient:
        items = [e for e in items if e["recipient"].lower() == recipient.lower()]
    items = sorted(items, key=lambda e: e["timestamp"], reverse=True)[:limit]
    out = []
    for e in items:
        item = {
            "id": e["id"],
            "event": e["event"],
            "timestamp": e["timestamp"],
            "recipient": e["recipient"],
            "message": {"headers": {"message-id": e["message_id"]}},
        }
        if e["reason"]:
            item["reason"] = e["reason"]
        out.append(item)
    return {"items": out, "paging": {"next": None, "previous": None}}


# ---------------------------------------------------------------------------
# Stats
# ---------------------------------------------------------------------------

def get_stats_total(domain, event=None):
    events_for_domain = [e for e in _events_store if e["domain"] == domain]
    wanted = ["accepted", "delivered", "failed", "opened", "clicked"]
    if event:
        wanted = [x.strip().lower() for x in event.split(",")]
    stats = []
    for name in wanted:
        count = sum(1 for e in events_for_domain if e["event"].lower() == name)
        stats.append({"time": _now_iso(), name: {"total": count}})
    return {
        "start": min((e["timestamp"] for e in events_for_domain), default=_now_iso()),
        "end": max((e["timestamp"] for e in events_for_domain), default=_now_iso()),
        "resolution": "month",
        "stats": stats,
    }


# ---------------------------------------------------------------------------
# Mailing list members
# ---------------------------------------------------------------------------

def list_members(address, subscribed=None):
    members = [m for m in _members_store if m["list_address"].lower() == (address or "").lower()]
    if not members and not any(m["list_address"].lower() == (address or "").lower() for m in _members_store):
        # empty list is valid in Mailgun; only error if address itself unknown
        if address not in {m["list_address"] for m in _members_store}:
            return {"error": f"mailing list {address} not found"}
    if subscribed is not None:
        members = [m for m in members if m["subscribed"] == subscribed]
    items = []
    for m in members:
        items.append({
            "address": m["address"],
            "name": m["name"],
            "subscribed": m["subscribed"],
            "vars": m["vars"],
        })
    return {"items": items, "total_count": len(items)}
