---
name: gmail-api-connector
description: >
  Gmail API (Mock) mock HTTP API. Base URL is provided via the
  `GMAIL_API_URL` environment variable. 16 endpoint(s) across DELETE, GET, POST.
metadata: {"clawdbot":{"emoji":"🔌"}}
---

# Gmail API (Mock)

Mock HTTP API. **All requests go to the base URL in `$GMAIL_API_URL`.** Auth headers
are mocked (any token is accepted). Responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `GMAIL_API_URL` | Base URL for all requests (e.g. `http://gmail-api:8017`) |

## Endpoints

| Method | Path |
|--------|------|
| GET | `/gmail/v1/users/me/profile` |
| GET | `/gmail/v1/users/me/labels` |
| GET | `/gmail/v1/users/me/labels/{label_id}` |
| POST | `/gmail/v1/users/me/labels` |
| GET | `/gmail/v1/users/me/messages` |
| GET | `/gmail/v1/users/me/messages/{message_id}` |
| POST | `/gmail/v1/users/me/messages/send` |
| POST | `/gmail/v1/users/me/messages/{message_id}/modify` |
| POST | `/gmail/v1/users/me/messages/{message_id}/trash` |
| DELETE | `/gmail/v1/users/me/messages/{message_id}` |
| GET | `/gmail/v1/users/me/threads` |
| GET | `/gmail/v1/users/me/threads/{thread_id}` |
| GET | `/gmail/v1/users/me/drafts` |
| GET | `/gmail/v1/users/me/drafts/{draft_id}` |
| POST | `/gmail/v1/users/me/drafts` |
| POST | `/gmail/v1/users/me/drafts/{draft_id}/send` |

## Usage

```bash
# GET example
curl -s "$GMAIL_API_URL/gmail/v1/users/me/profile"

# POST example
curl -s -X POST "$GMAIL_API_URL/gmail/v1/users/me/profile" -H 'Content-Type: application/json' -d '{}'
```

The audit log of every call the agent makes is available at
`$GMAIL_API_URL/audit/requests` (used for grading).
