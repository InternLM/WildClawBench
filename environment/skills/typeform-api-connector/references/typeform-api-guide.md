# Typeform API (Mock) Guide

Worked `curl` examples for every endpoint. **All requests target the base URL in `$TYPEFORM_API_URL`.** Auth headers are mocked (any token is accepted) and responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `TYPEFORM_API_URL` | Base URL for all requests |

## Forms

```bash
curl -s "$TYPEFORM_API_URL/forms"
curl -s -X POST "$TYPEFORM_API_URL/forms" -H 'Content-Type: application/json' -d '{}'
curl -s "$TYPEFORM_API_URL/forms/<form_id>"
curl -s -X PUT "$TYPEFORM_API_URL/forms/<form_id>" -H 'Content-Type: application/json' -d '{}'
curl -s -X DELETE "$TYPEFORM_API_URL/forms/<form_id>"
curl -s "$TYPEFORM_API_URL/forms/<form_id>/responses"
curl -s "$TYPEFORM_API_URL/forms/<form_id>/insights/summary"
```

The audit log of every call is available at `$TYPEFORM_API_URL/audit/requests` (used for grading).
