---
name: github-api-connector
description: >
  GitHub REST API (Mock) mock HTTP API. Base URL is provided via the
  `GITHUB_API_URL` environment variable. 13 endpoint(s) across GET, PATCH, POST, PUT.
metadata: {"clawdbot":{"emoji":"🔌"}}
---

# GitHub REST API (Mock)

Mock HTTP API. **All requests go to the base URL in `$GITHUB_API_URL`.** Auth headers
are mocked (any token is accepted). Responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `GITHUB_API_URL` | Base URL for all requests (e.g. `http://github-api:8019`) |

## Endpoints

| Method | Path |
|--------|------|
| GET | `/user` |
| GET | `/users/{owner}/repos` |
| GET | `/orgs/{owner}/repos` |
| GET | `/repos/{owner}/{repo}` |
| GET | `/repos/{owner}/{repo}/issues` |
| GET | `/repos/{owner}/{repo}/issues/{number}` |
| POST | `/repos/{owner}/{repo}/issues` |
| PATCH | `/repos/{owner}/{repo}/issues/{number}` |
| GET | `/repos/{owner}/{repo}/pulls` |
| GET | `/repos/{owner}/{repo}/pulls/{number}` |
| PUT | `/repos/{owner}/{repo}/pulls/{number}/merge` |
| GET | `/repos/{owner}/{repo}/issues/{number}/comments` |
| POST | `/repos/{owner}/{repo}/issues/{number}/comments` |

## Usage

```bash
# GET example
curl -s "$GITHUB_API_URL/user"

# POST example
curl -s -X POST "$GITHUB_API_URL/user" -H 'Content-Type: application/json' -d '{}'
```

The audit log of every call the agent makes is available at
`$GITHUB_API_URL/audit/requests` (used for grading).
