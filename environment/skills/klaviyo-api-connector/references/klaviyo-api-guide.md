# Klaviyo API (Mock) Guide

Worked `curl` examples for every endpoint. **All requests target the base URL in `$KLAVIYO_API_URL`.** Auth headers are mocked (any token is accepted) and responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `KLAVIYO_API_URL` | Base URL for all requests |

## Api

```bash
curl -s "$KLAVIYO_API_URL/api/profiles"
curl -s "$KLAVIYO_API_URL/api/profiles/<profile_id>"
curl -s -X POST "$KLAVIYO_API_URL/api/profiles" -H 'Content-Type: application/json' -d '{}'
curl -s "$KLAVIYO_API_URL/api/lists"
curl -s "$KLAVIYO_API_URL/api/campaigns"
```

The audit log of every call is available at `$KLAVIYO_API_URL/audit/requests` (used for grading).
