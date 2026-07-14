# Intercom Mock API — Test Results

Base URL: `http://localhost:8070` (in docker-compose: `http://intercom-api:8070`)

## Endpoints covered

| Method | Path                                          | Status  |
|--------|-----------------------------------------------|---------|
| GET    | /health                                       | 200     |
| GET    | /contacts                                     | 200     |
| POST   | /contacts                                     | 201     |
| GET    | /contacts/{id}                                | 200/404 |
| GET    | /conversations                                | 200     |
| POST   | /conversations                                | 201/404 |
| GET    | /conversations/{id}                           | 200/404 |
| POST   | /conversations/{id}/reply                     | 200/404 |
| POST   | /conversations/{id}/parts                     | 200/404 |
| GET    | /companies                                     | 200     |
| GET    | /companies/{id}                               | 200/404 |

## Seed data summary

- Contacts: 7 (roles user / lead) each linked to a company
- Companies: 4 (Brightpath, Nimbus Co, Helio Labs, Vela Tech)
- Conversations: 4 (2 open, 2 closed) with titles and assignees
- Conversation parts: 9 (user comments, admin replies, and close actions)

## Notes

- `GET /contacts` supports a `role` filter; `GET /conversations` supports a
  `state` filter (open/closed).
- `GET /conversations/{id}` embeds the ordered `conversation_parts`.
- `POST /conversations` creates an open conversation seeded with the user's
  first comment part.
- `POST /conversations/{id}/reply` appends a comment part and bumps
  `updated_at`.
- `POST /conversations/{id}/parts` takes a `message_type`: `close` /`open`
  toggle the state, `assignment` sets `assignee_id`, others append a part.
- `GET /companies/{id}` resolves by internal id or external `company_id`.
- Mutations are held in process memory and reset on container restart.
