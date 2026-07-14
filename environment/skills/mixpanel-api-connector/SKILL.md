---
name: mixpanel-api-connector
description: >
  Mixpanel API (Mock) mock HTTP API. Base URL is provided via the
  `MIXPANEL_API_URL` environment variable. 6 endpoint(s) across GET, POST.
metadata: {"clawdbot":{"emoji":"🔌"}}
---

# Mixpanel API (Mock)

Mock HTTP API. **All requests go to the base URL in `$MIXPANEL_API_URL`.** Auth headers
are mocked (any token is accepted). Responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `MIXPANEL_API_URL` | Base URL for all requests (e.g. `http://mixpanel-api:8056`) |

## Endpoints

| Method | Path |
|--------|------|
| POST | `/track` |
| GET | `/api/2.0/events` |
| GET | `/api/2.0/funnels/list` |
| GET | `/api/2.0/funnels` |
| GET | `/api/2.0/segmentation` |
| GET | `/api/2.0/engage` |

## Usage

```bash
# GET example
curl -s "$MIXPANEL_API_URL/track"

# POST example
curl -s -X POST "$MIXPANEL_API_URL/track" -H 'Content-Type: application/json' -d '{}'
```

The audit log of every call the agent makes is available at
`$MIXPANEL_API_URL/audit/requests` (used for grading).
