"""FastAPI server wrapping binance_data module as REST endpoints.

Mirrors a subset of the Binance Spot REST API (api.binance.com): symbol price
ticker, 24hr ticker, order book depth, klines (candles), and account balances.
"""

from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from typing import Optional

import binance_data
try:
    from tracking_middleware import install_tracker
    from admin_plane import install_admin_plane
except ModuleNotFoundError as _shared_plane_err:  # standalone run without the shared module on sys.path
    import logging as _logging
    _logging.error("SHARED PLANE MISSING - audit + admin disabled: %s", _shared_plane_err)
    def install_tracker(app):  # no-op fallback: audit endpoints disabled
        return None

    def install_admin_plane(app, store=None, one_shot_registry=None):
        return None

app = FastAPI(title="Binance API (Mock)", version="v3")
install_tracker(app)
install_admin_plane(app, store=binance_data._store)
@app.get("/health")
def health():
    return {"status": "ok"}


# --- Ticker price ---

@app.get("/api/v3/ticker/price")
def ticker_price(symbol: Optional[str] = None):
    result = binance_data.get_ticker_price(symbol=symbol)
    if isinstance(result, dict) and "error" in result:
        return JSONResponse(status_code=400, content=result)
    return result


# --- 24hr ticker ---

@app.get("/api/v3/ticker/24hr")
def ticker_24hr(symbol: Optional[str] = None):
    result = binance_data.get_ticker_24hr(symbol=symbol)
    if isinstance(result, dict) and "error" in result:
        return JSONResponse(status_code=400, content=result)
    return result


# --- Order book depth ---

@app.get("/api/v3/depth")
def depth(symbol: str, limit: int = Query(100, ge=1, le=5000)):
    result = binance_data.get_depth(symbol, limit=limit)
    if isinstance(result, dict) and "error" in result:
        return JSONResponse(status_code=400, content=result)
    return result


# --- Klines / candlesticks ---

@app.get("/api/v3/klines")
def klines(symbol: str, interval: str = "1h", limit: int = Query(500, ge=1, le=1000)):
    result = binance_data.get_klines(symbol, interval=interval, limit=limit)
    if isinstance(result, dict) and "error" in result:
        return JSONResponse(status_code=400, content=result)
    return result


# --- Account ---

@app.get("/api/v3/account")
def account():
    return binance_data.get_account()
