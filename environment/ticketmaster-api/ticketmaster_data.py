"""Data access module for the Ticketmaster Discovery API mock service.

Mirrors a subset of the Ticketmaster Discovery API v2: events, venues,
attractions, classifications. Records use stable string IDs. The server wraps
list responses in the ``{"_embedded": {...}, "page": {...}}`` shape.
"""

import csv
from pathlib import Path

DATA_DIR = Path(__file__).parent

import sys as _sys
_sys.path.insert(0, str(DATA_DIR.parent))
from _mutable_store import (
    read_seed_with_ctx, get_store,
    opt_int,
    opt_float,
)

_store = get_store("ticketmaster-api")
_API = "ticketmaster-api"

_store.register("classifications", primary_key="id",
                initial_loader=lambda: _coerce_classifications(_load("classifications.json", "classifications")))
_store.register("venues", primary_key="id",
                initial_loader=lambda: _coerce_venues(_load("venues.json", "venues")))
_store.register("attractions", primary_key="id",
                initial_loader=lambda: _coerce_attractions(_load("attractions.json", "attractions")))
_store.register("events", primary_key="id",
                initial_loader=lambda: _coerce_events(_load("events.json", "events")))


def _classifications_rows():
    return _store.table("classifications").rows()


def _venues_rows():
    return _store.table("venues").rows()


def _attractions_rows():
    return _store.table("attractions").rows()


def _events_rows():
    return _store.table("events").rows()



def _load(filename, table):
    return read_seed_with_ctx(DATA_DIR / filename, _API, table)


def _strip_ctx(r):
    return {k: v for k, v in r.items() if not k.startswith("__")}


def _to_float(v, default=0.0):
    if v is None or str(v).strip() == "":
        return default
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


def _to_int(v, default=0):
    if v is None or str(v).strip() == "":
        return default
    try:
        return int(v)
    except (TypeError, ValueError):
        return default


# ---------------------------------------------------------------------------
# Load + coerce
# ---------------------------------------------------------------------------

def _coerce_classifications(rows):
    return [_strip_ctx(r) for r in rows]


def _coerce_venues(rows):
    out = []
    for r in rows:
        d = _strip_ctx(r)
        d["latitude"] = opt_float(r, "latitude", default=0.0)
        d["longitude"] = opt_float(r, "longitude", default=0.0)
        out.append(d)
    return out


def _coerce_attractions(rows):
    out = []
    for r in rows:
        d = _strip_ctx(r)
        d["upcoming_events"] = opt_int(r, "upcoming_events", default=0)
        out.append(d)
    return out


def _coerce_events(rows):
    out = []
    for r in rows:
        d = _strip_ctx(r)
        d["price_min"] = opt_float(r, "price_min", default=0.0)
        d["price_max"] = opt_float(r, "price_max", default=0.0)
        out.append(d)
    return out










# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _find(store, obj_id):
    return next((x for x in store if x["id"] == obj_id), None)


def _classification_obj(classification_id):
    c = _find(_classifications_rows(), classification_id)
    if not c:
        return None
    return {
        "segment": {"name": c["segment"]},
        "genre": {"name": c["genre"]},
        "subGenre": {"name": c["subgenre"]},
    }


def _venue_obj(venue_id):
    v = _find(_venues_rows(), venue_id)
    if not v:
        return None
    return {
        "id": v["id"],
        "name": v["name"],
        "city": {"name": v["city"]},
        "state": {"stateCode": v["state"]},
        "country": {"countryCode": v["country"]},
        "postalCode": v["postal_code"],
        "address": {"line1": v["address"]},
        "location": {"latitude": v["latitude"], "longitude": v["longitude"]},
    }


def _attraction_obj(attraction_id):
    a = _find(_attractions_rows(), attraction_id)
    if not a:
        return None
    return {
        "id": a["id"],
        "name": a["name"],
        "type": a["type"],
        "upcomingEvents": {"_total": a["upcoming_events"]},
        "classifications": [{
            "segment": {"name": a["segment"]},
            "genre": {"name": a["genre"]},
        }],
    }


def _event_obj(e):
    cls = _classification_obj(e["classification_id"])
    venue = _venue_obj(e["venue_id"])
    attraction = _attraction_obj(e["attraction_id"])
    embedded = {}
    if venue:
        embedded["venues"] = [venue]
    if attraction:
        embedded["attractions"] = [attraction]
    return {
        "id": e["id"],
        "name": e["name"],
        "dates": {"start": {"dateTime": e["start_datetime"]}, "status": {"code": e["status"]}},
        "classifications": [cls] if cls else [],
        "priceRanges": [{
            "type": "standard",
            "currency": e["currency"],
            "min": e["price_min"],
            "max": e["price_max"],
        }],
        "_embedded": embedded,
    }


# ---------------------------------------------------------------------------
# Events
# ---------------------------------------------------------------------------

def search_events(keyword=None, city=None, classification_name=None,
                  start_datetime=None):
    results = list(_events_rows())
    if keyword:
        kw = keyword.lower()
        results = [e for e in results if kw in e["name"].lower()]
    if city:
        cl = city.lower()
        venue_ids = {v["id"] for v in _venues_rows() if v["city"].lower() == cl}
        results = [e for e in results if e["venue_id"] in venue_ids]
    if classification_name:
        cn = classification_name.lower()
        cls_ids = {c["id"] for c in _classifications_rows()
                   if cn in (c["segment"].lower(), c["genre"].lower(), c["subgenre"].lower())}
        results = [e for e in results if e["classification_id"] in cls_ids]
    if start_datetime:
        results = [e for e in results if e["start_datetime"] >= start_datetime]
    return [_event_obj(e) for e in results]


def get_event(event_id):
    e = _find(_events_rows(), event_id)
    if not e:
        return {"error": f"Event {event_id} not found"}
    return _event_obj(e)


# ---------------------------------------------------------------------------
# Venues
# ---------------------------------------------------------------------------

def search_venues(keyword=None):
    results = list(_venues_rows())
    if keyword:
        kw = keyword.lower()
        results = [v for v in results if kw in v["name"].lower() or kw in v["city"].lower()]
    return [_venue_obj(v["id"]) for v in results]


def get_venue(venue_id):
    v = _venue_obj(venue_id)
    if not v:
        return {"error": f"Venue {venue_id} not found"}
    return v


# ---------------------------------------------------------------------------
# Attractions
# ---------------------------------------------------------------------------

def search_attractions(keyword=None):
    results = list(_attractions_rows())
    if keyword:
        kw = keyword.lower()
        results = [a for a in results if kw in a["name"].lower()]
    return [_attraction_obj(a["id"]) for a in results]


def get_attraction(attraction_id):
    a = _attraction_obj(attraction_id)
    if not a:
        return {"error": f"Attraction {attraction_id} not found"}
    return a


# ---------------------------------------------------------------------------
# Classifications
# ---------------------------------------------------------------------------

def list_classifications():
    out = []
    for c in _classifications_rows():
        out.append({
            "id": c["id"],
            "segment": {
                "name": c["segment"],
                "_embedded": {"genres": [{
                    "name": c["genre"],
                    "_embedded": {"subgenres": [{"name": c["subgenre"]}]},
                }]},
            },
        })
    return out

_store.eager_load()
