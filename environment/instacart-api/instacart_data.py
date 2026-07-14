"""Data access module for the Instacart API mock service."""

import csv
import json
import uuid
from datetime import datetime, timedelta
from pathlib import Path

DATA_DIR = Path(__file__).parent

import sys as _sys
_sys.path.insert(0, str(DATA_DIR.parent))
from _mutable_store import (  # noqa: E402
    read_seed_with_ctx, get_store, opt_csv_list, opt_float, opt_str, strict_bool, strict_float, strict_int)

_store = get_store("instacart-api")
_API = "instacart-api"



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

_store.register("retailers", primary_key="retailer_id",
                initial_loader=lambda: _coerce_retailers(_load("retailers.json", "retailers")))
_store.register("products", primary_key="product_id",
                initial_loader=lambda: _coerce_products(_load("products.json", "products")))
_store.register("orders", primary_key="order_id",
                initial_loader=lambda: _coerce_orders(_load("orders.json", "orders")))
_store.register("order_items", primary_key="_pk",
                initial_loader=lambda: [{**r, "_pk": f"{r['order_id']}@{r['product_id']}@{i}"} for i, r in enumerate(_coerce_order_items(_load("order_items.json", "order_items")))])
_store.register_document("user", initial_loader=lambda: __import__('json').load(open(DATA_DIR / "user.json", encoding="utf-8")))


def _retailers_rows():
    return _store.table("retailers").rows()


def _products_rows():
    return _store.table("products").rows()


def _orders_rows():
    return _store.table("orders").rows()


def _order_items_rows():
    return [{k: v for k, v in r.items() if k != "_pk"} for r in _store.table("order_items").rows()]


def _user_doc():
    return _store.document("user").get()



def _load(filename, table):
    return read_seed_with_ctx(DATA_DIR / filename, _API, table)


def _strip_ctx(r):
    return {k: v for k, v in r.items() if not k.startswith("__")}


def _now_iso():
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


def _to_bool(v):
    return str(v).strip().lower() == "true"


def _coerce_retailers(rows):
    out = []
    for r in rows:
        out.append({
            **_strip_ctx(r),
            "min_basket": strict_float(r, "min_basket"),
            "delivery_fee": strict_float(r, "delivery_fee"),
            "service_fee_pct": strict_float(r, "service_fee_pct"),
            "eta_minutes": strict_int(r, "eta_minutes"),
            "delivers_to_zips": [z.strip() for z in opt_csv_list(r, "delivers_to_zips", sep=",")],
        })
    return out


def _coerce_products(rows):
    out = []
    for r in rows:
        out.append({
            **_strip_ctx(r),
            "price": strict_float(r, "price"),
            "sale_price": opt_float(r, "sale_price", default=None),
            "in_stock": strict_bool(r, "in_stock"),
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
            "replacement_for": opt_str(r, "replacement_for", default="") or None,
        })
    return out







_carts = {}  # cart_id -> {retailer_id, user_id, items: [{product_id, quantity}]}


def _new_id(prefix):
    return f"{prefix}-{uuid.uuid4().hex[:8]}"


# ---------------------------------------------------------------------------
# User
# ---------------------------------------------------------------------------

def get_user():
    return _user_doc()


# ---------------------------------------------------------------------------
# Retailers
# ---------------------------------------------------------------------------

def list_retailers(zip_code=None):
    if not zip_code:
        return _retailers_rows()
    return [r for r in _retailers_rows() if zip_code in r["delivers_to_zips"]]


def get_retailer(retailer_id):
    for r in _retailers_rows():
        if r["retailer_id"] == retailer_id:
            return r
    return {"error": f"Retailer {retailer_id} not found"}


# ---------------------------------------------------------------------------
# Products
# ---------------------------------------------------------------------------

def search_products(retailer_id=None, query=None, category=None, in_stock_only=True,
                    limit=25, offset=0):
    results = list(_products_rows())
    if retailer_id:
        results = [p for p in results if p["retailer_id"] == retailer_id]
    if query:
        q = query.lower()
        results = [p for p in results if q in p["name"].lower() or q in p["brand"].lower()]
    if category:
        results = [p for p in results if p["category"].lower() == category.lower()]
    if in_stock_only:
        results = [p for p in results if p["in_stock"]]
    total = len(results)
    page = results[offset: offset + limit]
    return {"total": total, "count": len(page), "offset": offset, "limit": limit, "results": page}


def get_product(product_id):
    for p in _products_rows():
        if p["product_id"] == product_id:
            return p
    return {"error": f"Product {product_id} not found"}


# ---------------------------------------------------------------------------
# Cart
# ---------------------------------------------------------------------------

def _get_cart(cart_id):
    return _carts.get(cart_id)


def create_cart(user_id, retailer_id):
    if not any(r["retailer_id"] == retailer_id for r in _retailers_rows()):
        return {"error": f"Retailer {retailer_id} not found"}
    cart_id = _new_id("cart")
    _carts[cart_id] = {
        "cart_id": cart_id,
        "user_id": user_id,
        "retailer_id": retailer_id,
        "items": [],
        "created_at": _now_iso(),
    }
    return _cart_with_totals(cart_id)


