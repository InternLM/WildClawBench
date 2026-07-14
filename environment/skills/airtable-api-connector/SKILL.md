---
name: airtable-api-connector
description: >
  Airtable API (Mock) mock HTTP API. Base URL is provided via the
  `AIRTABLE_API_URL` environment variable. 7 endpoint(s) across DELETE, GET, PATCH, POST.
metadata: {"clawdbot":{"emoji":"🔌"}}
---

# Airtable API (Mock)

Mock HTTP API. **All requests go to the base URL in `$AIRTABLE_API_URL`.** Auth headers
are mocked (any token is accepted). Responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `AIRTABLE_API_URL` | Base URL for all requests (e.g. `http://airtable-api:8032`) |

## Endpoints

| Method | Path |
|--------|------|
| GET | `/v0/meta/bases` |
| GET | `/v0/meta/bases/{base_id}/tables` |
| GET | `/v0/{base_id}/{table_id_or_name}` |
| GET | `/v0/{base_id}/{table_id_or_name}/{record_id}` |
| POST | `/v0/{base_id}/{table_id_or_name}` |
| PATCH | `/v0/{base_id}/{table_id_or_name}/{record_id}` |
| DELETE | `/v0/{base_id}/{table_id_or_name}/{record_id}` |

## Usage

```bash
# GET example
curl -s "$AIRTABLE_API_URL/v0/meta/bases"

# POST example
curl -s -X POST "$AIRTABLE_API_URL/v0/meta/bases" -H 'Content-Type: application/json' -d '{}'
```

The audit log of every call the agent makes is available at
`$AIRTABLE_API_URL/audit/requests` (used for grading).
