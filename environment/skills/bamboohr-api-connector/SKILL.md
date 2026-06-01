---
name: bamboohr-api-connector
description: >
  BambooHR API (Mock) mock HTTP API. Base URL is provided via the
  `BAMBOOHR_API_URL` environment variable. 0 endpoint(s) across GET.
metadata: {"clawdbot":{"emoji":"🔌"}}
---

# BambooHR API (Mock)

Mock HTTP API. **All requests go to the base URL in `$BAMBOOHR_API_URL`.** Auth headers
are mocked (any token is accepted). Responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `BAMBOOHR_API_URL` | Base URL for all requests (e.g. `http://bamboohr-api:8072`) |

## Endpoints

| Method | Path |
|--------|------|
| GET | `/` |

## Usage

```bash
# GET example
curl -s "$BAMBOOHR_API_URL/"

# POST example
curl -s -X POST "$BAMBOOHR_API_URL/" -H 'Content-Type: application/json' -d '{}'
```

The audit log of every call the agent makes is available at
`$BAMBOOHR_API_URL/audit/requests` (used for grading).
