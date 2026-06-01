---
name: woocommerce-api-connector
description: >
  WooCommerce REST API v3 (Mock) mock HTTP API. Base URL is provided via the
  `WOOCOMMERCE_API_URL` environment variable. 6 endpoint(s) across GET, POST.
metadata: {"clawdbot":{"emoji":"🔌"}}
---

# WooCommerce REST API v3 (Mock)

Mock HTTP API. **All requests go to the base URL in `$WOOCOMMERCE_API_URL`.** Auth headers
are mocked (any token is accepted). Responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `WOOCOMMERCE_API_URL` | Base URL for all requests (e.g. `http://woocommerce-api:8085`) |

## Endpoints

| Method | Path |
|--------|------|
| GET | `/wp-json/wc/v3/products` |
| GET | `/wp-json/wc/v3/products/{product_id}` |
| GET | `/wp-json/wc/v3/orders` |
| GET | `/wp-json/wc/v3/orders/{order_id}` |
| POST | `/wp-json/wc/v3/orders` |
| GET | `/wp-json/wc/v3/customers` |

## Usage

```bash
# GET example
curl -s "$WOOCOMMERCE_API_URL/wp-json/wc/v3/products"

# POST example
curl -s -X POST "$WOOCOMMERCE_API_URL/wp-json/wc/v3/products" -H 'Content-Type: application/json' -d '{}'
```

The audit log of every call the agent makes is available at
`$WOOCOMMERCE_API_URL/audit/requests` (used for grading).
