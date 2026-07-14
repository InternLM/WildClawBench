# ServiceNow Table API (Mock) Guide

Worked `curl` examples for every endpoint. **All requests target the base URL in `$SERVICENOW_API_URL`.** Auth headers are mocked (any token is accepted) and responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `SERVICENOW_API_URL` | Base URL for all requests |

## Api

```bash
curl -s "$SERVICENOW_API_URL/api/now/table/incident"
curl -s "$SERVICENOW_API_URL/api/now/table/incident/<sys_id>"
curl -s -X POST "$SERVICENOW_API_URL/api/now/table/incident" -H 'Content-Type: application/json' -d '{}'
curl -s -X PATCH "$SERVICENOW_API_URL/api/now/table/incident/<sys_id>" -H 'Content-Type: application/json' -d '{}'
curl -s "$SERVICENOW_API_URL/api/now/table/change_request"
curl -s "$SERVICENOW_API_URL/api/now/table/change_request/<sys_id>"
curl -s "$SERVICENOW_API_URL/api/now/table/problem"
curl -s "$SERVICENOW_API_URL/api/now/table/problem/<sys_id>"
curl -s "$SERVICENOW_API_URL/api/now/table/sys_user"
curl -s "$SERVICENOW_API_URL/api/now/table/sys_user/<sys_id>"
```

The audit log of every call is available at `$SERVICENOW_API_URL/audit/requests` (used for grading).
