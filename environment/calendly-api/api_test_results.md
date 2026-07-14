# Calendly Mock API — Test Results

Base URL: `http://localhost:8054` (in docker-compose: `http://calendly-api:8054`)

## Endpoints covered

| Method | Path                                          | Status  |
|--------|-----------------------------------------------|---------|
| GET    | /health                                       | 200     |
| GET    | /users/me                                     | 200     |
| GET    | /event_types?user=                            | 200     |
| GET    | /event_types/{uuid}                           | 200/404 |
| GET    | /scheduled_events?user=                       | 200     |
| GET    | /scheduled_events/{uuid}                       | 200/404 |
| GET    | /scheduled_events/{uuid}/invitees             | 200/404 |
| POST   | /scheduled_events                             | 201/400 |
| POST   | /scheduled_events/{uuid}/cancellation         | 200/404 |

## Seed data summary

- User: Amelia Ortega (`user-amelia-ortega`)
- Event types: 4 (Intro 15-min, Discovery 30-min, Deep Dive 60-min, 1 archived 45-min)
- Scheduled events: 4 (3 active + 1 canceled)
- Invitees: 4 (with questions_and_answers on active events)
- Availability: weekly working-hour windows (Mon-Fri)

## Notes

- `user` / `event_type` / `uuid` params accept either a bare uuid (e.g.
  `user-amelia-ortega`) or a full Calendly URI; the trailing segment is used.
- `POST /scheduled_events` books a slot for a given `event_type` and optionally
  creates an invitee. `POST /scheduled_events/{uuid}/cancellation` cancels the
  event and its invitees.
- Mutations are held in process memory and reset on container restart.
