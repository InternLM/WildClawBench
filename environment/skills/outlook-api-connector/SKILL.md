---
name: outlook-api-connector
description: >
  Outlook API (Mock) mock HTTP API. Base URL is provided via the
  `OUTLOOK_API_URL` environment variable. 5 endpoint(s) across GET, POST.
metadata: {"clawdbot":{"emoji":"🔌"}}
---

# Outlook API (Mock)

Mock HTTP API. **All requests go to the base URL in `$OUTLOOK_API_URL`.** Auth headers
are mocked (any token is accepted). Responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `OUTLOOK_API_URL` | Base URL for all requests (e.g. `http://outlook-api:8087`) |

## Endpoints

| Method | Path |
|--------|------|
| GET | `/v1.0/me/messages` |
| GET | `/v1.0/me/messages/{message_id}` |
| POST | `/v1.0/me/sendMail` |
| GET | `/v1.0/me/events` |
| GET | `/v1.0/me/contacts` |

## Usage

```bash
# GET example
curl -s "$OUTLOOK_API_URL/v1.0/me/messages"

# POST example
curl -s -X POST "$OUTLOOK_API_URL/v1.0/me/messages" -H 'Content-Type: application/json' -d '{}'
```

The audit log of every call the agent makes is available at
`$OUTLOOK_API_URL/audit/requests` (used for grading).
