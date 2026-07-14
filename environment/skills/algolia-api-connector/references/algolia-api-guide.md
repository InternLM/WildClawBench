# Algolia API (Mock) Guide

Worked `curl` examples for every endpoint. **All requests target the base URL in `$ALGOLIA_API_URL`.** Auth headers are mocked (any token is accepted) and responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `ALGOLIA_API_URL` | Base URL for all requests |

## 1

```bash
curl -s "$ALGOLIA_API_URL/1/indexes"
curl -s "$ALGOLIA_API_URL/1/indexes/<index>/settings"
curl -s -X POST "$ALGOLIA_API_URL/1/indexes/<index>/query" -H 'Content-Type: application/json' -d '{}'
curl -s "$ALGOLIA_API_URL/1/indexes/<index>/<object_id>"
curl -s -X POST "$ALGOLIA_API_URL/1/indexes/<index>" -H 'Content-Type: application/json' -d '{}'
curl -s -X PUT "$ALGOLIA_API_URL/1/indexes/<index>/<object_id>" -H 'Content-Type: application/json' -d '{}'
curl -s -X DELETE "$ALGOLIA_API_URL/1/indexes/<index>/<object_id>"
```

The audit log of every call is available at `$ALGOLIA_API_URL/audit/requests` (used for grading).
