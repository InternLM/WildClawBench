"""Data access module for the Alpaca trading API mock service.

Numeric fields are returned as strings to match Alpaca's JSON conventions
(e.g. qty "40", buying_power "50681.50"). Mutations are held in process
memory and reset on restart.
"""

import csv
import json
import uuid
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).parent

import sys as _sys
_sys.path.insert(0, str(DATA_DIR.parent))
from _mutable_store import (
    read_seed_with_ctx, get_store, opt_float, opt_str, strict_bool)

_store = get_store("alpaca-api")
_API = "alpaca-api"


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

_store.register("positions", primary_key="asset_id",
                initial_loader=lambda: _coerce_positions(_load("positions.json", "positions")))
_store.register("orders", primary_key="id",
                initial_loader=lambda: _coerce_orders(_load("orders.json", "orders")))
_store.register("assets", primary_key="id",
                initial_loader=lambda: _coerce_assets(_load("assets.json", "assets")))
_store.register_document("quotes", initial_loader=lambda: _coerce_quotes(_load("quotes.json", "quotes")))
_store.register_document("account", initial_loader=lambda: __import__('json').load(open(DATA_DIR / "account.json", encoding="utf-8")))


def _positions_rows():
    return _store.table("positions").rows()


def _orders_rows():
    return _store.table("orders").rows()


def _assets_rows():
    return _store.table("assets").rows()


def _quotes_doc():
    return _store.document("quotes").get()


def _account_doc():
    return _store.document("account").get()



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

def _coerce_positions(rows):
    out = []
    for r in rows:
        out.append({
            "asset_id": r["asset_id"],
            "symbol": r["symbol"],
            "qty": r["qty"],
            "avg_entry_price": r["avg_entry_price"],
            "current_price": r["current_price"],
            "side": r["side"],
            "market_value": r["market_value"],
            "cost_basis": r["cost_basis"],
            "unrealized_pl": r["unrealized_pl"],
            "asset_class": "us_equity",
            "exchange": "NASDAQ",
        })
    return out


def _coerce_orders(rows):
    out = []
    for r in rows:
        out.append({
            "id": r["id"],
            "client_order_id": r["client_order_id"],
            "symbol": r["symbol"],
            "qty": r["qty"],
            "filled_qty": r["filled_qty"],
            "side": r["side"],
            "type": r["type"],
            "time_in_force": r["time_in_force"],
            "limit_price": opt_str(r, "limit_price", default="") or None,
            "status": r["status"],
            "filled_avg_price": opt_str(r, "filled_avg_price", default="") or None,
            "submitted_at": r["submitted_at"],
            "filled_at": opt_str(r, "filled_at", default="") or None,
        })
    return out


def _coerce_assets(rows):
    out = []
    for r in rows:
        out.append({
            "id": r["id"],
            "symbol": r["symbol"],
            "name": r["name"],
            "exchange": r["exchange"],
            "class": r["asset_class"],
            "tradable": strict_bool(r, "tradable"),
            "fractionable": strict_bool(r, "fractionable"),
            "status": "active",
        })
    return out


def _coerce_quotes(rows):
    quotes = {}
    for r in rows:
        quotes[r["symbol"]] = {
            "t": r["timestamp"],
            "bp": opt_float(r, "bid_price", default=0.0),
            "bs": int(opt_float(r, "bid_size", default=0.0)),
            "ap": opt_float(r, "ask_price", default=0.0),
            "as": int(opt_float(r, "ask_size", default=0.0)),
        }
    return quotes



# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _new_order_id():
    return f"ORD-{uuid.uuid4()}"


def _find_position(symbol):
    return next((p for p in _positions_rows() if p["symbol"] == symbol.upper()), None)


def _find_asset(symbol):
    return next((a for a in _assets_rows() if a["symbol"] == symbol.upper()), None)


def _ref_price(symbol):
    q = _quotes_doc().get(symbol.upper())
    if q:
        return q["ap"]
    pos = _find_position(symbol)
    if pos:
        return _to_float(pos["current_price"])
    return 0.0


