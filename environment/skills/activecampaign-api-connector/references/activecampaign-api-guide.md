# ActiveCampaign API (Mock) Guide

Worked `curl` examples for every endpoint. **All requests target the base URL in `$ACTIVECAMPAIGN_API_URL`.** Auth headers are mocked (any token is accepted) and responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `ACTIVECAMPAIGN_API_URL` | Base URL for all requests |

## Api

```bash
curl -s "$ACTIVECAMPAIGN_API_URL/api/3/contacts"
curl -s "$ACTIVECAMPAIGN_API_URL/api/3/contacts/<contact_id>"
curl -s -X POST "$ACTIVECAMPAIGN_API_URL/api/3/contacts" -H 'Content-Type: application/json' -d '{}'
curl -s "$ACTIVECAMPAIGN_API_URL/api/3/lists"
curl -s "$ACTIVECAMPAIGN_API_URL/api/3/campaigns"
curl -s "$ACTIVECAMPAIGN_API_URL/api/3/deals"
```

The audit log of every call is available at `$ACTIVECAMPAIGN_API_URL/audit/requests` (used for grading).
