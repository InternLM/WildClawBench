---
name: discord-api-connector
description: >
  Discord API (Mock) mock HTTP API. Base URL is provided via the
  `DISCORD_API_URL` environment variable. 9 endpoint(s) across GET, POST.
metadata: {"clawdbot":{"emoji":"🔌"}}
---

# Discord API (Mock)

Mock HTTP API. **All requests go to the base URL in `$DISCORD_API_URL`.** Auth headers
are mocked (any token is accepted). Responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `DISCORD_API_URL` | Base URL for all requests (e.g. `http://discord-api:8057`) |

## Endpoints

| Method | Path |
|--------|------|
| GET | `/api/v10/users/@me` |
| GET | `/api/v10/users/@me/guilds` |
| GET | `/api/v10/guilds/{guild_id}` |
| GET | `/api/v10/guilds/{guild_id}/channels` |
| GET | `/api/v10/guilds/{guild_id}/members` |
| GET | `/api/v10/guilds/{guild_id}/roles` |
| GET | `/api/v10/channels/{channel_id}` |
| GET | `/api/v10/channels/{channel_id}/messages` |
| POST | `/api/v10/channels/{channel_id}/messages` |

## Usage

```bash
# GET example
curl -s "$DISCORD_API_URL/api/v10/users/@me"

# POST example
curl -s -X POST "$DISCORD_API_URL/api/v10/users/@me" -H 'Content-Type: application/json' -d '{}'
```

The audit log of every call the agent makes is available at
`$DISCORD_API_URL/audit/requests` (used for grading).
