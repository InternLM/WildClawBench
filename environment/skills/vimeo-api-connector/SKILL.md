---
name: vimeo-api-connector
description: >
  Vimeo API (Mock) mock HTTP API. Base URL is provided via the
  `VIMEO_API_URL` environment variable. 5 endpoint(s) across GET.
metadata: {"clawdbot":{"emoji":"🔌"}}
---

# Vimeo API (Mock)

Mock HTTP API. **All requests go to the base URL in `$VIMEO_API_URL`.** Auth headers
are mocked (any token is accepted). Responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `VIMEO_API_URL` | Base URL for all requests (e.g. `http://vimeo-api:8099`) |

## Endpoints

| Method | Path |
|--------|------|
| GET | `/me` |
| GET | `/me/videos` |
| GET | `/videos/{video_id}` |
| GET | `/users/{user_id}` |
| GET | `/users/{user_id}/videos` |

## Usage

```bash
# GET example
curl -s "$VIMEO_API_URL/me"

# POST example
curl -s -X POST "$VIMEO_API_URL/me" -H 'Content-Type: application/json' -d '{}'
```

The audit log of every call the agent makes is available at
`$VIMEO_API_URL/audit/requests` (used for grading).
