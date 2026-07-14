"""FastAPI server wrapping monday_data module as REST endpoints.

The real monday.com API is GraphQL; this mock exposes a REST-shaped surface for
consistency with the other Kensei2 environments. Base path: /v2
"""

from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any

import monday_data
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

app = FastAPI(title="monday.com API (Mock)", version="v2")
install_tracker(app)
install_admin_plane(app, store=monday_data._store)
@app.get("/health")
def health():
    return {"status": "ok"}


# --- Workspaces ---

@app.get("/v2/workspaces")
def workspaces():
    return monday_data.list_workspaces()


# --- Boards ---

@app.get("/v2/boards")
def boards(workspace_id: Optional[str] = None):
    return monday_data.list_boards(workspace_id=workspace_id)


@app.get("/v2/boards/{board_id}")
def get_board(board_id: str):
    result = monday_data.get_board(board_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.get("/v2/boards/{board_id}/items")
def board_items(board_id: str):
    result = monday_data.get_board_items(board_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Items ---

@app.get("/v2/items")
def list_items(board_id: Optional[str] = None, group_id: Optional[str] = None):
    return monday_data.list_items(board_id=board_id, group_id=group_id)


class ItemCreateBody(BaseModel):
    board_id: str
    item_name: str
    group_id: Optional[str] = None
    column_values: Optional[Dict[str, Any]] = None


@app.post("/v2/items", status_code=201)
def create_item(body: ItemCreateBody):
    result = monday_data.create_item(
        board_id=body.board_id,
        name=body.item_name,
        group_id=body.group_id,
        column_values=body.column_values,
    )
    if "error" in result:
        return JSONResponse(status_code=400, content=result)
    return result


@app.get("/v2/items/{item_id}")
def get_item(item_id: str):
    result = monday_data.get_item(item_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


class ItemUpdateBody(BaseModel):
    column_id: Optional[str] = None
    text: Optional[str] = None
    value: Optional[str] = None
    group_id: Optional[str] = None


@app.put("/v2/items/{item_id}")
def update_item(item_id: str, body: ItemUpdateBody):
    result = monday_data.update_item(
        item_id,
        column_id=body.column_id,
        text=body.text,
        value=body.value,
        group_id=body.group_id,
    )
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.delete("/v2/items/{item_id}")
def delete_item(item_id: str):
    result = monday_data.delete_item(item_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Users ---

@app.get("/v2/users")
def users():
    return monday_data.list_users()
