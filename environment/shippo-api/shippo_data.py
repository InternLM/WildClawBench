"""Data access module for the Shippo API mock service."""

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


# ---------------------------------------------------------------------------
# Load + coerce
# ---------------------------------------------------------------------------

def _coerce_addresses(rows):
    out = []
    for r in rows:
        out.append({
            **r,
            "is_residential": _to_bool(r["is_residential"]),
            "validated": _to_bool(r["validated"]),
        })
    return out


def _coerce_parcels(rows):
    out = []
    for r in rows:
        out.append({
            **r,
            "length": float(r["length"]),
            "width": float(r["width"]),
            "height": float(r["height"]),
            "weight": float(r["weight"]),
            "template": r["template"] or None,
        })
    return out


def _coerce_shipments(rows):
    return [{**r} for r in rows]


def _coerce_rates(rows):
    out = []
    for r in rows:
        out.append({
            **r,
            "amount": float(r["amount"]),
            "estimated_days": int(r["estimated_days"]),
        })
    return out


def _coerce_transactions(rows):
    return [{**r} for r in rows]


def _coerce_tracking(rows):
    return [{**r} for r in rows]


_addresses = _coerce_addresses(_load("addresses.csv"))
_parcels = _coerce_parcels(_load("parcels.csv"))
_shipments = _coerce_shipments(_load("shipments.csv"))
_rates = _coerce_rates(_load("rates.csv"))
_transactions = _coerce_transactions(_load("transactions.csv"))
_tracking = _coerce_tracking(_load("tracking.csv"))

_addresses_store = deepcopy(_addresses)
_parcels_store = deepcopy(_parcels)
_shipments_store = deepcopy(_shipments)
_rates_store = deepcopy(_rates)
_transactions_store = deepcopy(_transactions)
_tracking_store = deepcopy(_tracking)


def _new_id(prefix):
    return f"{prefix}-{uuid.uuid4().hex[:12]}"


# ---------------------------------------------------------------------------
# Serializers
# ---------------------------------------------------------------------------

def _address_obj(a):
    return dict(a)


def _rate_obj(r):
    return {
        "object_id": r["object_id"],
        "shipment": r["shipment"],
        "provider": r["provider"],
        "servicelevel": {"token": r["servicelevel_token"], "name": r["servicelevel_name"]},
        "amount": r["amount"],
        "currency": r["currency"],
        "estimated_days": r["estimated_days"],
    }


def _shipment_obj(s):
    rates = [_rate_obj(r) for r in _rates_store if r["shipment"] == s["object_id"]]
    return {
        "object_id": s["object_id"],
        "status": s["status"],
        "object_created": s["created_time"],
        "address_from": _find_address(s["address_from"]),
        "address_to": _find_address(s["address_to"]),
        "parcels": [_parcel_obj(p) for p in _parcels_store if p["object_id"] == s["parcel"]],
        "rates": rates,
    }


def _parcel_obj(p):
    return dict(p)


def _find_address(object_id):
    for a in _addresses_store:
        if a["object_id"] == object_id:
            return _address_obj(a)
    return None


# ---------------------------------------------------------------------------
# Addresses
# ---------------------------------------------------------------------------

def create_address(payload):
    addr = {
        "object_id": _new_id("addr"),
        "name": payload.get("name", ""),
        "company": payload.get("company", ""),
        "street1": payload.get("street1", ""),
        "street2": payload.get("street2", ""),
        "city": payload.get("city", ""),
        "state": payload.get("state", ""),
        "zip": payload.get("zip", ""),
        "country": payload.get("country", "US"),
        "phone": payload.get("phone", ""),
        "email": payload.get("email", ""),
        "is_residential": bool(payload.get("is_residential", False)),
        "validated": True,
    }
    _addresses_store.append(addr)
    return _address_obj(addr)


def get_address(object_id):
    addr = _find_address(object_id)
    if addr is None:
        return {"error": f"address {object_id} not found"}
    return addr


# ---------------------------------------------------------------------------
# Shipments + rates
# ---------------------------------------------------------------------------

_DEFAULT_RATE_TEMPLATES = [
    ("USPS", "usps_priority", "Priority Mail", 9.10, 2),
    ("UPS", "ups_ground", "UPS Ground", 12.45, 3),
    ("FedEx", "fedex_2day", "FedEx 2Day", 19.20, 2),
]


