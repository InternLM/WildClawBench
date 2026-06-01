# Zendesk Mock Support API — Test Results

Base URL: `http://localhost:8025` (in docker-compose: `http://zendesk-api:8025`)

## Endpoints covered

| Method | Path                                  | Status   |
|--------|---------------------------------------|----------|
| GET    | /health                               | 200      |
| GET    | /api/v2/tickets                       | 200      |
| GET    | /api/v2/tickets/{id}                  | 200/404  |
| POST   | /api/v2/tickets                       | 201/400  |
| PUT    | /api/v2/tickets/{id}                  | 200/400/404 |
| GET    | /api/v2/tickets/{id}/comments         | 200/404  |
| POST   | /api/v2/tickets/{id}/comments         | 201/400/404 |
| GET    | /api/v2/users                         | 200      |
| GET    | /api/v2/users/{id}                    | 200/404  |
| GET    | /api/v2/organizations                 | 200      |

## Seed data summary

- Organizations: 4 (ids 501-504)
- Users: 7 (ids 601-607) — 1 admin, 2 agents, 4 end-users
- Tickets: 8 (ids 701-708) in mixed status (new/open/pending/solved) and
  priority (low/normal/high/urgent); two are unassigned
- Comments: 10 (ids 801-810) threaded across several tickets (mix of public
  and internal/private notes)

## Notes

- IDs are integers; new tickets/comments get the next sequential id.
- Create/update bodies use the Zendesk envelope `{"ticket": {...}}`. A `PUT`
  update may embed `{"comment": {"body", "public", "author_id"}}` to add a
  comment in the same call (this is the common move-status-and-note flow).
- `status` must be one of new/open/pending/hold/solved/closed and `priority`
  one of low/normal/high/urgent; invalid values return 400.
- New tickets start in `new` status; a create with a `comment.body` (or
  `description`) seeds the first public comment.
- List tickets supports `status`, `priority`, and `assignee_id` filters; list
  users supports a `role` filter.
- Mutations are held in process memory and reset on container restart.
