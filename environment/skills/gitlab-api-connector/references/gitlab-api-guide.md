# GitLab API (Mock) Guide

Worked `curl` examples for every endpoint. **All requests target the base URL in `$GITLAB_API_URL`.** Auth headers are mocked (any token is accepted) and responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `GITLAB_API_URL` | Base URL for all requests |

## Api

```bash
curl -s "$GITLAB_API_URL/api/v4/user"
curl -s "$GITLAB_API_URL/api/v4/projects"
curl -s "$GITLAB_API_URL/api/v4/projects/<project_id>"
curl -s "$GITLAB_API_URL/api/v4/projects/<project_id>/issues"
curl -s "$GITLAB_API_URL/api/v4/projects/<project_id>/issues/<issue_iid>"
curl -s -X POST "$GITLAB_API_URL/api/v4/projects/<project_id>/issues" -H 'Content-Type: application/json' -d '{}'
curl -s -X PUT "$GITLAB_API_URL/api/v4/projects/<project_id>/issues/<issue_iid>" -H 'Content-Type: application/json' -d '{}'
curl -s "$GITLAB_API_URL/api/v4/projects/<project_id>/merge_requests"
curl -s -X POST "$GITLAB_API_URL/api/v4/projects/<project_id>/merge_requests" -H 'Content-Type: application/json' -d '{}'
curl -s -X PUT "$GITLAB_API_URL/api/v4/projects/<project_id>/merge_requests/<mr_iid>/merge" -H 'Content-Type: application/json' -d '{}'
curl -s "$GITLAB_API_URL/api/v4/projects/<project_id>/pipelines"
```

The audit log of every call is available at `$GITLAB_API_URL/audit/requests` (used for grading).
