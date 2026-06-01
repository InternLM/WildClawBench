---
name: klaviyo-api-connector
description: >
  Klaviyo API (Mock) mock HTTP API. Base URL is provided via the
  `KLAVIYO_API_URL` environment variable. 5 endpoint(s) across GET, POST.
metadata: {"clawdbot":{"emoji":"🔌"}}
---

# Klaviyo API (Mock)

Mock HTTP API. **All requests go to the base URL in `$KLAVIYO_API_URL`.** Auth headers
are mocked (any token is accepted). Responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `KLAVIYO_API_URL` | Base URL for all requests (e.g. `http://klaviyo-api:8089`) |

## Endpoints

| Method | Path |
|--------|------|
| GET | `/api/profiles` |
| GET | `/api/profiles/{profile_id}` |
| POST | `/api/profiles` |
| GET | `/api/lists` |
| GET | `/api/campaigns` |

## Usage

```bash
# GET example
curl -s "$KLAVIYO_API_URL/api/profiles"

# POST example
curl -s -X POST "$KLAVIYO_API_URL/api/profiles" -H 'Content-Type: application/json' -d '{}'
```

The audit log of every call the agent makes is available at
`$KLAVIYO_API_URL/audit/requests` (used for grading).
