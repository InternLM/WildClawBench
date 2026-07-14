"""FastAPI server wrapping gitlab_data module as REST endpoints.

Mirrors a subset of the GitLab REST API v4. Base path: /api/v4
"""

from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List

import gitlab_data
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

app = FastAPI(title="GitLab API (Mock)", version="v4")
install_tracker(app)
install_admin_plane(app, store=gitlab_data._store)
@app.get("/health")
def health():
    return {"status": "ok"}


# --- Current user ---

@app.get("/api/v4/user")
def get_user():
    return gitlab_data.get_current_user()


# --- Projects ---

@app.get("/api/v4/projects")
def list_projects(visibility: Optional[str] = None):
    return gitlab_data.list_projects(visibility=visibility)


@app.get("/api/v4/projects/{project_id}")
def get_project(project_id: str):
    result = gitlab_data.get_project(project_id)
    if isinstance(result, dict) and "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Issues ---

@app.get("/api/v4/projects/{project_id}/issues")
def list_issues(project_id: str, state: Optional[str] = None, labels: Optional[str] = None):
    result = gitlab_data.list_issues(project_id, state=state, labels=labels)
    if isinstance(result, dict) and "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.get("/api/v4/projects/{project_id}/issues/{issue_iid}")
def get_issue(project_id: str, issue_iid: int):
    result = gitlab_data.get_issue(project_id, issue_iid)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


class IssueCreateBody(BaseModel):
    title: str
    description: Optional[str] = ""
    assignee: Optional[str] = None
    labels: Optional[List[str]] = None


@app.post("/api/v4/projects/{project_id}/issues", status_code=201)
def create_issue(project_id: str, body: IssueCreateBody):
    result = gitlab_data.create_issue(
        project_id, title=body.title, description=body.description,
        assignee=body.assignee, labels=body.labels,
    )
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


class IssueUpdateBody(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    state_event: Optional[str] = None  # "close" or "reopen"
    assignee: Optional[str] = None
    labels: Optional[List[str]] = None


@app.put("/api/v4/projects/{project_id}/issues/{issue_iid}")
def update_issue(project_id: str, issue_iid: int, body: IssueUpdateBody):
    result = gitlab_data.update_issue(
        project_id, issue_iid,
        title=body.title, description=body.description,
        state_event=body.state_event, assignee=body.assignee, labels=body.labels,
    )
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Merge requests ---

@app.get("/api/v4/projects/{project_id}/merge_requests")
def list_merge_requests(project_id: str, state: Optional[str] = None):
    result = gitlab_data.list_merge_requests(project_id, state=state)
    if isinstance(result, dict) and "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


class MergeRequestCreateBody(BaseModel):
    title: str
    source_branch: str
    target_branch: Optional[str] = "main"
    description: Optional[str] = ""
    assignee: Optional[str] = None


@app.post("/api/v4/projects/{project_id}/merge_requests", status_code=201)
def create_merge_request(project_id: str, body: MergeRequestCreateBody):
    result = gitlab_data.create_merge_request(
        project_id, title=body.title, source_branch=body.source_branch,
        target_branch=body.target_branch or "main",
        description=body.description, assignee=body.assignee,
    )
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.put("/api/v4/projects/{project_id}/merge_requests/{mr_iid}/merge")
def merge_merge_request(project_id: str, mr_iid: int):
    result = gitlab_data.merge_merge_request(project_id, mr_iid)
    if "error" in result:
        status = 404 if "not found" in result["error"] else 405
        return JSONResponse(status_code=status, content=result)
    return result


# --- Pipelines ---

@app.get("/api/v4/projects/{project_id}/pipelines")
def list_pipelines(project_id: str, status: Optional[str] = None):
    result = gitlab_data.list_pipelines(project_id, status=status)
    if isinstance(result, dict) and "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result
