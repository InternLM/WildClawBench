"""FastAPI server wrapping github_data module as REST endpoints.

Mirrors the GitHub REST API v3 (subset). Base path uses bare /user, /repos/...
matching the real api.github.com structure.
"""

from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List

import github_data
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

app = FastAPI(title="GitHub REST API (Mock)", version="2022-11-28")
install_tracker(app)
install_admin_plane(app, store=github_data._store)
@app.get("/health")
def health():
    return {"status": "ok"}


# --- User ---

@app.get("/user")
def get_user():
    return github_data.get_user()


# --- Repos ---

@app.get("/users/{owner}/repos")
def list_user_repos(owner: str):
    return github_data.list_repos(owner=owner)


@app.get("/orgs/{owner}/repos")
def list_org_repos(owner: str):
    return github_data.list_repos(owner=owner)


@app.get("/repos/{owner}/{repo}")
def get_repo(owner: str, repo: str):
    result = github_data.get_repo(owner, repo)
    if isinstance(result, dict) and "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Issues ---

@app.get("/repos/{owner}/{repo}/issues")
def list_issues(
    owner: str, repo: str,
    state: str = "open",
    labels: Optional[str] = None,
    assignee: Optional[str] = None,
    per_page: int = Query(30, ge=1, le=100),
):
    result = github_data.list_issues(owner, repo, state=state, labels=labels,
                                     assignee=assignee, limit=per_page)
    if isinstance(result, dict) and "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.get("/repos/{owner}/{repo}/issues/{number}")
def get_issue(owner: str, repo: str, number: int):
    result = github_data.get_issue(owner, repo, number)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


class IssueCreateBody(BaseModel):
    title: str
    body: Optional[str] = ""
    assignee: Optional[str] = None
    labels: Optional[List[str]] = None


@app.post("/repos/{owner}/{repo}/issues", status_code=201)
def create_issue(owner: str, repo: str, body: IssueCreateBody):
    result = github_data.create_issue(
        owner, repo, title=body.title, body=body.body,
        assignee=body.assignee, labels=body.labels,
    )
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


class IssueUpdateBody(BaseModel):
    title: Optional[str] = None
    body: Optional[str] = None
    state: Optional[str] = None  # "open" or "closed"
    assignee: Optional[str] = None
    labels: Optional[List[str]] = None


@app.patch("/repos/{owner}/{repo}/issues/{number}")
def update_issue(owner: str, repo: str, number: int, body: IssueUpdateBody):
    result = github_data.update_issue(
        owner, repo, number,
        title=body.title, body=body.body, state=body.state,
        assignee=body.assignee, labels=body.labels,
    )
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Pulls ---

@app.get("/repos/{owner}/{repo}/pulls")
def list_pulls(owner: str, repo: str, state: str = "open"):
    result = github_data.list_pulls(owner, repo, state=state)
    if isinstance(result, dict) and "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.get("/repos/{owner}/{repo}/pulls/{number}")
def get_pull(owner: str, repo: str, number: int):
    result = github_data.get_pull(owner, repo, number)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.put("/repos/{owner}/{repo}/pulls/{number}/merge")
def merge_pull(owner: str, repo: str, number: int):
    result = github_data.merge_pull(owner, repo, number)
    if "error" in result:
        return JSONResponse(status_code=405, content=result)
    return result


# --- Comments ---

@app.get("/repos/{owner}/{repo}/issues/{number}/comments")
def list_comments(owner: str, repo: str, number: int):
    result = github_data.list_comments(owner, repo, number)
    if isinstance(result, dict) and "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


class CommentBody(BaseModel):
    body: str


@app.post("/repos/{owner}/{repo}/issues/{number}/comments", status_code=201)
def create_comment(owner: str, repo: str, number: int, body: CommentBody):
    result = github_data.create_comment(owner, repo, number, body.body)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result
