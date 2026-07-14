# DoorDash API (Mock) Guide

Worked `curl` examples for every endpoint. **All requests target the base URL in `$DOORDASH_API_URL`.** Auth headers are mocked (any token is accepted) and responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `DOORDASH_API_URL` | Base URL for all requests |

## Carts

```bash
curl -s -X POST "$DOORDASH_API_URL/v1/carts" -H 'Content-Type: application/json' -d '{}'
curl -s "$DOORDASH_API_URL/v1/carts/<cart_id>"
curl -s -X POST "$DOORDASH_API_URL/v1/carts/<cart_id>/items" -H 'Content-Type: application/json' -d '{}'
curl -s -X POST "$DOORDASH_API_URL/v1/carts/<cart_id>/checkout" -H 'Content-Type: application/json' -d '{}'
```

## Orders

```bash
curl -s "$DOORDASH_API_URL/v1/orders/<order_id>"
```

## Stores

```bash
curl -s "$DOORDASH_API_URL/v1/stores"
curl -s "$DOORDASH_API_URL/v1/stores/<store_id>"
curl -s "$DOORDASH_API_URL/v1/stores/<store_id>/menu"
```

The audit log of every call is available at `$DOORDASH_API_URL/audit/requests` (used for grading).
