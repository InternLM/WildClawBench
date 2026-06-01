# SendGrid Mock API — Test Results

Base URL: `http://localhost:8027` (in docker-compose: `http://sendgrid-api:8027`)

## Endpoints covered

| Method | Path                          | Status  |
|--------|-------------------------------|---------|
| GET    | /health                       | 200     |
| POST   | /v3/mail/send                 | 202/400 |
| GET    | /v3/templates                 | 200     |
| POST   | /v3/templates                 | 201     |
| GET    | /v3/templates/{id}            | 200/404 |
| GET    | /v3/marketing/contacts        | 200     |
| POST   | /v3/marketing/contacts        | 202     |
| GET    | /v3/marketing/lists           | 200     |
| GET    | /v3/stats?start_date=         | 200     |

## Seed data summary

- Templates: 5 dynamic (welcome, password reset, newsletter, invoice, trial-ending)
- Lists: 4 (newsletter subscribers, active customers, trial users, beta testers)
- Contacts: 6 (mapped onto lists via `list_ids`)
- Sent log: 6 messages (delivered/bounced/opened, with open/click counts)
- Daily stats: 7 rows (2026-05-20 .. 2026-05-26)

## Notes

- Mutations are held in process memory and reset on container restart.
- `POST /v3/mail/send` returns 202 with generated `message_id`s; the from address is
  supplied as `from.email` (JSON key `from`). Invalid template ids return 400.
- `POST /v3/marketing/contacts` upserts by email and merges supplied `list_ids`.
- `GET /v3/stats` requires `start_date`; `end_date` is optional. Metrics are nested under
  `stats[0].metrics` to mirror the real SendGrid shape.
- Template ids follow SendGrid's dynamic-template form `d-<hex>`.
