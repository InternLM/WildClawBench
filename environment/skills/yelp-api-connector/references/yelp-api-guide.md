# Yelp Fusion API (Mock) Guide

Worked `curl` examples for every endpoint. **All requests target the base URL in `$YELP_API_URL`.** Auth headers are mocked (any token is accepted) and responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `YELP_API_URL` | Base URL for all requests |

## Businesses

```bash
curl -s "$YELP_API_URL/v3/businesses/search"
curl -s "$YELP_API_URL/v3/businesses/<business_id>"
curl -s "$YELP_API_URL/v3/businesses/<business_id>/reviews"
```

## Categories

```bash
curl -s "$YELP_API_URL/v3/categories"
```

The audit log of every call is available at `$YELP_API_URL/audit/requests` (used for grading).
