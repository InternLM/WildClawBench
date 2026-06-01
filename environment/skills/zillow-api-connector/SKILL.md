---
name: zillow-api-connector
description: >
  Zillow API (Mock) mock HTTP API. Base URL is provided via the
  `ZILLOW_API_URL` environment variable. 9 endpoint(s) across DELETE, GET, POST.
metadata: {"clawdbot":{"emoji":"🔌"}}
---

# Zillow API (Mock)

Mock HTTP API. **All requests go to the base URL in `$ZILLOW_API_URL`.** Auth headers
are mocked (any token is accepted). Responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `ZILLOW_API_URL` | Base URL for all requests (e.g. `http://zillow-api:8011`) |

## Endpoints

| Method | Path |
|--------|------|
| GET | `/v1/properties/search` |
| GET | `/v1/properties/{zpid}` |
| GET | `/v1/properties/{zpid}/zestimate` |
| GET | `/v1/properties/{zpid}/price-history` |
| GET | `/v1/agents` |
| GET | `/v1/agents/{agent_id}` |
| GET | `/v1/users/{user_id}/saved-searches` |
| POST | `/v1/users/{user_id}/saved-searches` |
| DELETE | `/v1/saved-searches/{search_id}` |

## Usage

```bash
# GET example
curl -s "$ZILLOW_API_URL/v1/properties/search"

# POST example
curl -s -X POST "$ZILLOW_API_URL/v1/properties/search" -H 'Content-Type: application/json' -d '{}'
```

The audit log of every call the agent makes is available at
`$ZILLOW_API_URL/audit/requests` (used for grading).
