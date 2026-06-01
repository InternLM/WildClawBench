# Confluence Cloud Mock API — Test Results

Base URL: `http://localhost:8045` (in docker-compose: `http://confluence-api:8045`)
All paths are prefixed with `/wiki/rest/api`.

## Endpoints covered

| Method | Path                                   | Status  |
|--------|----------------------------------------|---------|
| GET    | /health                                | 200     |
| GET    | /space                                 | 200     |
| GET    | /space/{spaceKey}                      | 200/404 |
| GET    | /content                               | 200     |
| POST   | /content                               | 201/404 |
| GET    | /content/{id}                          | 200/404 |
| PUT    | /content/{id}                          | 200/404/409 |
| GET    | /content/{id}/child/page               | 200/404 |
| GET    | /content/{id}/label                    | 200/404 |
| GET    | /content/{id}/child/comment            | 200/404 |
| GET    | /content/search?cql=                   | 200/400 |

## Seed data summary

- Spaces: 2 (`ENG` Engineering, `PROD` Product)
- Pages: 8 with parent/child relationships and version numbers
  (e.g. `Engineering Home` -> `Service Runbooks` -> `Auth Service Runbook`)
- Comments: 4 (attached to pages)
- Labels: 6 (runbook, oncall, roadmap, architecture, adr)

## Notes

- Mutations are held in process memory and reset on container restart.
- `POST /content` requires a valid `space.key` (else 404) and, if provided, a
  valid `ancestors[0].id` parent (else 404). New pages start at version 1.
- `PUT /content/{id}` bumps the version by one. If a `version.number` is supplied
  it must equal current+1, otherwise a 409 conflict is returned (optimistic lock).
- `GET /content/search?cql=` supports simplified CQL terms combined with ` AND `:
  `space=KEY`, `title~"text"`, and `type=page`.
- Page bodies are returned in Confluence storage format under
  `body.storage.value`.
