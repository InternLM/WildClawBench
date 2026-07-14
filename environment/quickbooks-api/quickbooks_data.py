"""Data access module for QuickBooks Online API simulation."""

import csv
import json
import re
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).parent

import sys as _sys
_sys.path.insert(0, str(DATA_DIR.parent))
from _mutable_store import (
    read_seed_with_ctx, get_store, opt_str, strict_float)
_store = get_store("quickbooks-api")
_API = "quickbooks-api"

REALM_ID = "4620816365272861350"


def _load(filename, table):
    return read_seed_with_ctx(DATA_DIR / filename, _API, table)


def _strip_ctx(r):
    return {k: v for k, v in r.items() if not k.startswith("__")}


def _load_json(filename):
    with open(DATA_DIR / filename, encoding="utf-8") as f:
        return json.load(f)


def _load_qbo_envelope(filename, envelope_key):
    raw = _load_json(filename)
    if isinstance(raw, dict):
        qr = raw.get("QueryResponse")
        if isinstance(qr, dict) and envelope_key in qr:
            inner = qr[envelope_key]
            if isinstance(inner, list):
                return inner
    return raw


def _load_qbo_or_csv(filename, envelope_key, csv_coercer, table):
    csv_sibling = (DATA_DIR / filename).with_suffix(".csv")
    if csv_sibling.exists():
        return csv_coercer(_load(csv_sibling.name, table))
    return _load_qbo_envelope(filename, envelope_key)


def _now():
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S-00:00")


def _coerce_customers(rows):
    out = []
    for r in rows:
        out.append({
            "Id": r["Id"],
            "DisplayName": r["DisplayName"],
            "GivenName": opt_str(r, "GivenName", default="") or None,
            "FamilyName": opt_str(r, "FamilyName", default="") or None,
            "CompanyName": opt_str(r, "CompanyName", default="") or None,
            "PrimaryEmailAddr": {"Address": r["PrimaryEmailAddr"]} if r["PrimaryEmailAddr"] else None,
            "PrimaryPhone": {"FreeFormNumber": r["PrimaryPhone"]} if r["PrimaryPhone"] else None,
            "BillAddr": {
                "Line1": r["BillAddr_Line1"],
                "City": r["BillAddr_City"],
                "CountrySubDivisionCode": r["BillAddr_CountrySubDivisionCode"],
                "PostalCode": r["BillAddr_PostalCode"],
            },
            "Balance": strict_float(r, "Balance"),
            "Active": r["Active"].lower() == "true",
            "Job": r["Job"].lower() == "true",
            "Notes": opt_str(r, "Notes", default="") or None,
            "MetaData": {"CreateTime": _now(), "LastUpdatedTime": _now()},
            "SyncToken": "0",
        })
    return out


def _coerce_vendors(rows):
    out = []
    for r in rows:
        out.append({
            "Id": r["Id"],
            "DisplayName": r["DisplayName"],
            "CompanyName": opt_str(r, "CompanyName", default="") or None,
            "PrimaryEmailAddr": {"Address": r["PrimaryEmailAddr"]} if r["PrimaryEmailAddr"] else None,
            "PrimaryPhone": {"FreeFormNumber": r["PrimaryPhone"]} if r["PrimaryPhone"] else None,
            "BillAddr": {
                "Line1": r["BillAddr_Line1"],
                "City": r["BillAddr_City"],
                "CountrySubDivisionCode": r["BillAddr_CountrySubDivisionCode"],
                "PostalCode": r["BillAddr_PostalCode"],
            },
            "Balance": strict_float(r, "Balance"),
            "Active": r["Active"].lower() == "true",
            "AcctNum": opt_str(r, "AcctNum", default="") or None,
            "Vendor1099": r["Vendor1099"].lower() == "true",
            "MetaData": {"CreateTime": _now(), "LastUpdatedTime": _now()},
            "SyncToken": "0",
        })
    return out


def _coerce_items(rows):
    out = []
    for r in rows:
        out.append({
            "Id": r["Id"],
            "Name": r["Name"],
            "Description": opt_str(r, "Description", default="") or None,
            "Type": r["Type"],
            "UnitPrice": strict_float(r, "UnitPrice"),
            "IncomeAccountRef": {
                "value": r["IncomeAccountRef_value"],
                "name": r["IncomeAccountRef_name"],
            },
            "Active": r["Active"].lower() == "true",
            "Taxable": r["Taxable"].lower() == "true",
            "MetaData": {"CreateTime": _now(), "LastUpdatedTime": _now()},
            "SyncToken": "0",
        })
    return out


