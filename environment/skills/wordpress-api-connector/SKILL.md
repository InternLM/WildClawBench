---
name: wordpress-api-connector
description: >
  WordPress REST API (Mock) mock HTTP API. Base URL is provided via the
  `WORDPRESS_API_URL` environment variable. 0 endpoint(s) across GET.
metadata: {"clawdbot":{"emoji":"🔌"}}
---

# WordPress REST API (Mock)

Mock HTTP API. **All requests go to the base URL in `$WORDPRESS_API_URL`.** Auth headers
are mocked (any token is accepted). Responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `WORDPRESS_API_URL` | Base URL for all requests (e.g. `http://wordpress-api:8065`) |

## Endpoints

| Method | Path |
|--------|------|
| GET | `/` |

## Usage

```bash
# GET example
curl -s "$WORDPRESS_API_URL/"

# POST example
curl -s -X POST "$WORDPRESS_API_URL/" -H 'Content-Type: application/json' -d '{}'
```

The audit log of every call the agent makes is available at
`$WORDPRESS_API_URL/audit/requests` (used for grading).
