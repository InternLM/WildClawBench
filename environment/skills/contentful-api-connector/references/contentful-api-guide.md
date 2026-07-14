# Contentful API (Mock) Guide

Worked `curl` examples for every endpoint. **All requests target the base URL in `$CONTENTFUL_API_URL`.** Auth headers are mocked (any token is accepted) and responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `CONTENTFUL_API_URL` | Base URL for all requests |

## Spaces

```bash
curl -s "$CONTENTFUL_API_URL/spaces/<space_id>"
curl -s "$CONTENTFUL_API_URL/spaces/<space_id>/environments/<env_id>/content_types"
curl -s "$CONTENTFUL_API_URL/spaces/<space_id>/environments/<env_id>/content_types/<content_type_id>"
curl -s "$CONTENTFUL_API_URL/spaces/<space_id>/environments/<env_id>/entries"
curl -s "$CONTENTFUL_API_URL/spaces/<space_id>/environments/<env_id>/entries/<entry_id>"
curl -s -X POST "$CONTENTFUL_API_URL/spaces/<space_id>/environments/<env_id>/entries" -H 'Content-Type: application/json' -d '{}'
curl -s -X PUT "$CONTENTFUL_API_URL/spaces/<space_id>/environments/<env_id>/entries/<entry_id>" -H 'Content-Type: application/json' -d '{}'
curl -s -X DELETE "$CONTENTFUL_API_URL/spaces/<space_id>/environments/<env_id>/entries/<entry_id>"
curl -s "$CONTENTFUL_API_URL/spaces/<space_id>/environments/<env_id>/assets"
curl -s "$CONTENTFUL_API_URL/spaces/<space_id>/environments/<env_id>/assets/<asset_id>"
```

The audit log of every call is available at `$CONTENTFUL_API_URL/audit/requests` (used for grading).