def _coerce_accounts(rows):
    out = []
    for r in rows:
        out.append({
            "Id": r["Id"],
            "Name": r["Name"],
            "AccountType": r["AccountType"],
            "AccountSubType": r["AccountSubType"],
            "CurrentBalance": strict_float(r, "CurrentBalance"),
            "Active": r["Active"].lower() == "true",
            "Classification": r["Classification"],
            "Description": opt_str(r, "Description", default="") or None,
            "MetaData": {"CreateTime": _now(), "LastUpdatedTime": _now()},
            "SyncToken": "0",
        })
    return out


_store.register("customers", primary_key="Id",
                initial_loader=lambda: _load_qbo_or_csv("customers.json", "Customer", _coerce_customers, "customers"))
_store.register("vendors", primary_key="Id",
                initial_loader=lambda: _load_qbo_or_csv("vendors.json", "Vendor", _coerce_vendors, "vendors"))
_store.register("items", primary_key="Id",
                initial_loader=lambda: _coerce_items(_load("items.json", "items")))
_store.register("accounts", primary_key="Id",
                initial_loader=lambda: _load_qbo_or_csv("accounts.json", "Account", _coerce_accounts, "accounts"))
_store.register("invoices", primary_key="Id",
                initial_loader=lambda: _load("invoices.json", "invoices"))
_store.register("bills", primary_key="Id",
                initial_loader=lambda: _load("bills.json", "bills"))
_store.register("payments", primary_key="Id",
                initial_loader=lambda: _load("payments.json", "payments"))
_store.register("estimates", primary_key="Id",
                initial_loader=lambda: _load("estimates.json", "estimates"))
_store.register("expenses", primary_key="Id",
                initial_loader=lambda: _load("expenses.json", "expenses"))

_store.register_document("company_info",
                         initial_loader=lambda: _load_json("company_info.json"))
_store.register_document("company_raw",
                         initial_loader=lambda: _load_json("company.json"))
_store.register_document("bill_payments",
                         initial_loader=lambda: _load_json("bill-payments.json"))
_store.register_document("corporate_expense_ledger",
                         initial_loader=lambda: _load_json("Corporate_Expense_Ledger.json"))
_store.register_document("reimbursement_policy",
                         initial_loader=lambda: _load_json("Reimbursement_Policy.json"))
_store.register_document("break_even_analysis",
                         initial_loader=lambda: _load_json("break-even-analysis.json"))


def _next_int_id(table_name: str) -> int:
    """Monotonic int counter for QBO-style IDs: scan current IDs and return max+1.

    Quickbooks uses bare integer IDs (as strings) rather than UUIDs; we must
    recompute the next id at every write so that drift-plane upserts (which can
    inject rows out of band) don't collide.
    """
    ids = []
    for row in _store.table(table_name).rows():
        try:
            ids.append(int(row.get("Id", "0")))
        except (TypeError, ValueError):
            continue
    return (max(ids) + 1) if ids else 1


def get_company_info():
    return {"CompanyInfo": _store.document("company_info").get()}


def get_company_raw():
    # company.json is already API-shaped ({"CompanyInfo": {...}}); served verbatim.
    return _store.document("company_raw").get()


def get_bill_payments():
    return _store.document("bill_payments").get()


def get_corporate_expense_ledger():
    return _store.document("corporate_expense_ledger").get()


def get_reimbursement_policy():
    return _store.document("reimbursement_policy").get()


def get_break_even_analysis():
    return _store.document("break_even_analysis").get()


def list_customers():
    return _store.table("customers").rows()


def get_customer(customer_id: str):
    c = _store.table("customers").get(customer_id)
    if c:
        return {"Customer": c}
    return {"error": f"Customer {customer_id} not found"}


def create_customer(data: dict):
    now = _now()
    new_id = str(_next_int_id("customers"))
    customer = {
        "Id": new_id,
        "DisplayName": data.get("DisplayName", ""),
        "GivenName": data.get("GivenName"),
        "FamilyName": data.get("FamilyName"),
        "CompanyName": data.get("CompanyName"),
        "PrimaryEmailAddr": data.get("PrimaryEmailAddr"),
        "PrimaryPhone": data.get("PrimaryPhone"),
        "BillAddr": data.get("BillAddr"),
        "Balance": 0.00,
        "Active": True,
        "Job": False,
        "Notes": data.get("Notes"),
        "MetaData": {"CreateTime": now, "LastUpdatedTime": now},
        "SyncToken": "0",
    }
    _store.table("customers").upsert(customer)
    return {"Customer": customer}


