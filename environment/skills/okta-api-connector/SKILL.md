---
name: okta-api-connector
description: >
  Okta API (Mock) mock HTTP API. Base URL is provided via the
  `OKTA_API_URL` environment variable. 10 endpoint(s) across GET, POST.
metadata: {"clawdbot":{"emoji":"🔌"}}
---

# Okta API (Mock)

Mock HTTP API. **All requests go to the base URL in `$OKTA_API_URL`.** Auth headers
are mocked (any token is accepted). Responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `OKTA_API_URL` | Base URL for all requests (e.g. `http://okta-api:8049`) |

## Endpoints

| Method | Path |
|--------|------|
| GET | `/api/v1/users` |
| GET | `/api/v1/users/{user_id}` |
| POST | `/api/v1/users` |
| POST | `/api/v1/users/{user_id}/lifecycle/activate` |
| POST | `/api/v1/users/{user_id}/lifecycle/suspend` |
| POST | `/api/v1/users/{user_id}/lifecycle/deactivate` |
| GET | `/api/v1/groups` |
| GET | `/api/v1/groups/{group_id}` |
| GET | `/api/v1/groups/{group_id}/users` |
| GET | `/api/v1/apps` |

## Usage

```bash
# GET example
curl -s "$OKTA_API_URL/api/v1/users"

# POST example
curl -s -X POST "$OKTA_API_URL/api/v1/users" -H 'Content-Type: application/json' -d '{}'
```

The audit log of every call the agent makes is available at
`$OKTA_API_URL/audit/requests` (used for grading).
