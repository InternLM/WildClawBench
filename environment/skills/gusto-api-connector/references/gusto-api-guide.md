# Gusto Payroll API (Mock) Guide

Worked `curl` examples for every endpoint. **All requests target the base URL in `$GUSTO_API_URL`.** Auth headers are mocked (any token is accepted) and responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `GUSTO_API_URL` | Base URL for all requests |

## Companies

```bash
curl -s "$GUSTO_API_URL/v1/companies/<company_id>"
curl -s "$GUSTO_API_URL/v1/companies/<company_id>/employees"
curl -s "$GUSTO_API_URL/v1/companies/<company_id>/payrolls"
curl -s -X POST "$GUSTO_API_URL/v1/companies/<company_id>/payrolls" -H 'Content-Type: application/json' -d '{}'
curl -s "$GUSTO_API_URL/v1/companies/<company_id>/contractors"
```

## Employees

```bash
curl -s "$GUSTO_API_URL/v1/employees/<employee_id>"
```

## Payrolls

```bash
curl -s "$GUSTO_API_URL/v1/payrolls/<payroll_id>"
curl -s -X PUT "$GUSTO_API_URL/v1/payrolls/<payroll_id>/submit" -H 'Content-Type: application/json' -d '{}'
```

The audit log of every call is available at `$GUSTO_API_URL/audit/requests` (used for grading).
