"""FastAPI server wrapping amadeus_data module as REST endpoints.

Implements a subset of the Amadeus Self-Service APIs (flight offers search,
reference data, pricing).
"""

from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

import amadeus_data
try:
    from tracking_middleware import install_tracker
except ModuleNotFoundError:  # standalone run without the shared module on sys.path
    def install_tracker(app):  # no-op fallback: audit endpoints disabled
        return None

app = FastAPI(title="Amadeus API (Mock)", version="v2")
install_tracker(app)


@app.get("/health")
def health():
    return {"status": "ok"}


# --- Flight offers search ---

@app.get("/v2/shopping/flight-offers")
def flight_offers(
    originLocationCode: str = Query(...),
    destinationLocationCode: str = Query(...),
    departureDate: Optional[str] = None,
    adults: int = Query(1, ge=1, le=9),
    max: int = Query(50, ge=1, le=250),
):
    return amadeus_data.search_flight_offers(
        origin=originLocationCode,
        destination=destinationLocationCode,
        departure_date=departureDate,
        adults=adults,
        max_results=max,
    )


# --- Flight offers pricing ---

class PricingData(BaseModel):
    type: Optional[str] = "flight-offers-pricing"
    flightOffers: List[Dict[str, Any]]


class PricingBody(BaseModel):
    data: PricingData


@app.post("/v1/shopping/flight-offers/pricing")
def price_offer(body: PricingBody):
    offers = body.data.flightOffers
    if not offers:
        return JSONResponse(status_code=400, content={"error": "No flight offers supplied"})
    result = amadeus_data.price_flight_offer(offers[0])
    if "error" in result:
        return JSONResponse(status_code=400, content=result)
    return result


# --- Reference data: locations ---

@app.get("/v1/reference-data/locations")
def locations(
    keyword: Optional[str] = None,
    subType: str = Query("AIRPORT,CITY"),
):
    return amadeus_data.search_locations(keyword=keyword, sub_type=subType)


@app.get("/v1/reference-data/locations/{location_id}")
def location(location_id: str):
    result = amadeus_data.get_location(location_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Reference data: airlines ---

@app.get("/v1/reference-data/airlines")
def airlines(airlineCodes: Optional[str] = None):
    return amadeus_data.get_airlines(airline_codes=airlineCodes)
