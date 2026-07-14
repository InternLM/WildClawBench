"""FastAPI server wrapping openweather_data module as REST endpoints.

Implements a subset of the OpenWeather API. Data base path: /data/2.5,
geocoding base path: /geo/1.0. Responses use OpenWeather-style JSON shapes.
"""

from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from typing import Optional

import openweather_data
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

app = FastAPI(title="OpenWeather API (Mock)", version="2.5")
install_tracker(app)
install_admin_plane(app, store=openweather_data._store)
@app.get("/health")
def health():
    return {"status": "ok"}


# --- Current weather ---

@app.get("/data/2.5/weather")
def current_weather(
    q: Optional[str] = None,
    lat: Optional[float] = None,
    lon: Optional[float] = None,
):
    result = openweather_data.get_current_weather(q=q, lat=lat, lon=lon)
    cod = str(result.get("cod"))
    if cod == "404":
        return JSONResponse(status_code=404, content=result)
    if cod == "400":
        return JSONResponse(status_code=400, content=result)
    return result


# --- Forecast ---

@app.get("/data/2.5/forecast")
def forecast(
    q: Optional[str] = None,
    lat: Optional[float] = None,
    lon: Optional[float] = None,
):
    result = openweather_data.get_forecast(q=q, lat=lat, lon=lon)
    cod = str(result.get("cod"))
    if cod == "404":
        return JSONResponse(status_code=404, content=result)
    if cod == "400":
        return JSONResponse(status_code=400, content=result)
    return result


# --- Geocoding ---

@app.get("/geo/1.0/direct")
def geocode_direct(q: str = Query(...), limit: int = Query(5, ge=1, le=10)):
    return openweather_data.geocode_direct(q, limit=limit)
