---
name: eventbrite-api-connector
description: >
  Eventbrite API (Mock) mock HTTP API. Base URL is provided via the
  `EVENTBRITE_API_URL` environment variable. 15 endpoint(s) across GET, POST.
metadata: {"clawdbot":{"emoji":"🔌"}}
---

# Eventbrite API (Mock)

Mock HTTP API. **All requests go to the base URL in `$EVENTBRITE_API_URL`.** Auth headers
are mocked (any token is accepted). Responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `EVENTBRITE_API_URL` | Base URL for all requests (e.g. `http://eventbrite-api:8020`) |

## Endpoints

| Method | Path |
|--------|------|
| GET | `/v3/users/me/organizations` |
| GET | `/v3/organizations/{org_id}` |
| GET | `/v3/organizations/{org_id}/events` |
| GET | `/v3/events/search` |
| GET | `/v3/events/{event_id}` |
| POST | `/v3/events` |
| POST | `/v3/events/{event_id}/publish` |
| POST | `/v3/events/{event_id}/cancel` |
| GET | `/v3/venues` |
| GET | `/v3/venues/{venue_id}` |
| GET | `/v3/events/{event_id}/ticket_classes` |
| POST | `/v3/events/{event_id}/ticket_classes` |
| GET | `/v3/events/{event_id}/attendees` |
| POST | `/v3/events/{event_id}/attendees` |
| POST | `/v3/attendees/{attendee_id}/check_in` |

## Usage

```bash
# GET example
curl -s "$EVENTBRITE_API_URL/v3/users/me/organizations"

# POST example
curl -s -X POST "$EVENTBRITE_API_URL/v3/users/me/organizations" -H 'Content-Type: application/json' -d '{}'
```

The audit log of every call the agent makes is available at
`$EVENTBRITE_API_URL/audit/requests` (used for grading).
