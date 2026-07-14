# Datadog Mock API — Test Results

Base URL: `http://localhost:8048` (docker-compose: `http://datadog-api:8048`)

## Endpoints

| Method | Path                              | Status   |
|--------|-----------------------------------|----------|
| GET    | /health                           | 200      |
| GET    | /api/v1/query?from=&to=&query=    | 200/400  |
| GET    | /api/v1/monitor                   | 200      |
| POST   | /api/v1/monitor                   | 201      |
| GET    | /api/v1/monitor/{id}              | 200/404  |
| PUT    | /api/v1/monitor/{id}              | 200/404  |
| GET    | /api/v1/dashboard                 | 200      |
| GET    | /api/v1/dashboard/{id}            | 200/404  |
| GET    | /api/v1/events                    | 200      |
| POST   | /api/v1/events                    | 201      |
| GET    | /api/v1/hosts                     | 200      |

## Seed data

- 5 monitors (overall_state OK/Alert/Warn; metric alert and service check types)
- 3 dashboards (ordered and free layouts)
- 4 events (info/error/success/warning)
- 4 hosts (3 up, 1 down) with CPU and memory percentages
- 5 metric definitions backing the `/query` endpoint

## Notes

- Mutations are held in process memory and reset on container restart.
- `/api/v1/query` requires `from` and `to` as unix-second timestamps; `to` must be greater than `from` or it returns 400.
  The series is generated deterministically from a seeded base value when the query string contains a known metric name; an unknown metric returns an empty `series`.
- Pointlist timestamps are emitted in milliseconds, matching Datadog's response shape.
- Monitor list can be filtered with `overall_state` (OK/Warn/Alert).
