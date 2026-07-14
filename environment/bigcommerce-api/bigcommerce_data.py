"""Data access module for the BigCommerce API mock service.

Mirrors a subset of the BigCommerce Catalog (v3), Orders (v2) and Customers
(v3) APIs. v3 list responses are wrapped in `{"data": [...], "meta": {...}}`;
v2 responses are bare arrays/objects.
"""

import csv
from pathlib import Path

DATA_DIR = Path(__file__).parent

import sys as _sys
_sys.path.insert(0, str(DATA_DIR.parent))
from _mutable_store import (
    read_seed_with_ctx, get_store, opt_csv_list, opt_float, opt_int, strict_bool)

_store = get_store("bigcommerce-api")
_API = "bigcommerce-api"


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

_store.register("products", primary_key="id",
                initial_loader=lambda: _coerce_products(_load("products.json", "products")))
_store.register("customers", primary_key="id",
                initial_loader=lambda: _coerce_customers(_load("customers.json", "customers")))
_store.register("orders", primary_key="id",
                initial_loader=lambda: _coerce_orders(_load("orders.json", "orders")))


def _products_rows():
    return _store.table("products").rows()


def _customers_rows():
    return _store.table("customers").rows()


def _orders_rows():
    return _store.table("orders").rows()



def _load(filename, table):
    return read_seed_with_ctx(DATA_DIR / filename, _API, table)


def _strip_ctx(r):
    return {k: v for k, v in r.items() if not k.startswith("__")}


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
            "id": opt_int(r, "id", default=0),
            "name": r["name"],
            "sku": r["sku"],
            "type": r["type"],
            "price": opt_float(r, "price", default=None),
            "sale_price": opt_float(r, "sale_price", default=None),
            "cost_price": opt_float(r, "cost_price", default=None),
            "weight": opt_float(r, "weight", default=None),
            "inventory_level": opt_int(r, "inventory_level", default=0),
            "inventory_tracking": r["inventory_tracking"],
            "is_visible": strict_bool(r, "is_visible"),
            "brand_id": opt_int(r, "brand_id", default=0),
            "categories": [int(c) for c in opt_csv_list(r, "categories", sep=";") if c],
            "description": r["description"],
            "date_created": r["date_created"],
        })
    return out


def _coerce_customers(rows):
    out = []
    for r in rows:
        out.append({
            "id": opt_int(r, "id", default=0),
            "first_name": r["first_name"],
            "last_name": r["last_name"],
            "email": r["email"],
            "company": r["company"],
            "phone": r["phone"],
            "customer_group_id": opt_int(r, "customer_group_id", default=0),
            "date_created": r["date_created"],
        })
    return out


def _coerce_orders(rows):
    out = []
    for r in rows:
        out.append({
            "id": opt_int(r, "id", default=0),
            "customer_id": opt_int(r, "customer_id", default=0),
            "status_id": opt_int(r, "status_id", default=0),
            "status": r["status"],
            "total_inc_tax": opt_float(r, "total_inc_tax", default=None),
            "subtotal_inc_tax": opt_float(r, "subtotal_inc_tax", default=None),
            "currency_code": r["currency_code"],
            "payment_method": r["payment_method"],
            "items_total": opt_int(r, "items_total", default=0),
            "date_created": r["date_created"],
            "billing_first_name": r["billing_first_name"],
            "billing_last_name": r["billing_last_name"],
            "billing_email": r["billing_email"],
        })
    return out








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
    items = _products_rows()
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
    p = next((x for x in _products_rows() if x["id"] == int(product_id)), None)
    if not p:
        return {"error": "Not Found", "status": 404,
                "title": f"Product {product_id} not found"}
    return {"data": _serialize_product(p), "meta": {}}


# ---------------------------------------------------------------------------
# Orders (v2)
# ---------------------------------------------------------------------------

def list_orders(customer_id=None, status_id=None, page=1, limit=50):
    items = _orders_rows()
    if customer_id is not None:
        items = [o for o in items if o["customer_id"] == int(customer_id)]
    if status_id is not None:
        items = [o for o in items if o["status_id"] == int(status_id)]
    start = (page - 1) * limit
    page_items = items[start:start + limit]
    return [_serialize_order(o) for o in page_items]


def get_order(order_id):
    o = next((x for x in _orders_rows() if x["id"] == int(order_id)), None)
    if not o:
        return {"error": "Not Found", "status": 404,
                "title": f"Order {order_id} not found"}
    return _serialize_order(o)


def create_order(customer_id=0, status_id=1, payment_method="manual",
                 currency_code="USD", billing_address=None, products=None):
    billing_address = billing_address or {}
    products = products or []
    next_id = max((o["id"] for o in _orders_rows()), default=2000) + 1
    subtotal = 0.0
    items_total = 0
    for line in products:
        prod = next((p for p in _products_rows()
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
    _store_insert("orders", order)
    return _serialize_order(order)


# ---------------------------------------------------------------------------
# Customers (v3)
# ---------------------------------------------------------------------------

def list_customers(email=None, company=None, page=1, limit=50):
    items = _customers_rows()
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

_store.eager_load()
