"""Data access module for the Square API mock service.

Amounts are integer cents wrapped in Square-style Money objects
({"amount": <int>, "currency": "USD"}). IDs use stable string identifiers.
Mutations are held in process memory and reset on restart.
"""

import csv
import json
import uuid
from copy import deepcopy
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).parent


def _load(filename):
    with open(DATA_DIR / filename, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


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
            "email_address": r["email_address"] or None,
            "phone_number": r["phone_number"] or None,
            "company_name": r["company_name"] or None,
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
            "quantity": str(_to_int(r["quantity"])),
            "state": r["state"],
        })
    return out


def _coerce_payments(rows):
    out = []
    for r in rows:
        out.append({
            "id": r["id"],
            "order_id": r["order_id"] or None,
            "customer_id": r["customer_id"] or None,
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
        for chunk in [c.strip() for c in r["line_items"].split(";") if c.strip()]:
            parts = chunk.rsplit("x", 1)
            uid = parts[0].strip()
            qty = parts[1].strip() if len(parts) > 1 else "1"
            line_items.append({
                "catalog_object_id": uid,
                "quantity": str(_to_int(qty, 1)),
            })
        out.append({
            "id": r["id"],
            "customer_id": r["customer_id"] or None,
            "location_id": r["location_id"],
            "line_items": line_items,
            "total_money": _money(r["total_amount"], r["currency"]),
            "state": r["state"],
            "created_at": r["created_at"],
        })
    return out


_customers = _coerce_customers(_load("customers.csv"))
_catalog = _coerce_catalog(_load("catalog_items.csv"))
_inventory = _coerce_inventory(_load("inventory.csv"))
_payments = _coerce_payments(_load("payments.csv"))
_orders = _coerce_orders(_load("orders.csv"))

with open(DATA_DIR / "merchant.json", encoding="utf-8") as _f:
    _merchant = json.load(_f)

_customers_store = deepcopy(_customers)
_catalog_store = deepcopy(_catalog)
_inventory_store = deepcopy(_inventory)
_payments_store = deepcopy(_payments)
_orders_store = deepcopy(_orders)
_refunds_store = []
_merchant_store = deepcopy(_merchant)


# ---------------------------------------------------------------------------
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
    results = list(_payments_store)
    if location_id:
        results = [p for p in results if p["location_id"] == location_id]
    return {"payments": results[:limit]}


def get_payment(payment_id):
    p = _find(_payments_store, payment_id)
    if not p:
        return {"error": f"Payment {payment_id} not found"}
    return {"payment": p}


def create_payment(amount, currency="USD", source_id="cnon:card-nonce-ok",
                   customer_id=None, order_id=None, location_id="LOC_MAIN"):
    if amount is None or _to_int(amount) <= 0:
        return {"error": "amount_money.amount must be a positive integer (cents)"}
    if customer_id and not _find(_customers_store, customer_id):
        return {"error": f"Customer {customer_id} not found"}
    seq = len(_payments_store) + 1
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
    _payments_store.append(payment)
    return {"payment": payment}


# ---------------------------------------------------------------------------
# Refunds
# ---------------------------------------------------------------------------

def create_refund(payment_id, amount=None, currency="USD", reason=None):
    payment = _find(_payments_store, payment_id)
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
    _refunds_store.append(refund)
    return {"refund": refund}


# ---------------------------------------------------------------------------
# Customers
# ---------------------------------------------------------------------------

def list_customers(limit=50):
    return {"customers": list(_customers_store)[:limit]}


def get_customer(customer_id):
    c = _find(_customers_store, customer_id)
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
    _customers_store.append(customer)
    return {"customer": customer}


# ---------------------------------------------------------------------------
# Catalog
# ---------------------------------------------------------------------------

def list_catalog(types=None):
    objects = list(_catalog_store)
    if types:
        wanted = {t.strip().upper() for t in types.split(",")}
        objects = [o for o in objects if o["type"] in wanted]
    return {"objects": objects}


# ---------------------------------------------------------------------------
# Orders
# ---------------------------------------------------------------------------

def get_order(order_id):
    o = _find(_orders_store, order_id)
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
        for item in _catalog_store:
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
    _orders_store.append(order)
    return {"order": order}


# ---------------------------------------------------------------------------
# Inventory
# ---------------------------------------------------------------------------

def get_inventory(catalog_object_id):
    counts = [i for i in _inventory_store if i["catalog_object_id"] == catalog_object_id]
    if not counts:
        return {"error": f"No inventory for catalog object {catalog_object_id}"}
    return {"counts": counts}


# ---------------------------------------------------------------------------
# Merchant
# ---------------------------------------------------------------------------

def get_merchant():
    return {"merchant": _merchant_store}
