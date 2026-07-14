"""Data access module for Etsy Open API v3 seller simulation."""

import csv
import json
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).parent

import sys as _sys
_sys.path.insert(0, str(DATA_DIR.parent))
from _mutable_store import (
    read_seed_with_ctx, get_store, opt_csv_list, opt_float, opt_int, opt_str, strict_float, strict_int)

_store = get_store("etsy-api")
_API = "etsy-api"



def _store_patch(_table, _row_or_pk, _updates):
    """Persist field updates to a stored row (was: in-place mutation of a copy)."""
    _t = _store.table(_table)
    _pk = _row_or_pk.get(_t.primary_key, _row_or_pk.get("id")) if isinstance(_row_or_pk, dict) else _row_or_pk
    return _t.patch(_pk, _updates)


def _store_delete(_table, _row_or_pk):
    """Persist a row deletion (was: pop/remove on a copy)."""
    _t = _store.table(_table)
    _pk = _row_or_pk.get(_t.primary_key, _row_or_pk.get("id")) if isinstance(_row_or_pk, dict) else _row_or_pk
    return _t.delete(_pk)

def _store_insert(_table, _row):
    """Persist a newly-created row into the shared store (drift/injection-safe).

    Synthesizes the table's registered primary key from the row's ``id`` field
    when the row doesn't already carry it, so creates work regardless of whether
    the table was registered with primary_key="id" or a domain-specific key.
    """
    _t = _store.table(_table)
    if _t.primary_key not in _row and "id" in _row:
        _row = {**_row, _t.primary_key: _row["id"]}
    return _t.upsert(_row)

_store.register("listings", primary_key="listing_id",
                initial_loader=lambda: _coerce_listings(_load("listings.json", "listings")))
_store.register("listing_images", primary_key="listing_image_id",
                initial_loader=lambda: _coerce_listing_images(_load("listing_images.json", "listing_images")))
_store.register("receipts", primary_key="receipt_id",
                initial_loader=lambda: _coerce_receipts(_load("receipts.json", "receipts")))
_store.register("transactions", primary_key="transaction_id",
                initial_loader=lambda: _coerce_transactions(_load("transactions.json", "transactions")))
_store.register("reviews", primary_key="review_id",
                initial_loader=lambda: _coerce_reviews(_load("reviews.json", "reviews")))
_store.register("shop_sections", primary_key="shop_section_id",
                initial_loader=lambda: _coerce_shop_sections(_load("shop_sections.json", "shop_sections")))
_store.register("shipping_profiles", primary_key="shipping_profile_id",
                initial_loader=lambda: _coerce_shipping_profiles(_load("shipping_profiles.json", "shipping_profiles")))
_store.register("return_policies", primary_key="return_policy_id",
                initial_loader=lambda: _coerce_return_policies(_load("return_policies.json", "return_policies")))
_store.register_document("shop", initial_loader=lambda: __import__('json').load(open(DATA_DIR / "shop.json", encoding="utf-8")))


def _listings_rows():
    return _store.table("listings").rows()


def _listing_images_rows():
    return _store.table("listing_images").rows()


def _receipts_rows():
    return _store.table("receipts").rows()


def _transactions_rows():
    return _store.table("transactions").rows()


def _reviews_rows():
    return _store.table("reviews").rows()


def _shop_sections_rows():
    return _store.table("shop_sections").rows()


def _shipping_profiles_rows():
    return _store.table("shipping_profiles").rows()


def _return_policies_rows():
    return _store.table("return_policies").rows()


def _shop_doc():
    return _store.document("shop").get()



def _load(filename, table):
    return read_seed_with_ctx(DATA_DIR / filename, _API, table)


def _strip_ctx(r):
    return {k: v for k, v in r.items() if not k.startswith("__")}


def _now():
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")


# ---------------------------------------------------------------------------
# Load and coerce data
# ---------------------------------------------------------------------------

