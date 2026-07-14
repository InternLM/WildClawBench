"""FastAPI server wrapping figma_data module as REST endpoints.

Implements a subset of the Figma REST API. Base path: /v1
"""

from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any

import figma_data
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

app = FastAPI(title="Figma API (Mock)", version="v1")
install_tracker(app)
install_admin_plane(app, store=figma_data._store)
@app.get("/health")
def health():
    return {"status": "ok"}


# --- User ---

@app.get("/v1/me")
def get_me():
    return figma_data.get_me()


# --- Teams / projects ---

@app.get("/v1/teams/{team_id}/projects")
def team_projects(team_id: str):
    result = figma_data.get_team_projects(team_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.get("/v1/projects/{project_id}/files")
def project_files(project_id: str):
    result = figma_data.get_project_files(project_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Files / nodes ---

@app.get("/v1/files/{file_key}")
def get_file(file_key: str):
    result = figma_data.get_file(file_key)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.get("/v1/files/{file_key}/nodes")
def get_file_nodes(file_key: str, ids: str = Query(...)):
    result = figma_data.get_file_nodes(file_key, ids)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Comments ---

@app.get("/v1/files/{file_key}/comments")
def get_comments(file_key: str):
    result = figma_data.get_comments(file_key)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


class CommentBody(BaseModel):
    message: str
    client_meta: Optional[Dict[str, Any]] = None
    user_id: Optional[str] = None


@app.post("/v1/files/{file_key}/comments", status_code=201)
def create_comment(file_key: str, body: CommentBody):
    node_id = None
    if body.client_meta:
        node_id = body.client_meta.get("node_id")
    result = figma_data.create_comment(
        file_key,
        message=body.message,
        node_id=node_id,
        user_id=body.user_id or "user-1001",
    )
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Components ---

@app.get("/v1/files/{file_key}/components")
def get_components(file_key: str):
    result = figma_data.get_components(file_key)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result
