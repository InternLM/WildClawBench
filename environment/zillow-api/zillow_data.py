"""Data access module for the Zillow API mock service."""

import csv
import uuid
from copy import deepcopy
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).parent


def _load(filename):
    with open(DATA_DIR / filename, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _now():
    return datetime.utcnow().strftime("%Y-%m-%d")


def _coerce_properties(rows):
    out = []
    for r in rows:
        out.append({
            **r,
            "zpid": int(r["zpid"]),
            "latitude": float(r["latitude"]),
            "longitude": float(r["longitude"]),
            "bedrooms": int(r["bedrooms"]),
            "bathrooms": float(r["bathrooms"]),
            "living_area_sqft": int(r["living_area_sqft"]),
            "lot_size_sqft": int(r["lot_size_sqft"]),
            "year_built": int(r["year_built"]),
            "list_price": int(r["list_price"]),
            "zestimate": int(r["zestimate"]),
            "rent_zestimate": int(r["rent_zestimate"]),
            "days_on_zillow": int(r["days_on_zillow"]),
        })
    return out


def _coerce_price_history(rows):
    out = []
    for r in rows:
        out.append({
            **r,
            "zpid": int(r["zpid"]),
            "price": float(r["price"]),
            "price_per_sqft": float(r["price_per_sqft"]),
        })
    return out


def _coerce_agents(rows):
    out = []
    for r in rows:
        out.append({
            **r,
            "active_listings": int(r["active_listings"]),
            "sold_last_12mo": int(r["sold_last_12mo"]),
            "rating": float(r["rating"]),
            "reviews": int(r["reviews"]),
        })
    return out


def _coerce_saved_searches(rows):
    out = []
    for r in rows:
        out.append({
            **r,
            "min_price": int(r["min_price"]),
            "max_price": int(r["max_price"]),
            "min_beds": int(r["min_beds"]),
            "min_baths": float(r["min_baths"]),
            "city": r["city"] or None,
        })
    return out


_properties = _coerce_properties(_load("properties.csv"))
_price_history = _coerce_price_history(_load("price_history.csv"))
_agents = _coerce_agents(_load("agents.csv"))
_saved_searches = _coerce_saved_searches(_load("saved_searches.csv"))

_properties_store = deepcopy(_properties)
_price_history_store = deepcopy(_price_history)
_agents_store = deepcopy(_agents)
_saved_searches_store = deepcopy(_saved_searches)


def _new_search_id():
    return f"search-{uuid.uuid4().hex[:8]}"


# ---------------------------------------------------------------------------
# Properties
# ---------------------------------------------------------------------------

def search_properties(city=None, state=None, zipcode=None, min_price=None, max_price=None,
                      min_beds=None, min_baths=None, home_type=None, status="FOR_SALE",
                      limit=25, offset=0, sort_by="list_price", sort_order="asc"):
    results = list(_properties_store)
    if status:
        results = [p for p in results if p["status"].upper() == status.upper()]
    if city:
        results = [p for p in results if p["city"].lower() == city.lower()]
    if state:
        results = [p for p in results if p["state"].upper() == state.upper()]
    if zipcode:
        results = [p for p in results if p["zipcode"] == zipcode]
    if min_price is not None:
        results = [p for p in results if p["list_price"] >= min_price]
    if max_price is not None:
        results = [p for p in results if p["list_price"] <= max_price]
    if min_beds is not None:
        results = [p for p in results if p["bedrooms"] >= min_beds]
    if min_baths is not None:
        results = [p for p in results if p["bathrooms"] >= min_baths]
    if home_type:
        results = [p for p in results if p["home_type"].lower() == home_type.lower()]

    sort_key = sort_by if sort_by in {"list_price", "zestimate", "days_on_zillow", "living_area_sqft"} else "list_price"
    reverse = sort_order.lower() == "desc"
    results.sort(key=lambda p: p[sort_key], reverse=reverse)

    total = len(results)
    page = results[offset: offset + limit]
    return {
        "total": total,
        "count": len(page),
        "offset": offset,
        "limit": limit,
        "results": page,
    }


def get_property(zpid):
    for p in _properties_store:
        if p["zpid"] == zpid:
            return p
    return {"error": f"Property {zpid} not found"}


def get_zestimate(zpid):
    p = get_property(zpid)
    if "error" in p:
        return p
    return {
        "zpid": p["zpid"],
        "address": p["address"],
        "zestimate": p["zestimate"],
        "rent_zestimate": p["rent_zestimate"],
        "list_price": p["list_price"],
        "delta_pct": round((p["zestimate"] - p["list_price"]) / p["list_price"] * 100, 2),
    }


def get_price_history(zpid):
    if not any(p["zpid"] == zpid for p in _properties_store):
        return {"error": f"Property {zpid} not found"}
    events = [e for e in _price_history_store if e["zpid"] == zpid]
    events.sort(key=lambda e: e["event_date"], reverse=True)
    return {"zpid": zpid, "count": len(events), "history": events}


# ---------------------------------------------------------------------------
# Agents
# ---------------------------------------------------------------------------

def list_agents(city=None, state=None):
    # Filter by city/state via the properties they list
    if not city and not state:
        return {"count": len(_agents_store), "agents": _agents_store}

    matching_ids = set()
    for p in _properties_store:
        if city and p["city"].lower() != city.lower():
            continue
        if state and p["state"].upper() != state.upper():
            continue
        matching_ids.add(p["listing_agent_id"])
    agents = [a for a in _agents_store if a["agent_id"] in matching_ids]
    return {"count": len(agents), "agents": agents}


def get_agent(agent_id):
    for a in _agents_store:
        if a["agent_id"] == agent_id:
            listings = [p for p in _properties_store
                        if p["listing_agent_id"] == agent_id and p["status"] == "FOR_SALE"]
            return {**a, "listings": listings}
    return {"error": f"Agent {agent_id} not found"}


# ---------------------------------------------------------------------------
# Saved searches
# ---------------------------------------------------------------------------

def list_saved_searches(user_id):
    return [s for s in _saved_searches_store if s["user_id"] == user_id]


def create_saved_search(user_id, name, city=None, state=None,
                        min_price=0, max_price=10000000, min_beds=0, min_baths=0.0,
                        home_type=""):
    search = {
        "search_id": _new_search_id(),
        "user_id": user_id,
        "name": name,
        "city": city or None,
        "state": state or "",
        "min_price": int(min_price),
        "max_price": int(max_price),
        "min_beds": int(min_beds),
        "min_baths": float(min_baths),
        "home_type": home_type,
        "created_at": _now(),
    }
    _saved_searches_store.append(search)
    return search


def delete_saved_search(search_id):
    for i, s in enumerate(_saved_searches_store):
        if s["search_id"] == search_id:
            _saved_searches_store.pop(i)
            return {"deleted": True, "search_id": search_id}
    return {"error": f"Saved search {search_id} not found"}
