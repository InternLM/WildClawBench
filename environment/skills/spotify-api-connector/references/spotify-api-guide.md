# Spotify API (Mock) Guide

Worked `curl` examples for every endpoint. **All requests target the base URL in `$SPOTIFY_API_URL`.** Auth headers are mocked (any token is accepted) and responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `SPOTIFY_API_URL` | Base URL for all requests |

## Me

```bash
curl -s "$SPOTIFY_API_URL/v1/me"
curl -s "$SPOTIFY_API_URL/v1/me/playlists"
curl -s "$SPOTIFY_API_URL/v1/me/player"
curl -s -X PUT "$SPOTIFY_API_URL/v1/me/player/play" -H 'Content-Type: application/json' -d '{}'
```

## Playlists

```bash
curl -s "$SPOTIFY_API_URL/v1/playlists/<playlist_id>"
curl -s "$SPOTIFY_API_URL/v1/playlists/<playlist_id>/tracks"
curl -s -X POST "$SPOTIFY_API_URL/v1/playlists/<playlist_id>/tracks" -H 'Content-Type: application/json' -d '{}'
```

## Search

```bash
curl -s "$SPOTIFY_API_URL/v1/search"
```

## Users

```bash
curl -s -X POST "$SPOTIFY_API_URL/v1/users/<user_id>/playlists" -H 'Content-Type: application/json' -d '{}'
```

The audit log of every call is available at `$SPOTIFY_API_URL/audit/requests` (used for grading).
