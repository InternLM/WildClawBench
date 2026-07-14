# Square API (Mock) Guide

Worked `curl` examples for every endpoint. **All requests target the base URL in `$SQUARE_API_URL`.** Auth headers are mocked (any token is accepted) and responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `SQUARE_API_URL` | Base URL for all requests |

## Catalog

```bash
curl -s "$SQUARE_API_URL/v2/catalog/list"
```

## Customers

```bash
curl -s "$SQUARE_API_URL/v2/customers"
curl -s "$SQUARE_API_URL/v2/customers/<customer_id>"
curl -s -X POST "$SQUARE_API_URL/v2/customers" -H 'Content-Type: application/json' -d '{}'
```

## Inventory

```bash
curl -s "$SQUARE_API_URL/v2/inventory/<catalog_object_id>"
```

## Merchants

```bash
curl -s "$SQUARE_API_URL/v2/merchants/me"
```

## Orders

```bash
curl -s -X POST "$SQUARE_API_URL/v2/orders" -H 'Content-Type: application/json' -d '{}'
curl -s "$SQUARE_API_URL/v2/orders/<order_id>"
```

## Payments

```bash
curl -s "$SQUARE_API_URL/v2/payments"
curl -s "$SQUARE_API_URL/v2/payments/<payment_id>"
curl -s -X POST "$SQUARE_API_URL/v2/payments" -H 'Content-Type: application/json' -d '{}'
```

## Refunds

```bash
curl -s -X POST "$SQUARE_API_URL/v2/refunds" -H 'Content-Type: application/json' -d '{}'
```

The audit log of every call is available at `$SQUARE_API_URL/audit/requests` (used for grading).
