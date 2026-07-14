# Cloudflare Mock API — Test Results

Base URL: `http://localhost:8050` (docker-compose: `http://cloudflare-api:8050`)

## Endpoints

| Method | Path                                                  | Status   |
|--------|-------------------------------------------------------|----------|
| GET    | /health                                               | 200      |
| GET    | /client/v4/zones                                      | 200      |
| GET    | /client/v4/zones/{zone_id}                            | 200/404  |
| GET    | /client/v4/zones/{zone_id}/dns_records                | 200/404  |
| POST   | /client/v4/zones/{zone_id}/dns_records                | 200/404  |
| GET    | /client/v4/zones/{zone_id}/dns_records/{id}           | 200/404  |
| PUT    | /client/v4/zones/{zone_id}/dns_records/{id}           | 200/404  |
| DELETE | /client/v4/zones/{zone_id}/dns_records/{id}           | 200/404  |
| GET    | /client/v4/zones/{zone_id}/firewall/rules             | 200/404  |

## Seed data

- 2 zones (orbit-labs.com on Pro, orbit-cdn.net on Business)
- 9 DNS records across the zones (A, AAAA, CNAME, MX, TXT)
- 4 firewall rules (block / challenge / allow / js_challenge)
- 3 page rules (seeded for completeness)

## Notes

- Mutations are held in process memory and reset on container restart.
- All responses use the Cloudflare envelope `{"success", "errors", "messages", "result"}`.
- Errors return `success: false` with a populated `errors` array and the matching HTTP status (404 for unknown zone or record).
- DNS list supports `type` and `name` query params; firewall rules are returned sorted by priority.
