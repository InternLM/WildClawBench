# Freshdesk API (Mock) Guide

Worked `curl` examples for every endpoint. **All requests target the base URL in `$FRESHDESK_API_URL`.** Auth headers are mocked (any token is accepted) and responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `FRESHDESK_API_URL` | Base URL for all requests |

## Api

```bash
curl -s "$FRESHDESK_API_URL/api/v2/tickets"
curl -s "$FRESHDESK_API_URL/api/v2/tickets/<ticket_id>"
curl -s -X POST "$FRESHDESK_API_URL/api/v2/tickets" -H 'Content-Type: application/json' -d '{}'
curl -s -X PUT "$FRESHDESK_API_URL/api/v2/tickets/<ticket_id>" -H 'Content-Type: application/json' -d '{}'
curl -s "$FRESHDESK_API_URL/api/v2/contacts"
curl -s "$FRESHDESK_API_URL/api/v2/agents"
```

The audit log of every call is available at `$FRESHDESK_API_URL/audit/requests` (used for grading).
