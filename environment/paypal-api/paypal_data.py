"""Data access module for the PayPal API mock service.

Amounts use PayPal-style Money objects {"currency_code": "USD", "value": "49.99"}
where value is a string decimal. Statuses follow PayPal conventions
(CREATED / APPROVED / COMPLETED / VOIDED). Mutations are in-memory.
"""

import csv
import uuid
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).parent

import sys as _sys
_sys.path.insert(0, str(DATA_DIR.parent))
from _mutable_store import (
    read_seed_with_ctx, get_store,
    strict_bool,
)

_store = get_store("paypal-api")
_API = "paypal-api"


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

_store.register("orders", primary_key="id",
                initial_loader=lambda: _coerce_orders(_load("orders.json", "orders")))
_store.register("captures", primary_key="id",
                initial_loader=lambda: _coerce_captures(_load("captures.json", "captures")))
_store.register("invoices", primary_key="id",
                initial_loader=lambda: _coerce_invoices(_load("invoices.json", "invoices")))
_store.register("payouts", primary_key="payout_batch_id",
                initial_loader=lambda: [{**_strip_ctx(r), 'payout_batch_id': r['batch_header']['payout_batch_id']} for r in _coerce_payouts(_load("payouts.json", "payouts"))])
_store.register("refunds", primary_key="id",
                initial_loader=lambda: _coerce_refunds(_load("refunds.json", "refunds")))


def _orders_rows():
    return _store.table("orders").rows()


def _captures_rows():
    return _store.table("captures").rows()


def _invoices_rows():
    return _store.table("invoices").rows()


def _payouts_rows():
    return _store.table("payouts").rows()


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


def _money(value, currency="USD"):
    try:
        value = f"{float(value):.2f}"
    except (TypeError, ValueError):
        value = "0.00"
    return {"currency_code": currency or "USD", "value": value}


# ---------------------------------------------------------------------------
# Load + coerce
# ---------------------------------------------------------------------------

def _coerce_orders(rows):
    out = []
    for r in rows:
        out.append({
            "id": r["id"],
            "intent": r["intent"],
            "status": r["status"],
            "purchase_units": [{
                "amount": _money(r["amount_value"], r["currency_code"]),
                "payee": {"email_address": r["payee_email"]},
                "description": r["description"],
            }],
            "create_time": r["create_time"],
        })
    return out


def _coerce_captures(rows):
    out = []
    for r in rows:
        out.append({
            "id": r["id"],
            "order_id": r["order_id"],
            "status": r["status"],
            "amount": _money(r["amount_value"], r["currency_code"]),
            "final_capture": strict_bool(r, "final_capture"),
            "create_time": r["create_time"],
        })
    return out


def _coerce_invoices(rows):
    out = []
    for r in rows:
        out.append({
            "id": r["id"],
            "detail": {
                "invoice_number": r["invoice_number"],
                "currency_code": r["currency_code"],
                "note": r["note"],
            },
            "status": r["status"],
            "primary_recipients": [{"billing_info": {"email_address": r["recipient_email"]}}],
            "amount": _money(r["amount_value"], r["currency_code"]),
            "due_date": r["due_date"],
        })
    return out


def _coerce_payouts(rows):
    out = []
    for r in rows:
        out.append({
            "batch_header": {
                "payout_batch_id": r["payout_batch_id"],
                "batch_status": r["status"],
                "sender_batch_header": {"sender_batch_id": r["sender_batch_id"]},
                "amount": _money(r["amount_value"], r["currency_code"]),
            },
            "recipient_email": r["recipient_email"],
            "create_time": r["create_time"],
        })
    return out


def _coerce_refunds(rows):
    out = []
    for r in rows:
        out.append({
            "id": r["id"],
            "capture_id": r["capture_id"],
            "status": r["status"],
            "amount": _money(r["amount_value"], r["currency_code"]),
            "note_to_payer": r["note_to_payer"],
            "create_time": r["create_time"],
        })
    return out












# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _new_order_id():
    return f"ORDER-{uuid.uuid4().hex[:17].upper()}"


def _new_id(prefix):
    return f"{prefix}_{uuid.uuid4().hex[:16].upper()}"


def _find(store, obj_id):
    return next((x for x in store if x["id"] == obj_id), None)


