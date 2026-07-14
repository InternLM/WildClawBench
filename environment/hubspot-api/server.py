"""FastAPI server wrapping hubspot_data module as REST endpoints.

Mirrors a subset of the HubSpot CRM v3 API. Base path: /crm/v3
Create/update use the HubSpot {"properties": {...}} body shape.
"""

from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any

import hubspot_data
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

app = FastAPI(title="HubSpot CRM API (Mock)", version="v3")
install_tracker(app)
install_admin_plane(app, store=hubspot_data._store)
@app.get("/health")
def health():
    return {"status": "ok"}


class ObjectBody(BaseModel):
    properties: Dict[str, Any] = {}


# --- Contacts ---

@app.get("/crm/v3/objects/contacts")
def list_contacts(limit: int = Query(10, ge=1, le=100), after: Optional[str] = None):
    return hubspot_data.list_contacts(limit=limit, after=after)


@app.get("/crm/v3/objects/contacts/{contact_id}")
def get_contact(contact_id: str):
    result = hubspot_data.get_contact(contact_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.post("/crm/v3/objects/contacts", status_code=201)
def create_contact(body: ObjectBody):
    return hubspot_data.create_contact(body.properties)


@app.patch("/crm/v3/objects/contacts/{contact_id}")
def update_contact(contact_id: str, body: ObjectBody):
    result = hubspot_data.update_contact(contact_id, body.properties)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Companies ---

@app.get("/crm/v3/objects/companies")
def list_companies(limit: int = Query(10, ge=1, le=100), after: Optional[str] = None):
    return hubspot_data.list_companies(limit=limit, after=after)


@app.get("/crm/v3/objects/companies/{company_id}")
def get_company(company_id: str):
    result = hubspot_data.get_company(company_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Deals ---

@app.get("/crm/v3/objects/deals")
def list_deals(limit: int = Query(10, ge=1, le=100), after: Optional[str] = None):
    return hubspot_data.list_deals(limit=limit, after=after)


@app.get("/crm/v3/objects/deals/{deal_id}")
def get_deal(deal_id: str):
    result = hubspot_data.get_deal(deal_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.post("/crm/v3/objects/deals", status_code=201)
def create_deal(body: ObjectBody):
    return hubspot_data.create_deal(body.properties)


@app.patch("/crm/v3/objects/deals/{deal_id}")
def update_deal(deal_id: str, body: ObjectBody):
    result = hubspot_data.update_deal(deal_id, body.properties)
    if "error" in result:
        status = 404 if result.get("category") == "OBJECT_NOT_FOUND" else 400
        return JSONResponse(status_code=status, content=result)
    return result


# --- Pipelines ---

@app.get("/crm/v3/pipelines/deals")
def list_deal_pipelines():
    return hubspot_data.list_deal_pipelines()
