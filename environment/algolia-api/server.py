"""FastAPI server wrapping algolia_data module as REST endpoints.

Implements a subset of the Algolia Search API. Routes live under /1/...
"""

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any

import algolia_data
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

app = FastAPI(title="Algolia API (Mock)", version="0.1.0")
install_tracker(app)
install_admin_plane(app, store=algolia_data._store)
@app.get("/health")
def health():
    return {"status": "ok"}


# --- Indices ---

@app.get("/1/indexes")
def list_indexes():
    return algolia_data.list_indexes()


@app.get("/1/indexes/{index}/settings")
def get_settings(index: str):
    result = algolia_data.get_settings(index)
    if isinstance(result, dict) and "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Query ---

class QueryBody(BaseModel):
    query: Optional[str] = None
    filters: Optional[str] = None
    hitsPerPage: int = 20
    page: int = 0


@app.post("/1/indexes/{index}/query")
def query_index(index: str, body: QueryBody):
    result = algolia_data.query_index(
        index,
        query=body.query,
        filters=body.filters,
        hits_per_page=body.hitsPerPage,
        page=body.page,
    )
    if isinstance(result, dict) and "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Records ---

@app.get("/1/indexes/{index}/{object_id}")
def get_object(index: str, object_id: str):
    result = algolia_data.get_object(index, object_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.post("/1/indexes/{index}", status_code=201)
def add_object(index: str, body: Dict[str, Any]):
    result = algolia_data.add_object(index, body)
    if isinstance(result, dict) and "error" in result:
        return JSONResponse(status_code=400, content=result)
    return result


@app.put("/1/indexes/{index}/{object_id}")
def update_object(index: str, object_id: str, body: Dict[str, Any]):
    result = algolia_data.update_object(index, object_id, body)
    if isinstance(result, dict) and "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.delete("/1/indexes/{index}/{object_id}")
def delete_object(index: str, object_id: str):
    result = algolia_data.delete_object(index, object_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result
