"""Data access module for the Airbnb API mock service."""

import csv
import sys
import uuid
from datetime import datetime, date
from pathlib import Path

DATA_DIR = Path(__file__).parent

sys.path.insert(0, str(DATA_DIR.parent))
from _mutable_store import (
    read_seed_with_ctx, get_store, opt_csv_list, strict_bool, strict_float, strict_int)

_store = get_store("airbnb-api")
_API = "airbnb-api"

SERVICE_FEE_PCT = 14.0  # guest service fee as percent of nightly subtotal


def _load(filename, table):
    return read_seed_with_ctx(DATA_DIR / filename, _API, table)


def _strip_ctx(r):
    return {k: v for k, v in r.items() if not k.startswith("__")}


def _now_iso():
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


def _to_bool(v):
    return str(v).strip().lower() == "true"


def _parse_date(value):
    if not value:
        return None
    try:
        return date.fromisoformat(value)
    except (TypeError, ValueError):
        return None


# ---------------------------------------------------------------------------
# Load + coerce
# ---------------------------------------------------------------------------

def _coerce_listings(rows):
    out = []
    for r in rows:
        out.append({
            **_strip_ctx(r),
            "price_per_night": strict_float(r, "price_per_night"),
            "cleaning_fee": strict_float(r, "cleaning_fee"),
            "beds": strict_int(r, "beds"),
            "baths": strict_float(r, "baths"),
            "max_guests": strict_int(r, "max_guests"),
            "rating": strict_float(r, "rating"),
            "review_count": strict_int(r, "review_count"),
            "instant_book": strict_bool(r, "instant_book"),
        })
    return out


def _coerce_hosts(rows):
    out = []
    for r in rows:
        out.append({
            **_strip_ctx(r),
            "superhost": strict_bool(r, "superhost"),
            "joined_year": strict_int(r, "joined_year"),
            "response_rate": strict_int(r, "response_rate"),
            "languages": [x.strip() for x in opt_csv_list(r, "languages", sep=",")],
        })
    return out


def _coerce_availability(rows):
    out = []
    for r in rows:
        out.append({
            **_strip_ctx(r),
            "available": strict_bool(r, "available"),
        })
    return out


def _coerce_reviews(rows):
    out = []
    for r in rows:
        out.append({
            **_strip_ctx(r),
            "rating": strict_int(r, "rating"),
        })
    return out


_store.register("listings", primary_key="listing_id",
                initial_loader=lambda: _coerce_listings(_load("listings.json", "listings")))
_store.register("hosts", primary_key="host_id",
                initial_loader=lambda: _coerce_hosts(_load("hosts.json", "hosts")))
_store.register("availability", primary_key="_pk",
                initial_loader=lambda: [
                    {**row, "_pk": f"{row['listing_id']}@{row['start_date']}"}
                    for row in _coerce_availability(_load("availability.json", "availability"))
                ])
_store.register("reviews", primary_key="review_id",
                initial_loader=lambda: _coerce_reviews(_load("reviews.json", "reviews")))
_store.register("reservations", primary_key="reservation_id",
                initial_loader=lambda: [])


def _listings_rows():
    return _store.table("listings").rows()


def _hosts_rows():
    return _store.table("hosts").rows()


def _availability_rows():
    return _store.table("availability").rows()


def _reviews_rows():
    return _store.table("reviews").rows()


def _reservations_rows():
    return _store.table("reservations").rows()


def _new_id(prefix):
    return f"{prefix}-{uuid.uuid4().hex[:10]}"


def _get_host(host_id):
    return next((h for h in _hosts_rows() if h["host_id"] == host_id), None)


def _attach_host(listing):
    listing = dict(listing)
    listing["host"] = _get_host(listing["host_id"])
    return listing


# ---------------------------------------------------------------------------
# Listings / search
# ---------------------------------------------------------------------------

