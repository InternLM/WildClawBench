# Amadeus API (Mock) Guide

Worked `curl` examples for every endpoint. **All requests target the base URL in `$AMADEUS_API_URL`.** Auth headers are mocked (any token is accepted) and responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `AMADEUS_API_URL` | Base URL for all requests |

## Reference Data

```bash
curl -s "$AMADEUS_API_URL/v1/reference-data/locations"
curl -s "$AMADEUS_API_URL/v1/reference-data/locations/<location_id>"
curl -s "$AMADEUS_API_URL/v1/reference-data/airlines"
```

## Shopping

```bash
curl -s "$AMADEUS_API_URL/v2/shopping/flight-offers"
curl -s -X POST "$AMADEUS_API_URL/v1/shopping/flight-offers/pricing" -H 'Content-Type: application/json' -d '{}'
```

The audit log of every call is available at `$AMADEUS_API_URL/audit/requests` (used for grading).
