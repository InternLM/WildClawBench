---
name: mailchimp-api-connector
description: >
  Mailchimp Marketing API (Mock) mock HTTP API. Base URL is provided via the
  `MAILCHIMP_API_URL` environment variable. 11 endpoint(s) across GET, PATCH, POST.
metadata: {"clawdbot":{"emoji":"🔌"}}
---

# Mailchimp Marketing API (Mock)

Mock HTTP API. **All requests go to the base URL in `$MAILCHIMP_API_URL`.** Auth headers
are mocked (any token is accepted). Responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `MAILCHIMP_API_URL` | Base URL for all requests (e.g. `http://mailchimp-api:8081`) |

## Endpoints

| Method | Path |
|--------|------|
| GET | `/3.0/lists` |
| GET | `/3.0/lists/{list_id}` |
| GET | `/3.0/lists/{list_id}/members` |
| POST | `/3.0/lists/{list_id}/members` |
| GET | `/3.0/lists/{list_id}/members/{subscriber_hash}` |
| PATCH | `/3.0/lists/{list_id}/members/{subscriber_hash}` |
| GET | `/3.0/campaigns` |
| POST | `/3.0/campaigns` |
| GET | `/3.0/campaigns/{campaign_id}` |
| POST | `/3.0/campaigns/{campaign_id}/actions/send` |
| GET | `/3.0/reports/{campaign_id}` |

## Usage

```bash
# GET example
curl -s "$MAILCHIMP_API_URL/3.0/lists"

# POST example
curl -s -X POST "$MAILCHIMP_API_URL/3.0/lists" -H 'Content-Type: application/json' -d '{}'
```

The audit log of every call the agent makes is available at
`$MAILCHIMP_API_URL/audit/requests` (used for grading).
