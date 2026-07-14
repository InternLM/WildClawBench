# Zoom API (Mock) Guide

Worked `curl` examples for every endpoint. **All requests target the base URL in `$ZOOM_API_URL`.** Auth headers are mocked (any token is accepted) and responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `ZOOM_API_URL` | Base URL for all requests |

## Meetings

```bash
curl -s "$ZOOM_API_URL/v2/meetings/<meeting_id>"
curl -s -X PATCH "$ZOOM_API_URL/v2/meetings/<meeting_id>" -H 'Content-Type: application/json' -d '{}'
curl -s -X DELETE "$ZOOM_API_URL/v2/meetings/<meeting_id>"
curl -s "$ZOOM_API_URL/v2/meetings/<meeting_id>/recordings"
curl -s "$ZOOM_API_URL/v2/meetings/<meeting_id>/registrants"
```

## Users

```bash
curl -s "$ZOOM_API_URL/v2/users/me"
curl -s "$ZOOM_API_URL/v2/users/<user_id>/meetings"
curl -s -X POST "$ZOOM_API_URL/v2/users/<user_id>/meetings" -H 'Content-Type: application/json' -d '{}'
```

The audit log of every call is available at `$ZOOM_API_URL/audit/requests` (used for grading).
