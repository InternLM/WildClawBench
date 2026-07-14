---
name: box-api-connector
description: >
  Box API (Mock) mock HTTP API. Base URL is provided via the
  `BOX_API_URL` environment variable. 5 endpoint(s) across GET.
metadata: {"clawdbot":{"emoji":"🔌"}}
---

# Box API (Mock)

Mock HTTP API. **All requests go to the base URL in `$BOX_API_URL`.** Auth headers
are mocked (any token is accepted). Responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `BOX_API_URL` | Base URL for all requests (e.g. `http://box-api:8083`) |

## Endpoints

| Method | Path |
|--------|------|
| GET | `/2.0/users/me` |
| GET | `/2.0/folders/{folder_id}` |
| GET | `/2.0/folders/{folder_id}/items` |
| GET | `/2.0/files/{file_id}` |
| GET | `/2.0/search` |

## Usage

```bash
# GET example
curl -s "$BOX_API_URL/2.0/users/me"

# POST example
curl -s -X POST "$BOX_API_URL/2.0/users/me" -H 'Content-Type: application/json' -d '{}'
```

The audit log of every call the agent makes is available at
`$BOX_API_URL/audit/requests` (used for grading).
