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
except ModuleNotFoundError:  # standalone run without the shared module on sys.path
    def install_tracker(app):  # no-op fallback: audit endpoints disabled
        return None

app = FastAPI(title="Dropbox API v2 (Mock)", version="2")
install_tracker(app)


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
