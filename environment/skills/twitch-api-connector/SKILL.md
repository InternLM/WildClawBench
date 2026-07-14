---
name: twitch-api-connector
description: >
  Twitch Helix API (Mock) mock HTTP API. Base URL is provided via the
  `TWITCH_API_URL` environment variable. 7 endpoint(s) across GET.
metadata: {"clawdbot":{"emoji":"🔌"}}
---

# Twitch Helix API (Mock)

Mock HTTP API. **All requests go to the base URL in `$TWITCH_API_URL`.** Auth headers
are mocked (any token is accepted). Responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `TWITCH_API_URL` | Base URL for all requests (e.g. `http://twitch-api:8064`) |

## Endpoints

| Method | Path |
|--------|------|
| GET | `/helix/users` |
| GET | `/helix/streams` |
| GET | `/helix/channels` |
| GET | `/helix/channels/followers` |
| GET | `/helix/games/top` |
| GET | `/helix/games` |
| GET | `/helix/clips` |

## Usage

```bash
# GET example
curl -s "$TWITCH_API_URL/helix/users"

# POST example
curl -s -X POST "$TWITCH_API_URL/helix/users" -H 'Content-Type: application/json' -d '{}'
```

The audit log of every call the agent makes is available at
`$TWITCH_API_URL/audit/requests` (used for grading).
