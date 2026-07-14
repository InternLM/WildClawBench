---
name: figma-api-connector
description: >
  Figma API (Mock) mock HTTP API. Base URL is provided via the
  `FIGMA_API_URL` environment variable. 8 endpoint(s) across GET, POST.
metadata: {"clawdbot":{"emoji":"🔌"}}
---

# Figma API (Mock)

Mock HTTP API. **All requests go to the base URL in `$FIGMA_API_URL`.** Auth headers
are mocked (any token is accepted). Responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `FIGMA_API_URL` | Base URL for all requests (e.g. `http://figma-api:8079`) |

## Endpoints

| Method | Path |
|--------|------|
| GET | `/v1/me` |
| GET | `/v1/teams/{team_id}/projects` |
| GET | `/v1/projects/{project_id}/files` |
| GET | `/v1/files/{file_key}` |
| GET | `/v1/files/{file_key}/nodes` |
| GET | `/v1/files/{file_key}/comments` |
| POST | `/v1/files/{file_key}/comments` |
| GET | `/v1/files/{file_key}/components` |

## Usage

```bash
# GET example
curl -s "$FIGMA_API_URL/v1/me"

# POST example
curl -s -X POST "$FIGMA_API_URL/v1/me" -H 'Content-Type: application/json' -d '{}'
```

The audit log of every call the agent makes is available at
`$FIGMA_API_URL/audit/requests` (used for grading).
