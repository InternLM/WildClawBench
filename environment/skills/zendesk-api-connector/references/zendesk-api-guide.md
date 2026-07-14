# Zendesk Support API (Mock) Guide

Worked `curl` examples for every endpoint. **All requests target the base URL in `$ZENDESK_API_URL`.** Auth headers are mocked (any token is accepted) and responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `ZENDESK_API_URL` | Base URL for all requests |

## Api

```bash
curl -s "$ZENDESK_API_URL/api/v2/tickets"
curl -s "$ZENDESK_API_URL/api/v2/tickets/<ticket_id>"
curl -s -X POST "$ZENDESK_API_URL/api/v2/tickets" -H 'Content-Type: application/json' -d '{}'
curl -s -X PUT "$ZENDESK_API_URL/api/v2/tickets/<ticket_id>" -H 'Content-Type: application/json' -d '{}'
curl -s "$ZENDESK_API_URL/api/v2/tickets/<ticket_id>/comments"
curl -s -X POST "$ZENDESK_API_URL/api/v2/tickets/<ticket_id>/comments" -H 'Content-Type: application/json' -d '{}'
curl -s "$ZENDESK_API_URL/api/v2/users"
curl -s "$ZENDESK_API_URL/api/v2/users/<user_id>"
curl -s "$ZENDESK_API_URL/api/v2/organizations"
```

The audit log of every call is available at `$ZENDESK_API_URL/audit/requests` (used for grading).
