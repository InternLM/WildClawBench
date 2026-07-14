"""Data access module for the Mixpanel API mock service.

Mirrors a subset of Mixpanel's ingestion + query surface: /track, events counts,
funnels, segmentation, and engage (user profiles).
"""

import csv
import uuid
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

DATA_DIR = Path(__file__).parent

import sys as _sys
_sys.path.insert(0, str(DATA_DIR.parent))
from _mutable_store import (  # noqa: E402
    read_seed_with_ctx, get_store,
    strict_int,
)

_store = get_store("mixpanel-api")
_API = "mixpanel-api"


def _store_insert(_table, _row):
    """Persist a newly-created row into the shared store (drift/injection-safe).

    Synthesizes the table's registered primary key from the row's ``id`` field
    when the row doesn't already carry it, so creates work regardless of whether
    the table was registered with primary_key="id" or a domain-specific key.
    """
    _t = _store.table(_table)
    if _t.primary_key not in _row and "id" in _row:
        _row = {**_row, _t.primary_key: _row["id"]}
    return _t.upsert(_row)

_store.register("events", primary_key="event_id",
                initial_loader=lambda: _coerce_events(_load("events.json", "events")))
_store.register_document("funnels", initial_loader=lambda: _coerce_funnels(_load("funnels.json", "funnels")))
_store.register("profiles", primary_key="distinct_id",
                initial_loader=lambda: _coerce_profiles(_load("profiles.json", "profiles")))


def _events_rows():
    return _store.table("events").rows()


def _funnels_doc():
    return _store.document("funnels").get()


def _profiles_rows():
    return _store.table("profiles").rows()



def _load(filename, table):
    return read_seed_with_ctx(DATA_DIR / filename, _API, table)


def _strip_ctx(r):
    return {k: v for k, v in r.items() if not k.startswith("__")}


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
            "order": strict_int(r, "step_order"),
            "event": r["step_event"],
            "count": strict_int(r, "count"),
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
                "total_events": strict_int(r, "total_events"),
                "$last_seen": r["last_seen"],
            },
        })
    return out








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
    _store_insert("events", record)
    return {"status": 1, "event_id": record["event_id"]}


# ---------------------------------------------------------------------------
# Events query (counts per day)
# ---------------------------------------------------------------------------

def events_counts(event=None, from_date=None, to_date=None):
    wanted = set()
    if event:
        wanted = {e.strip() for e in event.split(",") if e.strip()}
    series = sorted({_day(e["time"]) for e in _events_rows()
                     if _in_range(e["time"], from_date, to_date)})
    names = wanted or {e["event"] for e in _events_rows()}
    values = {}
    for name in names:
        per_day = {d: 0 for d in series}
        for e in _events_rows():
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
        for f in sorted(_funnels_doc().values(), key=lambda x: x["funnel_id"])
    ]


def funnel(funnel_id):
    f = _funnels_doc().get(str(funnel_id))
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
    series = sorted({_day(e["time"]) for e in _events_rows()
                     if e["event"] == event and _in_range(e["time"], from_date, to_date)})
    values = defaultdict(lambda: {d: 0 for d in series})
    for e in _events_rows():
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
    results = list(_profiles_rows())
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

_store.eager_load()
