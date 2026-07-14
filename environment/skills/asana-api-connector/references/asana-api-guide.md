# Asana API (Mock) Guide

Worked `curl` examples for every endpoint. **All requests target the base URL in `$ASANA_API_URL`.** Auth headers are mocked (any token is accepted) and responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `ASANA_API_URL` | Base URL for all requests |

## Api

```bash
curl -s "$ASANA_API_URL/api/1.0/workspaces"
curl -s "$ASANA_API_URL/api/1.0/users"
curl -s "$ASANA_API_URL/api/1.0/projects"
curl -s "$ASANA_API_URL/api/1.0/projects/<project_gid>"
curl -s "$ASANA_API_URL/api/1.0/projects/<project_gid>/sections"
curl -s "$ASANA_API_URL/api/1.0/projects/<project_gid>/tasks"
curl -s "$ASANA_API_URL/api/1.0/tasks"
curl -s -X POST "$ASANA_API_URL/api/1.0/tasks" -H 'Content-Type: application/json' -d '{}'
curl -s "$ASANA_API_URL/api/1.0/tasks/<task_gid>"
curl -s -X PUT "$ASANA_API_URL/api/1.0/tasks/<task_gid>" -H 'Content-Type: application/json' -d '{}'
```

The audit log of every call is available at `$ASANA_API_URL/audit/requests` (used for grading).
