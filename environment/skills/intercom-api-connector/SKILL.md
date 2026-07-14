---
name: intercom-api-connector
description: >
  Intercom API (Mock) mock HTTP API. Base URL is provided via the
  `INTERCOM_API_URL` environment variable. 10 endpoint(s) across GET, POST.
metadata: {"clawdbot":{"emoji":"🔌"}}
---

# Intercom API (Mock)

Mock HTTP API. **All requests go to the base URL in `$INTERCOM_API_URL`.** Auth headers
are mocked (any token is accepted). Responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `INTERCOM_API_URL` | Base URL for all requests (e.g. `http://intercom-api:8070`) |

## Endpoints

| Method | Path |
|--------|------|
| GET | `/contacts` |
| POST | `/contacts` |
| GET | `/contacts/{contact_id}` |
| GET | `/conversations` |
| POST | `/conversations` |
| GET | `/conversations/{conversation_id}` |
| POST | `/conversations/{conversation_id}/reply` |
| POST | `/conversations/{conversation_id}/parts` |
| GET | `/companies` |
| GET | `/companies/{company_id}` |

## Usage

```bash
# GET example
curl -s "$INTERCOM_API_URL/contacts"

# POST example
curl -s -X POST "$INTERCOM_API_URL/contacts" -H 'Content-Type: application/json' -d '{}'
```

The audit log of every call the agent makes is available at
`$INTERCOM_API_URL/audit/requests` (used for grading).
