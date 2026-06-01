"""Data access module for the Mixpanel API mock service.

Mirrors a subset of Mixpanel's ingestion + query surface: /track, events counts,
funnels, segmentation, and engage (user profiles).
"""

import csv
import uuid
from collections import defaultdict
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path

DATA_DIR = Path(__file__).parent


def _load(filename):
    with open(DATA_DIR / filename, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _to_bool(v):
    return str(v).strip().lower() == "true"


# ---------------------------------------------------------------------------
# Load + coerce
# ---------------------------------------------------------------------------

def _coerce_events(rows):
    out = []
    for r in rows:
        props = {k: r[k] for k in ("country", "plan", "platform", "utm_source") if r.get(k)}
        out.append({
            "event_id": r["event_id"],
            "event": r["event"],
            "distinct_id": r["distinct_id"],
            "time": r["time"],
            "properties": props,
        })
    return out


def _coerce_funnels(rows):
    # Group rows into funnels with ordered steps.
    grouped = {}
    for r in rows:
        fid = r["funnel_id"]
        f = grouped.setdefault(fid, {"funnel_id": fid, "name": r["name"], "steps": []})
        f["steps"].append({
            "order": int(r["step_order"]),
            "event": r["step_event"],
            "count": int(r["count"]),
        })
    for f in grouped.values():
        f["steps"].sort(key=lambda s: s["order"])
    return grouped


def _coerce_profiles(rows):
    out = []
    for r in rows:
        out.append({
            "distinct_id": r["distinct_id"],
            "properties": {
                "$name": r["name"],
                "$email": r["email"],
                "country": r["country"],
                "plan": r["plan"],
                "total_events": int(r["total_events"]),
                "$last_seen": r["last_seen"],
            },
        })
    return out


_events = _coerce_events(_load("events.csv"))
_funnels = _coerce_funnels(_load("funnels.csv"))
_profiles = _coerce_profiles(_load("profiles.csv"))

_events_store = deepcopy(_events)
_funnels_store = deepcopy(_funnels)
_profiles_store = deepcopy(_profiles)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _day(ts):
    # Return the YYYY-MM-DD portion of an ISO timestamp.
    return (ts or "")[:10]


def _in_range(ts, from_date, to_date):
    d = _day(ts)
    if from_date and d < from_date:
        return False
    if to_date and d > to_date:
        return False
    return True


# ---------------------------------------------------------------------------
# Ingestion
# ---------------------------------------------------------------------------

def track(event, distinct_id, time=None, properties=None):
    if not event:
        return {"error": "event name is required", "status": 0}
    record = {
        "event_id": f"evt-{uuid.uuid4().hex[:8]}",
        "event": event,
        "distinct_id": distinct_id or "anonymous",
        "time": time or _now(),
        "properties": dict(properties or {}),
    }
    _events_store.append(record)
    return {"status": 1, "event_id": record["event_id"]}


# ---------------------------------------------------------------------------
# Events query (counts per day)
# ---------------------------------------------------------------------------

def events_counts(event=None, from_date=None, to_date=None):
    wanted = set()
    if event:
        wanted = {e.strip() for e in event.split(",") if e.strip()}
    series = sorted({_day(e["time"]) for e in _events_store
                     if _in_range(e["time"], from_date, to_date)})
    names = wanted or {e["event"] for e in _events_store}
    values = {}
    for name in names:
        per_day = {d: 0 for d in series}
        for e in _events_store:
            if e["event"] != name:
                continue
            if not _in_range(e["time"], from_date, to_date):
                continue
            per_day[_day(e["time"])] += 1
        values[name] = per_day
    return {
        "data": {"series": series, "values": values},
        "legend_size": len(values),
    }


# ---------------------------------------------------------------------------
# Funnels
# ---------------------------------------------------------------------------

def funnels_list():
    return [
        {"funnel_id": int(f["funnel_id"]), "name": f["name"]}
        for f in sorted(_funnels_store.values(), key=lambda x: x["funnel_id"])
    ]


def funnel(funnel_id):
    f = _funnels_store.get(str(funnel_id))
    if not f:
        return {"error": f"Funnel {funnel_id} not found"}
    steps = f["steps"]
    top = steps[0]["count"] if steps else 0
    out_steps = []
    prev = None
    for s in steps:
        step_conv = round(s["count"] / prev, 4) if prev else 1.0
        overall = round(s["count"] / top, 4) if top else 0.0
        out_steps.append({
            "step_label": s["event"],
            "event": s["event"],
            "count": s["count"],
            "step_conv_ratio": step_conv,
            "overall_conv_ratio": overall,
        })
        prev = s["count"]
    return {
        "funnel_id": int(f["funnel_id"]),
        "name": f["name"],
        "steps": out_steps,
        "analysis": {
            "completion": out_steps[-1]["count"] if out_steps else 0,
            "starting_amount": top,
            "conversion": out_steps[-1]["overall_conv_ratio"] if out_steps else 0.0,
        },
    }


# ---------------------------------------------------------------------------
# Segmentation
# ---------------------------------------------------------------------------

def segmentation(event=None, from_date=None, to_date=None, on=None):
    if not event:
        return {"error": "event is required"}
    prop = (on or "").strip() or None
    series = sorted({_day(e["time"]) for e in _events_store
                     if e["event"] == event and _in_range(e["time"], from_date, to_date)})
    values = defaultdict(lambda: {d: 0 for d in series})
    for e in _events_store:
        if e["event"] != event:
            continue
        if not _in_range(e["time"], from_date, to_date):
            continue
        bucket = e["properties"].get(prop, "$none") if prop else event
        values[bucket][_day(e["time"])] += 1
    return {"data": {"series": series, "values": {k: dict(v) for k, v in values.items()}}}


# ---------------------------------------------------------------------------
# Engage (user profiles)
# ---------------------------------------------------------------------------

def engage(distinct_id=None, where=None, page_size=50):
    results = list(_profiles_store)
    if distinct_id:
        results = [p for p in results if p["distinct_id"] == distinct_id]
    if where:
        # where is a simple "prop==value" expression on a profile property.
        if "==" in where:
            key, _, val = where.partition("==")
            key = key.strip()
            val = val.strip().strip('"')
            results = [p for p in results if str(p["properties"].get(key)) == val]
    results = results[: max(1, page_size)]
    return {
        "results": results,
        "page": 0,
        "page_size": page_size,
        "total": len(results),
    }
