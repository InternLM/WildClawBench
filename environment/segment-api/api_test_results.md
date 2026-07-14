# Segment Mock API — Test Results

Base URL: `http://localhost:8090` (in docker-compose: `http://segment-api:8090`)

## Endpoints covered

| Method | Path               | Status |
|--------|--------------------|--------|
| GET    | /health            | 200    |
| POST   | /v1/track          | 200    |
| POST   | /v1/identify       | 200    |
| POST   | /v1/page           | 200    |
| POST   | /v1/batch          | 200    |
| GET    | /v1/events         | 200    |
| GET    | /v1/sources        | 200    |
| GET    | /v1/destinations   | 200    |

## Seed data summary

- Events: 10 seeded events (track/identify/page) across 5 users, dated 2026-05.
- Sources: 5 sources (web, iOS, Android, server, legacy) with enabled flags.
- Destinations: 6 destinations (GA4, Amplitude, BigQuery, Slack, Mixpanel, Facebook).

## Notes

- `/v1/track`, `/v1/identify`, `/v1/page` accept a JSON body and append to the
  in-memory event list, returning `{"success": true}`.
- `/v1/batch` accepts `{"batch": [...]}` and ingests each item by its `type`.
- `/v1/events` returns seeded + ingested events; filterable by `type` and `userId`.
- Ingested events are held in process memory and reset on container restart.