def _cart_with_totals(cart_id):
    cart = _get_cart(cart_id)
    if not cart:
        return {"error": f"Cart {cart_id} not found"}
    retailer = next(r for r in _retailers_rows() if r["retailer_id"] == cart["retailer_id"])
    subtotal = 0.0
    detailed_items = []
    for it in cart["items"]:
        product = next((p for p in _products_rows() if p["product_id"] == it["product_id"]), None)
        if not product:
            continue
        unit_price = product["sale_price"] or product["price"]
        line_total = round(unit_price * it["quantity"], 2)
        subtotal += line_total
        detailed_items.append({
            "product_id": product["product_id"],
            "name": product["name"],
            "quantity": it["quantity"],
            "unit_price": unit_price,
            "line_total": line_total,
        })
    service_fee = round(subtotal * retailer["service_fee_pct"] / 100, 2)
    delivery_fee = retailer["delivery_fee"]
    return {
        **cart,
        "items": detailed_items,
        "subtotal": round(subtotal, 2),
        "service_fee": service_fee,
        "delivery_fee": delivery_fee,
        "min_basket": retailer["min_basket"],
        "meets_minimum": subtotal >= retailer["min_basket"],
        "estimated_total": round(subtotal + service_fee + delivery_fee, 2),
    }


def get_cart(cart_id):
    return _cart_with_totals(cart_id)


def add_to_cart(cart_id, product_id, quantity):
    cart = _get_cart(cart_id)
    if not cart:
        return {"error": f"Cart {cart_id} not found"}
    product = next((p for p in _products_rows() if p["product_id"] == product_id), None)
    if not product:
        return {"error": f"Product {product_id} not found"}
    if product["retailer_id"] != cart["retailer_id"]:
        return {"error": "Product belongs to a different retailer than the cart"}
    for it in cart["items"]:
        if it["product_id"] == product_id:
            it["quantity"] += quantity
            return _cart_with_totals(cart_id)
    cart["items"].append({"product_id": product_id, "quantity": quantity})
    return _cart_with_totals(cart_id)


def update_cart_item(cart_id, product_id, quantity):
    cart = _get_cart(cart_id)
    if not cart:
        return {"error": f"Cart {cart_id} not found"}
    for it in cart["items"]:
        if it["product_id"] == product_id:
            if quantity <= 0:
                cart["items"].remove(it)
            else:
                it["quantity"] = quantity
            return _cart_with_totals(cart_id)
    return {"error": f"Product {product_id} not in cart"}


def checkout(cart_id, tip=0.0, delivery_window_start=None, delivery_window_end=None):
    cart_full = _cart_with_totals(cart_id)
    if "error" in cart_full:
        return cart_full
    if not cart_full["meets_minimum"]:
        return {"error": "Cart does not meet retailer minimum basket"}
    order_id = _new_id("order")
    now = _now_iso()
    if not delivery_window_start:
        start = datetime.utcnow() + timedelta(hours=2)
        delivery_window_start = start.strftime("%Y-%m-%dT%H:%M:%SZ")
        delivery_window_end = (start + timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
    order = {
        "order_id": order_id,
        "user_id": cart_full["user_id"],
        "retailer_id": cart_full["retailer_id"],
        "status": "PLACED",
        "subtotal": cart_full["subtotal"],
        "delivery_fee": cart_full["delivery_fee"],
        "service_fee": cart_full["service_fee"],
        "tip": float(tip),
        "total": round(cart_full["estimated_total"] + float(tip), 2),
        "placed_at": now,
        "delivery_window_start": delivery_window_start,
        "delivery_window_end": delivery_window_end,
        "shopper_id": "",
    }
    _store_insert("orders", order)
    for i, it in enumerate(cart_full["items"]):
        _store_insert("order_items", {
            "_pk": f"{order_id}@{it['product_id']}@{i}",
            "order_id": order_id,
            "product_id": it["product_id"],
            "quantity": it["quantity"],
            "unit_price": it["unit_price"],
            "line_total": it["line_total"],
            "replacement_for": None,
        })
    _carts.pop(cart_id, None)
    return order


# ---------------------------------------------------------------------------
# Orders
# ---------------------------------------------------------------------------

def list_orders(user_id=None, status=None):
    results = list(_orders_rows())
    if user_id:
        results = [o for o in results if o["user_id"] == user_id]
    if status:
        results = [o for o in results if o["status"].upper() == status.upper()]
    results.sort(key=lambda o: o["placed_at"], reverse=True)
    return {"count": len(results), "results": results}


def get_order(order_id):
    for o in _orders_rows():
        if o["order_id"] == order_id:
            items = [i for i in _order_items_rows() if i["order_id"] == order_id]
            return {**o, "items": items}
    return {"error": f"Order {order_id} not found"}


def cancel_order(order_id):
    for o in _orders_rows():
        if o["order_id"] == order_id:
            if o["status"] in {"DELIVERED", "CANCELLED"}:
                return {"error": f"Order {order_id} cannot be cancelled (status: {o['status']})"}
            _changes = {"status": "CANCELLED"}
            o.update(_changes)
            _store_patch("orders", o, _changes)
            return o
    return {"error": f"Order {order_id} not found"}

_store.eager_load()
