"""FastAPI server wrapping openlibrary_data module as REST endpoints.

Implements a subset of the Open Library API (openlibrary.org): search, works,
editions, authors, subjects, and ISBN lookup.
"""

from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from typing import Optional

import openlibrary_data
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

app = FastAPI(title="Open Library API (Mock)", version="v1")
install_tracker(app)
install_admin_plane(app, store=openlibrary_data._store)
@app.get("/health")
def health():
    return {"status": "ok"}


# --- Search ---

@app.get("/search.json")
def search(
    q: Optional[str] = None,
    author: Optional[str] = None,
    title: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
):
    return openlibrary_data.search(q=q, author=author, title=title, page=page, limit=limit)


# --- Works ---

@app.get("/works/{work_id}.json")
def get_work(work_id: str):
    result = openlibrary_data.get_work(work_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.get("/works/{work_id}/editions.json")
def get_work_editions(work_id: str):
    result = openlibrary_data.get_work_editions(work_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Authors ---

@app.get("/authors/{author_id}.json")
def get_author(author_id: str):
    result = openlibrary_data.get_author(author_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.get("/authors/{author_id}/works.json")
def get_author_works(author_id: str):
    result = openlibrary_data.get_author_works(author_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Subjects ---

@app.get("/subjects/{subject}.json")
def get_subject(subject: str):
    return openlibrary_data.get_subject(subject)


# --- ISBN ---

@app.get("/isbn/{isbn}.json")
def get_isbn(isbn: str):
    result = openlibrary_data.get_isbn(isbn)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result
