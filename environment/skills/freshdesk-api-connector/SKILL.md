---
name: freshdesk-api-connector
description: >
  Freshdesk API (Mock) mock HTTP API. Base URL is provided via the
  `FRESHDESK_API_URL` environment variable. 6 endpoint(s) across GET, POST, PUT.
metadata: {"clawdbot":{"emoji":"🔌"}}
---

# Freshdesk API (Mock)

Mock HTTP API. **All requests go to the base URL in `$FRESHDESK_API_URL`.** Auth headers
are mocked (any token is accepted). Responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `FRESHDESK_API_URL` | Base URL for all requests (e.g. `http://freshdesk-api:8093`) |

## Endpoints

| Method | Path |
|--------|------|
| GET | `/api/v2/tickets` |
| GET | `/api/v2/tickets/{ticket_id}` |
| POST | `/api/v2/tickets` |
| PUT | `/api/v2/tickets/{ticket_id}` |
| GET | `/api/v2/contacts` |
| GET | `/api/v2/agents` |

## Usage

```bash
# GET example
curl -s "$FRESHDESK_API_URL/api/v2/tickets"

# POST example
curl -s -X POST "$FRESHDESK_API_URL/api/v2/tickets" -H 'Content-Type: application/json' -d '{}'
```

The audit log of every call the agent makes is available at
`$FRESHDESK_API_URL/audit/requests` (used for grading).