# ---------------------------------------------------------------------------
# Account
# ---------------------------------------------------------------------------

def get_account():
    return _account_doc()


# ---------------------------------------------------------------------------
# Positions
# ---------------------------------------------------------------------------

def list_positions():
    return list(_positions_rows())


def get_position(symbol):
    p = _find_position(symbol)
    if not p:
        return {"error": f"position not found for {symbol.upper()}", "code": 40410000}
    return p


# ---------------------------------------------------------------------------
# Orders
# ---------------------------------------------------------------------------

def list_orders(status=None):
    results = list(_orders_rows())
    if status and status != "all":
        if status == "open":
            results = [o for o in results if o["status"] in ("new", "accepted", "partially_filled")]
        elif status == "closed":
            results = [o for o in results if o["status"] in ("filled", "canceled", "expired")]
        else:
            results = [o for o in results if o["status"] == status]
    return results


def get_order(order_id):
    o = next((o for o in _orders_rows() if o["id"] == order_id), None)
    if not o:
        return {"error": f"order not found: {order_id}", "code": 40410000}
    return o


def create_order(symbol, qty, side, type="market", time_in_force="day", limit_price=None):
    symbol = (symbol or "").upper()
    side = (side or "").lower()
    if side not in ("buy", "sell"):
        return {"error": "side must be 'buy' or 'sell'", "code": 42210000}
    asset = _find_asset(symbol)
    if not asset:
        return {"error": f"asset not found: {symbol}", "code": 40410000}
    if not asset["tradable"]:
        return {"error": f"asset {symbol} is not tradable", "code": 40310000}
    qty_f = _to_float(qty)
    if qty_f <= 0:
        return {"error": "qty must be positive", "code": 42210000}

    price = _to_float(limit_price) if limit_price else _ref_price(symbol)

    if side == "buy":
        cost = price * qty_f
        buying_power = _to_float(_account_doc()["buying_power"])
        if cost > buying_power:
            return {
                "error": f"insufficient buying power: need {cost:.2f}, have {buying_power:.2f}",
                "code": 40310000,
            }
    else:  # sell
        pos = _find_position(symbol)
        held = _to_float(pos["qty"]) if pos else 0.0
        if qty_f > held:
            return {
                "error": f"insufficient qty available: requested {qty_f:.0f}, held {held:.0f}",
                "code": 40310000,
            }

    order = {
        "id": _new_order_id(),
        "client_order_id": f"cli-{uuid.uuid4().hex[:12]}",
        "symbol": symbol,
        "qty": str(int(qty_f)) if qty_f.is_integer() else str(qty_f),
        "filled_qty": "0",
        "side": side,
        "type": type or "market",
        "time_in_force": time_in_force or "day",
        "limit_price": str(limit_price) if limit_price else None,
        "status": "new",
        "filled_avg_price": None,
        "submitted_at": _now(),
        "filled_at": None,
    }
    _store_insert("orders", order)
    return order


def cancel_order(order_id):
    o = next((o for o in _orders_rows() if o["id"] == order_id), None)
    if not o:
        return {"error": f"order not found: {order_id}", "code": 40410000}
    if o["status"] in ("filled", "canceled", "expired"):
        return {"error": f"order {order_id} is not cancelable (status {o['status']})", "code": 42210000}
    o["status"] = "canceled"
    return {"status": "canceled", "id": order_id}


# ---------------------------------------------------------------------------
# Assets
# ---------------------------------------------------------------------------

def list_assets(status=None, asset_class=None):
    results = list(_assets_rows())
    if status:
        results = [a for a in results if a["status"] == status]
    if asset_class:
        results = [a for a in results if a["class"] == asset_class]
    return results


# ---------------------------------------------------------------------------
# Market data
# ---------------------------------------------------------------------------

def get_latest_quote(symbol):
    q = _quotes_doc().get(symbol.upper())
    if not q:
        return {"error": f"no quote for {symbol.upper()}", "code": 40410000}
    return {"symbol": symbol.upper(), "quote": q}

_store.eager_load()
