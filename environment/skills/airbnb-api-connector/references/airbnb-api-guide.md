# Airbnb API (Mock) Guide

Worked `curl` examples for every endpoint. **All requests target the base URL in `$AIRBNB_API_URL`.** Auth headers are mocked (any token is accepted) and responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `AIRBNB_API_URL` | Base URL for all requests |

## Listings

```bash
curl -s "$AIRBNB_API_URL/v2/listings/search"
curl -s "$AIRBNB_API_URL/v2/listings/<listing_id>"
curl -s "$AIRBNB_API_URL/v2/listings/<listing_id>/availability"
curl -s "$AIRBNB_API_URL/v2/listings/<listing_id>/reviews"
```

## Reservations

```bash
curl -s -X POST "$AIRBNB_API_URL/v2/reservations" -H 'Content-Type: application/json' -d '{}'
curl -s "$AIRBNB_API_URL/v2/reservations/<reservation_id>"
curl -s -X DELETE "$AIRBNB_API_URL/v2/reservations/<reservation_id>"
```

The audit log of every call is available at `$AIRBNB_API_URL/audit/requests` (used for grading).
