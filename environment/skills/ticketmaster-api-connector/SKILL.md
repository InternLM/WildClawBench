---
name: ticketmaster-api-connector
description: >
  Ticketmaster Discovery API (Mock) mock HTTP API. Base URL is provided via the
  `TICKETMASTER_API_URL` environment variable. 7 endpoint(s) across GET.
metadata: {"clawdbot":{"emoji":"🔌"}}
---

# Ticketmaster Discovery API (Mock)

Mock HTTP API. **All requests go to the base URL in `$TICKETMASTER_API_URL`.** Auth headers
are mocked (any token is accepted). Responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `TICKETMASTER_API_URL` | Base URL for all requests (e.g. `http://ticketmaster-api:8075`) |

## Endpoints

| Method | Path |
|--------|------|
| GET | `/discovery/v2/events` |
| GET | `/discovery/v2/events/{event_id}` |
| GET | `/discovery/v2/venues` |
| GET | `/discovery/v2/venues/{venue_id}` |
| GET | `/discovery/v2/attractions` |
| GET | `/discovery/v2/attractions/{attraction_id}` |
| GET | `/discovery/v2/classifications` |

## Usage

```bash
# GET example
curl -s "$TICKETMASTER_API_URL/discovery/v2/events"

# POST example
curl -s -X POST "$TICKETMASTER_API_URL/discovery/v2/events" -H 'Content-Type: application/json' -d '{}'
```

The audit log of every call the agent makes is available at
`$TICKETMASTER_API_URL/audit/requests` (used for grading).
