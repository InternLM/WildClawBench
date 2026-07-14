# Gmail API (Mock) Guide

Worked `curl` examples for every endpoint. **All requests target the base URL in `$GMAIL_API_URL`.** Auth headers are mocked (any token is accepted) and responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `GMAIL_API_URL` | Base URL for all requests |

## Gmail

```bash
curl -s "$GMAIL_API_URL/gmail/v1/users/me/profile"
curl -s "$GMAIL_API_URL/gmail/v1/users/me/labels"
curl -s "$GMAIL_API_URL/gmail/v1/users/me/labels/<label_id>"
curl -s -X POST "$GMAIL_API_URL/gmail/v1/users/me/labels" -H 'Content-Type: application/json' -d '{}'
curl -s "$GMAIL_API_URL/gmail/v1/users/me/messages"
curl -s "$GMAIL_API_URL/gmail/v1/users/me/messages/<message_id>"
curl -s -X POST "$GMAIL_API_URL/gmail/v1/users/me/messages/send" -H 'Content-Type: application/json' -d '{}'
curl -s -X POST "$GMAIL_API_URL/gmail/v1/users/me/messages/<message_id>/modify" -H 'Content-Type: application/json' -d '{}'
curl -s -X POST "$GMAIL_API_URL/gmail/v1/users/me/messages/<message_id>/trash" -H 'Content-Type: application/json' -d '{}'
curl -s -X DELETE "$GMAIL_API_URL/gmail/v1/users/me/messages/<message_id>"
curl -s "$GMAIL_API_URL/gmail/v1/users/me/threads"
curl -s "$GMAIL_API_URL/gmail/v1/users/me/threads/<thread_id>"
curl -s "$GMAIL_API_URL/gmail/v1/users/me/drafts"
curl -s "$GMAIL_API_URL/gmail/v1/users/me/drafts/<draft_id>"
curl -s -X POST "$GMAIL_API_URL/gmail/v1/users/me/drafts" -H 'Content-Type: application/json' -d '{}'
curl -s -X POST "$GMAIL_API_URL/gmail/v1/users/me/drafts/<draft_id>/send" -H 'Content-Type: application/json' -d '{}'
```

The audit log of every call is available at `$GMAIL_API_URL/audit/requests` (used for grading).
