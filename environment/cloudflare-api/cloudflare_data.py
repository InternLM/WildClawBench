"""Data access module for the Cloudflare API mock service."""

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
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000000Z")


def _to_bool(v):
    return str(v).strip().lower() == "true"


# ---------------------------------------------------------------------------
# Load + coerce
# ---------------------------------------------------------------------------

def _coerce_zones(rows):
    out = []
    for r in rows:
        out.append({
            **r,
            "paused": _to_bool(r["paused"]),
            "development_mode": int(r["development_mode"]),
        })
    return out


def _coerce_dns(rows):
    out = []
    for r in rows:
        out.append({
            **r,
            "ttl": int(r["ttl"]),
            "proxied": _to_bool(r["proxied"]),
            "priority": int(r["priority"]),
        })
    return out


def _coerce_firewall(rows):
    out = []
    for r in rows:
        out.append({
            **r,
            "paused": _to_bool(r["paused"]),
            "priority": int(r["priority"]),
        })
    return out


def _coerce_page_rules(rows):
    return [{**r, "priority": int(r["priority"])} for r in rows]


_zones = _coerce_zones(_load("zones.csv"))
_dns = _coerce_dns(_load("dns_records.csv"))
_firewall = _coerce_firewall(_load("firewall_rules.csv"))
_page_rules = _coerce_page_rules(_load("page_rules.csv"))

_zones_store = deepcopy(_zones)
_dns_store = deepcopy(_dns)
_firewall_store = deepcopy(_firewall)
_page_rules_store = deepcopy(_page_rules)


# ---------------------------------------------------------------------------
# Envelope helpers
# ---------------------------------------------------------------------------

def _ok(result):
    return {"success": True, "errors": [], "messages": [], "result": result}


def _err(message, code=1003, status=404):
    return {
        "success": False,
        "errors": [{"code": code, "message": message}],
        "messages": [],
        "result": None,
        "_status": status,
    }


def _new_id():
    return uuid.uuid4().hex + uuid.uuid4().hex[:8]


def _zone_exists(zone_id):
    return any(z["id"] == zone_id for z in _zones_store)


def _serialize_zone(z):
    return {
        "id": z["id"],
        "name": z["name"],
        "status": z["status"],
        "paused": z["paused"],
        "type": z["type"],
        "development_mode": z["development_mode"],
        "plan": {"name": z["plan"]},
        "created_on": z["created_on"],
        "modified_on": z["modified_on"],
    }


def _serialize_dns(r):
    return {
        "id": r["id"],
        "zone_id": r["zone_id"],
        "type": r["type"],
        "name": r["name"],
        "content": r["content"],
        "ttl": r["ttl"],
        "proxied": r["proxied"],
        "priority": r["priority"],
        "created_on": r["created_on"],
        "modified_on": r["modified_on"],
    }


def _serialize_firewall(r):
    return {
        "id": r["id"],
        "description": r["description"],
        "action": r["action"],
        "filter": {"expression": r["expression"]},
        "paused": r["paused"],
        "priority": r["priority"],
        "created_on": r["created_on"],
    }


# ---------------------------------------------------------------------------
# Zones
# ---------------------------------------------------------------------------

def list_zones(name=None, status=None):
    results = list(_zones_store)
    if name:
        results = [z for z in results if z["name"] == name]
    if status:
        results = [z for z in results if z["status"] == status]
    return _ok([_serialize_zone(z) for z in results])


def get_zone(zone_id):
    for z in _zones_store:
        if z["id"] == zone_id:
            return _ok(_serialize_zone(z))
    return _err(f"Zone {zone_id} not found", code=1003, status=404)


# ---------------------------------------------------------------------------
# DNS records
# ---------------------------------------------------------------------------

def list_dns_records(zone_id, type=None, name=None):
    if not _zone_exists(zone_id):
        return _err(f"Zone {zone_id} not found", code=1003, status=404)
    results = [r for r in _dns_store if r["zone_id"] == zone_id]
    if type:
        results = [r for r in results if r["type"] == type]
    if name:
        results = [r for r in results if r["name"] == name]
    return _ok([_serialize_dns(r) for r in results])


def get_dns_record(zone_id, record_id):
    if not _zone_exists(zone_id):
        return _err(f"Zone {zone_id} not found", code=1003, status=404)
    for r in _dns_store:
        if r["zone_id"] == zone_id and r["id"] == record_id:
            return _ok(_serialize_dns(r))
    return _err(f"DNS record {record_id} not found", code=81044, status=404)


def create_dns_record(zone_id, type, name, content, ttl=1, proxied=False, priority=0):
    if not _zone_exists(zone_id):
        return _err(f"Zone {zone_id} not found", code=1003, status=404)
    record = {
        "id": _new_id(),
        "zone_id": zone_id,
        "type": type,
        "name": name,
        "content": content,
        "ttl": ttl,
        "proxied": proxied,
        "priority": priority,
        "created_on": _now(),
        "modified_on": _now(),
    }
    _dns_store.append(record)
    return _ok(_serialize_dns(record))


def update_dns_record(zone_id, record_id, type=None, name=None, content=None,
                      ttl=None, proxied=None, priority=None):
    if not _zone_exists(zone_id):
        return _err(f"Zone {zone_id} not found", code=1003, status=404)
    for idx, r in enumerate(_dns_store):
        if r["zone_id"] == zone_id and r["id"] == record_id:
            if type is not None:
                _dns_store[idx]["type"] = type
            if name is not None:
                _dns_store[idx]["name"] = name
            if content is not None:
                _dns_store[idx]["content"] = content
            if ttl is not None:
                _dns_store[idx]["ttl"] = ttl
            if proxied is not None:
                _dns_store[idx]["proxied"] = proxied
            if priority is not None:
                _dns_store[idx]["priority"] = priority
            _dns_store[idx]["modified_on"] = _now()
            return _ok(_serialize_dns(_dns_store[idx]))
    return _err(f"DNS record {record_id} not found", code=81044, status=404)


def delete_dns_record(zone_id, record_id):
    if not _zone_exists(zone_id):
        return _err(f"Zone {zone_id} not found", code=1003, status=404)
    for idx, r in enumerate(_dns_store):
        if r["zone_id"] == zone_id and r["id"] == record_id:
            _dns_store.pop(idx)
            return _ok({"id": record_id})
    return _err(f"DNS record {record_id} not found", code=81044, status=404)


# ---------------------------------------------------------------------------
# Firewall rules
# ---------------------------------------------------------------------------

def list_firewall_rules(zone_id):
    if not _zone_exists(zone_id):
        return _err(f"Zone {zone_id} not found", code=1003, status=404)
    results = [r for r in _firewall_store if r["zone_id"] == zone_id]
    results.sort(key=lambda r: r["priority"])
    return _ok([_serialize_firewall(r) for r in results])
