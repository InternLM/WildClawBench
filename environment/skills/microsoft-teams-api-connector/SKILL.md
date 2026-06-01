---
name: microsoft-teams-api-connector
description: >
  Microsoft Teams API (Mock) mock HTTP API. Base URL is provided via the
  `MICROSOFT_TEAMS_API_URL` environment variable. 5 endpoint(s) across GET, POST.
metadata: {"clawdbot":{"emoji":"🔌"}}
---

# Microsoft Teams API (Mock)

Mock HTTP API. **All requests go to the base URL in `$MICROSOFT_TEAMS_API_URL`.** Auth headers
are mocked (any token is accepted). Responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `MICROSOFT_TEAMS_API_URL` | Base URL for all requests (e.g. `http://microsoft-teams-api:8086`) |

## Endpoints

| Method | Path |
|--------|------|
| GET | `/v1.0/me/joinedTeams` |
| GET | `/v1.0/teams/{team_id}` |
| GET | `/v1.0/teams/{team_id}/channels` |
| GET | `/v1.0/teams/{team_id}/channels/{channel_id}/messages` |
| POST | `/v1.0/teams/{team_id}/channels/{channel_id}/messages` |

## Usage

```bash
# GET example
curl -s "$MICROSOFT_TEAMS_API_URL/v1.0/me/joinedTeams"

# POST example
curl -s -X POST "$MICROSOFT_TEAMS_API_URL/v1.0/me/joinedTeams" -H 'Content-Type: application/json' -d '{}'
```

The audit log of every call the agent makes is available at
`$MICROSOFT_TEAMS_API_URL/audit/requests` (used for grading).
