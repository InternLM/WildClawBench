---
name: strava-api-connector
description: >
  Strava API (Mock) mock HTTP API. Base URL is provided via the
  `STRAVA_API_URL` environment variable. 7 endpoint(s) across GET, PUT.
metadata: {"clawdbot":{"emoji":"🔌"}}
---

# Strava API (Mock)

Mock HTTP API. **All requests go to the base URL in `$STRAVA_API_URL`.** Auth headers
are mocked (any token is accepted). Responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `STRAVA_API_URL` | Base URL for all requests (e.g. `http://strava-api:8060`) |

## Endpoints

| Method | Path |
|--------|------|
| GET | `/api/v3/athlete` |
| GET | `/api/v3/athlete/activities` |
| GET | `/api/v3/athletes/{athlete_id}/stats` |
| GET | `/api/v3/activities/{activity_id}` |
| PUT | `/api/v3/activities/{activity_id}` |
| GET | `/api/v3/activities/{activity_id}/kudos` |
| GET | `/api/v3/segments/{segment_id}` |

## Usage

```bash
# GET example
curl -s "$STRAVA_API_URL/api/v3/athlete"

# POST example
curl -s -X POST "$STRAVA_API_URL/api/v3/athlete" -H 'Content-Type: application/json' -d '{}'
```

The audit log of every call the agent makes is available at
`$STRAVA_API_URL/audit/requests` (used for grading).
