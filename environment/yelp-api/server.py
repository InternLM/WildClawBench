"""FastAPI server wrapping yelp_data module as REST endpoints.

Implements a subset of the Yelp Fusion API. Base path: /v3
"""

from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from typing import Optional

import yelp_data
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

app = FastAPI(title="Yelp Fusion API (Mock)", version="3.0.0")
install_tracker(app)
install_admin_plane(app, store=yelp_data._store)
@app.get("/health")
def health():
    return {"status": "ok"}


# --- Businesses ---

@app.get("/v3/businesses/search")
def search_businesses(
    term: Optional[str] = None,
    location: Optional[str] = None,
    categories: Optional[str] = None,
    price: Optional[str] = None,
    sort_by: str = "best_match",
    limit: int = Query(20, ge=1, le=50),
    offset: int = Query(0, ge=0),
):
    return yelp_data.search_businesses(
        term=term, location=location, categories=categories, price=price,
        sort_by=sort_by, limit=limit, offset=offset,
    )


@app.get("/v3/businesses/{business_id}")
def get_business(business_id: str):
    result = yelp_data.get_business(business_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.get("/v3/businesses/{business_id}/reviews")
def get_business_reviews(business_id: str):
    result = yelp_data.get_business_reviews(business_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Categories ---

@app.get("/v3/categories")
def list_categories():
    return yelp_data.list_categories()
