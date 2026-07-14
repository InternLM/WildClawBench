"""Data access module for the Uber API mock service."""

import csv
from copy import deepcopy
import json
import math
import uuid
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).parent

import sys as _sys
_sys.path.insert(0, str(DATA_DIR.parent))
from _mutable_store import (
    read_seed_with_ctx, get_store, opt_str, strict_bool, strict_float, strict_int)

_store = get_store("uber-api")
_API = "uber-api"



def _store_patch(_table, _row_or_pk, _updates):
    """Persist field updates to a stored row (was: in-place mutation of a copy)."""
    _t = _store.table(_table)
    _pk = _row_or_pk.get(_t.primary_key, _row_or_pk.get("id")) if isinstance(_row_or_pk, dict) else _row_or_pk
    return _t.patch(_pk, _updates)


def _store_delete(_table, _row_or_pk):
    """Persist a row deletion (was: pop/remove on a copy)."""
    _t = _store.table(_table)
    _pk = _row_or_pk.get(_t.primary_key, _row_or_pk.get("id")) if isinstance(_row_or_pk, dict) else _row_or_pk
    return _t.delete(_pk)

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

_store.register("products", primary_key="product_id",
                initial_loader=lambda: _coerce_products(_load("products.json", "products")))
_store.register("trips", primary_key="request_id",
                initial_loader=lambda: _coerce_trips(_load("trips.json", "trips")))
_store.register_document("rider", initial_loader=lambda: __import__('json').load(open(DATA_DIR / "rider.json", encoding="utf-8")))


def _products_rows():
    return _store.table("products").rows()


def _trips_rows():
    return _store.table("trips").rows()


def _rider_doc():
    return _store.document("rider").get()



def _load(filename, table):
    return read_seed_with_ctx(DATA_DIR / filename, _API, table)


def _strip_ctx(r):
    return {k: v for k, v in r.items() if not k.startswith("__")}


def _now_iso():
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


def _to_bool(v):
    return str(v).strip().lower() == "true"


# ---------------------------------------------------------------------------
# Load + coerce
# ---------------------------------------------------------------------------

def _coerce_products(rows):
    out = []
    for r in rows:
        out.append({
            **_strip_ctx(r),
            "capacity": strict_int(r, "capacity"),
            "base_fare": strict_float(r, "base_fare"),
            "cost_per_mile": strict_float(r, "cost_per_mile"),
            "cost_per_minute": strict_float(r, "cost_per_minute"),
            "booking_fee": strict_float(r, "booking_fee"),
            "minimum_fare": strict_float(r, "minimum_fare"),
            "shared": strict_bool(r, "shared"),
        })
    return out


def _coerce_trips(rows):
    out = []
    for r in rows:
        out.append({
            **_strip_ctx(r),
            "start_latitude": strict_float(r, "start_latitude"),
            "start_longitude": strict_float(r, "start_longitude"),
            "end_latitude": strict_float(r, "end_latitude"),
            "end_longitude": strict_float(r, "end_longitude"),
            "distance_miles": strict_float(r, "distance_miles"),
            "duration_minutes": strict_float(r, "duration_minutes"),
            "fare": strict_float(r, "fare"),
            "surge_multiplier": strict_float(r, "surge_multiplier"),
            "driver_name": opt_str(r, "driver_name", default="") or None,
            "vehicle": opt_str(r, "vehicle", default="") or None,
            "license_plate": opt_str(r, "license_plate", default="") or None,
            "completed_at": opt_str(r, "completed_at", default="") or None,
        })
    return out





def _new_id(prefix):
    return f"{prefix}-{uuid.uuid4().hex[:8]}"


# ---------------------------------------------------------------------------
# Geo helpers
# ---------------------------------------------------------------------------

