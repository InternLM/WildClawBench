# Jira API (Mock) Guide

Worked `curl` examples for every endpoint. **All requests target the base URL in `$JIRA_API_URL`.** Auth headers are mocked (any token is accepted) and responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `JIRA_API_URL` | Base URL for all requests |

## Rest

```bash
curl -s "$JIRA_API_URL/rest/api/3/project"
curl -s -X POST "$JIRA_API_URL/rest/api/3/issue" -H 'Content-Type: application/json' -d '{}'
curl -s "$JIRA_API_URL/rest/api/3/issue/<issue_key>"
curl -s -X PUT "$JIRA_API_URL/rest/api/3/issue/<issue_key>" -H 'Content-Type: application/json' -d '{}'
curl -s "$JIRA_API_URL/rest/api/3/issue/<issue_key>/transitions"
curl -s -X POST "$JIRA_API_URL/rest/api/3/issue/<issue_key>/transitions" -H 'Content-Type: application/json' -d '{}'
curl -s "$JIRA_API_URL/rest/api/3/search"
curl -s "$JIRA_API_URL/rest/agile/1.0/board"
curl -s "$JIRA_API_URL/rest/agile/1.0/board/<board_id>/sprint"
```

The audit log of every call is available at `$JIRA_API_URL/audit/requests` (used for grading).