def _coerce_listings(rows):
    out = []
    for r in rows:
        out.append({
            **_strip_ctx(r),
            "listing_id": strict_int(r, "listing_id"),
            "shop_id": strict_int(r, "shop_id"),
            "price": strict_float(r, "price"),
            "quantity": strict_int(r, "quantity"),
            "taxonomy_id": strict_int(r, "taxonomy_id"),
            "tags": [t.strip() for t in opt_csv_list(r, "tags", sep=",")],
            "materials": [m.strip() for m in opt_csv_list(r, "materials", sep=",")],
            "shop_section_id": opt_int(r, "shop_section_id", default=None),
            "processing_min": opt_int(r, "processing_min", default=None),
            "processing_max": opt_int(r, "processing_max", default=None),
            "item_weight": opt_float(r, "item_weight", default=None),
            "item_length": opt_float(r, "item_length", default=None),
            "item_width": opt_float(r, "item_width", default=None),
            "item_height": opt_float(r, "item_height", default=None),
            "views": strict_int(r, "views"),
            "num_favorers": strict_int(r, "num_favorers"),
            "shipping_profile_id": opt_int(r, "shipping_profile_id", default=None),
            "return_policy_id": opt_int(r, "return_policy_id", default=None),
            "is_supply": r["is_supply"].lower() == "true",
            "is_customizable": r["is_customizable"].lower() == "true",
            "is_personalizable": r["is_personalizable"].lower() == "true",
        })
    return out


def _coerce_listing_images(rows):
    out = []
    for r in rows:
        out.append({
            **_strip_ctx(r),
            "listing_image_id": strict_int(r, "listing_image_id"),
            "listing_id": strict_int(r, "listing_id"),
            "shop_id": strict_int(r, "shop_id"),
            "rank": strict_int(r, "rank"),
        })
    return out


def _coerce_receipts(rows):
    out = []
    for r in rows:
        out.append({
            **_strip_ctx(r),
            "receipt_id": strict_int(r, "receipt_id"),
            "shop_id": strict_int(r, "shop_id"),
            "buyer_user_id": strict_int(r, "buyer_user_id"),
            "grandtotal": strict_float(r, "grandtotal"),
            "subtotal": strict_float(r, "subtotal"),
            "total_shipping_cost": strict_float(r, "total_shipping_cost"),
            "total_tax_cost": strict_float(r, "total_tax_cost"),
            "discount_amt": strict_float(r, "discount_amt"),
            "is_gift": r["is_gift"].lower() == "true",
            "gift_message": opt_str(r, "gift_message", default="") or None,
            "shipped_timestamp": opt_str(r, "shipped_timestamp", default="") or None,
            "estimated_delivery": opt_str(r, "estimated_delivery", default="") or None,
            "shipping_carrier": opt_str(r, "shipping_carrier", default="") or None,
            "tracking_code": opt_str(r, "tracking_code", default="") or None,
        })
    return out


def _coerce_transactions(rows):
    out = []
    for r in rows:
        out.append({
            **_strip_ctx(r),
            "transaction_id": strict_int(r, "transaction_id"),
            "receipt_id": strict_int(r, "receipt_id"),
            "listing_id": strict_int(r, "listing_id"),
            "shop_id": strict_int(r, "shop_id"),
            "buyer_user_id": strict_int(r, "buyer_user_id"),
            "quantity": strict_int(r, "quantity"),
            "price": strict_float(r, "price"),
            "shipping_cost": strict_float(r, "shipping_cost"),
            "is_digital": r["is_digital"].lower() == "true",
        })
    return out


def _coerce_reviews(rows):
    out = []
    for r in rows:
        out.append({
            **_strip_ctx(r),
            "review_id": strict_int(r, "review_id"),
            "shop_id": strict_int(r, "shop_id"),
            "listing_id": strict_int(r, "listing_id"),
            "buyer_user_id": strict_int(r, "buyer_user_id"),
            "rating": strict_int(r, "rating"),
            "image_url": opt_str(r, "image_url", default="") or None,
        })
    return out


def _coerce_shop_sections(rows):
    out = []
    for r in rows:
        out.append({
            **_strip_ctx(r),
            "shop_section_id": strict_int(r, "shop_section_id"),
            "shop_id": strict_int(r, "shop_id"),
            "rank": strict_int(r, "rank"),
            "active_listing_count": strict_int(r, "active_listing_count"),
        })
    return out


def _coerce_shipping_profiles(rows):
    out = []
    for r in rows:
        out.append({
            **_strip_ctx(r),
            "shipping_profile_id": strict_int(r, "shipping_profile_id"),
            "shop_id": strict_int(r, "shop_id"),
            "processing_min": strict_int(r, "processing_min"),
            "processing_max": strict_int(r, "processing_max"),
            "min_delivery_days": strict_int(r, "min_delivery_days"),
            "max_delivery_days": strict_int(r, "max_delivery_days"),
            "cost": strict_float(r, "cost"),
            "secondary_cost": strict_float(r, "secondary_cost"),
        })
    return out


