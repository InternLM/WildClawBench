# Google Docs API (Mock) Guide

Worked `curl` examples for every endpoint. **All requests target the base URL in `$GOOGLE_DOCS_API_URL`.** Auth headers are mocked (any token is accepted) and responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `GOOGLE_DOCS_API_URL` | Base URL for all requests |

## Documents

```bash
curl -s "$GOOGLE_DOCS_API_URL/documents"
curl -s "$GOOGLE_DOCS_API_URL/documents/<item_id>"
curl -s -X POST "$GOOGLE_DOCS_API_URL/documents" -H 'Content-Type: application/json' -d '{}'
curl -s -X PATCH "$GOOGLE_DOCS_API_URL/documents/<item_id>" -H 'Content-Type: application/json' -d '{}'
```

The audit log of every call is available at `$GOOGLE_DOCS_API_URL/audit/requests` (used for grading).
