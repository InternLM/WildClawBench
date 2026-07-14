"""FastAPI server wrapping zoom_data module as REST endpoints.

Mirrors a subset of the Zoom API v2: users, meetings, recordings,
registrants. Base path: /v2
"""

from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional

import zoom_data
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

app = FastAPI(title="Zoom API (Mock)", version="v2")
install_tracker(app)
install_admin_plane(app, store=zoom_data._store)
@app.get("/health")
def health():
    return {"status": "ok"}


# --- Users ---

@app.get("/v2/users/me")
def get_me():
    return zoom_data.get_me()


# --- Meetings ---

@app.get("/v2/users/{user_id}/meetings")
def list_meetings(
    user_id: str,
    type: str = "scheduled",
    page_size: int = Query(30, ge=1, le=300),
):
    result = zoom_data.list_meetings(user_id, meeting_type=type, page_size=page_size)
    if isinstance(result, dict) and "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


class MeetingCreateBody(BaseModel):
    topic: str
    type: int = 2
    start_time: Optional[str] = None
    duration: int = 60
    timezone: str = "UTC"
    agenda: Optional[str] = ""


@app.post("/v2/users/{user_id}/meetings", status_code=201)
def create_meeting(user_id: str, body: MeetingCreateBody):
    result = zoom_data.create_meeting(
        user_id,
        topic=body.topic,
        start_time=body.start_time,
        duration=body.duration,
        timezone=body.timezone,
        agenda=body.agenda,
        meeting_type=body.type,
    )
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.get("/v2/meetings/{meeting_id}")
def get_meeting(meeting_id: int):
    result = zoom_data.get_meeting(meeting_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


class MeetingUpdateBody(BaseModel):
    topic: Optional[str] = None
    start_time: Optional[str] = None
    duration: Optional[int] = None
    agenda: Optional[str] = None
    timezone: Optional[str] = None


@app.patch("/v2/meetings/{meeting_id}")
def update_meeting(meeting_id: int, body: MeetingUpdateBody):
    result = zoom_data.update_meeting(
        meeting_id,
        topic=body.topic,
        start_time=body.start_time,
        duration=body.duration,
        agenda=body.agenda,
        timezone=body.timezone,
    )
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.delete("/v2/meetings/{meeting_id}", status_code=204)
def delete_meeting(meeting_id: int):
    result = zoom_data.delete_meeting(meeting_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return JSONResponse(status_code=204, content=None)


# --- Recordings ---

@app.get("/v2/meetings/{meeting_id}/recordings")
def get_recordings(meeting_id: int):
    result = zoom_data.get_recordings(meeting_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Registrants ---

@app.get("/v2/meetings/{meeting_id}/registrants")
def list_registrants(meeting_id: int, status: str = "approved"):
    result = zoom_data.list_registrants(meeting_id, status=status)
    if isinstance(result, dict) and "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result
