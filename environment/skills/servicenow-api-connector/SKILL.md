---
name: servicenow-api-connector
description: >
  ServiceNow Table API (Mock) mock HTTP API. Base URL is provided via the
  `SERVICENOW_API_URL` environment variable. 10 endpoint(s) across GET, PATCH, POST.
metadata: {"clawdbot":{"emoji":"🔌"}}
---

# ServiceNow Table API (Mock)

Mock HTTP API. **All requests go to the base URL in `$SERVICENOW_API_URL`.** Auth headers
are mocked (any token is accepted). Responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `SERVICENOW_API_URL` | Base URL for all requests (e.g. `http://servicenow-api:8071`) |

## Endpoints

| Method | Path |
|--------|------|
| GET | `/api/now/table/incident` |
| GET | `/api/now/table/incident/{sys_id}` |
| POST | `/api/now/table/incident` |
| PATCH | `/api/now/table/incident/{sys_id}` |
| GET | `/api/now/table/change_request` |
| GET | `/api/now/table/change_request/{sys_id}` |
| GET | `/api/now/table/problem` |
| GET | `/api/now/table/problem/{sys_id}` |
| GET | `/api/now/table/sys_user` |
| GET | `/api/now/table/sys_user/{sys_id}` |

## Usage

```bash
# GET example
curl -s "$SERVICENOW_API_URL/api/now/table/incident"

# POST example
curl -s -X POST "$SERVICENOW_API_URL/api/now/table/incident" -H 'Content-Type: application/json' -d '{}'
```

The audit log of every call the agent makes is available at
`$SERVICENOW_API_URL/audit/requests` (used for grading).
