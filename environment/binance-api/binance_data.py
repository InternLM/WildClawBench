"""Data access module for the Binance API mock service.

Mirrors a subset of the Binance Spot REST API (api.binance.com): symbol price
ticker, 24hr ticker, order book depth, klines (candles), and account balances.
"""

import csv
from pathlib import Path

DATA_DIR = Path(__file__).parent

import sys as _sys
_sys.path.insert(0, str(DATA_DIR.parent))
from _mutable_store import (
    read_seed_with_ctx, get_store,
    strict_int,
    opt_float,
)

_store = get_store("binance-api")
_API = "binance-api"

_store.register("prices", primary_key="symbol",
                initial_loader=lambda: _coerce_prices(_load("prices.json", "prices")))
_store.register("klines", primary_key="_pk",
                initial_loader=lambda: [
                    {**r, "_pk": f"{r['symbol']}@{r['interval']}@{r['open_time']}"}
                    for r in _coerce_klines(_load("klines.json", "klines"))])
_store.register("balances", primary_key="asset",
                initial_loader=lambda: _coerce_balances(_load("balances.json", "balances")))
_store.register("depth", primary_key="_pk",
                initial_loader=lambda: [
                    {**r, "_pk": f"{r['symbol']}@{r['side']}@{r['price']}"}
                    for r in _coerce_depth(_load("depth.json", "depth"))])


def _prices_rows():
    return _store.table("prices").rows()


def _klines_rows():
    return [{k: v for k, v in r.items() if k != "_pk"} for r in _store.table("klines").rows()]


def _balances_rows():
    return _store.table("balances").rows()


def _depth_rows():
    return [{k: v for k, v in r.items() if k != "_pk"} for r in _store.table("depth").rows()]



def _load(filename, table):
    return read_seed_with_ctx(DATA_DIR / filename, _API, table)


def _strip_ctx(r):
    return {k: v for k, v in r.items() if not k.startswith("__")}


def _to_float(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return 0.0


def _fmt(v):
    """Binance returns numeric fields as strings."""
    return f"{_to_float(v):.8f}"


# ---------------------------------------------------------------------------
# Load + coerce
# ---------------------------------------------------------------------------

def _coerce_prices(rows):
    out = []
    for r in rows:
        out.append({
            "symbol": r["symbol"],
            "price": opt_float(r, "price", default=None),
            "priceChange": opt_float(r, "priceChange", default=None),
            "priceChangePercent": opt_float(r, "priceChangePercent", default=None),
            "highPrice": opt_float(r, "highPrice", default=None),
            "lowPrice": opt_float(r, "lowPrice", default=None),
            "volume": opt_float(r, "volume", default=None),
        })
    return out


def _coerce_klines(rows):
    out = []
    for r in rows:
        out.append({
            "symbol": r["symbol"],
            "interval": r["interval"],
            "open_time": strict_int(r, "open_time"),
            "open": opt_float(r, "open", default=None),
            "high": opt_float(r, "high", default=None),
            "low": opt_float(r, "low", default=None),
            "close": opt_float(r, "close", default=None),
            "volume": opt_float(r, "volume", default=None),
            "close_time": strict_int(r, "close_time"),
        })
    return out


def _coerce_balances(rows):
    out = []
    for r in rows:
        out.append({
            "asset": r["asset"],
            "free": opt_float(r, "free", default=None),
            "locked": opt_float(r, "locked", default=None),
        })
    return out


def _coerce_depth(rows):
    out = []
    for r in rows:
        out.append({
            "symbol": r["symbol"],
            "side": r["side"],
            "price": opt_float(r, "price", default=None),
            "qty": opt_float(r, "qty", default=None),
        })
    return out










# ---------------------------------------------------------------------------
# Ticker price  (GET /api/v3/ticker/price)
# ---------------------------------------------------------------------------

def get_ticker_price(symbol=None):
    if symbol:
        p = next((x for x in _prices_rows() if x["symbol"] == symbol.upper()), None)
        if not p:
            return {"error": "Invalid symbol.", "code": -1121}
        return {"symbol": p["symbol"], "price": _fmt(p["price"])}
    return [{"symbol": p["symbol"], "price": _fmt(p["price"])} for p in _prices_rows()]


# ---------------------------------------------------------------------------
# 24hr ticker  (GET /api/v3/ticker/24hr)
# ---------------------------------------------------------------------------

def _ticker_24hr_view(p):
    return {
        "symbol": p["symbol"],
        "priceChange": _fmt(p["priceChange"]),
        "priceChangePercent": f"{p['priceChangePercent']:.3f}",
        "lastPrice": _fmt(p["price"]),
        "highPrice": _fmt(p["highPrice"]),
        "lowPrice": _fmt(p["lowPrice"]),
        "volume": _fmt(p["volume"]),
    }


def get_ticker_24hr(symbol=None):
    if symbol:
        p = next((x for x in _prices_rows() if x["symbol"] == symbol.upper()), None)
        if not p:
            return {"error": "Invalid symbol.", "code": -1121}
        return _ticker_24hr_view(p)
    return [_ticker_24hr_view(p) for p in _prices_rows()]


# ---------------------------------------------------------------------------
# Order book depth  (GET /api/v3/depth)
# ---------------------------------------------------------------------------

def get_depth(symbol, limit=100):
    sym = (symbol or "").upper()
    levels = [d for d in _depth_rows() if d["symbol"] == sym]
    if not levels:
        return {"error": "Invalid symbol.", "code": -1121}
    bids = sorted((d for d in levels if d["side"] == "bid"), key=lambda d: d["price"], reverse=True)
    asks = sorted((d for d in levels if d["side"] == "ask"), key=lambda d: d["price"])
    bids = bids[:limit]
    asks = asks[:limit]
    return {
        "lastUpdateId": 1027024,
        "bids": [[_fmt(b["price"]), _fmt(b["qty"])] for b in bids],
        "asks": [[_fmt(a["price"]), _fmt(a["qty"])] for a in asks],
    }


# ---------------------------------------------------------------------------
# Klines / candlesticks  (GET /api/v3/klines)
# ---------------------------------------------------------------------------

def get_klines(symbol, interval="1h", limit=500):
    sym = (symbol or "").upper()
    candles = [
        k for k in _klines_rows()
        if k["symbol"] == sym and k["interval"] == interval
    ]
    if not candles:
        return {"error": "Invalid symbol.", "code": -1121}
    candles = sorted(candles, key=lambda k: k["open_time"])[:limit]
    out = []
    for k in candles:
        out.append([
            k["open_time"],
            _fmt(k["open"]),
            _fmt(k["high"]),
            _fmt(k["low"]),
            _fmt(k["close"]),
            _fmt(k["volume"]),
            k["close_time"],
            _fmt(k["close"] * k["volume"]),
            0,
            "0",
            "0",
            "0",
        ])
    return out


# ---------------------------------------------------------------------------
# Account  (GET /api/v3/account)
# ---------------------------------------------------------------------------

def get_account():
    balances = [
        {"asset": b["asset"], "free": _fmt(b["free"]), "locked": _fmt(b["locked"])}
        for b in _balances_rows()
    ]
    return {
        "makerCommission": 10,
        "takerCommission": 10,
        "buyerCommission": 0,
        "sellerCommission": 0,
        "canTrade": True,
        "canWithdraw": True,
        "canDeposit": True,
        "accountType": "SPOT",
        "balances": balances,
        "permissions": ["SPOT"],
    }

_store.eager_load()
