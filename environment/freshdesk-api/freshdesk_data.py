"""Data access module for the Freshdesk API mock service.

Mirrors a subset of the Freshdesk v2 API: tickets (list/get/create/update),
contacts, and agents. Status is an int (2=open, 3=pending, 4=resolved,
5=closed) and priority is an int (1=low .. 4=urgent). Mutations are held in
process memory and reset on container restart.
"""

import csv
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path

DATA_DIR = Path(__file__).parent


def _load(filename):
    with open(DATA_DIR / filename, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _to_bool(v):
    return str(v).strip().lower() == "true"


def _to_int(v, default=None):
    try:
        return int(v)
    except (TypeError, ValueError):
        return default


# ---------------------------------------------------------------------------
# Load + coerce
# ---------------------------------------------------------------------------

def _coerce_tickets(rows):
    out = []
    for r in rows:
        out.append({
            "id": int(r["id"]),
            "subject": r["subject"],
            "description": r["description"],
            "status": int(r["status"]),
            "priority": int(r["priority"]),
            "requester_id": int(r["requester_id"]),
            "responder_id": _to_int(r["responder_id"]),
            "type": r["type"],
            "tags": [t for t in r["tags"].split(";") if t],
            "created_at": r["created_at"],
            "updated_at": r["updated_at"],
        })
    return out


def _coerce_contacts(rows):
    out = []
    for r in rows:
        out.append({
            "id": int(r["id"]),
            "name": r["name"],
            "email": r["email"],
            "phone": r["phone"],
            "company_id": _to_int(r["company_id"]),
            "active": _to_bool(r["active"]),
            "created_at": r["created_at"],
        })
    return out


def _coerce_agents(rows):
    out = []
    for r in rows:
        out.append({
            "id": int(r["id"]),
            "available": _to_bool(r["available"]),
            "ticket_scope": int(r["ticket_scope"]),
            "occasional": _to_bool(r["occasional"]),
            "created_at": r["created_at"],
            "contact": {
                "name": r["name"],
                "email": r["email"],
            },
        })
    return out


_tickets = _coerce_tickets(_load("tickets.csv"))
_contacts = _coerce_contacts(_load("contacts.csv"))
_agents = _coerce_agents(_load("agents.csv"))

_tickets_store = deepcopy(_tickets)
_contacts_store = deepcopy(_contacts)
_agents_store = deepcopy(_agents)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _next_ticket_id():
    return max((t["id"] for t in _tickets_store), default=70000) + 1


# ---------------------------------------------------------------------------
# Tickets
# ---------------------------------------------------------------------------

def list_tickets(status=None, priority=None, requester_id=None):
    tickets = list(_tickets_store)
    if status is not None:
        tickets = [t for t in tickets if t["status"] == int(status)]
    if priority is not None:
        tickets = [t for t in tickets if t["priority"] == int(priority)]
    if requester_id is not None:
        tickets = [t for t in tickets if t["requester_id"] == int(requester_id)]
    return tickets


def get_ticket(ticket_id):
    t = next((x for x in _tickets_store if x["id"] == int(ticket_id)), None)
    if not t:
        return {"error": "ticket not found", "message": f"Ticket {ticket_id} not found"}
    return t


def create_ticket(payload):
    now = _now_iso()
    ticket = {
        "id": _next_ticket_id(),
        "subject": payload.get("subject") or "",
        "description": payload.get("description") or "",
        "status": int(payload.get("status") or 2),
        "priority": int(payload.get("priority") or 1),
        "requester_id": _to_int(payload.get("requester_id")),
        "responder_id": _to_int(payload.get("responder_id")),
        "type": payload.get("type") or "Question",
        "tags": payload.get("tags") or [],
        "created_at": now,
        "updated_at": now,
    }
    _tickets_store.append(ticket)
    return ticket


def update_ticket(ticket_id, payload):
    for i, t in enumerate(_tickets_store):
        if t["id"] == int(ticket_id):
            for field in ("subject", "description", "type"):
                if field in payload and payload[field] is not None:
                    _tickets_store[i][field] = payload[field]
            for field in ("status", "priority", "responder_id", "requester_id"):
                if field in payload and payload[field] is not None:
                    _tickets_store[i][field] = int(payload[field])
            if "tags" in payload and payload["tags"] is not None:
                _tickets_store[i]["tags"] = payload["tags"]
            _tickets_store[i]["updated_at"] = _now_iso()
            return _tickets_store[i]
    return {"error": "ticket not found", "message": f"Ticket {ticket_id} not found"}


# ---------------------------------------------------------------------------
# Contacts + agents
# ---------------------------------------------------------------------------

def list_contacts():
    return list(_contacts_store)


def list_agents():
    return list(_agents_store)
