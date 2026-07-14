"""FastAPI server wrapping alpaca_data module as REST endpoints.

Implements a subset of the Alpaca Trading API v2 surface. Base path: /v2
Buy orders validate buying power; sell orders validate the held position.
"""

from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional

import alpaca_data
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

app = FastAPI(title="Alpaca Trading API (Mock)", version="v2")
install_tracker(app)
install_admin_plane(app, store=alpaca_data._store)
@app.get("/health")
def health():
    return {"status": "ok"}


# --- Account ---

@app.get("/v2/account")
def get_account():
    return alpaca_data.get_account()


# --- Positions ---

@app.get("/v2/positions")
def list_positions():
    return alpaca_data.list_positions()


@app.get("/v2/positions/{symbol}")
def get_position(symbol: str):
    result = alpaca_data.get_position(symbol)
    if isinstance(result, dict) and "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Orders ---

@app.get("/v2/orders")
def list_orders(status: Optional[str] = None):
    return alpaca_data.list_orders(status=status)


@app.get("/v2/orders/{order_id}")
def get_order(order_id: str):
    result = alpaca_data.get_order(order_id)
    if isinstance(result, dict) and "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


class OrderCreateBody(BaseModel):
    symbol: str
    qty: float
    side: str
    type: Optional[str] = "market"
    time_in_force: Optional[str] = "day"
    limit_price: Optional[float] = None


@app.post("/v2/orders", status_code=201)
def create_order(body: OrderCreateBody):
    result = alpaca_data.create_order(
        symbol=body.symbol, qty=body.qty, side=body.side, type=body.type,
        time_in_force=body.time_in_force, limit_price=body.limit_price,
    )
    if "error" in result:
        code = result.get("code", 0)
        status = 404 if str(code).startswith("404") else (403 if str(code).startswith("403") else 422)
        return JSONResponse(status_code=status, content=result)
    return result


@app.delete("/v2/orders/{order_id}")
def cancel_order(order_id: str):
    result = alpaca_data.cancel_order(order_id)
    if "error" in result:
        code = result.get("code", 0)
        status = 404 if str(code).startswith("404") else 422
        return JSONResponse(status_code=status, content=result)
    return result


# --- Assets ---

@app.get("/v2/assets")
def list_assets(status: Optional[str] = None, asset_class: Optional[str] = None):
    return alpaca_data.list_assets(status=status, asset_class=asset_class)


# --- Market data ---

@app.get("/v2/stocks/{symbol}/quotes/latest")
def get_latest_quote(symbol: str):
    result = alpaca_data.get_latest_quote(symbol)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result
