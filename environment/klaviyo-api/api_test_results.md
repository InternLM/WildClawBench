# Klaviyo Mock API — Test Results

Base URL: `http://localhost:8089` (in docker-compose: `http://klaviyo-api:8089`)

## Endpoints covered

| Method | Path                    | Status      |
|--------|-------------------------|-------------|
| GET    | /health                 | 200         |
| GET    | /api/profiles           | 200         |
| GET    | /api/profiles/{id}      | 200/404     |
| POST   | /api/profiles           | 201/400/409 |
| GET    | /api/lists              | 200         |
| GET    | /api/campaigns          | 200         |

## Seed data summary

- Profiles: 10 with email, phone, name, organization, title, and location (city/region/country), created/updated in 2026.
- Lists: 6 audiences (Newsletter, VIP, Abandoned Cart, etc.) with profile counts.
- Campaigns: 6 email/SMS campaigns across Sent/Scheduled/Draft, each linked to a list.

## Notes

- Responses use the JSON:API envelope: collections as `{"data": [{type, id, attributes}]}` and a single resource as `{"data": {...}}`.
- `/api/profiles` supports an `email` filter; `/api/campaigns` supports `status` and `channel` filters.
- `POST /api/profiles` accepts a JSON:API body (`{"data": {"type": "profile", "attributes": {"email", ...}}}`); a missing email returns 400 and a duplicate email returns 409.
- Mutations are held in process memory and reset on container restart.
