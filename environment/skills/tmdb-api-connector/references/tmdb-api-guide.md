# TMDB API (Mock) Guide

Worked `curl` examples for every endpoint. **All requests target the base URL in `$TMDB_API_URL`.** Auth headers are mocked (any token is accepted) and responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `TMDB_API_URL` | Base URL for all requests |

## 3

```bash
curl -s "$TMDB_API_URL/3/search/movie"
curl -s "$TMDB_API_URL/3/movie/popular"
curl -s "$TMDB_API_URL/3/movie/<movie_id>"
curl -s "$TMDB_API_URL/3/movie/<movie_id>/credits"
curl -s "$TMDB_API_URL/3/tv/<tv_id>"
curl -s "$TMDB_API_URL/3/genre/movie/list"
curl -s "$TMDB_API_URL/3/trending/all/week"
```

The audit log of every call is available at `$TMDB_API_URL/audit/requests` (used for grading).
