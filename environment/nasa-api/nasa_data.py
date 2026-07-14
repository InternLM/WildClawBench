"""Data access module for the NASA Open APIs mock service.

Mirrors a subset of api.nasa.gov: APOD, Mars Rover Photos, NeoWs (NEO feed),
and EPIC natural imagery.
"""

import csv
from pathlib import Path

DATA_DIR = Path(__file__).parent

import sys as _sys
_sys.path.insert(0, str(DATA_DIR.parent))
from _mutable_store import (
    read_seed_with_ctx, get_store,
    strict_int,
    strict_float,
    strict_bool,
)

_store = get_store("nasa-api")
_API = "nasa-api"

_store.register("apod", primary_key="date",
                initial_loader=lambda: _coerce_apod(_load("apod.json", "apod")))
_store.register("rover_photos", primary_key="id",
                initial_loader=lambda: _coerce_rover_photos(_load("rover_photos.json", "rover_photos")))
_store.register("rovers", primary_key="name",
                initial_loader=lambda: _coerce_rovers(_load("rovers.json", "rovers")))
_store.register("neos", primary_key="id",
                initial_loader=lambda: _coerce_neos(_load("neos.json", "neos")))
_store.register("epic", primary_key="identifier",
                initial_loader=lambda: _coerce_epic(_load("epic.json", "epic")))


def _apod_rows():
    return _store.table("apod").rows()


def _rover_photos_rows():
    return _store.table("rover_photos").rows()


def _rovers_rows():
    return _store.table("rovers").rows()


def _neos_rows():
    return _store.table("neos").rows()


def _epic_rows():
    return _store.table("epic").rows()



def _load(filename, table):
    return read_seed_with_ctx(DATA_DIR / filename, _API, table)


def _strip_ctx(r):
    return {k: v for k, v in r.items() if not k.startswith("__")}


def _to_bool(v):
    return str(v).strip().lower() == "true"


# ---------------------------------------------------------------------------
# Load + coerce
# ---------------------------------------------------------------------------

def _coerce_apod(rows):
    out = []
    for r in rows:
        entry = {
            "date": r["date"],
            "title": r["title"],
            "explanation": r["explanation"],
            "url": r["url"],
            "media_type": r["media_type"],
            "service_version": "v1",
        }
        if r.get("hdurl"):
            entry["hdurl"] = r["hdurl"]
        if r.get("copyright"):
            entry["copyright"] = r["copyright"]
        out.append(entry)
    return out


def _coerce_rover_photos(rows):
    out = []
    for r in rows:
        out.append({
            "id": strict_int(r, "id"),
            "rover": r["rover"],
            "sol": strict_int(r, "sol"),
            "camera": r["camera"],
            "camera_full_name": r["camera_full_name"],
            "img_src": r["img_src"],
            "earth_date": r["earth_date"],
        })
    return out


def _coerce_rovers(rows):
    out = []
    for r in rows:
        out.append({
            "name": r["name"],
            "status": r["status"],
            "landing_date": r["landing_date"],
            "launch_date": r["launch_date"],
            "max_sol": strict_int(r, "max_sol"),
            "max_date": r["max_date"],
            "total_photos": strict_int(r, "total_photos"),
        })
    return out


def _coerce_neos(rows):
    out = []
    for r in rows:
        out.append({
            "id": r["id"],
            "name": r["name"],
            "close_approach_date": r["close_approach_date"],
            "absolute_magnitude_h": strict_float(r, "absolute_magnitude_h"),
            "est_diameter_min_km": strict_float(r, "est_diameter_min_km"),
            "est_diameter_max_km": strict_float(r, "est_diameter_max_km"),
            "is_potentially_hazardous": strict_bool(r, "is_potentially_hazardous"),
            "miss_distance_km": strict_float(r, "miss_distance_km"),
            "relative_velocity_kph": strict_float(r, "relative_velocity_kph"),
            "orbiting_body": r["orbiting_body"],
        })
    return out


def _coerce_epic(rows):
    out = []
    for r in rows:
        out.append({
            "identifier": r["identifier"],
            "image": r["image"],
            "caption": r["caption"],
            "date": r["date"],
            "centroid_coordinates": {
                "lat": strict_float(r, "centroid_lat"),
                "lon": strict_float(r, "centroid_lon"),
            },
        })
    return out












# ---------------------------------------------------------------------------
# APOD
# ---------------------------------------------------------------------------

