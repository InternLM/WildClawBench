---
name: linkedin-api-connector
description: >
  LinkedIn API v2 (Mock) mock HTTP API. Base URL is provided via the
  `LINKEDIN_API_URL` environment variable. 8 endpoint(s) across GET, POST.
metadata: {"clawdbot":{"emoji":"🔌"}}
---

# LinkedIn API v2 (Mock)

Mock HTTP API. **All requests go to the base URL in `$LINKEDIN_API_URL`.** Auth headers
are mocked (any token is accepted). Responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `LINKEDIN_API_URL` | Base URL for all requests (e.g. `http://linkedin-api:8062`) |

## Endpoints

| Method | Path |
|--------|------|
| GET | `/v2/me` |
| GET | `/v2/connections` |
| GET | `/v2/posts` |
| POST | `/v2/posts` |
| GET | `/v2/posts/{post_id}` |
| GET | `/v2/organizations/{org_id}` |
| GET | `/v2/jobs` |
| GET | `/v2/jobs/{job_id}` |

## Usage

```bash
# GET example
curl -s "$LINKEDIN_API_URL/v2/me"

# POST example
curl -s -X POST "$LINKEDIN_API_URL/v2/me" -H 'Content-Type: application/json' -d '{}'
```

The audit log of every call the agent makes is available at
`$LINKEDIN_API_URL/audit/requests` (used for grading).
