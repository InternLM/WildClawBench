# Ticketmaster Discovery API (Mock) Guide

Worked `curl` examples for every endpoint. **All requests target the base URL in `$TICKETMASTER_API_URL`.** Auth headers are mocked (any token is accepted) and responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `TICKETMASTER_API_URL` | Base URL for all requests |

## Discovery

```bash
curl -s "$TICKETMASTER_API_URL/discovery/v2/events"
curl -s "$TICKETMASTER_API_URL/discovery/v2/events/<event_id>"
curl -s "$TICKETMASTER_API_URL/discovery/v2/venues"
curl -s "$TICKETMASTER_API_URL/discovery/v2/venues/<venue_id>"
curl -s "$TICKETMASTER_API_URL/discovery/v2/attractions"
curl -s "$TICKETMASTER_API_URL/discovery/v2/attractions/<attraction_id>"
curl -s "$TICKETMASTER_API_URL/discovery/v2/classifications"
```

The audit log of every call is available at `$TICKETMASTER_API_URL/audit/requests` (used for grading).
