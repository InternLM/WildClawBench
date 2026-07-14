---
name: binance-api-connector
description: >
  Binance API (Mock) mock HTTP API. Base URL is provided via the
  `BINANCE_API_URL` environment variable. 5 endpoint(s) across GET.
metadata: {"clawdbot":{"emoji":"🔌"}}
---

# Binance API (Mock)

Mock HTTP API. **All requests go to the base URL in `$BINANCE_API_URL`.** Auth headers
are mocked (any token is accepted). Responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `BINANCE_API_URL` | Base URL for all requests (e.g. `http://binance-api:8097`) |

## Endpoints

| Method | Path |
|--------|------|
| GET | `/api/v3/ticker/price` |
| GET | `/api/v3/ticker/24hr` |
| GET | `/api/v3/depth` |
| GET | `/api/v3/klines` |
| GET | `/api/v3/account` |

## Usage

```bash
# GET example
curl -s "$BINANCE_API_URL/api/v3/ticker/price"

# POST example
curl -s -X POST "$BINANCE_API_URL/api/v3/ticker/price" -H 'Content-Type: application/json' -d '{}'
```

The audit log of every call the agent makes is available at
`$BINANCE_API_URL/audit/requests` (used for grading).
