---
name: activecampaign-api-connector
description: >
  ActiveCampaign API (Mock) mock HTTP API. Base URL is provided via the
  `ACTIVECAMPAIGN_API_URL` environment variable. 6 endpoint(s) across GET, POST.
metadata: {"clawdbot":{"emoji":"🔌"}}
---

# ActiveCampaign API (Mock)

Mock HTTP API. **All requests go to the base URL in `$ACTIVECAMPAIGN_API_URL`.** Auth headers
are mocked (any token is accepted). Responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `ACTIVECAMPAIGN_API_URL` | Base URL for all requests (e.g. `http://activecampaign-api:8101`) |

## Endpoints

| Method | Path |
|--------|------|
| GET | `/api/3/contacts` |
| GET | `/api/3/contacts/{contact_id}` |
| POST | `/api/3/contacts` |
| GET | `/api/3/lists` |
| GET | `/api/3/campaigns` |
| GET | `/api/3/deals` |

## Usage

```bash
# GET example
curl -s "$ACTIVECAMPAIGN_API_URL/api/3/contacts"

# POST example
curl -s -X POST "$ACTIVECAMPAIGN_API_URL/api/3/contacts" -H 'Content-Type: application/json' -d '{}'
```

The audit log of every call the agent makes is available at
`$ACTIVECAMPAIGN_API_URL/audit/requests` (used for grading).