def _coerce_return_policies(rows):
    out = []
    for r in rows:
        out.append({
            **_strip_ctx(r),
            "return_policy_id": strict_int(r, "return_policy_id"),
            "shop_id": strict_int(r, "shop_id"),
            "accepts_returns": r["accepts_returns"].lower() == "true",
            "accepts_exchanges": r["accepts_exchanges"].lower() == "true",
            "return_deadline": strict_int(r, "return_deadline"),
        })
    return out


# Load all data at module init









# Mutable in-memory stores









_store.eager_load()
_next_listing_id = max(l["listing_id"] for l in _listings_rows()) + 1
_next_receipt_id = max(r["receipt_id"] for r in _receipts_rows()) + 1
_next_image_id = max(i["listing_image_id"] for i in _listing_images_rows()) + 1
_next_review_id = max(r["review_id"] for r in _reviews_rows()) + 1


# ---------------------------------------------------------------------------
# User
# ---------------------------------------------------------------------------

def get_current_user():
    return {
        "user_id": _shop_doc()["user_id"],
        "login_name": _shop_doc()["login_name"],
        "primary_email": None,
        "create_timestamp": _shop_doc()["create_date"],
        "shop_id": _shop_doc()["shop_id"],
    }


# ---------------------------------------------------------------------------
# Shop
# ---------------------------------------------------------------------------

def get_shop(shop_id: int):
    if shop_id != _shop_doc()["shop_id"]:
        return {"error": f"Shop {shop_id} not found"}
    return {"type": "shop", "shop": _shop_doc()}


def update_shop(shop_id: int, data: dict):
    if shop_id != _shop_doc()["shop_id"]:
        return {"error": f"Shop {shop_id} not found"}
    updatable = {"title", "announcement", "sale_message", "is_vacation",
                 "vacation_message", "accepts_custom_requests",
                 "policy_welcome", "policy_payment", "policy_shipping", "policy_refunds"}
    _changes = {}
    for k, v in data.items():
        if k in updatable:
            _changes[k] = v
    _changes["update_date"] = _now()
    shop = _store.document("shop").merge(_changes)
    return {"type": "shop", "shop": shop}


# ---------------------------------------------------------------------------
# Shop Sections
# ---------------------------------------------------------------------------

def list_shop_sections(shop_id: int):
    sections = [s for s in _shop_sections_rows() if s["shop_id"] == shop_id]
    if not sections and shop_id != _shop_doc()["shop_id"]:
        return {"error": f"Shop {shop_id} not found"}
    return {"type": "shop_sections", "count": len(sections), "results": sections}


def get_shop_section(shop_id: int, section_id: int):
    for s in _shop_sections_rows():
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
    results = [l for l in _listings_rows() if l["shop_id"] == shop_id]

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
    for l in _listings_rows():
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
    _store_insert("listings", listing)
    _next_listing_id += 1
    return {"type": "listing", "listing": listing}


def update_listing(listing_id: int, data: dict):
    for listing in _listings_rows():
        if listing["listing_id"] == listing_id:
            updatable = {
                "title", "description", "price", "quantity", "tags", "materials",
                "state", "who_made", "when_made", "taxonomy_id", "shop_section_id",
                "processing_min", "processing_max", "item_weight", "item_weight_unit",
                "item_length", "item_width", "item_height", "item_dimensions_unit",
                "shipping_profile_id", "return_policy_id", "is_supply",
                "is_customizable", "is_personalizable",
            }
            _changes = {}
            for k, v in data.items():
                if k in updatable:
                    if k == "price" and v is not None:
                        _changes[k] = float(v)
                    elif k == "quantity" and v is not None:
                        _changes[k] = int(v)
                    elif k == "taxonomy_id" and v is not None:
                        _changes[k] = int(v)
                    else:
                        _changes[k] = v
            _changes["updated_timestamp"] = _now()
            listing.update(_changes)
            _store_patch("listings", listing, _changes)
            return {"type": "listing", "listing": listing}
    return {"error": f"Listing {listing_id} not found"}


def delete_listing(listing_id: int):
    for listing in _listings_rows():
        if listing["listing_id"] == listing_id:
            removed = listing
            _store_delete("listings", listing)
            return {"type": "listing", "deleted": True, "listing_id": listing_id}
    return {"error": f"Listing {listing_id} not found"}


# ---------------------------------------------------------------------------
# Listing Images
# ---------------------------------------------------------------------------

