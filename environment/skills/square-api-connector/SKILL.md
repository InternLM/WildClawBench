---
name: square-api-connector
description: >
  Square API (Mock) mock HTTP API. Base URL is provided via the
  `SQUARE_API_URL` environment variable. 12 endpoint(s) across GET, POST.
metadata: {"clawdbot":{"emoji":"🔌"}}
---

# Square API (Mock)

Mock HTTP API. **All requests go to the base URL in `$SQUARE_API_URL`.** Auth headers
are mocked (any token is accepted). Responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `SQUARE_API_URL` | Base URL for all requests (e.g. `http://square-api:8041`) |

## Endpoints

| Method | Path |
|--------|------|
| GET | `/v2/merchants/me` |
| GET | `/v2/payments` |
| GET | `/v2/payments/{payment_id}` |
| POST | `/v2/payments` |
| POST | `/v2/refunds` |
| GET | `/v2/customers` |
| GET | `/v2/customers/{customer_id}` |
| POST | `/v2/customers` |
| GET | `/v2/catalog/list` |
| POST | `/v2/orders` |
| GET | `/v2/orders/{order_id}` |
| GET | `/v2/inventory/{catalog_object_id}` |

## Usage

```bash
# GET example
curl -s "$SQUARE_API_URL/v2/merchants/me"

# POST example
curl -s -X POST "$SQUARE_API_URL/v2/merchants/me" -H 'Content-Type: application/json' -d '{}'
```

The audit log of every call the agent makes is available at
`$SQUARE_API_URL/audit/requests` (used for grading).
