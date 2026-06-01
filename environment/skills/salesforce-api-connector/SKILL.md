---
name: salesforce-api-connector
description: >
  Salesforce REST API (Mock) mock HTTP API. Base URL is provided via the
  `SALESFORCE_API_URL` environment variable. 0 endpoint(s) across GET.
metadata: {"clawdbot":{"emoji":"🔌"}}
---

# Salesforce REST API (Mock)

Mock HTTP API. **All requests go to the base URL in `$SALESFORCE_API_URL`.** Auth headers
are mocked (any token is accepted). Responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `SALESFORCE_API_URL` | Base URL for all requests (e.g. `http://salesforce-api:8044`) |

## Endpoints

| Method | Path |
|--------|------|
| GET | `/` |

## Usage

```bash
# GET example
curl -s "$SALESFORCE_API_URL/"

# POST example
curl -s -X POST "$SALESFORCE_API_URL/" -H 'Content-Type: application/json' -d '{}'
```

The audit log of every call the agent makes is available at
`$SALESFORCE_API_URL/audit/requests` (used for grading).
