"""Data access module for the Binance API mock service.

Mirrors a subset of the Binance Spot REST API (api.binance.com): symbol price
ticker, 24hr ticker, order book depth, klines (candles), and account balances.
"""

import csv
from copy import deepcopy
from pathlib import Path

DATA_DIR = Path(__file__).parent


def _load(filename):
    with open(DATA_DIR / filename, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


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
            "price": _to_float(r["price"]),
            "priceChange": _to_float(r["priceChange"]),
            "priceChangePercent": _to_float(r["priceChangePercent"]),
            "highPrice": _to_float(r["highPrice"]),
            "lowPrice": _to_float(r["lowPrice"]),
            "volume": _to_float(r["volume"]),
        })
    return out


def _coerce_klines(rows):
    out = []
    for r in rows:
        out.append({
            "symbol": r["symbol"],
            "interval": r["interval"],
            "open_time": int(r["open_time"]),
            "open": _to_float(r["open"]),
            "high": _to_float(r["high"]),
            "low": _to_float(r["low"]),
            "close": _to_float(r["close"]),
            "volume": _to_float(r["volume"]),
            "close_time": int(r["close_time"]),
        })
    return out


def _coerce_balances(rows):
    out = []
    for r in rows:
        out.append({
            "asset": r["asset"],
            "free": _to_float(r["free"]),
            "locked": _to_float(r["locked"]),
        })
    return out


def _coerce_depth(rows):
    out = []
    for r in rows:
        out.append({
            "symbol": r["symbol"],
            "side": r["side"],
            "price": _to_float(r["price"]),
            "qty": _to_float(r["qty"]),
        })
    return out


_prices = _coerce_prices(_load("prices.csv"))
_klines = _coerce_klines(_load("klines.csv"))
_balances = _coerce_balances(_load("balances.csv"))
_depth = _coerce_depth(_load("depth.csv"))

_prices_store = deepcopy(_prices)
_klines_store = deepcopy(_klines)
_balances_store = deepcopy(_balances)
_depth_store = deepcopy(_depth)


# ---------------------------------------------------------------------------
# Ticker price  (GET /api/v3/ticker/price)
# ---------------------------------------------------------------------------

def get_ticker_price(symbol=None):
    if symbol:
        p = next((x for x in _prices_store if x["symbol"] == symbol.upper()), None)
        if not p:
            return {"error": "Invalid symbol.", "code": -1121}
        return {"symbol": p["symbol"], "price": _fmt(p["price"])}
    return [{"symbol": p["symbol"], "price": _fmt(p["price"])} for p in _prices_store]


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
        p = next((x for x in _prices_store if x["symbol"] == symbol.upper()), None)
        if not p:
            return {"error": "Invalid symbol.", "code": -1121}
        return _ticker_24hr_view(p)
    return [_ticker_24hr_view(p) for p in _prices_store]


# ---------------------------------------------------------------------------
# Order book depth  (GET /api/v3/depth)
# ---------------------------------------------------------------------------

def get_depth(symbol, limit=100):
    sym = (symbol or "").upper()
    levels = [d for d in _depth_store if d["symbol"] == sym]
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
        k for k in _klines_store
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
        for b in _balances_store
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
