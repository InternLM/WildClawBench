# WhatsApp Cloud API Mock — Test Results

Base URL: `http://localhost:8015` (docker-compose: `http://whatsapp-api:8015`)

## Endpoints

| Method | Path                              | Status   |
|--------|-----------------------------------|----------|
| GET    | /health                           | 200      |
| GET    | /v17.0/business                   | 200      |
| GET    | /v17.0/contacts                   | 200      |
| GET    | /v17.0/contacts/{wa_id}           | 200/404  |
| GET    | /v17.0/message_templates          | 200      |
| GET    | /v17.0/message_templates/{name}   | 200/404  |
| GET    | /v17.0/conversations              | 200      |
| GET    | /v17.0/messages                   | 200      |
| POST   | /v17.0/messages                   | 200/400  |
| POST   | /v17.0/messages/status            | 200/404  |

## Seed data

- Business account: `wba-orbit-labs` (Orbit Labs Support)
- Contacts: 5 (4 opted in, 1 not opted in)
- Approved templates: 4; PENDING: 1
- Active conversations: 4; messages: 8

## Notes

- Sending a `type=text` message outside the 24-hour window or to a non-opted-in
  contact returns 400 — use a template instead.
- Sending a template with `status != APPROVED` returns 400.
- Outbound message status starts at `sent`; call `/messages/status` to mark it `read`.
