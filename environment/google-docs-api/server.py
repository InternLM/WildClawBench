"""FastAPI server for the Google Docs API (Mock) mock service."""

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any

import docs_data as data
try:
    from tracking_middleware import install_tracker
    from admin_plane import install_admin_plane
except ModuleNotFoundError:
    def install_tracker(app):
        return None

    def install_admin_plane(app, store=None, one_shot_registry=None):
        return None

app = FastAPI(title="Google Docs API (Mock)", version="v1")
install_tracker(app)
install_admin_plane(app, store=data._store)


@app.get("/health")
def health():
    return {"status": "ok"}


class _Body(BaseModel):
    class Config:
        extra = "allow"


@app.get("/documents")
def list_documents():
    return {"documents": data.list_table("documents")}


@app.get("/documents/{item_id}")
def get_documents(item_id: str):
    r = data.get_row("documents", item_id)
    return r if r else JSONResponse(status_code=404, content={"error": "not found"})


@app.post("/documents", status_code=201)
def create_documents(body: _Body):
    return data.create_row("documents", body.model_dump())


@app.patch("/documents/{item_id}")
def update_documents(item_id: str, body: _Body):
    r = data.update_row("documents", item_id, body.model_dump())
    return r if r else JSONResponse(status_code=404, content={"error": "not found"})
