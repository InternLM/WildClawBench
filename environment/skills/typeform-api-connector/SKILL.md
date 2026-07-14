---
name: typeform-api-connector
description: >
  Typeform API (Mock) mock HTTP API. Base URL is provided via the
  `TYPEFORM_API_URL` environment variable. 7 endpoint(s) across DELETE, GET, POST, PUT.
metadata: {"clawdbot":{"emoji":"🔌"}}
---

# Typeform API (Mock)

Mock HTTP API. **All requests go to the base URL in `$TYPEFORM_API_URL`.** Auth headers
are mocked (any token is accepted). Responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `TYPEFORM_API_URL` | Base URL for all requests (e.g. `http://typeform-api:8055`) |

## Endpoints

| Method | Path |
|--------|------|
| GET | `/forms` |
| POST | `/forms` |
| GET | `/forms/{form_id}` |
| PUT | `/forms/{form_id}` |
| DELETE | `/forms/{form_id}` |
| GET | `/forms/{form_id}/responses` |
| GET | `/forms/{form_id}/insights/summary` |

## Usage

```bash
# GET example
curl -s "$TYPEFORM_API_URL/forms"

# POST example
curl -s -X POST "$TYPEFORM_API_URL/forms" -H 'Content-Type: application/json' -d '{}'
```

The audit log of every call the agent makes is available at
`$TYPEFORM_API_URL/audit/requests` (used for grading).
