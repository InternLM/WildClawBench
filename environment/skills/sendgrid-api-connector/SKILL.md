---
name: sendgrid-api-connector
description: >
  SendGrid API (Mock) mock HTTP API. Base URL is provided via the
  `SENDGRID_API_URL` environment variable. 8 endpoint(s) across GET, POST.
metadata: {"clawdbot":{"emoji":"🔌"}}
---

# SendGrid API (Mock)

Mock HTTP API. **All requests go to the base URL in `$SENDGRID_API_URL`.** Auth headers
are mocked (any token is accepted). Responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `SENDGRID_API_URL` | Base URL for all requests (e.g. `http://sendgrid-api:8027`) |

## Endpoints

| Method | Path |
|--------|------|
| POST | `/v3/mail/send` |
| GET | `/v3/templates` |
| GET | `/v3/templates/{template_id}` |
| POST | `/v3/templates` |
| GET | `/v3/marketing/contacts` |
| POST | `/v3/marketing/contacts` |
| GET | `/v3/marketing/lists` |
| GET | `/v3/stats` |

## Usage

```bash
# GET example
curl -s "$SENDGRID_API_URL/v3/mail/send"

# POST example
curl -s -X POST "$SENDGRID_API_URL/v3/mail/send" -H 'Content-Type: application/json' -d '{}'
```

The audit log of every call the agent makes is available at
`$SENDGRID_API_URL/audit/requests` (used for grading).
