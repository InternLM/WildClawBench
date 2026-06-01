# Dropbox API v2 Mock — Test Results

Base URL: `http://localhost:8082` (in docker-compose: `http://dropbox-api:8082`)

## Endpoints covered

| Method | Path                                | Status  |
|--------|-------------------------------------|---------|
| GET    | /health                             | 200     |
| POST   | /2/users/get_current_account        | 200     |
| POST   | /2/files/list_folder                | 200     |
| POST   | /2/files/get_metadata               | 200/409 |
| POST   | /2/files/search_v2                  | 200     |
| POST   | /2/sharing/list_shared_links        | 200     |

## Seed data summary

- Account: 1 business account (Maya Robinson) for `get_current_account`.
- Files: 10 entries (3 folders, 7 files) under /Documents, /Photos, /Projects
  with id, path_lower/path_display, size, client_modified and rev.
- Shared links: 4 links (public, team_only, password visibility) tied to files.

## Notes

- Like the real Dropbox API v2, all resource endpoints are POST and read their
  arguments from a JSON request body (e.g. `{"path": "/Documents"}`).
- `/2/files/list_folder` returns direct children by default; pass
  `{"recursive": true}` to descend into all subfolders. Root is `""` or `"/"`.
- `/2/files/get_metadata` accepts a `path` or a file `id`; an unknown path
  returns HTTP 409 with a `path/not_found/` error summary (Dropbox convention).
- `/2/files/search_v2` filters by case-insensitive `query` against file names and
  can be scoped via `options.path`.
- Mutations are held in process memory and reset on container restart (this mock
  is read-only).
