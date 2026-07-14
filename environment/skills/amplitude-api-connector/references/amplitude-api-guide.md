# Amplitude API (Mock) Guide

Worked `curl` examples for every endpoint. **All requests target the base URL in `$AMPLITUDE_API_URL`.** Auth headers are mocked (any token is accepted) and responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `AMPLITUDE_API_URL` | Base URL for all requests |

## 2

```bash
curl -s -X POST "$AMPLITUDE_API_URL/2/httpapi" -H 'Content-Type: application/json' -d '{}'
```

## Api

```bash
curl -s "$AMPLITUDE_API_URL/api/2/events/segmentation"
curl -s "$AMPLITUDE_API_URL/api/2/useractivity"
```

The audit log of every call is available at `$AMPLITUDE_API_URL/audit/requests` (used for grading).
