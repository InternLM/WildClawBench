# FedEx API (Mock) Guide

Worked `curl` examples for every endpoint. **All requests target the base URL in `$FEDEX_API_URL`.** Auth headers are mocked (any token is accepted) and responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `FEDEX_API_URL` | Base URL for all requests |

## Rate

```bash
curl -s -X POST "$FEDEX_API_URL/rate/v1/rates/quotes" -H 'Content-Type: application/json' -d '{}'
```

## Ship

```bash
curl -s -X POST "$FEDEX_API_URL/ship/v1/shipments" -H 'Content-Type: application/json' -d '{}'
```

## Track

```bash
curl -s -X POST "$FEDEX_API_URL/track/v1/trackingnumbers" -H 'Content-Type: application/json' -d '{}'
```

The audit log of every call is available at `$FEDEX_API_URL/audit/requests` (used for grading).
