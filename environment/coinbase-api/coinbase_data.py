"""Data access module for the Coinbase API mock service.

Mirrors a subset of the Coinbase v2 API. Crypto balances are decimal strings;
fiat-equivalent ("native") amounts accompany each balance. Buys/sells and the
resulting transactions are held in process memory and reset on restart.
"""

import csv
import json
import uuid
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).parent

import sys as _sys
_sys.path.insert(0, str(DATA_DIR.parent))
from _mutable_store import (  # noqa: E402
    read_seed_with_ctx, get_store,
    strict_bool,
    opt_float,
)

_store = get_store("coinbase-api")
_API = "coinbase-api"

_API = "coinbase-api"


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

_store.register("accounts", primary_key="id",
                initial_loader=lambda: _coerce_accounts(_load("accounts.json", "accounts")))
_store.register("prices", primary_key="pair",
                initial_loader=lambda: _coerce_prices(_load("prices.json", "prices")))
_store.register("transactions", primary_key="id",
                initial_loader=lambda: _coerce_transactions(_load("transactions.json", "transactions")))
_store.register_document("user", initial_loader=lambda: __import__('json').load(open(DATA_DIR / "user.json", encoding="utf-8")))


def _accounts_rows():
    return _store.table("accounts").rows()


def _prices_rows():
    return _store.table("prices").rows()


def _transactions_rows():
    return _store.table("transactions").rows()


def _user_doc():
    return _store.document("user").get()



def _load(filename, table):
    return read_seed_with_ctx(DATA_DIR / filename, _API, table)


def _strip_ctx(r):
    return {k: v for k, v in r.items() if not k.startswith("__")}


def _now():
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


def _to_bool(v):
    return str(v).strip().lower() == "true"


def _to_float(v, default=0.0):
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


# ---------------------------------------------------------------------------
# Load + coerce
# ---------------------------------------------------------------------------

def _coerce_accounts(rows):
    out = []
    for r in rows:
        out.append({
            "id": r["id"],
            "name": r["name"],
            "primary": strict_bool(r, "primary"),
            "type": r["type"],
            "currency": {"code": r["currency_code"], "name": r["currency_name"]},
            "balance": {"amount": r["balance_amount"], "currency": r["currency_code"]},
            "native_balance": {"amount": r["native_balance_amount"], "currency": r["native_currency"]},
            "created_at": r["created_at"],
            "updated_at": r["updated_at"],
            "_balance_num": opt_float(r, "balance_amount", default=0.0),
            "_native_num": opt_float(r, "native_balance_amount", default=0.0),
        })
    return out


def _coerce_prices(rows):
    return [{"pair": r["pair"], "base": r["base"], "currency": r["currency"],
             "amount": r["amount"], "_amount_num": opt_float(r, "amount", default=0.0)}
            for r in rows]


def _coerce_transactions(rows):
    out = []
    for r in rows:
        out.append({
            "id": r["id"],
            "account_id": r["account_id"],
            "type": r["type"],
            "status": r["status"],
            "amount": {"amount": r["amount"], "currency": r["currency"]},
            "native_amount": {"amount": r["native_amount"], "currency": r["native_currency"]},
            "description": r["description"],
            "created_at": r["created_at"],
            "updated_at": r["created_at"],
        })
    return out






# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _new_id():
    return str(uuid.uuid4())


def _public_account(a):
    return {k: v for k, v in a.items() if not k.startswith("_")}


def _find_account(account_id):
    return next((a for a in _accounts_rows() if a["id"] == account_id), None)


def _fmt_crypto(value):
    return f"{value:.8f}"


def _fmt_fiat(value):
    return f"{value:.2f}"


# ---------------------------------------------------------------------------
# Accounts
# ---------------------------------------------------------------------------

def list_accounts():
    return {"data": [_public_account(a) for a in _accounts_rows()]}


def get_account(account_id):
    a = _find_account(account_id)
    if not a:
        return {"error": f"Account {account_id} not found"}
    return {"data": _public_account(a)}


# ---------------------------------------------------------------------------
# Prices
# ---------------------------------------------------------------------------

def get_spot_price(pair):
    p = next((x for x in _prices_rows() if x["pair"].upper() == pair.upper()), None)
    if not p:
        return {"error": f"No spot price for pair {pair}"}
    return {"data": {"base": p["base"], "currency": p["currency"], "amount": p["amount"]}}


def _price_for(currency_code):
    return next((x for x in _prices_rows()
                 if x["base"] == currency_code and x["currency"] == "USD"), None)


# ---------------------------------------------------------------------------
# Buys / Sells
# ---------------------------------------------------------------------------

def _trade(account_id, amount, side):
    account = _find_account(account_id)
    if not account:
        return {"error": f"Account {account_id} not found"}
    try:
        qty = float(amount)
    except (TypeError, ValueError):
        return {"error": "amount must be a number"}
    if qty <= 0:
        return {"error": "amount must be positive"}

    code = account["currency"]["code"]
    price = _price_for(code)
    if not price:
        return {"error": f"No spot price available for {code}"}
    fiat = qty * price["_amount_num"]

    if side == "buy":
        account["_balance_num"] += qty
        account["_native_num"] += fiat
        signed_qty = qty
        signed_fiat = fiat
    else:  # sell
        if qty > account["_balance_num"]:
            return {"error": f"Insufficient {code} balance to sell {qty}"}
        account["_balance_num"] -= qty
        account["_native_num"] = max(0.0, account["_native_num"] - fiat)
        signed_qty = -qty
        signed_fiat = -fiat

    account["balance"]["amount"] = _fmt_crypto(account["_balance_num"])
    account["native_balance"]["amount"] = _fmt_fiat(account["_native_num"])
    account["updated_at"] = _now()

    txn = {
        "id": _new_id(),
        "account_id": account_id,
        "type": side,
        "status": "completed",
        "amount": {"amount": _fmt_crypto(signed_qty), "currency": code},
        "native_amount": {"amount": _fmt_fiat(signed_fiat), "currency": "USD"},
        "description": f"{side.capitalize()} {qty} {code}",
        "created_at": _now(),
        "updated_at": _now(),
    }
    _store_insert("transactions", txn)

    return {"data": {
        "id": _new_id(),
        "status": "completed",
        "resource": side,
        "amount": {"amount": _fmt_crypto(qty), "currency": code},
        "total": {"amount": _fmt_fiat(fiat), "currency": "USD"},
        "unit_price": {"amount": price["amount"], "currency": "USD"},
        "account_id": account_id,
        "transaction_id": txn["id"],
        "created_at": txn["created_at"],
    }}


def create_buy(account_id, amount):
    return _trade(account_id, amount, "buy")


def create_sell(account_id, amount):
    return _trade(account_id, amount, "sell")


# ---------------------------------------------------------------------------
# Transactions
# ---------------------------------------------------------------------------

def list_transactions(account_id):
    if not _find_account(account_id):
        return {"error": f"Account {account_id} not found"}
    txns = [t for t in _transactions_rows() if t["account_id"] == account_id]
    txns.sort(key=lambda t: t["created_at"], reverse=True)
    return {"data": txns}


# ---------------------------------------------------------------------------
# User
# ---------------------------------------------------------------------------

def get_user():
    return {"data": _user_doc()}

_store.eager_load()
