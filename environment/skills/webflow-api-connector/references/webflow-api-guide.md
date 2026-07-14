# Webflow Data API (Mock) Guide

Worked `curl` examples for every endpoint. **All requests target the base URL in `$WEBFLOW_API_URL`.** Auth headers are mocked (any token is accepted) and responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `WEBFLOW_API_URL` | Base URL for all requests |

## Collections

```bash
curl -s "$WEBFLOW_API_URL/v2/collections/<collection_id>/items"
curl -s -X POST "$WEBFLOW_API_URL/v2/collections/<collection_id>/items" -H 'Content-Type: application/json' -d '{}'
```

## Sites

```bash
curl -s "$WEBFLOW_API_URL/v2/sites"
curl -s "$WEBFLOW_API_URL/v2/sites/<site_id>"
curl -s "$WEBFLOW_API_URL/v2/sites/<site_id>/collections"
```

The audit log of every call is available at `$WEBFLOW_API_URL/audit/requests` (used for grading).
