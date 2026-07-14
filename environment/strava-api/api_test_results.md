# Strava Mock API — Test Results

Base URL: `http://localhost:8060` (in docker-compose: `http://strava-api:8060`)

## Endpoints covered

| Method | Path                                | Status |
|--------|-------------------------------------|--------|
| GET    | /health                             | 200    |
| GET    | /api/v3/athlete                     | 200    |
| GET    | /api/v3/athlete/activities          | 200    |
| GET    | /api/v3/activities/{id}             | 200/404 |
| PUT    | /api/v3/activities/{id}             | 200/404 |
| GET    | /api/v3/activities/{id}/kudos       | 200/404 |
| GET    | /api/v3/segments/{id}               | 200/404 |
| GET    | /api/v3/athletes/{id}/stats         | 200/404 |

## Seed data summary

- Athlete: `Nadia Voss` (id `4410022`), Portland OR, premium.
- Activities: 12 (types `Run`, `Ride`, `Swim`) with distance (m), moving_time (s),
  total_elevation_gain, average_speed, start_date, kudos_count.
- Segments: 3 (Waterfront Loop, Powell Butte Climb, Springwater Corridor).
- Kudoers: 12 kudo rows across 5 activities (5 distinct athletes).

## Notes

- `/api/v3/athlete/activities` supports `before`/`after` (unix epoch seconds, compared against the
  activity `start_date`), plus `page`/`per_page`; results are newest-first.
- `PUT /api/v3/activities/{id}` updates `name` and/or `type` in process memory (resets on restart).
- `/api/v3/athletes/{id}/stats` aggregates run/ride/swim totals (count, distance, moving_time,
  elevation_gain) for the seeded athlete.
- Not-found responses use Strava-style `{error, errors: [{resource, code}]}`.
