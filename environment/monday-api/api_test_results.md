# monday.com Mock API — Test Results

Base URL: `http://localhost:8080` (in docker-compose: `http://monday-api:8080`)

The real monday.com API is GraphQL; this mock exposes a REST-shaped surface for
consistency with the other Kensei2 environments.

## Endpoints covered

| Method | Path                          | Status  |
|--------|-------------------------------|---------|
| GET    | /health                       | 200     |
| GET    | /v2/workspaces                | 200     |
| GET    | /v2/boards                    | 200     |
| GET    | /v2/boards/{id}               | 200/404 |
| GET    | /v2/boards/{id}/items         | 200/404 |
| GET    | /v2/items                     | 200     |
| POST   | /v2/items                     | 201/400 |
| GET    | /v2/items/{id}                | 200/404 |
| PUT    | /v2/items/{id}                | 200/404 |
| DELETE | /v2/items/{id}                | 200/404 |
| GET    | /v2/users                     | 200     |

## Seed data summary

- Workspaces: 2 (Engineering, Marketing).
- Boards: 3 (Sprint Backlog, Bug Tracker, Q3 Campaigns), each with groups + columns.
- Columns: status / person (owner) / date / text per board.
- Groups: To Do / In Progress / Done style buckets (7 total).
- Items: 8 with column_values; Users: 5.

## Notes

- `GET /v2/boards/{id}` includes the board's `groups` and `columns`.
- `POST /v2/items` requires `board_id` and `item_name`; `column_values` is a map of
  `{column_id: {"text": ..., "value": ...}}`. Group defaults to the board's first group.
- `PUT /v2/items/{id}` changes a single column value (`column_id` + `text`/`value`) and/or
  moves the item to another group (`group_id`).
- Mutations are held in process memory and reset on container restart.
