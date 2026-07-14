# Airtable API (Mock) Guide

Worked `curl` examples for every endpoint. **All requests target the base URL in `$AIRTABLE_API_URL`.** Auth headers are mocked (any token is accepted) and responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `AIRTABLE_API_URL` | Base URL for all requests |

## Meta

```bash
curl -s "$AIRTABLE_API_URL/v0/meta/bases"
curl -s "$AIRTABLE_API_URL/v0/meta/bases/<base_id>/tables"
```

## Root

```bash
curl -s "$AIRTABLE_API_URL/v0/<base_id>/<table_id_or_name>"
curl -s "$AIRTABLE_API_URL/v0/<base_id>/<table_id_or_name>/<record_id>"
curl -s -X POST "$AIRTABLE_API_URL/v0/<base_id>/<table_id_or_name>" -H 'Content-Type: application/json' -d '{}'
curl -s -X PATCH "$AIRTABLE_API_URL/v0/<base_id>/<table_id_or_name>/<record_id>" -H 'Content-Type: application/json' -d '{}'
curl -s -X DELETE "$AIRTABLE_API_URL/v0/<base_id>/<table_id_or_name>/<record_id>"
```

The audit log of every call is available at `$AIRTABLE_API_URL/audit/requests` (used for grading).
