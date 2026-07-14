"""Data access module for the Google Maps API mock service.

Distances are computed from lat/lng using the haversine formula (no external
libraries). All list endpoints return Google-style `{"status": "OK", ...}`
envelopes.
"""

import csv
from copy import deepcopy
import math
from pathlib import Path

DATA_DIR = Path(__file__).parent

import sys as _sys
_sys.path.insert(0, str(DATA_DIR.parent))
from _mutable_store import (
    read_json_with_ctx, get_store, opt_csv_list, strict_float, strict_int)

_store = get_store("google-maps-api")
_API = "google-maps-api"

_store.register("places", primary_key="place_id",
                initial_loader=lambda: _coerce_places(_load("places.json", "places")))
_store.register("geocodes", primary_key="query",
                initial_loader=lambda: _coerce_geocodes(_load("geocodes.json", "geocodes")))


def _places_rows():
    return _store.table("places").rows()


def _geocodes_rows():
    return _store.table("geocodes").rows()


EARTH_RADIUS_M = 6371000.0  # mean Earth radius in meters
WALK_SPEED_MPS = 1.39       # ~5 km/h
DRIVE_SPEED_MPS = 13.4      # ~48 km/h (urban average)


def _load(filename, table):
    return read_json_with_ctx((DATA_DIR / filename).with_suffix(".json"), _API, table)


def _strip_ctx(r):
    return {k: v for k, v in r.items() if not k.startswith("__")}


# ---------------------------------------------------------------------------
# Load + coerce
# ---------------------------------------------------------------------------

def _coerce_places(rows):
    out = []
    for r in rows:
        out.append({
            "place_id": r["place_id"],
            "name": r["name"],
            "formatted_address": r["formatted_address"],
            "geometry": {"location": {"lat": strict_float(r, "lat"), "lng": strict_float(r, "lng")}},
            "rating": strict_float(r, "rating"),
            "user_ratings_total": strict_int(r, "user_ratings_total"),
            "types": [t for t in opt_csv_list(r, "types", sep="|") if t],
            "business_status": r["business_status"],
            "price_level": strict_int(r, "price_level"),
        })
    return out


def _coerce_geocodes(rows):
    out = []
    for r in rows:
        out.append({
            "query": r["query"],
            "formatted_address": r["formatted_address"],
            "lat": strict_float(r, "lat"),
            "lng": strict_float(r, "lng"),
            "place_id": r["place_id"],
            "location_type": r["location_type"],
        })
    return out






# ---------------------------------------------------------------------------
# Geometry helpers
# ---------------------------------------------------------------------------

