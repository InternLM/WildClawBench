# NASA Open Mock API — Test Results

Base URL: `http://localhost:8077` (in docker-compose: `http://nasa-api:8077`)

## Endpoints covered

| Method | Path                                          | Status  |
|--------|-----------------------------------------------|---------|
| GET    | /health                                       | 200     |
| GET    | /planetary/apod                               | 200/404 |
| GET    | /mars-photos/api/v1/rovers/{rover}/photos     | 200/404 |
| GET    | /mars-photos/api/v1/rovers/{rover}            | 200/404 |
| GET    | /neo/rest/v1/feed                             | 200     |
| GET    | /neo/rest/v1/neo/{neo_id}                     | 200/404 |
| GET    | /EPIC/api/natural                             | 200     |

## Seed data summary

- APOD: 8 entries keyed by date 2026-05-20..27 (title, explanation, url, media_type, copyright).
- Rovers: 3 (curiosity, perseverance, opportunity) with manifest fields.
- Rover photos: 11 (rover, sol, camera, img_src, earth_date).
- NEOs: 8 objects (name, diameter, close-approach date, miss distance, velocity, hazardous flag).
- EPIC: 5 natural-color images with centroid coordinates.

## Notes

- `/planetary/apod` with no params returns the latest entry; `date=` returns one
  entry; `start_date`/`end_date` return a list spanning the range.
- `/mars-photos/.../photos` filters by `sol`, `camera`, and/or `earth_date`.
- `/neo/rest/v1/feed` groups objects under `near_earth_objects` by close-approach date.
- Mutations are held in process memory and reset on container restart (this mock is read-only).
