"""FastAPI server wrapping freshdesk_data module as REST endpoints.

Mirrors a subset of the Freshdesk v2 API: tickets (list/get/create/update),
contacts, and agents. Routes live under /api/v2/...
"""

from fastapi import FastAPI, Query, Body
from fastapi.responses import JSONResponse
from typing import Optional

import freshdesk_data
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

app = FastAPI(title="Freshdesk API (Mock)", version="v2")
install_tracker(app)
install_admin_plane(app, store=freshdesk_data._store)
@app.get("/health")
def health():
    return {"status": "ok"}


# --- Tickets ---

@app.get("/api/v2/tickets")
def list_tickets(
    status: Optional[int] = Query(None),
    priority: Optional[int] = Query(None),
    requester_id: Optional[int] = Query(None),
):
    return freshdesk_data.list_tickets(
        status=status, priority=priority, requester_id=requester_id
    )


@app.get("/api/v2/tickets/{ticket_id}")
def get_ticket(ticket_id: int):
    result = freshdesk_data.get_ticket(ticket_id)
    if isinstance(result, dict) and "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.post("/api/v2/tickets", status_code=201)
def create_ticket(body: dict = Body(...)):
    return freshdesk_data.create_ticket(body)


@app.put("/api/v2/tickets/{ticket_id}")
def update_ticket(ticket_id: int, body: dict = Body(...)):
    result = freshdesk_data.update_ticket(ticket_id, body)
    if isinstance(result, dict) and "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Contacts + agents ---

@app.get("/api/v2/contacts")
def list_contacts():
    return freshdesk_data.list_contacts()


@app.get("/api/v2/agents")
def list_agents():
    return freshdesk_data.list_agents()
