---
name: google-maps-api-connector
description: >
  Google Maps API (Mock) mock HTTP API. Base URL is provided via the
  `GOOGLE_MAPS_API_URL` environment variable. 6 endpoint(s) across GET.
metadata: {"clawdbot":{"emoji":"🔌"}}
---

# Google Maps API (Mock)

Mock HTTP API. **All requests go to the base URL in `$GOOGLE_MAPS_API_URL`.** Auth headers
are mocked (any token is accepted). Responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `GOOGLE_MAPS_API_URL` | Base URL for all requests (e.g. `http://google-maps-api:8033`) |

## Endpoints

| Method | Path |
|--------|------|
| GET | `/maps/api/place/textsearch/json` |
| GET | `/maps/api/place/details/json` |
| GET | `/maps/api/place/nearbysearch/json` |
| GET | `/maps/api/geocode/json` |
| GET | `/maps/api/directions/json` |
| GET | `/maps/api/distancematrix/json` |

## Usage

```bash
# GET example
curl -s "$GOOGLE_MAPS_API_URL/maps/api/place/textsearch/json"

# POST example
curl -s -X POST "$GOOGLE_MAPS_API_URL/maps/api/place/textsearch/json" -H 'Content-Type: application/json' -d '{}'
```

The audit log of every call the agent makes is available at
`$GOOGLE_MAPS_API_URL/audit/requests` (used for grading).
