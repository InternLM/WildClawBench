# ActiveCampaign Mock API — Test Results

Base URL: `http://localhost:8101` (in docker-compose: `http://activecampaign-api:8101`)

## Endpoints covered

| Method | Path                          | Status      |
|--------|-------------------------------|-------------|
| GET    | /health                       | 200         |
| GET    | /api/3/contacts               | 200         |
| GET    | /api/3/contacts/{id}          | 200/404     |
| POST   | /api/3/contacts               | 201/422     |
| GET    | /api/3/lists                  | 200         |
| GET    | /api/3/campaigns              | 200         |
| GET    | /api/3/deals                  | 200         |

## Seed data summary

- Contacts: 8 (email, first/last name, phone, status) created/updated in 2026-04/05.
- Lists: 5 (Newsletter Subscribers, Product Updates, Webinar Leads, Trial Users,
  Churned Customers) with subscriber counts.
- Campaigns: 6 (single + automation) with status, opens, clicks, send dates.
- Deals: 7 tied to contacts, with value, currency, stage, and owner.

## Notes

- Mirrors the ActiveCampaign API v3; all paths are under `/api/3`.
- List endpoints return a top-level plural key (`contacts`, `lists`,
  `campaigns`, `deals`) plus a `meta` block whose `total` is the unpaged count.
  They accept `limit`/`offset` query params.
- `GET /api/3/contacts` also accepts `email` and `status` filters.
- `GET /api/3/contacts/{id}` returns `{"contact": {...}}`; unknown ids 404.
- `POST /api/3/contacts` accepts `{"contact": {"email": ..., "firstName": ...}}`,
  returns 201 with the created contact, or 422 on a missing/duplicate email.
- Mutations are held in process memory and reset on container restart.