def haversine_meters(lat1, lng1, lat2, lng2):
    """Great-circle distance between two points in meters."""
    rlat1, rlat2 = math.radians(lat1), math.radians(lat2)
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    a = (math.sin(dlat / 2) ** 2
         + math.cos(rlat1) * math.cos(rlat2) * math.sin(dlng / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return EARTH_RADIUS_M * c


def _parse_latlng(value):
    """Parse a 'lat,lng' string into (lat, lng), else None."""
    if not value:
        return None
    parts = value.split(",")
    if len(parts) != 2:
        return None
    try:
        return float(parts[0].strip()), float(parts[1].strip())
    except ValueError:
        return None


def _resolve_point(value):
    """Resolve an origin/destination string to (lat, lng, label).

    Accepts a 'lat,lng' pair, a known geocode query, a place name, or a
    place_id. Returns None if it cannot be resolved.
    """
    ll = _parse_latlng(value)
    if ll:
        return ll[0], ll[1], value
    v = value.strip().lower()
    for g in _geocodes_rows():
        if g["query"].lower() == v or g["formatted_address"].lower() == v:
            return g["lat"], g["lng"], g["formatted_address"]
    for p in _places_rows():
        if p["place_id"] == value or p["name"].lower() == v:
            loc = p["geometry"]["location"]
            return loc["lat"], loc["lng"], p["formatted_address"]
    # partial geocode match
    for g in _geocodes_rows():
        if v in g["query"].lower() or v in g["formatted_address"].lower():
            return g["lat"], g["lng"], g["formatted_address"]
    return None


def _fmt_distance(meters):
    if meters >= 1000:
        return {"text": f"{meters / 1000:.1f} km", "value": int(round(meters))}
    return {"text": f"{int(round(meters))} m", "value": int(round(meters))}


def _fmt_duration(seconds):
    mins = max(1, int(round(seconds / 60)))
    return {"text": f"{mins} min", "value": int(round(seconds))}


# ---------------------------------------------------------------------------
# Places
# ---------------------------------------------------------------------------

def text_search(query):
    results = list(_places_rows())
    if query:
        q = query.lower()
        results = [p for p in results
                   if q in p["name"].lower()
                   or q in p["formatted_address"].lower()
                   or any(q in t for t in p["types"])]
    return {"status": "OK", "results": results}


def place_details(place_id):
    for p in _places_rows():
        if p["place_id"] == place_id:
            return {"status": "OK", "result": p}
    return {"status": "NOT_FOUND", "result": {}, "error": f"Place {place_id} not found"}


def nearby_search(location, radius=5000, place_type=None):
    point = _resolve_point(location)
    if not point:
        return {"status": "INVALID_REQUEST", "results": [],
                "error": f"Could not resolve location '{location}'"}
    lat0, lng0 = point[0], point[1]
    out = []
    for p in _places_rows():
        loc = p["geometry"]["location"]
        dist = haversine_meters(lat0, lng0, loc["lat"], loc["lng"])
        if dist <= radius and (not place_type or place_type in p["types"]):
            entry = deepcopy(p)
            entry["distance_meters"] = int(round(dist))
            out.append(entry)
    out.sort(key=lambda p: p["distance_meters"])
    return {"status": "OK", "results": out}


# ---------------------------------------------------------------------------
# Geocoding
# ---------------------------------------------------------------------------

def geocode(address):
    point = _resolve_point(address)
    if not point:
        return {"status": "ZERO_RESULTS", "results": []}
    lat, lng, label = point
    # find a matching place_id if we have one
    place_id = "ChIJgeo-derived"
    location_type = "APPROXIMATE"
    for g in _geocodes_rows():
        if abs(g["lat"] - lat) < 1e-6 and abs(g["lng"] - lng) < 1e-6:
            place_id = g["place_id"]
            location_type = g["location_type"]
            break
    return {
        "status": "OK",
        "results": [{
            "formatted_address": label,
            "geometry": {"location": {"lat": lat, "lng": lng}, "location_type": location_type},
            "place_id": place_id,
        }],
    }


# ---------------------------------------------------------------------------
# Directions / distance matrix
# ---------------------------------------------------------------------------

def directions(origin, destination, mode="driving"):
    o = _resolve_point(origin)
    d = _resolve_point(destination)
    if not o or not d:
        return {"status": "NOT_FOUND", "routes": [],
                "error": "Could not resolve origin or destination"}
    olat, olng, olabel = o
    dlat, dlng, dlabel = d
    meters = haversine_meters(olat, olng, dlat, dlng)
    # ground travel is longer than the straight-line distance
    route_meters = meters * 1.3
    speed = WALK_SPEED_MPS if mode == "walking" else DRIVE_SPEED_MPS
    seconds = route_meters / speed
    leg = {
        "start_address": olabel,
        "end_address": dlabel,
        "start_location": {"lat": olat, "lng": olng},
        "end_location": {"lat": dlat, "lng": dlng},
        "distance": _fmt_distance(route_meters),
        "duration": _fmt_duration(seconds),
    }
    return {
        "status": "OK",
        "routes": [{
            "summary": f"{olabel} to {dlabel}",
            "legs": [leg],
            "overview_polyline": {"points": "mock_polyline"},
        }],
    }


def distance_matrix(origins, destinations, mode="driving"):
    o_points = [(_resolve_point(o), o) for o in origins]
    d_points = [(_resolve_point(d), d) for d in destinations]
    speed = WALK_SPEED_MPS if mode == "walking" else DRIVE_SPEED_MPS

    origin_addresses = [p[0][2] if p[0] else p[1] for p in o_points]
    dest_addresses = [p[0][2] if p[0] else p[1] for p in d_points]

    rows = []
    for op, _ in o_points:
        elements = []
        for dp, _ in d_points:
            if not op or not dp:
                elements.append({"status": "NOT_FOUND"})
                continue
            meters = haversine_meters(op[0], op[1], dp[0], dp[1]) * 1.3
            elements.append({
                "status": "OK",
                "distance": _fmt_distance(meters),
                "duration": _fmt_duration(meters / speed),
            })
        rows.append({"elements": elements})

    return {
        "status": "OK",
        "origin_addresses": origin_addresses,
        "destination_addresses": dest_addresses,
        "rows": rows,
    }

_store.eager_load()
