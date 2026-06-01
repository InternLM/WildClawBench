"""FastAPI server wrapping maps_data module as REST endpoints.

Implements a subset of the Google Maps Platform web services. Base path:
/maps/api. Responses use Google-style `{"status": "OK", ...}` envelopes.
"""

from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from typing import Optional

import maps_data
try:
    from tracking_middleware import install_tracker
except ModuleNotFoundError:  # standalone run without the shared module on sys.path
    def install_tracker(app):  # no-op fallback: audit endpoints disabled
        return None

app = FastAPI(title="Google Maps API (Mock)", version="1.0.0")
install_tracker(app)


@app.get("/health")
def health():
    return {"status": "ok"}


# --- Places ---

@app.get("/maps/api/place/textsearch/json")
def text_search(query: str = Query(...)):
    return maps_data.text_search(query)


@app.get("/maps/api/place/details/json")
def place_details(place_id: str = Query(...)):
    result = maps_data.place_details(place_id)
    if result["status"] == "NOT_FOUND":
        return JSONResponse(status_code=404, content=result)
    return result


@app.get("/maps/api/place/nearbysearch/json")
def nearby_search(
    location: str = Query(...),
    radius: int = Query(5000, ge=1),
    type: Optional[str] = None,
):
    result = maps_data.nearby_search(location, radius=radius, place_type=type)
    if result["status"] == "INVALID_REQUEST":
        return JSONResponse(status_code=400, content=result)
    return result


# --- Geocoding ---

@app.get("/maps/api/geocode/json")
def geocode(address: str = Query(...)):
    return maps_data.geocode(address)


# --- Directions / distance matrix ---

@app.get("/maps/api/directions/json")
def directions(
    origin: str = Query(...),
    destination: str = Query(...),
    mode: str = "driving",
):
    result = maps_data.directions(origin, destination, mode=mode)
    if result["status"] == "NOT_FOUND":
        return JSONResponse(status_code=404, content=result)
    return result


@app.get("/maps/api/distancematrix/json")
def distance_matrix(
    origins: str = Query(...),
    destinations: str = Query(...),
    mode: str = "driving",
):
    origin_list = [o.strip() for o in origins.split("|") if o.strip()]
    dest_list = [d.strip() for d in destinations.split("|") if d.strip()]
    return maps_data.distance_matrix(origin_list, dest_list, mode=mode)
