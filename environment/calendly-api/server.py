"""FastAPI server wrapping calendly_data module as REST endpoints.

Mirrors a subset of the Calendly API v2 surface.
"""

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any

import calendly_data
try:
    from tracking_middleware import install_tracker
except ModuleNotFoundError:  # standalone run without the shared module on sys.path
    def install_tracker(app):  # no-op fallback: audit endpoints disabled
        return None

app = FastAPI(title="Calendly API (Mock)", version="v2")
install_tracker(app)


@app.get("/health")
def health():
    return {"status": "ok"}


# --- Users ---

@app.get("/users/me")
def get_me():
    return calendly_data.get_me()


# --- Event types ---

@app.get("/event_types")
def list_event_types(user: Optional[str] = None):
    return calendly_data.list_event_types(user=user)


@app.get("/event_types/{uuid}")
def get_event_type(uuid: str):
    result = calendly_data.get_event_type(uuid)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Scheduled events ---

@app.get("/scheduled_events")
def list_scheduled_events(user: Optional[str] = None, status: Optional[str] = None):
    return calendly_data.list_scheduled_events(user=user, status=status)


@app.get("/scheduled_events/{uuid}")
def get_scheduled_event(uuid: str):
    result = calendly_data.get_scheduled_event(uuid)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.get("/scheduled_events/{uuid}/invitees")
def list_invitees(uuid: str):
    result = calendly_data.list_invitees(uuid)
    if isinstance(result, dict) and "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


class BookBody(BaseModel):
    event_type: str
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    location_type: Optional[str] = "zoom"
    location: Optional[str] = ""
    invitee: Optional[Dict[str, Any]] = None


@app.post("/scheduled_events", status_code=201)
def book_event(body: BookBody):
    result = calendly_data.book_event(body.model_dump(exclude_none=True))
    if isinstance(result, dict) and "error" in result:
        return JSONResponse(status_code=400, content=result)
    return result


class CancelBody(BaseModel):
    reason: Optional[str] = None


@app.post("/scheduled_events/{uuid}/cancellation")
def cancel_event(uuid: str, body: CancelBody):
    result = calendly_data.cancel_event(uuid, reason=body.reason)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result
