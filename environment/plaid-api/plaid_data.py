"""Data access module for the Plaid API mock service.

Plaid uses POST for reads. This module exposes the underlying data operations;
the server maps them to POST /accounts/get, /transactions/get, etc.
Amounts are floats in the account's currency. Mutations (none) reset on restart.
"""

import csv
import json
import sys
import uuid
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).parent

sys.path.insert(0, str(DATA_DIR.parent))
from _mutable_store import (
    read_seed_with_ctx, get_store, opt_csv_list, opt_float, opt_str, strict_bool)

_store = get_store("plaid-api")
_API = "plaid-api"


def _load(filename, table):
    return read_seed_with_ctx(DATA_DIR / filename, _API, table)


def _strip_ctx(r):
    return {k: v for k, v in r.items() if not k.startswith("__")}


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
            "official_name": opt_str(r, "official_name", default="") or None,
            "mask": r["mask"],
            "type": r["type"],
            "subtype": r["subtype"],
            "balances": {
                "available": opt_float(r, "available", default=None),
                "current": opt_float(r, "current", default=None),
                "limit": opt_float(r, "limit", default=None),
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
            "amount": opt_float(r, "amount", default=None),
            "iso_currency_code": r["iso_currency_code"],
            "date": r["date"],
            "name": r["name"],
            "merchant_name": opt_str(r, "merchant_name", default="") or None,
            "category": [c for c in opt_csv_list(r, "category", sep=";") if c],
            "pending": strict_bool(r, "pending"),
            "payment_channel": r["payment_channel"],
        })
    return out


def _load_item():
    with open(DATA_DIR / "item.json", encoding="utf-8") as f:
        return json.load(f)


def _load_identity():
    with open(DATA_DIR / "identity.json", encoding="utf-8") as f:
        return json.load(f)


_store.register("accounts", primary_key="account_id",
                initial_loader=lambda: _coerce_accounts(_load("accounts.json", "accounts")))
_store.register("transactions", primary_key="transaction_id",
                initial_loader=lambda: _coerce_transactions(_load("transactions.json", "transactions")))
_store.register_document("item", initial_loader=_load_item)
_store.register_document("identity", initial_loader=_load_identity)


def _accounts_rows():
    return _store.table("accounts").rows()


def _transactions_rows():
    return _store.table("transactions").rows()


def _item_doc():
    return _store.document("item").get()


def _identity_doc():
    return _store.document("identity").get()


def _request_id():
    return uuid.uuid4().hex[:16]


# ---------------------------------------------------------------------------
# Accounts
# ---------------------------------------------------------------------------

def get_accounts(account_ids=None):
    accounts = list(_accounts_rows())
    if account_ids:
        wanted = set(account_ids)
        accounts = [a for a in accounts if a["account_id"] in wanted]
    return {
        "accounts": accounts,
        "item": _item_doc()["item"],
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
    txns = list(_transactions_rows())
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
        "item": _item_doc()["item"],
        "request_id": _request_id(),
    }


# ---------------------------------------------------------------------------
# Institution
# ---------------------------------------------------------------------------

def get_institution_by_id(institution_id):
    inst = _item_doc()["institution"]
    if institution_id != inst["institution_id"]:
        return {"error_code": "INSTITUTION_NOT_FOUND",
                "error_message": f"Unknown institution {institution_id}"}
    return {"institution": inst, "request_id": _request_id()}


# ---------------------------------------------------------------------------
# Identity
# ---------------------------------------------------------------------------

def get_identity(account_ids=None):
    accounts = []
    for a in _accounts_rows():
        if account_ids and a["account_id"] not in set(account_ids):
            continue
        owners = _identity_doc()["owners"].get(a["account_id"], [])
        accounts.append({**a, "owners": owners})
    return {
        "accounts": accounts,
        "item": _item_doc()["item"],
        "request_id": _request_id(),
    }

_store.eager_load()
