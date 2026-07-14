---
name: webflow-api-connector
description: >
  Webflow Data API (Mock) mock HTTP API. Base URL is provided via the
  `WEBFLOW_API_URL` environment variable. 5 endpoint(s) across GET, POST.
metadata: {"clawdbot":{"emoji":"🔌"}}
---

# Webflow Data API (Mock)

Mock HTTP API. **All requests go to the base URL in `$WEBFLOW_API_URL`.** Auth headers
are mocked (any token is accepted). Responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `WEBFLOW_API_URL` | Base URL for all requests (e.g. `http://webflow-api:8100`) |

## Endpoints

| Method | Path |
|--------|------|
| GET | `/v2/sites` |
| GET | `/v2/sites/{site_id}` |
| GET | `/v2/sites/{site_id}/collections` |
| GET | `/v2/collections/{collection_id}/items` |
| POST | `/v2/collections/{collection_id}/items` |

## Usage

```bash
# GET example
curl -s "$WEBFLOW_API_URL/v2/sites"

# POST example
curl -s -X POST "$WEBFLOW_API_URL/v2/sites" -H 'Content-Type: application/json' -d '{}'
```

The audit log of every call the agent makes is available at
`$WEBFLOW_API_URL/audit/requests` (used for grading).
