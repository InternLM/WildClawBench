"""FastAPI server wrapping eventbrite_data module as REST endpoints.

Mirrors Eventbrite v3 API (subset).
"""

from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional

import eventbrite_data
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

app = FastAPI(title="Eventbrite API (Mock)", version="v3")
install_tracker(app)
install_admin_plane(app, store=eventbrite_data._store)
@app.get("/health")
def health():
    return {"status": "ok"}


# --- Organizations ---

@app.get("/v3/users/me/organizations")
def list_organizations():
    return eventbrite_data.list_organizations()


@app.get("/v3/organizations/{org_id}")
def get_organization(org_id: str):
    result = eventbrite_data.get_organization(org_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Events ---

@app.get("/v3/organizations/{org_id}/events")
def list_org_events(
    org_id: str,
    status: Optional[str] = None,
    q: Optional[str] = None,
    page_size: int = Query(50, ge=1, le=200),
):
    return eventbrite_data.list_events(organization_id=org_id, status=status, q=q, page_size=page_size)


@app.get("/v3/events/search")
def search_events(
    q: Optional[str] = None,
    status: Optional[str] = None,
    page_size: int = Query(50, ge=1, le=200),
):
    return eventbrite_data.list_events(q=q, status=status, page_size=page_size)


@app.get("/v3/events/{event_id}")
def get_event(event_id: str):
    result = eventbrite_data.get_event(event_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


class EventCreateBody(BaseModel):
    organization_id: str
    name: str
    summary: str
    start_utc: str
    end_utc: str
    timezone: Optional[str] = "America/Los_Angeles"
    venue_id: Optional[str] = None
    capacity: Optional[int] = 50
    is_free: Optional[bool] = True
    online_event: Optional[bool] = False


@app.post("/v3/events", status_code=201)
def create_event(body: EventCreateBody):
    result = eventbrite_data.create_event(
        organization_id=body.organization_id,
        name=body.name, summary=body.summary,
        start_utc=body.start_utc, end_utc=body.end_utc,
        timezone=body.timezone, venue_id=body.venue_id,
        capacity=body.capacity or 50, is_free=body.is_free,
        online_event=body.online_event,
    )
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.post("/v3/events/{event_id}/publish")
def publish_event(event_id: str):
    result = eventbrite_data.publish_event(event_id)
    if "error" in result:
        return JSONResponse(status_code=400, content=result)
    return result


@app.post("/v3/events/{event_id}/cancel")
def cancel_event(event_id: str):
    result = eventbrite_data.cancel_event(event_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Venues ---

@app.get("/v3/venues")
def list_venues():
    return eventbrite_data.list_venues()


@app.get("/v3/venues/{venue_id}")
def get_venue(venue_id: str):
    result = eventbrite_data.get_venue(venue_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Ticket classes ---

@app.get("/v3/events/{event_id}/ticket_classes")
def list_ticket_classes(event_id: str):
    result = eventbrite_data.list_ticket_classes(event_id)
    if isinstance(result, dict) and "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


class TicketClassCreateBody(BaseModel):
    name: str
    quantity_total: int
    cost: int = 0
    free: bool = True


@app.post("/v3/events/{event_id}/ticket_classes", status_code=201)
def create_ticket_class(event_id: str, body: TicketClassCreateBody):
    result = eventbrite_data.create_ticket_class(
        event_id, name=body.name, quantity_total=body.quantity_total,
        cost=body.cost, free=body.free,
    )
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Attendees ---

@app.get("/v3/events/{event_id}/attendees")
def list_attendees(
    event_id: str,
    status: Optional[str] = None,
    checked_in: Optional[bool] = None,
):
    result = eventbrite_data.list_attendees(event_id, status=status, checked_in=checked_in)
    if isinstance(result, dict) and "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


class RegisterAttendeeBody(BaseModel):
    ticket_class_id: str
    name: str
    email: str


@app.post("/v3/events/{event_id}/attendees", status_code=201)
def register_attendee(event_id: str, body: RegisterAttendeeBody):
    result = eventbrite_data.register_attendee(
        event_id, ticket_class_id=body.ticket_class_id,
        name=body.name, email=body.email,
    )
    if "error" in result:
        return JSONResponse(status_code=400, content=result)
    return result


@app.post("/v3/attendees/{attendee_id}/check_in")
def check_in_attendee(attendee_id: str):
    result = eventbrite_data.check_in_attendee(attendee_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result
