---
name: yelp-api-connector
description: >
  Yelp Fusion API (Mock) mock HTTP API. Base URL is provided via the
  `YELP_API_URL` environment variable. 4 endpoint(s) across GET.
metadata: {"clawdbot":{"emoji":"🔌"}}
---

# Yelp Fusion API (Mock)

Mock HTTP API. **All requests go to the base URL in `$YELP_API_URL`.** Auth headers
are mocked (any token is accepted). Responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `YELP_API_URL` | Base URL for all requests (e.g. `http://yelp-api:8034`) |

## Endpoints

| Method | Path |
|--------|------|
| GET | `/v3/businesses/search` |
| GET | `/v3/businesses/{business_id}` |
| GET | `/v3/businesses/{business_id}/reviews` |
| GET | `/v3/categories` |

## Usage

```bash
# GET example
curl -s "$YELP_API_URL/v3/businesses/search"

# POST example
curl -s -X POST "$YELP_API_URL/v3/businesses/search" -H 'Content-Type: application/json' -d '{}'
```

The audit log of every call the agent makes is available at
`$YELP_API_URL/audit/requests` (used for grading).
