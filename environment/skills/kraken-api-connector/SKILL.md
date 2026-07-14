---
name: kraken-api-connector
description: >
  Kraken API (Mock) mock HTTP API. Base URL is provided via the
  `KRAKEN_API_URL` environment variable. 5 endpoint(s) across GET, POST.
metadata: {"clawdbot":{"emoji":"🔌"}}
---

# Kraken API (Mock)

Mock HTTP API. **All requests go to the base URL in `$KRAKEN_API_URL`.** Auth headers
are mocked (any token is accepted). Responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `KRAKEN_API_URL` | Base URL for all requests (e.g. `http://kraken-api:8098`) |

## Endpoints

| Method | Path |
|--------|------|
| GET | `/0/public/Ticker` |
| GET | `/0/public/OHLC` |
| GET | `/0/public/AssetPairs` |
| GET | `/0/public/Assets` |
| POST | `/0/private/Balance` |

## Usage

```bash
# GET example
curl -s "$KRAKEN_API_URL/0/public/Ticker"

# POST example
curl -s -X POST "$KRAKEN_API_URL/0/public/Ticker" -H 'Content-Type: application/json' -d '{}'
```

The audit log of every call the agent makes is available at
`$KRAKEN_API_URL/audit/requests` (used for grading).
