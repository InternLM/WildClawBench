"""FastAPI server wrapping webflow_data module as REST endpoints.

Mirrors a subset of the Webflow Data API v2 (api.webflow.com/v2): sites,
collections, and CMS collection items (list + create). Items carry a
`fieldData` object as in the real v2 API.
"""

from fastapi import FastAPI, Query, Body
from fastapi.responses import JSONResponse
from typing import Optional

import webflow_data
try:
    from tracking_middleware import install_tracker
except ModuleNotFoundError:  # standalone run without the shared module on sys.path
    def install_tracker(app):  # no-op fallback: audit endpoints disabled
        return None

app = FastAPI(title="Webflow Data API (Mock)", version="v2")
install_tracker(app)


@app.get("/health")
def health():
    return {"status": "ok"}


# --- Sites ---

@app.get("/v2/sites")
def list_sites():
    return webflow_data.list_sites()


@app.get("/v2/sites/{site_id}")
def get_site(site_id: str):
    result = webflow_data.get_site(site_id)
    if isinstance(result, dict) and "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Collections ---

@app.get("/v2/sites/{site_id}/collections")
def list_collections(site_id: str):
    result = webflow_data.list_collections(site_id)
    if isinstance(result, dict) and "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Collection items ---

@app.get("/v2/collections/{collection_id}/items")
def list_items(
    collection_id: str,
    limit: int = Query(default=100),
    offset: int = Query(default=0),
):
    result = webflow_data.list_items(collection_id, limit=limit, offset=offset)
    if isinstance(result, dict) and "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.post("/v2/collections/{collection_id}/items", status_code=202)
def create_item(collection_id: str, payload: dict = Body(default={})):
    result = webflow_data.create_item(
        collection_id,
        field_data=payload.get("fieldData") or {},
        is_draft=payload.get("isDraft", False),
        is_archived=payload.get("isArchived", False),
    )
    if isinstance(result, dict) and "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result
