# Discord Mock API — Test Results

Base URL: `http://localhost:8057` (in docker-compose: `http://discord-api:8057`)

## Endpoints covered

| Method | Path                                      | Status |
|--------|-------------------------------------------|--------|
| GET    | /health                                   | 200    |
| GET    | /api/v10/users/@me                        | 200    |
| GET    | /api/v10/users/@me/guilds                 | 200    |
| GET    | /api/v10/guilds/{guild_id}                | 200/404 |
| GET    | /api/v10/guilds/{guild_id}/channels       | 200/404 |
| GET    | /api/v10/guilds/{guild_id}/members        | 200/404 |
| GET    | /api/v10/guilds/{guild_id}/roles          | 200/404 |
| GET    | /api/v10/channels/{channel_id}            | 200/404 |
| GET    | /api/v10/channels/{channel_id}/messages   | 200/404 |
| POST   | /api/v10/channels/{channel_id}/messages   | 201/400/404 |

## Seed data summary

- Bot user (`/users/@me`): `orbitbot` (id `300100200300400001`).
- Guilds: 2 (`Orbit Labs Community`, `Indie Game Devs`).
- Channels: 7 (text type `0` + voice type `2`) across both guilds.
- Members: 8 memberships (5 in Orbit Labs, 3 in Indie Game Devs).
- Roles: 6 (Admin, Moderator, Member, Bots, Organizer, Dev).
- Messages: 8 across multiple channels.

## Notes

- All IDs are Discord-style snowflakes (numeric strings, 18-19 digits).
- New messages get a freshly generated snowflake id and are held in memory until restart.
- Channel `type`: `0` = text, `2` = guild voice.
- Not-found errors use Discord-style `{ "error": ..., "code": ... }` (10003 channel, 10004 guild).
