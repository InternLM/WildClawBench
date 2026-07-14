"""FastAPI server wrapping uber_data module as REST endpoints.

Implements a subset of the Uber Rides API surface. Base path: /v1.2
"""

from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional

import uber_data
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

app = FastAPI(title="Uber API (Mock)", version="1.2.0")
install_tracker(app)
install_admin_plane(app, store=uber_data._store)
@app.get("/health")
def health():
    return {"status": "ok"}


# --- Products ---

@app.get("/v1.2/products")
def list_products(latitude: float = Query(...), longitude: float = Query(...)):
    return uber_data.list_products(latitude=latitude, longitude=longitude)


@app.get("/v1.2/products/{product_id}")
def get_product(product_id: str):
    result = uber_data.get_product(product_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Estimates ---

@app.get("/v1.2/estimates/price")
def price_estimates(
    start_latitude: float = Query(...),
    start_longitude: float = Query(...),
    end_latitude: float = Query(...),
    end_longitude: float = Query(...),
):
    return uber_data.price_estimates(
        start_latitude, start_longitude, end_latitude, end_longitude)


@app.get("/v1.2/estimates/time")
def time_estimates(
    start_latitude: float = Query(...),
    start_longitude: float = Query(...),
    product_id: Optional[str] = None,
):
    return uber_data.time_estimates(start_latitude, start_longitude, product_id=product_id)


# --- Ride requests ---

class RequestBody(BaseModel):
    product_id: str
    start_latitude: float
    start_longitude: float
    end_latitude: Optional[float] = None
    end_longitude: Optional[float] = None
    rider_id: Optional[str] = None


@app.post("/v1.2/requests", status_code=201)
def create_request(body: RequestBody):
    result = uber_data.create_request(
        product_id=body.product_id,
        start_latitude=body.start_latitude,
        start_longitude=body.start_longitude,
        end_latitude=body.end_latitude,
        end_longitude=body.end_longitude,
        rider_id=body.rider_id,
    )
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.get("/v1.2/requests/{request_id}")
def get_request(request_id: str):
    result = uber_data.get_request(request_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.delete("/v1.2/requests/{request_id}")
def cancel_request(request_id: str):
    result = uber_data.cancel_request(request_id)
    if "error" in result:
        return JSONResponse(status_code=400, content=result)
    return result


# --- History ---

@app.get("/v1.2/history")
def get_history(
    rider_id: Optional[str] = None,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    return uber_data.get_history(rider_id=rider_id, limit=limit, offset=offset)


# --- Rider profile ---

@app.get("/v1.2/me")
def get_me():
    return uber_data.get_me()
