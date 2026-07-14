---
name: google-drive-api-connector
description: >
  Google Drive API (Mock) mock HTTP API. Base URL is provided via the
  `GOOGLE_DRIVE_API_URL` environment variable. 10 endpoint(s) across DELETE, GET, PATCH, POST.
metadata: {"clawdbot":{"emoji":"🔌"}}
---

# Google Drive API (Mock)

Mock HTTP API. **All requests go to the base URL in `$GOOGLE_DRIVE_API_URL`.** Auth headers
are mocked (any token is accepted). Responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `GOOGLE_DRIVE_API_URL` | Base URL for all requests (e.g. `http://google-drive-api:8018`) |

## Endpoints

| Method | Path |
|--------|------|
| GET | `/drive/v3/about` |
| GET | `/drive/v3/files` |
| GET | `/drive/v3/files/{file_id}` |
| POST | `/drive/v3/files` |
| PATCH | `/drive/v3/files/{file_id}` |
| POST | `/drive/v3/files/{file_id}/trash` |
| DELETE | `/drive/v3/files/{file_id}` |
| GET | `/drive/v3/files/{file_id}/permissions` |
| POST | `/drive/v3/files/{file_id}/permissions` |
| DELETE | `/drive/v3/files/{file_id}/permissions/{permission_id}` |

## Usage

```bash
# GET example
curl -s "$GOOGLE_DRIVE_API_URL/drive/v3/about"

# POST example
curl -s -X POST "$GOOGLE_DRIVE_API_URL/drive/v3/about" -H 'Content-Type: application/json' -d '{}'
```

The audit log of every call the agent makes is available at
`$GOOGLE_DRIVE_API_URL/audit/requests` (used for grading).
