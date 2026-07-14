"""FastAPI server wrapping pagerduty_data module as REST endpoints.

Implements a subset of the PagerDuty REST API surface.
"""

from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List

import pagerduty_data
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

app = FastAPI(title="PagerDuty API (Mock)", version="1.0.0")
install_tracker(app)
install_admin_plane(app, store=pagerduty_data._store)
@app.get("/health")
def health():
    return {"status": "ok"}


# --- Services ---

@app.get("/services")
def list_services():
    return pagerduty_data.list_services()


@app.get("/services/{service_id}")
def get_service(service_id: str):
    result = pagerduty_data.get_service(service_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Incidents ---

@app.get("/incidents")
def list_incidents(
    statuses: Optional[List[str]] = Query(None, alias="statuses[]"),
    service_id: Optional[str] = None,
    urgency: Optional[str] = None,
):
    return pagerduty_data.list_incidents(
        statuses=statuses, service_id=service_id, urgency=urgency)


@app.get("/incidents/{incident_id}")
def get_incident(incident_id: str):
    result = pagerduty_data.get_incident(incident_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


class IncidentCreateBody(BaseModel):
    title: str
    service_id: str
    urgency: str = "high"
    assigned_to: Optional[str] = None


@app.post("/incidents", status_code=201)
def create_incident(body: IncidentCreateBody):
    result = pagerduty_data.create_incident(
        title=body.title,
        service_id=body.service_id,
        urgency=body.urgency,
        assigned_to=body.assigned_to,
    )
    if "error" in result:
        return JSONResponse(status_code=400, content=result)
    return result


class IncidentUpdateBody(BaseModel):
    status: Optional[str] = None
    assigned_to: Optional[str] = None


@app.put("/incidents/{incident_id}")
def update_incident(incident_id: str, body: IncidentUpdateBody):
    result = pagerduty_data.update_incident(
        incident_id, status=body.status, assigned_to=body.assigned_to)
    if "error" in result:
        status = 404 if "not found" in result["error"] else 400
        return JSONResponse(status_code=status, content=result)
    return result


# --- Notes ---

@app.get("/incidents/{incident_id}/notes")
def list_notes(incident_id: str):
    result = pagerduty_data.list_notes(incident_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


class NoteCreateBody(BaseModel):
    content: str
    user_id: Optional[str] = None


@app.post("/incidents/{incident_id}/notes", status_code=201)
def create_note(incident_id: str, body: NoteCreateBody):
    result = pagerduty_data.create_note(incident_id, body.content, user_id=body.user_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- On-call / schedules / escalation policies ---

@app.get("/oncalls")
def list_oncalls(escalation_policy_id: Optional[str] = None):
    return pagerduty_data.list_oncalls(escalation_policy_id=escalation_policy_id)


@app.get("/schedules")
def list_schedules():
    return pagerduty_data.list_schedules()


@app.get("/escalation_policies")
def list_escalation_policies():
    return pagerduty_data.list_escalation_policies()


# --- Users ---

@app.get("/users")
def list_users():
    return pagerduty_data.list_users()
