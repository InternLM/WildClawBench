# Salesforce REST API (Mock) Guide

Worked `curl` examples for every endpoint. **All requests target the base URL in `$SALESFORCE_API_URL`.** Auth headers are mocked (any token is accepted) and responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `SALESFORCE_API_URL` | Base URL for all requests |

## Root

```bash
curl -s "$SALESFORCE_API_URL/"
```

The audit log of every call is available at `$SALESFORCE_API_URL/audit/requests` (used for grading).
