---
name: google-analytics-api-connector
description: >
  Google Analytics Data API (Mock) mock HTTP API. Base URL is provided via the
  `GOOGLE_ANALYTICS_API_URL` environment variable. 5 endpoint(s) across GET, POST.
metadata: {"clawdbot":{"emoji":"🔌"}}
---

# Google Analytics Data API (Mock)

Mock HTTP API. **All requests go to the base URL in `$GOOGLE_ANALYTICS_API_URL`.** Auth headers
are mocked (any token is accepted). Responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `GOOGLE_ANALYTICS_API_URL` | Base URL for all requests (e.g. `http://google-analytics-api:8068`) |

## Endpoints

| Method | Path |
|--------|------|
| POST | `/v1beta/properties/{property_id}:runReport` |
| POST | `/v1beta/properties/{property_id}:runRealtimeReport` |
| POST | `/v1beta/properties/{property_id}:batchRunReports` |
| GET | `/v1beta/properties/{property_id}/metadata` |
| GET | `/v1beta/properties/{property_id}` |

## Usage

```bash
# GET example
curl -s "$GOOGLE_ANALYTICS_API_URL/v1beta/properties/{property_id}:runReport"

# POST example
curl -s -X POST "$GOOGLE_ANALYTICS_API_URL/v1beta/properties/{property_id}:runReport" -H 'Content-Type: application/json' -d '{}'
```

The audit log of every call the agent makes is available at
`$GOOGLE_ANALYTICS_API_URL/audit/requests` (used for grading).
