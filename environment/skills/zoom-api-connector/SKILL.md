---
name: zoom-api-connector
description: >
  Zoom API (Mock) mock HTTP API. Base URL is provided via the
  `ZOOM_API_URL` environment variable. 8 endpoint(s) across DELETE, GET, PATCH, POST.
metadata: {"clawdbot":{"emoji":"🔌"}}
---

# Zoom API (Mock)

Mock HTTP API. **All requests go to the base URL in `$ZOOM_API_URL`.** Auth headers
are mocked (any token is accepted). Responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `ZOOM_API_URL` | Base URL for all requests (e.g. `http://zoom-api:8028`) |

## Endpoints

| Method | Path |
|--------|------|
| GET | `/v2/users/me` |
| GET | `/v2/users/{user_id}/meetings` |
| POST | `/v2/users/{user_id}/meetings` |
| GET | `/v2/meetings/{meeting_id}` |
| PATCH | `/v2/meetings/{meeting_id}` |
| DELETE | `/v2/meetings/{meeting_id}` |
| GET | `/v2/meetings/{meeting_id}/recordings` |
| GET | `/v2/meetings/{meeting_id}/registrants` |

## Usage

```bash
# GET example
curl -s "$ZOOM_API_URL/v2/users/me"

# POST example
curl -s -X POST "$ZOOM_API_URL/v2/users/me" -H 'Content-Type: application/json' -d '{}'
```

The audit log of every call the agent makes is available at
`$ZOOM_API_URL/audit/requests` (used for grading).
