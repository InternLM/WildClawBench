---
name: cloudflare-api-connector
description: >
  Cloudflare API (Mock) mock HTTP API. Base URL is provided via the
  `CLOUDFLARE_API_URL` environment variable. 8 endpoint(s) across DELETE, GET, POST, PUT.
metadata: {"clawdbot":{"emoji":"🔌"}}
---

# Cloudflare API (Mock)

Mock HTTP API. **All requests go to the base URL in `$CLOUDFLARE_API_URL`.** Auth headers
are mocked (any token is accepted). Responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `CLOUDFLARE_API_URL` | Base URL for all requests (e.g. `http://cloudflare-api:8050`) |

## Endpoints

| Method | Path |
|--------|------|
| GET | `/client/v4/zones` |
| GET | `/client/v4/zones/{zone_id}` |
| GET | `/client/v4/zones/{zone_id}/dns_records` |
| GET | `/client/v4/zones/{zone_id}/dns_records/{record_id}` |
| POST | `/client/v4/zones/{zone_id}/dns_records` |
| PUT | `/client/v4/zones/{zone_id}/dns_records/{record_id}` |
| DELETE | `/client/v4/zones/{zone_id}/dns_records/{record_id}` |
| GET | `/client/v4/zones/{zone_id}/firewall/rules` |

## Usage

```bash
# GET example
curl -s "$CLOUDFLARE_API_URL/client/v4/zones"

# POST example
curl -s -X POST "$CLOUDFLARE_API_URL/client/v4/zones" -H 'Content-Type: application/json' -d '{}'
```

The audit log of every call the agent makes is available at
`$CLOUDFLARE_API_URL/audit/requests` (used for grading).
