"""FastAPI server wrapping datadog_data module as REST endpoints.

Mirrors a subset of the Datadog API v1. Base path: /api/v1
"""

from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List

import datadog_data
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

app = FastAPI(title="Datadog API (Mock)", version="v1")
install_tracker(app)
install_admin_plane(app, store=datadog_data._store)
@app.get("/health")
def health():
    return {"status": "ok"}


# --- Metrics query ---

@app.get("/api/v1/query")
def query_metrics(
    query: str,
    from_: int = Query(..., alias="from"),
    to: int = Query(...),
):
    result = datadog_data.query_metrics(from_, to, query)
    if result.get("status") == "error":
        return JSONResponse(status_code=400, content=result)
    return result


# --- Monitors ---

@app.get("/api/v1/monitor")
def list_monitors(overall_state: Optional[str] = None):
    return datadog_data.list_monitors(overall_state=overall_state)


@app.get("/api/v1/monitor/{monitor_id}")
def get_monitor(monitor_id: str):
    result = datadog_data.get_monitor(monitor_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


class MonitorCreateBody(BaseModel):
    name: str
    type: str
    query: str
    message: Optional[str] = ""
    priority: Optional[int] = 3
    tags: Optional[List[str]] = None


@app.post("/api/v1/monitor", status_code=201)
def create_monitor(body: MonitorCreateBody):
    return datadog_data.create_monitor(
        name=body.name, mtype=body.type, query=body.query,
        message=body.message, priority=body.priority, tags=body.tags,
    )


class MonitorUpdateBody(BaseModel):
    name: Optional[str] = None
    query: Optional[str] = None
    message: Optional[str] = None
    overall_state: Optional[str] = None
    priority: Optional[int] = None
    tags: Optional[List[str]] = None


@app.put("/api/v1/monitor/{monitor_id}")
def update_monitor(monitor_id: str, body: MonitorUpdateBody):
    result = datadog_data.update_monitor(
        monitor_id, name=body.name, query=body.query, message=body.message,
        overall_state=body.overall_state, priority=body.priority, tags=body.tags,
    )
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Dashboards ---

@app.get("/api/v1/dashboard")
def list_dashboards():
    return datadog_data.list_dashboards()


@app.get("/api/v1/dashboard/{dashboard_id}")
def get_dashboard(dashboard_id: str):
    result = datadog_data.get_dashboard(dashboard_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Events ---

@app.get("/api/v1/events")
def list_events(start: Optional[int] = None, end: Optional[int] = None):
    return datadog_data.list_events(start=start, end=end)


class EventCreateBody(BaseModel):
    title: str
    text: str
    alert_type: Optional[str] = "info"
    priority: Optional[str] = "normal"
    host: Optional[str] = None
    tags: Optional[List[str]] = None


@app.post("/api/v1/events", status_code=201)
def create_event(body: EventCreateBody):
    return datadog_data.create_event(
        title=body.title, text=body.text, alert_type=body.alert_type,
        priority=body.priority, host=body.host, tags=body.tags,
    )


# --- Hosts ---

@app.get("/api/v1/hosts")
def list_hosts():
    return datadog_data.list_hosts()
