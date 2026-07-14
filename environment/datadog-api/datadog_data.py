"""Data access module for the Datadog API mock service."""

import csv
import math
import time
import uuid
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).parent

import sys as _sys
_sys.path.insert(0, str(DATA_DIR.parent))
from _mutable_store import (  # noqa: E402
    read_seed_with_ctx, get_store,
    strict_int,
    strict_float,
    strict_bool,
)

_store = get_store("datadog-api")
_API = "datadog-api"



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

_store.register("monitors", primary_key="id",
                initial_loader=lambda: _coerce_monitors(_load("monitors.json", "monitors")))
_store.register("dashboards", primary_key="id",
                initial_loader=lambda: _coerce_dashboards(_load("dashboards.json", "dashboards")))
_store.register("events", primary_key="id",
                initial_loader=lambda: _coerce_events(_load("events.json", "events")))
_store.register("hosts", primary_key="name",
                initial_loader=lambda: _coerce_hosts(_load("hosts.json", "hosts")))
_store.register("metrics", primary_key="_pk",
                initial_loader=lambda: _coerce_metrics(_load("metrics.json", "metrics")))


def _monitors_rows():
    return _store.table("monitors").rows()


def _dashboards_rows():
    return _store.table("dashboards").rows()


def _events_rows():
    return _store.table("events").rows()


def _hosts_rows():
    return _store.table("hosts").rows()


def _metrics_rows():
    return _store.table("metrics").rows()



def _load(filename, table):
    return read_seed_with_ctx(DATA_DIR / filename, _API, table)


def _strip_ctx(r):
    return {k: v for k, v in r.items() if not k.startswith("__")}


def _now_iso():
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S+00:00")


def _to_bool(v):
    return str(v).strip().lower() == "true"


def _split_tags(v):
    return [t for t in v.split(";") if t]


# ---------------------------------------------------------------------------
# Load + coerce
# ---------------------------------------------------------------------------

def _coerce_monitors(rows):
    out = []
    for r in rows:
        out.append({
            **_strip_ctx(r),
            "id": strict_int(r, "id"),
            "priority": strict_int(r, "priority"),
            "tags": _split_tags(r["tags"]),
        })
    return out


def _coerce_dashboards(rows):
    out = []
    for r in rows:
        out.append({
            **_strip_ctx(r),
            "widget_count": strict_int(r, "widget_count"),
            "is_read_only": strict_bool(r, "is_read_only"),
        })
    return out


def _coerce_events(rows):
    out = []
    for r in rows:
        out.append({
            **_strip_ctx(r),
            "id": strict_int(r, "id"),
            "tags": _split_tags(r["tags"]),
            "date_happened": strict_int(r, "date_happened"),
        })
    return out


def _coerce_hosts(rows):
    out = []
    for r in rows:
        out.append({
            **_strip_ctx(r),
            "up": strict_bool(r, "up"),
            "apps": _split_tags(r["apps"]),
            "cpu_pct": strict_float(r, "cpu_pct"),
            "mem_pct": strict_float(r, "mem_pct"),
            "last_reported": strict_int(r, "last_reported"),
        })
    return out


def _coerce_metrics(rows):
    out = []
    for r in rows:
        clean = _strip_ctx(r)
        tags = clean.get("tags") or []
        if isinstance(tags, str):
            tags = _split_tags(tags)
        tag_string = ",".join(sorted(tags))
        out.append({
            **clean,
            "tags": tags,
            "_pk": f"{clean['metric']}|{tag_string}",
            "base_value": strict_float(r, "base_value"),
            "amplitude": strict_float(r, "amplitude"),
        })
    return out












# ---------------------------------------------------------------------------
# Metrics query
# ---------------------------------------------------------------------------

def _match_metric(query):
    """Find the seeded metric whose metric name appears in the query string."""
    for m in _metrics_rows():
        if m["metric"] in query:
            return m
    return None


