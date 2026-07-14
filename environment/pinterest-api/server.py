"""FastAPI server wrapping pinterest_data module as REST endpoints."""

from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional

import pinterest_data
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

app = FastAPI(title="Pinterest API v5 (Mock)", version="5.0.0")
install_tracker(app)
install_admin_plane(app, store=pinterest_data._store)
@app.get("/health")
def health():
    return {"status": "ok"}


# --- User Account ---

@app.get("/v5/user_account")
def get_user_account():
    return pinterest_data.get_user_account()


@app.get("/v5/user_account/analytics")
def get_user_analytics(
    start_date: Optional[str] = Query(default=None),
    end_date: Optional[str] = Query(default=None),
):
    return pinterest_data.get_user_analytics(start_date=start_date, end_date=end_date)


# --- Boards ---

@app.get("/v5/boards")
def list_boards(
    privacy: Optional[str] = Query(default=None),
    limit: int = Query(default=25, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    return pinterest_data.list_boards(privacy=privacy, limit=limit, offset=offset)


@app.get("/v5/boards/{board_id}")
def get_board(board_id: str):
    result = pinterest_data.get_board(board_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


class BoardCreateBody(BaseModel):
    name: str
    description: Optional[str] = None
    privacy: Optional[str] = None


@app.post("/v5/boards", status_code=201)
def create_board(body: BoardCreateBody):
    result = pinterest_data.create_board(body.model_dump())
    if "error" in result:
        return JSONResponse(status_code=400, content=result)
    return result


class BoardUpdateBody(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    privacy: Optional[str] = None


@app.patch("/v5/boards/{board_id}")
def update_board(board_id: str, body: BoardUpdateBody):
    data = {k: v for k, v in body.model_dump().items() if v is not None}
    result = pinterest_data.update_board(board_id, data)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.delete("/v5/boards/{board_id}")
def delete_board(board_id: str):
    result = pinterest_data.delete_board(board_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.get("/v5/boards/{board_id}/pins")
def list_board_pins(
    board_id: str,
    limit: int = Query(default=25, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    result = pinterest_data.list_board_pins(board_id, limit=limit, offset=offset)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Board Sections ---

@app.get("/v5/boards/{board_id}/sections")
def list_board_sections(board_id: str):
    result = pinterest_data.list_board_sections(board_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


class BoardSectionCreateBody(BaseModel):
    name: str


@app.post("/v5/boards/{board_id}/sections", status_code=201)
def create_board_section(board_id: str, body: BoardSectionCreateBody):
    result = pinterest_data.create_board_section(board_id, body.model_dump())
    if "error" in result:
        return JSONResponse(status_code=400, content=result)
    return result


@app.get("/v5/boards/{board_id}/sections/{section_id}/pins")
def list_section_pins(
    board_id: str,
    section_id: str,
    limit: int = Query(default=25, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    result = pinterest_data.list_section_pins(board_id, section_id, limit=limit, offset=offset)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Pins ---

@app.get("/v5/pins")
def list_pins(
    limit: int = Query(default=25, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    return pinterest_data.list_pins(limit=limit, offset=offset)


@app.get("/v5/pins/{pin_id}")
def get_pin(pin_id: str):
    result = pinterest_data.get_pin(pin_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


class PinCreateBody(BaseModel):
    board_id: str
    title: str
    description: Optional[str] = None
    link: Optional[str] = None
    media_type: Optional[str] = None
    board_section_id: Optional[str] = None
    dominant_color: Optional[str] = None
    alt_text: Optional[str] = None


@app.post("/v5/pins", status_code=201)
def create_pin(body: PinCreateBody):
    result = pinterest_data.create_pin(body.model_dump())
    if "error" in result:
        return JSONResponse(status_code=400, content=result)
    return result


class PinUpdateBody(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    link: Optional[str] = None
    board_id: Optional[str] = None
    board_section_id: Optional[str] = None
    alt_text: Optional[str] = None


@app.patch("/v5/pins/{pin_id}")
def update_pin(pin_id: str, body: PinUpdateBody):
    data = {k: v for k, v in body.model_dump().items() if v is not None}
    result = pinterest_data.update_pin(pin_id, data)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.delete("/v5/pins/{pin_id}")
def delete_pin(pin_id: str):
    result = pinterest_data.delete_pin(pin_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.get("/v5/pins/{pin_id}/analytics")
def get_pin_analytics(
    pin_id: str,
    start_date: Optional[str] = Query(default=None),
    end_date: Optional[str] = Query(default=None),
):
    result = pinterest_data.get_pin_analytics(pin_id, start_date=start_date, end_date=end_date)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Search ---

@app.get("/v5/search/pins")
def search_pins(
    query: str = Query(...),
    limit: int = Query(default=25, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    return pinterest_data.search_pins(query=query, limit=limit, offset=offset)


# --- Media ---

@app.get("/v5/media/{media_id}")
def get_media_upload_status(media_id: str):
    result = pinterest_data.get_media_upload_status(media_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Ad Accounts ---

@app.get("/v5/ad_accounts")
def list_ad_accounts(
    limit: int = Query(default=25, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    return pinterest_data.list_ad_accounts(limit=limit, offset=offset)


@app.get("/v5/ad_accounts/{ad_account_id}")
def get_ad_account(ad_account_id: str):
    result = pinterest_data.get_ad_account(ad_account_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.get("/v5/ad_accounts/{ad_account_id}/campaigns")
def list_campaigns(
    ad_account_id: str,
    status: Optional[str] = Query(default=None),
    limit: int = Query(default=25, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    result = pinterest_data.list_campaigns(ad_account_id, status=status, limit=limit, offset=offset)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result
