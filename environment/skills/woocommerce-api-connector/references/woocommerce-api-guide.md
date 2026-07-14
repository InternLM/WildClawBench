# WooCommerce REST API v3 (Mock) Guide

Worked `curl` examples for every endpoint. **All requests target the base URL in `$WOOCOMMERCE_API_URL`.** Auth headers are mocked (any token is accepted) and responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `WOOCOMMERCE_API_URL` | Base URL for all requests |

## Wp Json

```bash
curl -s "$WOOCOMMERCE_API_URL/wp-json/wc/v3/products"
curl -s "$WOOCOMMERCE_API_URL/wp-json/wc/v3/products/<product_id>"
curl -s "$WOOCOMMERCE_API_URL/wp-json/wc/v3/orders"
curl -s "$WOOCOMMERCE_API_URL/wp-json/wc/v3/orders/<order_id>"
curl -s -X POST "$WOOCOMMERCE_API_URL/wp-json/wc/v3/orders" -H 'Content-Type: application/json' -d '{}'
curl -s "$WOOCOMMERCE_API_URL/wp-json/wc/v3/customers"
```

The audit log of every call is available at `$WOOCOMMERCE_API_URL/audit/requests` (used for grading).
