---
name: doordash-api-connector
description: >
  DoorDash API (Mock) mock HTTP API. Base URL is provided via the
  `DOORDASH_API_URL` environment variable. 8 endpoint(s) across GET, POST.
metadata: {"clawdbot":{"emoji":"🔌"}}
---

# DoorDash API (Mock)

Mock HTTP API. **All requests go to the base URL in `$DOORDASH_API_URL`.** Auth headers
are mocked (any token is accepted). Responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `DOORDASH_API_URL` | Base URL for all requests (e.g. `http://doordash-api:8037`) |

## Endpoints

| Method | Path |
|--------|------|
| GET | `/v1/stores` |
| GET | `/v1/stores/{store_id}` |
| GET | `/v1/stores/{store_id}/menu` |
| POST | `/v1/carts` |
| GET | `/v1/carts/{cart_id}` |
| POST | `/v1/carts/{cart_id}/items` |
| POST | `/v1/carts/{cart_id}/checkout` |
| GET | `/v1/orders/{order_id}` |

## Usage

```bash
# GET example
curl -s "$DOORDASH_API_URL/v1/stores"

# POST example
curl -s -X POST "$DOORDASH_API_URL/v1/stores" -H 'Content-Type: application/json' -d '{}'
```

The audit log of every call the agent makes is available at
`$DOORDASH_API_URL/audit/requests` (used for grading).
