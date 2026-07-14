"""Data access module for the Xero accounting mock service.

Mirrors a subset of the Xero Accounting API (api.xro/2.0): Invoices, Contacts,
and Accounts. Xero wraps collections under a PascalCase key, e.g.
{"Invoices": [...]}. Creating an invoice appends to an in-memory store that
resets on restart.
"""

import csv
import uuid
import time
from pathlib import Path

DATA_DIR = Path(__file__).parent

import sys as _sys
_sys.path.insert(0, str(DATA_DIR.parent))
from _mutable_store import (
    read_seed_with_ctx, get_store,
    strict_bool,
    opt_float,
)

_store = get_store("xero-api")
_API = "xero-api"


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

_store.register("contacts", primary_key="ContactID",
                initial_loader=lambda: _coerce_contacts(_load("contacts.json", "contacts")))
_store.register("accounts", primary_key="AccountID",
                initial_loader=lambda: _coerce_accounts(_load("accounts.json", "accounts")))
_store.register("invoices", primary_key="InvoiceID",
                initial_loader=lambda: _coerce_invoices(_load("invoices.json", "invoices")))


def _contacts_rows():
    return _store.table("contacts").rows()


def _accounts_rows():
    return _store.table("accounts").rows()


def _invoices_rows():
    return _store.table("invoices").rows()



def _load(filename, table):
    return read_seed_with_ctx(DATA_DIR / filename, _API, table)


def _strip_ctx(r):
    return {k: v for k, v in r.items() if not k.startswith("__")}


def _to_bool(v):
    return str(v).strip().lower() == "true"


def _to_float(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return 0.0


# ---------------------------------------------------------------------------
# Load + coerce
# ---------------------------------------------------------------------------

def _coerce_contacts(rows):
    out = []
    for r in rows:
        out.append({
            "ContactID": r["contact_id"],
            "Name": r["name"],
            "FirstName": r["first_name"],
            "LastName": r["last_name"],
            "EmailAddress": r["email"],
            "IsCustomer": strict_bool(r, "is_customer"),
            "IsSupplier": strict_bool(r, "is_supplier"),
            "ContactStatus": r["status"],
            "AccountNumber": r["account_number"],
        })
    return out


def _coerce_accounts(rows):
    out = []
    for r in rows:
        out.append({
            "AccountID": r["account_id"],
            "Code": r["code"],
            "Name": r["name"],
            "Type": r["type"],
            "TaxType": r["tax_type"],
            "Status": r["status"],
            "Description": r["description"],
            "EnablePaymentsToAccount": strict_bool(r, "enable_payments_to_account"),
        })
    return out


def _coerce_invoices(rows):
    out = []
    for r in rows:
        out.append({
            "InvoiceID": r["invoice_id"],
            "InvoiceNumber": r["invoice_number"],
            "Type": r["type"],
            "contact_id": r["contact_id"],
            "contact_name": r["contact_name"],
            "Date": r["date"],
            "DueDate": r["due_date"],
            "Status": r["status"],
            "LineAmountTypes": r["line_amount_types"],
            "SubTotal": opt_float(r, "sub_total", default=None),
            "TotalTax": opt_float(r, "total_tax", default=None),
            "Total": opt_float(r, "total", default=None),
            "AmountDue": opt_float(r, "amount_due", default=None),
            "AmountPaid": opt_float(r, "amount_paid", default=None),
            "CurrencyCode": r["currency_code"],
            "Reference": r["reference"],
        })
    return out








# ---------------------------------------------------------------------------
# Serializers
# ---------------------------------------------------------------------------

def _serialize_contact(c):
    return {
        "ContactID": c["ContactID"],
        "Name": c["Name"],
        "FirstName": c["FirstName"],
        "LastName": c["LastName"],
        "EmailAddress": c["EmailAddress"],
        "IsCustomer": c["IsCustomer"],
        "IsSupplier": c["IsSupplier"],
        "ContactStatus": c["ContactStatus"],
        "AccountNumber": c["AccountNumber"],
    }


def _serialize_account(a):
    return dict(a)


def _serialize_invoice(inv):
    return {
        "InvoiceID": inv["InvoiceID"],
        "InvoiceNumber": inv["InvoiceNumber"],
        "Type": inv["Type"],
        "Contact": {"ContactID": inv["contact_id"], "Name": inv["contact_name"]},
        "Date": inv["Date"],
        "DueDate": inv["DueDate"],
        "Status": inv["Status"],
        "LineAmountTypes": inv["LineAmountTypes"],
        "SubTotal": inv["SubTotal"],
        "TotalTax": inv["TotalTax"],
        "Total": inv["Total"],
        "AmountDue": inv["AmountDue"],
        "AmountPaid": inv["AmountPaid"],
        "CurrencyCode": inv["CurrencyCode"],
        "Reference": inv["Reference"],
    }


# ---------------------------------------------------------------------------
# Invoices
# ---------------------------------------------------------------------------

def list_invoices(status=None, type_=None):
    invoices = list(_invoices_rows())
    if status:
        invoices = [i for i in invoices if i["Status"].upper() == status.upper()]
    if type_:
        invoices = [i for i in invoices if i["Type"].upper() == type_.upper()]
    return {"Invoices": [_serialize_invoice(i) for i in invoices]}


def get_invoice(invoice_id):
    for i in _invoices_rows():
        if i["InvoiceID"] == invoice_id or i["InvoiceNumber"] == invoice_id:
            return {"Invoices": [_serialize_invoice(i)]}
    return {"error": "invoice not found", "message": f"Invoice {invoice_id} not found"}


def create_invoice(contact_id, line_items=None, type_="ACCREC", date=None,
                   due_date=None, status="DRAFT", reference="",
                   currency_code="USD"):
    contact = next((c for c in _contacts_rows() if c["ContactID"] == contact_id), None)
    if not contact:
        return {"error": "contact not found", "message": f"Contact {contact_id} not found"}
    sub_total = 0.0
    for li in (line_items or []):
        qty = _to_float(li.get("Quantity", 1))
        unit = _to_float(li.get("UnitAmount", 0))
        sub_total += qty * unit
    sub_total = round(sub_total, 2)
    total_tax = round(sub_total * 0.10, 2)
    total = round(sub_total + total_tax, 2)
    existing = [i for i in _invoices_rows() if i["Type"] == "ACCREC"]
    next_num = 2047 + len([i for i in existing if i["InvoiceNumber"].startswith("INV-")])
    inv = {
        "InvoiceID": str(uuid.uuid4()),
        "InvoiceNumber": f"INV-{next_num}",
        "Type": type_ or "ACCREC",
        "contact_id": contact_id,
        "contact_name": contact["Name"],
        "Date": date or time.strftime("%Y-%m-%d", time.gmtime()),
        "DueDate": due_date or "",
        "Status": status or "DRAFT",
        "LineAmountTypes": "Exclusive",
        "SubTotal": sub_total,
        "TotalTax": total_tax,
        "Total": total,
        "AmountDue": total,
        "AmountPaid": 0.0,
        "CurrencyCode": currency_code or "USD",
        "Reference": reference or "",
    }
    _store_insert("invoices", inv)
    return {"Invoices": [_serialize_invoice(inv)]}


# ---------------------------------------------------------------------------
# Contacts
# ---------------------------------------------------------------------------

def list_contacts():
    return {"Contacts": [_serialize_contact(c) for c in _contacts_rows()]}


# ---------------------------------------------------------------------------
# Accounts
# ---------------------------------------------------------------------------

def list_accounts():
    return {"Accounts": [_serialize_account(a) for a in _accounts_rows()]}

_store.eager_load()
