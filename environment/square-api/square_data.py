"""Data access module for the Square API mock service.

Amounts are integer cents wrapped in Square-style Money objects
({"amount": <int>, "currency": "USD"}). IDs use stable string identifiers.
Mutations are held in process memory and reset on restart.
"""

import csv
import json
import uuid
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).parent

import sys as _sys
_sys.path.insert(0, str(DATA_DIR.parent))
from _mutable_store import (
    read_seed_with_ctx, get_store, opt_csv_list, opt_int, opt_str)

_store = get_store("square-api")
_API = "square-api"


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

_store.register("customers", primary_key="id",
                initial_loader=lambda: _coerce_customers(_load("customers.json", "customers")))
_store.register("catalog", primary_key="id",
                initial_loader=lambda: _coerce_catalog(_load("catalog_items.json", "catalog")))
_store.register("inventory", primary_key="catalog_object_id",
                initial_loader=lambda: _coerce_inventory(_load("inventory.json", "inventory")))
_store.register("payments", primary_key="id",
                initial_loader=lambda: _coerce_payments(_load("payments.json", "payments")))
_store.register("orders", primary_key="id",
                initial_loader=lambda: _coerce_orders(_load("orders.json", "orders")))
_store.register_document("merchant", initial_loader=lambda: __import__('json').load(open(DATA_DIR / "merchant.json", encoding="utf-8")))
_store.register("refunds", primary_key="refund_id",
                initial_loader=lambda: [])


def _customers_rows():
    return _store.table("customers").rows()


def _catalog_rows():
    return _store.table("catalog").rows()


def _inventory_rows():
    return _store.table("inventory").rows()


def _payments_rows():
    return _store.table("payments").rows()


def _orders_rows():
    return _store.table("orders").rows()


def _merchant_doc():
    return _store.document("merchant").get()


def _refunds_rows():
    return _store.table("refunds").rows()



def _load(filename, table):
    return read_seed_with_ctx(DATA_DIR / filename, _API, table)


def _strip_ctx(r):
    return {k: v for k, v in r.items() if not k.startswith("__")}


def _now():
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


def _to_bool(v):
    return str(v).strip().lower() == "true"


def _to_int(v, default=0):
    try:
        return int(v)
    except (TypeError, ValueError):
        return default


def _money(amount, currency="USD"):
    return {"amount": _to_int(amount), "currency": currency or "USD"}


# ---------------------------------------------------------------------------
# Load + coerce
# ---------------------------------------------------------------------------

def _coerce_customers(rows):
    out = []
    for r in rows:
        out.append({
            "id": r["id"],
            "given_name": r["given_name"],
            "family_name": r["family_name"],
            "email_address": opt_str(r, "email_address", default="") or None,
            "phone_number": opt_str(r, "phone_number", default="") or None,
            "company_name": opt_str(r, "company_name", default="") or None,
            "created_at": r["created_at"],
        })
    return out


def _coerce_catalog(rows):
    out = []
    for r in rows:
        out.append({
            "type": r["type"],
            "id": r["id"],
            "item_data": {
                "name": r["name"],
                "description": r["description"],
                "category": r["category"],
                "variations": [{
                    "type": "ITEM_VARIATION",
                    "id": r["variation_id"],
                    "item_variation_data": {
                        "name": r["variation_name"],
                        "price_money": _money(r["price_amount"], r["currency"]),
                    },
                }],
            },
        })
    return out


def _coerce_inventory(rows):
    out = []
    for r in rows:
        out.append({
            "catalog_object_id": r["catalog_object_id"],
            "location_id": r["location_id"],
            "quantity": str(opt_int(r, "quantity", default=0)),
            "state": r["state"],
        })
    return out


def _coerce_payments(rows):
    out = []
    for r in rows:
        out.append({
            "id": r["id"],
            "order_id": opt_str(r, "order_id", default="") or None,
            "customer_id": opt_str(r, "customer_id", default="") or None,
            "amount_money": _money(r["amount"], r["currency"]),
            "status": r["status"],
            "source_type": r["source_type"],
            "location_id": r["location_id"],
            "receipt_number": r["receipt_number"],
            "created_at": r["created_at"],
        })
    return out


def _coerce_orders(rows):
    out = []
    for r in rows:
        line_items = []
        for chunk in [c.strip() for c in opt_csv_list(r, "line_items", sep=";") if c.strip()]:
            parts = chunk.rsplit("x", 1)
            uid = parts[0].strip()
            qty = parts[1].strip() if len(parts) > 1 else "1"
            line_items.append({
                "catalog_object_id": uid,
                "quantity": str(_to_int(qty, 1)),
            })
        out.append({
            "id": r["id"],
            "customer_id": opt_str(r, "customer_id", default="") or None,
            "location_id": r["location_id"],
            "line_items": line_items,
            "total_money": _money(r["total_amount"], r["currency"]),
            "state": r["state"],
            "created_at": r["created_at"],
        })
    return out








# Helpers
# ---------------------------------------------------------------------------

def _new_id(prefix):
    return f"{prefix}_{uuid.uuid4().hex[:18].upper()}"


