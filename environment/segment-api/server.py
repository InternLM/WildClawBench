"""FastAPI server wrapping segment_data module as REST endpoints.

Mirrors a subset of Segment's HTTP Tracking API (track, identify, page, batch)
plus read-only convenience endpoints for events, sources, and destinations.
"""

from fastapi import FastAPI, Query, Body
from fastapi.responses import JSONResponse
from typing import Optional

import segment_data
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

app = FastAPI(title="Segment API (Mock)", version="v1")
install_tracker(app)
install_admin_plane(app, store=segment_data._store)
@app.get("/health")
def health():
    return {"status": "ok"}


# --- Tracking API (writes) ---

@app.post("/v1/track")
def track(body: dict = Body(...)):
    return segment_data.track(body)


@app.post("/v1/identify")
def identify(body: dict = Body(...)):
    return segment_data.identify(body)


@app.post("/v1/page")
def page(body: dict = Body(...)):
    return segment_data.page(body)


@app.post("/v1/batch")
def batch(body: dict = Body(...)):
    return segment_data.batch(body)


# --- Read-only convenience endpoints ---

@app.get("/v1/events")
def list_events(
    type: Optional[str] = Query(None),
    userId: Optional[str] = Query(None),
):
    return segment_data.list_events(event_type=type, user_id=userId)


@app.get("/v1/sources")
def list_sources():
    return segment_data.list_sources()


@app.get("/v1/destinations")
def list_destinations():
    return segment_data.list_destinations()