def get_apod(date=None, start_date=None, end_date=None):
    if start_date or end_date:
        lo = start_date or min(a["date"] for a in _apod_rows())
        hi = end_date or max(a["date"] for a in _apod_rows())
        return [a for a in _apod_rows() if lo <= a["date"] <= hi]
    if date:
        a = next((x for x in _apod_rows() if x["date"] == date), None)
        if not a:
            return {"error": f"No APOD entry for {date}"}
        return a
    # latest
    return max(_apod_rows(), key=lambda x: x["date"])


# ---------------------------------------------------------------------------
# Mars rover photos
# ---------------------------------------------------------------------------

def _rover(name):
    return next((r for r in _rovers_rows() if r["name"].lower() == (name or "").lower()), None)


def get_rover_manifest(rover):
    r = _rover(rover)
    if not r:
        return {"error": f"Rover {rover} not found"}
    photos_for_rover = [p for p in _rover_photos_rows() if p["rover"].lower() == r["name"].lower()]
    by_sol = {}
    for p in photos_for_rover:
        by_sol.setdefault(p["sol"], {"sol": p["sol"], "earth_date": p["earth_date"], "total_photos": 0, "cameras": set()})
        by_sol[p["sol"]]["total_photos"] += 1
        by_sol[p["sol"]]["cameras"].add(p["camera"])
    photos = []
    for sol in sorted(by_sol):
        item = by_sol[sol]
        photos.append({
            "sol": item["sol"],
            "earth_date": item["earth_date"],
            "total_photos": item["total_photos"],
            "cameras": sorted(item["cameras"]),
        })
    return {
        "photo_manifest": {
            "name": r["name"],
            "landing_date": r["landing_date"],
            "launch_date": r["launch_date"],
            "status": r["status"],
            "max_sol": r["max_sol"],
            "max_date": r["max_date"],
            "total_photos": r["total_photos"],
            "photos": photos,
        }
    }


def get_rover_photos(rover, sol=None, camera=None, earth_date=None):
    r = _rover(rover)
    if not r:
        return {"error": f"Rover {rover} not found"}
    photos = [p for p in _rover_photos_rows() if p["rover"].lower() == r["name"].lower()]
    if sol is not None:
        photos = [p for p in photos if p["sol"] == int(sol)]
    if earth_date:
        photos = [p for p in photos if p["earth_date"] == earth_date]
    if camera:
        photos = [p for p in photos if p["camera"].lower() == camera.lower()]
    rover_summary = {
        "name": r["name"],
        "landing_date": r["landing_date"],
        "launch_date": r["launch_date"],
        "status": r["status"],
    }
    result = []
    for p in photos:
        result.append({
            "id": p["id"],
            "sol": p["sol"],
            "camera": {"name": p["camera"], "full_name": p["camera_full_name"]},
            "img_src": p["img_src"],
            "earth_date": p["earth_date"],
            "rover": rover_summary,
        })
    return {"photos": result}


# ---------------------------------------------------------------------------
# NeoWs (Near Earth Objects)
# ---------------------------------------------------------------------------

def _neo_view(n):
    return {
        "id": n["id"],
        "neo_reference_id": n["id"],
        "name": n["name"],
        "absolute_magnitude_h": n["absolute_magnitude_h"],
        "estimated_diameter": {
            "kilometers": {
                "estimated_diameter_min": n["est_diameter_min_km"],
                "estimated_diameter_max": n["est_diameter_max_km"],
            }
        },
        "is_potentially_hazardous_asteroid": n["is_potentially_hazardous"],
        "close_approach_data": [
            {
                "close_approach_date": n["close_approach_date"],
                "relative_velocity": {"kilometers_per_hour": f"{n['relative_velocity_kph']}"},
                "miss_distance": {"kilometers": f"{n['miss_distance_km']}"},
                "orbiting_body": n["orbiting_body"],
            }
        ],
    }


def get_neo_feed(start_date=None, end_date=None):
    lo = start_date or min(n["close_approach_date"] for n in _neos_rows())
    hi = end_date or lo
    matches = [n for n in _neos_rows() if lo <= n["close_approach_date"] <= hi]
    by_date = {}
    for n in matches:
        by_date.setdefault(n["close_approach_date"], []).append(_neo_view(n))
    return {
        "element_count": len(matches),
        "near_earth_objects": by_date,
    }


def get_neo(neo_id):
    n = next((x for x in _neos_rows() if x["id"] == str(neo_id)), None)
    if not n:
        return {"error": f"NEO {neo_id} not found"}
    return _neo_view(n)


# ---------------------------------------------------------------------------
# EPIC
# ---------------------------------------------------------------------------

def get_epic_natural():
    return list(_epic_rows())

_store.eager_load()
