# Twitch Helix API (Mock) Guide

Worked `curl` examples for every endpoint. **All requests target the base URL in `$TWITCH_API_URL`.** Auth headers are mocked (any token is accepted) and responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `TWITCH_API_URL` | Base URL for all requests |

## Helix

```bash
curl -s "$TWITCH_API_URL/helix/users"
curl -s "$TWITCH_API_URL/helix/streams"
curl -s "$TWITCH_API_URL/helix/channels"
curl -s "$TWITCH_API_URL/helix/channels/followers"
curl -s "$TWITCH_API_URL/helix/games/top"
curl -s "$TWITCH_API_URL/helix/games"
curl -s "$TWITCH_API_URL/helix/clips"
```

The audit log of every call is available at `$TWITCH_API_URL/audit/requests` (used for grading).
