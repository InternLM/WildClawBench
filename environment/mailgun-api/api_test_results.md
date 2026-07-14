# Mailgun Mock API — Test Results

Base URL: `http://localhost:8094` (in docker-compose: `http://mailgun-api:8094`)

## Endpoints covered

| Method | Path                              | Status  |
|--------|-----------------------------------|---------|
| GET    | /health                           | 200     |
| POST   | /v3/{domain}/messages             | 200/400 |
| GET    | /v3/{domain}/events               | 200     |
| GET    | /v3/{domain}/stats/total          | 200     |
| GET    | /v3/lists/{address}/members       | 200/404 |

## Seed data summary

- Messages: 7 sent messages (domain, from, to, subject, body, timestamp) keyed by Mailgun-style message ids, dated 2026-05.
- Events: 12 delivery events (accepted, delivered, opened, clicked, failed) linked to messages.
- List members: 7 members across two mailing lists (newsletter@, developers@) with subscribed flag and vars.

## Notes

- `POST /v3/{domain}/messages` accepts the message fields in the request body
  (`from`, `to`, `subject`, `text`) and returns `{"id": "<...>", "message": "Queued. Thank you."}`.
- `GET /v3/{domain}/events` filters by `event` (supports `a OR b`) and `recipient`.
- `GET /v3/{domain}/stats/total` aggregates accepted/delivered/failed/opened/clicked counts.
- `GET /v3/lists/{address}/members` filters by `subscribed`; returns 404 for unknown lists.
- Mutations (sent messages) are held in process memory and reset on container restart.