def update_customer(customer_id: str, data: dict):
    c = _store.table("customers").get(customer_id)
    if not c:
        return {"error": f"Customer {customer_id} not found"}
    updatable = {"DisplayName", "GivenName", "FamilyName", "CompanyName",
                 "PrimaryEmailAddr", "PrimaryPhone", "BillAddr", "Active", "Notes"}
    patch = {k: v for k, v in data.items() if k in updatable}
    existing_meta = c.get("MetaData") or {}
    meta = dict(existing_meta) if isinstance(existing_meta, dict) else {}
    meta.setdefault("CreateTime", _now())
    meta["LastUpdatedTime"] = _now()
    patch["MetaData"] = meta
    try:
        current_sync = int(c.get("SyncToken") or 0)
    except (TypeError, ValueError):
        current_sync = 0
    patch["SyncToken"] = str(current_sync + 1)
    _store.table("customers").patch(customer_id, patch)
    return {"Customer": _store.table("customers").get(customer_id)}


def list_vendors():
    return _store.table("vendors").rows()


def get_vendor(vendor_id: str):
    v = _store.table("vendors").get(vendor_id)
    if v:
        return {"Vendor": v}
    return {"error": f"Vendor {vendor_id} not found"}


def create_vendor(data: dict):
    now = _now()
    new_id = str(_next_int_id("vendors"))
    vendor = {
        "Id": new_id,
        "DisplayName": data.get("DisplayName", ""),
        "CompanyName": data.get("CompanyName"),
        "PrimaryEmailAddr": data.get("PrimaryEmailAddr"),
        "PrimaryPhone": data.get("PrimaryPhone"),
        "BillAddr": data.get("BillAddr"),
        "Balance": 0.00,
        "Active": True,
        "AcctNum": data.get("AcctNum"),
        "Vendor1099": data.get("Vendor1099", False),
        "MetaData": {"CreateTime": now, "LastUpdatedTime": now},
        "SyncToken": "0",
    }
    _store.table("vendors").upsert(vendor)
    return {"Vendor": vendor}


def update_vendor(vendor_id: str, data: dict):
    v = _store.table("vendors").get(vendor_id)
    if not v:
        return {"error": f"Vendor {vendor_id} not found"}
    updatable = {"DisplayName", "CompanyName", "PrimaryEmailAddr",
                 "PrimaryPhone", "BillAddr", "Active", "AcctNum", "Vendor1099"}
    patch = {k: val for k, val in data.items() if k in updatable}
    existing_meta = v.get("MetaData") or {}
    meta = dict(existing_meta) if isinstance(existing_meta, dict) else {}
    meta.setdefault("CreateTime", _now())
    meta["LastUpdatedTime"] = _now()
    patch["MetaData"] = meta
    try:
        current_sync = int(v.get("SyncToken") or 0)
    except (TypeError, ValueError):
        current_sync = 0
    patch["SyncToken"] = str(current_sync + 1)
    _store.table("vendors").patch(vendor_id, patch)
    return {"Vendor": _store.table("vendors").get(vendor_id)}


def list_items():
    return _store.table("items").rows()


def get_item(item_id: str):
    it = _store.table("items").get(item_id)
    if it:
        return {"Item": it}
    return {"error": f"Item {item_id} not found"}


def create_item(data: dict):
    now = _now()
    new_id = str(_next_int_id("items"))
    item = {
        "Id": new_id,
        "Name": data.get("Name", ""),
        "Description": data.get("Description"),
        "Type": data.get("Type", "Service"),
        "UnitPrice": float(data.get("UnitPrice") or 0),
        "IncomeAccountRef": data.get("IncomeAccountRef", {"value": "1", "name": "Landscaping Services Revenue"}),
        "Active": True,
        "Taxable": data.get("Taxable", False),
        "MetaData": {"CreateTime": now, "LastUpdatedTime": now},
        "SyncToken": "0",
    }
    _store.table("items").upsert(item)
    return {"Item": item}


def update_item(item_id: str, data: dict):
    it = _store.table("items").get(item_id)
    if not it:
        return {"error": f"Item {item_id} not found"}
    updatable = {"Name", "Description", "UnitPrice", "Active", "Taxable", "IncomeAccountRef"}
    patch = {}
    for k, v in data.items():
        if k in updatable:
            patch[k] = float(v) if k == "UnitPrice" else v
    meta = dict(it["MetaData"]); meta["LastUpdatedTime"] = _now()
    patch["MetaData"] = meta
    patch["SyncToken"] = str(int(it["SyncToken"]) + 1)
    _store.table("items").patch(item_id, patch)
    return {"Item": _store.table("items").get(item_id)}


