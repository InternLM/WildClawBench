"""Data access module for the Stripe API mock service.

Amounts are integer cents. IDs use Stripe-style prefixes (cus_, ch_, in_,
sub_, pi_, re_). Mutations are held in process memory and reset on restart.
"""

import csv
import json
import time
import uuid
from pathlib import Path

DATA_DIR = Path(__file__).parent

import sys as _sys
_sys.path.insert(0, str(DATA_DIR.parent))
from _mutable_store import (
    read_seed_with_ctx, get_store, opt_int, opt_str, strict_bool)

_store = get_store("stripe-api")
_API = "stripe-api"


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
_store.register("products", primary_key="id",
                initial_loader=lambda: _coerce_products(_load("products.json", "products")))
_store.register("prices", primary_key="id",
                initial_loader=lambda: _coerce_prices(_load("prices.json", "prices")))
_store.register("charges", primary_key="id",
                initial_loader=lambda: _coerce_charges(_load("charges.json", "charges")))
_store.register("invoices", primary_key="id",
                initial_loader=lambda: _coerce_invoices(_load("invoices.json", "invoices")))
_store.register("subscriptions", primary_key="id",
                initial_loader=lambda: _coerce_subscriptions(_load("subscriptions.json", "subscriptions")))
_store.register_document("balance", initial_loader=lambda: __import__('json').load(open(DATA_DIR / "balance.json", encoding="utf-8")))
_store.register("payment_intents", primary_key="payment_intent_id",
                initial_loader=lambda: [])
_store.register("refunds", primary_key="refund_id",
                initial_loader=lambda: [])


def _customers_rows():
    return _store.table("customers").rows()


def _products_rows():
    return _store.table("products").rows()


def _prices_rows():
    return _store.table("prices").rows()


def _charges_rows():
    return _store.table("charges").rows()


def _invoices_rows():
    return _store.table("invoices").rows()


def _subscriptions_rows():
    return _store.table("subscriptions").rows()


def _balance_doc():
    return _store.document("balance").get()


def _payment_intents_rows():
    return _store.table("payment_intents").rows()


def _refunds_rows():
    return _store.table("refunds").rows()



def _load(filename, table):
    return read_seed_with_ctx(DATA_DIR / filename, _API, table)


def _strip_ctx(r):
    return {k: v for k, v in r.items() if not k.startswith("__")}


def _now():
    return int(time.time())


def _to_bool(v):
    return str(v).strip().lower() == "true"


def _to_int(v, default=0):
    try:
        return int(v)
    except (TypeError, ValueError):
        return default


# ---------------------------------------------------------------------------
# Load + coerce
# ---------------------------------------------------------------------------

def _coerce_customers(rows):
    out = []
    for r in rows:
        out.append({
            **_strip_ctx(r),
            "object": "customer",
            "delinquent": strict_bool(r, "delinquent"),
            "balance": opt_int(r, "balance", default=0),
            "created": opt_int(r, "created", default=0),
        })
    return out


def _coerce_products(rows):
    return [{**_strip_ctx(r), "object": "product", "active": strict_bool(r, "active"),
             "created": opt_int(r, "created", default=0)} for r in rows]


def _coerce_prices(rows):
    out = []
    for r in rows:
        recurring = {"interval": r["recurring_interval"]} if r["recurring_interval"] else None
        out.append({
            **_strip_ctx(r),
            "object": "price",
            "unit_amount": opt_int(r, "unit_amount", default=0),
            "active": strict_bool(r, "active"),
            "recurring": recurring,
            "type": "recurring" if recurring else "one_time",
        })
    return out


def _coerce_charges(rows):
    return [{**_strip_ctx(r), "object": "charge", "amount": opt_int(r, "amount", default=0),
             "paid": strict_bool(r, "paid"), "refunded": strict_bool(r, "refunded"),
             "amount_refunded": opt_int(r, "amount_refunded", default=0),
             "created": opt_int(r, "created", default=0)} for r in rows]


