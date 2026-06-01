---
name: alpaca-api-connector
description: >
  Alpaca Trading API (Mock) mock HTTP API. Base URL is provided via the
  `ALPACA_API_URL` environment variable. 9 endpoint(s) across DELETE, GET, POST.
metadata: {"clawdbot":{"emoji":"🔌"}}
---

# Alpaca Trading API (Mock)

Mock HTTP API. **All requests go to the base URL in `$ALPACA_API_URL`.** Auth headers
are mocked (any token is accepted). Responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `ALPACA_API_URL` | Base URL for all requests (e.g. `http://alpaca-api:8043`) |

## Endpoints

| Method | Path |
|--------|------|
| GET | `/v2/account` |
| GET | `/v2/positions` |
| GET | `/v2/positions/{symbol}` |
| GET | `/v2/orders` |
| GET | `/v2/orders/{order_id}` |
| POST | `/v2/orders` |
| DELETE | `/v2/orders/{order_id}` |
| GET | `/v2/assets` |
| GET | `/v2/stocks/{symbol}/quotes/latest` |

## Usage

```bash
# GET example
curl -s "$ALPACA_API_URL/v2/account"

# POST example
curl -s -X POST "$ALPACA_API_URL/v2/account" -H 'Content-Type: application/json' -d '{}'
```

The audit log of every call the agent makes is available at
`$ALPACA_API_URL/audit/requests` (used for grading).
