---
name: notion-api-connector
description: >
  Notion API (Mock) mock HTTP API. Base URL is provided via the
  `NOTION_API_URL` environment variable. 17 endpoint(s) across DELETE, GET, PATCH, POST.
metadata: {"clawdbot":{"emoji":"🔌"}}
---

# Notion API (Mock)

Mock HTTP API. **All requests go to the base URL in `$NOTION_API_URL`.** Auth headers
are mocked (any token is accepted). Responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `NOTION_API_URL` | Base URL for all requests (e.g. `http://notion-api:8010`) |

## Endpoints

| Method | Path |
|--------|------|
| GET | `/v1/users` |
| GET | `/v1/users/me` |
| GET | `/v1/users/{user_id}` |
| GET | `/v1/workspace` |
| POST | `/v1/search` |
| GET | `/v1/databases/{database_id}` |
| POST | `/v1/databases/{database_id}/query` |
| GET | `/v1/pages/{page_id}` |
| POST | `/v1/pages` |
| PATCH | `/v1/pages/{page_id}` |
| DELETE | `/v1/pages/{page_id}` |
| GET | `/v1/blocks/{block_id}/children` |
| PATCH | `/v1/blocks/{block_id}/children` |
| PATCH | `/v1/blocks/{block_id}` |
| DELETE | `/v1/blocks/{block_id}` |
| GET | `/v1/comments` |
| POST | `/v1/comments` |

## Usage

```bash
# GET example
curl -s "$NOTION_API_URL/v1/users"

# POST example
curl -s -X POST "$NOTION_API_URL/v1/users" -H 'Content-Type: application/json' -d '{}'
```

The audit log of every call the agent makes is available at
`$NOTION_API_URL/audit/requests` (used for grading).
