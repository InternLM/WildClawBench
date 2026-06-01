---
name: zendesk-api-connector
description: >
  Zendesk Support API (Mock) mock HTTP API. Base URL is provided via the
  `ZENDESK_API_URL` environment variable. 9 endpoint(s) across GET, POST, PUT.
metadata: {"clawdbot":{"emoji":"🔌"}}
---

# Zendesk Support API (Mock)

Mock HTTP API. **All requests go to the base URL in `$ZENDESK_API_URL`.** Auth headers
are mocked (any token is accepted). Responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `ZENDESK_API_URL` | Base URL for all requests (e.g. `http://zendesk-api:8025`) |

## Endpoints

| Method | Path |
|--------|------|
| GET | `/api/v2/tickets` |
| GET | `/api/v2/tickets/{ticket_id}` |
| POST | `/api/v2/tickets` |
| PUT | `/api/v2/tickets/{ticket_id}` |
| GET | `/api/v2/tickets/{ticket_id}/comments` |
| POST | `/api/v2/tickets/{ticket_id}/comments` |
| GET | `/api/v2/users` |
| GET | `/api/v2/users/{user_id}` |
| GET | `/api/v2/organizations` |

## Usage

```bash
# GET example
curl -s "$ZENDESK_API_URL/api/v2/tickets"

# POST example
curl -s -X POST "$ZENDESK_API_URL/api/v2/tickets" -H 'Content-Type: application/json' -d '{}'
```

The audit log of every call the agent makes is available at
`$ZENDESK_API_URL/audit/requests` (used for grading).
