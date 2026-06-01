---
name: tmdb-api-connector
description: >
  TMDB API (Mock) mock HTTP API. Base URL is provided via the
  `TMDB_API_URL` environment variable. 7 endpoint(s) across GET.
metadata: {"clawdbot":{"emoji":"🔌"}}
---

# TMDB API (Mock)

Mock HTTP API. **All requests go to the base URL in `$TMDB_API_URL`.** Auth headers
are mocked (any token is accepted). Responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `TMDB_API_URL` | Base URL for all requests (e.g. `http://tmdb-api:8059`) |

## Endpoints

| Method | Path |
|--------|------|
| GET | `/3/search/movie` |
| GET | `/3/movie/popular` |
| GET | `/3/movie/{movie_id}` |
| GET | `/3/movie/{movie_id}/credits` |
| GET | `/3/tv/{tv_id}` |
| GET | `/3/genre/movie/list` |
| GET | `/3/trending/all/week` |

## Usage

```bash
# GET example
curl -s "$TMDB_API_URL/3/search/movie"

# POST example
curl -s -X POST "$TMDB_API_URL/3/search/movie" -H 'Content-Type: application/json' -d '{}'
```

The audit log of every call the agent makes is available at
`$TMDB_API_URL/audit/requests` (used for grading).
