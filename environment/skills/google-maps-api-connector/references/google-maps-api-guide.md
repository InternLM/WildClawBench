# Google Maps API (Mock) Guide

Worked `curl` examples for every endpoint. **All requests target the base URL in `$GOOGLE_MAPS_API_URL`.** Auth headers are mocked (any token is accepted) and responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `GOOGLE_MAPS_API_URL` | Base URL for all requests |

## Maps

```bash
curl -s "$GOOGLE_MAPS_API_URL/maps/api/place/textsearch/json"
curl -s "$GOOGLE_MAPS_API_URL/maps/api/place/details/json"
curl -s "$GOOGLE_MAPS_API_URL/maps/api/place/nearbysearch/json"
curl -s "$GOOGLE_MAPS_API_URL/maps/api/geocode/json"
curl -s "$GOOGLE_MAPS_API_URL/maps/api/directions/json"
curl -s "$GOOGLE_MAPS_API_URL/maps/api/distancematrix/json"
```

The audit log of every call is available at `$GOOGLE_MAPS_API_URL/audit/requests` (used for grading).
