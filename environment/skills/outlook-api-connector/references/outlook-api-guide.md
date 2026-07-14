# Outlook API (Mock) Guide

Worked `curl` examples for every endpoint. **All requests target the base URL in `$OUTLOOK_API_URL`.** Auth headers are mocked (any token is accepted) and responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `OUTLOOK_API_URL` | Base URL for all requests |

## V1.0

```bash
curl -s "$OUTLOOK_API_URL/v1.0/me/messages"
curl -s "$OUTLOOK_API_URL/v1.0/me/messages/<message_id>"
curl -s -X POST "$OUTLOOK_API_URL/v1.0/me/sendMail" -H 'Content-Type: application/json' -d '{}'
curl -s "$OUTLOOK_API_URL/v1.0/me/events"
curl -s "$OUTLOOK_API_URL/v1.0/me/contacts"
```

The audit log of every call is available at `$OUTLOOK_API_URL/audit/requests` (used for grading).
