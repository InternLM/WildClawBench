"""FastAPI server wrapping calendar_data module as REST endpoints.

Mirrors the Google Calendar API v3 surface (subset).
"""

from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

import calendar_data
try:
    from tracking_middleware import install_tracker
except ModuleNotFoundError:  # standalone run without the shared module on sys.path
    def install_tracker(app):  # no-op fallback: audit endpoints disabled
        return None

app = FastAPI(title="Google Calendar API (Mock)", version="v3")
install_tracker(app)


@app.get("/health")
def health():
    return {"status": "ok"}


# --- Calendars ---

@app.get("/calendar/v3/users/me/calendarList")
def list_calendars():
    return calendar_data.list_calendars()


@app.get("/calendar/v3/calendars/{calendar_id}")
def get_calendar(calendar_id: str):
    result = calendar_data.get_calendar(calendar_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Events ---

@app.get("/calendar/v3/calendars/{calendar_id}/events")
def list_events(
    calendar_id: str,
    timeMin: Optional[str] = None,
    timeMax: Optional[str] = None,
    q: Optional[str] = None,
    singleEvents: bool = True,
    orderBy: str = "startTime",
    maxResults: int = Query(25, ge=1, le=250),
    pageToken: Optional[str] = None,
):
    result = calendar_data.list_events(
        calendar_id, time_min=timeMin, time_max=timeMax, q=q,
        single_events=singleEvents, order_by=orderBy,
        max_results=maxResults, page_token=pageToken,
    )
    if isinstance(result, dict) and "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.get("/calendar/v3/calendars/{calendar_id}/events/{event_id}")
def get_event(calendar_id: str, event_id: str):
    result = calendar_data.get_event(calendar_id, event_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


class TimeBlock(BaseModel):
    dateTime: Optional[str] = None
    date: Optional[str] = None
    timeZone: Optional[str] = None


class Attendee(BaseModel):
    email: str
    displayName: Optional[str] = ""
    responseStatus: Optional[str] = "needsAction"
    optional: Optional[bool] = False
    organizer: Optional[bool] = False


class EventCreateBody(BaseModel):
    summary: str
    description: Optional[str] = ""
    location: Optional[str] = ""
    start: TimeBlock
    end: TimeBlock
    attendees: Optional[List[Attendee]] = None
    recurrence: Optional[List[str]] = None
    visibility: Optional[str] = "default"


@app.post("/calendar/v3/calendars/{calendar_id}/events", status_code=201)
def create_event(calendar_id: str, body: EventCreateBody):
    payload = body.model_dump(exclude_none=True)
    result = calendar_data.create_event(calendar_id, payload)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


class EventUpdateBody(BaseModel):
    summary: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    start: Optional[TimeBlock] = None
    end: Optional[TimeBlock] = None
    attendees: Optional[List[Attendee]] = None
    status: Optional[str] = None
    visibility: Optional[str] = None


@app.patch("/calendar/v3/calendars/{calendar_id}/events/{event_id}")
def update_event(calendar_id: str, event_id: str, body: EventUpdateBody):
    payload = body.model_dump(exclude_none=True)
    result = calendar_data.update_event(calendar_id, event_id, payload)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.delete("/calendar/v3/calendars/{calendar_id}/events/{event_id}")
def delete_event(calendar_id: str, event_id: str):
    result = calendar_data.delete_event(calendar_id, event_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Free/busy ---

class FreeBusyItem(BaseModel):
    id: str


class FreeBusyBody(BaseModel):
    timeMin: str
    timeMax: str
    items: List[FreeBusyItem]


@app.post("/calendar/v3/freeBusy")
def freebusy(body: FreeBusyBody):
    return calendar_data.freebusy(body.timeMin, body.timeMax, [i.id for i in body.items])
