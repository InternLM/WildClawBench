---
name: stripe-api-connector
description: >
  Stripe API (Mock) mock HTTP API. Base URL is provided via the
  `STRIPE_API_URL` environment variable. 18 endpoint(s) across GET, POST.
metadata: {"clawdbot":{"emoji":"🔌"}}
---

# Stripe API (Mock)

Mock HTTP API. **All requests go to the base URL in `$STRIPE_API_URL`.** Auth headers
are mocked (any token is accepted). Responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `STRIPE_API_URL` | Base URL for all requests (e.g. `http://stripe-api:8021`) |

## Endpoints

| Method | Path |
|--------|------|
| GET | `/v1/customers` |
| GET | `/v1/customers/{customer_id}` |
| POST | `/v1/customers` |
| GET | `/v1/products` |
| GET | `/v1/prices` |
| POST | `/v1/payment_intents` |
| GET | `/v1/payment_intents/{pi_id}` |
| GET | `/v1/charges` |
| GET | `/v1/charges/{charge_id}` |
| POST | `/v1/charges` |
| POST | `/v1/refunds` |
| GET | `/v1/invoices` |
| GET | `/v1/invoices/{invoice_id}` |
| POST | `/v1/invoices` |
| GET | `/v1/subscriptions` |
| GET | `/v1/subscriptions/{sub_id}` |
| POST | `/v1/subscriptions` |
| GET | `/v1/balance` |

## Usage

```bash
# GET example
curl -s "$STRIPE_API_URL/v1/customers"

# POST example
curl -s -X POST "$STRIPE_API_URL/v1/customers" -H 'Content-Type: application/json' -d '{}'
```

The audit log of every call the agent makes is available at
`$STRIPE_API_URL/audit/requests` (used for grading).
