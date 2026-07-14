"""FastAPI server wrapping activecampaign_data module as REST endpoints.

Mirrors a subset of the ActiveCampaign API v3. Base path: /api/3
List responses include a `meta` block with the total count.
"""

from fastapi import FastAPI, Query, Body
from fastapi.responses import JSONResponse
from typing import Optional

import activecampaign_data
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

app = FastAPI(title="ActiveCampaign API (Mock)", version="3")
install_tracker(app)
install_admin_plane(app, store=activecampaign_data._store)
@app.get("/health")
def health():
    return {"status": "ok"}


# --- Contacts ---

@app.get("/api/3/contacts")
def list_contacts(
    email: Optional[str] = Query(default=None),
    status: Optional[str] = Query(default=None),
    limit: int = Query(default=20),
    offset: int = Query(default=0),
):
    return activecampaign_data.list_contacts(
        email=email, status=status, limit=limit, offset=offset
    )


@app.get("/api/3/contacts/{contact_id}")
def get_contact(contact_id: str):
    result = activecampaign_data.get_contact(contact_id)
    if isinstance(result, dict) and "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.post("/api/3/contacts", status_code=201)
def create_contact(payload: dict = Body(default={})):
    data = payload.get("contact") or {}
    result = activecampaign_data.create_contact(
        email=data.get("email"),
        first_name=data.get("firstName", ""),
        last_name=data.get("lastName", ""),
        phone=data.get("phone", ""),
        status=data.get("status", "1"),
    )
    if isinstance(result, dict) and "error" in result:
        code = 422 if result["error"] in ("validation", "duplicate") else 404
        return JSONResponse(status_code=code, content=result)
    return result


# --- Lists ---

@app.get("/api/3/lists")
def list_lists(limit: int = Query(default=20), offset: int = Query(default=0)):
    return activecampaign_data.list_lists(limit=limit, offset=offset)


# --- Campaigns ---

@app.get("/api/3/campaigns")
def list_campaigns(limit: int = Query(default=20), offset: int = Query(default=0)):
    return activecampaign_data.list_campaigns(limit=limit, offset=offset)


# --- Deals ---

@app.get("/api/3/deals")
def list_deals(limit: int = Query(default=20), offset: int = Query(default=0)):
    return activecampaign_data.list_deals(limit=limit, offset=offset)