def list_accounts():
    return _store.table("accounts").rows()


def get_account(account_id: str):
    a = _store.table("accounts").get(account_id)
    if a:
        return {"Account": a}
    return {"error": f"Account {account_id} not found"}


def list_invoices():
    return _store.table("invoices").rows()


def get_invoice(invoice_id: str):
    inv = _store.table("invoices").get(invoice_id)
    if inv:
        return {"Invoice": inv}
    return {"error": f"Invoice {invoice_id} not found"}


def create_invoice(data: dict):
    now = _now()
    new_id = str(_next_int_id("invoices"))
    lines = list(data.get("Line") or [])
    total = sum(l.get("Amount", 0) for l in lines if l.get("DetailType") != "SubTotalLineDetail")
    lines.append({"Amount": total, "DetailType": "SubTotalLineDetail", "SubTotalLineDetail": {}})

    invoice = {
        "Id": new_id,
        "DocNumber": new_id,
        "TxnDate": data.get("TxnDate", _now()[:10]),
        "DueDate": data.get("DueDate", _now()[:10]),
        "CustomerRef": data.get("CustomerRef", {}),
        "Line": lines,
        "TotalAmt": total,
        "Balance": total,
        "PrintStatus": "NotSet",
        "EmailStatus": "NotSet",
        "BillEmail": data.get("BillEmail"),
        "Status": "Open",
        "MetaData": {"CreateTime": now, "LastUpdatedTime": now},
        "SyncToken": "0",
    }
    _store.table("invoices").upsert(invoice)
    return {"Invoice": invoice}


def update_invoice(invoice_id: str, data: dict):
    inv = _store.table("invoices").get(invoice_id)
    if not inv:
        return {"error": f"Invoice {invoice_id} not found"}
    updatable = {"DueDate", "CustomerRef", "Line", "BillEmail", "PrintStatus", "EmailStatus"}
    patch = {k: v for k, v in data.items() if k in updatable}
    if "Line" in data:
        lines = data["Line"]
        total = sum(l.get("Amount", 0) for l in lines if l.get("DetailType") != "SubTotalLineDetail")
        patch["TotalAmt"] = total
        patch["Balance"] = total
    existing_meta = inv.get("MetaData") or {}
    meta = dict(existing_meta) if isinstance(existing_meta, dict) else {}
    meta.setdefault("CreateTime", _now())
    meta["LastUpdatedTime"] = _now()
    patch["MetaData"] = meta
    try:
        current_sync = int(inv.get("SyncToken") or 0)
    except (TypeError, ValueError):
        current_sync = 0
    patch["SyncToken"] = str(current_sync + 1)
    _store.table("invoices").patch(invoice_id, patch)
    return {"Invoice": _store.table("invoices").get(invoice_id)}


def void_invoice(invoice_id: str):
    inv = _store.table("invoices").get(invoice_id)
    if not inv:
        return {"error": f"Invoice {invoice_id} not found"}
    existing_meta = inv.get("MetaData") or {}
    meta = dict(existing_meta) if isinstance(existing_meta, dict) else {}
    meta.setdefault("CreateTime", _now())
    meta["LastUpdatedTime"] = _now()
    try:
        current_sync = int(inv.get("SyncToken") or 0)
    except (TypeError, ValueError):
        current_sync = 0
    _store.table("invoices").patch(invoice_id, {
        "Status": "Voided",
        "Balance": 0.00,
        "MetaData": meta,
        "SyncToken": str(current_sync + 1),
    })
    return {"Invoice": _store.table("invoices").get(invoice_id)}


def send_invoice(invoice_id: str):
    inv = _store.table("invoices").get(invoice_id)
    if not inv:
        return {"error": f"Invoice {invoice_id} not found"}
    existing_meta = inv.get("MetaData") or {}
    meta = dict(existing_meta) if isinstance(existing_meta, dict) else {}
    meta.setdefault("CreateTime", _now())
    meta["LastUpdatedTime"] = _now()
    _store.table("invoices").patch(invoice_id, {
        "EmailStatus": "Sent",
        "MetaData": meta,
    })
    return {"Invoice": _store.table("invoices").get(invoice_id)}


def get_invoice_pdf(invoice_id: str):
    inv = _store.table("invoices").get(invoice_id)
    if inv:
        return {"url": f"https://quickbooks.api.intuit.com/v3/company/{REALM_ID}/invoice/{invoice_id}/pdf"}
    return {"error": f"Invoice {invoice_id} not found"}


