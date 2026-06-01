---
name: gitlab-api-connector
description: >
  GitLab API (Mock) mock HTTP API. Base URL is provided via the
  `GITLAB_API_URL` environment variable. 11 endpoint(s) across GET, POST, PUT.
metadata: {"clawdbot":{"emoji":"🔌"}}
---

# GitLab API (Mock)

Mock HTTP API. **All requests go to the base URL in `$GITLAB_API_URL`.** Auth headers
are mocked (any token is accepted). Responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `GITLAB_API_URL` | Base URL for all requests (e.g. `http://gitlab-api:8046`) |

## Endpoints

| Method | Path |
|--------|------|
| GET | `/api/v4/user` |
| GET | `/api/v4/projects` |
| GET | `/api/v4/projects/{project_id}` |
| GET | `/api/v4/projects/{project_id}/issues` |
| GET | `/api/v4/projects/{project_id}/issues/{issue_iid}` |
| POST | `/api/v4/projects/{project_id}/issues` |
| PUT | `/api/v4/projects/{project_id}/issues/{issue_iid}` |
| GET | `/api/v4/projects/{project_id}/merge_requests` |
| POST | `/api/v4/projects/{project_id}/merge_requests` |
| PUT | `/api/v4/projects/{project_id}/merge_requests/{mr_iid}/merge` |
| GET | `/api/v4/projects/{project_id}/pipelines` |

## Usage

```bash
# GET example
curl -s "$GITLAB_API_URL/api/v4/user"

# POST example
curl -s -X POST "$GITLAB_API_URL/api/v4/user" -H 'Content-Type: application/json' -d '{}'
```

The audit log of every call the agent makes is available at
`$GITLAB_API_URL/audit/requests` (used for grading).
