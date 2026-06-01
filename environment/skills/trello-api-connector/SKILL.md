---
name: trello-api-connector
description: >
  Trello API (Mock) mock HTTP API. Base URL is provided via the
  `TRELLO_API_URL` environment variable. 11 endpoint(s) across DELETE, GET, POST, PUT.
metadata: {"clawdbot":{"emoji":"🔌"}}
---

# Trello API (Mock)

Mock HTTP API. **All requests go to the base URL in `$TRELLO_API_URL`.** Auth headers
are mocked (any token is accepted). Responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `TRELLO_API_URL` | Base URL for all requests (e.g. `http://trello-api:8030`) |

## Endpoints

| Method | Path |
|--------|------|
| GET | `/1/members/me` |
| GET | `/1/members/me/boards` |
| GET | `/1/boards/{board_id}` |
| GET | `/1/boards/{board_id}/lists` |
| GET | `/1/lists/{list_id}/cards` |
| GET | `/1/cards/{card_id}` |
| POST | `/1/cards` |
| PUT | `/1/cards/{card_id}` |
| DELETE | `/1/cards/{card_id}` |
| GET | `/1/cards/{card_id}/checklists` |
| POST | `/1/checklists` |

## Usage

```bash
# GET example
curl -s "$TRELLO_API_URL/1/members/me"

# POST example
curl -s -X POST "$TRELLO_API_URL/1/members/me" -H 'Content-Type: application/json' -d '{}'
```

The audit log of every call the agent makes is available at
`$TRELLO_API_URL/audit/requests` (used for grading).
