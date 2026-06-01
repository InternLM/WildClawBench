"""Data access module for the DoorDash API mock service."""

import csv
import uuid
from copy import deepcopy
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).parent

SERVICE_FEE_PCT = 10.0  # percent of subtotal


def _load(filename):
    with open(DATA_DIR / filename, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _now_iso():
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


def _to_bool(v):
    return str(v).strip().lower() == "true"


# ---------------------------------------------------------------------------
# Load + coerce
# ---------------------------------------------------------------------------

def _coerce_stores(rows):
    out = []
    for r in rows:
        out.append({
            **r,
            "rating": float(r["rating"]),
            "review_count": int(r["review_count"]),
            "delivery_fee": float(r["delivery_fee"]),
            "eta_minutes": int(r["eta_minutes"]),
            "latitude": float(r["latitude"]),
            "longitude": float(r["longitude"]),
            "is_open": _to_bool(r["is_open"]),
        })
    return out


def _coerce_menu(rows):
    out = []
    for r in rows:
        out.append({
            **r,
            "price": float(r["price"]),
            "calories": int(r["calories"]),
            "popular": _to_bool(r["popular"]),
            "available": _to_bool(r["available"]),
        })
    return out


def _coerce_orders(rows):
    out = []
    for r in rows:
        out.append({
            **r,
            "subtotal": float(r["subtotal"]),
            "delivery_fee": float(r["delivery_fee"]),
            "service_fee": float(r["service_fee"]),
            "tip": float(r["tip"]),
            "total": float(r["total"]),
        })
    return out


def _coerce_order_items(rows):
    out = []
    for r in rows:
        out.append({
            **r,
            "quantity": int(r["quantity"]),
            "unit_price": float(r["unit_price"]),
            "line_total": float(r["line_total"]),
        })
    return out


_stores = _coerce_stores(_load("stores.csv"))
_menu_items = _coerce_menu(_load("menu_items.csv"))
_orders = _coerce_orders(_load("orders.csv"))
_order_items = _coerce_order_items(_load("order_items.csv"))

_stores_store = deepcopy(_stores)
_menu_store = deepcopy(_menu_items)
_orders_store = deepcopy(_orders)
_order_items_store = deepcopy(_order_items)
_carts = {}  # cart_id -> {store_id, items: [{item_id, quantity}]}


def _new_id(prefix):
    return f"{prefix}-{uuid.uuid4().hex[:8]}"


# ---------------------------------------------------------------------------
# Stores
# ---------------------------------------------------------------------------

def list_stores(latitude=None, longitude=None, cuisine=None, open_only=False):
    results = list(_stores_store)
    if cuisine:
        results = [s for s in results if s["cuisine"].lower() == cuisine.lower()]
    if open_only:
        results = [s for s in results if s["is_open"]]
    results.sort(key=lambda s: s["rating"], reverse=True)
    return {"count": len(results), "stores": results}


def get_store(store_id):
    for s in _stores_store:
        if s["store_id"] == store_id:
            return s
    return {"error": f"Store {store_id} not found"}


def get_menu(store_id):
    if not any(s["store_id"] == store_id for s in _stores_store):
        return {"error": f"Store {store_id} not found"}
    items = [i for i in _menu_store if i["store_id"] == store_id]
    categories = {}
    for it in items:
        categories.setdefault(it["category"], []).append(it)
    return {
        "store_id": store_id,
        "categories": [
            {"name": name, "items": cat_items}
            for name, cat_items in categories.items()
        ],
        "items": items,
    }


def _get_item(item_id):
    return next((i for i in _menu_store if i["item_id"] == item_id), None)


# ---------------------------------------------------------------------------
# Cart
# ---------------------------------------------------------------------------

def create_cart(store_id):
    store = next((s for s in _stores_store if s["store_id"] == store_id), None)
    if not store:
        return {"error": f"Store {store_id} not found"}
    cart_id = _new_id("cart")
    _carts[cart_id] = {
        "cart_id": cart_id,
        "store_id": store_id,
        "items": [],
        "created_at": _now_iso(),
    }
    return _cart_with_totals(cart_id)


def _cart_with_totals(cart_id):
    cart = _carts.get(cart_id)
    if not cart:
        return {"error": f"Cart {cart_id} not found"}
    store = next(s for s in _stores_store if s["store_id"] == cart["store_id"])
    subtotal = 0.0
    detailed = []
    for it in cart["items"]:
        item = _get_item(it["item_id"])
        if not item:
            continue
        line_total = round(item["price"] * it["quantity"], 2)
        subtotal += line_total
        detailed.append({
            "item_id": item["item_id"],
            "name": item["name"],
            "quantity": it["quantity"],
            "unit_price": item["price"],
            "line_total": line_total,
        })
    service_fee = round(subtotal * SERVICE_FEE_PCT / 100, 2)
    delivery_fee = store["delivery_fee"]
    return {
        **cart,
        "items": detailed,
        "subtotal": round(subtotal, 2),
        "delivery_fee": delivery_fee,
        "service_fee": service_fee,
        "estimated_total": round(subtotal + delivery_fee + service_fee, 2),
    }


def get_cart(cart_id):
    return _cart_with_totals(cart_id)


def add_cart_item(cart_id, item_id, quantity):
    cart = _carts.get(cart_id)
    if not cart:
        return {"error": f"Cart {cart_id} not found"}
    item = _get_item(item_id)
    if not item:
        return {"error": f"Menu item {item_id} not found"}
    if item["store_id"] != cart["store_id"]:
        return {"error": "Item belongs to a different store than the cart"}
    if not item["available"]:
        return {"error": f"Menu item {item_id} is currently unavailable"}
    for it in cart["items"]:
        if it["item_id"] == item_id:
            it["quantity"] += quantity
            return _cart_with_totals(cart_id)
    cart["items"].append({"item_id": item_id, "quantity": quantity})
    return _cart_with_totals(cart_id)


def checkout(cart_id, customer_name="Guest", tip=0.0):
    cart_full = _cart_with_totals(cart_id)
    if "error" in cart_full:
        return cart_full
    if not cart_full["items"]:
        return {"error": "Cart is empty"}
    order_id = _new_id("order")
    order = {
        "order_id": order_id,
        "store_id": cart_full["store_id"],
        "customer_name": customer_name,
        "status": "confirmed",
        "subtotal": cart_full["subtotal"],
        "delivery_fee": cart_full["delivery_fee"],
        "service_fee": cart_full["service_fee"],
        "tip": float(tip),
        "total": round(cart_full["estimated_total"] + float(tip), 2),
        "placed_at": _now_iso(),
        "dasher_name": "",
    }
    _orders_store.append(order)
    for it in cart_full["items"]:
        _order_items_store.append({
            "order_id": order_id,
            "item_id": it["item_id"],
            "quantity": it["quantity"],
            "unit_price": it["unit_price"],
            "line_total": it["line_total"],
        })
    _carts.pop(cart_id, None)
    return get_order(order_id)


# ---------------------------------------------------------------------------
# Orders
# ---------------------------------------------------------------------------

def get_order(order_id):
    for o in _orders_store:
        if o["order_id"] == order_id:
            items = [i for i in _order_items_store if i["order_id"] == order_id]
            return {**o, "items": items}
    return {"error": f"Order {order_id} not found"}
