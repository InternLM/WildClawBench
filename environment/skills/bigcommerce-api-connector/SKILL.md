---
name: bigcommerce-api-connector
description: >
  BigCommerce API (Mock) mock HTTP API. Base URL is provided via the
  `BIGCOMMERCE_API_URL` environment variable. 6 endpoint(s) across GET, POST.
metadata: {"clawdbot":{"emoji":"🔌"}}
---

# BigCommerce API (Mock)

Mock HTTP API. **All requests go to the base URL in `$BIGCOMMERCE_API_URL`.** Auth headers
are mocked (any token is accepted). Responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `BIGCOMMERCE_API_URL` | Base URL for all requests (e.g. `http://bigcommerce-api:8084`) |

## Endpoints

| Method | Path |
|--------|------|
| GET | `/v3/catalog/products` |
| GET | `/v3/catalog/products/{product_id}` |
| GET | `/v2/orders` |
| GET | `/v2/orders/{order_id}` |
| POST | `/v2/orders` |
| GET | `/v3/customers` |

## Usage

```bash
# GET example
curl -s "$BIGCOMMERCE_API_URL/v3/catalog/products"

# POST example
curl -s -X POST "$BIGCOMMERCE_API_URL/v3/catalog/products" -H 'Content-Type: application/json' -d '{}'
```

The audit log of every call the agent makes is available at
`$BIGCOMMERCE_API_URL/audit/requests` (used for grading).
