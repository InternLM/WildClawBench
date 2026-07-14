# Dropbox API v2 (Mock) Guide

Worked `curl` examples for every endpoint. **All requests target the base URL in `$DROPBOX_API_URL`.** Auth headers are mocked (any token is accepted) and responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `DROPBOX_API_URL` | Base URL for all requests |

## 2

```bash
curl -s -X POST "$DROPBOX_API_URL/2/users/get_current_account" -H 'Content-Type: application/json' -d '{}'
curl -s -X POST "$DROPBOX_API_URL/2/files/list_folder" -H 'Content-Type: application/json' -d '{}'
curl -s -X POST "$DROPBOX_API_URL/2/files/get_metadata" -H 'Content-Type: application/json' -d '{}'
curl -s -X POST "$DROPBOX_API_URL/2/files/search_v2" -H 'Content-Type: application/json' -d '{}'
curl -s -X POST "$DROPBOX_API_URL/2/sharing/list_shared_links" -H 'Content-Type: application/json' -d '{}'
```

The audit log of every call is available at `$DROPBOX_API_URL/audit/requests` (used for grading).
