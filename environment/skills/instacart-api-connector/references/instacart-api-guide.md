# Instacart API (Mock) Guide

Worked `curl` examples for every endpoint. **All requests target the base URL in `$INSTACART_API_URL`.** Auth headers are mocked (any token is accepted) and responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `INSTACART_API_URL` | Base URL for all requests |

## Carts

```bash
curl -s -X POST "$INSTACART_API_URL/v1/carts" -H 'Content-Type: application/json' -d '{}'
curl -s "$INSTACART_API_URL/v1/carts/<cart_id>"
curl -s -X POST "$INSTACART_API_URL/v1/carts/<cart_id>/items" -H 'Content-Type: application/json' -d '{}'
curl -s -X PATCH "$INSTACART_API_URL/v1/carts/<cart_id>/items/<product_id>" -H 'Content-Type: application/json' -d '{}'
curl -s -X POST "$INSTACART_API_URL/v1/carts/<cart_id>/checkout" -H 'Content-Type: application/json' -d '{}'
```

## Orders

```bash
curl -s "$INSTACART_API_URL/v1/orders"
curl -s "$INSTACART_API_URL/v1/orders/<order_id>"
curl -s -X POST "$INSTACART_API_URL/v1/orders/<order_id>/cancel" -H 'Content-Type: application/json' -d '{}'
```

## Products

```bash
curl -s "$INSTACART_API_URL/v1/products"
curl -s "$INSTACART_API_URL/v1/products/<product_id>"
```

## Retailers

```bash
curl -s "$INSTACART_API_URL/v1/retailers"
curl -s "$INSTACART_API_URL/v1/retailers/<retailer_id>"
```

## Users

```bash
curl -s "$INSTACART_API_URL/v1/users/me"
```

The audit log of every call is available at `$INSTACART_API_URL/audit/requests` (used for grading).