def list_bills():
    return _store.table("bills").rows()


def get_bill(bill_id: str):
    b = _store.table("bills").get(bill_id)
    if b:
        return {"Bill": b}
    return {"error": f"Bill {bill_id} not found"}


def create_bill(data: dict):
    now = _now()
    new_id = str(_next_int_id("bills"))
    lines = data.get("Line", [])
    total = sum(l.get("Amount", 0) for l in lines)

    bill = {
        "Id": new_id,
        "VendorRef": data.get("VendorRef", {}),
        "TxnDate": data.get("TxnDate", _now()[:10]),
        "DueDate": data.get("DueDate", _now()[:10]),
        "TotalAmt": total,
        "Balance": total,
        "Line": lines,
        "Status": "Open",
        "DocNumber": data.get("DocNumber", f"BILL-{new_id}"),
        "MetaData": {"CreateTime": now, "LastUpdatedTime": now},
        "SyncToken": "0",
    }
    _store.table("bills").upsert(bill)
    return {"Bill": bill}


def pay_bill(bill_id: str):
    b = _store.table("bills").get(bill_id)
    if not b:
        return {"error": f"Bill {bill_id} not found"}
    existing_meta = b.get("MetaData") or {}
    meta = dict(existing_meta) if isinstance(existing_meta, dict) else {}
    meta.setdefault("CreateTime", _now())
    meta["LastUpdatedTime"] = _now()
    try:
        current_sync = int(b.get("SyncToken") or 0)
    except (TypeError, ValueError):
        current_sync = 0
    _store.table("bills").patch(bill_id, {
        "Balance": 0.00,
        "Status": "Paid",
        "MetaData": meta,
        "SyncToken": str(current_sync + 1),
    })
    return {"Bill": _store.table("bills").get(bill_id)}


def list_payments():
    return _store.table("payments").rows()


def get_payment(payment_id: str):
    p = _store.table("payments").get(payment_id)
    if p:
        return {"Payment": p}
    return {"error": f"Payment {payment_id} not found"}


def create_payment(data: dict):
    now = _now()
    new_id = str(_next_int_id("payments"))
    total = float(data.get("TotalAmt", 0))

    payment = {
        "Id": new_id,
        "TxnDate": data.get("TxnDate", _now()[:10]),
        "CustomerRef": data.get("CustomerRef", {}),
        "TotalAmt": total,
        "Line": data.get("Line", []),
        "MetaData": {"CreateTime": now, "LastUpdatedTime": now},
        "SyncToken": "0",
    }
    _store.table("payments").upsert(payment)

    for line in payment.get("Line", []):
        for linked in line.get("LinkedTxn", []):
            if linked.get("TxnType") == "Invoice":
                inv_id = linked.get("TxnId")
                inv = _store.table("invoices").get(inv_id)
                if not inv:
                    continue
                new_balance = max(0, inv["Balance"] - line.get("Amount", 0))
                patch = {"Balance": new_balance}
                if new_balance == 0:
                    patch["Status"] = "Paid"
                _store.table("invoices").patch(inv_id, patch)

    return {"Payment": payment}


def list_estimates():
    return _store.table("estimates").rows()


def get_estimate(estimate_id: str):
    e = _store.table("estimates").get(estimate_id)
    if e:
        return {"Estimate": e}
    return {"error": f"Estimate {estimate_id} not found"}


def create_estimate(data: dict):
    now = _now()
    new_id = str(_next_int_id("estimates"))
    lines = data.get("Line", [])
    total = sum(l.get("Amount", 0) for l in lines)

    estimate = {
        "Id": new_id,
        "DocNumber": f"E-{new_id}",
        "TxnDate": data.get("TxnDate", _now()[:10]),
        "ExpirationDate": data.get("ExpirationDate"),
        "CustomerRef": data.get("CustomerRef", {}),
        "Line": lines,
        "TotalAmt": total,
        "TxnStatus": "Pending",
        "AcceptedDate": None,
        "LinkedTxn": [],
        "MetaData": {"CreateTime": now, "LastUpdatedTime": now},
        "SyncToken": "0",
    }
    _store.table("estimates").upsert(estimate)
    return {"Estimate": estimate}


