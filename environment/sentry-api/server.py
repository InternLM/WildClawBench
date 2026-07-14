"""FastAPI server wrapping sentry_data module as REST endpoints.

Mirrors a subset of the Sentry API. Base path: /api/0
"""

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional

import sentry_data
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

app = FastAPI(title="Sentry API (Mock)", version="0")
install_tracker(app)
install_admin_plane(app, store=sentry_data._store)
@app.get("/health")
def health():
    return {"status": "ok"}


# --- Projects ---

@app.get("/api/0/organizations/{org_slug}/projects/")
def list_org_projects(org_slug: str):
    result = sentry_data.list_org_projects(org_slug)
    if isinstance(result, dict) and "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Issues ---

@app.get("/api/0/projects/{org_slug}/{project_slug}/issues/")
def list_project_issues(org_slug: str, project_slug: str,
                        status: Optional[str] = None, level: Optional[str] = None):
    result = sentry_data.list_project_issues(org_slug, project_slug, status=status, level=level)
    if isinstance(result, dict) and "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.get("/api/0/organizations/{org_slug}/issues/{issue_id}/")
def get_issue(org_slug: str, issue_id: str):
    result = sentry_data.get_issue(org_slug, issue_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


class IssueUpdateBody(BaseModel):
    status: str  # "resolved", "ignored", or "unresolved"


@app.put("/api/0/organizations/{org_slug}/issues/{issue_id}/")
def update_issue(org_slug: str, issue_id: str, body: IssueUpdateBody):
    result = sentry_data.update_issue_status(org_slug, issue_id, body.status)
    if "error" in result:
        status = 404 if "not found" in result["error"] else 400
        return JSONResponse(status_code=status, content=result)
    return result


@app.get("/api/0/organizations/{org_slug}/issues/{issue_id}/events/")
def list_issue_events(org_slug: str, issue_id: str):
    result = sentry_data.list_issue_events(org_slug, issue_id)
    if isinstance(result, dict) and "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Releases ---

@app.get("/api/0/organizations/{org_slug}/releases/")
def list_releases(org_slug: str, project: Optional[str] = None):
    result = sentry_data.list_releases(org_slug, project_slug=project)
    if isinstance(result, dict) and "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result
