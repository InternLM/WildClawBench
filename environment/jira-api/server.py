"""FastAPI server wrapping jira_data module as REST endpoints.

Mirrors a subset of the Jira Cloud platform API v3 and the Agile API v1.0.
Base paths: /rest/api/3/... and /rest/agile/1.0/...
"""

from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any

import jira_data
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

app = FastAPI(title="Jira API (Mock)", version="3")
install_tracker(app)
install_admin_plane(app, store=jira_data._store)
@app.get("/health")
def health():
    return {"status": "ok"}


# --- Projects ---

@app.get("/rest/api/3/project")
def list_projects():
    return jira_data.list_projects()


# --- Issues ---

class IssueFields(BaseModel):
    summary: str
    project: Optional[Dict[str, Any]] = None
    issuetype: Optional[Dict[str, Any]] = None
    description: Optional[str] = ""
    priority: Optional[Dict[str, Any]] = None
    assignee: Optional[Dict[str, Any]] = None


class IssueCreateBody(BaseModel):
    fields: IssueFields


@app.post("/rest/api/3/issue", status_code=201)
def create_issue(body: IssueCreateBody):
    f = body.fields
    project_key = (f.project or {}).get("key")
    issue_type = (f.issuetype or {}).get("name", "Task")
    priority = (f.priority or {}).get("name", "Medium")
    assignee = (f.assignee or {}).get("accountId") if f.assignee else None
    if not project_key:
        return JSONResponse(status_code=400, content={"errorMessages": ["fields.project.key is required"], "errors": {}})
    result = jira_data.create_issue(
        project_key=project_key,
        summary=f.summary,
        issue_type=issue_type,
        description=f.description,
        priority=priority,
        assignee=assignee,
    )
    if "errorMessages" in result:
        return JSONResponse(status_code=400, content=result)
    return result


@app.get("/rest/api/3/issue/{issue_key}")
def get_issue(issue_key: str):
    result = jira_data.get_issue(issue_key)
    if "errorMessages" in result:
        return JSONResponse(status_code=404, content=result)
    return result


class IssueUpdateBody(BaseModel):
    fields: Optional[Dict[str, Any]] = None


@app.put("/rest/api/3/issue/{issue_key}", status_code=204)
def update_issue(issue_key: str, body: IssueUpdateBody):
    fields = body.fields or {}
    summary = fields.get("summary")
    description = fields.get("description")
    priority = (fields.get("priority") or {}).get("name") if fields.get("priority") else None
    assignee = None
    if "assignee" in fields:
        assignee = (fields.get("assignee") or {}).get("accountId") or ""
    result = jira_data.update_issue(
        issue_key, summary=summary, description=description,
        priority=priority, assignee=assignee,
    )
    if "errorMessages" in result:
        return JSONResponse(status_code=404, content=result)
    return JSONResponse(status_code=204, content=None)


# --- Transitions ---

@app.get("/rest/api/3/issue/{issue_key}/transitions")
def get_transitions(issue_key: str):
    result = jira_data.get_transitions(issue_key)
    if "errorMessages" in result:
        return JSONResponse(status_code=404, content=result)
    return result


class TransitionBody(BaseModel):
    transition: Dict[str, Any]


@app.post("/rest/api/3/issue/{issue_key}/transitions", status_code=204)
def transition_issue(issue_key: str, body: TransitionBody):
    transition_id = str(body.transition.get("id"))
    result = jira_data.transition_issue(issue_key, transition_id)
    if "errorMessages" in result:
        status = 404 if "does not exist" in result["errorMessages"][0] else 400
        return JSONResponse(status_code=status, content=result)
    return JSONResponse(status_code=204, content=None)


# --- Search ---

@app.get("/rest/api/3/search")
def search(jql: Optional[str] = None, maxResults: int = Query(50, ge=1, le=100)):
    return jira_data.search(jql=jql, max_results=maxResults)


# --- Agile: boards + sprints ---

@app.get("/rest/agile/1.0/board")
def list_boards():
    return jira_data.list_boards()


@app.get("/rest/agile/1.0/board/{board_id}/sprint")
def list_sprints(board_id: int, state: Optional[str] = None):
    result = jira_data.list_sprints(board_id, state=state)
    if isinstance(result, dict) and "errorMessages" in result:
        return JSONResponse(status_code=404, content=result)
    return result
