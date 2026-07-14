---
name: monday-api-connector
description: >
  monday.com API (Mock) mock HTTP API. Base URL is provided via the
  `MONDAY_API_URL` environment variable. 10 endpoint(s) across DELETE, GET, POST, PUT.
metadata: {"clawdbot":{"emoji":"🔌"}}
---

# monday.com API (Mock)

Mock HTTP API. **All requests go to the base URL in `$MONDAY_API_URL`.** Auth headers
are mocked (any token is accepted). Responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `MONDAY_API_URL` | Base URL for all requests (e.g. `http://monday-api:8080`) |

## Endpoints

| Method | Path |
|--------|------|
| GET | `/v2/workspaces` |
| GET | `/v2/boards` |
| GET | `/v2/boards/{board_id}` |
| GET | `/v2/boards/{board_id}/items` |
| GET | `/v2/items` |
| POST | `/v2/items` |
| GET | `/v2/items/{item_id}` |
| PUT | `/v2/items/{item_id}` |
| DELETE | `/v2/items/{item_id}` |
| GET | `/v2/users` |

## Usage

```bash
# GET example
curl -s "$MONDAY_API_URL/v2/workspaces"

# POST example
curl -s -X POST "$MONDAY_API_URL/v2/workspaces" -H 'Content-Type: application/json' -d '{}'
```

The audit log of every call the agent makes is available at
`$MONDAY_API_URL/audit/requests` (used for grading).
