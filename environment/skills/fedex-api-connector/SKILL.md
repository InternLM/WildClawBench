---
name: fedex-api-connector
description: >
  FedEx API (Mock) mock HTTP API. Base URL is provided via the
  `FEDEX_API_URL` environment variable. 3 endpoint(s) across POST.
metadata: {"clawdbot":{"emoji":"🔌"}}
---

# FedEx API (Mock)

Mock HTTP API. **All requests go to the base URL in `$FEDEX_API_URL`.** Auth headers
are mocked (any token is accepted). Responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `FEDEX_API_URL` | Base URL for all requests (e.g. `http://fedex-api:8095`) |

## Endpoints

| Method | Path |
|--------|------|
| POST | `/rate/v1/rates/quotes` |
| POST | `/ship/v1/shipments` |
| POST | `/track/v1/trackingnumbers` |

## Usage

```bash
# GET example
curl -s "$FEDEX_API_URL/rate/v1/rates/quotes"

# POST example
curl -s -X POST "$FEDEX_API_URL/rate/v1/rates/quotes" -H 'Content-Type: application/json' -d '{}'
```

The audit log of every call the agent makes is available at
`$FEDEX_API_URL/audit/requests` (used for grading).
