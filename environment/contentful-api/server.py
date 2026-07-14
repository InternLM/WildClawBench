"""FastAPI server wrapping contentful_data module as REST endpoints.

Implements a subset of the Contentful Content Management API. Most routes live
under /spaces/{space_id}/environments/{env_id}/...
"""

from fastapi import FastAPI, Query, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any

import contentful_data
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

app = FastAPI(title="Contentful API (Mock)", version="0.1.0")
install_tracker(app)
install_admin_plane(app, store=contentful_data._store)
@app.get("/health")
def health():
    return {"status": "ok"}


# --- Space ---

@app.get("/spaces/{space_id}")
def get_space(space_id: str):
    return contentful_data.get_space()


# --- Content types ---

@app.get("/spaces/{space_id}/environments/{env_id}/content_types")
def list_content_types(space_id: str, env_id: str):
    return contentful_data.list_content_types()


@app.get("/spaces/{space_id}/environments/{env_id}/content_types/{content_type_id}")
def get_content_type(space_id: str, env_id: str, content_type_id: str):
    result = contentful_data.get_content_type(content_type_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Entries ---

@app.get("/spaces/{space_id}/environments/{env_id}/entries")
def list_entries(
    space_id: str,
    env_id: str,
    request: Request,
    content_type: Optional[str] = None,
    limit: int = Query(100, ge=1, le=1000),
    skip: int = Query(0, ge=0),
):
    # Collect any fields.X=value query params for simple equality filtering.
    field_filters = {}
    for key, value in request.query_params.items():
        if key.startswith("fields."):
            field_filters[key[len("fields."):]] = value
    return contentful_data.list_entries(
        content_type=content_type,
        field_filters=field_filters or None,
        limit=limit,
        skip=skip,
    )


@app.get("/spaces/{space_id}/environments/{env_id}/entries/{entry_id}")
def get_entry(space_id: str, env_id: str, entry_id: str):
    result = contentful_data.get_entry(entry_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


class EntryCreateBody(BaseModel):
    content_type: str
    fields: Dict[str, Any] = {}


@app.post("/spaces/{space_id}/environments/{env_id}/entries", status_code=201)
def create_entry(space_id: str, env_id: str, body: EntryCreateBody):
    result = contentful_data.create_entry(body.content_type, body.fields)
    if "error" in result:
        return JSONResponse(status_code=400, content=result)
    return result


class EntryUpdateBody(BaseModel):
    fields: Dict[str, Any] = {}


@app.put("/spaces/{space_id}/environments/{env_id}/entries/{entry_id}")
def update_entry(space_id: str, env_id: str, entry_id: str, body: EntryUpdateBody):
    result = contentful_data.update_entry(entry_id, body.fields)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.delete("/spaces/{space_id}/environments/{env_id}/entries/{entry_id}")
def delete_entry(space_id: str, env_id: str, entry_id: str):
    result = contentful_data.delete_entry(entry_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Assets ---

@app.get("/spaces/{space_id}/environments/{env_id}/assets")
def list_assets(space_id: str, env_id: str):
    return contentful_data.list_assets()


@app.get("/spaces/{space_id}/environments/{env_id}/assets/{asset_id}")
def get_asset(space_id: str, env_id: str, asset_id: str):
    result = contentful_data.get_asset(asset_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result