def query_metrics(from_ts, to_ts, query):
    try:
        from_ts = int(from_ts)
        to_ts = int(to_ts)
    except (TypeError, ValueError):
        return {"status": "error", "error": "from and to must be unix timestamps"}
    if to_ts <= from_ts:
        return {"status": "error", "error": "to must be greater than from"}

    metric = _match_metric(query)
    if not metric:
        return {
            "status": "ok",
            "query": query,
            "from_date": from_ts * 1000,
            "to_date": to_ts * 1000,
            "series": [],
        }

    # Build a deterministic sine-shaped series across the window.
    step = max(60, (to_ts - from_ts) // 20)
    pointlist = []
    t = from_ts
    idx = 0
    while t <= to_ts:
        wave = math.sin(idx / 3.0)
        value = round(metric["base_value"] + metric["amplitude"] * wave, 4)
        pointlist.append([t * 1000, value])
        t += step
        idx += 1

    return {
        "status": "ok",
        "query": query,
        "from_date": from_ts * 1000,
        "to_date": to_ts * 1000,
        "series": [{
            "metric": metric["metric"],
            "scope": metric["scope"],
            "unit": metric["unit"],
            "interval": step,
            "length": len(pointlist),
            "pointlist": pointlist,
        }],
    }


# ---------------------------------------------------------------------------
# Monitors
# ---------------------------------------------------------------------------

def list_monitors(overall_state=None):
    results = list(_monitors_rows())
    if overall_state:
        results = [m for m in results if m["overall_state"] == overall_state]
    return results


def get_monitor(monitor_id):
    for m in _monitors_rows():
        if str(m["id"]) == str(monitor_id):
            return m
    return {"error": f"Monitor {monitor_id} not found"}


def create_monitor(name, mtype, query, message="", priority=3, tags=None):
    monitor = {
        "id": max((m["id"] for m in _monitors_rows()), default=0) + 1,
        "name": name,
        "type": mtype,
        "query": query,
        "message": message or "",
        "overall_state": "OK",
        "priority": priority,
        "tags": tags or [],
        "created": _now_iso(),
        "modified": _now_iso(),
    }
    _store_insert("monitors", monitor)
    return monitor


def update_monitor(monitor_id, name=None, query=None, message=None,
                   overall_state=None, priority=None, tags=None):
    for m in _monitors_rows():
        if str(m["id"]) == str(monitor_id):
            _changes = {}
            if name is not None:
                _changes["name"] = name
            if query is not None:
                _changes["query"] = query
            if message is not None:
                _changes["message"] = message
            if overall_state is not None:
                _changes["overall_state"] = overall_state
            if priority is not None:
                _changes["priority"] = priority
            if tags is not None:
                _changes["tags"] = tags
            _changes["modified"] = _now_iso()
            m.update(_changes)
            _store_patch("monitors", m, _changes)
            return m
    return {"error": f"Monitor {monitor_id} not found"}


# ---------------------------------------------------------------------------
# Dashboards
# ---------------------------------------------------------------------------

def list_dashboards():
    return {"dashboards": list(_dashboards_rows())}


def get_dashboard(dashboard_id):
    for d in _dashboards_rows():
        if d["id"] == dashboard_id:
            return d
    return {"error": f"Dashboard {dashboard_id} not found"}


# ---------------------------------------------------------------------------
# Events
# ---------------------------------------------------------------------------

def list_events(start=None, end=None):
    results = list(_events_rows())
    if start is not None:
        results = [e for e in results if e["date_happened"] >= int(start)]
    if end is not None:
        results = [e for e in results if e["date_happened"] <= int(end)]
    results.sort(key=lambda e: e["date_happened"], reverse=True)
    return {"events": results}


def create_event(title, text, alert_type="info", priority="normal", host=None, tags=None):
    event = {
        "id": max((e["id"] for e in _events_rows()), default=0) + 1,
        "title": title,
        "text": text,
        "alert_type": alert_type,
        "priority": priority,
        "host": host or "",
        "tags": tags or [],
        "date_happened": int(time.time()),
    }
    _store_insert("events", event)
    return {"status": "ok", "event": event}


# ---------------------------------------------------------------------------
# Hosts
# ---------------------------------------------------------------------------

def list_hosts():
    return {"host_list": list(_hosts_rows()), "total_returned": len(_hosts_rows())}

_store.eager_load()
