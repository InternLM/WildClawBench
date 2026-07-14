---
name: instacart-api-connector
description: >
  Instacart API (Mock) mock HTTP API. Base URL is provided via the
  `INSTACART_API_URL` environment variable. 13 endpoint(s) across GET, PATCH, POST.
metadata: {"clawdbot":{"emoji":"🔌"}}
---

# Instacart API (Mock)

Mock HTTP API. **All requests go to the base URL in `$INSTACART_API_URL`.** Auth headers
are mocked (any token is accepted). Responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `INSTACART_API_URL` | Base URL for all requests (e.g. `http://instacart-api:8012`) |

## Endpoints

| Method | Path |
|--------|------|
| GET | `/v1/users/me` |
| GET | `/v1/retailers` |
| GET | `/v1/retailers/{retailer_id}` |
| GET | `/v1/products` |
| GET | `/v1/products/{product_id}` |
| POST | `/v1/carts` |
| GET | `/v1/carts/{cart_id}` |
| POST | `/v1/carts/{cart_id}/items` |
| PATCH | `/v1/carts/{cart_id}/items/{product_id}` |
| POST | `/v1/carts/{cart_id}/checkout` |
| GET | `/v1/orders` |
| GET | `/v1/orders/{order_id}` |
| POST | `/v1/orders/{order_id}/cancel` |

## Usage

```bash
# GET example
curl -s "$INSTACART_API_URL/v1/users/me"

# POST example
curl -s -X POST "$INSTACART_API_URL/v1/users/me" -H 'Content-Type: application/json' -d '{}'
```

The audit log of every call the agent makes is available at
`$INSTACART_API_URL/audit/requests` (used for grading).
