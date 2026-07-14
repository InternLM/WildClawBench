---
name: sentry-api-connector
description: >
  Sentry API (Mock) mock HTTP API. Base URL is provided via the
  `SENTRY_API_URL` environment variable. 6 endpoint(s) across GET, PUT.
metadata: {"clawdbot":{"emoji":"🔌"}}
---

# Sentry API (Mock)

Mock HTTP API. **All requests go to the base URL in `$SENTRY_API_URL`.** Auth headers
are mocked (any token is accepted). Responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `SENTRY_API_URL` | Base URL for all requests (e.g. `http://sentry-api:8047`) |

## Endpoints

| Method | Path |
|--------|------|
| GET | `/api/0/organizations/{org_slug}/projects/` |
| GET | `/api/0/projects/{org_slug}/{project_slug}/issues/` |
| GET | `/api/0/organizations/{org_slug}/issues/{issue_id}/` |
| PUT | `/api/0/organizations/{org_slug}/issues/{issue_id}/` |
| GET | `/api/0/organizations/{org_slug}/issues/{issue_id}/events/` |
| GET | `/api/0/organizations/{org_slug}/releases/` |

## Usage

```bash
# GET example
curl -s "$SENTRY_API_URL/api/0/organizations/{org_slug}/projects/"

# POST example
curl -s -X POST "$SENTRY_API_URL/api/0/organizations/{org_slug}/projects/" -H 'Content-Type: application/json' -d '{}'
```

The audit log of every call the agent makes is available at
`$SENTRY_API_URL/audit/requests` (used for grading).