def _find(store, obj_id):
    return next((x for x in store if x["id"] == obj_id), None)


# ---------------------------------------------------------------------------
# Payments
# ---------------------------------------------------------------------------

def list_payments(location_id=None, limit=50):
    results = list(_payments_rows())
    if location_id:
        results = [p for p in results if p["location_id"] == location_id]
    return {"payments": results[:limit]}


def get_payment(payment_id):
    p = _find(_payments_rows(), payment_id)
    if not p:
        return {"error": f"Payment {payment_id} not found"}
    return {"payment": p}


def create_payment(amount, currency="USD", source_id="cnon:card-nonce-ok",
                   customer_id=None, order_id=None, location_id="LOC_MAIN"):
    if amount is None or _to_int(amount) <= 0:
        return {"error": "amount_money.amount must be a positive integer (cents)"}
    if customer_id and not _find(_customers_rows(), customer_id):
        return {"error": f"Customer {customer_id} not found"}
    seq = len(_payments_rows()) + 1
    payment = {
        "id": _new_id("PAY"),
        "order_id": order_id,
        "customer_id": customer_id,
        "amount_money": _money(amount, currency),
        "status": "COMPLETED",
        "source_type": "CARD",
        "location_id": location_id,
        "receipt_number": f"RCP{seq:03d}",
        "created_at": _now(),
    }
    _store_insert("payments", payment)
    return {"payment": payment}


# ---------------------------------------------------------------------------
# Refunds
# ---------------------------------------------------------------------------

def create_refund(payment_id, amount=None, currency="USD", reason=None):
    payment = _find(_payments_rows(), payment_id)
    if not payment:
        return {"error": f"Payment {payment_id} not found"}
    paid = payment["amount_money"]["amount"]
    refund_amount = _to_int(amount) if amount is not None else paid
    if refund_amount <= 0 or refund_amount > paid:
        return {"error": f"Refund amount {refund_amount} exceeds payment amount {paid}"}
    refund = {
        "id": _new_id("REF"),
        "payment_id": payment_id,
        "amount_money": _money(refund_amount, currency or payment["amount_money"]["currency"]),
        "status": "COMPLETED",
        "reason": reason or "Requested by customer",
        "created_at": _now(),
    }
    _store_insert("refunds", refund)
    return {"refund": refund}


# ---------------------------------------------------------------------------
# Customers
# ---------------------------------------------------------------------------

def list_customers(limit=50):
    return {"customers": list(_customers_rows())[:limit]}


def get_customer(customer_id):
    c = _find(_customers_rows(), customer_id)
    if not c:
        return {"error": f"Customer {customer_id} not found"}
    return {"customer": c}


def create_customer(given_name=None, family_name=None, email_address=None,
                    phone_number=None, company_name=None):
    customer = {
        "id": _new_id("CUST"),
        "given_name": given_name or "",
        "family_name": family_name or "",
        "email_address": email_address,
        "phone_number": phone_number,
        "company_name": company_name,
        "created_at": _now(),
    }
    _store_insert("customers", customer)
    return {"customer": customer}


# ---------------------------------------------------------------------------
# Catalog
# ---------------------------------------------------------------------------

def list_catalog(types=None):
    objects = list(_catalog_rows())
    if types:
        wanted = {t.strip().upper() for t in types.split(",")}
        objects = [o for o in objects if o["type"] in wanted]
    return {"objects": objects}


# ---------------------------------------------------------------------------
# Orders
# ---------------------------------------------------------------------------

def get_order(order_id):
    o = _find(_orders_rows(), order_id)
    if not o:
        return {"error": f"Order {order_id} not found"}
    return {"order": o}


def create_order(customer_id=None, location_id="LOC_MAIN", line_items=None):
    line_items = line_items or []
    total = 0
    normalized = []
    for li in line_items:
        uid = li.get("catalog_object_id")
        qty = _to_int(li.get("quantity", 1), 1)
        unit_amount = 0
        for item in _catalog_rows():
            for var in item["item_data"]["variations"]:
                if var["id"] == uid:
                    unit_amount = var["item_variation_data"]["price_money"]["amount"]
        total += unit_amount * qty
        normalized.append({"catalog_object_id": uid, "quantity": str(qty)})
    order = {
        "id": _new_id("ORD"),
        "customer_id": customer_id,
        "location_id": location_id,
        "line_items": normalized,
        "total_money": _money(total, "USD"),
        "state": "OPEN",
        "created_at": _now(),
    }
    _store_insert("orders", order)
    return {"order": order}


# ---------------------------------------------------------------------------
# Inventory
# ---------------------------------------------------------------------------

def get_inventory(catalog_object_id):
    counts = [i for i in _inventory_rows() if i["catalog_object_id"] == catalog_object_id]
    if not counts:
        return {"error": f"No inventory for catalog object {catalog_object_id}"}
    return {"counts": counts}


# ---------------------------------------------------------------------------
# Merchant
# ---------------------------------------------------------------------------

def get_merchant():
    return {"merchant": _merchant_doc()}

_store.eager_load()
