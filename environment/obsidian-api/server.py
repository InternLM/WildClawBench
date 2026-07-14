"""FastAPI server wrapping obsidian_data module as REST endpoints.

Loosely mirrors the Obsidian Local REST API plugin's vault routes.
"""

from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional

import obsidian_data
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

app = FastAPI(title="Obsidian API (Mock)", version="1.0.0")
install_tracker(app)
install_admin_plane(app, store=obsidian_data._store)
@app.get("/health")
def health():
    return {"status": "ok"}


# --- Vault ---

@app.get("/vault")
def get_vault():
    return obsidian_data.get_vault()


# --- Notes ---

@app.get("/vault/notes")
def list_notes(folder: Optional[str] = None, tag: Optional[str] = None):
    return obsidian_data.list_notes(folder=folder, tag=tag)


@app.get("/vault/notes/{path:path}")
def get_note(path: str):
    result = obsidian_data.get_note(path)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


class NoteCreateBody(BaseModel):
    path: str
    content: str


@app.post("/vault/notes", status_code=201)
def create_note(body: NoteCreateBody):
    result = obsidian_data.create_note(body.path, body.content)
    if "error" in result:
        return JSONResponse(status_code=409, content=result)
    return result


class NoteUpdateBody(BaseModel):
    content: Optional[str] = None
    append: Optional[str] = None


@app.put("/vault/notes/{path:path}")
def update_note(path: str, body: NoteUpdateBody):
    result = obsidian_data.update_note(path, content=body.content, append=body.append)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.delete("/vault/notes/{path:path}")
def delete_note(path: str):
    result = obsidian_data.delete_note(path)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Search / links ---

@app.get("/vault/search")
def search(query: str = Query(...), content: bool = False):
    return obsidian_data.search(query, content=content)


@app.get("/vault/backlinks/{path:path}")
def list_backlinks(path: str):
    return obsidian_data.list_backlinks(path)


@app.get("/vault/daily/{date_str}")
def get_daily(date_str: str):
    result = obsidian_data.get_daily(date_str)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result
