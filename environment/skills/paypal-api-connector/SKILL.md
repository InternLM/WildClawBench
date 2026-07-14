---
name: paypal-api-connector
description: >
  PayPal API (Mock) mock HTTP API. Base URL is provided via the
  `PAYPAL_API_URL` environment variable. 8 endpoint(s) across GET, POST.
metadata: {"clawdbot":{"emoji":"🔌"}}
---

# PayPal API (Mock)

Mock HTTP API. **All requests go to the base URL in `$PAYPAL_API_URL`.** Auth headers
are mocked (any token is accepted). Responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `PAYPAL_API_URL` | Base URL for all requests (e.g. `http://paypal-api:8042`) |

## Endpoints

| Method | Path |
|--------|------|
| POST | `/v2/checkout/orders` |
| GET | `/v2/checkout/orders/{order_id}` |
| POST | `/v2/checkout/orders/{order_id}/capture` |
| POST | `/v2/payments/refunds` |
| GET | `/v2/payments/refunds/{refund_id}` |
| GET | `/v2/invoicing/invoices` |
| POST | `/v2/invoicing/invoices` |
| POST | `/v1/payments/payouts` |

## Usage

```bash
# GET example
curl -s "$PAYPAL_API_URL/v2/checkout/orders"

# POST example
curl -s -X POST "$PAYPAL_API_URL/v2/checkout/orders" -H 'Content-Type: application/json' -d '{}'
```

The audit log of every call the agent makes is available at
`$PAYPAL_API_URL/audit/requests` (used for grading).