def create_shipment(payload):
    addr_from = payload.get("address_from")
    addr_to = payload.get("address_to")
    parcel = payload.get("parcels")
    if isinstance(parcel, list):
        parcel = parcel[0] if parcel else None

    # Accept either an existing address object_id or an inline address dict.
    if isinstance(addr_from, dict):
        addr_from = create_address(addr_from)["object_id"]
    if isinstance(addr_to, dict):
        addr_to = create_address(addr_to)["object_id"]
    if isinstance(parcel, dict):
        parcel = create_parcel(parcel)["object_id"]

    if not _find_address(addr_from):
        return {"error": f"address_from {addr_from} not found"}
    if not _find_address(addr_to):
        return {"error": f"address_to {addr_to} not found"}

    shipment = {
        "object_id": _new_id("ship"),
        "address_from": addr_from,
        "address_to": addr_to,
        "parcel": parcel or "",
        "status": "SUCCESS",
        "created_time": _now(),
    }
    _shipments_store.append(shipment)
    # Generate rates across carriers for the new shipment.
    for provider, token, name, amount, days in _DEFAULT_RATE_TEMPLATES:
        _rates_store.append({
            "object_id": _new_id("rate"),
            "shipment": shipment["object_id"],
            "provider": provider,
            "servicelevel_token": token,
            "servicelevel_name": name,
            "amount": amount,
            "currency": "USD",
            "estimated_days": days,
        })
    return _shipment_obj(shipment)


def create_parcel(payload):
    parcel = {
        "object_id": _new_id("parcel"),
        "length": float(payload.get("length", 1)),
        "width": float(payload.get("width", 1)),
        "height": float(payload.get("height", 1)),
        "distance_unit": payload.get("distance_unit", "in"),
        "weight": float(payload.get("weight", 1)),
        "mass_unit": payload.get("mass_unit", "lb"),
        "template": payload.get("template") or None,
    }
    _parcels_store.append(parcel)
    return _parcel_obj(parcel)


def get_shipment(object_id):
    for s in _shipments_store:
        if s["object_id"] == object_id:
            return _shipment_obj(s)
    return {"error": f"shipment {object_id} not found"}


def list_shipment_rates(object_id):
    if not any(s["object_id"] == object_id for s in _shipments_store):
        return {"error": f"shipment {object_id} not found"}
    rates = [_rate_obj(r) for r in _rates_store if r["shipment"] == object_id]
    return {"count": len(rates), "results": rates}


# ---------------------------------------------------------------------------
# Transactions (buy a label)
# ---------------------------------------------------------------------------

def _gen_tracking_number(provider):
    digits = uuid.uuid4().int % (10 ** 18)
    if provider == "USPS":
        return f"9400{digits:018d}"[:22]
    if provider == "UPS":
        return f"1Z999AA1{digits:010d}"[:18]
    return f"{digits:012d}"[:12]


def create_transaction(payload):
    rate_id = payload.get("rate")
    rate = next((r for r in _rates_store if r["object_id"] == rate_id), None)
    if rate is None:
        return {"error": f"rate {rate_id} not found"}
    tracking_number = _gen_tracking_number(rate["provider"])
    txn = {
        "object_id": _new_id("txn"),
        "rate": rate_id,
        "shipment": rate["shipment"],
        "status": "SUCCESS",
        "tracking_number": tracking_number,
        "tracking_status": "PRE_TRANSIT",
        "carrier": rate["provider"],
        "label_url": f"https://shippo-delivery.s3.amazonaws.com/labels/{tracking_number}.pdf",
        "created_time": _now(),
    }
    _transactions_store.append(txn)
    _tracking_store.append({
        "carrier": rate["provider"],
        "tracking_number": tracking_number,
        "status": "PRE_TRANSIT",
        "status_detail": "Shipping label created",
        "location_city": "",
        "location_state": "",
        "status_time": txn["created_time"],
    })
    return dict(txn)


def get_transaction(object_id):
    for t in _transactions_store:
        if t["object_id"] == object_id:
            return dict(t)
    return {"error": f"transaction {object_id} not found"}


# ---------------------------------------------------------------------------
# Tracking
# ---------------------------------------------------------------------------

def get_tracking(carrier, tracking_number):
    history = [t for t in _tracking_store
               if t["carrier"].lower() == carrier.lower()
               and t["tracking_number"] == tracking_number]
    if not history:
        return {"error": f"tracking {tracking_number} for {carrier} not found"}
    history = sorted(history, key=lambda t: t["status_time"], reverse=True)
    latest = history[0]
    return {
        "carrier": carrier,
        "tracking_number": tracking_number,
        "tracking_status": {
            "status": latest["status"],
            "status_details": latest["status_detail"],
            "location": {"city": latest["location_city"], "state": latest["location_state"]},
            "status_date": latest["status_time"],
        },
        "tracking_history": [{
            "status": h["status"],
            "status_details": h["status_detail"],
            "location": {"city": h["location_city"], "state": h["location_state"]},
            "status_date": h["status_time"],
        } for h in history],
    }