def convert_estimate_to_invoice(estimate_id: str):
    e = _store.table("estimates").get(estimate_id)
    if not e:
        return {"error": f"Estimate {estimate_id} not found"}
    if e["TxnStatus"] not in ("Pending", "Accepted"):
        return {"error": f"Estimate {estimate_id} cannot be converted (status: {e['TxnStatus']})"}

    now = _now()
    lines = [l for l in e["Line"] if l.get("DetailType") == "SalesItemLineDetail"]
    total = sum(l.get("Amount", 0) for l in lines)
    lines.append({"Amount": total, "DetailType": "SubTotalLineDetail", "SubTotalLineDetail": {}})

    new_inv_id = str(_next_int_id("invoices"))
    invoice = {
        "Id": new_inv_id,
        "DocNumber": new_inv_id,
        "TxnDate": _now()[:10],
        "DueDate": _now()[:10],
        "CustomerRef": e["CustomerRef"],
        "Line": lines,
        "TotalAmt": total,
        "Balance": total,
        "PrintStatus": "NotSet",
        "EmailStatus": "NotSet",
        "BillEmail": None,
        "Status": "Open",
        "MetaData": {"CreateTime": now, "LastUpdatedTime": now},
        "SyncToken": "0",
    }
    _store.table("invoices").upsert(invoice)

    meta = dict(e["MetaData"]); meta["LastUpdatedTime"] = now
    _store.table("estimates").patch(estimate_id, {
        "TxnStatus": "Accepted",
        "AcceptedDate": _now()[:10],
        "LinkedTxn": [{"TxnId": new_inv_id, "TxnType": "Invoice"}],
        "MetaData": meta,
        "SyncToken": str(int(e["SyncToken"]) + 1),
    })

    return {"Invoice": invoice}


def list_expenses():
    return _store.table("expenses").rows()


def get_expense(expense_id: str):
    e = _store.table("expenses").get(expense_id)
    if e:
        return {"Purchase": e}
    return {"error": f"Expense {expense_id} not found"}


def create_expense(data: dict):
    now = _now()
    new_id = str(_next_int_id("expenses"))
    lines = data.get("Line", [])
    total = sum(l.get("Amount", 0) for l in lines)

    expense = {
        "Id": new_id,
        "TxnDate": data.get("TxnDate", _now()[:10]),
        "AccountRef": data.get("AccountRef", {}),
        "PaymentType": data.get("PaymentType", "CreditCard"),
        "TotalAmt": total,
        "Line": lines,
        "MetaData": {"CreateTime": now, "LastUpdatedTime": now},
        "SyncToken": "0",
    }
    _store.table("expenses").upsert(expense)
    return {"Purchase": expense}


def execute_query(query_str: str):
    """Parse simplified QuickBooks query: SELECT * FROM EntityName [WHERE field op 'value']"""
    query_str = query_str.strip()

    parts = query_str.upper().split()
    if len(parts) < 4 or parts[0] != "SELECT" or parts[2] != "FROM":
        return {"error": f"Invalid query syntax: {query_str}"}

    entity = query_str.split("FROM")[1].strip().split()[0].strip()

    entity_map = {
        "Invoice": "invoices",
        "Customer": "customers",
        "Vendor": "vendors",
        "Item": "items",
        "Account": "accounts",
        "Bill": "bills",
        "Payment": "payments",
        "Estimate": "estimates",
        "Purchase": "expenses",
    }

    if entity not in entity_map:
        return {"error": f"Unknown entity: {entity}"}

    results = _store.table(entity_map[entity]).rows()

    upper_query = query_str.upper()
    if "WHERE" in upper_query:
        where_idx = upper_query.index("WHERE") + 5
        where_clause = query_str[where_idx:].strip()
        results = _apply_where(results, where_clause)

    return {
        "QueryResponse": {
            entity: results,
            "startPosition": 1,
            "maxResults": len(results),
            "totalCount": len(results),
        }
    }


def _apply_where(results, where_clause):
    conditions = re.split(r'\s+AND\s+', where_clause, flags=re.IGNORECASE)

    for cond in conditions:
        cond = cond.strip()
        match = re.match(r"(\w+)\s*(=|!=|>|<|>=|<=|LIKE)\s*'?([^']*)'?", cond, re.IGNORECASE)
        if not match:
            continue

        field = match.group(1)
        op = match.group(2).upper()
        value = match.group(3)

        filtered = []
        for item in results:
            item_val = _get_nested_field(item, field)
            if item_val is None:
                continue
            if _compare(item_val, op, value):
                filtered.append(item)
        results = filtered

    return results


def _get_nested_field(item, field):
    if field in item:
        return item[field]
    if field + "Ref" in item:
        ref = item[field + "Ref"]
        if isinstance(ref, dict):
            return ref.get("value")
    parts = field.split(".")
    current = item
    for p in parts:
        if isinstance(current, dict) and p in current:
            current = current[p]
        else:
            return None
    return current


