"""FastAPI server wrapping strava_data module as REST endpoints.

Implements a subset of the Strava v3 API. Base path: /api/v3
"""

from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional

import strava_data
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

app = FastAPI(title="Strava API (Mock)", version="3")
install_tracker(app)
install_admin_plane(app, store=strava_data._store)
@app.get("/health")
def health():
    return {"status": "ok"}


# --- Athlete ---

@app.get("/api/v3/athlete")
def get_athlete():
    return strava_data.get_athlete()


@app.get("/api/v3/athlete/activities")
def list_activities(
    before: Optional[int] = None,
    after: Optional[int] = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(30, ge=1, le=200),
):
    return strava_data.list_activities(before=before, after=after, page=page, per_page=per_page)


@app.get("/api/v3/athletes/{athlete_id}/stats")
def athlete_stats(athlete_id: int):
    result = strava_data.athlete_stats(athlete_id)
    if isinstance(result, dict) and "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Activities ---

@app.get("/api/v3/activities/{activity_id}")
def get_activity(activity_id: int):
    result = strava_data.get_activity(activity_id)
    if isinstance(result, dict) and "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


class ActivityUpdateBody(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None


@app.put("/api/v3/activities/{activity_id}")
def update_activity(activity_id: int, body: ActivityUpdateBody):
    result = strava_data.update_activity(activity_id, name=body.name, type=body.type)
    if isinstance(result, dict) and "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.get("/api/v3/activities/{activity_id}/kudos")
def activity_kudos(activity_id: int):
    result = strava_data.activity_kudos(activity_id)
    if isinstance(result, dict) and "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Segments ---

@app.get("/api/v3/segments/{segment_id}")
def get_segment(segment_id: int):
    result = strava_data.get_segment(segment_id)
    if isinstance(result, dict) and "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result
