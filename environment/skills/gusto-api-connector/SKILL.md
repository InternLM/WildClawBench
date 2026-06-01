---
name: gusto-api-connector
description: >
  Gusto Payroll API (Mock) mock HTTP API. Base URL is provided via the
  `GUSTO_API_URL` environment variable. 8 endpoint(s) across GET, POST, PUT.
metadata: {"clawdbot":{"emoji":"🔌"}}
---

# Gusto Payroll API (Mock)

Mock HTTP API. **All requests go to the base URL in `$GUSTO_API_URL`.** Auth headers
are mocked (any token is accepted). Responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `GUSTO_API_URL` | Base URL for all requests (e.g. `http://gusto-api:8074`) |

## Endpoints

| Method | Path |
|--------|------|
| GET | `/v1/companies/{company_id}` |
| GET | `/v1/companies/{company_id}/employees` |
| GET | `/v1/employees/{employee_id}` |
| GET | `/v1/companies/{company_id}/payrolls` |
| GET | `/v1/payrolls/{payroll_id}` |
| POST | `/v1/companies/{company_id}/payrolls` |
| PUT | `/v1/payrolls/{payroll_id}/submit` |
| GET | `/v1/companies/{company_id}/contractors` |

## Usage

```bash
# GET example
curl -s "$GUSTO_API_URL/v1/companies/{company_id}"

# POST example
curl -s -X POST "$GUSTO_API_URL/v1/companies/{company_id}" -H 'Content-Type: application/json' -d '{}'
```

The audit log of every call the agent makes is available at
`$GUSTO_API_URL/audit/requests` (used for grading).
