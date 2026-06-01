"""Data access module for the NASA Open APIs mock service.

Mirrors a subset of api.nasa.gov: APOD, Mars Rover Photos, NeoWs (NEO feed),
and EPIC natural imagery.
"""

import csv
from copy import deepcopy
from pathlib import Path

DATA_DIR = Path(__file__).parent


def _load(filename):
    with open(DATA_DIR / filename, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


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
            "id": int(r["id"]),
            "rover": r["rover"],
            "sol": int(r["sol"]),
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
            "max_sol": int(r["max_sol"]),
            "max_date": r["max_date"],
            "total_photos": int(r["total_photos"]),
        })
    return out


def _coerce_neos(rows):
    out = []
    for r in rows:
        out.append({
            "id": r["id"],
            "name": r["name"],
            "close_approach_date": r["close_approach_date"],
            "absolute_magnitude_h": float(r["absolute_magnitude_h"]),
            "est_diameter_min_km": float(r["est_diameter_min_km"]),
            "est_diameter_max_km": float(r["est_diameter_max_km"]),
            "is_potentially_hazardous": _to_bool(r["is_potentially_hazardous"]),
            "miss_distance_km": float(r["miss_distance_km"]),
            "relative_velocity_kph": float(r["relative_velocity_kph"]),
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
                "lat": float(r["centroid_lat"]),
                "lon": float(r["centroid_lon"]),
            },
        })
    return out


_apod = _coerce_apod(_load("apod.csv"))
_rover_photos = _coerce_rover_photos(_load("rover_photos.csv"))
_rovers = _coerce_rovers(_load("rovers.csv"))
_neos = _coerce_neos(_load("neos.csv"))
_epic = _coerce_epic(_load("epic.csv"))

_apod_store = deepcopy(_apod)
_rover_photos_store = deepcopy(_rover_photos)
_rovers_store = deepcopy(_rovers)
_neos_store = deepcopy(_neos)
_epic_store = deepcopy(_epic)


# ---------------------------------------------------------------------------
# APOD
# ---------------------------------------------------------------------------

def get_apod(date=None, start_date=None, end_date=None):
    if start_date or end_date:
        lo = start_date or min(a["date"] for a in _apod_store)
        hi = end_date or max(a["date"] for a in _apod_store)
        return [a for a in _apod_store if lo <= a["date"] <= hi]
    if date:
        a = next((x for x in _apod_store if x["date"] == date), None)
        if not a:
            return {"error": f"No APOD entry for {date}"}
        return a
    # latest
    return max(_apod_store, key=lambda x: x["date"])


# ---------------------------------------------------------------------------
# Mars rover photos
# ---------------------------------------------------------------------------

def _rover(name):
    return next((r for r in _rovers_store if r["name"].lower() == (name or "").lower()), None)


def get_rover_manifest(rover):
    r = _rover(rover)
    if not r:
        return {"error": f"Rover {rover} not found"}
    photos_for_rover = [p for p in _rover_photos_store if p["rover"].lower() == r["name"].lower()]
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
    photos = [p for p in _rover_photos_store if p["rover"].lower() == r["name"].lower()]
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
    lo = start_date or min(n["close_approach_date"] for n in _neos_store)
    hi = end_date or lo
    matches = [n for n in _neos_store if lo <= n["close_approach_date"] <= hi]
    by_date = {}
    for n in matches:
        by_date.setdefault(n["close_approach_date"], []).append(_neo_view(n))
    return {
        "element_count": len(matches),
        "near_earth_objects": by_date,
    }


def get_neo(neo_id):
    n = next((x for x in _neos_store if x["id"] == str(neo_id)), None)
    if not n:
        return {"error": f"NEO {neo_id} not found"}
    return _neo_view(n)


# ---------------------------------------------------------------------------
# EPIC
# ---------------------------------------------------------------------------

def get_epic_natural():
    return list(_epic_store)
