"""Data access module for the Airbnb API mock service."""

import csv
import uuid
from copy import deepcopy
from datetime import datetime, date
from pathlib import Path

DATA_DIR = Path(__file__).parent

SERVICE_FEE_PCT = 14.0  # guest service fee as percent of nightly subtotal


def _load(filename):
    with open(DATA_DIR / filename, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


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
            **r,
            "price_per_night": float(r["price_per_night"]),
            "cleaning_fee": float(r["cleaning_fee"]),
            "beds": int(r["beds"]),
            "baths": float(r["baths"]),
            "max_guests": int(r["max_guests"]),
            "rating": float(r["rating"]),
            "review_count": int(r["review_count"]),
            "instant_book": _to_bool(r["instant_book"]),
        })
    return out


def _coerce_hosts(rows):
    out = []
    for r in rows:
        out.append({
            **r,
            "superhost": _to_bool(r["superhost"]),
            "joined_year": int(r["joined_year"]),
            "response_rate": int(r["response_rate"]),
            "languages": [x.strip() for x in r["languages"].split(",")],
        })
    return out


def _coerce_availability(rows):
    out = []
    for r in rows:
        out.append({
            **r,
            "available": _to_bool(r["available"]),
        })
    return out


def _coerce_reviews(rows):
    out = []
    for r in rows:
        out.append({
            **r,
            "rating": int(r["rating"]),
        })
    return out


_listings = _coerce_listings(_load("listings.csv"))
_hosts = _coerce_hosts(_load("hosts.csv"))
_availability = _coerce_availability(_load("availability.csv"))
_reviews = _coerce_reviews(_load("reviews.csv"))

_listings_store = deepcopy(_listings)
_hosts_store = deepcopy(_hosts)
_availability_store = deepcopy(_availability)
_reviews_store = deepcopy(_reviews)
_reservations_store = []  # built up in memory


def _new_id(prefix):
    return f"{prefix}-{uuid.uuid4().hex[:10]}"


def _get_host(host_id):
    return next((h for h in _hosts_store if h["host_id"] == host_id), None)


def _attach_host(listing):
    listing = dict(listing)
    listing["host"] = _get_host(listing["host_id"])
    return listing


# ---------------------------------------------------------------------------
# Listings / search
# ---------------------------------------------------------------------------

def search_listings(location=None, checkin=None, checkout=None, guests=None,
                    min_price=None, max_price=None):
    results = list(_listings_store)
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
    for l in _listings_store:
        if l["listing_id"] == listing_id:
            return _attach_host(l)
    return {"error": f"Listing {listing_id} not found"}


def get_availability(listing_id):
    if not any(l["listing_id"] == listing_id for l in _listings_store):
        return {"error": f"Listing {listing_id} not found"}
    windows = [a for a in _availability_store if a["listing_id"] == listing_id]
    return {"listing_id": listing_id, "windows": windows}


def get_reviews(listing_id):
    if not any(l["listing_id"] == listing_id for l in _listings_store):
        return {"error": f"Listing {listing_id} not found"}
    revs = [r for r in _reviews_store if r["listing_id"] == listing_id]
    return {"listing_id": listing_id, "count": len(revs), "reviews": revs}


def _is_available(listing_id, checkin, checkout):
    """A stay is available when fully covered by available windows
    and not intersecting any unavailable window."""
    windows = [a for a in _availability_store if a["listing_id"] == listing_id]
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
    listing = next((l for l in _listings_store if l["listing_id"] == listing_id), None)
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
    _reservations_store.append(reservation)
    return reservation


def get_reservation(reservation_id):
    for r in _reservations_store:
        if r["reservation_id"] == reservation_id:
            return r
    return {"error": f"Reservation {reservation_id} not found"}


def cancel_reservation(reservation_id):
    for i, r in enumerate(_reservations_store):
        if r["reservation_id"] == reservation_id:
            if r["status"] == "cancelled":
                return {"error": f"Reservation {reservation_id} is already cancelled"}
            _reservations_store[i]["status"] = "cancelled"
            return _reservations_store[i]
    return {"error": f"Reservation {reservation_id} not found"}
