"""FastAPI server wrapping zillow_data module as REST endpoints."""

from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional

import zillow_data
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

app = FastAPI(title="Zillow API (Mock)", version="1.0.0")
install_tracker(app)
install_admin_plane(app, store=zillow_data._store)
@app.get("/health")
def health():
    return {"status": "ok"}


# --- Properties ---

@app.get("/v1/properties/search")
def search_properties(
    city: Optional[str] = None,
    state: Optional[str] = None,
    zipcode: Optional[str] = None,
    min_price: Optional[int] = None,
    max_price: Optional[int] = None,
    min_beds: Optional[int] = None,
    min_baths: Optional[float] = None,
    home_type: Optional[str] = None,
    status: Optional[str] = "FOR_SALE",
    limit: int = Query(25, ge=1, le=100),
    offset: int = Query(0, ge=0),
    sort_by: str = "list_price",
    sort_order: str = "asc",
):
    return zillow_data.search_properties(
        city=city, state=state, zipcode=zipcode, min_price=min_price,
        max_price=max_price, min_beds=min_beds, min_baths=min_baths,
        home_type=home_type, status=status, limit=limit, offset=offset,
        sort_by=sort_by, sort_order=sort_order,
    )


@app.get("/v1/properties/{zpid}")
def get_property(zpid: int):
    result = zillow_data.get_property(zpid)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.get("/v1/properties/{zpid}/zestimate")
def get_zestimate(zpid: int):
    result = zillow_data.get_zestimate(zpid)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.get("/v1/properties/{zpid}/price-history")
def get_price_history(zpid: int):
    result = zillow_data.get_price_history(zpid)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Agents ---

@app.get("/v1/agents")
def list_agents(city: Optional[str] = None, state: Optional[str] = None):
    return zillow_data.list_agents(city=city, state=state)


@app.get("/v1/agents/{agent_id}")
def get_agent(agent_id: str):
    result = zillow_data.get_agent(agent_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Saved searches ---

@app.get("/v1/users/{user_id}/saved-searches")
def list_saved_searches(user_id: str):
    results = zillow_data.list_saved_searches(user_id)
    return {"count": len(results), "results": results}


class SavedSearchBody(BaseModel):
    name: str
    city: Optional[str] = None
    state: Optional[str] = None
    min_price: int = 0
    max_price: int = 10_000_000
    min_beds: int = 0
    min_baths: float = 0.0
    home_type: Optional[str] = ""


@app.post("/v1/users/{user_id}/saved-searches", status_code=201)
def create_saved_search(user_id: str, body: SavedSearchBody):
    return zillow_data.create_saved_search(
        user_id=user_id,
        name=body.name,
        city=body.city,
        state=body.state,
        min_price=body.min_price,
        max_price=body.max_price,
        min_beds=body.min_beds,
        min_baths=body.min_baths,
        home_type=body.home_type or "",
    )


@app.delete("/v1/saved-searches/{search_id}")
def delete_saved_search(search_id: str):
    result = zillow_data.delete_saved_search(search_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result
