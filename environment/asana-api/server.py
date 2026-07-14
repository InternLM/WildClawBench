"""FastAPI server wrapping asana_data module as REST endpoints.

Implements a subset of the Asana API surface. Base path: /api/1.0
"""

from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional

import asana_data
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

app = FastAPI(title="Asana API (Mock)", version="1.0.0")
install_tracker(app)
install_admin_plane(app, store=asana_data._store)
@app.get("/health")
def health():
    return {"status": "ok"}


# --- Workspaces ---

@app.get("/api/1.0/workspaces")
def list_workspaces():
    return asana_data.list_workspaces()


# --- Users ---

@app.get("/api/1.0/users")
def list_users(workspace: Optional[str] = None):
    return asana_data.list_users(workspace_gid=workspace)


# --- Projects ---

@app.get("/api/1.0/projects")
def list_projects(workspace: Optional[str] = None, archived: Optional[bool] = None):
    return asana_data.list_projects(workspace_gid=workspace, archived=archived)


@app.get("/api/1.0/projects/{project_gid}")
def get_project(project_gid: str):
    result = asana_data.get_project(project_gid)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.get("/api/1.0/projects/{project_gid}/sections")
def list_project_sections(project_gid: str):
    result = asana_data.list_project_sections(project_gid)
    if isinstance(result, dict) and "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.get("/api/1.0/projects/{project_gid}/tasks")
def list_project_tasks(project_gid: str, completed_since: Optional[str] = None):
    result = asana_data.list_project_tasks(project_gid, completed_since=completed_since)
    if isinstance(result, dict) and "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Tasks ---

@app.get("/api/1.0/tasks")
def list_tasks(project: Optional[str] = None, assignee: Optional[str] = None,
               completed: Optional[bool] = None):
    return asana_data.list_tasks(project_gid=project, assignee_gid=assignee, completed=completed)


class TaskData(BaseModel):
    name: str
    projects: Optional[list] = None
    project: Optional[str] = None
    section: Optional[str] = None
    assignee: Optional[str] = None
    due_on: Optional[str] = None
    notes: Optional[str] = ""
    completed: Optional[bool] = False


class TaskCreateBody(BaseModel):
    data: TaskData


@app.post("/api/1.0/tasks", status_code=201)
def create_task(body: TaskCreateBody):
    d = body.data
    project_gid = d.project
    if not project_gid and d.projects:
        project_gid = d.projects[0]
    result = asana_data.create_task(
        name=d.name,
        project_gid=project_gid,
        section_gid=d.section,
        assignee_gid=d.assignee,
        due_on=d.due_on,
        notes=d.notes or "",
        completed=bool(d.completed),
    )
    if "error" in result:
        return JSONResponse(status_code=400, content=result)
    return result


@app.get("/api/1.0/tasks/{task_gid}")
def get_task(task_gid: str):
    result = asana_data.get_task(task_gid)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


class TaskUpdateData(BaseModel):
    name: Optional[str] = None
    completed: Optional[bool] = None
    assignee: Optional[str] = None
    due_on: Optional[str] = None
    section: Optional[str] = None
    notes: Optional[str] = None


class TaskUpdateBody(BaseModel):
    data: TaskUpdateData


@app.put("/api/1.0/tasks/{task_gid}")
def update_task(task_gid: str, body: TaskUpdateBody):
    d = body.data
    result = asana_data.update_task(
        task_gid,
        name=d.name,
        completed=d.completed,
        assignee_gid=d.assignee,
        due_on=d.due_on,
        section_gid=d.section,
        notes=d.notes,
    )
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result
