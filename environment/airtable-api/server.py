"""FastAPI server wrapping airtable_data module as REST endpoints.

Implements a subset of the Airtable Web API. Meta base path: /v0/meta,
records base path: /v0/{baseId}/{tableIdOrName}.
"""

from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

import airtable_data
try:
    from tracking_middleware import install_tracker
except ModuleNotFoundError:  # standalone run without the shared module on sys.path
    def install_tracker(app):  # no-op fallback: audit endpoints disabled
        return None

app = FastAPI(title="Airtable API (Mock)", version="0.1.0")
install_tracker(app)


@app.get("/health")
def health():
    return {"status": "ok"}


# --- Meta ---

@app.get("/v0/meta/bases")
def list_bases():
    return airtable_data.list_bases()


@app.get("/v0/meta/bases/{base_id}/tables")
def list_tables(base_id: str):
    result = airtable_data.list_tables(base_id)
    if isinstance(result, dict) and "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Records ---

@app.get("/v0/{base_id}/{table_id_or_name}")
def list_records(
    base_id: str,
    table_id_or_name: str,
    pageSize: int = Query(100, ge=1, le=100),
    offset: Optional[str] = None,
    filterByFormula: Optional[str] = None,
):
    result = airtable_data.list_records(
        base_id, table_id_or_name,
        page_size=pageSize, offset=offset, filter_by_formula=filterByFormula,
    )
    if isinstance(result, dict) and "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.get("/v0/{base_id}/{table_id_or_name}/{record_id}")
def get_record(base_id: str, table_id_or_name: str, record_id: str):
    result = airtable_data.get_record(base_id, table_id_or_name, record_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


class RecordItem(BaseModel):
    fields: Dict[str, Any] = {}


class RecordsCreateBody(BaseModel):
    records: List[RecordItem]


@app.post("/v0/{base_id}/{table_id_or_name}", status_code=200)
def create_records(base_id: str, table_id_or_name: str, body: RecordsCreateBody):
    result = airtable_data.create_records(
        base_id, table_id_or_name,
        [{"fields": r.fields} for r in body.records],
    )
    if isinstance(result, dict) and "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


class RecordPatchBody(BaseModel):
    fields: Dict[str, Any] = {}


@app.patch("/v0/{base_id}/{table_id_or_name}/{record_id}")
def update_record(base_id: str, table_id_or_name: str, record_id: str, body: RecordPatchBody):
    result = airtable_data.update_record(base_id, table_id_or_name, record_id, body.fields)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.delete("/v0/{base_id}/{table_id_or_name}/{record_id}")
def delete_record(base_id: str, table_id_or_name: str, record_id: str):
    result = airtable_data.delete_record(base_id, table_id_or_name, record_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result
