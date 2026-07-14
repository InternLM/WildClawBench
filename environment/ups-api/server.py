"""FastAPI server wrapping ups_data module as REST endpoints.

Mirrors a subset of the UPS REST APIs: rating, shipping (label creation),
and tracking. Write operations post their fields in the request body;
responses are wrapped in UPS-style envelopes (RateResponse, ShipmentResponse,
trackResponse).
"""

from fastapi import FastAPI, Body
from fastapi.responses import JSONResponse
from typing import Optional

import ups_data
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

app = FastAPI(title="UPS API (Mock)", version="v1")
install_tracker(app)
install_admin_plane(app, store=ups_data._store)
@app.get("/health")
def health():
    return {"status": "ok"}


# --- Rating ---

@app.post("/api/rating/v1/Rate")
def rate(
    origin_zip: str = Body(..., embed=True),
    dest_zip: str = Body(..., embed=True),
    weight_lb: float = Body(1.0, embed=True),
    service_code: Optional[str] = Body(None, embed=True),
):
    result = ups_data.get_rate(origin_zip, dest_zip, weight_lb, service_code=service_code)
    if isinstance(result, dict) and "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Shipping (create label) ---

@app.post("/api/shipments/v1/ship")
def create_shipment(
    origin_zip: str = Body(..., embed=True),
    dest_zip: str = Body(..., embed=True),
    weight_lb: float = Body(1.0, embed=True),
    service_code: str = Body("03", embed=True),
):
    result = ups_data.create_shipment(origin_zip, dest_zip, weight_lb, service_code=service_code)
    if isinstance(result, dict) and "error" in result:
        return JSONResponse(status_code=400, content=result)
    return result


# --- Tracking ---

@app.get("/api/track/v1/details/{tracking_number}")
def track(tracking_number: str):
    result = ups_data.track(tracking_number)
    if isinstance(result, dict) and "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result
