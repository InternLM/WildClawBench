"""Data access module for QuickBooks Online API simulation."""

import csv
import json
from copy import deepcopy
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).parent

REALM_ID = "4620816365272861350"


def _load(filename):
    with open(DATA_DIR / filename, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _load_json(filename):
    with open(DATA_DIR / filename, encoding="utf-8") as f:
        return json.load(f)


def _now():
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S-00:00")


# ---------------------------------------------------------------------------
# Load and coerce data
# ---------------------------------------------------------------------------

def _coerce_customers(rows):
    out = []
    for r in rows:
        out.append({
            "Id": r["Id"],
            "DisplayName": r["DisplayName"],
            "GivenName": r["GivenName"] if r["GivenName"] else None,
            "FamilyName": r["FamilyName"] if r["FamilyName"] else None,
            "CompanyName": r["CompanyName"] if r["CompanyName"] else None,
            "PrimaryEmailAddr": {"Address": r["PrimaryEmailAddr"]} if r["PrimaryEmailAddr"] else None,
            "PrimaryPhone": {"FreeFormNumber": r["PrimaryPhone"]} if r["PrimaryPhone"] else None,
            "BillAddr": {
                "Line1": r["BillAddr_Line1"],
                "City": r["BillAddr_City"],
                "CountrySubDivisionCode": r["BillAddr_CountrySubDivisionCode"],
                "PostalCode": r["BillAddr_PostalCode"],
            },
            "Balance": float(r["Balance"]),
            "Active": r["Active"].lower() == "true",
            "Job": r["Job"].lower() == "true",
            "Notes": r["Notes"] if r["Notes"] else None,
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
            "CompanyName": r["CompanyName"] if r["CompanyName"] else None,
            "PrimaryEmailAddr": {"Address": r["PrimaryEmailAddr"]} if r["PrimaryEmailAddr"] else None,
            "PrimaryPhone": {"FreeFormNumber": r["PrimaryPhone"]} if r["PrimaryPhone"] else None,
            "BillAddr": {
                "Line1": r["BillAddr_Line1"],
                "City": r["BillAddr_City"],
                "CountrySubDivisionCode": r["BillAddr_CountrySubDivisionCode"],
                "PostalCode": r["BillAddr_PostalCode"],
            },
            "Balance": float(r["Balance"]),
            "Active": r["Active"].lower() == "true",
            "AcctNum": r["AcctNum"] if r["AcctNum"] else None,
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
            "Description": r["Description"] if r["Description"] else None,
            "Type": r["Type"],
            "UnitPrice": float(r["UnitPrice"]),
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
            "CurrentBalance": float(r["CurrentBalance"]),
            "Active": r["Active"].lower() == "true",
            "Classification": r["Classification"],
            "Description": r["Description"] if r["Description"] else None,
            "MetaData": {"CreateTime": _now(), "LastUpdatedTime": _now()},
            "SyncToken": "0",
        })
    return out


# Load all data at module init
_customers = _coerce_customers(_load("customers.csv"))
_vendors = _coerce_vendors(_load("vendors.csv"))
_items = _coerce_items(_load("items.csv"))
_accounts = _coerce_accounts(_load("accounts.csv"))
_invoices = _load_json("invoices.json")
_bills = _load_json("bills.json")
_payments = _load_json("payments.json")
_estimates = _load_json("estimates.json")
_expenses = _load_json("expenses.json")
_company_info = _load_json("company_info.json")

# Mutable in-memory stores
_customers_store = deepcopy(_customers)
_vendors_store = deepcopy(_vendors)
_items_store = deepcopy(_items)
_accounts_store = deepcopy(_accounts)
_invoices_store = deepcopy(_invoices)
_bills_store = deepcopy(_bills)
_payments_store = deepcopy(_payments)
_estimates_store = deepcopy(_estimates)
_expenses_store = deepcopy(_expenses)
_company_info_store = deepcopy(_company_info)

_next_customer_id = max(int(c["Id"]) for c in _customers_store) + 1
_next_vendor_id = max(int(v["Id"]) for v in _vendors_store) + 1
_next_item_id = max(int(i["Id"]) for i in _items_store) + 1
_next_invoice_id = max(int(inv["Id"]) for inv in _invoices_store) + 1
_next_bill_id = max(int(b["Id"]) for b in _bills_store) + 1
_next_payment_id = max(int(p["Id"]) for p in _payments_store) + 1
_next_estimate_id = max(int(e["Id"]) for e in _estimates_store) + 1
_next_expense_id = max(int(e["Id"]) for e in _expenses_store) + 1


# ---------------------------------------------------------------------------
# Company Info
# ---------------------------------------------------------------------------

def get_company_info():
    return {"CompanyInfo": _company_info_store}


# ---------------------------------------------------------------------------
# Customers
# ---------------------------------------------------------------------------

def list_customers():
    return _customers_store


def get_customer(customer_id: str):
    for c in _customers_store:
        if c["Id"] == customer_id:
            return {"Customer": c}
    return {"error": f"Customer {customer_id} not found"}


def create_customer(data: dict):
    global _next_customer_id
    now = _now()
    customer = {
        "Id": str(_next_customer_id),
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
    _customers_store.append(customer)
    _next_customer_id += 1
    return {"Customer": customer}


def update_customer(customer_id: str, data: dict):
    for i, c in enumerate(_customers_store):
        if c["Id"] == customer_id:
            updatable = {"DisplayName", "GivenName", "FamilyName", "CompanyName",
                         "PrimaryEmailAddr", "PrimaryPhone", "BillAddr", "Active", "Notes"}
            for k, v in data.items():
                if k in updatable:
                    _customers_store[i][k] = v
            _customers_store[i]["MetaData"]["LastUpdatedTime"] = _now()
            _customers_store[i]["SyncToken"] = str(int(_customers_store[i]["SyncToken"]) + 1)
            return {"Customer": _customers_store[i]}
    return {"error": f"Customer {customer_id} not found"}


# ---------------------------------------------------------------------------
# Vendors
# ---------------------------------------------------------------------------

def list_vendors():
    return _vendors_store


def get_vendor(vendor_id: str):
    for v in _vendors_store:
        if v["Id"] == vendor_id:
            return {"Vendor": v}
    return {"error": f"Vendor {vendor_id} not found"}


def create_vendor(data: dict):
    global _next_vendor_id
    now = _now()
    vendor = {
        "Id": str(_next_vendor_id),
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
    _vendors_store.append(vendor)
    _next_vendor_id += 1
    return {"Vendor": vendor}


def update_vendor(vendor_id: str, data: dict):
    for i, v in enumerate(_vendors_store):
        if v["Id"] == vendor_id:
            updatable = {"DisplayName", "CompanyName", "PrimaryEmailAddr",
                         "PrimaryPhone", "BillAddr", "Active", "AcctNum", "Vendor1099"}
            for k, val in data.items():
                if k in updatable:
                    _vendors_store[i][k] = val
            _vendors_store[i]["MetaData"]["LastUpdatedTime"] = _now()
            _vendors_store[i]["SyncToken"] = str(int(_vendors_store[i]["SyncToken"]) + 1)
            return {"Vendor": _vendors_store[i]}
    return {"error": f"Vendor {vendor_id} not found"}


# ---------------------------------------------------------------------------
# Items
# ---------------------------------------------------------------------------

def list_items():
    return _items_store


def get_item(item_id: str):
    for item in _items_store:
        if item["Id"] == item_id:
            return {"Item": item}
    return {"error": f"Item {item_id} not found"}


def create_item(data: dict):
    global _next_item_id
    now = _now()
    item = {
        "Id": str(_next_item_id),
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
    _items_store.append(item)
    _next_item_id += 1
    return {"Item": item}


def update_item(item_id: str, data: dict):
    for i, item in enumerate(_items_store):
        if item["Id"] == item_id:
            updatable = {"Name", "Description", "UnitPrice", "Active", "Taxable", "IncomeAccountRef"}
            for k, v in data.items():
                if k in updatable:
                    if k == "UnitPrice":
                        _items_store[i][k] = float(v)
                    else:
                        _items_store[i][k] = v
            _items_store[i]["MetaData"]["LastUpdatedTime"] = _now()
            _items_store[i]["SyncToken"] = str(int(_items_store[i]["SyncToken"]) + 1)
            return {"Item": _items_store[i]}
    return {"error": f"Item {item_id} not found"}


# ---------------------------------------------------------------------------
# Accounts
# ---------------------------------------------------------------------------

def list_accounts():
    return _accounts_store


def get_account(account_id: str):
    for a in _accounts_store:
        if a["Id"] == account_id:
            return {"Account": a}
    return {"error": f"Account {account_id} not found"}


# ---------------------------------------------------------------------------
# Invoices
# ---------------------------------------------------------------------------

def list_invoices():
    return _invoices_store


def get_invoice(invoice_id: str):
    for inv in _invoices_store:
        if inv["Id"] == invoice_id:
            return {"Invoice": inv}
    return {"error": f"Invoice {invoice_id} not found"}


def create_invoice(data: dict):
    global _next_invoice_id
    now = _now()
    lines = list(data.get("Line") or [])
    total = sum(l.get("Amount", 0) for l in lines if l.get("DetailType") != "SubTotalLineDetail")
    lines.append({"Amount": total, "DetailType": "SubTotalLineDetail", "SubTotalLineDetail": {}})

    invoice = {
        "Id": str(_next_invoice_id),
        "DocNumber": str(_next_invoice_id),
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
    _invoices_store.append(invoice)
    _next_invoice_id += 1
    return {"Invoice": invoice}


def update_invoice(invoice_id: str, data: dict):
    for i, inv in enumerate(_invoices_store):
        if inv["Id"] == invoice_id:
            updatable = {"DueDate", "CustomerRef", "Line", "BillEmail", "PrintStatus", "EmailStatus"}
            for k, v in data.items():
                if k in updatable:
                    _invoices_store[i][k] = v
            if "Line" in data:
                lines = data["Line"]
                total = sum(l.get("Amount", 0) for l in lines if l.get("DetailType") != "SubTotalLineDetail")
                _invoices_store[i]["TotalAmt"] = total
                _invoices_store[i]["Balance"] = total
            _invoices_store[i]["MetaData"]["LastUpdatedTime"] = _now()
            _invoices_store[i]["SyncToken"] = str(int(_invoices_store[i]["SyncToken"]) + 1)
            return {"Invoice": _invoices_store[i]}
    return {"error": f"Invoice {invoice_id} not found"}


def void_invoice(invoice_id: str):
    for i, inv in enumerate(_invoices_store):
        if inv["Id"] == invoice_id:
            _invoices_store[i]["Status"] = "Voided"
            _invoices_store[i]["Balance"] = 0.00
            _invoices_store[i]["MetaData"]["LastUpdatedTime"] = _now()
            _invoices_store[i]["SyncToken"] = str(int(_invoices_store[i]["SyncToken"]) + 1)
            return {"Invoice": _invoices_store[i]}
    return {"error": f"Invoice {invoice_id} not found"}


def send_invoice(invoice_id: str):
    for i, inv in enumerate(_invoices_store):
        if inv["Id"] == invoice_id:
            _invoices_store[i]["EmailStatus"] = "Sent"
            _invoices_store[i]["MetaData"]["LastUpdatedTime"] = _now()
            return {"Invoice": _invoices_store[i]}
    return {"error": f"Invoice {invoice_id} not found"}


def get_invoice_pdf(invoice_id: str):
    for inv in _invoices_store:
        if inv["Id"] == invoice_id:
            return {"url": f"https://quickbooks.api.intuit.com/v3/company/{REALM_ID}/invoice/{invoice_id}/pdf"}
    return {"error": f"Invoice {invoice_id} not found"}


# ---------------------------------------------------------------------------
# Bills
# ---------------------------------------------------------------------------

def list_bills():
    return _bills_store


def get_bill(bill_id: str):
    for b in _bills_store:
        if b["Id"] == bill_id:
            return {"Bill": b}
    return {"error": f"Bill {bill_id} not found"}


def create_bill(data: dict):
    global _next_bill_id
    now = _now()
    lines = data.get("Line", [])
    total = sum(l.get("Amount", 0) for l in lines)

    bill = {
        "Id": str(_next_bill_id),
        "VendorRef": data.get("VendorRef", {}),
        "TxnDate": data.get("TxnDate", _now()[:10]),
        "DueDate": data.get("DueDate", _now()[:10]),
        "TotalAmt": total,
        "Balance": total,
        "Line": lines,
        "Status": "Open",
        "DocNumber": data.get("DocNumber", f"BILL-{_next_bill_id}"),
        "MetaData": {"CreateTime": now, "LastUpdatedTime": now},
        "SyncToken": "0",
    }
    _bills_store.append(bill)
    _next_bill_id += 1
    return {"Bill": bill}


def pay_bill(bill_id: str):
    for i, b in enumerate(_bills_store):
        if b["Id"] == bill_id:
            _bills_store[i]["Balance"] = 0.00
            _bills_store[i]["Status"] = "Paid"
            _bills_store[i]["MetaData"]["LastUpdatedTime"] = _now()
            _bills_store[i]["SyncToken"] = str(int(_bills_store[i]["SyncToken"]) + 1)
            return {"Bill": _bills_store[i]}
    return {"error": f"Bill {bill_id} not found"}


# ---------------------------------------------------------------------------
# Payments
# ---------------------------------------------------------------------------

def list_payments():
    return _payments_store


def get_payment(payment_id: str):
    for p in _payments_store:
        if p["Id"] == payment_id:
            return {"Payment": p}
    return {"error": f"Payment {payment_id} not found"}


def create_payment(data: dict):
    global _next_payment_id
    now = _now()
    total = float(data.get("TotalAmt", 0))

    payment = {
        "Id": str(_next_payment_id),
        "TxnDate": data.get("TxnDate", _now()[:10]),
        "CustomerRef": data.get("CustomerRef", {}),
        "TotalAmt": total,
        "Line": data.get("Line", []),
        "MetaData": {"CreateTime": now, "LastUpdatedTime": now},
        "SyncToken": "0",
    }
    _payments_store.append(payment)
    _next_payment_id += 1

    # Apply payment to linked invoices
    for line in payment.get("Line", []):
        for linked in line.get("LinkedTxn", []):
            if linked.get("TxnType") == "Invoice":
                inv_id = linked.get("TxnId")
                for i, inv in enumerate(_invoices_store):
                    if inv["Id"] == inv_id:
                        _invoices_store[i]["Balance"] = max(0, _invoices_store[i]["Balance"] - line.get("Amount", 0))
                        if _invoices_store[i]["Balance"] == 0:
                            _invoices_store[i]["Status"] = "Paid"
                        break

    return {"Payment": payment}


# ---------------------------------------------------------------------------
# Estimates
# ---------------------------------------------------------------------------

def list_estimates():
    return _estimates_store


def get_estimate(estimate_id: str):
    for e in _estimates_store:
        if e["Id"] == estimate_id:
            return {"Estimate": e}
    return {"error": f"Estimate {estimate_id} not found"}


def create_estimate(data: dict):
    global _next_estimate_id
    now = _now()
    lines = data.get("Line", [])
    total = sum(l.get("Amount", 0) for l in lines)

    estimate = {
        "Id": str(_next_estimate_id),
        "DocNumber": f"E-{_next_estimate_id}",
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
    _estimates_store.append(estimate)
    _next_estimate_id += 1
    return {"Estimate": estimate}


def convert_estimate_to_invoice(estimate_id: str):
    global _next_invoice_id
    for i, e in enumerate(_estimates_store):
        if e["Id"] == estimate_id:
            if e["TxnStatus"] not in ("Pending", "Accepted"):
                return {"error": f"Estimate {estimate_id} cannot be converted (status: {e['TxnStatus']})"}
            now = _now()
            lines = [l for l in e["Line"] if l.get("DetailType") == "SalesItemLineDetail"]
            total = sum(l.get("Amount", 0) for l in lines)
            lines.append({"Amount": total, "DetailType": "SubTotalLineDetail", "SubTotalLineDetail": {}})

            invoice = {
                "Id": str(_next_invoice_id),
                "DocNumber": str(_next_invoice_id),
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
            _invoices_store.append(invoice)
            _next_invoice_id += 1

            _estimates_store[i]["TxnStatus"] = "Accepted"
            _estimates_store[i]["AcceptedDate"] = _now()[:10]
            _estimates_store[i]["LinkedTxn"] = [{"TxnId": invoice["Id"], "TxnType": "Invoice"}]
            _estimates_store[i]["MetaData"]["LastUpdatedTime"] = now
            _estimates_store[i]["SyncToken"] = str(int(_estimates_store[i]["SyncToken"]) + 1)

            return {"Invoice": invoice}
    return {"error": f"Estimate {estimate_id} not found"}


# ---------------------------------------------------------------------------
# Expenses (Purchases)
# ---------------------------------------------------------------------------

def list_expenses():
    return _expenses_store


def get_expense(expense_id: str):
    for e in _expenses_store:
        if e["Id"] == expense_id:
            return {"Purchase": e}
    return {"error": f"Expense {expense_id} not found"}


def create_expense(data: dict):
    global _next_expense_id
    now = _now()
    lines = data.get("Line", [])
    total = sum(l.get("Amount", 0) for l in lines)

    expense = {
        "Id": str(_next_expense_id),
        "TxnDate": data.get("TxnDate", _now()[:10]),
        "AccountRef": data.get("AccountRef", {}),
        "PaymentType": data.get("PaymentType", "CreditCard"),
        "TotalAmt": total,
        "Line": lines,
        "MetaData": {"CreateTime": now, "LastUpdatedTime": now},
        "SyncToken": "0",
    }
    _expenses_store.append(expense)
    _next_expense_id += 1
    return {"Purchase": expense}


# ---------------------------------------------------------------------------
# Query Engine (simplified SQL-like)
# ---------------------------------------------------------------------------

def execute_query(query_str: str):
    """Parse simplified QuickBooks query: SELECT * FROM EntityName [WHERE field op 'value']"""
    query_str = query_str.strip()

    # Parse entity name
    parts = query_str.upper().split()
    if len(parts) < 4 or parts[0] != "SELECT" or parts[2] != "FROM":
        return {"error": f"Invalid query syntax: {query_str}"}

    entity = query_str.split("FROM")[1].strip().split()[0].strip()

    # Map entity to store
    entity_map = {
        "Invoice": _invoices_store,
        "Customer": _customers_store,
        "Vendor": _vendors_store,
        "Item": _items_store,
        "Account": _accounts_store,
        "Bill": _bills_store,
        "Payment": _payments_store,
        "Estimate": _estimates_store,
        "Purchase": _expenses_store,
    }

    if entity not in entity_map:
        return {"error": f"Unknown entity: {entity}"}

    results = list(entity_map[entity])

    # Parse WHERE clause if present
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
    """Apply simplified WHERE filtering."""
    # Handle simple conditions: field = 'value', field > 'value', field < 'value'
    # Also: Active = true/false, Balance > '0'
    import re

    # Split on AND (simplified - no OR support)
    conditions = re.split(r'\s+AND\s+', where_clause, flags=re.IGNORECASE)

    for cond in conditions:
        cond = cond.strip()
        # Match: field operator value
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
    """Get field value, supporting dot notation and common QBO fields."""
    if field in item:
        return item[field]
    # Handle nested refs like CustomerRef
    if field + "Ref" in item:
        ref = item[field + "Ref"]
        if isinstance(ref, dict):
            return ref.get("value")
    # Dot notation
    parts = field.split(".")
    current = item
    for p in parts:
        if isinstance(current, dict) and p in current:
            current = current[p]
        else:
            return None
    return current


def _compare(item_val, op, value):
    """Compare values with type coercion."""
    # Handle booleans
    if isinstance(item_val, bool):
        bool_val = value.lower() in ("true", "1", "yes")
        if op == "=":
            return item_val == bool_val
        elif op == "!=":
            return item_val != bool_val
        return False

    # Try numeric comparison
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

    # String comparison
    str_item = str(item_val)
    if op == "=":
        return str_item.lower() == value.lower()
    elif op == "!=":
        return str_item.lower() != value.lower()
    elif op == "LIKE":
        pattern = value.replace("%", ".*")
        return bool(re.match(pattern, str_item, re.IGNORECASE))

    return False


# ---------------------------------------------------------------------------
# Reports
# ---------------------------------------------------------------------------

def profit_and_loss(start_date: str = None, end_date: str = None):
    """Generate a simplified P&L report."""
    # Filter invoices by date range for revenue
    revenue_invoices = _invoices_store
    expense_bills = _bills_store
    expense_purchases = _expenses_store

    if start_date:
        revenue_invoices = [inv for inv in revenue_invoices if (inv.get("TxnDate") or "") >= start_date]
        expense_bills = [b for b in expense_bills if (b.get("TxnDate") or "") >= start_date]
        expense_purchases = [e for e in expense_purchases if (e.get("TxnDate") or "") >= start_date]
    if end_date:
        revenue_invoices = [inv for inv in revenue_invoices if (inv.get("TxnDate") or "") <= end_date]
        expense_bills = [b for b in expense_bills if (b.get("TxnDate") or "") <= end_date]
        expense_purchases = [e for e in expense_purchases if (e.get("TxnDate") or "") <= end_date]

    # Only count paid invoices for revenue
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
    """Group expenses by account for P&L detail."""
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
    """Generate a simplified Balance Sheet report."""
    total_ar = sum(inv.get("Balance", 0) for inv in _invoices_store if inv.get("Status") not in ("Voided",))
    total_ap = sum(b.get("Balance", 0) for b in _bills_store)

    # Simplified balance sheet
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
    """Generate AR Aging report."""
    aging_buckets = {"Current": [], "1-30": [], "31-60": [], "61-90": [], "91+": []}
    today = datetime.utcnow().strftime("%Y-%m-%d")

    for inv in _invoices_store:
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
    """Generate AP Aging report."""
    aging_buckets = {"Current": [], "1-30": [], "31-60": [], "61-90": [], "91+": []}
    today = datetime.utcnow().strftime("%Y-%m-%d")

    for bill in _bills_store:
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



