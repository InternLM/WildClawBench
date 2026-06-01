---
name: coinbase-api-connector
description: >
  Coinbase API (Mock) mock HTTP API. Base URL is provided via the
  `COINBASE_API_URL` environment variable. 7 endpoint(s) across GET, POST.
metadata: {"clawdbot":{"emoji":"🔌"}}
---

# Coinbase API (Mock)

Mock HTTP API. **All requests go to the base URL in `$COINBASE_API_URL`.** Auth headers
are mocked (any token is accepted). Responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `COINBASE_API_URL` | Base URL for all requests (e.g. `http://coinbase-api:8023`) |

## Endpoints

| Method | Path |
|--------|------|
| GET | `/v2/user` |
| GET | `/v2/accounts` |
| GET | `/v2/accounts/{account_id}` |
| GET | `/v2/prices/{pair}/spot` |
| POST | `/v2/accounts/{account_id}/buys` |
| POST | `/v2/accounts/{account_id}/sells` |
| GET | `/v2/accounts/{account_id}/transactions` |

## Usage

```bash
# GET example
curl -s "$COINBASE_API_URL/v2/user"

# POST example
curl -s -X POST "$COINBASE_API_URL/v2/user" -H 'Content-Type: application/json' -d '{}'
```

The audit log of every call the agent makes is available at
`$COINBASE_API_URL/audit/requests` (used for grading).
