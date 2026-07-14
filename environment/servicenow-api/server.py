"""FastAPI server wrapping servicenow_data module as REST endpoints.

Mirrors a subset of the ServiceNow Table API. Base path: /api/now/table
All successful responses are wrapped as {"result": ...} per ServiceNow convention.
"""

from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional

import servicenow_data
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

app = FastAPI(title="ServiceNow Table API (Mock)", version="v1")
install_tracker(app)
install_admin_plane(app, store=servicenow_data._store)
@app.get("/health")
def health():
    return {"status": "ok"}


# --- Incidents ---

@app.get("/api/now/table/incident")
def list_incidents(sysparm_query: Optional[str] = None,
                   sysparm_limit: Optional[int] = Query(None, ge=1, le=1000)):
    return {"result": servicenow_data.list_incidents(
        sysparm_query=sysparm_query, sysparm_limit=sysparm_limit)}


@app.get("/api/now/table/incident/{sys_id}")
def get_incident(sys_id: str):
    result = servicenow_data.get_incident(sys_id)
    if "error" in result:
        return JSONResponse(status_code=404, content={"error": result["error"]})
    return {"result": result}


class IncidentCreate(BaseModel):
    short_description: str
    description: Optional[str] = None
    priority: Optional[str] = "3"
    impact: Optional[str] = "3"
    urgency: Optional[str] = "3"
    category: Optional[str] = "inquiry"
    assigned_to: Optional[str] = None
    opened_by: Optional[str] = None


@app.post("/api/now/table/incident", status_code=201)
def create_incident(body: IncidentCreate):
    result = servicenow_data.create_incident(
        short_description=body.short_description, description=body.description,
        priority=body.priority, impact=body.impact, urgency=body.urgency,
        category=body.category, assigned_to=body.assigned_to, opened_by=body.opened_by)
    if "error" in result:
        return JSONResponse(status_code=400, content={"error": result["error"]})
    return {"result": result}


class IncidentUpdate(BaseModel):
    short_description: Optional[str] = None
    description: Optional[str] = None
    state: Optional[str] = None
    priority: Optional[str] = None
    impact: Optional[str] = None
    urgency: Optional[str] = None
    category: Optional[str] = None
    assigned_to: Optional[str] = None


@app.patch("/api/now/table/incident/{sys_id}")
def update_incident(sys_id: str, body: IncidentUpdate):
    result = servicenow_data.update_incident(sys_id, **body.model_dump(exclude_none=True))
    if "error" in result:
        return JSONResponse(status_code=404, content={"error": result["error"]})
    return {"result": result}


# --- Change requests ---

@app.get("/api/now/table/change_request")
def list_change_requests(sysparm_query: Optional[str] = None,
                         sysparm_limit: Optional[int] = Query(None, ge=1, le=1000)):
    return {"result": servicenow_data.list_change_requests(
        sysparm_query=sysparm_query, sysparm_limit=sysparm_limit)}


@app.get("/api/now/table/change_request/{sys_id}")
def get_change_request(sys_id: str):
    result = servicenow_data.get_change_request(sys_id)
    if "error" in result:
        return JSONResponse(status_code=404, content={"error": result["error"]})
    return {"result": result}


# --- Problems ---

@app.get("/api/now/table/problem")
def list_problems(sysparm_query: Optional[str] = None,
                  sysparm_limit: Optional[int] = Query(None, ge=1, le=1000)):
    return {"result": servicenow_data.list_problems(
        sysparm_query=sysparm_query, sysparm_limit=sysparm_limit)}


@app.get("/api/now/table/problem/{sys_id}")
def get_problem(sys_id: str):
    result = servicenow_data.get_problem(sys_id)
    if "error" in result:
        return JSONResponse(status_code=404, content={"error": result["error"]})
    return {"result": result}


# --- Users ---

@app.get("/api/now/table/sys_user")
def list_users(sysparm_query: Optional[str] = None,
               sysparm_limit: Optional[int] = Query(None, ge=1, le=1000)):
    return {"result": servicenow_data.list_users(
        sysparm_query=sysparm_query, sysparm_limit=sysparm_limit)}


@app.get("/api/now/table/sys_user/{sys_id}")
def get_user(sys_id: str):
    result = servicenow_data.get_user(sys_id)
    if "error" in result:
        return JSONResponse(status_code=404, content={"error": result["error"]})
    return {"result": result}
