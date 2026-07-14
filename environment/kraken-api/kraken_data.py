"""Data access module for the Kraken API mock service.

Mirrors a subset of the Kraken REST API (api.kraken.com): public market data
(Ticker, OHLC, AssetPairs, Assets) and a private account Balance endpoint.

Every response is wrapped in Kraken's standard envelope:
    {"error": [], "result": {...}}
"""

import csv
import sys
from pathlib import Path

DATA_DIR = Path(__file__).parent

sys.path.insert(0, str(DATA_DIR.parent))
from _mutable_store import (
    read_seed_with_ctx, get_store,
    strict_int,
)

_store = get_store("kraken-api")
_API = "kraken-api"


def _load(filename, table):
    return read_seed_with_ctx(DATA_DIR / filename, _API, table)


def _strip_ctx(r):
    return {k: v for k, v in r.items() if not k.startswith("__")}


# ---------------------------------------------------------------------------
# Load + coerce
# ---------------------------------------------------------------------------

def _coerce_tickers(rows):
    out = []
    for r in rows:
        out.append({
            "pair": r["pair"],
            "altname": r["altname"],
            "ask": r["ask"],
            "bid": r["bid"],
            "last": r["last"],
            "volume": r["volume"],
            "high": r["high"],
            "low": r["low"],
            "open": r["open"],
        })
    return out


def _coerce_ohlc(rows):
    out = []
    for r in rows:
        out.append({
            "pair": r["pair"],
            "time": strict_int(r, "time"),
            "open": r["open"],
            "high": r["high"],
            "low": r["low"],
            "close": r["close"],
            "vwap": r["vwap"],
            "volume": r["volume"],
            "count": strict_int(r, "count"),
        })
    return out


def _coerce_pairs(rows):
    out = []
    for r in rows:
        out.append({
            "pair": r["pair"],
            "altname": r["altname"],
            "wsname": r["wsname"],
            "base": r["base"],
            "quote": r["quote"],
            "pair_decimals": strict_int(r, "pair_decimals"),
            "lot_decimals": strict_int(r, "lot_decimals"),
            "ordermin": r["ordermin"],
            "status": r["status"],
        })
    return out


def _coerce_assets(rows):
    out = []
    for r in rows:
        out.append({
            "asset": r["asset"],
            "altname": r["altname"],
            "aclass": r["aclass"],
            "decimals": strict_int(r, "decimals"),
            "display_decimals": strict_int(r, "display_decimals"),
        })
    return out


def _coerce_balances(rows):
    return [{"asset": r["asset"], "balance": r["balance"]} for r in rows]


_store.register("tickers", primary_key="pair",
                initial_loader=lambda: _coerce_tickers(_load("tickers.json", "tickers")))
_store.register("ohlc", primary_key="_pk",
                initial_loader=lambda: [
                    {**row, "_pk": f"{row['pair']}@{row['time']}"}
                    for row in _coerce_ohlc(_load("ohlc.json", "ohlc"))
                ])
_store.register("pairs", primary_key="pair",
                initial_loader=lambda: _coerce_pairs(_load("pairs.json", "pairs")))
_store.register("assets", primary_key="asset",
                initial_loader=lambda: _coerce_assets(_load("assets.json", "assets")))
_store.register("balances", primary_key="asset",
                initial_loader=lambda: _coerce_balances(_load("balances.json", "balances")))


def _rows(table):
    return _store.table(table).rows()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _envelope(result, error=None):
    return {"error": error or [], "result": result}


def _resolve_pair(pair):
    """Resolve a pair by canonical name or altname (case-insensitive)."""
    if not pair:
        return None
    p = pair.strip().upper()
    for t in _rows("tickers"):
        if t["pair"].upper() == p or t["altname"].upper() == p:
            return t["pair"]
    return None


# ---------------------------------------------------------------------------
# Public: Ticker
# ---------------------------------------------------------------------------

def get_ticker(pair=None):
    requested = [p.strip() for p in pair.split(",")] if pair else None
    if not requested:
        requested = [t["altname"] for t in _rows("tickers")]
    result = {}
    for req in requested:
        canonical = _resolve_pair(req)
        if not canonical:
            return {"error": f"Unknown asset pair: {req}"}
        t = next(t for t in _rows("tickers") if t["pair"] == canonical)
        result[canonical] = {
            "a": [t["ask"], "1", "1.000"],
            "b": [t["bid"], "1", "1.000"],
            "c": [t["last"], "0.10000000"],
            "v": [t["volume"], t["volume"]],
            "h": [t["high"], t["high"]],
            "l": [t["low"], t["low"]],
            "o": t["open"],
        }
    return _envelope(result)


# ---------------------------------------------------------------------------
# Public: OHLC
# ---------------------------------------------------------------------------

def get_ohlc(pair=None, interval=60):
    canonical = _resolve_pair(pair)
    if not canonical:
        return {"error": f"Unknown asset pair: {pair}"}
    candles = [c for c in _rows("ohlc") if c["pair"] == canonical]
    candles = sorted(candles, key=lambda c: c["time"])
    rows = [
        [c["time"], c["open"], c["high"], c["low"], c["close"],
         c["vwap"], c["volume"], c["count"]]
        for c in candles
    ]
    last = candles[-1]["time"] if candles else 0
    result = {canonical: rows, "last": last}
    return _envelope(result)


# ---------------------------------------------------------------------------
# Public: AssetPairs
# ---------------------------------------------------------------------------

def get_asset_pairs(pair=None):
    pairs = _rows("pairs")
    if pair:
        requested = {p.strip().upper() for p in pair.split(",")}
        pairs = [
            p for p in _rows("pairs")
            if p["pair"].upper() in requested or p["altname"].upper() in requested
        ]
        if not pairs:
            return {"error": f"Unknown asset pair: {pair}"}
    result = {}
    for p in pairs:
        result[p["pair"]] = {
            "altname": p["altname"],
            "wsname": p["wsname"],
            "aclass_base": "currency",
            "base": p["base"],
            "aclass_quote": "currency",
            "quote": p["quote"],
            "pair_decimals": p["pair_decimals"],
            "lot_decimals": p["lot_decimals"],
            "ordermin": p["ordermin"],
            "status": p["status"],
        }
    return _envelope(result)


# ---------------------------------------------------------------------------
# Public: Assets
# ---------------------------------------------------------------------------

def get_assets(asset=None):
    assets = _rows("assets")
    if asset:
        requested = {a.strip().upper() for a in asset.split(",")}
        assets = [
            a for a in _rows("assets")
            if a["asset"].upper() in requested or a["altname"].upper() in requested
        ]
        if not assets:
            return {"error": f"Unknown asset: {asset}"}
    result = {}
    for a in assets:
        result[a["asset"]] = {
            "aclass": a["aclass"],
            "altname": a["altname"],
            "decimals": a["decimals"],
            "display_decimals": a["display_decimals"],
        }
    return _envelope(result)


# ---------------------------------------------------------------------------
# Private: Balance
# ---------------------------------------------------------------------------

def get_balance():
    result = {b["asset"]: b["balance"] for b in _rows("balances")}
    return _envelope(result)

_store.eager_load()
