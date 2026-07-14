"""FastAPI server wrapping shippo_data module as REST endpoints.

Mirrors a subset of the Shippo shipping API surface.
"""

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any, Union

import shippo_data
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

app = FastAPI(title="Shippo API (Mock)", version="2018-02-08")
install_tracker(app)
install_admin_plane(app, store=shippo_data._store)
@app.get("/health")
def health():
    return {"status": "ok"}


# --- Addresses ---

class AddressBody(BaseModel):
    name: str
    company: Optional[str] = ""
    street1: str
    street2: Optional[str] = ""
    city: str
    state: str
    zip: str
    country: str = "US"
    phone: Optional[str] = ""
    email: Optional[str] = ""
    is_residential: Optional[bool] = False


@app.post("/addresses", status_code=201)
def create_address(body: AddressBody):
    return shippo_data.create_address(body.model_dump())


@app.get("/addresses/{object_id}")
def get_address(object_id: str):
    result = shippo_data.get_address(object_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Shipments ---

class ShipmentBody(BaseModel):
    address_from: Union[str, Dict[str, Any]]
    address_to: Union[str, Dict[str, Any]]
    parcels: Optional[Union[str, Dict[str, Any], List[Any]]] = None


@app.post("/shipments", status_code=201)
def create_shipment(body: ShipmentBody):
    result = shippo_data.create_shipment(body.model_dump(exclude_none=True))
    if isinstance(result, dict) and "error" in result:
        return JSONResponse(status_code=400, content=result)
    return result


@app.get("/shipments/{object_id}")
def get_shipment(object_id: str):
    result = shippo_data.get_shipment(object_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.get("/shipments/{object_id}/rates")
def list_shipment_rates(object_id: str):
    result = shippo_data.list_shipment_rates(object_id)
    if isinstance(result, dict) and "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Transactions (labels) ---

class TransactionBody(BaseModel):
    rate: str
    label_file_type: Optional[str] = "PDF"
    async_: Optional[bool] = False


@app.post("/transactions", status_code=201)
def create_transaction(body: TransactionBody):
    result = shippo_data.create_transaction(body.model_dump())
    if isinstance(result, dict) and "error" in result:
        return JSONResponse(status_code=400, content=result)
    return result


@app.get("/transactions/{object_id}")
def get_transaction(object_id: str):
    result = shippo_data.get_transaction(object_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Tracking ---

@app.get("/tracks/{carrier}/{tracking_number}")
def get_tracking(carrier: str, tracking_number: str):
    result = shippo_data.get_tracking(carrier, tracking_number)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result
