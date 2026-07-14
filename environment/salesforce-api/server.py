"""FastAPI server wrapping salesforce_data module as REST endpoints.

Implements a subset of the Salesforce REST API. Base path:
/services/data/v59.0  — generic sObject CRUD for Account, Contact, Lead,
Opportunity plus a simplified SOQL /query endpoint.
"""

from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any

import salesforce_data
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

app = FastAPI(title="Salesforce REST API (Mock)", version="v59.0")
install_tracker(app)
install_admin_plane(app, store=salesforce_data._store)
BASE = "/services/data/v59.0"


@app.get("/health")
def health():
    return {"status": "ok"}


# --- Generic sObject CRUD ---

@app.get(BASE + "/sobjects/{sobject}")
def list_records(sobject: str, limit: int = Query(200, ge=1, le=2000)):
    result = salesforce_data.list_records(sobject, limit=limit)
    if isinstance(result, dict) and "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.get(BASE + "/sobjects/{sobject}/{record_id}")
def get_record(sobject: str, record_id: str):
    result = salesforce_data.get_record(sobject, record_id)
    if isinstance(result, dict) and "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


class SObjectBody(BaseModel):
    fields: Optional[Dict[str, Any]] = None

    class Config:
        extra = "allow"


def _extract_fields(body: SObjectBody) -> Dict[str, Any]:
    # Accept either {"fields": {...}} or top-level field keys directly.
    data = body.model_dump(exclude_none=False)
    if data.get("fields"):
        return data["fields"]
    data.pop("fields", None)
    return {k: v for k, v in data.items() if v is not None}


@app.post(BASE + "/sobjects/{sobject}", status_code=201)
def create_record(sobject: str, body: SObjectBody):
    result = salesforce_data.create_record(sobject, _extract_fields(body))
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.patch(BASE + "/sobjects/{sobject}/{record_id}", status_code=204)
def update_record(sobject: str, record_id: str, body: SObjectBody):
    result = salesforce_data.update_record(sobject, record_id, _extract_fields(body))
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    # Salesforce returns 204 No Content on a successful PATCH.
    return JSONResponse(status_code=204, content=None)


# --- SOQL query ---

@app.get(BASE + "/query")
def soql_query(q: str = Query(..., description="SOQL query string")):
    result = salesforce_data.query(q)
    if isinstance(result, dict) and "error" in result:
        status = 404 if result["error"].startswith("INVALID_TYPE") else 400
        return JSONResponse(status_code=status, content=result)
    return result
