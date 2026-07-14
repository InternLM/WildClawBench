---
name: openlibrary-api-connector
description: >
  Open Library API (Mock) mock HTTP API. Base URL is provided via the
  `OPENLIBRARY_API_URL` environment variable. 7 endpoint(s) across GET.
metadata: {"clawdbot":{"emoji":"🔌"}}
---

# Open Library API (Mock)

Mock HTTP API. **All requests go to the base URL in `$OPENLIBRARY_API_URL`.** Auth headers
are mocked (any token is accepted). Responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `OPENLIBRARY_API_URL` | Base URL for all requests (e.g. `http://openlibrary-api:8078`) |

## Endpoints

| Method | Path |
|--------|------|
| GET | `/search.json` |
| GET | `/works/{work_id}.json` |
| GET | `/works/{work_id}/editions.json` |
| GET | `/authors/{author_id}.json` |
| GET | `/authors/{author_id}/works.json` |
| GET | `/subjects/{subject}.json` |
| GET | `/isbn/{isbn}.json` |

## Usage

```bash
# GET example
curl -s "$OPENLIBRARY_API_URL/search.json"

# POST example
curl -s -X POST "$OPENLIBRARY_API_URL/search.json" -H 'Content-Type: application/json' -d '{}'
```

The audit log of every call the agent makes is available at
`$OPENLIBRARY_API_URL/audit/requests` (used for grading).