def search_listings(location=None, checkin=None, checkout=None, guests=None,
                    min_price=None, max_price=None):
    results = list(_listings_rows())
    if location:
        loc = location.lower()
        results = [l for l in results if loc in l["city"].lower() or loc in l["country"].lower()]
    if guests:
        results = [l for l in results if l["max_guests"] >= int(guests)]
    if min_price is not None:
        results = [l for l in results if l["price_per_night"] >= float(min_price)]
    if max_price is not None:
        results = [l for l in results if l["price_per_night"] <= float(max_price)]
    ci, co = _parse_date(checkin), _parse_date(checkout)
    if ci and co:
        results = [l for l in results if _is_available(l["listing_id"], ci, co)]
    results = [_attach_host(l) for l in results]
    results.sort(key=lambda l: l["rating"], reverse=True)
    return {"count": len(results), "listings": results}


def get_listing(listing_id):
    for l in _listings_rows():
        if l["listing_id"] == listing_id:
            return _attach_host(l)
    return {"error": f"Listing {listing_id} not found"}


def get_availability(listing_id):
    if not any(l["listing_id"] == listing_id for l in _listings_rows()):
        return {"error": f"Listing {listing_id} not found"}
    windows = [a for a in _availability_rows() if a["listing_id"] == listing_id]
    return {"listing_id": listing_id, "windows": windows}


def get_reviews(listing_id):
    if not any(l["listing_id"] == listing_id for l in _listings_rows()):
        return {"error": f"Listing {listing_id} not found"}
    revs = [r for r in _reviews_rows() if r["listing_id"] == listing_id]
    return {"listing_id": listing_id, "count": len(revs), "reviews": revs}


def _is_available(listing_id, checkin, checkout):
    """A stay is available when fully covered by available windows
    and not intersecting any unavailable window."""
    windows = [a for a in _availability_rows() if a["listing_id"] == listing_id]
    covered = False
    for w in windows:
        ws, we = _parse_date(w["start_date"]), _parse_date(w["end_date"])
        if ws is None or we is None:
            continue
        overlaps = checkin < we and checkout > ws
        if not w["available"] and overlaps:
            return False
        if w["available"] and ws <= checkin and we >= checkout:
            covered = True
    return covered


# ---------------------------------------------------------------------------
# Reservations
# ---------------------------------------------------------------------------

def create_reservation(listing_id, checkin, checkout, guests, guest_name="Guest"):
    listing = next((l for l in _listings_rows() if l["listing_id"] == listing_id), None)
    if not listing:
        return {"error": f"Listing {listing_id} not found"}
    ci, co = _parse_date(checkin), _parse_date(checkout)
    if not ci or not co:
        return {"error": "checkin and checkout must be ISO dates (YYYY-MM-DD)"}
    if co <= ci:
        return {"error": "checkout must be after checkin"}
    if int(guests) > listing["max_guests"]:
        return {"error": f"Guest count {guests} exceeds max_guests {listing['max_guests']}"}
    if not _is_available(listing_id, ci, co):
        return {"error": "Listing is not available for the requested dates"}

    nights = (co - ci).days
    nightly_subtotal = round(listing["price_per_night"] * nights, 2)
    cleaning_fee = listing["cleaning_fee"]
    service_fee = round(nightly_subtotal * SERVICE_FEE_PCT / 100, 2)
    total = round(nightly_subtotal + cleaning_fee + service_fee, 2)

    reservation = {
        "reservation_id": _new_id("res"),
        "listing_id": listing_id,
        "guest_name": guest_name,
        "checkin": checkin,
        "checkout": checkout,
        "nights": nights,
        "guests": int(guests),
        "status": "confirmed",
        "nightly_subtotal": nightly_subtotal,
        "cleaning_fee": cleaning_fee,
        "service_fee": service_fee,
        "total": total,
        "created_at": _now_iso(),
    }
    _store.table("reservations").upsert(reservation)
    return reservation


def get_reservation(reservation_id):
    found = _store.table("reservations").get(reservation_id)
    if found is not None:
        return found
    return {"error": f"Reservation {reservation_id} not found"}


def cancel_reservation(reservation_id):
    existing = _store.table("reservations").get(reservation_id)
    if existing is None:
        return {"error": f"Reservation {reservation_id} not found"}
    if existing["status"] == "cancelled":
        return {"error": f"Reservation {reservation_id} is already cancelled"}
    _store.table("reservations").patch(reservation_id, {"status": "cancelled"})
    return _store.table("reservations").get(reservation_id)

_store.eager_load()
