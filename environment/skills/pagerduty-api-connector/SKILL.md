---
name: pagerduty-api-connector
description: >
  PagerDuty API (Mock) mock HTTP API. Base URL is provided via the
  `PAGERDUTY_API_URL` environment variable. 12 endpoint(s) across GET, POST, PUT.
metadata: {"clawdbot":{"emoji":"🔌"}}
---

# PagerDuty API (Mock)

Mock HTTP API. **All requests go to the base URL in `$PAGERDUTY_API_URL`.** Auth headers
are mocked (any token is accepted). Responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `PAGERDUTY_API_URL` | Base URL for all requests (e.g. `http://pagerduty-api:8040`) |

## Endpoints

| Method | Path |
|--------|------|
| GET | `/services` |
| GET | `/services/{service_id}` |
| GET | `/incidents` |
| GET | `/incidents/{incident_id}` |
| POST | `/incidents` |
| PUT | `/incidents/{incident_id}` |
| GET | `/incidents/{incident_id}/notes` |
| POST | `/incidents/{incident_id}/notes` |
| GET | `/oncalls` |
| GET | `/schedules` |
| GET | `/escalation_policies` |
| GET | `/users` |

## Usage

```bash
# GET example
curl -s "$PAGERDUTY_API_URL/services"

# POST example
curl -s -X POST "$PAGERDUTY_API_URL/services" -H 'Content-Type: application/json' -d '{}'
```

The audit log of every call the agent makes is available at
`$PAGERDUTY_API_URL/audit/requests` (used for grading).
