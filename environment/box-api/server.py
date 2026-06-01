"""FastAPI server wrapping box_data module as REST endpoints.

Mirrors a subset of the Box Content API. Base path: /2.0
"""

from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from typing import Optional

import box_data
try:
    from tracking_middleware import install_tracker
except ModuleNotFoundError:  # standalone run without the shared module on sys.path
    def install_tracker(app):  # no-op fallback: audit endpoints disabled
        return None

app = FastAPI(title="Box API (Mock)", version="2.0")
install_tracker(app)


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


# --- Search ---

@app.get("/2.0/search")
def search(
    query: Optional[str] = None,
    type: Optional[str] = None,
    limit: int = Query(100),
    offset: int = Query(0),
):
    return box_data.search(query=query, type_filter=type, limit=limit, offset=offset)