def _compare(item_val, op, value):
    if isinstance(item_val, bool):
        bool_val = value.lower() in ("true", "1", "yes")
        if op == "=":
            return item_val == bool_val
        elif op == "!=":
            return item_val != bool_val
        return False

    try:
        num_item = float(item_val) if not isinstance(item_val, (int, float)) else item_val
        num_val = float(value)
        if op == "=":
            return num_item == num_val
        elif op == "!=":
            return num_item != num_val
        elif op == ">":
            return num_item > num_val
        elif op == "<":
            return num_item < num_val
        elif op == ">=":
            return num_item >= num_val
        elif op == "<=":
            return num_item <= num_val
    except (ValueError, TypeError):
        pass

    str_item = str(item_val)
    if op == "=":
        return str_item.lower() == value.lower()
    elif op == "!=":
        return str_item.lower() != value.lower()
    elif op == "LIKE":
        pattern = value.replace("%", ".*")
        return bool(re.match(pattern, str_item, re.IGNORECASE))

    return False


def profit_and_loss(start_date: str = None, end_date: str = None):
    revenue_invoices = _store.table("invoices").rows()
    expense_bills = _store.table("bills").rows()
    expense_purchases = _store.table("expenses").rows()

    if start_date:
        revenue_invoices = [inv for inv in revenue_invoices if (inv.get("TxnDate") or "") >= start_date]
        expense_bills = [b for b in expense_bills if (b.get("TxnDate") or "") >= start_date]
        expense_purchases = [e for e in expense_purchases if (e.get("TxnDate") or "") >= start_date]
    if end_date:
        revenue_invoices = [inv for inv in revenue_invoices if (inv.get("TxnDate") or "") <= end_date]
        expense_bills = [b for b in expense_bills if (b.get("TxnDate") or "") <= end_date]
        expense_purchases = [e for e in expense_purchases if (e.get("TxnDate") or "") <= end_date]

    paid_invoices = [inv for inv in revenue_invoices if inv.get("Status") == "Paid"]
    total_revenue = sum(inv.get("TotalAmt", 0) for inv in paid_invoices)
    total_bill_expenses = sum(b.get("TotalAmt", 0) for b in expense_bills)
    total_purchase_expenses = sum(e.get("TotalAmt", 0) for e in expense_purchases)
    total_expenses = total_bill_expenses + total_purchase_expenses
    net_income = total_revenue - total_expenses

    return {
        "Header": {
            "ReportName": "ProfitAndLoss",
            "StartPeriod": start_date or "2025-01-01",
            "EndPeriod": end_date or "2025-12-31",
            "Currency": "USD",
            "Option": [{"Name": "AccountingMethod", "Value": "Accrual"}],
        },
        "Rows": {
            "Row": [
                {"group": "Income", "Summary": {"ColData": [{"value": "Total Income"}, {"value": f"{total_revenue:.2f}"}]},
                 "Rows": {"Row": [{"ColData": [{"value": "Landscaping Services Revenue"}, {"value": f"{total_revenue:.2f}"}]}]}},
                {"group": "Expenses", "Summary": {"ColData": [{"value": "Total Expenses"}, {"value": f"{total_expenses:.2f}"}]},
                 "Rows": {"Row": _build_expense_rows(expense_bills, expense_purchases)}},
                {"group": "NetIncome", "Summary": {"ColData": [{"value": "Net Income"}, {"value": f"{net_income:.2f}"}]}},
            ]
        },
    }


def _build_expense_rows(bills, purchases):
    account_totals = {}
    for b in bills:
        for line in b.get("Line", []):
            detail = line.get("AccountBasedExpenseLineDetail", {})
            acct = detail.get("AccountRef", {}).get("name", "Other Expense")
            account_totals[acct] = account_totals.get(acct, 0) + line.get("Amount", 0)
    for p in purchases:
        for line in p.get("Line", []):
            detail = line.get("AccountBasedExpenseLineDetail", {})
            acct = detail.get("AccountRef", {}).get("name", "Other Expense")
            account_totals[acct] = account_totals.get(acct, 0) + line.get("Amount", 0)

    rows = []
    for acct_name, total in sorted(account_totals.items()):
        rows.append({"ColData": [{"value": acct_name}, {"value": f"{total:.2f}"}]})
    return rows


