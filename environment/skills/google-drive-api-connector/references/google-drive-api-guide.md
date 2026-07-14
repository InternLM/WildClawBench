# Google Drive API (Mock) Guide

Worked `curl` examples for every endpoint. **All requests target the base URL in `$GOOGLE_DRIVE_API_URL`.** Auth headers are mocked (any token is accepted) and responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `GOOGLE_DRIVE_API_URL` | Base URL for all requests |

## Drive

```bash
curl -s "$GOOGLE_DRIVE_API_URL/drive/v3/about"
curl -s "$GOOGLE_DRIVE_API_URL/drive/v3/files"
curl -s "$GOOGLE_DRIVE_API_URL/drive/v3/files/<file_id>"
curl -s -X POST "$GOOGLE_DRIVE_API_URL/drive/v3/files" -H 'Content-Type: application/json' -d '{}'
curl -s -X PATCH "$GOOGLE_DRIVE_API_URL/drive/v3/files/<file_id>" -H 'Content-Type: application/json' -d '{}'
curl -s -X POST "$GOOGLE_DRIVE_API_URL/drive/v3/files/<file_id>/trash" -H 'Content-Type: application/json' -d '{}'
curl -s -X DELETE "$GOOGLE_DRIVE_API_URL/drive/v3/files/<file_id>"
curl -s "$GOOGLE_DRIVE_API_URL/drive/v3/files/<file_id>/permissions"
curl -s -X POST "$GOOGLE_DRIVE_API_URL/drive/v3/files/<file_id>/permissions" -H 'Content-Type: application/json' -d '{}'
curl -s -X DELETE "$GOOGLE_DRIVE_API_URL/drive/v3/files/<file_id>/permissions/<permission_id>"
```

The audit log of every call is available at `$GOOGLE_DRIVE_API_URL/audit/requests` (used for grading).
