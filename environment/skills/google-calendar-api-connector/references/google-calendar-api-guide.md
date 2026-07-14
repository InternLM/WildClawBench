# Google Calendar API (Mock) Guide

Worked `curl` examples for every endpoint. **All requests target the base URL in `$GOOGLE_CALENDAR_API_URL`.** Auth headers are mocked (any token is accepted) and responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `GOOGLE_CALENDAR_API_URL` | Base URL for all requests |

## Calendar

```bash
curl -s "$GOOGLE_CALENDAR_API_URL/calendar/v3/users/me/calendarList"
curl -s "$GOOGLE_CALENDAR_API_URL/calendar/v3/calendars/<calendar_id>"
curl -s "$GOOGLE_CALENDAR_API_URL/calendar/v3/calendars/<calendar_id>/events"
curl -s "$GOOGLE_CALENDAR_API_URL/calendar/v3/calendars/<calendar_id>/events/<event_id>"
curl -s -X POST "$GOOGLE_CALENDAR_API_URL/calendar/v3/calendars/<calendar_id>/events" -H 'Content-Type: application/json' -d '{}'
curl -s -X PATCH "$GOOGLE_CALENDAR_API_URL/calendar/v3/calendars/<calendar_id>/events/<event_id>" -H 'Content-Type: application/json' -d '{}'
curl -s -X DELETE "$GOOGLE_CALENDAR_API_URL/calendar/v3/calendars/<calendar_id>/events/<event_id>"
curl -s -X POST "$GOOGLE_CALENDAR_API_URL/calendar/v3/freeBusy" -H 'Content-Type: application/json' -d '{}'
```

The audit log of every call is available at `$GOOGLE_CALENDAR_API_URL/audit/requests` (used for grading).
