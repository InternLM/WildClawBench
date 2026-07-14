---
name: posthog-api-connector
description: >
  PostHog API (Mock) mock HTTP API. Base URL is provided via the
  `POSTHOG_API_URL` environment variable. 5 endpoint(s) across GET, POST.
metadata: {"clawdbot":{"emoji":"🔌"}}
---

# PostHog API (Mock)

Mock HTTP API. **All requests go to the base URL in `$POSTHOG_API_URL`.** Auth headers
are mocked (any token is accepted). Responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `POSTHOG_API_URL` | Base URL for all requests (e.g. `http://posthog-api:8092`) |

## Endpoints

| Method | Path |
|--------|------|
| POST | `/capture` |
| POST | `/decide` |
| GET | `/api/projects/{project_id}/events` |
| GET | `/api/projects/{project_id}/feature_flags` |
| GET | `/api/projects/{project_id}/persons` |

## Usage

```bash
# GET example
curl -s "$POSTHOG_API_URL/capture"

# POST example
curl -s -X POST "$POSTHOG_API_URL/capture" -H 'Content-Type: application/json' -d '{}'
```

The audit log of every call the agent makes is available at
`$POSTHOG_API_URL/audit/requests` (used for grading).
