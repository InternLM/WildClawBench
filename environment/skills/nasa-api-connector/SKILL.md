---
name: nasa-api-connector
description: >
  NASA Open API (Mock) mock HTTP API. Base URL is provided via the
  `NASA_API_URL` environment variable. 6 endpoint(s) across GET.
metadata: {"clawdbot":{"emoji":"🔌"}}
---

# NASA Open API (Mock)

Mock HTTP API. **All requests go to the base URL in `$NASA_API_URL`.** Auth headers
are mocked (any token is accepted). Responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `NASA_API_URL` | Base URL for all requests (e.g. `http://nasa-api:8077`) |

## Endpoints

| Method | Path |
|--------|------|
| GET | `/planetary/apod` |
| GET | `/mars-photos/api/v1/rovers/{rover}/photos` |
| GET | `/mars-photos/api/v1/rovers/{rover}` |
| GET | `/neo/rest/v1/feed` |
| GET | `/neo/rest/v1/neo/{neo_id}` |
| GET | `/EPIC/api/natural` |

## Usage

```bash
# GET example
curl -s "$NASA_API_URL/planetary/apod"

# POST example
curl -s -X POST "$NASA_API_URL/planetary/apod" -H 'Content-Type: application/json' -d '{}'
```

The audit log of every call the agent makes is available at
`$NASA_API_URL/audit/requests` (used for grading).
