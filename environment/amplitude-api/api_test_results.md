# Amplitude Mock API — Test Results

Base URL: `http://localhost:8091` (in docker-compose: `http://amplitude-api:8091`)

## Endpoints covered

| Method | Path                          | Status  |
|--------|-------------------------------|---------|
| GET    | /health                       | 200     |
| POST   | /2/httpapi                    | 200     |
| GET    | /api/2/events/segmentation    | 200     |
| GET    | /api/2/useractivity           | 200/404 |

## Seed data summary

- Events: 10 seeded events across 5 users (session_start, page_view, purchase, etc.), dated 2026-05.
- Users: 5 users with device, country, platform, version, first/last seen.
- Segmentation: daily counts for `purchase` and `session_start` over 2026-05-02..06.

## Notes

- `/2/httpapi` accepts `{"events": [...]}` and returns
  `{"code": 200, "events_ingested": N, ...}`; events append to in-memory store.
- `/api/2/events/segmentation` returns chart series; filter by `e` (event_type),
  `start`, and `end` (dates).
- `/api/2/useractivity?user=` returns the user's profile plus chronological event stream.
- Uploaded events are held in process memory and reset on container restart.
