---
name: spotify-api-connector
description: >
  Spotify API (Mock) mock HTTP API. Base URL is provided via the
  `SPOTIFY_API_URL` environment variable. 9 endpoint(s) across GET, POST, PUT.
metadata: {"clawdbot":{"emoji":"🔌"}}
---

# Spotify API (Mock)

Mock HTTP API. **All requests go to the base URL in `$SPOTIFY_API_URL`.** Auth headers
are mocked (any token is accepted). Responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `SPOTIFY_API_URL` | Base URL for all requests (e.g. `http://spotify-api:8039`) |

## Endpoints

| Method | Path |
|--------|------|
| GET | `/v1/me` |
| GET | `/v1/me/playlists` |
| GET | `/v1/playlists/{playlist_id}` |
| GET | `/v1/playlists/{playlist_id}/tracks` |
| POST | `/v1/users/{user_id}/playlists` |
| POST | `/v1/playlists/{playlist_id}/tracks` |
| GET | `/v1/search` |
| GET | `/v1/me/player` |
| PUT | `/v1/me/player/play` |

## Usage

```bash
# GET example
curl -s "$SPOTIFY_API_URL/v1/me"

# POST example
curl -s -X POST "$SPOTIFY_API_URL/v1/me" -H 'Content-Type: application/json' -d '{}'
```

The audit log of every call the agent makes is available at
`$SPOTIFY_API_URL/audit/requests` (used for grading).
