"""Data access module for the Amadeus API mock service.

Mirrors a subset of the Amadeus Self-Service APIs: flight offers search,
reference data for locations/airports and airlines, and offer pricing.
"""

import csv
import json
import uuid
from pathlib import Path

DATA_DIR = Path(__file__).parent

import sys as _sys
_sys.path.insert(0, str(DATA_DIR.parent))
from _mutable_store import (
    read_seed_with_ctx, get_store,
    strict_float,
)

_store = get_store("amadeus-api")
_API = "amadeus-api"

_store.register("airports", primary_key="iata_code",
                initial_loader=lambda: _coerce_airports(_load("airports.json", "airports")))
_store.register("airlines", primary_key="iata_code",
                initial_loader=lambda: _coerce_airlines(_load("airlines.json", "airlines")))
_store.register_document("offers", initial_loader=lambda: __import__('json').load(open(DATA_DIR / "flight_offers.json", encoding="utf-8")))


def _airports_rows():
    return _store.table("airports").rows()


def _airlines_rows():
    return _store.table("airlines").rows()


def _offers_doc():
    return _store.document("offers").get()



def _load(filename, table):
    return read_seed_with_ctx(DATA_DIR / filename, _API, table)


def _strip_ctx(r):
    return {k: v for k, v in r.items() if not k.startswith("__")}


# ---------------------------------------------------------------------------
# Load + coerce
# ---------------------------------------------------------------------------

def _coerce_airports(rows):
    out = []
    for r in rows:
        out.append({
            **_strip_ctx(r),
            "latitude": strict_float(r, "latitude"),
            "longitude": strict_float(r, "longitude"),
        })
    return out


def _coerce_airlines(rows):
    return [_strip_ctx(r) for r in rows]





# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _airport_by_code(code):
    return next((a for a in _airports_rows() if a["iata_code"] == code), None)


def _location_id(code):
    return f"A{code}"


def _location_view(a):
    return {
        "type": "location",
        "subType": "AIRPORT",
        "id": _location_id(a["iata_code"]),
        "name": a["name"],
        "iataCode": a["iata_code"],
        "address": {
            "cityName": a["city_name"],
            "cityCode": a["city_code"],
            "countryName": a["country_name"],
            "countryCode": a["country_code"],
        },
        "geoCode": {"latitude": a["latitude"], "longitude": a["longitude"]},
        "timeZone": {"offset": a["timezone"]},
    }


def _public_offer(offer):
    out = dict(offer)
    out.pop("originLocationCode", None)
    out.pop("destinationLocationCode", None)
    out.pop("departureDate", None)
    return out


# ---------------------------------------------------------------------------
# Flight offers
# ---------------------------------------------------------------------------

def search_flight_offers(origin, destination, departure_date=None, adults=1, max_results=50):
    matches = [
        o for o in _offers_doc()
        if o["originLocationCode"] == origin and o["destinationLocationCode"] == destination
    ]
    if departure_date:
        matches = [o for o in matches if o["departureDate"] == departure_date]

    adults = max(1, int(adults or 1))
    data = []
    for o in matches[:max_results]:
        view = _public_offer(o)
        base = float(o["price"]["base"])
        per_adult_total = float(o["price"]["total"])
        per_adult_fees = round(per_adult_total - base, 2)
        total = round(per_adult_total * adults, 2)
        view["price"] = {
            "currency": o["price"]["currency"],
            "total": f"{total:.2f}",
            "base": f"{round(base * adults, 2):.2f}",
            "grandTotal": f"{total:.2f}",
            "fees": [{"amount": f"{round(per_adult_fees * adults, 2):.2f}", "type": "SUPPLIER"}],
        }
        view["travelerPricings"] = [
            {
                "travelerId": str(i + 1),
                "fareOption": "STANDARD",
                "travelerType": "ADULT",
                "price": {"currency": o["price"]["currency"], "total": f"{per_adult_total:.2f}"},
            }
            for i in range(adults)
        ]
        data.append(view)

    return {
        "meta": {"count": len(data)},
        "data": data,
        "dictionaries": {
            "carriers": {a["iata_code"]: a["business_name"] for a in _airlines_rows()},
            "locations": {
                a["iata_code"]: {"cityCode": a["city_code"], "countryCode": a["country_code"]}
                for a in _airports_rows()
            },
        },
    }


def get_offer(offer_id):
    return next((o for o in _offers_doc() if o["id"] == str(offer_id)), None)


def price_flight_offer(offer):
    """Confirm pricing for an offer. Accepts a posted flight-offer dict.

    If the offer has an id matching a seeded offer, the seeded price is used as
    the authoritative quote; otherwise the posted price is echoed back.
    """
    offer_id = str(offer.get("id", "")) if isinstance(offer, dict) else ""
    seeded = get_offer(offer_id) if offer_id else None
    if seeded:
        priced = _public_offer(seeded)
    elif isinstance(offer, dict):
        priced = dict(offer)
    else:
        return {"error": "Invalid flight offer payload"}
    return {
        "data": {
            "type": "flight-offers-pricing",
            "flightOffers": [priced],
        }
    }


# ---------------------------------------------------------------------------
# Reference data: locations
# ---------------------------------------------------------------------------

def search_locations(keyword=None, sub_type="AIRPORT,CITY"):
    types = [t.strip().upper() for t in (sub_type or "AIRPORT,CITY").split(",") if t.strip()]
    pool = _airports_rows()
    if keyword:
        k = keyword.lower()
        pool = [
            a for a in pool
            if k in a["iata_code"].lower()
            or k in a["name"].lower()
            or k in a["city_name"].lower()
        ]
    data = []
    for a in pool:
        if "AIRPORT" in types:
            data.append(_location_view(a))
        if "CITY" in types:
            city = _location_view(a)
            city["subType"] = "CITY"
            city["id"] = f"C{a['city_code']}"
            city["name"] = a["city_name"]
            data.append(city)
    return {"meta": {"count": len(data)}, "data": data}


def get_location(location_id):
    code = location_id[1:] if location_id and location_id[0] in ("A", "C") else location_id
    a = _airport_by_code(code)
    if not a:
        a = next((x for x in _airports_rows() if x["city_code"] == code), None)
    if not a:
        return {"error": f"Location {location_id} not found"}
    return {"data": _location_view(a)}


# ---------------------------------------------------------------------------
# Reference data: airlines
# ---------------------------------------------------------------------------

def get_airlines(airline_codes=None):
    pool = _airlines_rows()
    if airline_codes:
        codes = {c.strip().upper() for c in airline_codes.split(",") if c.strip()}
        pool = [a for a in pool if a["iata_code"] in codes]
    data = [
        {
            "type": "airline",
            "iataCode": a["iata_code"],
            "icaoCode": a["icao_code"],
            "businessName": a["business_name"],
            "commonName": a["common_name"],
        }
        for a in pool
    ]
    return {"meta": {"count": len(data)}, "data": data}

_store.eager_load()
