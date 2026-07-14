"""Data access module for the DoorDash API mock service."""

import csv
import uuid
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).parent

import sys as _sys
_sys.path.insert(0, str(DATA_DIR.parent))
from _mutable_store import (
    read_seed_with_ctx, get_store,
    strict_int,
    strict_float,
    strict_bool,
)

_store = get_store("doordash-api")
_API = "doordash-api"

_API = "doordash-api"


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

_store.register("stores", primary_key="store_id",
                initial_loader=lambda: _coerce_stores(_load("stores.json", "stores")))
_store.register("menu_items", primary_key="item_id",
                initial_loader=lambda: _coerce_menu(_load("menu_items.json", "menu_items")))
_store.register("orders", primary_key="order_id",
                initial_loader=lambda: _coerce_orders(_load("orders.json", "orders")))
# order_items natural key (order_id, item_id) -> synth composite pk
_store.register("order_items", primary_key="_pk",
                initial_loader=lambda: [
                    {**r, "_pk": f"{r['order_id']}@{r['item_id']}"}
                    for r in _coerce_order_items(_load("order_items.json", "order_items"))])


def _stores_rows():
    return _store.table("stores").rows()


def _menu_items_rows():
    return _store.table("menu_items").rows()


def _orders_rows():
    return _store.table("orders").rows()


def _order_items_rows():
    return [{k: v for k, v in r.items() if k != "_pk"} for r in _store.table("order_items").rows()]


SERVICE_FEE_PCT = 10.0  # percent of subtotal


def _load(filename, table):
    return read_seed_with_ctx(DATA_DIR / filename, _API, table)


def _strip_ctx(r):
    return {k: v for k, v in r.items() if not k.startswith("__")}


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
            **_strip_ctx(r),
            "rating": strict_float(r, "rating"),
            "review_count": strict_int(r, "review_count"),
            "delivery_fee": strict_float(r, "delivery_fee"),
            "eta_minutes": strict_int(r, "eta_minutes"),
            "latitude": strict_float(r, "latitude"),
            "longitude": strict_float(r, "longitude"),
            "is_open": strict_bool(r, "is_open"),
        })
    return out


def _coerce_menu(rows):
    out = []
    for r in rows:
        out.append({
            **_strip_ctx(r),
            "price": strict_float(r, "price"),
            "calories": strict_int(r, "calories"),
            "popular": strict_bool(r, "popular"),
            "available": strict_bool(r, "available"),
        })
    return out


def _coerce_orders(rows):
    out = []
    for r in rows:
        out.append({
            **_strip_ctx(r),
            "subtotal": strict_float(r, "subtotal"),
            "delivery_fee": strict_float(r, "delivery_fee"),
            "service_fee": strict_float(r, "service_fee"),
            "tip": strict_float(r, "tip"),
            "total": strict_float(r, "total"),
        })
    return out


def _coerce_order_items(rows):
    out = []
    for r in rows:
        out.append({
            **_strip_ctx(r),
            "quantity": strict_int(r, "quantity"),
            "unit_price": strict_float(r, "unit_price"),
            "line_total": strict_float(r, "line_total"),
        })
    return out










_carts = {}  # cart_id -> {store_id, items: [{item_id, quantity}]}


def _new_id(prefix):
    return f"{prefix}-{uuid.uuid4().hex[:8]}"


# ---------------------------------------------------------------------------
# Stores
# ---------------------------------------------------------------------------

def list_stores(latitude=None, longitude=None, cuisine=None, open_only=False):
    results = list(_stores_rows())
    if cuisine:
        results = [s for s in results if s["cuisine"].lower() == cuisine.lower()]
    if open_only:
        results = [s for s in results if s["is_open"]]
    results.sort(key=lambda s: s["rating"], reverse=True)
    return {"count": len(results), "stores": results}


def get_store(store_id):
    for s in _stores_rows():
        if s["store_id"] == store_id:
            return s
    return {"error": f"Store {store_id} not found"}


def get_menu(store_id):
    if not any(s["store_id"] == store_id for s in _stores_rows()):
        return {"error": f"Store {store_id} not found"}
    items = [i for i in _menu_items_rows() if i["store_id"] == store_id]
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
    return next((i for i in _menu_items_rows() if i["item_id"] == item_id), None)


# ---------------------------------------------------------------------------
# Cart
# ---------------------------------------------------------------------------

def create_cart(store_id):
    store = next((s for s in _stores_rows() if s["store_id"] == store_id), None)
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
    store = next(s for s in _stores_rows() if s["store_id"] == cart["store_id"])
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
    _store_insert("orders", order)
    for it in cart_full["items"]:
        _store_insert("order_items", {
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
    for o in _orders_rows():
        if o["order_id"] == order_id:
            items = [i for i in _order_items_rows() if i["order_id"] == order_id]
            return {**o, "items": items}
    return {"error": f"Order {order_id} not found"}

_store.eager_load()
