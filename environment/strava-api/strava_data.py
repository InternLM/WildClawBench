"""Data access module for the Strava API mock service.

Mirrors a subset of the Strava v3 API: athlete, activities, segments, kudos,
and athlete stats.
"""

import csv
import json
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path

DATA_DIR = Path(__file__).parent


def _load(filename):
    with open(DATA_DIR / filename, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _epoch(iso):
    """Convert an ISO-8601 Z timestamp to a unix epoch (seconds)."""
    try:
        return datetime.strptime(iso, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc).timestamp()
    except (ValueError, TypeError):
        return 0.0


# ---------------------------------------------------------------------------
# Load + coerce
# ---------------------------------------------------------------------------

def _coerce_activities(rows):
    out = []
    for r in rows:
        out.append({
            "id": int(r["id"]),
            "name": r["name"],
            "type": r["type"],
            "sport_type": r["type"],
            "distance": float(r["distance"]),
            "moving_time": int(r["moving_time"]),
            "elapsed_time": int(r["elapsed_time"]),
            "total_elevation_gain": float(r["total_elevation_gain"]),
            "average_speed": float(r["average_speed"]),
            "start_date": r["start_date"],
            "kudos_count": int(r["kudos_count"]),
            "segment_id": int(r["segment_id"]) if r["segment_id"] else None,
        })
    return out


def _coerce_segments(rows):
    out = []
    for r in rows:
        out.append({
            "id": int(r["id"]),
            "name": r["name"],
            "activity_type": r["activity_type"],
            "distance": float(r["distance"]),
            "average_grade": float(r["average_grade"]),
            "maximum_grade": float(r["maximum_grade"]),
            "elevation_high": float(r["elevation_high"]),
            "elevation_low": float(r["elevation_low"]),
            "climb_category": int(r["climb_category"]),
            "city": r["city"],
            "state": r["state"],
        })
    return out


def _coerce_kudoers(rows):
    out = []
    for r in rows:
        out.append({
            "activity_id": int(r["activity_id"]),
            "athlete_id": int(r["athlete_id"]),
            "firstname": r["firstname"],
            "lastname": r["lastname"],
        })
    return out


_activities = _coerce_activities(_load("activities.csv"))
_segments = _coerce_segments(_load("segments.csv"))
_kudoers = _coerce_kudoers(_load("kudoers.csv"))

with open(DATA_DIR / "athlete.json", encoding="utf-8") as _f:
    _athlete = json.load(_f)

_activities_store = deepcopy(_activities)
_segments_store = deepcopy(_segments)
_kudoers_store = deepcopy(_kudoers)
_athlete_store = deepcopy(_athlete)


# ---------------------------------------------------------------------------
# Athlete
# ---------------------------------------------------------------------------

def get_athlete():
    return _athlete_store


# ---------------------------------------------------------------------------
# Activities
# ---------------------------------------------------------------------------

def list_activities(before=None, after=None, page=1, per_page=30):
    acts = list(_activities_store)
    if before is not None:
        acts = [a for a in acts if _epoch(a["start_date"]) <= float(before)]
    if after is not None:
        acts = [a for a in acts if _epoch(a["start_date"]) >= float(after)]
    acts.sort(key=lambda a: a["start_date"], reverse=True)
    page = max(1, page)
    per_page = max(1, per_page)
    start = (page - 1) * per_page
    return acts[start: start + per_page]


def get_activity(activity_id):
    a = next((x for x in _activities_store if x["id"] == activity_id), None)
    if not a:
        return {"error": f"Activity {activity_id} not found", "errors": [{"resource": "Activity", "code": "not_found"}]}
    out = dict(a)
    out["athlete"] = {"id": _athlete_store["id"]}
    return out


def update_activity(activity_id, name=None, type=None):
    for i, a in enumerate(_activities_store):
        if a["id"] == activity_id:
            if name is not None:
                _activities_store[i]["name"] = name
            if type is not None:
                _activities_store[i]["type"] = type
                _activities_store[i]["sport_type"] = type
            return get_activity(activity_id)
    return {"error": f"Activity {activity_id} not found", "errors": [{"resource": "Activity", "code": "not_found"}]}


def activity_kudos(activity_id):
    if not any(a["id"] == activity_id for a in _activities_store):
        return {"error": f"Activity {activity_id} not found", "errors": [{"resource": "Activity", "code": "not_found"}]}
    return [
        {"firstname": k["firstname"], "lastname": k["lastname"]}
        for k in _kudoers_store if k["activity_id"] == activity_id
    ]


# ---------------------------------------------------------------------------
# Segments
# ---------------------------------------------------------------------------

def get_segment(segment_id):
    s = next((x for x in _segments_store if x["id"] == segment_id), None)
    if not s:
        return {"error": f"Segment {segment_id} not found", "errors": [{"resource": "Segment", "code": "not_found"}]}
    return s


# ---------------------------------------------------------------------------
# Stats
# ---------------------------------------------------------------------------

def athlete_stats(athlete_id):
    if athlete_id != _athlete_store["id"]:
        return {"error": f"Athlete {athlete_id} not found", "errors": [{"resource": "Athlete", "code": "not_found"}]}

    def _totals(act_type):
        acts = [a for a in _activities_store if a["type"] == act_type]
        return {
            "count": len(acts),
            "distance": round(sum(a["distance"] for a in acts), 1),
            "moving_time": sum(a["moving_time"] for a in acts),
            "elevation_gain": round(sum(a["total_elevation_gain"] for a in acts), 1),
        }

    return {
        "all_run_totals": _totals("Run"),
        "all_ride_totals": _totals("Ride"),
        "all_swim_totals": _totals("Swim"),
    }
