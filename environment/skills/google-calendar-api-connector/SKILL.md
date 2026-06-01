---
name: google-calendar-api-connector
description: >
  Google Calendar API (Mock) mock HTTP API. Base URL is provided via the
  `GOOGLE_CALENDAR_API_URL` environment variable. 8 endpoint(s) across DELETE, GET, PATCH, POST.
metadata: {"clawdbot":{"emoji":"🔌"}}
---

# Google Calendar API (Mock)

Mock HTTP API. **All requests go to the base URL in `$GOOGLE_CALENDAR_API_URL`.** Auth headers
are mocked (any token is accepted). Responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `GOOGLE_CALENDAR_API_URL` | Base URL for all requests (e.g. `http://google-calendar-api:8016`) |

## Endpoints

| Method | Path |
|--------|------|
| GET | `/calendar/v3/users/me/calendarList` |
| GET | `/calendar/v3/calendars/{calendar_id}` |
| GET | `/calendar/v3/calendars/{calendar_id}/events` |
| GET | `/calendar/v3/calendars/{calendar_id}/events/{event_id}` |
| POST | `/calendar/v3/calendars/{calendar_id}/events` |
| PATCH | `/calendar/v3/calendars/{calendar_id}/events/{event_id}` |
| DELETE | `/calendar/v3/calendars/{calendar_id}/events/{event_id}` |
| POST | `/calendar/v3/freeBusy` |

## Usage

```bash
# GET example
curl -s "$GOOGLE_CALENDAR_API_URL/calendar/v3/users/me/calendarList"

# POST example
curl -s -X POST "$GOOGLE_CALENDAR_API_URL/calendar/v3/users/me/calendarList" -H 'Content-Type: application/json' -d '{}'
```

The audit log of every call the agent makes is available at
`$GOOGLE_CALENDAR_API_URL/audit/requests` (used for grading).
