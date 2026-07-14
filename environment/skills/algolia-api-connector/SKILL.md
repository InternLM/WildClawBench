---
name: algolia-api-connector
description: >
  Algolia API (Mock) mock HTTP API. Base URL is provided via the
  `ALGOLIA_API_URL` environment variable. 7 endpoint(s) across DELETE, GET, POST, PUT.
metadata: {"clawdbot":{"emoji":"🔌"}}
---

# Algolia API (Mock)

Mock HTTP API. **All requests go to the base URL in `$ALGOLIA_API_URL`.** Auth headers
are mocked (any token is accepted). Responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `ALGOLIA_API_URL` | Base URL for all requests (e.g. `http://algolia-api:8067`) |

## Endpoints

| Method | Path |
|--------|------|
| GET | `/1/indexes` |
| GET | `/1/indexes/{index}/settings` |
| POST | `/1/indexes/{index}/query` |
| GET | `/1/indexes/{index}/{object_id}` |
| POST | `/1/indexes/{index}` |
| PUT | `/1/indexes/{index}/{object_id}` |
| DELETE | `/1/indexes/{index}/{object_id}` |

## Usage

```bash
# GET example
curl -s "$ALGOLIA_API_URL/1/indexes"

# POST example
curl -s -X POST "$ALGOLIA_API_URL/1/indexes" -H 'Content-Type: application/json' -d '{}'
```

The audit log of every call the agent makes is available at
`$ALGOLIA_API_URL/audit/requests` (used for grading).
