# Binance API (Mock) Guide

Worked `curl` examples for every endpoint. **All requests target the base URL in `$BINANCE_API_URL`.** Auth headers are mocked (any token is accepted) and responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `BINANCE_API_URL` | Base URL for all requests |

## Api

```bash
curl -s "$BINANCE_API_URL/api/v3/ticker/price"
curl -s "$BINANCE_API_URL/api/v3/ticker/24hr"
curl -s "$BINANCE_API_URL/api/v3/depth"
curl -s "$BINANCE_API_URL/api/v3/klines"
curl -s "$BINANCE_API_URL/api/v3/account"
```

The audit log of every call is available at `$BINANCE_API_URL/audit/requests` (used for grading).
