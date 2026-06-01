"""FastAPI server wrapping nasa_data module as REST endpoints.

Implements a subset of the NASA Open APIs (api.nasa.gov): APOD, Mars Rover
Photos, NeoWs feed, and EPIC natural imagery.
"""

from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from typing import Optional

import nasa_data
try:
    from tracking_middleware import install_tracker
except ModuleNotFoundError:  # standalone run without the shared module on sys.path
    def install_tracker(app):  # no-op fallback: audit endpoints disabled
        return None

app = FastAPI(title="NASA Open API (Mock)", version="v1")
install_tracker(app)


@app.get("/health")
def health():
    return {"status": "ok"}


# --- APOD (Astronomy Picture of the Day) ---

@app.get("/planetary/apod")
def apod(
    date: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
):
    result = nasa_data.get_apod(date=date, start_date=start_date, end_date=end_date)
    if isinstance(result, dict) and "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Mars Rover Photos ---

@app.get("/mars-photos/api/v1/rovers/{rover}/photos")
def rover_photos(
    rover: str,
    sol: Optional[int] = None,
    camera: Optional[str] = None,
    earth_date: Optional[str] = None,
):
    result = nasa_data.get_rover_photos(rover, sol=sol, camera=camera, earth_date=earth_date)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.get("/mars-photos/api/v1/rovers/{rover}")
def rover_manifest(rover: str):
    result = nasa_data.get_rover_manifest(rover)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- NeoWs (Near Earth Object Web Service) ---

@app.get("/neo/rest/v1/feed")
def neo_feed(start_date: Optional[str] = None, end_date: Optional[str] = None):
    return nasa_data.get_neo_feed(start_date=start_date, end_date=end_date)


@app.get("/neo/rest/v1/neo/{neo_id}")
def neo(neo_id: str):
    result = nasa_data.get_neo(neo_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- EPIC (Earth Polychromatic Imaging Camera) ---

@app.get("/EPIC/api/natural")
def epic_natural():
    return nasa_data.get_epic_natural()
