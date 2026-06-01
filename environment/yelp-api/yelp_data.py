"""Data access module for the Yelp Fusion API mock service."""

import csv
from copy import deepcopy
from pathlib import Path

DATA_DIR = Path(__file__).parent

# price symbol -> integer level for sort/compare
_PRICE_LEVEL = {"$": 1, "$$": 2, "$$$": 3, "$$$$": 4}


def _load(filename):
    with open(DATA_DIR / filename, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _to_bool(v):
    return str(v).strip().lower() == "true"


# ---------------------------------------------------------------------------
# Load + coerce
# ---------------------------------------------------------------------------

def _coerce_businesses(rows):
    out = []
    for r in rows:
        out.append({
            "id": r["id"],
            "alias": r["id"],
            "name": r["name"],
            "rating": float(r["rating"]),
            "price": r["price"],
            "review_count": int(r["review_count"]),
            "is_closed": _to_bool(r["is_closed"]),
            "phone": r["phone"],
            "image_url": r["image_url"],
            "categories": [{"alias": r["category"], "title": r["category_title"]}],
            "coordinates": {"latitude": float(r["latitude"]), "longitude": float(r["longitude"])},
            "location": {
                "address1": r["address"],
                "city": r["city"],
                "state": r["state"],
                "display_address": [r["address"], f"{r['city']}, {r['state']}"],
            },
        })
    return out


def _coerce_reviews(rows):
    out = []
    for r in rows:
        out.append({
            "id": r["id"],
            "business_id": r["business_id"],
            "rating": int(r["rating"]),
            "text": r["text"],
            "time_created": r["time_created"],
            "user": {"name": r["user_name"]},
        })
    return out


def _coerce_categories(rows):
    return [{"alias": r["alias"], "title": r["title"], "parent_aliases": [r["parent"]]} for r in rows]


_businesses = _coerce_businesses(_load("businesses.csv"))
_reviews = _coerce_reviews(_load("reviews.csv"))
_categories = _coerce_categories(_load("categories.csv"))

_businesses_store = deepcopy(_businesses)
_reviews_store = deepcopy(_reviews)
_categories_store = deepcopy(_categories)


# ---------------------------------------------------------------------------
# Businesses
# ---------------------------------------------------------------------------

def search_businesses(term=None, location=None, categories=None, price=None,
                      sort_by="best_match", limit=20, offset=0):
    results = list(_businesses_store)
    if term:
        t = term.lower()
        results = [b for b in results
                   if t in b["name"].lower()
                   or any(t in c["title"].lower() or t in c["alias"].lower() for c in b["categories"])]
    if location:
        loc = location.lower()
        results = [b for b in results
                   if loc in b["location"]["city"].lower()
                   or loc in b["location"]["state"].lower()
                   or loc in b["location"]["address1"].lower()]
    if categories:
        wanted = {c.strip().lower() for c in categories.split(",") if c.strip()}
        results = [b for b in results
                   if any(c["alias"].lower() in wanted for c in b["categories"])]
    if price:
        wanted_levels = set()
        for p in price.split(","):
            p = p.strip()
            if p.isdigit():
                wanted_levels.add(int(p))
            elif p in _PRICE_LEVEL:
                wanted_levels.add(_PRICE_LEVEL[p])
        results = [b for b in results if _PRICE_LEVEL.get(b["price"], 0) in wanted_levels]

    if sort_by == "rating":
        results.sort(key=lambda b: b["rating"], reverse=True)
    elif sort_by == "review_count":
        results.sort(key=lambda b: b["review_count"], reverse=True)
    # best_match / distance fall back to seed order

    total = len(results)
    page = results[offset: offset + limit]
    return {"total": total, "businesses": page, "region": {"center": {"latitude": 37.7749, "longitude": -122.4194}}}


def get_business(business_id):
    for b in _businesses_store:
        if b["id"] == business_id or b["alias"] == business_id:
            return b
    return {"error": f"Business {business_id} not found"}


def get_business_reviews(business_id):
    if not any(b["id"] == business_id or b["alias"] == business_id for b in _businesses_store):
        return {"error": f"Business {business_id} not found"}
    reviews = [r for r in _reviews_store if r["business_id"] == business_id]
    return {"total": len(reviews), "reviews": reviews,
            "possible_languages": ["en"]}


# ---------------------------------------------------------------------------
# Categories
# ---------------------------------------------------------------------------

def list_categories():
    return {"categories": _categories_store}
