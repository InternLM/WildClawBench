# Uber API (Mock) Guide

Worked `curl` examples for every endpoint. **All requests target the base URL in `$UBER_API_URL`.** Auth headers are mocked (any token is accepted) and responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `UBER_API_URL` | Base URL for all requests |

## V1.2

```bash
curl -s "$UBER_API_URL/v1.2/products"
curl -s "$UBER_API_URL/v1.2/products/<product_id>"
curl -s "$UBER_API_URL/v1.2/estimates/price"
curl -s "$UBER_API_URL/v1.2/estimates/time"
curl -s -X POST "$UBER_API_URL/v1.2/requests" -H 'Content-Type: application/json' -d '{}'
curl -s "$UBER_API_URL/v1.2/requests/<request_id>"
curl -s -X DELETE "$UBER_API_URL/v1.2/requests/<request_id>"
curl -s "$UBER_API_URL/v1.2/history"
curl -s "$UBER_API_URL/v1.2/me"
```

The audit log of every call is available at `$UBER_API_URL/audit/requests` (used for grading).
