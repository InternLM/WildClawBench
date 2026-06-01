---
name: confluence-api-connector
description: >
  Confluence Cloud API (Mock) mock HTTP API. Base URL is provided via the
  `CONFLUENCE_API_URL` environment variable. 0 endpoint(s) across GET.
metadata: {"clawdbot":{"emoji":"🔌"}}
---

# Confluence Cloud API (Mock)

Mock HTTP API. **All requests go to the base URL in `$CONFLUENCE_API_URL`.** Auth headers
are mocked (any token is accepted). Responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `CONFLUENCE_API_URL` | Base URL for all requests (e.g. `http://confluence-api:8045`) |

## Endpoints

| Method | Path |
|--------|------|
| GET | `/` |

## Usage

```bash
# GET example
curl -s "$CONFLUENCE_API_URL/"

# POST example
curl -s -X POST "$CONFLUENCE_API_URL/" -H 'Content-Type: application/json' -d '{}'
```

The audit log of every call the agent makes is available at
`$CONFLUENCE_API_URL/audit/requests` (used for grading).
