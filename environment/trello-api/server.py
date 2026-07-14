"""FastAPI server wrapping trello_data module as REST endpoints.

Mirrors a subset of the Trello REST API. Base path: /1
Like the real Trello API, write operations take their fields as query params.
"""

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from typing import Optional

import trello_data
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

app = FastAPI(title="Trello API (Mock)", version="1")
install_tracker(app)
install_admin_plane(app, store=trello_data._store)
@app.get("/health")
def health():
    return {"status": "ok"}


# --- Members ---

@app.get("/1/members/me")
def get_me():
    return trello_data.get_me()


@app.get("/1/members/me/boards")
def list_my_boards():
    return trello_data.list_my_boards()


# --- Boards ---

@app.get("/1/boards/{board_id}")
def get_board(board_id: str):
    result = trello_data.get_board(board_id)
    if isinstance(result, dict) and "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.get("/1/boards/{board_id}/lists")
def list_board_lists(board_id: str):
    result = trello_data.list_board_lists(board_id)
    if isinstance(result, dict) and "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Lists -> cards ---

@app.get("/1/lists/{list_id}/cards")
def list_cards(list_id: str):
    result = trello_data.list_cards(list_id)
    if isinstance(result, dict) and "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Cards ---

@app.get("/1/cards/{card_id}")
def get_card(card_id: str):
    result = trello_data.get_card(card_id)
    if isinstance(result, dict) and "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.post("/1/cards", status_code=200)
def create_card(
    idList: str,
    name: str,
    desc: str = "",
    due: Optional[str] = None,
    idMembers: Optional[str] = None,
):
    members = [m for m in idMembers.split(",") if m] if idMembers else None
    result = trello_data.create_card(
        id_list=idList, name=name, desc=desc, due=due, member_ids=members,
    )
    if isinstance(result, dict) and "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.put("/1/cards/{card_id}")
def update_card(
    card_id: str,
    name: Optional[str] = None,
    desc: Optional[str] = None,
    idList: Optional[str] = None,
    due: Optional[str] = None,
    closed: Optional[bool] = None,
    pos: Optional[float] = None,
):
    result = trello_data.update_card(
        card_id, name=name, desc=desc, id_list=idList,
        due=due, closed=closed, pos=pos,
    )
    if isinstance(result, dict) and "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.delete("/1/cards/{card_id}")
def delete_card(card_id: str):
    result = trello_data.delete_card(card_id)
    if isinstance(result, dict) and "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Checklists ---

@app.get("/1/cards/{card_id}/checklists")
def list_card_checklists(card_id: str):
    result = trello_data.list_card_checklists(card_id)
    if isinstance(result, dict) and "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.post("/1/checklists", status_code=200)
def create_checklist(idCard: str, name: str = "Checklist"):
    result = trello_data.create_checklist(id_card=idCard, name=name)
    if isinstance(result, dict) and "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result
