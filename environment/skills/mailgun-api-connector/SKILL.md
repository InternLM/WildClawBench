---
name: mailgun-api-connector
description: >
  Mailgun API (Mock) mock HTTP API. Base URL is provided via the
  `MAILGUN_API_URL` environment variable. 4 endpoint(s) across GET, POST.
metadata: {"clawdbot":{"emoji":"🔌"}}
---

# Mailgun API (Mock)

Mock HTTP API. **All requests go to the base URL in `$MAILGUN_API_URL`.** Auth headers
are mocked (any token is accepted). Responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `MAILGUN_API_URL` | Base URL for all requests (e.g. `http://mailgun-api:8094`) |

## Endpoints

| Method | Path |
|--------|------|
| POST | `/v3/{domain}/messages` |
| GET | `/v3/{domain}/events` |
| GET | `/v3/{domain}/stats/total` |
| GET | `/v3/lists/{address}/members` |

## Usage

```bash
# GET example
curl -s "$MAILGUN_API_URL/v3/{domain}/messages"

# POST example
curl -s -X POST "$MAILGUN_API_URL/v3/{domain}/messages" -H 'Content-Type: application/json' -d '{}'
```

The audit log of every call the agent makes is available at
`$MAILGUN_API_URL/audit/requests` (used for grading).
