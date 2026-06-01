"""Data access module for the BigCommerce API mock service.

Mirrors a subset of the BigCommerce Catalog (v3), Orders (v2) and Customers
(v3) APIs. v3 list responses are wrapped in `{"data": [...], "meta": {...}}`;
v2 responses are bare arrays/objects.
"""

import csv
from copy import deepcopy
from pathlib import Path

DATA_DIR = Path(__file__).parent


def _load(filename):
    with open(DATA_DIR / filename, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _to_bool(v):
    return str(v).strip().lower() == "true"


def _to_int(v):
    try:
        return int(v)
    except (TypeError, ValueError):
        return 0


def _to_float(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return 0.0


# ---------------------------------------------------------------------------
# Load + coerce
# ---------------------------------------------------------------------------

def _coerce_products(rows):
    out = []
    for r in rows:
        out.append({
            "id": _to_int(r["id"]),
            "name": r["name"],
            "sku": r["sku"],
            "type": r["type"],
            "price": _to_float(r["price"]),
            "sale_price": _to_float(r["sale_price"]),
            "cost_price": _to_float(r["cost_price"]),
            "weight": _to_float(r["weight"]),
            "inventory_level": _to_int(r["inventory_level"]),
            "inventory_tracking": r["inventory_tracking"],
            "is_visible": _to_bool(r["is_visible"]),
            "brand_id": _to_int(r["brand_id"]),
            "categories": [int(c) for c in r["categories"].split(";") if c],
            "description": r["description"],
            "date_created": r["date_created"],
        })
    return out


def _coerce_customers(rows):
    out = []
    for r in rows:
        out.append({
            "id": _to_int(r["id"]),
            "first_name": r["first_name"],
            "last_name": r["last_name"],
            "email": r["email"],
            "company": r["company"],
            "phone": r["phone"],
            "customer_group_id": _to_int(r["customer_group_id"]),
            "date_created": r["date_created"],
        })
    return out


def _coerce_orders(rows):
    out = []
    for r in rows:
        out.append({
            "id": _to_int(r["id"]),
            "customer_id": _to_int(r["customer_id"]),
            "status_id": _to_int(r["status_id"]),
            "status": r["status"],
            "total_inc_tax": _to_float(r["total_inc_tax"]),
            "subtotal_inc_tax": _to_float(r["subtotal_inc_tax"]),
            "currency_code": r["currency_code"],
            "payment_method": r["payment_method"],
            "items_total": _to_int(r["items_total"]),
            "date_created": r["date_created"],
            "billing_first_name": r["billing_first_name"],
            "billing_last_name": r["billing_last_name"],
            "billing_email": r["billing_email"],
        })
    return out


_products = _coerce_products(_load("products.csv"))
_customers = _coerce_customers(_load("customers.csv"))
_orders = _coerce_orders(_load("orders.csv"))

_products_store = deepcopy(_products)
_customers_store = deepcopy(_customers)
_orders_store = deepcopy(_orders)


# ---------------------------------------------------------------------------
# Serializers
# ---------------------------------------------------------------------------

def _serialize_product(p):
    return {
        "id": p["id"],
        "name": p["name"],
        "sku": p["sku"],
        "type": p["type"],
        "price": p["price"],
        "sale_price": p["sale_price"],
        "cost_price": p["cost_price"],
        "weight": p["weight"],
        "inventory_level": p["inventory_level"],
        "inventory_tracking": p["inventory_tracking"],
        "is_visible": p["is_visible"],
        "brand_id": p["brand_id"],
        "categories": p["categories"],
        "description": p["description"],
        "date_created": p["date_created"],
    }


def _serialize_customer(c):
    return {
        "id": c["id"],
        "first_name": c["first_name"],
        "last_name": c["last_name"],
        "email": c["email"],
        "company": c["company"],
        "phone": c["phone"],
        "customer_group_id": c["customer_group_id"],
        "date_created": c["date_created"],
    }


def _serialize_order(o):
    return {
        "id": o["id"],
        "customer_id": o["customer_id"],
        "status_id": o["status_id"],
        "status": o["status"],
        "total_inc_tax": f"{o['total_inc_tax']:.2f}",
        "subtotal_inc_tax": f"{o['subtotal_inc_tax']:.2f}",
        "currency_code": o["currency_code"],
        "payment_method": o["payment_method"],
        "items_total": o["items_total"],
        "date_created": o["date_created"],
        "billing_address": {
            "first_name": o["billing_first_name"],
            "last_name": o["billing_last_name"],
            "email": o["billing_email"],
        },
    }


def _meta(total, count, page, limit):
    total_pages = (total + limit - 1) // limit if limit else 1
    return {
        "pagination": {
            "total": total,
            "count": count,
            "per_page": limit,
            "current_page": page,
            "total_pages": total_pages,
        }
    }


# ---------------------------------------------------------------------------
# Catalog / Products (v3)
# ---------------------------------------------------------------------------

def list_products(name=None, sku=None, is_visible=None, page=1, limit=50):
    items = _products_store
    if name:
        items = [p for p in items if name.lower() in p["name"].lower()]
    if sku:
        items = [p for p in items if p["sku"].lower() == sku.lower()]
    if is_visible is not None:
        items = [p for p in items if p["is_visible"] == is_visible]
    total = len(items)
    start = (page - 1) * limit
    page_items = items[start:start + limit]
    return {
        "data": [_serialize_product(p) for p in page_items],
        "meta": _meta(total, len(page_items), page, limit),
    }


def get_product(product_id):
    p = next((x for x in _products_store if x["id"] == int(product_id)), None)
    if not p:
        return {"error": "Not Found", "status": 404,
                "title": f"Product {product_id} not found"}
    return {"data": _serialize_product(p), "meta": {}}


# ---------------------------------------------------------------------------
# Orders (v2)
# ---------------------------------------------------------------------------

def list_orders(customer_id=None, status_id=None, page=1, limit=50):
    items = _orders_store
    if customer_id is not None:
        items = [o for o in items if o["customer_id"] == int(customer_id)]
    if status_id is not None:
        items = [o for o in items if o["status_id"] == int(status_id)]
    start = (page - 1) * limit
    page_items = items[start:start + limit]
    return [_serialize_order(o) for o in page_items]


def get_order(order_id):
    o = next((x for x in _orders_store if x["id"] == int(order_id)), None)
    if not o:
        return {"error": "Not Found", "status": 404,
                "title": f"Order {order_id} not found"}
    return _serialize_order(o)


def create_order(customer_id=0, status_id=1, payment_method="manual",
                 currency_code="USD", billing_address=None, products=None):
    billing_address = billing_address or {}
    products = products or []
    next_id = max((o["id"] for o in _orders_store), default=2000) + 1
    subtotal = 0.0
    items_total = 0
    for line in products:
        prod = next((p for p in _products_store
                     if p["id"] == int(line.get("product_id", 0))), None)
        qty = int(line.get("quantity", 1))
        price = prod["price"] if prod else _to_float(line.get("price_inc_tax", 0))
        subtotal += price * qty
        items_total += qty
    status_map = {1: "Pending", 2: "Shipped", 10: "Completed",
                  11: "Awaiting Fulfillment"}
    order = {
        "id": next_id,
        "customer_id": int(customer_id),
        "status_id": int(status_id),
        "status": status_map.get(int(status_id), "Pending"),
        "total_inc_tax": round(subtotal, 2),
        "subtotal_inc_tax": round(subtotal, 2),
        "currency_code": currency_code,
        "payment_method": payment_method,
        "items_total": items_total,
        "date_created": "2026-05-28T00:00:00Z",
        "billing_first_name": billing_address.get("first_name", ""),
        "billing_last_name": billing_address.get("last_name", ""),
        "billing_email": billing_address.get("email", ""),
    }
    _orders_store.append(order)
    return _serialize_order(order)


# ---------------------------------------------------------------------------
# Customers (v3)
# ---------------------------------------------------------------------------

def list_customers(email=None, company=None, page=1, limit=50):
    items = _customers_store
    if email:
        items = [c for c in items if email.lower() in c["email"].lower()]
    if company:
        items = [c for c in items if company.lower() in c["company"].lower()]
    total = len(items)
    start = (page - 1) * limit
    page_items = items[start:start + limit]
    return {
        "data": [_serialize_customer(c) for c in page_items],
        "meta": _meta(total, len(page_items), page, limit),
    }
