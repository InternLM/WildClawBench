"""Data access module for the Stripe API mock service.

Amounts are integer cents. IDs use Stripe-style prefixes (cus_, ch_, in_,
sub_, pi_, re_). Mutations are held in process memory and reset on restart.
"""

import csv
import json
import time
import uuid
from copy import deepcopy
from pathlib import Path

DATA_DIR = Path(__file__).parent


def _load(filename):
    with open(DATA_DIR / filename, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


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
            **r,
            "object": "customer",
            "delinquent": _to_bool(r["delinquent"]),
            "balance": _to_int(r["balance"]),
            "created": _to_int(r["created"]),
        })
    return out


def _coerce_products(rows):
    return [{**r, "object": "product", "active": _to_bool(r["active"]),
             "created": _to_int(r["created"])} for r in rows]


def _coerce_prices(rows):
    out = []
    for r in rows:
        recurring = {"interval": r["recurring_interval"]} if r["recurring_interval"] else None
        out.append({
            **r,
            "object": "price",
            "unit_amount": _to_int(r["unit_amount"]),
            "active": _to_bool(r["active"]),
            "recurring": recurring,
            "type": "recurring" if recurring else "one_time",
        })
    return out


def _coerce_charges(rows):
    return [{**r, "object": "charge", "amount": _to_int(r["amount"]),
             "paid": _to_bool(r["paid"]), "refunded": _to_bool(r["refunded"]),
             "amount_refunded": _to_int(r["amount_refunded"]),
             "created": _to_int(r["created"])} for r in rows]


def _coerce_invoices(rows):
    out = []
    for r in rows:
        out.append({
            **r,
            "object": "invoice",
            "subscription": r["subscription"] or None,
            "charge": r["charge"] or None,
            "amount_due": _to_int(r["amount_due"]),
            "amount_paid": _to_int(r["amount_paid"]),
            "created": _to_int(r["created"]),
            "due_date": _to_int(r["due_date"]) if r["due_date"] else None,
        })
    return out


def _coerce_subscriptions(rows):
    return [{**r, "object": "subscription", "quantity": _to_int(r["quantity"]),
             "current_period_start": _to_int(r["current_period_start"]),
             "current_period_end": _to_int(r["current_period_end"]),
             "cancel_at_period_end": _to_bool(r["cancel_at_period_end"]),
             "created": _to_int(r["created"])} for r in rows]


_customers = _coerce_customers(_load("customers.csv"))
_products = _coerce_products(_load("products.csv"))
_prices = _coerce_prices(_load("prices.csv"))
_charges = _coerce_charges(_load("charges.csv"))
_invoices = _coerce_invoices(_load("invoices.csv"))
_subscriptions = _coerce_subscriptions(_load("subscriptions.csv"))

with open(DATA_DIR / "balance.json", encoding="utf-8") as _f:
    _balance = json.load(_f)

_customers_store = deepcopy(_customers)
_products_store = deepcopy(_products)
_prices_store = deepcopy(_prices)
_charges_store = deepcopy(_charges)
_invoices_store = deepcopy(_invoices)
_subscriptions_store = deepcopy(_subscriptions)
_payment_intents_store = []
_refunds_store = []
_balance_store = deepcopy(_balance)


# ---------------------------------------------------------------------------
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
    results = list(_customers_store)
    if email:
        results = [c for c in results if c["email"] == email]
    return _list_envelope(results[:limit], "/v1/customers")


def get_customer(customer_id):
    c = _find(_customers_store, customer_id)
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
    _customers_store.append(customer)
    return customer


# ---------------------------------------------------------------------------
# Products / Prices
# ---------------------------------------------------------------------------

def list_products(limit=10):
    return _list_envelope(list(_products_store)[:limit], "/v1/products")


def list_prices(limit=10, product=None):
    results = list(_prices_store)
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
    if customer and not _find(_customers_store, customer):
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
    _payment_intents_store.append(pi)
    return pi


def get_payment_intent(pi_id):
    pi = _find(_payment_intents_store, pi_id)
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
    _charges_store.append(charge)
    return charge


def list_charges(limit=10, customer=None):
    results = list(_charges_store)
    if customer:
        results = [c for c in results if c["customer"] == customer]
    return _list_envelope(results[:limit], "/v1/charges")


def get_charge(charge_id):
    c = _find(_charges_store, charge_id)
    return c if c else {"error": f"No such charge: {charge_id}"}


def create_charge(amount, currency="usd", customer=None, description=None):
    if amount is None or amount <= 0:
        return {"error": "amount must be a positive integer (cents)"}
    if customer and not _find(_customers_store, customer):
        return {"error": f"No such customer: {customer}"}
    return _record_charge(amount, currency, customer, description, None, "succeeded")


def create_refund(charge=None, amount=None, reason=None):
    if not charge:
        return {"error": "charge is required"}
    ch = _find(_charges_store, charge)
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
    _refunds_store.append(refund)
    return refund


# ---------------------------------------------------------------------------
# Invoices
# ---------------------------------------------------------------------------

def list_invoices(limit=10, customer=None, status=None):
    results = list(_invoices_store)
    if customer:
        results = [i for i in results if i["customer"] == customer]
    if status:
        results = [i for i in results if i["status"] == status]
    return _list_envelope(results[:limit], "/v1/invoices")


def get_invoice(invoice_id):
    inv = _find(_invoices_store, invoice_id)
    return inv if inv else {"error": f"No such invoice: {invoice_id}"}


def create_invoice(customer=None, amount_due=None, currency="usd", subscription=None):
    if not customer or not _find(_customers_store, customer):
        return {"error": f"No such customer: {customer}"}
    seq = len(_invoices_store) + 1
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
    _invoices_store.append(invoice)
    return invoice


# ---------------------------------------------------------------------------
# Subscriptions
# ---------------------------------------------------------------------------

def list_subscriptions(limit=10, customer=None, status=None):
    results = list(_subscriptions_store)
    if customer:
        results = [s for s in results if s["customer"] == customer]
    if status:
        results = [s for s in results if s["status"] == status]
    return _list_envelope(results[:limit], "/v1/subscriptions")


def get_subscription(sub_id):
    s = _find(_subscriptions_store, sub_id)
    return s if s else {"error": f"No such subscription: {sub_id}"}


def create_subscription(customer=None, price=None, quantity=1):
    if not customer or not _find(_customers_store, customer):
        return {"error": f"No such customer: {customer}"}
    if not price or not _find(_prices_store, price):
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
    _subscriptions_store.append(sub)
    return sub


# ---------------------------------------------------------------------------
# Balance
# ---------------------------------------------------------------------------

def get_balance():
    return _balance_store
