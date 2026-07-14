# Google Calendar API Mock — Test Results

Base URL: `http://localhost:8016` (docker-compose: `http://google-calendar-api:8016`)

## Endpoints

| Method | Path                                              | Status   |
|--------|---------------------------------------------------|----------|
| GET    | /health                                           | 200      |
| GET    | /calendar/v3/users/me/calendarList                | 200      |
| GET    | /calendar/v3/calendars/{calendar_id}              | 200/404  |
| GET    | /calendar/v3/calendars/{calendar_id}/events       | 200/404  |
| GET    | /calendar/v3/calendars/{cid}/events/{event_id}    | 200/404  |
| POST   | /calendar/v3/calendars/{cid}/events               | 201/404  |
| PATCH  | /calendar/v3/calendars/{cid}/events/{event_id}    | 200/404  |
| DELETE | /calendar/v3/calendars/{cid}/events/{event_id}    | 200/404  |
| POST   | /calendar/v3/freeBusy                             | 200      |

## Seed data

- 4 calendars (primary, team eng, holidays, personal)
- 7 events spanning recurring 1:1s, team syncs, focus blocks, all-day holidays
- Attendee responses across 4 events

## Notes

- `calendar_id = "primary"` resolves to the primary calendar.
- `timeMin` / `timeMax` accept ISO-8601 strings; filtering compares as strings.
- `freeBusy` only returns `confirmed` events (matches Google's behavior).