def _haversine_miles(lat1, lon1, lat2, lon2):
    """Great-circle distance between two points in miles."""
    radius_miles = 3958.8
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = (math.sin(dphi / 2) ** 2
         + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return radius_miles * c


def _estimate_minutes(distance_miles):
    """Rough city travel time: ~18 mph average plus a fixed pickup buffer."""
    return round(distance_miles / 18.0 * 60.0 + 2.0, 1)


# ---------------------------------------------------------------------------
# Products
# ---------------------------------------------------------------------------

def list_products(latitude=None, longitude=None):
    return {"products": deepcopy(_products_rows())}


def get_product(product_id):
    for p in _products_rows():
        if p["product_id"] == product_id:
            return p
    return {"error": f"Product {product_id} not found"}


# ---------------------------------------------------------------------------
# Estimates
# ---------------------------------------------------------------------------

def price_estimates(start_latitude, start_longitude, end_latitude, end_longitude):
    distance = _haversine_miles(start_latitude, start_longitude,
                                end_latitude, end_longitude)
    duration = _estimate_minutes(distance)
    prices = []
    for p in _products_rows():
        raw = (p["base_fare"] + p["booking_fee"]
               + p["cost_per_mile"] * distance
               + p["cost_per_minute"] * duration)
        low = max(raw, p["minimum_fare"])
        high = low * 1.25
        prices.append({
            "product_id": p["product_id"],
            "display_name": p["display_name"],
            "currency_code": "USD",
            "distance": round(distance, 2),
            "duration": int(round(duration * 60)),
            "estimate": f"${low:.2f}-{high:.2f}",
            "low_estimate": round(low, 2),
            "high_estimate": round(high, 2),
            "surge_multiplier": 1.0,
        })
    return {"prices": prices}


def time_estimates(start_latitude, start_longitude, product_id=None):
    times = []
    for p in _products_rows():
        if product_id and p["product_id"] != product_id:
            continue
        # Pickup ETA scales with vehicle tier; deterministic per product.
        eta_minutes = {"uberx": 3, "uberxl": 5, "uberblack": 8, "uberpool": 4}.get(
            p["product_id"], 4)
        times.append({
            "product_id": p["product_id"],
            "display_name": p["display_name"],
            "estimate": eta_minutes * 60,
        })
    return {"times": times}


# ---------------------------------------------------------------------------
# Ride requests / trips
# ---------------------------------------------------------------------------

_DRIVERS = [
    ("Sofia Marquez", "Toyota Corolla White", "4DRV883"),
    ("Daniel Osei", "Hyundai Sonata Gray", "6CAB220"),
    ("Mei Tanaka", "Tesla Model 3 Black", "8EVX771"),
]


def create_request(product_id, start_latitude, start_longitude,
                   end_latitude=None, end_longitude=None, rider_id=None):
    product = next((p for p in _products_rows() if p["product_id"] == product_id), None)
    if not product:
        return {"error": f"Product {product_id} not found"}

    distance = duration = fare = 0.0
    if end_latitude is not None and end_longitude is not None:
        distance = _haversine_miles(start_latitude, start_longitude,
                                    end_latitude, end_longitude)
        duration = _estimate_minutes(distance)
        raw = (product["base_fare"] + product["booking_fee"]
               + product["cost_per_mile"] * distance
               + product["cost_per_minute"] * duration)
        fare = round(max(raw, product["minimum_fare"]), 2)

    driver_name, vehicle, plate = _DRIVERS[len(_trips_rows()) % len(_DRIVERS)]
    trip = {
        "request_id": _new_id("req"),
        "product_id": product_id,
        "status": "processing",
        "rider_id": rider_id or _rider_doc()["rider_id"],
        "driver_name": driver_name,
        "vehicle": vehicle,
        "license_plate": plate,
        "start_latitude": start_latitude,
        "start_longitude": start_longitude,
        "start_address": "",
        "end_latitude": end_latitude if end_latitude is not None else 0.0,
        "end_longitude": end_longitude if end_longitude is not None else 0.0,
        "end_address": "",
        "distance_miles": round(distance, 2),
        "duration_minutes": duration,
        "fare": fare,
        "surge_multiplier": 1.0,
        "eta_minutes": 3,
        "requested_at": _now_iso(),
        "completed_at": None,
    }
    _store_insert("trips", trip)
    return trip


def get_request(request_id):
    for t in _trips_rows():
        if t["request_id"] == request_id:
            return t
    return {"error": f"Request {request_id} not found"}


def cancel_request(request_id):
    for t in _trips_rows():
        if t["request_id"] == request_id:
            if t["status"] in {"completed", "canceled_rider", "canceled_driver"}:
                return {"error": f"Request {request_id} cannot be canceled (status: {t['status']})"}
            _changes = {"status": "canceled_rider"}
            t.update(_changes)
            _store_patch("trips", t, _changes)
            return t
    return {"error": f"Request {request_id} not found"}


def get_history(rider_id=None, limit=50, offset=0):
    results = [t for t in _trips_rows() if t["completed_at"]]
    if rider_id:
        results = [t for t in results if t["rider_id"] == rider_id]
    results.sort(key=lambda t: t["requested_at"], reverse=True)
    page = results[offset: offset + limit]
    return {
        "count": len(results),
        "limit": limit,
        "offset": offset,
        "history": page,
    }


# ---------------------------------------------------------------------------
# Rider profile
# ---------------------------------------------------------------------------

def get_me():
    return _rider_doc()

_store.eager_load()
