# OpenWeather API (Mock) Guide

Worked `curl` examples for every endpoint. **All requests target the base URL in `$OPENWEATHER_API_URL`.** Auth headers are mocked (any token is accepted) and responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `OPENWEATHER_API_URL` | Base URL for all requests |

## Data

```bash
curl -s "$OPENWEATHER_API_URL/data/2.5/weather"
curl -s "$OPENWEATHER_API_URL/data/2.5/forecast"
```

## Geo

```bash
curl -s "$OPENWEATHER_API_URL/geo/1.0/direct"
```

The audit log of every call is available at `$OPENWEATHER_API_URL/audit/requests` (used for grading).
