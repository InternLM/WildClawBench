# HubSpot CRM API (Mock) Guide

Worked `curl` examples for every endpoint. **All requests target the base URL in `$HUBSPOT_API_URL`.** Auth headers are mocked (any token is accepted) and responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `HUBSPOT_API_URL` | Base URL for all requests |

## Crm

```bash
curl -s "$HUBSPOT_API_URL/crm/v3/objects/contacts"
curl -s "$HUBSPOT_API_URL/crm/v3/objects/contacts/<contact_id>"
curl -s -X POST "$HUBSPOT_API_URL/crm/v3/objects/contacts" -H 'Content-Type: application/json' -d '{}'
curl -s -X PATCH "$HUBSPOT_API_URL/crm/v3/objects/contacts/<contact_id>" -H 'Content-Type: application/json' -d '{}'
curl -s "$HUBSPOT_API_URL/crm/v3/objects/companies"
curl -s "$HUBSPOT_API_URL/crm/v3/objects/companies/<company_id>"
curl -s "$HUBSPOT_API_URL/crm/v3/objects/deals"
curl -s "$HUBSPOT_API_URL/crm/v3/objects/deals/<deal_id>"
curl -s -X POST "$HUBSPOT_API_URL/crm/v3/objects/deals" -H 'Content-Type: application/json' -d '{}'
curl -s -X PATCH "$HUBSPOT_API_URL/crm/v3/objects/deals/<deal_id>" -H 'Content-Type: application/json' -d '{}'
curl -s "$HUBSPOT_API_URL/crm/v3/pipelines/deals"
```

The audit log of every call is available at `$HUBSPOT_API_URL/audit/requests` (used for grading).
