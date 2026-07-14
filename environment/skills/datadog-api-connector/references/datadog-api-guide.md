# Datadog API (Mock) Guide

Worked `curl` examples for every endpoint. **All requests target the base URL in `$DATADOG_API_URL`.** Auth headers are mocked (any token is accepted) and responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `DATADOG_API_URL` | Base URL for all requests |

## Api

```bash
curl -s "$DATADOG_API_URL/api/v1/query"
curl -s "$DATADOG_API_URL/api/v1/monitor"
curl -s "$DATADOG_API_URL/api/v1/monitor/<monitor_id>"
curl -s -X POST "$DATADOG_API_URL/api/v1/monitor" -H 'Content-Type: application/json' -d '{}'
curl -s -X PUT "$DATADOG_API_URL/api/v1/monitor/<monitor_id>" -H 'Content-Type: application/json' -d '{}'
curl -s "$DATADOG_API_URL/api/v1/dashboard"
curl -s "$DATADOG_API_URL/api/v1/dashboard/<dashboard_id>"
curl -s "$DATADOG_API_URL/api/v1/events"
curl -s -X POST "$DATADOG_API_URL/api/v1/events" -H 'Content-Type: application/json' -d '{}'
curl -s "$DATADOG_API_URL/api/v1/hosts"
```

The audit log of every call is available at `$DATADOG_API_URL/audit/requests` (used for grading).
