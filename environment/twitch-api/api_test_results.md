# Twitch Helix Mock API — Test Results

Base URL: `http://localhost:8064` (in docker-compose: `http://twitch-api:8064`)

## Endpoints covered

| Method | Path                          | Status |
|--------|-------------------------------|--------|
| GET    | /health                       | 200    |
| GET    | /helix/users                  | 200    |
| GET    | /helix/streams                | 200    |
| GET    | /helix/channels               | 200    |
| GET    | /helix/channels/followers     | 200    |
| GET    | /helix/games/top              | 200    |
| GET    | /helix/games                  | 200    |
| GET    | /helix/clips                  | 200    |

## Seed data summary

- Users: 6 (partners, affiliates, and one non-affiliate).
- Streams: 6 total - 3 live (PixelPaladin, SprintQueen, OrbitDev) and 3 offline.
- Channels: 6 (one per user) with game, title, tags, and follower counts.
- Games: 6 ranked top games.
- Clips: 5 across multiple broadcasters/games.

## Notes

- Mutations are not modeled - this Helix subset is read-only. Data resets on restart.
- All collection responses wrap rows in `{"data": [...]}`.
- `GET /helix/streams` returns only live streams; filter by repeatable `user_login`
  / `user_id` query params or by `game_id`.
- `GET /helix/users` and `/helix/games` accept repeatable `login`/`id` and `name`/`id` params.
- `GET /helix/channels/followers` returns `{"data": [], "total": <follower_count>}`,
  matching Helix where the total is the headline figure.
