"""FastAPI server wrapping airbnb_data module as REST endpoints.

Implements a subset of a lodging marketplace API surface. Base path: /v2
"""

from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional

import airbnb_data
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

app = FastAPI(title="Airbnb API (Mock)", version="2.0.0")
install_tracker(app)
install_admin_plane(app, store=airbnb_data._store)


@app.get("/health")
def health():
    return {"status": "ok"}


# --- Listings / search ---

@app.get("/v2/listings/search")
def search_listings(
    location: Optional[str] = None,
    checkin: Optional[str] = None,
    checkout: Optional[str] = None,
    guests: Optional[int] = Query(None, ge=1),
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
):
    return airbnb_data.search_listings(
        location=location, checkin=checkin, checkout=checkout,
        guests=guests, min_price=min_price, max_price=max_price)


@app.get("/v2/listings/{listing_id}")
def get_listing(listing_id: str):
    result = airbnb_data.get_listing(listing_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.get("/v2/listings/{listing_id}/availability")
def get_availability(listing_id: str):
    result = airbnb_data.get_availability(listing_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.get("/v2/listings/{listing_id}/reviews")
def get_reviews(listing_id: str):
    result = airbnb_data.get_reviews(listing_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Reservations ---

class ReservationBody(BaseModel):
    listing_id: str
    checkin: str
    checkout: str
    guests: int = 1
    guest_name: Optional[str] = "Guest"


@app.post("/v2/reservations", status_code=201)
def create_reservation(body: ReservationBody):
    result = airbnb_data.create_reservation(
        listing_id=body.listing_id,
        checkin=body.checkin,
        checkout=body.checkout,
        guests=body.guests,
        guest_name=body.guest_name or "Guest",
    )
    if "error" in result:
        status = 404 if "not found" in result["error"] else 400
        return JSONResponse(status_code=status, content=result)
    return result


@app.get("/v2/reservations/{reservation_id}")
def get_reservation(reservation_id: str):
    result = airbnb_data.get_reservation(reservation_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.delete("/v2/reservations/{reservation_id}")
def cancel_reservation(reservation_id: str):
    result = airbnb_data.cancel_reservation(reservation_id)
    if "error" in result:
        status = 404 if "not found" in result["error"] else 400
        return JSONResponse(status_code=status, content=result)
    return result
