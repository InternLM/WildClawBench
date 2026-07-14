# BambooHR API (Mock) Guide

Worked `curl` examples for every endpoint. **All requests target the base URL in `$BAMBOOHR_API_URL`.** Auth headers are mocked (any token is accepted) and responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `BAMBOOHR_API_URL` | Base URL for all requests |

## Root

```bash
curl -s "$BAMBOOHR_API_URL/"
```

The audit log of every call is available at `$BAMBOOHR_API_URL/audit/requests` (used for grading).
