"""Data access module for the Xero accounting mock service.

Mirrors a subset of the Xero Accounting API (api.xro/2.0): Invoices, Contacts,
and Accounts. Xero wraps collections under a PascalCase key, e.g.
{"Invoices": [...]}. Creating an invoice appends to an in-memory store that
resets on restart.
"""

import csv
import uuid
import time
from copy import deepcopy
from pathlib import Path

DATA_DIR = Path(__file__).parent


def _load(filename):
    with open(DATA_DIR / filename, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


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
            "IsCustomer": _to_bool(r["is_customer"]),
            "IsSupplier": _to_bool(r["is_supplier"]),
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
            "EnablePaymentsToAccount": _to_bool(r["enable_payments_to_account"]),
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
            "SubTotal": _to_float(r["sub_total"]),
            "TotalTax": _to_float(r["total_tax"]),
            "Total": _to_float(r["total"]),
            "AmountDue": _to_float(r["amount_due"]),
            "AmountPaid": _to_float(r["amount_paid"]),
            "CurrencyCode": r["currency_code"],
            "Reference": r["reference"],
        })
    return out


_contacts = _coerce_contacts(_load("contacts.csv"))
_accounts = _coerce_accounts(_load("accounts.csv"))
_invoices = _coerce_invoices(_load("invoices.csv"))

_contacts_store = deepcopy(_contacts)
_accounts_store = deepcopy(_accounts)
_invoices_store = deepcopy(_invoices)


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
    invoices = list(_invoices_store)
    if status:
        invoices = [i for i in invoices if i["Status"].upper() == status.upper()]
    if type_:
        invoices = [i for i in invoices if i["Type"].upper() == type_.upper()]
    return {"Invoices": [_serialize_invoice(i) for i in invoices]}


def get_invoice(invoice_id):
    for i in _invoices_store:
        if i["InvoiceID"] == invoice_id or i["InvoiceNumber"] == invoice_id:
            return {"Invoices": [_serialize_invoice(i)]}
    return {"error": "invoice not found", "message": f"Invoice {invoice_id} not found"}


def create_invoice(contact_id, line_items=None, type_="ACCREC", date=None,
                   due_date=None, status="DRAFT", reference="",
                   currency_code="USD"):
    contact = next((c for c in _contacts_store if c["ContactID"] == contact_id), None)
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
    existing = [i for i in _invoices_store if i["Type"] == "ACCREC"]
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
    _invoices_store.append(inv)
    return {"Invoices": [_serialize_invoice(inv)]}


# ---------------------------------------------------------------------------
# Contacts
# ---------------------------------------------------------------------------

def list_contacts():
    return {"Contacts": [_serialize_contact(c) for c in _contacts_store]}


# ---------------------------------------------------------------------------
# Accounts
# ---------------------------------------------------------------------------

def list_accounts():
    return {"Accounts": [_serialize_account(a) for a in _accounts_store]}
