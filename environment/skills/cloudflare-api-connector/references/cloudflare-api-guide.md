# Cloudflare API (Mock) Guide

Worked `curl` examples for every endpoint. **All requests target the base URL in `$CLOUDFLARE_API_URL`.** Auth headers are mocked (any token is accepted) and responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `CLOUDFLARE_API_URL` | Base URL for all requests |

## Client

```bash
curl -s "$CLOUDFLARE_API_URL/client/v4/zones"
curl -s "$CLOUDFLARE_API_URL/client/v4/zones/<zone_id>"
curl -s "$CLOUDFLARE_API_URL/client/v4/zones/<zone_id>/dns_records"
curl -s "$CLOUDFLARE_API_URL/client/v4/zones/<zone_id>/dns_records/<record_id>"
curl -s -X POST "$CLOUDFLARE_API_URL/client/v4/zones/<zone_id>/dns_records" -H 'Content-Type: application/json' -d '{}'
curl -s -X PUT "$CLOUDFLARE_API_URL/client/v4/zones/<zone_id>/dns_records/<record_id>" -H 'Content-Type: application/json' -d '{}'
curl -s -X DELETE "$CLOUDFLARE_API_URL/client/v4/zones/<zone_id>/dns_records/<record_id>"
curl -s "$CLOUDFLARE_API_URL/client/v4/zones/<zone_id>/firewall/rules"
```

The audit log of every call is available at `$CLOUDFLARE_API_URL/audit/requests` (used for grading).
