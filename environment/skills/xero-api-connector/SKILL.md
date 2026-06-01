---
name: xero-api-connector
description: >
  Xero Accounting API (Mock) mock HTTP API. Base URL is provided via the
  `XERO_API_URL` environment variable. 5 endpoint(s) across GET, POST.
metadata: {"clawdbot":{"emoji":"🔌"}}
---

# Xero Accounting API (Mock)

Mock HTTP API. **All requests go to the base URL in `$XERO_API_URL`.** Auth headers
are mocked (any token is accepted). Responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `XERO_API_URL` | Base URL for all requests (e.g. `http://xero-api:8088`) |

## Endpoints

| Method | Path |
|--------|------|
| GET | `/api.xro/2.0/Invoices` |
| GET | `/api.xro/2.0/Invoices/{invoice_id}` |
| POST | `/api.xro/2.0/Invoices` |
| GET | `/api.xro/2.0/Contacts` |
| GET | `/api.xro/2.0/Accounts` |

## Usage

```bash
# GET example
curl -s "$XERO_API_URL/api.xro/2.0/Invoices"

# POST example
curl -s -X POST "$XERO_API_URL/api.xro/2.0/Invoices" -H 'Content-Type: application/json' -d '{}'
```

The audit log of every call the agent makes is available at
`$XERO_API_URL/audit/requests` (used for grading).
