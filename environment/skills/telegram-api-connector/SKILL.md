---
name: telegram-api-connector
description: >
  Telegram Bot API (Mock) mock HTTP API. Base URL is provided via the
  `TELEGRAM_API_URL` environment variable. 8 endpoint(s) across GET, POST.
metadata: {"clawdbot":{"emoji":"🔌"}}
---

# Telegram Bot API (Mock)

Mock HTTP API. **All requests go to the base URL in `$TELEGRAM_API_URL`.** Auth headers
are mocked (any token is accepted). Responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `TELEGRAM_API_URL` | Base URL for all requests (e.g. `http://telegram-api:8063`) |

## Endpoints

| Method | Path |
|--------|------|
| GET | `/bot/getMe` |
| POST | `/bot/sendMessage` |
| POST | `/bot/sendPhoto` |
| POST | `/bot/editMessageText` |
| POST | `/bot/deleteMessage` |
| GET | `/bot/getUpdates` |
| GET | `/bot/getChat` |
| GET | `/bot/getChatMember` |

## Usage

```bash
# GET example
curl -s "$TELEGRAM_API_URL/bot/getMe"

# POST example
curl -s -X POST "$TELEGRAM_API_URL/bot/getMe" -H 'Content-Type: application/json' -d '{}'
```

The audit log of every call the agent makes is available at
`$TELEGRAM_API_URL/audit/requests` (used for grading).
