# Notion Mock API — Test Results

Base URL: `http://localhost:8010` (in docker-compose: `http://notion-api:8010`)

## Endpoints covered

| Method | Path                                  | Status |
|--------|---------------------------------------|--------|
| GET    | /health                               | 200    |
| GET    | /v1/users                             | 200    |
| GET    | /v1/users/me                          | 200    |
| GET    | /v1/users/{user_id}                   | 200/404 |
| GET    | /v1/workspace                         | 200    |
| POST   | /v1/search                            | 200    |
| GET    | /v1/databases/{database_id}           | 200/404 |
| POST   | /v1/databases/{database_id}/query     | 200/404 |
| GET    | /v1/pages/{page_id}                   | 200/404 |
| POST   | /v1/pages                             | 201/400 |
| PATCH  | /v1/pages/{page_id}                   | 200/404 |
| DELETE | /v1/pages/{page_id}                   | 200/404 |
| GET    | /v1/blocks/{block_id}/children        | 200    |
| PATCH  | /v1/blocks/{block_id}/children        | 200/404 |
| PATCH  | /v1/blocks/{block_id}                 | 200/404 |
| DELETE | /v1/blocks/{block_id}                 | 200/404 |
| GET    | /v1/comments                          | 200    |
| POST   | /v1/comments                          | 201/404 |

## Seed data summary

- Workspace: `workspace-orbit-labs` (Orbit Labs)
- Users: 5 people + 1 bot
- Databases: 4 (engineering tasks, OKRs, meeting notes, customer research)
- Pages: 11 (mix of database rows and parent pages)
- Blocks: 10 (mix of paragraph, heading, to_do, bulleted_list_item, callout)
- Comments: 4

## Notes

- Mutations are held in process memory and reset on container restart.
- Search filter accepts `{"property": "object", "value": "page" | "database"}`.
- Database query supports `filter.property = "Status" | "Assignee"` and a single
  `sorts[0].timestamp` of `last_edited_time` or `created_time`.
