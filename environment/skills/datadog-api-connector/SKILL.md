---
name: datadog-api-connector
description: >
  Datadog API (Mock) mock HTTP API. Base URL is provided via the
  `DATADOG_API_URL` environment variable. 10 endpoint(s) across GET, POST, PUT.
metadata: {"clawdbot":{"emoji":"🔌"}}
---

# Datadog API (Mock)

Mock HTTP API. **All requests go to the base URL in `$DATADOG_API_URL`.** Auth headers
are mocked (any token is accepted). Responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `DATADOG_API_URL` | Base URL for all requests (e.g. `http://datadog-api:8048`) |

## Endpoints

| Method | Path |
|--------|------|
| GET | `/api/v1/query` |
| GET | `/api/v1/monitor` |
| GET | `/api/v1/monitor/{monitor_id}` |
| POST | `/api/v1/monitor` |
| PUT | `/api/v1/monitor/{monitor_id}` |
| GET | `/api/v1/dashboard` |
| GET | `/api/v1/dashboard/{dashboard_id}` |
| GET | `/api/v1/events` |
| POST | `/api/v1/events` |
| GET | `/api/v1/hosts` |

## Usage

```bash
# GET example
curl -s "$DATADOG_API_URL/api/v1/query"

# POST example
curl -s -X POST "$DATADOG_API_URL/api/v1/query" -H 'Content-Type: application/json' -d '{}'
```

The audit log of every call the agent makes is available at
`$DATADOG_API_URL/audit/requests` (used for grading).
