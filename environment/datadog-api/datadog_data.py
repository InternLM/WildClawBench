"""Data access module for the Datadog API mock service."""

import csv
import math
import time
import uuid
from copy import deepcopy
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).parent


def _load(filename):
    with open(DATA_DIR / filename, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


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
            **r,
            "id": int(r["id"]),
            "priority": int(r["priority"]),
            "tags": _split_tags(r["tags"]),
        })
    return out


def _coerce_dashboards(rows):
    out = []
    for r in rows:
        out.append({
            **r,
            "widget_count": int(r["widget_count"]),
            "is_read_only": _to_bool(r["is_read_only"]),
        })
    return out


def _coerce_events(rows):
    out = []
    for r in rows:
        out.append({
            **r,
            "id": int(r["id"]),
            "tags": _split_tags(r["tags"]),
            "date_happened": int(r["date_happened"]),
        })
    return out


def _coerce_hosts(rows):
    out = []
    for r in rows:
        out.append({
            **r,
            "up": _to_bool(r["up"]),
            "apps": _split_tags(r["apps"]),
            "cpu_pct": float(r["cpu_pct"]),
            "mem_pct": float(r["mem_pct"]),
            "last_reported": int(r["last_reported"]),
        })
    return out


def _coerce_metrics(rows):
    out = []
    for r in rows:
        out.append({
            **r,
            "base_value": float(r["base_value"]),
            "amplitude": float(r["amplitude"]),
        })
    return out


_monitors = _coerce_monitors(_load("monitors.csv"))
_dashboards = _coerce_dashboards(_load("dashboards.csv"))
_events = _coerce_events(_load("events.csv"))
_hosts = _coerce_hosts(_load("hosts.csv"))
_metrics = _coerce_metrics(_load("metrics.csv"))

_monitors_store = deepcopy(_monitors)
_dashboards_store = deepcopy(_dashboards)
_events_store = deepcopy(_events)
_hosts_store = deepcopy(_hosts)
_metrics_store = deepcopy(_metrics)


# ---------------------------------------------------------------------------
# Metrics query
# ---------------------------------------------------------------------------

def _match_metric(query):
    """Find the seeded metric whose metric name appears in the query string."""
    for m in _metrics_store:
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
    results = list(_monitors_store)
    if overall_state:
        results = [m for m in results if m["overall_state"] == overall_state]
    return results


def get_monitor(monitor_id):
    for m in _monitors_store:
        if str(m["id"]) == str(monitor_id):
            return m
    return {"error": f"Monitor {monitor_id} not found"}


def create_monitor(name, mtype, query, message="", priority=3, tags=None):
    monitor = {
        "id": max((m["id"] for m in _monitors_store), default=0) + 1,
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
    _monitors_store.append(monitor)
    return monitor


def update_monitor(monitor_id, name=None, query=None, message=None,
                   overall_state=None, priority=None, tags=None):
    for idx, m in enumerate(_monitors_store):
        if str(m["id"]) == str(monitor_id):
            if name is not None:
                _monitors_store[idx]["name"] = name
            if query is not None:
                _monitors_store[idx]["query"] = query
            if message is not None:
                _monitors_store[idx]["message"] = message
            if overall_state is not None:
                _monitors_store[idx]["overall_state"] = overall_state
            if priority is not None:
                _monitors_store[idx]["priority"] = priority
            if tags is not None:
                _monitors_store[idx]["tags"] = tags
            _monitors_store[idx]["modified"] = _now_iso()
            return _monitors_store[idx]
    return {"error": f"Monitor {monitor_id} not found"}


# ---------------------------------------------------------------------------
# Dashboards
# ---------------------------------------------------------------------------

def list_dashboards():
    return {"dashboards": list(_dashboards_store)}


def get_dashboard(dashboard_id):
    for d in _dashboards_store:
        if d["id"] == dashboard_id:
            return d
    return {"error": f"Dashboard {dashboard_id} not found"}


# ---------------------------------------------------------------------------
# Events
# ---------------------------------------------------------------------------

def list_events(start=None, end=None):
    results = list(_events_store)
    if start is not None:
        results = [e for e in results if e["date_happened"] >= int(start)]
    if end is not None:
        results = [e for e in results if e["date_happened"] <= int(end)]
    results.sort(key=lambda e: e["date_happened"], reverse=True)
    return {"events": results}


def create_event(title, text, alert_type="info", priority="normal", host=None, tags=None):
    event = {
        "id": max((e["id"] for e in _events_store), default=0) + 1,
        "title": title,
        "text": text,
        "alert_type": alert_type,
        "priority": priority,
        "host": host or "",
        "tags": tags or [],
        "date_happened": int(time.time()),
    }
    _events_store.append(event)
    return {"status": "ok", "event": event}


# ---------------------------------------------------------------------------
# Hosts
# ---------------------------------------------------------------------------

def list_hosts():
    return {"host_list": list(_hosts_store), "total_returned": len(_hosts_store)}
