# PayPal API (Mock) Guide

Worked `curl` examples for every endpoint. **All requests target the base URL in `$PAYPAL_API_URL`.** Auth headers are mocked (any token is accepted) and responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `PAYPAL_API_URL` | Base URL for all requests |

## Checkout

```bash
curl -s -X POST "$PAYPAL_API_URL/v2/checkout/orders" -H 'Content-Type: application/json' -d '{}'
curl -s "$PAYPAL_API_URL/v2/checkout/orders/<order_id>"
curl -s -X POST "$PAYPAL_API_URL/v2/checkout/orders/<order_id>/capture" -H 'Content-Type: application/json' -d '{}'
```

## Invoicing

```bash
curl -s "$PAYPAL_API_URL/v2/invoicing/invoices"
curl -s -X POST "$PAYPAL_API_URL/v2/invoicing/invoices" -H 'Content-Type: application/json' -d '{}'
```

## Payments

```bash
curl -s -X POST "$PAYPAL_API_URL/v2/payments/refunds" -H 'Content-Type: application/json' -d '{}'
curl -s "$PAYPAL_API_URL/v2/payments/refunds/<refund_id>"
curl -s -X POST "$PAYPAL_API_URL/v1/payments/payouts" -H 'Content-Type: application/json' -d '{}'
```

The audit log of every call is available at `$PAYPAL_API_URL/audit/requests` (used for grading).
