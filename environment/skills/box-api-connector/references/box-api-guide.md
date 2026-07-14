# Box API (Mock) Guide

Worked `curl` examples for every endpoint. **All requests target the base URL in `$BOX_API_URL`.** Auth headers are mocked (any token is accepted) and responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `BOX_API_URL` | Base URL for all requests |

## 2.0

```bash
curl -s "$BOX_API_URL/2.0/users/me"
curl -s "$BOX_API_URL/2.0/folders/<folder_id>"
curl -s "$BOX_API_URL/2.0/folders/<folder_id>/items"
curl -s "$BOX_API_URL/2.0/files/<file_id>"
curl -s "$BOX_API_URL/2.0/search"
```

The audit log of every call is available at `$BOX_API_URL/audit/requests` (used for grading).
