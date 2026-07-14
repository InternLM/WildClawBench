"""FastAPI server for the Google Contacts API (Mock) mock service."""

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any

import contacts_data as data
try:
    from tracking_middleware import install_tracker
    from admin_plane import install_admin_plane
except ModuleNotFoundError:
    def install_tracker(app):
        return None

    def install_admin_plane(app, store=None, one_shot_registry=None):
        return None

app = FastAPI(title="Google Contacts API (Mock)", version="v1")
install_tracker(app)
install_admin_plane(app, store=data._store)


@app.get("/health")
def health():
    return {"status": "ok"}


class _Body(BaseModel):
    class Config:
        extra = "allow"


@app.get("/contacts")
def list_contacts():
    return {"contacts": data.list_table("contacts")}


@app.get("/contacts/{item_id}")
def get_contacts(item_id: str):
    r = data.get_row("contacts", item_id)
    return r if r else JSONResponse(status_code=404, content={"error": "not found"})


@app.post("/contacts", status_code=201)
def create_contacts(body: _Body):
    return data.create_row("contacts", body.model_dump())


@app.get("/contact_groups")
def list_contact_groups():
    return {"contact_groups": data.list_table("contact_groups")}
