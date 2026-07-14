"""FastAPI server wrapping mixpanel_data module as REST endpoints.

Implements a subset of the Mixpanel ingestion + query API surface.
"""

from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any

import mixpanel_data
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

app = FastAPI(title="Mixpanel API (Mock)", version="2.0.0")
install_tracker(app)
install_admin_plane(app, store=mixpanel_data._store)
@app.get("/health")
def health():
    return {"status": "ok"}


# --- Ingestion ---

class TrackBody(BaseModel):
    event: str
    distinct_id: Optional[str] = None
    time: Optional[str] = None
    properties: Optional[Dict[str, Any]] = None


@app.post("/track")
def track(body: TrackBody):
    result = mixpanel_data.track(
        event=body.event,
        distinct_id=body.distinct_id,
        time=body.time,
        properties=body.properties,
    )
    if "error" in result:
        return JSONResponse(status_code=400, content=result)
    return result


# --- Events ---

@app.get("/api/2.0/events")
def events(
    event: Optional[str] = None,
    from_date: Optional[str] = Query(None),
    to_date: Optional[str] = Query(None),
):
    return mixpanel_data.events_counts(event=event, from_date=from_date, to_date=to_date)


# --- Funnels ---

@app.get("/api/2.0/funnels/list")
def funnels_list():
    return mixpanel_data.funnels_list()


@app.get("/api/2.0/funnels")
def funnel(funnel_id: int = Query(...)):
    result = mixpanel_data.funnel(funnel_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Segmentation ---

@app.get("/api/2.0/segmentation")
def segmentation(
    event: str = Query(...),
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    on: Optional[str] = None,
):
    result = mixpanel_data.segmentation(event=event, from_date=from_date, to_date=to_date, on=on)
    if "error" in result:
        return JSONResponse(status_code=400, content=result)
    return result


# --- Engage (profiles) ---

@app.get("/api/2.0/engage")
def engage(
    distinct_id: Optional[str] = None,
    where: Optional[str] = None,
    page_size: int = Query(50, ge=1, le=200),
):
    return mixpanel_data.engage(distinct_id=distinct_id, where=where, page_size=page_size)
