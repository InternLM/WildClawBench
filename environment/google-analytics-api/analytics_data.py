"""Data access module for the Google Analytics (GA4 Data API) mock service.

Holds a per-day event dataset with dimensions (date, country, pagePath,
deviceCategory) and metrics (sessions, activeUsers, screenPageViews,
eventCount). ``run_report`` groups and sums the seed rows by the requested
dimensions and metrics, mimicking the GA4 ``runReport`` response shape.
"""

import csv
import json
from copy import deepcopy
from pathlib import Path

DATA_DIR = Path(__file__).parent


def _load(filename):
    with open(DATA_DIR / filename, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _to_int(v, default=0):
    try:
        return int(v)
    except (TypeError, ValueError):
        return default


# ---------------------------------------------------------------------------
# Known dimensions / metrics
# ---------------------------------------------------------------------------

_DIMENSIONS = ["date", "country", "pagePath", "deviceCategory"]
_REALTIME_DIMENSIONS = ["country", "deviceCategory", "unifiedScreenName"]
_METRICS = ["sessions", "activeUsers", "screenPageViews", "eventCount"]
_REALTIME_METRICS = ["activeUsers", "eventCount"]


def _coerce_events(rows):
    out = []
    for r in rows:
        row = {d: r[d] for d in _DIMENSIONS}
        for m in _METRICS:
            row[m] = _to_int(r[m])
        out.append(row)
    return out


def _coerce_realtime(rows):
    out = []
    for r in rows:
        row = {d: r[d] for d in _REALTIME_DIMENSIONS}
        for m in _REALTIME_METRICS:
            row[m] = _to_int(r[m])
        out.append(row)
    return out


_events = _coerce_events(_load("events.csv"))
_realtime = _coerce_realtime(_load("realtime.csv"))

with open(DATA_DIR / "property.json", encoding="utf-8") as _f:
    _property = json.load(_f)

_events_store = deepcopy(_events)
_realtime_store = deepcopy(_realtime)
_property_store = deepcopy(_property)


# ---------------------------------------------------------------------------
# Aggregation helpers
# ---------------------------------------------------------------------------

def _aggregate(source_rows, dimensions, metrics, available_dims, available_metrics):
    dims = [d for d in dimensions if d in available_dims]
    mets = [m for m in metrics if m in available_metrics]
    if not mets:
        mets = [available_metrics[0]]

    grouped = {}
    order = []
    for row in source_rows:
        key = tuple(row.get(d, "") for d in dims)
        if key not in grouped:
            grouped[key] = {m: 0 for m in mets}
            order.append(key)
        for m in mets:
            grouped[key][m] += _to_int(row.get(m, 0))

    rows = []
    for key in order:
        rows.append({
            "dimensionValues": [{"value": v} for v in key],
            "metricValues": [{"value": str(grouped[key][m])} for m in mets],
        })

    return {
        "dimensionHeaders": [{"name": d} for d in dims],
        "metricHeaders": [{"name": m, "type": "TYPE_INTEGER"} for m in mets],
        "rows": rows,
        "rowCount": len(rows),
    }


# ---------------------------------------------------------------------------
# Reports
# ---------------------------------------------------------------------------

def run_report(property_id, dimensions=None, metrics=None, date_ranges=None):
    report = _aggregate(
        _events_store,
        dimensions or [],
        metrics or [],
        _DIMENSIONS,
        _METRICS,
    )
    report["kind"] = "analyticsData#runReport"
    if date_ranges:
        report["metadata"] = {"dateRanges": date_ranges}
    return report


def run_realtime_report(property_id, dimensions=None, metrics=None):
    report = _aggregate(
        _realtime_store,
        dimensions or [],
        metrics or [],
        _REALTIME_DIMENSIONS,
        _REALTIME_METRICS,
    )
    report["kind"] = "analyticsData#runRealtimeReport"
    return report


def _names(items):
    """Normalize a list of dimension/metric specs to a list of name strings.

    Accepts either ``["country"]`` or ``[{"name": "country"}]``.
    """
    out = []
    for item in items or []:
        if isinstance(item, dict):
            name = item.get("name")
            if name:
                out.append(name)
        elif item:
            out.append(item)
    return out


def batch_run_reports(property_id, requests):
    reports = []
    for req in requests or []:
        reports.append(run_report(
            property_id,
            dimensions=_names(req.get("dimensions")),
            metrics=_names(req.get("metrics")),
            date_ranges=req.get("dateRanges"),
        ))
    return {"kind": "analyticsData#batchRunReports", "reports": reports}


def get_metadata(property_id):
    return {
        "name": f"properties/{property_id}/metadata",
        "dimensions": [
            {"apiName": d, "uiName": d, "category": "Page / Screen" if d == "pagePath" else "General"}
            for d in _DIMENSIONS
        ],
        "metrics": [
            {"apiName": m, "uiName": m, "type": "TYPE_INTEGER"}
            for m in _METRICS
        ],
    }


def get_property():
    return deepcopy(_property_store)
