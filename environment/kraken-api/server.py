"""FastAPI server wrapping kraken_data module as REST endpoints.

Mirrors a subset of the Kraken REST API (api.kraken.com): public market data
under /0/public and a private account Balance under /0/private. All responses
use Kraken's standard envelope: {"error": [], "result": {...}}.
"""

from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from typing import Optional

import kraken_data
try:
    from tracking_middleware import install_tracker
except ModuleNotFoundError:  # standalone run without the shared module on sys.path
    def install_tracker(app):  # no-op fallback: audit endpoints disabled
        return None

app = FastAPI(title="Kraken API (Mock)", version="0")
install_tracker(app)


@app.get("/health")
def health():
    return {"status": "ok"}


def _wrap(result):
    if isinstance(result, dict) and set(result.keys()) == {"error"} and isinstance(result["error"], str):
        return JSONResponse(status_code=404, content={"error": [result["error"]], "result": {}})
    return result


# --- Public market data ---

@app.get("/0/public/Ticker")
def ticker(pair: Optional[str] = Query(default=None)):
    return _wrap(kraken_data.get_ticker(pair=pair))


@app.get("/0/public/OHLC")
def ohlc(pair: str = Query(...), interval: int = Query(default=60)):
    return _wrap(kraken_data.get_ohlc(pair=pair, interval=interval))


@app.get("/0/public/AssetPairs")
def asset_pairs(pair: Optional[str] = Query(default=None)):
    return _wrap(kraken_data.get_asset_pairs(pair=pair))


@app.get("/0/public/Assets")
def assets(asset: Optional[str] = Query(default=None)):
    return _wrap(kraken_data.get_assets(asset=asset))


# --- Private account data ---

@app.post("/0/private/Balance")
def balance():
    return kraken_data.get_balance()
