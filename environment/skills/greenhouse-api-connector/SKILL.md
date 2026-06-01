---
name: greenhouse-api-connector
description: >
  Greenhouse Harvest API (Mock) mock HTTP API. Base URL is provided via the
  `GREENHOUSE_API_URL` environment variable. 10 endpoint(s) across GET, POST.
metadata: {"clawdbot":{"emoji":"🔌"}}
---

# Greenhouse Harvest API (Mock)

Mock HTTP API. **All requests go to the base URL in `$GREENHOUSE_API_URL`.** Auth headers
are mocked (any token is accepted). Responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `GREENHOUSE_API_URL` | Base URL for all requests (e.g. `http://greenhouse-api:8073`) |

## Endpoints

| Method | Path |
|--------|------|
| GET | `/v1/candidates` |
| GET | `/v1/candidates/{candidate_id}` |
| POST | `/v1/candidates` |
| GET | `/v1/jobs` |
| GET | `/v1/jobs/{job_id}` |
| GET | `/v1/applications` |
| GET | `/v1/applications/{application_id}` |
| POST | `/v1/applications/{application_id}/advance` |
| POST | `/v1/applications/{application_id}/reject` |
| GET | `/v1/scorecards` |

## Usage

```bash
# GET example
curl -s "$GREENHOUSE_API_URL/v1/candidates"

# POST example
curl -s -X POST "$GREENHOUSE_API_URL/v1/candidates" -H 'Content-Type: application/json' -d '{}'
```

The audit log of every call the agent makes is available at
`$GREENHOUSE_API_URL/audit/requests` (used for grading).
