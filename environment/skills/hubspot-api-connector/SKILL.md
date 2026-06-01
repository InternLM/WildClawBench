---
name: hubspot-api-connector
description: >
  HubSpot CRM API (Mock) mock HTTP API. Base URL is provided via the
  `HUBSPOT_API_URL` environment variable. 11 endpoint(s) across GET, PATCH, POST.
metadata: {"clawdbot":{"emoji":"🔌"}}
---

# HubSpot CRM API (Mock)

Mock HTTP API. **All requests go to the base URL in `$HUBSPOT_API_URL`.** Auth headers
are mocked (any token is accepted). Responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `HUBSPOT_API_URL` | Base URL for all requests (e.g. `http://hubspot-api:8024`) |

## Endpoints

| Method | Path |
|--------|------|
| GET | `/crm/v3/objects/contacts` |
| GET | `/crm/v3/objects/contacts/{contact_id}` |
| POST | `/crm/v3/objects/contacts` |
| PATCH | `/crm/v3/objects/contacts/{contact_id}` |
| GET | `/crm/v3/objects/companies` |
| GET | `/crm/v3/objects/companies/{company_id}` |
| GET | `/crm/v3/objects/deals` |
| GET | `/crm/v3/objects/deals/{deal_id}` |
| POST | `/crm/v3/objects/deals` |
| PATCH | `/crm/v3/objects/deals/{deal_id}` |
| GET | `/crm/v3/pipelines/deals` |

## Usage

```bash
# GET example
curl -s "$HUBSPOT_API_URL/crm/v3/objects/contacts"

# POST example
curl -s -X POST "$HUBSPOT_API_URL/crm/v3/objects/contacts" -H 'Content-Type: application/json' -d '{}'
```

The audit log of every call the agent makes is available at
`$HUBSPOT_API_URL/audit/requests` (used for grading).
