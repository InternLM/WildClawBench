# Telegram Bot API (Mock) Guide

Worked `curl` examples for every endpoint. **All requests target the base URL in `$TELEGRAM_API_URL`.** Auth headers are mocked (any token is accepted) and responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `TELEGRAM_API_URL` | Base URL for all requests |

## Bot

```bash
curl -s "$TELEGRAM_API_URL/bot/getMe"
curl -s -X POST "$TELEGRAM_API_URL/bot/sendMessage" -H 'Content-Type: application/json' -d '{}'
curl -s -X POST "$TELEGRAM_API_URL/bot/sendPhoto" -H 'Content-Type: application/json' -d '{}'
curl -s -X POST "$TELEGRAM_API_URL/bot/editMessageText" -H 'Content-Type: application/json' -d '{}'
curl -s -X POST "$TELEGRAM_API_URL/bot/deleteMessage" -H 'Content-Type: application/json' -d '{}'
curl -s "$TELEGRAM_API_URL/bot/getUpdates"
curl -s "$TELEGRAM_API_URL/bot/getChat"
curl -s "$TELEGRAM_API_URL/bot/getChatMember"
```

The audit log of every call is available at `$TELEGRAM_API_URL/audit/requests` (used for grading).
