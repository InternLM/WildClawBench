---
name: segment-api-connector
description: >
  Segment API (Mock) mock HTTP API. Base URL is provided via the
  `SEGMENT_API_URL` environment variable. 7 endpoint(s) across GET, POST.
metadata: {"clawdbot":{"emoji":"🔌"}}
---

# Segment API (Mock)

Mock HTTP API. **All requests go to the base URL in `$SEGMENT_API_URL`.** Auth headers
are mocked (any token is accepted). Responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `SEGMENT_API_URL` | Base URL for all requests (e.g. `http://segment-api:8090`) |

## Endpoints

| Method | Path |
|--------|------|
| POST | `/v1/track` |
| POST | `/v1/identify` |
| POST | `/v1/page` |
| POST | `/v1/batch` |
| GET | `/v1/events` |
| GET | `/v1/sources` |
| GET | `/v1/destinations` |

## Usage

```bash
# GET example
curl -s "$SEGMENT_API_URL/v1/track"

# POST example
curl -s -X POST "$SEGMENT_API_URL/v1/track" -H 'Content-Type: application/json' -d '{}'
```

The audit log of every call the agent makes is available at
`$SEGMENT_API_URL/audit/requests` (used for grading).
