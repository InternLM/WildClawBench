"""FastAPI server wrapping confluence_data module as REST endpoints.

Implements a subset of the Confluence Cloud REST API. Base path:
/wiki/rest/api  — spaces, content (pages), children, labels, comments,
and a simplified CQL search.
"""

from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any

import confluence_data
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

app = FastAPI(title="Confluence Cloud API (Mock)", version="v1")
install_tracker(app)
install_admin_plane(app, store=confluence_data._store)
BASE = "/wiki/rest/api"


@app.get("/health")
def health():
    return {"status": "ok"}


# --- Spaces ---

@app.get(BASE + "/space")
def list_spaces(limit: int = Query(25, ge=1, le=100)):
    return confluence_data.list_spaces(limit=limit)


@app.get(BASE + "/space/{space_key}")
def get_space(space_key: str):
    result = confluence_data.get_space(space_key)
    if isinstance(result, dict) and "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Content search (must precede /content/{id}) ---

@app.get(BASE + "/content/search")
def search_content(cql: str = Query(..., description="Simplified CQL string")):
    result = confluence_data.search(cql)
    if isinstance(result, dict) and "error" in result:
        return JSONResponse(status_code=400, content=result)
    return result


# --- Content (pages) ---

@app.get(BASE + "/content")
def list_content(type: str = "page", spaceKey: Optional[str] = None,
                 limit: int = Query(25, ge=1, le=100)):
    return confluence_data.list_content(type=type, space_key=spaceKey, limit=limit)


class ContentBodyStorage(BaseModel):
    value: str
    representation: Optional[str] = "storage"


class ContentBodyWrapper(BaseModel):
    storage: ContentBodyStorage


class ContentSpace(BaseModel):
    key: str


class ContentAncestor(BaseModel):
    id: str


class ContentVersion(BaseModel):
    number: int


class ContentCreateBody(BaseModel):
    type: Optional[str] = "page"
    title: str
    space: ContentSpace
    ancestors: Optional[list[ContentAncestor]] = None
    body: Optional[ContentBodyWrapper] = None
    created_by: Optional[str] = None


@app.post(BASE + "/content", status_code=201)
def create_content(body: ContentCreateBody):
    parent_id = body.ancestors[0].id if body.ancestors else None
    storage_value = body.body.storage.value if body.body else ""
    result = confluence_data.create_content(
        title=body.title, space_key=body.space.key, body=storage_value,
        parent_id=parent_id, created_by=body.created_by or "apiuser",
    )
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.get(BASE + "/content/{content_id}")
def get_content(content_id: str):
    result = confluence_data.get_content(content_id)
    if isinstance(result, dict) and "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


class ContentUpdateBody(BaseModel):
    title: Optional[str] = None
    type: Optional[str] = "page"
    body: Optional[ContentBodyWrapper] = None
    version: Optional[ContentVersion] = None


@app.put(BASE + "/content/{content_id}")
def update_content(content_id: str, body: ContentUpdateBody):
    storage_value = body.body.storage.value if body.body else None
    version_number = body.version.number if body.version else None
    result = confluence_data.update_content(
        content_id, title=body.title, body=storage_value, version_number=version_number,
    )
    if "error" in result:
        status = 409 if result.get("conflict") else 404
        return JSONResponse(status_code=status, content=result)
    return result


@app.get(BASE + "/content/{content_id}/child/page")
def list_child_pages(content_id: str, limit: int = Query(25, ge=1, le=100)):
    result = confluence_data.list_child_pages(content_id, limit=limit)
    if isinstance(result, dict) and "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.get(BASE + "/content/{content_id}/label")
def list_labels(content_id: str):
    result = confluence_data.list_labels(content_id)
    if isinstance(result, dict) and "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.get(BASE + "/content/{content_id}/child/comment")
def list_comments(content_id: str):
    result = confluence_data.list_comments(content_id)
    if isinstance(result, dict) and "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result
