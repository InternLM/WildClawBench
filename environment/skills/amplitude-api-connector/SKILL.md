---
name: amplitude-api-connector
description: >
  Amplitude API (Mock) mock HTTP API. Base URL is provided via the
  `AMPLITUDE_API_URL` environment variable. 3 endpoint(s) across GET, POST.
metadata: {"clawdbot":{"emoji":"🔌"}}
---

# Amplitude API (Mock)

Mock HTTP API. **All requests go to the base URL in `$AMPLITUDE_API_URL`.** Auth headers
are mocked (any token is accepted). Responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `AMPLITUDE_API_URL` | Base URL for all requests (e.g. `http://amplitude-api:8091`) |

## Endpoints

| Method | Path |
|--------|------|
| POST | `/2/httpapi` |
| GET | `/api/2/events/segmentation` |
| GET | `/api/2/useractivity` |

## Usage

```bash
# GET example
curl -s "$AMPLITUDE_API_URL/2/httpapi"

# POST example
curl -s -X POST "$AMPLITUDE_API_URL/2/httpapi" -H 'Content-Type: application/json' -d '{}'
```

The audit log of every call the agent makes is available at
`$AMPLITUDE_API_URL/audit/requests` (used for grading).
