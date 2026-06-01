# Freshdesk Mock API — Test Results

Base URL: `http://localhost:8093` (in docker-compose: `http://freshdesk-api:8093`)

## Endpoints covered

| Method | Path                       | Status  |
|--------|----------------------------|---------|
| GET    | /health                    | 200     |
| GET    | /api/v2/tickets            | 200     |
| GET    | /api/v2/tickets/{id}       | 200/404 |
| POST   | /api/v2/tickets            | 201     |
| PUT    | /api/v2/tickets/{id}       | 200/404 |
| GET    | /api/v2/contacts           | 200     |
| GET    | /api/v2/agents             | 200     |

## Seed data summary

- Tickets: 8 tickets with int status (2=open, 3=pending, 4=resolved, 5=closed) and int priority (1..4), dated 2026-05.
- Contacts: 6 contacts (name, email, phone, company_id, active).
- Agents: 5 agents with availability, ticket_scope, and nested contact info.

## Notes

- `/api/v2/tickets` is filterable by `status`, `priority`, and `requester_id`.
- `POST /api/v2/tickets` creates a ticket (defaults: status=2, priority=1) and returns 201.
- `PUT /api/v2/tickets/{id}` updates provided fields and refreshes `updated_at`.
- Status/priority follow Freshdesk conventions (int values).
- Mutations are held in process memory and reset on container restart.
