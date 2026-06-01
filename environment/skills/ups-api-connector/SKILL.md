---
name: ups-api-connector
description: >
  UPS API (Mock) mock HTTP API. Base URL is provided via the
  `UPS_API_URL` environment variable. 3 endpoint(s) across GET, POST.
metadata: {"clawdbot":{"emoji":"🔌"}}
---

# UPS API (Mock)

Mock HTTP API. **All requests go to the base URL in `$UPS_API_URL`.** Auth headers
are mocked (any token is accepted). Responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `UPS_API_URL` | Base URL for all requests (e.g. `http://ups-api:8096`) |

## Endpoints

| Method | Path |
|--------|------|
| POST | `/api/rating/v1/Rate` |
| POST | `/api/shipments/v1/ship` |
| GET | `/api/track/v1/details/{tracking_number}` |

## Usage

```bash
# GET example
curl -s "$UPS_API_URL/api/rating/v1/Rate"

# POST example
curl -s -X POST "$UPS_API_URL/api/rating/v1/Rate" -H 'Content-Type: application/json' -d '{}'
```

The audit log of every call the agent makes is available at
`$UPS_API_URL/audit/requests` (used for grading).