def _coerce_invoices(rows):
    out = []
    for r in rows:
        out.append({
            **_strip_ctx(r),
            "object": "invoice",
            "subscription": opt_str(r, "subscription", default="") or None,
            "charge": opt_str(r, "charge", default="") or None,
            "amount_due": opt_int(r, "amount_due", default=0),
            "amount_paid": opt_int(r, "amount_paid", default=0),
            "created": opt_int(r, "created", default=0),
            "due_date": opt_int(r, "due_date", default=None),
        })
    return out


def _coerce_subscriptions(rows):
    return [{**_strip_ctx(r), "object": "subscription", "quantity": opt_int(r, "quantity", default=0),
             "current_period_start": opt_int(r, "current_period_start", default=0),
             "current_period_end": opt_int(r, "current_period_end", default=0),
             "cancel_at_period_end": strict_bool(r, "cancel_at_period_end"),
             "created": opt_int(r, "created", default=0)} for r in rows]









# Helpers
# ---------------------------------------------------------------------------

def _new_id(prefix):
    return f"{prefix}_{uuid.uuid4().hex[:16]}"


def _list_envelope(data, url):
    return {"object": "list", "url": url, "has_more": False, "data": data}


def _find(store, obj_id):
    return next((x for x in store if x["id"] == obj_id), None)


# ---------------------------------------------------------------------------
# Customers
# ---------------------------------------------------------------------------

def list_customers(limit=10, email=None):
    results = list(_customers_rows())
    if email:
        results = [c for c in results if c["email"] == email]
    return _list_envelope(results[:limit], "/v1/customers")


def get_customer(customer_id):
    c = _find(_customers_rows(), customer_id)
    return c if c else {"error": f"No such customer: {customer_id}"}


def create_customer(name=None, email=None, description=None, currency="usd", phone=None):
    customer = {
        "id": _new_id("cus"),
        "object": "customer",
        "name": name or "",
        "email": email or "",
        "description": description or "",
        "currency": currency or "usd",
        "delinquent": False,
        "balance": 0,
        "phone": phone or "",
        "created": _now(),
    }
    _store_insert("customers", customer)
    return customer


# ---------------------------------------------------------------------------
# Products / Prices
# ---------------------------------------------------------------------------

def list_products(limit=10):
    return _list_envelope(list(_products_rows())[:limit], "/v1/products")


def list_prices(limit=10, product=None):
    results = list(_prices_rows())
    if product:
        results = [p for p in results if p["product"] == product]
    return _list_envelope(results[:limit], "/v1/prices")


# ---------------------------------------------------------------------------
# Payment Intents / Charges / Refunds
# ---------------------------------------------------------------------------

def create_payment_intent(amount, currency="usd", customer=None, description=None,
                          confirm=False):
    if amount is None or amount <= 0:
        return {"error": "amount must be a positive integer (cents)"}
    if customer and not _find(_customers_rows(), customer):
        return {"error": f"No such customer: {customer}"}
    pi = {
        "id": _new_id("pi"),
        "object": "payment_intent",
        "amount": int(amount),
        "currency": currency or "usd",
        "customer": customer,
        "description": description or "",
        "status": "succeeded" if confirm else "requires_confirmation",
        "latest_charge": None,
        "created": _now(),
    }
    if confirm:
        charge = _record_charge(amount, currency, customer, description, pi["id"], "succeeded")
        pi["latest_charge"] = charge["id"]
    _store_insert("payment_intents", pi)
    return pi


def get_payment_intent(pi_id):
    pi = _find(_payment_intents_rows(), pi_id)
    return pi if pi else {"error": f"No such payment_intent: {pi_id}"}


def _record_charge(amount, currency, customer, description, payment_intent, status):
    charge = {
        "id": _new_id("ch"),
        "object": "charge",
        "customer": customer,
        "amount": int(amount),
        "currency": currency or "usd",
        "status": status,
        "paid": status == "succeeded",
        "refunded": False,
        "amount_refunded": 0,
        "description": description or "",
        "payment_intent": payment_intent,
        "created": _now(),
    }
    _store_insert("charges", charge)
    return charge


def list_charges(limit=10, customer=None):
    results = list(_charges_rows())
    if customer:
        results = [c for c in results if c["customer"] == customer]
    return _list_envelope(results[:limit], "/v1/charges")