def list_listing_images(listing_id: int):
    images = [img for img in _listing_images_rows() if img["listing_id"] == listing_id]
    if not images:
        # Check if listing exists
        if not any(l["listing_id"] == listing_id for l in _listings_rows()):
            return {"error": f"Listing {listing_id} not found"}
    return {"type": "listing_images", "count": len(images), "results": images}


def get_listing_image(listing_id: int, image_id: int):
    for img in _listing_images_rows():
        if img["listing_id"] == listing_id and img["listing_image_id"] == image_id:
            return {"type": "listing_image", "listing_image": img}
    return {"error": f"Image {image_id} not found for listing {listing_id}"}


def delete_listing_image(listing_id: int, image_id: int):
    for img in _listing_images_rows():
        if img["listing_id"] == listing_id and img["listing_image_id"] == image_id:
            _store_delete("listing_images", img)
            return {"type": "listing_image", "deleted": True, "listing_image_id": image_id}
    return {"error": f"Image {image_id} not found for listing {listing_id}"}


# ---------------------------------------------------------------------------
# Receipts (Orders)
# ---------------------------------------------------------------------------

def _attach_transactions(receipt: dict) -> dict:
    txns = [t for t in _transactions_rows() if t["receipt_id"] == receipt["receipt_id"]]
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
    results = [r for r in _receipts_rows() if r["shop_id"] == shop_id]

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
    for r in _receipts_rows():
        if r["receipt_id"] == receipt_id:
            return {"type": "receipt", "receipt": _attach_transactions(r)}
    return {"error": f"Receipt {receipt_id} not found"}


def update_receipt(receipt_id: int, data: dict):
    for r in _receipts_rows():
        if r["receipt_id"] == receipt_id:
            updatable = {"shipping_carrier", "tracking_code", "status"}
            _changes = {}
            for k, v in data.items():
                if k in updatable:
                    _changes[k] = v
            r.update(_changes)
            if data.get("was_shipped") or data.get("tracking_code"):
                if not r["shipped_timestamp"]:
                    _changes["shipped_timestamp"] = _now()
                    r["shipped_timestamp"] = _changes["shipped_timestamp"]
                if r["status"] == "paid":
                    _changes["status"] = "shipped"
                    r["status"] = "shipped"
            _changes["updated_timestamp"] = _now()
            r["updated_timestamp"] = _changes["updated_timestamp"]
            _store_patch("receipts", r, _changes)
            return {"type": "receipt", "receipt": _attach_transactions(r)}
    return {"error": f"Receipt {receipt_id} not found"}


# ---------------------------------------------------------------------------
# Transactions
# ---------------------------------------------------------------------------

def list_receipt_transactions(receipt_id: int):
    txns = [t for t in _transactions_rows() if t["receipt_id"] == receipt_id]
    if not txns:
        if not any(r["receipt_id"] == receipt_id for r in _receipts_rows()):
            return {"error": f"Receipt {receipt_id} not found"}
    return {"type": "transactions", "count": len(txns), "results": txns}


def get_transaction(transaction_id: int):
    for t in _transactions_rows():
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
    results = list(_reviews_rows())
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
    for r in _reviews_rows():
        if r["review_id"] == review_id:
            return {"type": "review", "review": r}
    return {"error": f"Review {review_id} not found"}


# ---------------------------------------------------------------------------
# Shipping Profiles
# ---------------------------------------------------------------------------

def list_shipping_profiles(shop_id: int):
    profiles = [p for p in _shipping_profiles_rows() if p["shop_id"] == shop_id]
    return {"type": "shipping_profiles", "count": len(profiles), "results": profiles}


def get_shipping_profile(shop_id: int, profile_id: int):
    for p in _shipping_profiles_rows():
        if p["shop_id"] == shop_id and p["shipping_profile_id"] == profile_id:
            return {"type": "shipping_profile", "shipping_profile": p}
    return {"error": f"Shipping profile {profile_id} not found"}


# ---------------------------------------------------------------------------
# Return Policies
# ---------------------------------------------------------------------------

def list_return_policies(shop_id: int):
    policies = [p for p in _return_policies_rows() if p["shop_id"] == shop_id]
    return {"type": "return_policies", "count": len(policies), "results": policies}


def get_return_policy(shop_id: int, policy_id: int):
    for p in _return_policies_rows():
        if p["shop_id"] == shop_id and p["return_policy_id"] == policy_id:
            return {"type": "return_policy", "return_policy": p}
    return {"error": f"Return policy {policy_id} not found"}
