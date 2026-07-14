"""FastAPI server wrapping dropbox_data module as REST endpoints.

Mirrors a subset of the Dropbox API v2 (api.dropboxapi.com). Like the real
Dropbox API, endpoints are POST and accept their arguments as a JSON body.
"""

from fastapi import FastAPI, Body
from fastapi.responses import JSONResponse
from typing import Optional

import dropbox_data
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

app = FastAPI(title="Dropbox API v2 (Mock)", version="2")
install_tracker(app)
install_admin_plane(app, store=dropbox_data._store)
@app.get("/health")
def health():
    return {"status": "ok"}


# --- Users ---

@app.post("/2/users/get_current_account")
def get_current_account():
    return dropbox_data.get_current_account()


# --- Files ---

@app.post("/2/files/list_folder")
def list_folder(body: Optional[dict] = Body(default=None)):
    body = body or {}
    result = dropbox_data.list_folder(
        path=body.get("path", ""),
        recursive=bool(body.get("recursive", False)),
    )
    if isinstance(result, dict) and "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.post("/2/files/get_metadata")
def get_metadata(body: Optional[dict] = Body(default=None)):
    body = body or {}
    result = dropbox_data.get_metadata(path=body.get("path"))
    if isinstance(result, dict) and "error" in result:
        return JSONResponse(status_code=409, content=result)
    return result


@app.post("/2/files/download")
def download_file(body: Optional[dict] = Body(default=None)):
    body = body or {}
    try:
        return dropbox_data.download_file_content(path=body.get("path"))
    except dropbox_data.DownloadError as e:
        return JSONResponse(
            status_code=e.http_status,
            content={"error_summary": f"{e.code}/", "error": {".tag": e.code},
                     "message": e.message},
        )


@app.post("/2/files/search_v2")
def search_v2(body: Optional[dict] = Body(default=None)):
    body = body or {}
    options = body.get("options") or {}
    result = dropbox_data.search_v2(
        query=body.get("query"),
        path=options.get("path", ""),
    )
    if isinstance(result, dict) and "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Sharing ---

@app.post("/2/sharing/list_shared_links")
def list_shared_links(body: Optional[dict] = Body(default=None)):
    body = body or {}
    result = dropbox_data.list_shared_links(path=body.get("path"))
    if isinstance(result, dict) and "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result
