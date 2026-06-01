"""Data access module for the Plaid API mock service.

Plaid uses POST for reads. This module exposes the underlying data operations;
the server maps them to POST /accounts/get, /transactions/get, etc.
Amounts are floats in the account's currency. Mutations (none) reset on restart.
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


def _to_bool(v):
    return str(v).strip().lower() == "true"


def _to_float(v):
    if v is None or str(v).strip() == "":
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


# ---------------------------------------------------------------------------
# Load + coerce
# ---------------------------------------------------------------------------

def _coerce_accounts(rows):
    out = []
    for r in rows:
        out.append({
            "account_id": r["account_id"],
            "name": r["name"],
            "official_name": r["official_name"] or None,
            "mask": r["mask"],
            "type": r["type"],
            "subtype": r["subtype"],
            "balances": {
                "available": _to_float(r["available"]),
                "current": _to_float(r["current"]),
                "limit": _to_float(r["limit"]),
                "iso_currency_code": r["iso_currency_code"],
                "unofficial_currency_code": None,
            },
        })
    return out


def _coerce_transactions(rows):
    out = []
    for r in rows:
        out.append({
            "transaction_id": r["transaction_id"],
            "account_id": r["account_id"],
            "amount": _to_float(r["amount"]),
            "iso_currency_code": r["iso_currency_code"],
            "date": r["date"],
            "name": r["name"],
            "merchant_name": r["merchant_name"] or None,
            "category": [c for c in r["category"].split(";") if c],
            "pending": _to_bool(r["pending"]),
            "payment_channel": r["payment_channel"],
        })
    return out


_accounts = _coerce_accounts(_load("accounts.csv"))
_transactions = _coerce_transactions(_load("transactions.csv"))

with open(DATA_DIR / "item.json", encoding="utf-8") as _f:
    _item = json.load(_f)
with open(DATA_DIR / "identity.json", encoding="utf-8") as _f:
    _identity = json.load(_f)

_accounts_store = deepcopy(_accounts)
_transactions_store = deepcopy(_transactions)
_item_store = deepcopy(_item)
_identity_store = deepcopy(_identity)


def _request_id():
    return uuid.uuid4().hex[:16]


# ---------------------------------------------------------------------------
# Accounts
# ---------------------------------------------------------------------------

def get_accounts(account_ids=None):
    accounts = list(_accounts_store)
    if account_ids:
        wanted = set(account_ids)
        accounts = [a for a in accounts if a["account_id"] in wanted]
    return {
        "accounts": accounts,
        "item": _item_store["item"],
        "request_id": _request_id(),
    }


def get_balances(account_ids=None):
    # Same shape as get_accounts; balances are embedded in each account.
    return get_accounts(account_ids=account_ids)


# ---------------------------------------------------------------------------
# Transactions
# ---------------------------------------------------------------------------

def get_transactions(start_date=None, end_date=None, account_ids=None,
                     count=100, offset=0):
    txns = list(_transactions_store)
    if account_ids:
        wanted = set(account_ids)
        txns = [t for t in txns if t["account_id"] in wanted]
    if start_date:
        txns = [t for t in txns if t["date"] >= start_date]
    if end_date:
        txns = [t for t in txns if t["date"] <= end_date]
    txns.sort(key=lambda t: t["date"], reverse=True)
    total = len(txns)
    try:
        offset = max(0, int(offset))
    except (TypeError, ValueError):
        offset = 0
    try:
        count = max(1, min(int(count), 500))
    except (TypeError, ValueError):
        count = 100
    page = txns[offset: offset + count]
    return {
        "accounts": get_accounts(account_ids=account_ids)["accounts"],
        "transactions": page,
        "total_transactions": total,
        "item": _item_store["item"],
        "request_id": _request_id(),
    }


# ---------------------------------------------------------------------------
# Institution
# ---------------------------------------------------------------------------

def get_institution_by_id(institution_id):
    inst = _item_store["institution"]
    if institution_id != inst["institution_id"]:
        return {"error_code": "INSTITUTION_NOT_FOUND",
                "error_message": f"Unknown institution {institution_id}"}
    return {"institution": inst, "request_id": _request_id()}


# ---------------------------------------------------------------------------
# Identity
# ---------------------------------------------------------------------------

def get_identity(account_ids=None):
    accounts = []
    for a in _accounts_store:
        if account_ids and a["account_id"] not in set(account_ids):
            continue
        owners = _identity_store["owners"].get(a["account_id"], [])
        accounts.append({**a, "owners": owners})
    return {
        "accounts": accounts,
        "item": _item_store["item"],
        "request_id": _request_id(),
    }
