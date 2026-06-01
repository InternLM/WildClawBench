---
name: obsidian-api-connector
description: >
  Obsidian API (Mock) mock HTTP API. Base URL is provided via the
  `OBSIDIAN_API_URL` environment variable. 9 endpoint(s) across DELETE, GET, POST, PUT.
metadata: {"clawdbot":{"emoji":"🔌"}}
---

# Obsidian API (Mock)

Mock HTTP API. **All requests go to the base URL in `$OBSIDIAN_API_URL`.** Auth headers
are mocked (any token is accepted). Responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `OBSIDIAN_API_URL` | Base URL for all requests (e.g. `http://obsidian-api:8014`) |

## Endpoints

| Method | Path |
|--------|------|
| GET | `/vault` |
| GET | `/vault/notes` |
| GET | `/vault/notes/{path:path}` |
| POST | `/vault/notes` |
| PUT | `/vault/notes/{path:path}` |
| DELETE | `/vault/notes/{path:path}` |
| GET | `/vault/search` |
| GET | `/vault/backlinks/{path:path}` |
| GET | `/vault/daily/{date_str}` |

## Usage

```bash
# GET example
curl -s "$OBSIDIAN_API_URL/vault"

# POST example
curl -s -X POST "$OBSIDIAN_API_URL/vault" -H 'Content-Type: application/json' -d '{}'
```

The audit log of every call the agent makes is available at
`$OBSIDIAN_API_URL/audit/requests` (used for grading).