def get_charge(charge_id):
    c = _find(_charges_rows(), charge_id)
    return c if c else {"error": f"No such charge: {charge_id}"}


def create_charge(amount, currency="usd", customer=None, description=None):
    if amount is None or amount <= 0:
        return {"error": "amount must be a positive integer (cents)"}
    if customer and not _find(_customers_rows(), customer):
        return {"error": f"No such customer: {customer}"}
    return _record_charge(amount, currency, customer, description, None, "succeeded")


def create_refund(charge=None, amount=None, reason=None):
    if not charge:
        return {"error": "charge is required"}
    ch = _find(_charges_rows(), charge)
    if not ch:
        return {"error": f"No such charge: {charge}"}
    refundable = ch["amount"] - ch["amount_refunded"]
    refund_amount = int(amount) if amount is not None else refundable
    if refund_amount <= 0 or refund_amount > refundable:
        return {"error": f"Refund amount {refund_amount} exceeds refundable {refundable}"}
    refund = {
        "id": _new_id("re"),
        "object": "refund",
        "charge": charge,
        "amount": refund_amount,
        "currency": ch["currency"],
        "reason": reason or "requested_by_customer",
        "status": "succeeded",
        "created": _now(),
    }
    ch["amount_refunded"] += refund_amount
    ch["refunded"] = ch["amount_refunded"] >= ch["amount"]
    _store_insert("refunds", refund)
    return refund


# ---------------------------------------------------------------------------
# Invoices
# ---------------------------------------------------------------------------

def list_invoices(limit=10, customer=None, status=None):
    results = list(_invoices_rows())
    if customer:
        results = [i for i in results if i["customer"] == customer]
    if status:
        results = [i for i in results if i["status"] == status]
    return _list_envelope(results[:limit], "/v1/invoices")


def get_invoice(invoice_id):
    inv = _find(_invoices_rows(), invoice_id)
    return inv if inv else {"error": f"No such invoice: {invoice_id}"}


def create_invoice(customer=None, amount_due=None, currency="usd", subscription=None):
    if not customer or not _find(_customers_rows(), customer):
        return {"error": f"No such customer: {customer}"}
    seq = len(_invoices_rows()) + 1
    invoice = {
        "id": _new_id("in"),
        "object": "invoice",
        "customer": customer,
        "subscription": subscription,
        "amount_due": int(amount_due) if amount_due is not None else 0,
        "amount_paid": 0,
        "currency": currency or "usd",
        "status": "draft",
        "number": f"ORBIT-{seq:04d}",
        "charge": None,
        "created": _now(),
        "due_date": None,
    }
    _store_insert("invoices", invoice)
    return invoice


# ---------------------------------------------------------------------------
# Subscriptions
# ---------------------------------------------------------------------------

def list_subscriptions(limit=10, customer=None, status=None):
    results = list(_subscriptions_rows())
    if customer:
        results = [s for s in results if s["customer"] == customer]
    if status:
        results = [s for s in results if s["status"] == status]
    return _list_envelope(results[:limit], "/v1/subscriptions")


def get_subscription(sub_id):
    s = _find(_subscriptions_rows(), sub_id)
    return s if s else {"error": f"No such subscription: {sub_id}"}


def create_subscription(customer=None, price=None, quantity=1):
    if not customer or not _find(_customers_rows(), customer):
        return {"error": f"No such customer: {customer}"}
    if not price or not _find(_prices_rows(), price):
        return {"error": f"No such price: {price}"}
    now = _now()
    sub = {
        "id": _new_id("sub"),
        "object": "subscription",
        "customer": customer,
        "price": price,
        "status": "active",
        "quantity": int(quantity or 1),
        "current_period_start": now,
        "current_period_end": now + 2592000,
        "cancel_at_period_end": False,
        "created": now,
    }
    _store_insert("subscriptions", sub)
    return sub


# ---------------------------------------------------------------------------
# Balance
# ---------------------------------------------------------------------------

def get_balance():
    return _balance_doc()

_store.eager_load()
