# Confluence Cloud API (Mock) Guide

Worked `curl` examples for every endpoint. **All requests target the base URL in `$CONFLUENCE_API_URL`.** Auth headers are mocked (any token is accepted) and responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `CONFLUENCE_API_URL` | Base URL for all requests |

## Root

```bash
curl -s "$CONFLUENCE_API_URL/"
```

The audit log of every call is available at `$CONFLUENCE_API_URL/audit/requests` (used for grading).
