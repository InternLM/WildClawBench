"""FastAPI server wrapping google_analytics_data module as REST endpoints.

Implements a subset of the GA4 Analytics Data API (v1beta). Report endpoints
use the ``properties/{id}:method`` colon-suffix convention.
"""

from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

import google_analytics_data
try:
    from tracking_middleware import install_tracker
    from admin_plane import install_admin_plane
except ModuleNotFoundError as _shared_plane_err:  # standalone run without the shared module on sys.path
    import logging as _logging
    _logging.error("SHARED PLANE MISSING - audit + admin disabled: %s", _shared_plane_err)
    def install_tracker(app):  # no-op fallback: audit endpoints disabled
        return None

    def install_admin_plane(app, store=None, one_shot_registry=None):
        return None

app = FastAPI(title="Google Analytics Data API (Mock)", version="v1beta")
install_tracker(app)
install_admin_plane(app, store=google_analytics_data._store)
@app.get("/health")
def health():
    return {"status": "ok"}


# --- Reports ---

class Dimension(BaseModel):
    name: str


class Metric(BaseModel):
    name: str


class DateRange(BaseModel):
    startDate: Optional[str] = None
    endDate: Optional[str] = None
    name: Optional[str] = None


class RunReportBody(BaseModel):
    dimensions: List[Dimension] = []
    metrics: List[Metric] = []
    dateRanges: List[DateRange] = []


@app.post("/v1beta/properties/{property_id}:runReport")
def run_report(property_id: str, body: RunReportBody):
    return google_analytics_data.run_report(
        property_id,
        dimensions=[d.name for d in body.dimensions],
        metrics=[m.name for m in body.metrics],
        date_ranges=[r.model_dump(exclude_none=True) for r in body.dateRanges],
    )


@app.post("/v1beta/properties/{property_id}:runRealtimeReport")
def run_realtime_report(property_id: str, body: RunReportBody):
    return google_analytics_data.run_realtime_report(
        property_id,
        dimensions=[d.name for d in body.dimensions],
        metrics=[m.name for m in body.metrics],
    )


class BatchRunReportsBody(BaseModel):
    requests: List[Dict[str, Any]] = []


@app.post("/v1beta/properties/{property_id}:batchRunReports")
def batch_run_reports(property_id: str, body: BatchRunReportsBody):
    return google_analytics_data.batch_run_reports(property_id, body.requests)


# --- Metadata ---

@app.get("/v1beta/properties/{property_id}/metadata")
def get_metadata(property_id: str):
    return google_analytics_data.get_metadata(property_id)


@app.get("/v1beta/properties/{property_id}")
def get_property(property_id: str):
    return google_analytics_data.get_property()
