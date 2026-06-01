---
name: calendly-api-connector
description: >
  Calendly API (Mock) mock HTTP API. Base URL is provided via the
  `CALENDLY_API_URL` environment variable. 8 endpoint(s) across GET, POST.
metadata: {"clawdbot":{"emoji":"🔌"}}
---

# Calendly API (Mock)

Mock HTTP API. **All requests go to the base URL in `$CALENDLY_API_URL`.** Auth headers
are mocked (any token is accepted). Responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `CALENDLY_API_URL` | Base URL for all requests (e.g. `http://calendly-api:8054`) |

## Endpoints

| Method | Path |
|--------|------|
| GET | `/users/me` |
| GET | `/event_types` |
| GET | `/event_types/{uuid}` |
| GET | `/scheduled_events` |
| GET | `/scheduled_events/{uuid}` |
| GET | `/scheduled_events/{uuid}/invitees` |
| POST | `/scheduled_events` |
| POST | `/scheduled_events/{uuid}/cancellation` |

## Usage

```bash
# GET example
curl -s "$CALENDLY_API_URL/users/me"

# POST example
curl -s -X POST "$CALENDLY_API_URL/users/me" -H 'Content-Type: application/json' -d '{}'
```

The audit log of every call the agent makes is available at
`$CALENDLY_API_URL/audit/requests` (used for grading).
