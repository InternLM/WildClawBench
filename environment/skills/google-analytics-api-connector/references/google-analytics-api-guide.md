# Google Analytics Data API (Mock) Guide

Worked `curl` examples for every endpoint. **All requests target the base URL in `$GOOGLE_ANALYTICS_API_URL`.** Auth headers are mocked (any token is accepted) and responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `GOOGLE_ANALYTICS_API_URL` | Base URL for all requests |

## V1Beta

```bash
curl -s -X POST "$GOOGLE_ANALYTICS_API_URL/v1beta/properties/<property_id>:runReport" -H 'Content-Type: application/json' -d '{}'
curl -s -X POST "$GOOGLE_ANALYTICS_API_URL/v1beta/properties/<property_id>:runRealtimeReport" -H 'Content-Type: application/json' -d '{}'
curl -s -X POST "$GOOGLE_ANALYTICS_API_URL/v1beta/properties/<property_id>:batchRunReports" -H 'Content-Type: application/json' -d '{}'
curl -s "$GOOGLE_ANALYTICS_API_URL/v1beta/properties/<property_id>/metadata"
curl -s "$GOOGLE_ANALYTICS_API_URL/v1beta/properties/<property_id>"
```

The audit log of every call is available at `$GOOGLE_ANALYTICS_API_URL/audit/requests` (used for grading).
