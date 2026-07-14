# Intercom API (Mock) Guide

Worked `curl` examples for every endpoint. **All requests target the base URL in `$INTERCOM_API_URL`.** Auth headers are mocked (any token is accepted) and responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `INTERCOM_API_URL` | Base URL for all requests |

## Companies

```bash
curl -s "$INTERCOM_API_URL/companies"
curl -s "$INTERCOM_API_URL/companies/<company_id>"
```

## Contacts

```bash
curl -s "$INTERCOM_API_URL/contacts"
curl -s -X POST "$INTERCOM_API_URL/contacts" -H 'Content-Type: application/json' -d '{}'
curl -s "$INTERCOM_API_URL/contacts/<contact_id>"
```

## Conversations

```bash
curl -s "$INTERCOM_API_URL/conversations"
curl -s -X POST "$INTERCOM_API_URL/conversations" -H 'Content-Type: application/json' -d '{}'
curl -s "$INTERCOM_API_URL/conversations/<conversation_id>"
curl -s -X POST "$INTERCOM_API_URL/conversations/<conversation_id>/reply" -H 'Content-Type: application/json' -d '{}'
curl -s -X POST "$INTERCOM_API_URL/conversations/<conversation_id>/parts" -H 'Content-Type: application/json' -d '{}'
```

The audit log of every call is available at `$INTERCOM_API_URL/audit/requests` (used for grading).
