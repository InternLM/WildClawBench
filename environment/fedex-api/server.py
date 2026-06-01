"""FastAPI server wrapping fedex_data module as REST endpoints.

Mirrors a subset of the FedEx Web Services REST APIs: rate quotes,
shipment (label) creation, and tracking. Like the real FedEx API, write
operations post their fields in the request body and responses are wrapped
in `{"output": {...}}` envelopes.
"""

from fastapi import FastAPI, Body
from fastapi.responses import JSONResponse
from typing import Optional

import fedex_data
try:
    from tracking_middleware import install_tracker
except ModuleNotFoundError:  # standalone run without the shared module on sys.path
    def install_tracker(app):  # no-op fallback: audit endpoints disabled
        return None

app = FastAPI(title="FedEx API (Mock)", version="v1")
install_tracker(app)


@app.get("/health")
def health():
    return {"status": "ok"}


# --- Rate quotes ---

@app.post("/rate/v1/rates/quotes")
def rate_quotes(
    origin_zip: str = Body(..., embed=True),
    dest_zip: str = Body(..., embed=True),
    weight_lb: float = Body(1.0, embed=True),
    service_type: Optional[str] = Body(None, embed=True),
):
    result = fedex_data.get_rate_quote(origin_zip, dest_zip, weight_lb, service_type=service_type)
    if isinstance(result, dict) and "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Shipments (create label) ---

@app.post("/ship/v1/shipments")
def create_shipment(
    origin_zip: str = Body(..., embed=True),
    dest_zip: str = Body(..., embed=True),
    weight_lb: float = Body(1.0, embed=True),
    service_type: str = Body("FEDEX_GROUND", embed=True),
):
    result = fedex_data.create_shipment(origin_zip, dest_zip, weight_lb, service_type=service_type)
    if isinstance(result, dict) and "error" in result:
        return JSONResponse(status_code=400, content=result)
    return result


# --- Tracking ---

@app.post("/track/v1/trackingnumbers")
def track(tracking_number: str = Body(..., embed=True)):
    result = fedex_data.track(tracking_number)
    if isinstance(result, dict) and "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result
