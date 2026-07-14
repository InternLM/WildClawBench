---
name: jira-api-connector
description: >
  Jira API (Mock) mock HTTP API. Base URL is provided via the
  `JIRA_API_URL` environment variable. 9 endpoint(s) across GET, POST, PUT.
metadata: {"clawdbot":{"emoji":"🔌"}}
---

# Jira API (Mock)

Mock HTTP API. **All requests go to the base URL in `$JIRA_API_URL`.** Auth headers
are mocked (any token is accepted). Responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `JIRA_API_URL` | Base URL for all requests (e.g. `http://jira-api:8029`) |

## Endpoints

| Method | Path |
|--------|------|
| GET | `/rest/api/3/project` |
| POST | `/rest/api/3/issue` |
| GET | `/rest/api/3/issue/{issue_key}` |
| PUT | `/rest/api/3/issue/{issue_key}` |
| GET | `/rest/api/3/issue/{issue_key}/transitions` |
| POST | `/rest/api/3/issue/{issue_key}/transitions` |
| GET | `/rest/api/3/search` |
| GET | `/rest/agile/1.0/board` |
| GET | `/rest/agile/1.0/board/{board_id}/sprint` |

## Usage

```bash
# GET example
curl -s "$JIRA_API_URL/rest/api/3/project"

# POST example
curl -s -X POST "$JIRA_API_URL/rest/api/3/project" -H 'Content-Type: application/json' -d '{}'
```

The audit log of every call the agent makes is available at
`$JIRA_API_URL/audit/requests` (used for grading).
