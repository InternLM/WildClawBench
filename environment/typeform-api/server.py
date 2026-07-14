"""FastAPI server wrapping typeform_data module as REST endpoints.

Mirrors a subset of the Typeform Create + Responses API surface.
"""

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

import typeform_data
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

app = FastAPI(title="Typeform API (Mock)", version="v1")
install_tracker(app)
install_admin_plane(app, store=typeform_data._store)
@app.get("/health")
def health():
    return {"status": "ok"}


# --- Forms ---

@app.get("/forms")
def list_forms():
    return typeform_data.list_forms()


class FormBody(BaseModel):
    title: str
    workspace: Optional[str] = "ws-orbit-labs"
    language: Optional[str] = "en"
    is_public: Optional[bool] = False
    fields: Optional[List[Dict[str, Any]]] = None


@app.post("/forms", status_code=201)
def create_form(body: FormBody):
    return typeform_data.create_form(body.model_dump(exclude_none=True))


@app.get("/forms/{form_id}")
def get_form(form_id: str):
    result = typeform_data.get_form(form_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


class FormUpdateBody(BaseModel):
    title: Optional[str] = None
    language: Optional[str] = None
    is_public: Optional[bool] = None


@app.put("/forms/{form_id}")
def update_form(form_id: str, body: FormUpdateBody):
    result = typeform_data.update_form(form_id, body.model_dump(exclude_none=True))
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.delete("/forms/{form_id}")
def delete_form(form_id: str):
    result = typeform_data.delete_form(form_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Responses ---

@app.get("/forms/{form_id}/responses")
def list_responses(form_id: str, completed: Optional[bool] = None):
    result = typeform_data.list_responses(form_id, completed=completed)
    if isinstance(result, dict) and "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Insights ---

@app.get("/forms/{form_id}/insights/summary")
def insights_summary(form_id: str):
    result = typeform_data.insights_summary(form_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result
