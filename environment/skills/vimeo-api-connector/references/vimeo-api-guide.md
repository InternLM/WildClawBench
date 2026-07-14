# Vimeo API (Mock) Guide

Worked `curl` examples for every endpoint. **All requests target the base URL in `$VIMEO_API_URL`.** Auth headers are mocked (any token is accepted) and responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `VIMEO_API_URL` | Base URL for all requests |

## Me

```bash
curl -s "$VIMEO_API_URL/me"
curl -s "$VIMEO_API_URL/me/videos"
```

## Users

```bash
curl -s "$VIMEO_API_URL/users/<user_id>"
curl -s "$VIMEO_API_URL/users/<user_id>/videos"
```

## Videos

```bash
curl -s "$VIMEO_API_URL/videos/<video_id>"
```

The audit log of every call is available at `$VIMEO_API_URL/audit/requests` (used for grading).
