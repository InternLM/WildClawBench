# BigCommerce API (Mock) Guide

Worked `curl` examples for every endpoint. **All requests target the base URL in `$BIGCOMMERCE_API_URL`.** Auth headers are mocked (any token is accepted) and responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `BIGCOMMERCE_API_URL` | Base URL for all requests |

## Catalog

```bash
curl -s "$BIGCOMMERCE_API_URL/v3/catalog/products"
curl -s "$BIGCOMMERCE_API_URL/v3/catalog/products/<product_id>"
```

## Customers

```bash
curl -s "$BIGCOMMERCE_API_URL/v3/customers"
```

## Orders

```bash
curl -s "$BIGCOMMERCE_API_URL/v2/orders"
curl -s "$BIGCOMMERCE_API_URL/v2/orders/<order_id>"
curl -s -X POST "$BIGCOMMERCE_API_URL/v2/orders" -H 'Content-Type: application/json' -d '{}'
```

The audit log of every call is available at `$BIGCOMMERCE_API_URL/audit/requests` (used for grading).
