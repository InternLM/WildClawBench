# SendGrid API (Mock) Guide

Worked `curl` examples for every endpoint. **All requests target the base URL in `$SENDGRID_API_URL`.** Auth headers are mocked (any token is accepted) and responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `SENDGRID_API_URL` | Base URL for all requests |

## Mail

```bash
curl -s -X POST "$SENDGRID_API_URL/v3/mail/send" -H 'Content-Type: application/json' -d '{}'
```

## Marketing

```bash
curl -s "$SENDGRID_API_URL/v3/marketing/contacts"
curl -s -X POST "$SENDGRID_API_URL/v3/marketing/contacts" -H 'Content-Type: application/json' -d '{}'
curl -s "$SENDGRID_API_URL/v3/marketing/lists"
```

## Stats

```bash
curl -s "$SENDGRID_API_URL/v3/stats"
```

## Templates

```bash
curl -s "$SENDGRID_API_URL/v3/templates"
curl -s "$SENDGRID_API_URL/v3/templates/<template_id>"
curl -s -X POST "$SENDGRID_API_URL/v3/templates" -H 'Content-Type: application/json' -d '{}'
```

The audit log of every call is available at `$SENDGRID_API_URL/audit/requests` (used for grading).
