"""Data access module for the WooCommerce REST API v3 mock service.

Mirrors a subset of the WooCommerce REST API (wc/v3): products, orders and
customers. Returns bare arrays/objects like the real API.
"""

import csv
from pathlib import Path

DATA_DIR = Path(__file__).parent

import sys as _sys
_sys.path.insert(0, str(DATA_DIR.parent))
from _mutable_store import (
    read_seed_with_ctx, get_store, opt_csv_list, opt_float, opt_int, strict_bool)

_store = get_store("woocommerce-api")
_API = "woocommerce-api"


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
            "slug": r["slug"],
            "sku": r["sku"],
            "type": r["type"],
            "status": r["status"],
            "price": opt_float(r, "price", default=None),
            "regular_price": opt_float(r, "regular_price", default=None),
            "sale_price": opt_float(r, "sale_price", default=None),
            "on_sale": strict_bool(r, "on_sale"),
            "stock_quantity": opt_int(r, "stock_quantity", default=0),
            "stock_status": r["stock_status"],
            "manage_stock": strict_bool(r, "manage_stock"),
            "categories": [c for c in opt_csv_list(r, "categories", sep=";") if c],
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
            "username": r["username"],
            "role": r["role"],
            "billing_city": r["billing_city"],
            "billing_country": r["billing_country"],
            "is_paying_customer": strict_bool(r, "is_paying_customer"),
            "date_created": r["date_created"],
        })
    return out


def _coerce_orders(rows):
    out = []
    for r in rows:
        out.append({
            "id": opt_int(r, "id", default=0),
            "number": r["number"],
            "customer_id": opt_int(r, "customer_id", default=0),
            "status": r["status"],
            "currency": r["currency"],
            "total": opt_float(r, "total", default=None),
            "subtotal": opt_float(r, "subtotal", default=None),
            "total_tax": opt_float(r, "total_tax", default=None),
            "payment_method": r["payment_method"],
            "payment_method_title": r["payment_method_title"],
            "billing_first_name": r["billing_first_name"],
            "billing_last_name": r["billing_last_name"],
            "billing_email": r["billing_email"],
            "date_created": r["date_created"],
        })
    return out








# ---------------------------------------------------------------------------
# Serializers
# ---------------------------------------------------------------------------

def _serialize_product(p):
    return {
        "id": p["id"],
        "name": p["name"],
        "slug": p["slug"],
        "sku": p["sku"],
        "type": p["type"],
        "status": p["status"],
        "price": f"{p['price']:.2f}",
        "regular_price": f"{p['regular_price']:.2f}",
        "sale_price": (f"{p['sale_price']:.2f}" if p["sale_price"] else ""),
        "on_sale": p["on_sale"],
        "stock_quantity": p["stock_quantity"],
        "stock_status": p["stock_status"],
        "manage_stock": p["manage_stock"],
        "categories": [{"name": c, "slug": c.lower().replace(" ", "-")}
                       for c in p["categories"]],
        "description": p["description"],
        "date_created": p["date_created"],
    }


def _serialize_customer(c):
    return {
        "id": c["id"],
        "first_name": c["first_name"],
        "last_name": c["last_name"],
        "email": c["email"],
        "username": c["username"],
        "role": c["role"],
        "billing": {"city": c["billing_city"], "country": c["billing_country"]},
        "is_paying_customer": c["is_paying_customer"],
        "date_created": c["date_created"],
    }


def _serialize_order(o):
    return {
        "id": o["id"],
        "number": o["number"],
        "customer_id": o["customer_id"],
        "status": o["status"],
        "currency": o["currency"],
        "total": f"{o['total']:.2f}",
        "subtotal": f"{o['subtotal']:.2f}",
        "total_tax": f"{o['total_tax']:.2f}",
        "payment_method": o["payment_method"],
        "payment_method_title": o["payment_method_title"],
        "billing": {
            "first_name": o["billing_first_name"],
            "last_name": o["billing_last_name"],
            "email": o["billing_email"],
        },
        "date_created": o["date_created"],
    }


# ---------------------------------------------------------------------------
# Products
# ---------------------------------------------------------------------------

def list_products(search=None, sku=None, status=None, page=1, per_page=10):
    items = _products_rows()
    if search:
        items = [p for p in items if search.lower() in p["name"].lower()]
    if sku:
        items = [p for p in items if p["sku"].lower() == sku.lower()]
    if status:
        items = [p for p in items if p["status"] == status]
    start = (page - 1) * per_page
    page_items = items[start:start + per_page]
    return [_serialize_product(p) for p in page_items]


def get_product(product_id):
    p = next((x for x in _products_rows() if x["id"] == int(product_id)), None)
    if not p:
        return {"error": "woocommerce_rest_product_invalid_id", "status": 404,
                "message": f"Invalid product ID: {product_id}"}
    return _serialize_product(p)


# ---------------------------------------------------------------------------
# Orders
# ---------------------------------------------------------------------------

def list_orders(customer=None, status=None, page=1, per_page=10):
    items = _orders_rows()
    if customer is not None:
        items = [o for o in items if o["customer_id"] == int(customer)]
    if status:
        items = [o for o in items if o["status"] == status]
    start = (page - 1) * per_page
    page_items = items[start:start + per_page]
    return [_serialize_order(o) for o in page_items]


def get_order(order_id):
    o = next((x for x in _orders_rows() if x["id"] == int(order_id)), None)
    if not o:
        return {"error": "woocommerce_rest_shop_order_invalid_id", "status": 404,
                "message": f"Invalid order ID: {order_id}"}
    return _serialize_order(o)


def create_order(customer_id=0, status="pending", currency="USD",
                 payment_method="bacs", payment_method_title="Direct Bank Transfer",
                 billing=None, line_items=None):
    billing = billing or {}
    line_items = line_items or []
    next_id = max((o["id"] for o in _orders_rows()), default=400) + 1
    subtotal = 0.0
    for line in line_items:
        prod = next((p for p in _products_rows()
                     if p["id"] == int(line.get("product_id", 0))), None)
        qty = int(line.get("quantity", 1))
        price = prod["price"] if prod else 0.0
        subtotal += price * qty
    tax = round(subtotal * 0.1, 2)
    order = {
        "id": next_id,
        "number": str(next_id),
        "customer_id": int(customer_id),
        "status": status,
        "currency": currency,
        "total": round(subtotal + tax, 2),
        "subtotal": round(subtotal, 2),
        "total_tax": tax,
        "payment_method": payment_method,
        "payment_method_title": payment_method_title,
        "billing_first_name": billing.get("first_name", ""),
        "billing_last_name": billing.get("last_name", ""),
        "billing_email": billing.get("email", ""),
        "date_created": "2026-05-28T00:00:00",
    }
    _store_insert("orders", order)
    return _serialize_order(order)


# ---------------------------------------------------------------------------
# Customers
# ---------------------------------------------------------------------------

def list_customers(search=None, email=None, page=1, per_page=10):
    items = _customers_rows()
    if email:
        items = [c for c in items if email.lower() in c["email"].lower()]
    if search:
        items = [c for c in items
                 if search.lower() in (c["first_name"] + " " + c["last_name"]).lower()
                 or search.lower() in c["email"].lower()]
    start = (page - 1) * per_page
    page_items = items[start:start + per_page]
    return [_serialize_customer(c) for c in page_items]

_store.eager_load()
