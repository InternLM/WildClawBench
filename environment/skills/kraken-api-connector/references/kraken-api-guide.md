# Kraken API (Mock) Guide

Worked `curl` examples for every endpoint. **All requests target the base URL in `$KRAKEN_API_URL`.** Auth headers are mocked (any token is accepted) and responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `KRAKEN_API_URL` | Base URL for all requests |

## 0

```bash
curl -s "$KRAKEN_API_URL/0/public/Ticker"
curl -s "$KRAKEN_API_URL/0/public/OHLC"
curl -s "$KRAKEN_API_URL/0/public/AssetPairs"
curl -s "$KRAKEN_API_URL/0/public/Assets"
curl -s -X POST "$KRAKEN_API_URL/0/private/Balance" -H 'Content-Type: application/json' -d '{}'
```

The audit log of every call is available at `$KRAKEN_API_URL/audit/requests` (used for grading).
