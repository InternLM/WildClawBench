# Google Contacts API (Mock) Guide

Worked `curl` examples for every endpoint. **All requests target the base URL in `$GOOGLE_CONTACTS_API_URL`.** Auth headers are mocked (any token is accepted) and responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `GOOGLE_CONTACTS_API_URL` | Base URL for all requests |

## Contact_Groups

```bash
curl -s "$GOOGLE_CONTACTS_API_URL/contact_groups"
```

## Contacts

```bash
curl -s "$GOOGLE_CONTACTS_API_URL/contacts"
curl -s "$GOOGLE_CONTACTS_API_URL/contacts/<item_id>"
curl -s -X POST "$GOOGLE_CONTACTS_API_URL/contacts" -H 'Content-Type: application/json' -d '{}'
```

The audit log of every call is available at `$GOOGLE_CONTACTS_API_URL/audit/requests` (used for grading).
