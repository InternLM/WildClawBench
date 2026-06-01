---
name: amadeus-api-connector
description: >
  Amadeus API (Mock) mock HTTP API. Base URL is provided via the
  `AMADEUS_API_URL` environment variable. 5 endpoint(s) across GET, POST.
metadata: {"clawdbot":{"emoji":"🔌"}}
---

# Amadeus API (Mock)

Mock HTTP API. **All requests go to the base URL in `$AMADEUS_API_URL`.** Auth headers
are mocked (any token is accepted). Responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `AMADEUS_API_URL` | Base URL for all requests (e.g. `http://amadeus-api:8076`) |

## Endpoints

| Method | Path |
|--------|------|
| GET | `/v2/shopping/flight-offers` |
| POST | `/v1/shopping/flight-offers/pricing` |
| GET | `/v1/reference-data/locations` |
| GET | `/v1/reference-data/locations/{location_id}` |
| GET | `/v1/reference-data/airlines` |

## Usage

```bash
# GET example
curl -s "$AMADEUS_API_URL/v2/shopping/flight-offers"

# POST example
curl -s -X POST "$AMADEUS_API_URL/v2/shopping/flight-offers" -H 'Content-Type: application/json' -d '{}'
```

The audit log of every call the agent makes is available at
`$AMADEUS_API_URL/audit/requests` (used for grading).
