# UPS API (Mock) Guide

Worked `curl` examples for every endpoint. **All requests target the base URL in `$UPS_API_URL`.** Auth headers are mocked (any token is accepted) and responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `UPS_API_URL` | Base URL for all requests |

## Api

```bash
curl -s -X POST "$UPS_API_URL/api/rating/v1/Rate" -H 'Content-Type: application/json' -d '{}'
curl -s -X POST "$UPS_API_URL/api/shipments/v1/ship" -H 'Content-Type: application/json' -d '{}'
curl -s "$UPS_API_URL/api/track/v1/details/<tracking_number>"
```

The audit log of every call is available at `$UPS_API_URL/audit/requests` (used for grading).
