# Stripe API (Mock) Guide

Worked `curl` examples for every endpoint. **All requests target the base URL in `$STRIPE_API_URL`.** Auth headers are mocked (any token is accepted) and responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `STRIPE_API_URL` | Base URL for all requests |

## Balance

```bash
curl -s "$STRIPE_API_URL/v1/balance"
```

## Charges

```bash
curl -s "$STRIPE_API_URL/v1/charges"
curl -s "$STRIPE_API_URL/v1/charges/<charge_id>"
curl -s -X POST "$STRIPE_API_URL/v1/charges" -H 'Content-Type: application/json' -d '{}'
```

## Customers

```bash
curl -s "$STRIPE_API_URL/v1/customers"
curl -s "$STRIPE_API_URL/v1/customers/<customer_id>"
curl -s -X POST "$STRIPE_API_URL/v1/customers" -H 'Content-Type: application/json' -d '{}'
```

## Invoices

```bash
curl -s "$STRIPE_API_URL/v1/invoices"
curl -s "$STRIPE_API_URL/v1/invoices/<invoice_id>"
curl -s -X POST "$STRIPE_API_URL/v1/invoices" -H 'Content-Type: application/json' -d '{}'
```

## Payment_Intents

```bash
curl -s -X POST "$STRIPE_API_URL/v1/payment_intents" -H 'Content-Type: application/json' -d '{}'
curl -s "$STRIPE_API_URL/v1/payment_intents/<pi_id>"
```

## Prices

```bash
curl -s "$STRIPE_API_URL/v1/prices"
```

## Products

```bash
curl -s "$STRIPE_API_URL/v1/products"
```

## Refunds

```bash
curl -s -X POST "$STRIPE_API_URL/v1/refunds" -H 'Content-Type: application/json' -d '{}'
```

## Subscriptions

```bash
curl -s "$STRIPE_API_URL/v1/subscriptions"
curl -s "$STRIPE_API_URL/v1/subscriptions/<sub_id>"
curl -s -X POST "$STRIPE_API_URL/v1/subscriptions" -H 'Content-Type: application/json' -d '{}'
```

The audit log of every call is available at `$STRIPE_API_URL/audit/requests` (used for grading).
