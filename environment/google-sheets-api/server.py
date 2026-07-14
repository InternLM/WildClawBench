"""FastAPI server for the Google Sheets API (Mock) mock service."""

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any

import sheets_data as data
try:
    from tracking_middleware import install_tracker
    from admin_plane import install_admin_plane
except ModuleNotFoundError:
    def install_tracker(app):
        return None

    def install_admin_plane(app, store=None, one_shot_registry=None):
        return None

app = FastAPI(title="Google Sheets API (Mock)", version="v1")
install_tracker(app)
install_admin_plane(app, store=data._store)


@app.get("/health")
def health():
    return {"status": "ok"}


class _Body(BaseModel):
    class Config:
        extra = "allow"


@app.get("/spreadsheets")
def list_spreadsheets():
    return {"spreadsheets": data.list_table("spreadsheets")}


@app.get("/spreadsheets/{item_id}")
def get_spreadsheets(item_id: str):
    r = data.get_row("spreadsheets", item_id)
    return r if r else JSONResponse(status_code=404, content={"error": "not found"})


@app.post("/spreadsheets", status_code=201)
def create_spreadsheets(body: _Body):
    return data.create_row("spreadsheets", body.model_dump())


@app.get("/sheet_values")
def list_sheet_data():
    return {"sheet_data": data.list_table("sheet_data")}
