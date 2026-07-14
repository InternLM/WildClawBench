"""FastAPI server wrapping box_data module as REST endpoints.

Mirrors a subset of the Box Content API. Base path: /2.0
"""

from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from typing import Optional

import box_data
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

app = FastAPI(title="Box API (Mock)", version="2.0")
install_tracker(app)
install_admin_plane(app, store=box_data._store)
@app.get("/health")
def health():
    return {"status": "ok"}


# --- Users ---

@app.get("/2.0/users/me")
def get_me():
    return box_data.get_me()


# --- Folders ---

@app.get("/2.0/folders/{folder_id}")
def get_folder(folder_id: str):
    result = box_data.get_folder(folder_id)
    if isinstance(result, dict) and "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.get("/2.0/folders/{folder_id}/items")
def get_folder_items(
    folder_id: str,
    limit: int = Query(100),
    offset: int = Query(0),
):
    result = box_data.get_folder_items(folder_id, limit=limit, offset=offset)
    if isinstance(result, dict) and "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Files ---

@app.get("/2.0/files/{file_id}")
def get_file(file_id: str):
    result = box_data.get_file(file_id)
    if isinstance(result, dict) and "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.get("/2.0/files/{file_id}/content")
def download_file(file_id: str):
    try:
        return box_data.download_file_content(file_id)
    except box_data.DownloadError as e:
        return JSONResponse(
            status_code=e.http_status,
            content={"type": "error", "status": e.http_status,
                     "code": e.code, "message": e.message},
        )


# --- Search ---

@app.get("/2.0/search")
def search(
    query: Optional[str] = None,
    type: Optional[str] = None,
    limit: int = Query(100),
    offset: int = Query(0),
):
    return box_data.search(query=query, type_filter=type, limit=limit, offset=offset)
