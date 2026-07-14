# WhatsApp Cloud API (Mock) Guide

Worked `curl` examples for every endpoint. **All requests target the base URL in `$WHATSAPP_API_URL`.** Auth headers are mocked (any token is accepted) and responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `WHATSAPP_API_URL` | Base URL for all requests |

## V17.0

```bash
curl -s "$WHATSAPP_API_URL/v17.0/business"
curl -s "$WHATSAPP_API_URL/v17.0/contacts"
curl -s "$WHATSAPP_API_URL/v17.0/contacts/<wa_id>"
curl -s "$WHATSAPP_API_URL/v17.0/message_templates"
curl -s "$WHATSAPP_API_URL/v17.0/message_templates/<name>"
curl -s "$WHATSAPP_API_URL/v17.0/conversations"
curl -s "$WHATSAPP_API_URL/v17.0/messages"
curl -s -X POST "$WHATSAPP_API_URL/v17.0/messages" -H 'Content-Type: application/json' -d '{}'
curl -s -X POST "$WHATSAPP_API_URL/v17.0/messages/status" -H 'Content-Type: application/json' -d '{}'
```

The audit log of every call is available at `$WHATSAPP_API_URL/audit/requests` (used for grading).
