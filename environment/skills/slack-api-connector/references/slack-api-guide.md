# Slack Web API (Mock) Guide

Worked `curl` examples for every endpoint. **All requests target the base URL in `$SLACK_API_URL`.** Auth headers are mocked (any token is accepted) and responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `SLACK_API_URL` | Base URL for all requests |

## Api

```bash
curl -s "$SLACK_API_URL/api/auth.test"
curl -s -X POST "$SLACK_API_URL/api/auth.test" -H 'Content-Type: application/json' -d '{}'
curl -s "$SLACK_API_URL/api/team.info"
curl -s "$SLACK_API_URL/api/users.list"
curl -s "$SLACK_API_URL/api/users.info"
curl -s -X POST "$SLACK_API_URL/api/users.setPresence" -H 'Content-Type: application/json' -d '{}'
curl -s "$SLACK_API_URL/api/conversations.list"
curl -s "$SLACK_API_URL/api/conversations.info"
curl -s -X POST "$SLACK_API_URL/api/conversations.create" -H 'Content-Type: application/json' -d '{}'
curl -s -X POST "$SLACK_API_URL/api/conversations.archive" -H 'Content-Type: application/json' -d '{}'
curl -s "$SLACK_API_URL/api/conversations.members"
curl -s -X POST "$SLACK_API_URL/api/conversations.invite" -H 'Content-Type: application/json' -d '{}'
curl -s "$SLACK_API_URL/api/conversations.history"
curl -s "$SLACK_API_URL/api/conversations.replies"
curl -s -X POST "$SLACK_API_URL/api/chat.postMessage" -H 'Content-Type: application/json' -d '{}'
curl -s -X POST "$SLACK_API_URL/api/chat.update" -H 'Content-Type: application/json' -d '{}'
curl -s -X POST "$SLACK_API_URL/api/chat.delete" -H 'Content-Type: application/json' -d '{}'
curl -s -X POST "$SLACK_API_URL/api/reactions.add" -H 'Content-Type: application/json' -d '{}'
curl -s "$SLACK_API_URL/api/search.messages"
```

The audit log of every call is available at `$SLACK_API_URL/audit/requests` (used for grading).
