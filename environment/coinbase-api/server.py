"""FastAPI server wrapping coinbase_data module as REST endpoints.

Mirrors a subset of the Coinbase v2 API. Base path: /v2
"""

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel

import coinbase_data
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

app = FastAPI(title="Coinbase API (Mock)", version="2021-09-07")
install_tracker(app)
install_admin_plane(app, store=coinbase_data._store)
@app.get("/health")
def health():
    return {"status": "ok"}


# --- User ---

@app.get("/v2/user")
def get_user():
    return coinbase_data.get_user()


# --- Accounts ---

@app.get("/v2/accounts")
def list_accounts():
    return coinbase_data.list_accounts()


@app.get("/v2/accounts/{account_id}")
def get_account(account_id: str):
    result = coinbase_data.get_account(account_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Prices ---

@app.get("/v2/prices/{pair}/spot")
def get_spot_price(pair: str):
    result = coinbase_data.get_spot_price(pair)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Buys / Sells ---

class TradeBody(BaseModel):
    amount: str
    currency: str = None


@app.post("/v2/accounts/{account_id}/buys", status_code=201)
def create_buy(account_id: str, body: TradeBody):
    result = coinbase_data.create_buy(account_id, body.amount)
    if "error" in result:
        status = 404 if "not found" in result["error"] else 400
        return JSONResponse(status_code=status, content=result)
    return result


@app.post("/v2/accounts/{account_id}/sells", status_code=201)
def create_sell(account_id: str, body: TradeBody):
    result = coinbase_data.create_sell(account_id, body.amount)
    if "error" in result:
        status = 404 if "not found" in result["error"] else 400
        return JSONResponse(status_code=status, content=result)
    return result


# --- Transactions ---

@app.get("/v2/accounts/{account_id}/transactions")
def list_transactions(account_id: str):
    result = coinbase_data.list_transactions(account_id)
    if isinstance(result, dict) and "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result
