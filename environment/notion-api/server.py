"""FastAPI server wrapping notion_data module as REST endpoints.

Implements a subset of the Notion API v1 surface. Base path: /v1
"""

from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

import notion_data
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

app = FastAPI(title="Notion API (Mock)", version="2022-06-28")
install_tracker(app)
install_admin_plane(app, store=notion_data._store)
@app.get("/health")
def health():
    return {"status": "ok"}


# --- Users ---

@app.get("/v1/users")
def list_users(start_cursor: Optional[str] = None, page_size: int = Query(50, ge=1, le=100)):
    return notion_data.list_users(start_cursor=start_cursor, page_size=page_size)


@app.get("/v1/users/me")
def get_me():
    return notion_data.get_me()


@app.get("/v1/users/{user_id}")
def get_user(user_id: str):
    result = notion_data.get_user(user_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Workspace ---

@app.get("/v1/workspace")
def get_workspace():
    return notion_data.get_workspace()


# --- Search ---

class SearchBody(BaseModel):
    query: Optional[str] = None
    filter: Optional[Dict[str, Any]] = None
    sort: Optional[Dict[str, Any]] = None
    start_cursor: Optional[str] = None
    page_size: int = 50


@app.post("/v1/search")
def search(body: SearchBody):
    filter_value = None
    if body.filter and body.filter.get("property") == "object":
        filter_value = body.filter.get("value")
    return notion_data.search(
        query=body.query,
        filter_value=filter_value,
        start_cursor=body.start_cursor,
        page_size=body.page_size,
    )


# --- Databases ---

@app.get("/v1/databases/{database_id}")
def get_database(database_id: str):
    result = notion_data.get_database(database_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


class DatabaseQueryBody(BaseModel):
    filter: Optional[Dict[str, Any]] = None
    sorts: Optional[List[Dict[str, Any]]] = None
    start_cursor: Optional[str] = None
    page_size: int = 50


@app.post("/v1/databases/{database_id}/query")
def query_database(database_id: str, body: DatabaseQueryBody):
    filter_status = None
    filter_assignee = None
    if body.filter:
        prop = body.filter.get("property")
        if prop == "Status":
            filter_status = (body.filter.get("status") or {}).get("equals")
        elif prop == "Assignee":
            filter_assignee = (body.filter.get("people") or {}).get("contains")
    sort_by = None
    if body.sorts:
        first = body.sorts[0]
        if first.get("timestamp") in ("last_edited_time", "created_time"):
            sort_by = first["timestamp"]
    result = notion_data.query_database(
        database_id,
        filter_status=filter_status,
        filter_assignee=filter_assignee,
        sort_by=sort_by,
        start_cursor=body.start_cursor,
        page_size=body.page_size,
    )
    if isinstance(result, dict) and "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Pages ---

@app.get("/v1/pages/{page_id}")
def get_page(page_id: str):
    result = notion_data.get_page(page_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


class PageParent(BaseModel):
    type: str  # "database_id", "page_id", "workspace"
    database_id: Optional[str] = None
    page_id: Optional[str] = None
    workspace: Optional[bool] = None


class PageCreateBody(BaseModel):
    parent: PageParent
    title: str
    properties: Optional[Dict[str, Any]] = None
    created_by: Optional[str] = None


@app.post("/v1/pages", status_code=201)
def create_page(body: PageCreateBody):
    if body.parent.type == "database_id":
        parent_type = "database"
        parent_id = body.parent.database_id
    elif body.parent.type == "page_id":
        parent_type = "page"
        parent_id = body.parent.page_id
    elif body.parent.type == "workspace":
        parent_type = "workspace"
        parent_id = notion_data.get_workspace()["id"]
    else:
        return JSONResponse(status_code=400, content={"error": f"Unsupported parent.type {body.parent.type}"})

    if not parent_id:
        return JSONResponse(status_code=400, content={"error": "Parent id missing"})

    result = notion_data.create_page(
        parent_type=parent_type,
        parent_id=parent_id,
        title=body.title,
        properties=body.properties,
        created_by=body.created_by or "user-amelia",
    )
    if "error" in result:
        return JSONResponse(status_code=400, content=result)
    return result


class PageUpdateBody(BaseModel):
    title: Optional[str] = None
    archived: Optional[bool] = None
    properties: Optional[Dict[str, Any]] = None


@app.patch("/v1/pages/{page_id}")
def update_page(page_id: str, body: PageUpdateBody):
    result = notion_data.update_page(
        page_id,
        title=body.title,
        archived=body.archived,
        properties=body.properties,
    )
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.delete("/v1/pages/{page_id}")
def delete_page(page_id: str):
    result = notion_data.delete_page(page_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Blocks ---

@app.get("/v1/blocks/{block_id}/children")
def list_block_children(block_id: str, start_cursor: Optional[str] = None,
                        page_size: int = Query(50, ge=1, le=100)):
    return notion_data.list_block_children(block_id, start_cursor=start_cursor, page_size=page_size)


class BlockChild(BaseModel):
    type: str
    text: Optional[str] = ""
    checked: Optional[bool] = None


class AppendBlocksBody(BaseModel):
    children: List[BlockChild]


@app.patch("/v1/blocks/{block_id}/children")
def append_block_children(block_id: str, body: AppendBlocksBody):
    result = notion_data.append_block_children(block_id, [c.model_dump() for c in body.children])
    if isinstance(result, dict) and "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


class BlockUpdateBody(BaseModel):
    text: Optional[str] = None
    checked: Optional[bool] = None


@app.patch("/v1/blocks/{block_id}")
def update_block(block_id: str, body: BlockUpdateBody):
    result = notion_data.update_block(block_id, text=body.text, checked=body.checked)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.delete("/v1/blocks/{block_id}")
def delete_block(block_id: str):
    result = notion_data.delete_block(block_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Comments ---

@app.get("/v1/comments")
def list_comments(block_id: Optional[str] = None, page_id: Optional[str] = None):
    return notion_data.list_comments(block_id=block_id, page_id=page_id)


class CommentParent(BaseModel):
    page_id: str
    block_id: Optional[str] = None


class CommentCreateBody(BaseModel):
    parent: CommentParent
    author_id: str
    text: str


@app.post("/v1/comments", status_code=201)
def create_comment(body: CommentCreateBody):
    result = notion_data.create_comment(
        parent_page_id=body.parent.page_id,
        parent_block_id=body.parent.block_id,
        author_id=body.author_id,
        text=body.text,
    )
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result
