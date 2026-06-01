---
name: shippo-api-connector
description: >
  Shippo API (Mock) mock HTTP API. Base URL is provided via the
  `SHIPPO_API_URL` environment variable. 8 endpoint(s) across GET, POST.
metadata: {"clawdbot":{"emoji":"🔌"}}
---

# Shippo API (Mock)

Mock HTTP API. **All requests go to the base URL in `$SHIPPO_API_URL`.** Auth headers
are mocked (any token is accepted). Responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `SHIPPO_API_URL` | Base URL for all requests (e.g. `http://shippo-api:8052`) |

## Endpoints

| Method | Path |
|--------|------|
| POST | `/addresses` |
| GET | `/addresses/{object_id}` |
| POST | `/shipments` |
| GET | `/shipments/{object_id}` |
| GET | `/shipments/{object_id}/rates` |
| POST | `/transactions` |
| GET | `/transactions/{object_id}` |
| GET | `/tracks/{carrier}/{tracking_number}` |

## Usage

```bash
# GET example
curl -s "$SHIPPO_API_URL/addresses"

# POST example
curl -s -X POST "$SHIPPO_API_URL/addresses" -H 'Content-Type: application/json' -d '{}'
```

The audit log of every call the agent makes is available at
`$SHIPPO_API_URL/audit/requests` (used for grading).
