# Discord API (Mock) Guide

Worked `curl` examples for every endpoint. **All requests target the base URL in `$DISCORD_API_URL`.** Auth headers are mocked (any token is accepted) and responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `DISCORD_API_URL` | Base URL for all requests |

## Api

```bash
curl -s "$DISCORD_API_URL/api/v10/users/@me"
curl -s "$DISCORD_API_URL/api/v10/users/@me/guilds"
curl -s "$DISCORD_API_URL/api/v10/guilds/<guild_id>"
curl -s "$DISCORD_API_URL/api/v10/guilds/<guild_id>/channels"
curl -s "$DISCORD_API_URL/api/v10/guilds/<guild_id>/members"
curl -s "$DISCORD_API_URL/api/v10/guilds/<guild_id>/roles"
curl -s "$DISCORD_API_URL/api/v10/channels/<channel_id>"
curl -s "$DISCORD_API_URL/api/v10/channels/<channel_id>/messages"
curl -s -X POST "$DISCORD_API_URL/api/v10/channels/<channel_id>/messages" -H 'Content-Type: application/json' -d '{}'
```

The audit log of every call is available at `$DISCORD_API_URL/audit/requests` (used for grading).
