---
name: dropbox-api-connector
description: >
  Dropbox API v2 (Mock) mock HTTP API. Base URL is provided via the
  `DROPBOX_API_URL` environment variable. 5 endpoint(s) across POST.
metadata: {"clawdbot":{"emoji":"🔌"}}
---

# Dropbox API v2 (Mock)

Mock HTTP API. **All requests go to the base URL in `$DROPBOX_API_URL`.** Auth headers
are mocked (any token is accepted). Responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `DROPBOX_API_URL` | Base URL for all requests (e.g. `http://dropbox-api:8082`) |

## Endpoints

| Method | Path |
|--------|------|
| POST | `/2/users/get_current_account` |
| POST | `/2/files/list_folder` |
| POST | `/2/files/get_metadata` |
| POST | `/2/files/search_v2` |
| POST | `/2/sharing/list_shared_links` |

## Usage

```bash
# GET example
curl -s "$DROPBOX_API_URL/2/users/get_current_account"

# POST example
curl -s -X POST "$DROPBOX_API_URL/2/users/get_current_account" -H 'Content-Type: application/json' -d '{}'
```

The audit log of every call the agent makes is available at
`$DROPBOX_API_URL/audit/requests` (used for grading).
