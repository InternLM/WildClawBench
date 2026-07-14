# Microsoft Teams API (Mock) Guide

Worked `curl` examples for every endpoint. **All requests target the base URL in `$MICROSOFT_TEAMS_API_URL`.** Auth headers are mocked (any token is accepted) and responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `MICROSOFT_TEAMS_API_URL` | Base URL for all requests |

## V1.0

```bash
curl -s "$MICROSOFT_TEAMS_API_URL/v1.0/me/joinedTeams"
curl -s "$MICROSOFT_TEAMS_API_URL/v1.0/teams/<team_id>"
curl -s "$MICROSOFT_TEAMS_API_URL/v1.0/teams/<team_id>/channels"
curl -s "$MICROSOFT_TEAMS_API_URL/v1.0/teams/<team_id>/channels/<channel_id>/messages"
curl -s -X POST "$MICROSOFT_TEAMS_API_URL/v1.0/teams/<team_id>/channels/<channel_id>/messages" -H 'Content-Type: application/json' -d '{}'
```

The audit log of every call is available at `$MICROSOFT_TEAMS_API_URL/audit/requests` (used for grading).
