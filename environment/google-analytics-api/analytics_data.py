"""Data access module for the Google Analytics (GA4 Data API) mock service.

Holds a per-day event dataset with dimensions (date, country, pagePath,
deviceCategory) and metrics (sessions, activeUsers, screenPageViews,
eventCount). ``run_report`` groups and sums the seed rows by the requested
dimensions and metrics, mimicking the GA4 ``runReport`` response shape.
"""

import csv
from copy import deepcopy
import json
from pathlib import Path

DATA_DIR = Path(__file__).parent

import sys as _sys
_sys.path.insert(0, str(DATA_DIR.parent))
from _mutable_store import read_json_with_ctx, get_store, opt_int  # noqa: E402

_store = get_store("google-analytics-api")
_API = "google-analytics-api"

_store.register("events", primary_key="_pk",
                initial_loader=lambda: [
                    {**r, "_pk": f"{r['date']}@{r['country']}@{r['pagePath']}@{r['deviceCategory']}"}
                    for r in _coerce_events(_load("events.json", "events"))])
_store.register("realtime", primary_key="_pk",
                initial_loader=lambda: [
                    {**r, "_pk": f"{r['country']}@{r['deviceCategory']}@{r['unifiedScreenName']}"}
                    for r in _coerce_realtime(_load("realtime.json", "realtime"))])
_store.register_document("property", initial_loader=lambda: __import__('json').load(open(DATA_DIR / "property.json", encoding="utf-8")))


def _events_rows():
    return [{k: v for k, v in r.items() if k != "_pk"} for r in _store.table("events").rows()]


def _realtime_rows():
    return [{k: v for k, v in r.items() if k != "_pk"} for r in _store.table("realtime").rows()]


def _property_doc():
    return _store.document("property").get()



def _load(filename, table):
    return read_json_with_ctx((DATA_DIR / filename).with_suffix(".json"), _API, table)


def _strip_ctx(r):
    return {k: v for k, v in r.items() if not k.startswith("__")}


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
            row[m] = opt_int(r, m, default=0)
        out.append(row)
    return out


def _coerce_realtime(rows):
    out = []
    for r in rows:
        row = {d: r[d] for d in _REALTIME_DIMENSIONS}
        for m in _REALTIME_METRICS:
            row[m] = opt_int(r, m, default=0)
        out.append(row)
    return out





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
        _events_rows(),
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
        _realtime_rows(),
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
    return deepcopy(_property_doc())

_store.eager_load()
