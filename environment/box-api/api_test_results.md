# Box API Mock — Test Results

Base URL: `http://localhost:8083` (in docker-compose: `http://box-api:8083`)

## Endpoints covered

| Method | Path                              | Status  |
|--------|-----------------------------------|---------|
| GET    | /health                           | 200     |
| GET    | /2.0/users/me                     | 200     |
| GET    | /2.0/folders/{folder_id}          | 200/404 |
| GET    | /2.0/folders/{folder_id}/items    | 200/404 |
| GET    | /2.0/files/{file_id}              | 200/404 |
| GET    | /2.0/search                       | 200     |

## Seed data summary

- Users: 3 (admin Aaron Levie + 2 users) with role, status, space usage.
- Folders: 5 including the root folder (id `0`); Marketing/Engineering/Finance
  hang off root and Campaigns is nested under Marketing.
- Files: 6 across the folders with size, extension and sha1.

## Notes

- Responses use Box-style envelopes: collection endpoints return
  `{"total_count", "entries", "offset", "limit"}` and objects carry a `type`
  field (`user`/`folder`/`file`).
- The root folder is id `0`; `/2.0/folders/0/items` lists its child folders and
  files. Pagination is via `limit`/`offset` query params.
- `/2.0/search` filters by case-insensitive `query` against names and can be
  restricted with `type=file` or `type=folder`.
- Unknown folder/file ids return HTTP 404 with a Box `type=error` body.
- Mutations are held in process memory and reset on container restart (this mock
  is read-only).
