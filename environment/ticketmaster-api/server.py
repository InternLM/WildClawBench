"""FastAPI server wrapping ticketmaster_data module as REST endpoints.

Mirrors a subset of the Ticketmaster Discovery API v2. Base path: /discovery/v2
List responses use the {"_embedded": {...}, "page": {...}} shape.
"""

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from typing import Optional

import ticketmaster_data
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

app = FastAPI(title="Ticketmaster Discovery API (Mock)", version="v2")
install_tracker(app)
install_admin_plane(app, store=ticketmaster_data._store)
def _page(items, key):
    size = len(items)
    return {
        "_embedded": {key: items},
        "page": {"size": size, "totalElements": size, "totalPages": 1, "number": 0},
    }


@app.get("/health")
def health():
    return {"status": "ok"}


# --- Events ---

@app.get("/discovery/v2/events")
def search_events(keyword: Optional[str] = None, city: Optional[str] = None,
                  classificationName: Optional[str] = None,
                  startDateTime: Optional[str] = None):
    events = ticketmaster_data.search_events(
        keyword=keyword, city=city, classification_name=classificationName,
        start_datetime=startDateTime)
    return _page(events, "events")


@app.get("/discovery/v2/events/{event_id}")
def get_event(event_id: str):
    result = ticketmaster_data.get_event(event_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Venues ---

@app.get("/discovery/v2/venues")
def search_venues(keyword: Optional[str] = None):
    venues = ticketmaster_data.search_venues(keyword=keyword)
    return _page(venues, "venues")


@app.get("/discovery/v2/venues/{venue_id}")
def get_venue(venue_id: str):
    result = ticketmaster_data.get_venue(venue_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Attractions ---

@app.get("/discovery/v2/attractions")
def search_attractions(keyword: Optional[str] = None):
    attractions = ticketmaster_data.search_attractions(keyword=keyword)
    return _page(attractions, "attractions")


@app.get("/discovery/v2/attractions/{attraction_id}")
def get_attraction(attraction_id: str):
    result = ticketmaster_data.get_attraction(attraction_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Classifications ---

@app.get("/discovery/v2/classifications")
def list_classifications():
    classifications = ticketmaster_data.list_classifications()
    return _page(classifications, "classifications")