def balance_sheet(start_date: str = None, end_date: str = None):
    invoices = _store.table("invoices").rows()
    bills = _store.table("bills").rows()
    total_ar = sum(inv.get("Balance", 0) for inv in invoices if inv.get("Status") not in ("Voided",))
    total_ap = sum(b.get("Balance", 0) for b in bills)

    checking = 47250.00
    savings = 15000.00
    total_assets = checking + savings + total_ar
    total_liabilities = total_ap
    equity = total_assets - total_liabilities

    return {
        "Header": {
            "ReportName": "BalanceSheet",
            "StartPeriod": start_date or "2025-01-01",
            "EndPeriod": end_date or "2025-12-31",
            "Currency": "USD",
        },
        "Rows": {
            "Row": [
                {"group": "Assets", "Summary": {"ColData": [{"value": "Total Assets"}, {"value": f"{total_assets:.2f}"}]},
                 "Rows": {"Row": [
                     {"ColData": [{"value": "Business Checking"}, {"value": f"{checking:.2f}"}]},
                     {"ColData": [{"value": "Business Savings"}, {"value": f"{savings:.2f}"}]},
                     {"ColData": [{"value": "Accounts Receivable"}, {"value": f"{total_ar:.2f}"}]},
                 ]}},
                {"group": "Liabilities", "Summary": {"ColData": [{"value": "Total Liabilities"}, {"value": f"{total_liabilities:.2f}"}]},
                 "Rows": {"Row": [
                     {"ColData": [{"value": "Accounts Payable"}, {"value": f"{total_ap:.2f}"}]},
                 ]}},
                {"group": "Equity", "Summary": {"ColData": [{"value": "Total Equity"}, {"value": f"{equity:.2f}"}]}},
            ]
        },
    }


def accounts_receivable_aging():
    aging_buckets = {"Current": [], "1-30": [], "31-60": [], "61-90": [], "91+": []}
    today = datetime.utcnow().strftime("%Y-%m-%d")

    for inv in _store.table("invoices").rows():
        if inv.get("Balance", 0) <= 0 or inv.get("Status") == "Voided":
            continue
        due_date = inv.get("DueDate", today)
        days_overdue = (datetime.strptime(today, "%Y-%m-%d") - datetime.strptime(due_date, "%Y-%m-%d")).days
        if days_overdue <= 0:
            aging_buckets["Current"].append(inv)
        elif days_overdue <= 30:
            aging_buckets["1-30"].append(inv)
        elif days_overdue <= 60:
            aging_buckets["31-60"].append(inv)
        elif days_overdue <= 90:
            aging_buckets["61-90"].append(inv)
        else:
            aging_buckets["91+"].append(inv)

    rows = []
    for bucket, invoices in aging_buckets.items():
        total = sum(inv.get("Balance", 0) for inv in invoices)
        rows.append({
            "ColData": [{"value": bucket}, {"value": f"{total:.2f}"}],
            "Details": [{"CustomerRef": inv.get("CustomerRef"), "Balance": inv.get("Balance"), "DueDate": inv.get("DueDate")} for inv in invoices],
        })

    return {
        "Header": {
            "ReportName": "AgedReceivableDetail",
            "ReportBasis": "Accrual",
            "Currency": "USD",
        },
        "Rows": {"Row": rows},
    }


def accounts_payable_aging():
    aging_buckets = {"Current": [], "1-30": [], "31-60": [], "61-90": [], "91+": []}
    today = datetime.utcnow().strftime("%Y-%m-%d")

    for bill in _store.table("bills").rows():
        if bill.get("Balance", 0) <= 0:
            continue
        due_date = bill.get("DueDate", today)
        days_overdue = (datetime.strptime(today, "%Y-%m-%d") - datetime.strptime(due_date, "%Y-%m-%d")).days
        if days_overdue <= 0:
            aging_buckets["Current"].append(bill)
        elif days_overdue <= 30:
            aging_buckets["1-30"].append(bill)
        elif days_overdue <= 60:
            aging_buckets["31-60"].append(bill)
        elif days_overdue <= 90:
            aging_buckets["61-90"].append(bill)
        else:
            aging_buckets["91+"].append(bill)

    rows = []
    for bucket, bills in aging_buckets.items():
        total = sum(b.get("Balance", 0) for b in bills)
        rows.append({
            "ColData": [{"value": bucket}, {"value": f"{total:.2f}"}],
            "Details": [{"VendorRef": b.get("VendorRef"), "Balance": b.get("Balance"), "DueDate": b.get("DueDate")} for b in bills],
        })

    return {
        "Header": {
            "ReportName": "AgedPayableDetail",
            "ReportBasis": "Accrual",
            "Currency": "USD",
        },
        "Rows": {"Row": rows},
    }

_store.eager_load()
