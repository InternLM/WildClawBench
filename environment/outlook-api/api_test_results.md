# Outlook Mock API — Test Results

Base URL: `http://localhost:8087` (in docker-compose: `http://outlook-api:8087`)

## Endpoints covered

| Method | Path                            | Status      |
|--------|---------------------------------|-------------|
| GET    | /health                         | 200         |
| GET    | /v1.0/me/messages               | 200         |
| GET    | /v1.0/me/messages/{id}          | 200/404     |
| POST   | /v1.0/me/sendMail               | 202/400     |
| GET    | /v1.0/me/events                 | 200         |
| GET    | /v1.0/me/contacts               | 200         |

## Seed data summary

- Messages: 8 mailbox messages with from/to recipients, read flag, importance, and 2026-05 received dates.
- Events: 6 calendar events (meetings, an all-day holiday, online demos) with organizer and attendees.
- Contacts: 7 contacts with name, email, job title, company, and phone.

## Seed data summary notes

- Collection responses are wrapped in `{"value": [...]}` to match Microsoft Graph.

## Notes

- `/v1.0/me/messages` supports the `isRead` filter (e.g. `?isRead=false`).
- `POST /v1.0/me/sendMail` accepts a Graph message envelope (`{"message": {"subject","body","toRecipients"}}`) and returns 202 Accepted; an empty `toRecipients` returns 400. The sent message is appended to the in-memory store.
- Mutations are held in process memory and reset on container restart.
