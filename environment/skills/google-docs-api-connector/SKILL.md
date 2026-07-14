---
name: google-docs-api-connector
description: >
  Google Docs API (Mock) mock HTTP API. Base URL is provided via the `GOOGLE_DOCS_API_URL` environment
  variable. Auth headers are mocked (any token accepted); responses are
  deterministic fixtures backed by the task's mock_data.
metadata: {"clawdbot":{"emoji":"🔌"}}
---

# Google Docs API (Mock)

Mock HTTP API. **All requests go to the base URL in `$GOOGLE_DOCS_API_URL`.**

## Base URL

| Variable | Purpose |
|----------|---------|
| `GOOGLE_DOCS_API_URL` | Base URL for all requests (e.g. `http://google-docs-api:8103`) |

## Endpoints

| Method | Path |
|--------|------|
| GET | `/documents` |
| GET | `/documents/{item_id}` |
| POST | `/documents` |
| PATCH | `/documents/{item_id}` |

All list endpoints return `{"<resource>": [ ... ]}`. GET-by-id returns the row
or 404. POST creates; PATCH updates by id.
