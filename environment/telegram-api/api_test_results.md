# Telegram Bot Mock API — Test Results

Base URL: `http://localhost:8063` (in docker-compose: `http://telegram-api:8063`)

## Endpoints covered

| Method | Path                    | Status |
|--------|-------------------------|--------|
| GET    | /health                 | 200    |
| GET    | /bot/getMe              | 200    |
| POST   | /bot/sendMessage        | 200/400 |
| GET    | /bot/getUpdates         | 200    |
| GET    | /bot/getChat            | 200/400 |
| POST   | /bot/sendPhoto          | 200/400 |
| GET    | /bot/getChatMember      | 200/400 |
| POST   | /bot/editMessageText    | 200/400 |
| POST   | /bot/deleteMessage      | 200/400 |

## Seed data summary

- Bot: `orbit_ops_bot` (id `7654321098`) from `bot.json`.
- Users: 6 (5 people + the bot).
- Chats: 5 (2 private, 2 group, 1 supergroup).
- Messages: 9 across the seeded chats (some are replies).
- Chat members: 9 membership rows with creator/administrator/member statuses.

## Notes

- Mutations are held in process memory and reset on container restart.
- All responses use the Telegram envelope `{"ok": true, "result": ...}`.
  Failures return `{"ok": false, "error_code": 400, "description": ...}` with HTTP 400.
- `getUpdates` synthesizes an update per stored message, ordered by date; pass
  `offset` to skip earlier `update_id`s.
- `sendMessage` / `sendPhoto` post as the bot and append to the message log so
  they then appear in `getUpdates`.
- `getChatMember` returns `status: "left"` for known users who are not members.
