# Eventbrite API Mock — Test Results

Base URL: `http://localhost:8020` (docker-compose: `http://eventbrite-api:8020`)

## Endpoints

| Method | Path                                              | Status   |
|--------|---------------------------------------------------|----------|
| GET    | /health                                           | 200      |
| GET    | /v3/users/me/organizations                        | 200      |
| GET    | /v3/organizations/{org_id}                        | 200/404  |
| GET    | /v3/organizations/{org_id}/events                 | 200      |
| GET    | /v3/events/search                                 | 200      |
| GET    | /v3/events/{event_id}                             | 200/404  |
| POST   | /v3/events                                        | 201/404  |
| POST   | /v3/events/{event_id}/publish                     | 200/400  |
| POST   | /v3/events/{event_id}/cancel                      | 200/404  |
| GET    | /v3/venues                                        | 200      |
| GET    | /v3/venues/{venue_id}                             | 200/404  |
| GET    | /v3/events/{event_id}/ticket_classes              | 200/404  |
| POST   | /v3/events/{event_id}/ticket_classes              | 201/404  |
| GET    | /v3/events/{event_id}/attendees                   | 200/404  |
| POST   | /v3/events/{event_id}/attendees                   | 201/400  |
| POST   | /v3/attendees/{attendee_id}/check_in              | 200/404  |

## Seed data

- 2 organizations, 5 events (3 live, 1 draft, 1 completed), 3 venues
- 5 ticket classes (free + paid), 7 attendees (1 checked in)

## Notes

- Publishing requires at least one ticket class — otherwise 400.
- Registering an attendee against a sold-out ticket class returns 400.
- All `*_utc` fields are ISO-8601 UTC.