# ---------------------------------------------------------------------------
# Checkout Orders
# ---------------------------------------------------------------------------

def create_order(intent="CAPTURE", amount_value="0.00", currency_code="USD",
                 payee_email="merchant@orbit-labs.com", description=""):
    order = {
        "id": _new_order_id(),
        "intent": intent or "CAPTURE",
        "status": "CREATED",
        "purchase_units": [{
            "amount": _money(amount_value, currency_code),
            "payee": {"email_address": payee_email},
            "description": description,
        }],
        "create_time": _now(),
    }
    _store_insert("orders", order)
    return order


def get_order(order_id):
    o = _find(_orders_rows(), order_id)
    return o if o else {"error": f"Order {order_id} not found"}


def capture_order(order_id):
    order = _find(_orders_rows(), order_id)
    if not order:
        return {"error": f"Order {order_id} not found"}
    if order["status"] == "COMPLETED":
        return {"error": f"Order {order_id} has already been captured"}
    if order["status"] == "VOIDED":
        return {"error": f"Order {order_id} is voided and cannot be captured"}
    amount = order["purchase_units"][0]["amount"]
    capture = {
        "id": _new_id("CAP"),
        "order_id": order_id,
        "status": "COMPLETED",
        "amount": amount,
        "final_capture": True,
        "create_time": _now(),
    }
    _store_insert("captures", capture)
    order["status"] = "COMPLETED"
    return {
        "id": order_id,
        "status": "COMPLETED",
        "purchase_units": [{
            "payments": {"captures": [capture]},
        }],
    }


# ---------------------------------------------------------------------------
# Refunds
# ---------------------------------------------------------------------------

def create_refund(capture_id, amount_value=None, currency_code="USD", note_to_payer=None):
    capture = _find(_captures_rows(), capture_id)
    if not capture:
        return {"error": f"Capture {capture_id} not found"}
    if amount_value is None:
        amount = capture["amount"]
    else:
        amount = _money(amount_value, currency_code or capture["amount"]["currency_code"])
    refund = {
        "id": _new_id("REF"),
        "capture_id": capture_id,
        "status": "COMPLETED",
        "amount": amount,
        "note_to_payer": note_to_payer or "",
        "create_time": _now(),
    }
    _store_insert("refunds", refund)
    return refund


def get_refund(refund_id):
    r = _find(_refunds_rows(), refund_id)
    return r if r else {"error": f"Refund {refund_id} not found"}


# ---------------------------------------------------------------------------
# Invoices
# ---------------------------------------------------------------------------

def list_invoices(status=None, page_size=20):
    results = list(_invoices_rows())
    if status:
        results = [i for i in results if i["status"] == status.upper()]
    return {
        "total_items": len(results),
        "total_pages": 1,
        "items": results[:page_size],
    }


def create_invoice(invoice_number=None, recipient_email=None, amount_value="0.00",
                   currency_code="USD", due_date=None, note=None):
    seq = len(_invoices_rows()) + 1
    invoice = {
        "id": _new_id("INV2"),
        "detail": {
            "invoice_number": invoice_number or f"INV-{seq:04d}",
            "currency_code": currency_code or "USD",
            "note": note or "",
        },
        "status": "DRAFT",
        "primary_recipients": [{"billing_info": {"email_address": recipient_email or ""}}],
        "amount": _money(amount_value, currency_code),
        "due_date": due_date,
    }
    _store_insert("invoices", invoice)
    return invoice


# ---------------------------------------------------------------------------
# Payouts
# ---------------------------------------------------------------------------

def create_payout(sender_batch_id=None, amount_value="0.00", currency_code="USD",
                  recipient_email=None, note=None):
    payout = {
        "batch_header": {
            "payout_batch_id": f"PAYOUT-{uuid.uuid4().hex[:12].upper()}",
            "batch_status": "PENDING",
            "sender_batch_header": {
                "sender_batch_id": sender_batch_id or f"Batch_{uuid.uuid4().hex[:8]}",
                "email_subject": note or "You have a payout",
            },
            "amount": _money(amount_value, currency_code),
        },
        "recipient_email": recipient_email or "",
        "create_time": _now(),
    }
    _store_insert("payouts", payout)
    return payout

_store.eager_load()
