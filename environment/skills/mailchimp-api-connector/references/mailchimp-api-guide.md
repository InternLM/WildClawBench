# Mailchimp Marketing API (Mock) Guide

Worked `curl` examples for every endpoint. **All requests target the base URL in `$MAILCHIMP_API_URL`.** Auth headers are mocked (any token is accepted) and responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `MAILCHIMP_API_URL` | Base URL for all requests |

## 3.0

```bash
curl -s "$MAILCHIMP_API_URL/3.0/lists"
curl -s "$MAILCHIMP_API_URL/3.0/lists/<list_id>"
curl -s "$MAILCHIMP_API_URL/3.0/lists/<list_id>/members"
curl -s -X POST "$MAILCHIMP_API_URL/3.0/lists/<list_id>/members" -H 'Content-Type: application/json' -d '{}'
curl -s "$MAILCHIMP_API_URL/3.0/lists/<list_id>/members/<subscriber_hash>"
curl -s -X PATCH "$MAILCHIMP_API_URL/3.0/lists/<list_id>/members/<subscriber_hash>" -H 'Content-Type: application/json' -d '{}'
curl -s "$MAILCHIMP_API_URL/3.0/campaigns"
curl -s -X POST "$MAILCHIMP_API_URL/3.0/campaigns" -H 'Content-Type: application/json' -d '{}'
curl -s "$MAILCHIMP_API_URL/3.0/campaigns/<campaign_id>"
curl -s -X POST "$MAILCHIMP_API_URL/3.0/campaigns/<campaign_id>/actions/send" -H 'Content-Type: application/json' -d '{}'
curl -s "$MAILCHIMP_API_URL/3.0/reports/<campaign_id>"
```

The audit log of every call is available at `$MAILCHIMP_API_URL/audit/requests` (used for grading).
