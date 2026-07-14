---
name: uber-api-connector
description: >
  Uber API (Mock) mock HTTP API. Base URL is provided via the
  `UBER_API_URL` environment variable. 9 endpoint(s) across DELETE, GET, POST.
metadata: {"clawdbot":{"emoji":"🔌"}}
---

# Uber API (Mock)

Mock HTTP API. **All requests go to the base URL in `$UBER_API_URL`.** Auth headers
are mocked (any token is accepted). Responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `UBER_API_URL` | Base URL for all requests (e.g. `http://uber-api:8036`) |

## Endpoints

| Method | Path |
|--------|------|
| GET | `/v1.2/products` |
| GET | `/v1.2/products/{product_id}` |
| GET | `/v1.2/estimates/price` |
| GET | `/v1.2/estimates/time` |
| POST | `/v1.2/requests` |
| GET | `/v1.2/requests/{request_id}` |
| DELETE | `/v1.2/requests/{request_id}` |
| GET | `/v1.2/history` |
| GET | `/v1.2/me` |

## Usage

```bash
# GET example
curl -s "$UBER_API_URL/v1.2/products"

# POST example
curl -s -X POST "$UBER_API_URL/v1.2/products" -H 'Content-Type: application/json' -d '{}'
```

The audit log of every call the agent makes is available at
`$UBER_API_URL/audit/requests` (used for grading).
