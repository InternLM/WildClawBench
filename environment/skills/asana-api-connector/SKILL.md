---
name: asana-api-connector
description: >
  Asana API (Mock) mock HTTP API. Base URL is provided via the
  `ASANA_API_URL` environment variable. 10 endpoint(s) across GET, POST, PUT.
metadata: {"clawdbot":{"emoji":"🔌"}}
---

# Asana API (Mock)

Mock HTTP API. **All requests go to the base URL in `$ASANA_API_URL`.** Auth headers
are mocked (any token is accepted). Responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `ASANA_API_URL` | Base URL for all requests (e.g. `http://asana-api:8031`) |

## Endpoints

| Method | Path |
|--------|------|
| GET | `/api/1.0/workspaces` |
| GET | `/api/1.0/users` |
| GET | `/api/1.0/projects` |
| GET | `/api/1.0/projects/{project_gid}` |
| GET | `/api/1.0/projects/{project_gid}/sections` |
| GET | `/api/1.0/projects/{project_gid}/tasks` |
| GET | `/api/1.0/tasks` |
| POST | `/api/1.0/tasks` |
| GET | `/api/1.0/tasks/{task_gid}` |
| PUT | `/api/1.0/tasks/{task_gid}` |

## Usage

```bash
# GET example
curl -s "$ASANA_API_URL/api/1.0/workspaces"

# POST example
curl -s -X POST "$ASANA_API_URL/api/1.0/workspaces" -H 'Content-Type: application/json' -d '{}'
```

The audit log of every call the agent makes is available at
`$ASANA_API_URL/audit/requests` (used for grading).
