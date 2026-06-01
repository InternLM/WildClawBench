# Binance Mock API — Test Results

Base URL: `http://localhost:8097` (in docker-compose: `http://binance-api:8097`)

## Endpoints covered

| Method | Path                        | Status  |
|--------|-----------------------------|---------|
| GET    | /health                     | 200     |
| GET    | /api/v3/ticker/price        | 200/400 |
| GET    | /api/v3/ticker/24hr         | 200/400 |
| GET    | /api/v3/depth               | 200/400 |
| GET    | /api/v3/klines              | 200/400 |
| GET    | /api/v3/account             | 200     |

## Seed data summary

- Prices: 10 symbols (BTCUSDT, ETHUSDT, BNBUSDT, SOLUSDT, XRPUSDT, ADAUSDT, DOGEUSDT, MATICUSDT, DOTUSDT, LTCUSDT) with price, 24h change, high/low, volume.
- Klines: 11 candles for BTCUSDT/ETHUSDT at 1h and 1d intervals (open/high/low/close/volume, ms open/close times in 2026-05).
- Balances: 8 spot assets with free and locked amounts.
- Depth: 16 order-book levels (bids/asks) across BTCUSDT and ETHUSDT.

## Notes

- `GET /api/v3/ticker/price` returns one object when `symbol=` is given, else an array of all symbols.
- `GET /api/v3/ticker/24hr` mirrors the price ticker with priceChange/percent, high/low, volume.
- `GET /api/v3/depth` returns `bids`/`asks` as `[price, qty]` string pairs (bids high→low, asks low→high), capped by `limit`.
- `GET /api/v3/klines` returns candles as Binance-style arrays; filtered by `symbol` and `interval`.
- Numeric fields are returned as strings, matching the real Binance API.
- Unknown symbols return `{"code": -1121, "error": "Invalid symbol."}` with HTTP 400.
