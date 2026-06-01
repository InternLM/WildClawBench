"""Data access module for the Instacart API mock service."""

import csv
import json
import uuid
from copy import deepcopy
from datetime import datetime, timedelta
from pathlib import Path

DATA_DIR = Path(__file__).parent


def _load(filename):
    with open(DATA_DIR / filename, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _now_iso():
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


def _to_bool(v):
    return str(v).strip().lower() == "true"


def _coerce_retailers(rows):
    out = []
    for r in rows:
        out.append({
            **r,
            "min_basket": float(r["min_basket"]),
            "delivery_fee": float(r["delivery_fee"]),
            "service_fee_pct": float(r["service_fee_pct"]),
            "eta_minutes": int(r["eta_minutes"]),
            "delivers_to_zips": [z.strip() for z in r["delivers_to_zips"].split(",")],
        })
    return out


def _coerce_products(rows):
    out = []
    for r in rows:
        out.append({
            **r,
            "price": float(r["price"]),
            "sale_price": float(r["sale_price"]) if r["sale_price"] else None,
            "in_stock": _to_bool(r["in_stock"]),
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
            "replacement_for": r["replacement_for"] or None,
        })
    return out


_retailers = _coerce_retailers(_load("retailers.csv"))
_products = _coerce_products(_load("products.csv"))
_orders = _coerce_orders(_load("orders.csv"))
_order_items = _coerce_order_items(_load("order_items.csv"))

with open(DATA_DIR / "user.json", encoding="utf-8") as _f:
    _user = json.load(_f)

_retailers_store = deepcopy(_retailers)
_products_store = deepcopy(_products)
_orders_store = deepcopy(_orders)
_order_items_store = deepcopy(_order_items)
_user_store = deepcopy(_user)
_carts = {}  # cart_id -> {retailer_id, user_id, items: [{product_id, quantity}]}


def _new_id(prefix):
    return f"{prefix}-{uuid.uuid4().hex[:8]}"


# ---------------------------------------------------------------------------
# User
# ---------------------------------------------------------------------------

def get_user():
    return _user_store


# ---------------------------------------------------------------------------
# Retailers
# ---------------------------------------------------------------------------

def list_retailers(zip_code=None):
    if not zip_code:
        return _retailers_store
    return [r for r in _retailers_store if zip_code in r["delivers_to_zips"]]


def get_retailer(retailer_id):
    for r in _retailers_store:
        if r["retailer_id"] == retailer_id:
            return r
    return {"error": f"Retailer {retailer_id} not found"}


# ---------------------------------------------------------------------------
# Products
# ---------------------------------------------------------------------------

def search_products(retailer_id=None, query=None, category=None, in_stock_only=True,
                    limit=25, offset=0):
    results = list(_products_store)
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
    for p in _products_store:
        if p["product_id"] == product_id:
            return p
    return {"error": f"Product {product_id} not found"}


# ---------------------------------------------------------------------------
# Cart
# ---------------------------------------------------------------------------

def _get_cart(cart_id):
    return _carts.get(cart_id)


def create_cart(user_id, retailer_id):
    if not any(r["retailer_id"] == retailer_id for r in _retailers_store):
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
    retailer = next(r for r in _retailers_store if r["retailer_id"] == cart["retailer_id"])
    subtotal = 0.0
    detailed_items = []
    for it in cart["items"]:
        product = next((p for p in _products_store if p["product_id"] == it["product_id"]), None)
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
    product = next((p for p in _products_store if p["product_id"] == product_id), None)
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
    _orders_store.append(order)
    for it in cart_full["items"]:
        _order_items_store.append({
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
    results = list(_orders_store)
    if user_id:
        results = [o for o in results if o["user_id"] == user_id]
    if status:
        results = [o for o in results if o["status"].upper() == status.upper()]
    results.sort(key=lambda o: o["placed_at"], reverse=True)
    return {"count": len(results), "results": results}


def get_order(order_id):
    for o in _orders_store:
        if o["order_id"] == order_id:
            items = [i for i in _order_items_store if i["order_id"] == order_id]
            return {**o, "items": items}
    return {"error": f"Order {order_id} not found"}


def cancel_order(order_id):
    for i, o in enumerate(_orders_store):
        if o["order_id"] == order_id:
            if o["status"] in {"DELIVERED", "CANCELLED"}:
                return {"error": f"Order {order_id} cannot be cancelled (status: {o['status']})"}
            _orders_store[i]["status"] = "CANCELLED"
            return _orders_store[i]
    return {"error": f"Order {order_id} not found"}
