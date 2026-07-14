# Vimeo Mock API — Test Results

Base URL: `http://localhost:8099` (in docker-compose: `http://vimeo-api:8099`)

## Endpoints covered

| Method | Path                       | Status  |
|--------|----------------------------|---------|
| GET    | /health                    | 200     |
| GET    | /me                        | 200     |
| GET    | /me/videos                 | 200     |
| GET    | /videos/{video_id}         | 200/404 |
| GET    | /users/{user_id}           | 200/404 |
| GET    | /users/{user_id}/videos    | 200/404 |

## Seed data summary

- Users: 6 (Aiko Tanaka, Marcus Reed, Lena Fischer, Priya Nair, Diego Santos,
  Hannah Cole) with account tier, location, bio, websites.
- Videos: 10 across all users (name, description, duration, dimensions, privacy,
  plays, likes, created/modified time, link) dated 2026-05.
- The authenticated user (`/me`) is Aiko Tanaka (id 12000001).

## Notes

- List endpoints (`/me/videos`, `/users/{id}/videos`) return Vimeo's paged
  envelope: `{"total", "page", "per_page", "paging", "data"}`, sorted by
  `created_time` descending. They accept `page` and `per_page` query params.
- Each resource exposes a `uri` (e.g. `/videos/901000103`, `/users/12000002`)
  mirroring the real Vimeo API.
- Unknown video or user ids return a 404 with an `error` message.
- Mutations are held in process memory and reset on container restart (this mock is read-only).
