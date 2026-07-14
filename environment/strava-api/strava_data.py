"""Data access module for the Strava API mock service.

Mirrors a subset of the Strava v3 API: athlete, activities, segments, kudos,
and athlete stats.
"""

import csv
import json
from datetime import datetime, timezone
from pathlib import Path

DATA_DIR = Path(__file__).parent

import sys as _sys
_sys.path.insert(0, str(DATA_DIR.parent))
from _mutable_store import (  # noqa: E402
    read_seed_with_ctx, get_store, opt_int, strict_float, strict_int)

_store = get_store("strava-api")
_API = "strava-api"


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

_store.register("activities", primary_key="id",
                initial_loader=lambda: _coerce_activities(_load("activities.json", "activities")))
_store.register("segments", primary_key="id",
                initial_loader=lambda: _coerce_segments(_load("segments.json", "segments")))
_store.register("kudoers", primary_key="_pk",
                initial_loader=lambda: [{**r, "_pk": f"{r['activity_id']}@{r['athlete_id']}"}
                                        for r in _coerce_kudoers(_load("kudoers.json", "kudoers"))])
_store.register_document("athlete", initial_loader=lambda: __import__('json').load(open(DATA_DIR / "athlete.json", encoding="utf-8")))


def _activities_rows():
    return _store.table("activities").rows()


def _segments_rows():
    return _store.table("segments").rows()


def _kudoers_rows():
    return [{k: v for k, v in r.items() if k != "_pk"} for r in _store.table("kudoers").rows()]


def _athlete_doc():
    return _store.document("athlete").get()



def _load(filename, table):
    return read_seed_with_ctx(DATA_DIR / filename, _API, table)


def _strip_ctx(r):
    return {k: v for k, v in r.items() if not k.startswith("__")}


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
            "id": strict_int(r, "id"),
            "name": r["name"],
            "type": r["type"],
            "sport_type": r["type"],
            "distance": strict_float(r, "distance"),
            "moving_time": strict_int(r, "moving_time"),
            "elapsed_time": strict_int(r, "elapsed_time"),
            "total_elevation_gain": strict_float(r, "total_elevation_gain"),
            "average_speed": strict_float(r, "average_speed"),
            "start_date": r["start_date"],
            "kudos_count": strict_int(r, "kudos_count"),
            "segment_id": opt_int(r, "segment_id", default=None),
        })
    return out


def _coerce_segments(rows):
    out = []
    for r in rows:
        out.append({
            "id": strict_int(r, "id"),
            "name": r["name"],
            "activity_type": r["activity_type"],
            "distance": strict_float(r, "distance"),
            "average_grade": strict_float(r, "average_grade"),
            "maximum_grade": strict_float(r, "maximum_grade"),
            "elevation_high": strict_float(r, "elevation_high"),
            "elevation_low": strict_float(r, "elevation_low"),
            "climb_category": strict_int(r, "climb_category"),
            "city": r["city"],
            "state": r["state"],
        })
    return out


def _coerce_kudoers(rows):
    out = []
    for r in rows:
        out.append({
            "activity_id": strict_int(r, "activity_id"),
            "athlete_id": strict_int(r, "athlete_id"),
            "firstname": r["firstname"],
            "lastname": r["lastname"],
        })
    return out






# ---------------------------------------------------------------------------
# Athlete
# ---------------------------------------------------------------------------

def get_athlete():
    return _athlete_doc()


# ---------------------------------------------------------------------------
# Activities
# ---------------------------------------------------------------------------

def list_activities(before=None, after=None, page=1, per_page=30):
    acts = list(_activities_rows())
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
    a = next((x for x in _activities_rows() if x["id"] == activity_id), None)
    if not a:
        return {"error": f"Activity {activity_id} not found", "errors": [{"resource": "Activity", "code": "not_found"}]}
    out = dict(a)
    out["athlete"] = {"id": _athlete_doc()["id"]}
    return out


def update_activity(activity_id, name=None, type=None):
    for a in _activities_rows():
        if a["id"] == activity_id:
            _changes = {}
            if name is not None:
                _changes["name"] = name
            if type is not None:
                _changes["type"] = type
                _changes["sport_type"] = type
            a.update(_changes)
            _store_patch("activities", a, _changes)
            return get_activity(activity_id)
    return {"error": f"Activity {activity_id} not found", "errors": [{"resource": "Activity", "code": "not_found"}]}


def activity_kudos(activity_id):
    if not any(a["id"] == activity_id for a in _activities_rows()):
        return {"error": f"Activity {activity_id} not found", "errors": [{"resource": "Activity", "code": "not_found"}]}
    return [
        {"firstname": k["firstname"], "lastname": k["lastname"]}
        for k in _kudoers_rows() if k["activity_id"] == activity_id
    ]


# ---------------------------------------------------------------------------
# Segments
# ---------------------------------------------------------------------------

def get_segment(segment_id):
    s = next((x for x in _segments_rows() if x["id"] == segment_id), None)
    if not s:
        return {"error": f"Segment {segment_id} not found", "errors": [{"resource": "Segment", "code": "not_found"}]}
    return s


# ---------------------------------------------------------------------------
# Stats
# ---------------------------------------------------------------------------

def athlete_stats(athlete_id):
    if athlete_id != _athlete_doc()["id"]:
        return {"error": f"Athlete {athlete_id} not found", "errors": [{"resource": "Athlete", "code": "not_found"}]}

    def _totals(act_type):
        acts = [a for a in _activities_rows() if a["type"] == act_type]
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

_store.eager_load()
