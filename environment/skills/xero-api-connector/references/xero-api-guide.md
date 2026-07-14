# Xero Accounting API (Mock) Guide

Worked `curl` examples for every endpoint. **All requests target the base URL in `$XERO_API_URL`.** Auth headers are mocked (any token is accepted) and responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `XERO_API_URL` | Base URL for all requests |

## Api.Xro

```bash
curl -s "$XERO_API_URL/api.xro/2.0/Invoices"
curl -s "$XERO_API_URL/api.xro/2.0/Invoices/<invoice_id>"
curl -s -X POST "$XERO_API_URL/api.xro/2.0/Invoices" -H 'Content-Type: application/json' -d '{}'
curl -s "$XERO_API_URL/api.xro/2.0/Contacts"
curl -s "$XERO_API_URL/api.xro/2.0/Accounts"
```

The audit log of every call is available at `$XERO_API_URL/audit/requests` (used for grading).
