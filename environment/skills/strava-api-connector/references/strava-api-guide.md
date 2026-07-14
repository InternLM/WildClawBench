# Strava API (Mock) Guide

Worked `curl` examples for every endpoint. **All requests target the base URL in `$STRAVA_API_URL`.** Auth headers are mocked (any token is accepted) and responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `STRAVA_API_URL` | Base URL for all requests |

## Api

```bash
curl -s "$STRAVA_API_URL/api/v3/athlete"
curl -s "$STRAVA_API_URL/api/v3/athlete/activities"
curl -s "$STRAVA_API_URL/api/v3/athletes/<athlete_id>/stats"
curl -s "$STRAVA_API_URL/api/v3/activities/<activity_id>"
curl -s -X PUT "$STRAVA_API_URL/api/v3/activities/<activity_id>" -H 'Content-Type: application/json' -d '{}'
curl -s "$STRAVA_API_URL/api/v3/activities/<activity_id>/kudos"
curl -s "$STRAVA_API_URL/api/v3/segments/<segment_id>"
```

The audit log of every call is available at `$STRAVA_API_URL/audit/requests` (used for grading).
