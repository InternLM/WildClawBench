---
name: slack-api-connector
description: >
  Slack Web API (Mock) mock HTTP API. Base URL is provided via the
  `SLACK_API_URL` environment variable. 19 endpoint(s) across GET, POST.
metadata: {"clawdbot":{"emoji":"🔌"}}
---

# Slack Web API (Mock)

Mock HTTP API. **All requests go to the base URL in `$SLACK_API_URL`.** Auth headers
are mocked (any token is accepted). Responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `SLACK_API_URL` | Base URL for all requests (e.g. `http://slack-api:8013`) |

## Endpoints

| Method | Path |
|--------|------|
| GET | `/api/auth.test` |
| POST | `/api/auth.test` |
| GET | `/api/team.info` |
| GET | `/api/users.list` |
| GET | `/api/users.info` |
| POST | `/api/users.setPresence` |
| GET | `/api/conversations.list` |
| GET | `/api/conversations.info` |
| POST | `/api/conversations.create` |
| POST | `/api/conversations.archive` |
| GET | `/api/conversations.members` |
| POST | `/api/conversations.invite` |
| GET | `/api/conversations.history` |
| GET | `/api/conversations.replies` |
| POST | `/api/chat.postMessage` |
| POST | `/api/chat.update` |
| POST | `/api/chat.delete` |
| POST | `/api/reactions.add` |
| GET | `/api/search.messages` |

## Usage

```bash
# GET example
curl -s "$SLACK_API_URL/api/auth.test"

# POST example
curl -s -X POST "$SLACK_API_URL/api/auth.test" -H 'Content-Type: application/json' -d '{}'
```

The audit log of every call the agent makes is available at
`$SLACK_API_URL/audit/requests` (used for grading).
