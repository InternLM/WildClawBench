# Kraken Mock API — Test Results

Base URL: `http://localhost:8098` (in docker-compose: `http://kraken-api:8098`)

## Endpoints covered

| Method | Path                       | Status  |
|--------|----------------------------|---------|
| GET    | /health                    | 200     |
| GET    | /0/public/Ticker           | 200/404 |
| GET    | /0/public/OHLC             | 200/404 |
| GET    | /0/public/AssetPairs       | 200/404 |
| GET    | /0/public/Assets           | 200/404 |
| POST   | /0/private/Balance         | 200     |

## Seed data summary

- Tickers: 9 pairs (XBTUSD, ETHUSD, XRPUSD, SOLUSD, ADAUSD, DOTUSD, XBTEUR, LINKUSD, MATICUSD) with ask/bid/last/volume/high/low/open.
- OHLC: 10 candles across XBTUSD, ETHUSD, SOLUSD, ADAUSD (time, OHLC, vwap, volume, count).
- Asset pairs: 9 trading pairs with base/quote, decimals, ordermin, status.
- Assets: 10 currencies (XBT, ETH, USD, EUR, XRP, SOL, ADA, DOT, LINK, MATIC).
- Balances: 6 account asset balances (USD, XBT, ETH, SOL, ADA, USDT).

## Notes

- Every response uses Kraken's envelope: `{"error": [], "result": {...}}`.
- `pair` accepts canonical names (XXBTZUSD) or altnames (XBTUSD), comma-separated
  for `Ticker` to request multiple pairs. Unknown pairs return a 404 with the
  error list populated, e.g. `{"error": ["Unknown asset pair: FOO"], "result": {}}`.
- `OHLC` accepts an `interval` query param (minutes); seed candles are returned
  sorted by time with a `last` cursor.
- `/0/private/Balance` is a POST (Kraken private endpoints are POST); the mock
  ignores auth/nonce and returns the seeded account balances.
- Mutations are held in process memory and reset on container restart (this mock is read-only).
