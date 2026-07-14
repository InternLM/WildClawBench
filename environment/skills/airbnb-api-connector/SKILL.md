---
name: airbnb-api-connector
description: >
  Airbnb API (Mock) mock HTTP API. Base URL is provided via the
  `AIRBNB_API_URL` environment variable. 7 endpoint(s) across DELETE, GET, POST.
metadata: {"clawdbot":{"emoji":"🔌"}}
---

# Airbnb API (Mock)

Mock HTTP API. **All requests go to the base URL in `$AIRBNB_API_URL`.** Auth headers
are mocked (any token is accepted). Responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `AIRBNB_API_URL` | Base URL for all requests (e.g. `http://airbnb-api:8038`) |

## Endpoints

| Method | Path |
|--------|------|
| GET | `/v2/listings/search` |
| GET | `/v2/listings/{listing_id}` |
| GET | `/v2/listings/{listing_id}/availability` |
| GET | `/v2/listings/{listing_id}/reviews` |
| POST | `/v2/reservations` |
| GET | `/v2/reservations/{reservation_id}` |
| DELETE | `/v2/reservations/{reservation_id}` |

## Usage

```bash
# GET example
curl -s "$AIRBNB_API_URL/v2/listings/search"

# POST example
curl -s -X POST "$AIRBNB_API_URL/v2/listings/search" -H 'Content-Type: application/json' -d '{}'
```

The audit log of every call the agent makes is available at
`$AIRBNB_API_URL/audit/requests` (used for grading).
