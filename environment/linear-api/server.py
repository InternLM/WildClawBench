"""FastAPI server wrapping linear_data module as REST endpoints."""

from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List

import linear_data
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

app = FastAPI(title="Linear API (Mock)", version="2024.01")
install_tracker(app)
install_admin_plane(app, store=linear_data._store)
@app.get("/health")
def health():
    return {"status": "ok"}


# --- Teams ---

@app.get("/v1/teams")
def list_teams(
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    return linear_data.list_teams(limit=limit, offset=offset)


@app.get("/v1/teams/{team_id}")
def get_team(team_id: str):
    result = linear_data.get_team(team_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.get("/v1/teams/{team_id}/members")
def get_team_members(team_id: str):
    result = linear_data.get_team_members(team_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.get("/v1/teams/{team_id}/issues")
def get_team_issues(
    team_id: str,
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    result = linear_data.get_team_issues(team_id, limit=limit, offset=offset)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.get("/v1/teams/{team_id}/projects")
def get_team_projects(team_id: str):
    result = linear_data.get_team_projects(team_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.get("/v1/teams/{team_id}/cycles")
def get_team_cycles(team_id: str):
    result = linear_data.get_team_cycles(team_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.get("/v1/teams/{team_id}/workflow-states")
def get_team_workflow_states(team_id: str):
    result = linear_data.get_team_workflow_states(team_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.get("/v1/teams/{team_id}/labels")
def get_team_labels(team_id: str):
    result = linear_data.get_team_labels(team_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Users ---

@app.get("/v1/users")
def list_users(
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    return linear_data.list_users(limit=limit, offset=offset)


@app.get("/v1/users/{user_id}")
def get_user(user_id: str):
    result = linear_data.get_user(user_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.get("/v1/users/{user_id}/issues")
def get_user_assigned_issues(
    user_id: str,
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    result = linear_data.get_user_assigned_issues(user_id, limit=limit, offset=offset)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Workflow States ---

@app.get("/v1/workflow-states")
def list_workflow_states(
    teamId: Optional[str] = Query(default=None),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    return linear_data.list_workflow_states(team_id=teamId, limit=limit, offset=offset)


@app.get("/v1/workflow-states/{state_id}")
def get_workflow_state(state_id: str):
    result = linear_data.get_workflow_state(state_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Labels ---

@app.get("/v1/labels")
def list_labels(
    teamId: Optional[str] = Query(default=None),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    return linear_data.list_labels(team_id=teamId, limit=limit, offset=offset)


@app.get("/v1/labels/{label_id}")
def get_label(label_id: str):
    result = linear_data.get_label(label_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


class LabelCreateBody(BaseModel):
    name: str
    color: str
    description: Optional[str] = None
    teamId: Optional[str] = None


@app.post("/v1/labels", status_code=201)
def create_label(body: LabelCreateBody):
    result = linear_data.create_label(body.model_dump())
    if "error" in result:
        return JSONResponse(status_code=400, content=result)
    return result


# --- Projects ---

@app.get("/v1/projects")
def list_projects(
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    return linear_data.list_projects(limit=limit, offset=offset)


@app.get("/v1/projects/{project_id}")
def get_project(project_id: str):
    result = linear_data.get_project(project_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


class ProjectCreateBody(BaseModel):
    name: str
    description: Optional[str] = None
    state: Optional[str] = None
    leadId: Optional[str] = None
    teamIds: Optional[List[str]] = None
    startDate: Optional[str] = None
    targetDate: Optional[str] = None


@app.post("/v1/projects", status_code=201)
def create_project(body: ProjectCreateBody):
    data = {k: v for k, v in body.model_dump().items() if v is not None}
    result = linear_data.create_project(data)
    if "error" in result:
        return JSONResponse(status_code=400, content=result)
    return result


class ProjectUpdateBody(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    state: Optional[str] = None
    leadId: Optional[str] = None
    teamIds: Optional[List[str]] = None
    startDate: Optional[str] = None
    targetDate: Optional[str] = None


@app.put("/v1/projects/{project_id}")
def update_project(project_id: str, body: ProjectUpdateBody):
    data = {k: v for k, v in body.model_dump().items() if v is not None}
    result = linear_data.update_project(project_id, data)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.get("/v1/projects/{project_id}/issues")
def get_project_issues(
    project_id: str,
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    result = linear_data.get_project_issues(project_id, limit=limit, offset=offset)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Cycles ---

@app.get("/v1/cycles")
def list_cycles(
    teamId: Optional[str] = Query(default=None),
    status: Optional[str] = Query(default=None),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    return linear_data.list_cycles(team_id=teamId, status=status, limit=limit, offset=offset)


@app.get("/v1/cycles/{cycle_id}")
def get_cycle(cycle_id: str):
    result = linear_data.get_cycle(cycle_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


class CycleCreateBody(BaseModel):
    name: str
    teamId: str
    startsAt: str
    endsAt: str


@app.post("/v1/cycles", status_code=201)
def create_cycle(body: CycleCreateBody):
    result = linear_data.create_cycle(body.model_dump())
    if "error" in result:
        return JSONResponse(status_code=400, content=result)
    return result


@app.get("/v1/cycles/{cycle_id}/issues")
def get_cycle_issues(
    cycle_id: str,
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    result = linear_data.get_cycle_issues(cycle_id, limit=limit, offset=offset)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Issues ---

@app.get("/v1/issues")
def list_issues(
    stateId: Optional[str] = Query(default=None),
    assigneeId: Optional[str] = Query(default=None),
    projectId: Optional[str] = Query(default=None),
    cycleId: Optional[str] = Query(default=None),
    teamId: Optional[str] = Query(default=None),
    priority: Optional[int] = Query(default=None),
    labelId: Optional[str] = Query(default=None),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    return linear_data.list_issues(
        state_id=stateId, assignee_id=assigneeId, project_id=projectId,
        cycle_id=cycleId, team_id=teamId, priority=priority, label_id=labelId,
        limit=limit, offset=offset,
    )


@app.get("/v1/issues/search")
def search_issues(
    q: str = Query(...),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    return linear_data.search_issues(query=q, limit=limit, offset=offset)


@app.get("/v1/issues/{issue_id}")
def get_issue(issue_id: str):
    result = linear_data.get_issue(issue_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


class IssueCreateBody(BaseModel):
    title: str
    teamId: str
    description: Optional[str] = None
    priority: Optional[int] = None
    estimate: Optional[int] = None
    stateId: Optional[str] = None
    assigneeId: Optional[str] = None
    projectId: Optional[str] = None
    cycleId: Optional[str] = None
    labelIds: Optional[List[str]] = None
    dueDate: Optional[str] = None


@app.post("/v1/issues", status_code=201)
def create_issue(body: IssueCreateBody):
    data = {k: v for k, v in body.model_dump().items() if v is not None}
    result = linear_data.create_issue(data)
    if "error" in result:
        return JSONResponse(status_code=400, content=result)
    return result


class IssueUpdateBody(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[int] = None
    estimate: Optional[int] = None
    stateId: Optional[str] = None
    assigneeId: Optional[str] = None
    projectId: Optional[str] = None
    cycleId: Optional[str] = None
    labelIds: Optional[List[str]] = None
    dueDate: Optional[str] = None
    sortOrder: Optional[float] = None


@app.put("/v1/issues/{issue_id}")
def update_issue(issue_id: str, body: IssueUpdateBody):
    data = {k: v for k, v in body.model_dump().items() if v is not None}
    result = linear_data.update_issue(issue_id, data)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.delete("/v1/issues/{issue_id}")
def delete_issue(issue_id: str):
    result = linear_data.delete_issue(issue_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Comments ---

@app.get("/v1/issues/{issue_id}/comments")
def list_comments(
    issue_id: str,
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    result = linear_data.list_comments(issue_id, limit=limit, offset=offset)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.get("/v1/comments/{comment_id}")
def get_comment(comment_id: str):
    result = linear_data.get_comment(comment_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


class CommentCreateBody(BaseModel):
    body: str
    issueId: str
    userId: Optional[str] = None


@app.post("/v1/comments", status_code=201)
def create_comment(body: CommentCreateBody):
    data = body.model_dump()
    result = linear_data.create_comment(data)
    if "error" in result:
        return JSONResponse(status_code=400, content=result)
    return result


class CommentUpdateBody(BaseModel):
    body: str


@app.put("/v1/comments/{comment_id}")
def update_comment(comment_id: str, body: CommentUpdateBody):
    data = body.model_dump()
    result = linear_data.update_comment(comment_id, data)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.delete("/v1/comments/{comment_id}")
def delete_comment(comment_id: str):
    result = linear_data.delete_comment(comment_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result
