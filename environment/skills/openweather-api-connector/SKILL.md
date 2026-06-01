---
name: openweather-api-connector
description: >
  OpenWeather API (Mock) mock HTTP API. Base URL is provided via the
  `OPENWEATHER_API_URL` environment variable. 3 endpoint(s) across GET.
metadata: {"clawdbot":{"emoji":"🔌"}}
---

# OpenWeather API (Mock)

Mock HTTP API. **All requests go to the base URL in `$OPENWEATHER_API_URL`.** Auth headers
are mocked (any token is accepted). Responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `OPENWEATHER_API_URL` | Base URL for all requests (e.g. `http://openweather-api:8035`) |

## Endpoints

| Method | Path |
|--------|------|
| GET | `/data/2.5/weather` |
| GET | `/data/2.5/forecast` |
| GET | `/geo/1.0/direct` |

## Usage

```bash
# GET example
curl -s "$OPENWEATHER_API_URL/data/2.5/weather"

# POST example
curl -s -X POST "$OPENWEATHER_API_URL/data/2.5/weather" -H 'Content-Type: application/json' -d '{}'
```

The audit log of every call the agent makes is available at
`$OPENWEATHER_API_URL/audit/requests` (used for grading).
