"""Data access module for Etsy Open API v3 seller simulation."""

import csv
import json
from copy import deepcopy
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).parent


def _load(filename):
    with open(DATA_DIR / filename, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _now():
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")


# ---------------------------------------------------------------------------
# Load and coerce data
# ---------------------------------------------------------------------------

def _coerce_listings(rows):
    out = []
    for r in rows:
        out.append({
            **r,
            "listing_id": int(r["listing_id"]),
            "shop_id": int(r["shop_id"]),
            "price": float(r["price"]),
            "quantity": int(r["quantity"]),
            "taxonomy_id": int(r["taxonomy_id"]),
            "tags": [t.strip() for t in r["tags"].split(",")] if r["tags"] else [],
            "materials": [m.strip() for m in r["materials"].split(",")] if r["materials"] else [],
            "shop_section_id": int(r["shop_section_id"]) if r["shop_section_id"] else None,
            "processing_min": int(r["processing_min"]) if r["processing_min"] else None,
            "processing_max": int(r["processing_max"]) if r["processing_max"] else None,
            "item_weight": float(r["item_weight"]) if r["item_weight"] else None,
            "item_length": float(r["item_length"]) if r["item_length"] else None,
            "item_width": float(r["item_width"]) if r["item_width"] else None,
            "item_height": float(r["item_height"]) if r["item_height"] else None,
            "views": int(r["views"]),
            "num_favorers": int(r["num_favorers"]),
            "shipping_profile_id": int(r["shipping_profile_id"]) if r["shipping_profile_id"] else None,
            "return_policy_id": int(r["return_policy_id"]) if r["return_policy_id"] else None,
            "is_supply": r["is_supply"].lower() == "true",
            "is_customizable": r["is_customizable"].lower() == "true",
            "is_personalizable": r["is_personalizable"].lower() == "true",
        })
    return out


def _coerce_listing_images(rows):
    out = []
    for r in rows:
        out.append({
            **r,
            "listing_image_id": int(r["listing_image_id"]),
            "listing_id": int(r["listing_id"]),
            "shop_id": int(r["shop_id"]),
            "rank": int(r["rank"]),
        })
    return out


def _coerce_receipts(rows):
    out = []
    for r in rows:
        out.append({
            **r,
            "receipt_id": int(r["receipt_id"]),
            "shop_id": int(r["shop_id"]),
            "buyer_user_id": int(r["buyer_user_id"]),
            "grandtotal": float(r["grandtotal"]),
            "subtotal": float(r["subtotal"]),
            "total_shipping_cost": float(r["total_shipping_cost"]),
            "total_tax_cost": float(r["total_tax_cost"]),
            "discount_amt": float(r["discount_amt"]),
            "is_gift": r["is_gift"].lower() == "true",
            "gift_message": r["gift_message"] if r["gift_message"] else None,
            "shipped_timestamp": r["shipped_timestamp"] if r["shipped_timestamp"] else None,
            "estimated_delivery": r["estimated_delivery"] if r["estimated_delivery"] else None,
            "shipping_carrier": r["shipping_carrier"] if r["shipping_carrier"] else None,
            "tracking_code": r["tracking_code"] if r["tracking_code"] else None,
        })
    return out


def _coerce_transactions(rows):
    out = []
    for r in rows:
        out.append({
            **r,
            "transaction_id": int(r["transaction_id"]),
            "receipt_id": int(r["receipt_id"]),
            "listing_id": int(r["listing_id"]),
            "shop_id": int(r["shop_id"]),
            "buyer_user_id": int(r["buyer_user_id"]),
            "quantity": int(r["quantity"]),
            "price": float(r["price"]),
            "shipping_cost": float(r["shipping_cost"]),
            "is_digital": r["is_digital"].lower() == "true",
        })
    return out


def _coerce_reviews(rows):
    out = []
    for r in rows:
        out.append({
            **r,
            "review_id": int(r["review_id"]),
            "shop_id": int(r["shop_id"]),
            "listing_id": int(r["listing_id"]),
            "buyer_user_id": int(r["buyer_user_id"]),
            "rating": int(r["rating"]),
            "image_url": r["image_url"] if r["image_url"] else None,
        })
    return out


def _coerce_shop_sections(rows):
    out = []
    for r in rows:
        out.append({
            **r,
            "shop_section_id": int(r["shop_section_id"]),
            "shop_id": int(r["shop_id"]),
            "rank": int(r["rank"]),
            "active_listing_count": int(r["active_listing_count"]),
        })
    return out


def _coerce_shipping_profiles(rows):
    out = []
    for r in rows:
        out.append({
            **r,
            "shipping_profile_id": int(r["shipping_profile_id"]),
            "shop_id": int(r["shop_id"]),
            "processing_min": int(r["processing_min"]),
            "processing_max": int(r["processing_max"]),
            "min_delivery_days": int(r["min_delivery_days"]),
            "max_delivery_days": int(r["max_delivery_days"]),
            "cost": float(r["cost"]),
            "secondary_cost": float(r["secondary_cost"]),
        })
    return out


def _coerce_return_policies(rows):
    out = []
    for r in rows:
        out.append({
            **r,
            "return_policy_id": int(r["return_policy_id"]),
            "shop_id": int(r["shop_id"]),
            "accepts_returns": r["accepts_returns"].lower() == "true",
            "accepts_exchanges": r["accepts_exchanges"].lower() == "true",
            "return_deadline": int(r["return_deadline"]),
        })
    return out


# Load all data at module init
_listings = _coerce_listings(_load("listings.csv"))
_listing_images = _coerce_listing_images(_load("listing_images.csv"))
_receipts = _coerce_receipts(_load("receipts.csv"))
_transactions = _coerce_transactions(_load("transactions.csv"))
_reviews = _coerce_reviews(_load("reviews.csv"))
_shop_sections = _coerce_shop_sections(_load("shop_sections.csv"))
_shipping_profiles = _coerce_shipping_profiles(_load("shipping_profiles.csv"))
_return_policies = _coerce_return_policies(_load("return_policies.csv"))

with open(DATA_DIR / "shop.json", encoding="utf-8") as _f:
    _shop = json.load(_f)

# Mutable in-memory stores
_listings_store = deepcopy(_listings)
_listing_images_store = deepcopy(_listing_images)
_receipts_store = deepcopy(_receipts)
_transactions_store = deepcopy(_transactions)
_reviews_store = deepcopy(_reviews)
_shop_sections_store = deepcopy(_shop_sections)
_shipping_profiles_store = deepcopy(_shipping_profiles)
_return_policies_store = deepcopy(_return_policies)
_shop_store = deepcopy(_shop)

_next_listing_id = max(l["listing_id"] for l in _listings_store) + 1
_next_receipt_id = max(r["receipt_id"] for r in _receipts_store) + 1
_next_image_id = max(i["listing_image_id"] for i in _listing_images_store) + 1
_next_review_id = max(r["review_id"] for r in _reviews_store) + 1


# ---------------------------------------------------------------------------
# User
# ---------------------------------------------------------------------------

def get_current_user():
    return {
        "user_id": _shop_store["user_id"],
        "login_name": _shop_store["login_name"],
        "primary_email": None,
        "create_timestamp": _shop_store["create_date"],
        "shop_id": _shop_store["shop_id"],
    }


# ---------------------------------------------------------------------------
# Shop
# ---------------------------------------------------------------------------

def get_shop(shop_id: int):
    if shop_id != _shop_store["shop_id"]:
        return {"error": f"Shop {shop_id} not found"}
    return {"type": "shop", "shop": _shop_store}


def update_shop(shop_id: int, data: dict):
    if shop_id != _shop_store["shop_id"]:
        return {"error": f"Shop {shop_id} not found"}
    updatable = {"title", "announcement", "sale_message", "is_vacation",
                 "vacation_message", "accepts_custom_requests",
                 "policy_welcome", "policy_payment", "policy_shipping", "policy_refunds"}
    for k, v in data.items():
        if k in updatable:
            _shop_store[k] = v
    _shop_store["update_date"] = _now()
    return {"type": "shop", "shop": _shop_store}


# ---------------------------------------------------------------------------
# Shop Sections
# ---------------------------------------------------------------------------

def list_shop_sections(shop_id: int):
    sections = [s for s in _shop_sections_store if s["shop_id"] == shop_id]
    if not sections and shop_id != _shop_store["shop_id"]:
        return {"error": f"Shop {shop_id} not found"}
    return {"type": "shop_sections", "count": len(sections), "results": sections}


def get_shop_section(shop_id: int, section_id: int):
    for s in _shop_sections_store:
        if s["shop_id"] == shop_id and s["shop_section_id"] == section_id:
            return {"type": "shop_section", "shop_section": s}
    return {"error": f"Shop section {section_id} not found"}


# ---------------------------------------------------------------------------
# Listings
# ---------------------------------------------------------------------------

def list_listings(
    shop_id: int,
    state: str = "active",
    sort_on: str = "created",
    sort_order: str = "desc",
    limit: int = 25,
    offset: int = 0,
    section_id: int = None,
    q: str = None,
):
    results = [l for l in _listings_store if l["shop_id"] == shop_id]

    if state:
        results = [l for l in results if l["state"].lower() == state.lower()]
    if section_id:
        results = [l for l in results if l["shop_section_id"] == section_id]
    if q:
        q_l = q.lower()
        results = [l for l in results if q_l in l["title"].lower() or q_l in l["description"].lower()]

    sort_key_map = {
        "created": "created_timestamp",
        "price": "price",
        "updated": "updated_timestamp",
        "score": "views",
    }
    key = sort_key_map.get(sort_on, "created_timestamp")
    reverse = sort_order.lower() == "desc"
    results = sorted(results, key=lambda x: x[key], reverse=reverse)

    total = len(results)
    page_results = results[offset: offset + limit]
    return {
        "type": "listings",
        "count": len(page_results),
        "total": total,
        "offset": offset,
        "limit": limit,
        "results": page_results,
    }


def get_listing(listing_id: int):
    for l in _listings_store:
        if l["listing_id"] == listing_id:
            return {"type": "listing", "listing": l}
    return {"error": f"Listing {listing_id} not found"}


def create_listing(shop_id: int, data: dict):
    global _next_listing_id
    required = ["title", "description", "price", "quantity", "who_made", "when_made", "taxonomy_id"]
    for f in required:
        if f not in data or data[f] is None:
            return {"error": f"Missing required field: {f}"}

    now = _now()
    listing = {
        "listing_id": _next_listing_id,
        "shop_id": shop_id,
        "title": data["title"],
        "description": data["description"],
        "price": float(data["price"]),
        "currency_code": "USD",
        "quantity": int(data["quantity"]),
        "taxonomy_id": int(data["taxonomy_id"]),
        "tags": data.get("tags", []),
        "materials": data.get("materials", []),
        "who_made": data["who_made"],
        "when_made": data["when_made"],
        "state": "draft",
        "shop_section_id": data.get("shop_section_id"),
        "processing_min": data.get("processing_min"),
        "processing_max": data.get("processing_max"),
        "item_weight": data.get("item_weight"),
        "item_weight_unit": data.get("item_weight_unit", "oz"),
        "item_length": data.get("item_length"),
        "item_width": data.get("item_width"),
        "item_height": data.get("item_height"),
        "item_dimensions_unit": data.get("item_dimensions_unit", "in"),
        "views": 0,
        "num_favorers": 0,
        "shipping_profile_id": data.get("shipping_profile_id"),
        "return_policy_id": data.get("return_policy_id"),
        "is_supply": data.get("is_supply", False),
        "is_customizable": data.get("is_customizable", False),
        "is_personalizable": data.get("is_personalizable", False),
        "created_timestamp": now,
        "updated_timestamp": now,
        "ending_timestamp": None,
    }
    _listings_store.append(listing)
    _next_listing_id += 1
    return {"type": "listing", "listing": listing}


def update_listing(listing_id: int, data: dict):
    for i, listing in enumerate(_listings_store):
        if listing["listing_id"] == listing_id:
            updatable = {
                "title", "description", "price", "quantity", "tags", "materials",
                "state", "who_made", "when_made", "taxonomy_id", "shop_section_id",
                "processing_min", "processing_max", "item_weight", "item_weight_unit",
                "item_length", "item_width", "item_height", "item_dimensions_unit",
                "shipping_profile_id", "return_policy_id", "is_supply",
                "is_customizable", "is_personalizable",
            }
            for k, v in data.items():
                if k in updatable:
                    if k == "price" and v is not None:
                        _listings_store[i][k] = float(v)
                    elif k == "quantity" and v is not None:
                        _listings_store[i][k] = int(v)
                    elif k == "taxonomy_id" and v is not None:
                        _listings_store[i][k] = int(v)
                    else:
                        _listings_store[i][k] = v
            _listings_store[i]["updated_timestamp"] = _now()
            return {"type": "listing", "listing": _listings_store[i]}
    return {"error": f"Listing {listing_id} not found"}


def delete_listing(listing_id: int):
    for i, listing in enumerate(_listings_store):
        if listing["listing_id"] == listing_id:
            removed = _listings_store.pop(i)
            return {"type": "listing", "deleted": True, "listing_id": listing_id}
    return {"error": f"Listing {listing_id} not found"}


# ---------------------------------------------------------------------------
# Listing Images
# ---------------------------------------------------------------------------

def list_listing_images(listing_id: int):
    images = [img for img in _listing_images_store if img["listing_id"] == listing_id]
    if not images:
        # Check if listing exists
        if not any(l["listing_id"] == listing_id for l in _listings_store):
            return {"error": f"Listing {listing_id} not found"}
    return {"type": "listing_images", "count": len(images), "results": images}


def get_listing_image(listing_id: int, image_id: int):
    for img in _listing_images_store:
        if img["listing_id"] == listing_id and img["listing_image_id"] == image_id:
            return {"type": "listing_image", "listing_image": img}
    return {"error": f"Image {image_id} not found for listing {listing_id}"}


def delete_listing_image(listing_id: int, image_id: int):
    for i, img in enumerate(_listing_images_store):
        if img["listing_id"] == listing_id and img["listing_image_id"] == image_id:
            _listing_images_store.pop(i)
            return {"type": "listing_image", "deleted": True, "listing_image_id": image_id}
    return {"error": f"Image {image_id} not found for listing {listing_id}"}


# ---------------------------------------------------------------------------
# Receipts (Orders)
# ---------------------------------------------------------------------------

def _attach_transactions(receipt: dict) -> dict:
    txns = [t for t in _transactions_store if t["receipt_id"] == receipt["receipt_id"]]
    return {**receipt, "transactions": txns}


def list_receipts(
    shop_id: int,
    status: str = None,
    min_created: str = None,
    max_created: str = None,
    sort_on: str = "created",
    sort_order: str = "desc",
    limit: int = 25,
    offset: int = 0,
    was_shipped: bool = None,
    was_paid: bool = None,
):
    results = [r for r in _receipts_store if r["shop_id"] == shop_id]

    if status:
        results = [r for r in results if r["status"].lower() == status.lower()]
    if min_created:
        results = [r for r in results if r["created_timestamp"] >= min_created]
    if max_created:
        results = [r for r in results if r["created_timestamp"] <= max_created]
    if was_shipped is True:
        results = [r for r in results if r["shipped_timestamp"]]
    elif was_shipped is False:
        results = [r for r in results if not r["shipped_timestamp"]]
    if was_paid is True:
        results = [r for r in results if r["status"] in ("paid", "completed", "shipped")]
    elif was_paid is False:
        results = [r for r in results if r["status"] == "open"]

    sort_key_map = {
        "created": "created_timestamp",
        "updated": "updated_timestamp",
    }
    key = sort_key_map.get(sort_on, "created_timestamp")
    reverse = sort_order.lower() == "desc"
    results = sorted(results, key=lambda x: x.get(key, ""), reverse=reverse)

    total = len(results)
    page_results = results[offset: offset + limit]
    return {
        "type": "receipts",
        "count": len(page_results),
        "total": total,
        "offset": offset,
        "limit": limit,
        "results": [_attach_transactions(r) for r in page_results],
    }


def get_receipt(receipt_id: int):
    for r in _receipts_store:
        if r["receipt_id"] == receipt_id:
            return {"type": "receipt", "receipt": _attach_transactions(r)}
    return {"error": f"Receipt {receipt_id} not found"}


def update_receipt(receipt_id: int, data: dict):
    for i, r in enumerate(_receipts_store):
        if r["receipt_id"] == receipt_id:
            updatable = {"shipping_carrier", "tracking_code", "status"}
            for k, v in data.items():
                if k in updatable:
                    _receipts_store[i][k] = v
            if data.get("was_shipped") or data.get("tracking_code"):
                if not _receipts_store[i]["shipped_timestamp"]:
                    _receipts_store[i]["shipped_timestamp"] = _now()
                if _receipts_store[i]["status"] == "paid":
                    _receipts_store[i]["status"] = "shipped"
            _receipts_store[i]["updated_timestamp"] = _now()
            return {"type": "receipt", "receipt": _attach_transactions(_receipts_store[i])}
    return {"error": f"Receipt {receipt_id} not found"}


# ---------------------------------------------------------------------------
# Transactions
# ---------------------------------------------------------------------------

def list_receipt_transactions(receipt_id: int):
    txns = [t for t in _transactions_store if t["receipt_id"] == receipt_id]
    if not txns:
        if not any(r["receipt_id"] == receipt_id for r in _receipts_store):
            return {"error": f"Receipt {receipt_id} not found"}
    return {"type": "transactions", "count": len(txns), "results": txns}


def get_transaction(transaction_id: int):
    for t in _transactions_store:
        if t["transaction_id"] == transaction_id:
            return {"type": "transaction", "transaction": t}
    return {"error": f"Transaction {transaction_id} not found"}


# ---------------------------------------------------------------------------
# Reviews
# ---------------------------------------------------------------------------

def list_reviews(
    shop_id: int = None,
    listing_id: int = None,
    min_rating: int = None,
    limit: int = 25,
    offset: int = 0,
):
    results = list(_reviews_store)
    if shop_id:
        results = [r for r in results if r["shop_id"] == shop_id]
    if listing_id:
        results = [r for r in results if r["listing_id"] == listing_id]
    if min_rating:
        results = [r for r in results if r["rating"] >= min_rating]

    results = sorted(results, key=lambda x: x["created_timestamp"], reverse=True)

    total = len(results)
    page_results = results[offset: offset + limit]
    return {
        "type": "reviews",
        "count": len(page_results),
        "total": total,
        "offset": offset,
        "limit": limit,
        "results": page_results,
    }


def get_review(review_id: int):
    for r in _reviews_store:
        if r["review_id"] == review_id:
            return {"type": "review", "review": r}
    return {"error": f"Review {review_id} not found"}


# ---------------------------------------------------------------------------
# Shipping Profiles
# ---------------------------------------------------------------------------

def list_shipping_profiles(shop_id: int):
    profiles = [p for p in _shipping_profiles_store if p["shop_id"] == shop_id]
    return {"type": "shipping_profiles", "count": len(profiles), "results": profiles}


def get_shipping_profile(shop_id: int, profile_id: int):
    for p in _shipping_profiles_store:
        if p["shop_id"] == shop_id and p["shipping_profile_id"] == profile_id:
            return {"type": "shipping_profile", "shipping_profile": p}
    return {"error": f"Shipping profile {profile_id} not found"}


# ---------------------------------------------------------------------------
# Return Policies
# ---------------------------------------------------------------------------

def list_return_policies(shop_id: int):
    policies = [p for p in _return_policies_store if p["shop_id"] == shop_id]
    return {"type": "return_policies", "count": len(policies), "results": policies}


def get_return_policy(shop_id: int, policy_id: int):
    for p in _return_policies_store:
        if p["shop_id"] == shop_id and p["return_policy_id"] == policy_id:
            return {"type": "return_policy", "return_policy": p}
    return {"error": f"Return policy {policy_id} not found"}
