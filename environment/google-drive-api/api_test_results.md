# Google Drive API Mock — Test Results

Base URL: `http://localhost:8018` (docker-compose: `http://google-drive-api:8018`)

## Endpoints

| Method | Path                                              | Status   |
|--------|---------------------------------------------------|----------|
| GET    | /health                                           | 200      |
| GET    | /drive/v3/about                                   | 200      |
| GET    | /drive/v3/files                                   | 200      |
| GET    | /drive/v3/files/{file_id}                         | 200/404  |
| POST   | /drive/v3/files                                   | 201/404  |
| PATCH  | /drive/v3/files/{file_id}                         | 200/404  |
| POST   | /drive/v3/files/{file_id}/trash                   | 200/404  |
| DELETE | /drive/v3/files/{file_id}                         | 200/404  |
| GET    | /drive/v3/files/{file_id}/permissions             | 200/404  |
| POST   | /drive/v3/files/{file_id}/permissions             | 201/404  |
| DELETE | /drive/v3/files/{file_id}/permissions/{perm_id}   | 200/404  |

## Query operators supported

- `'<parent_id>' in parents`
- `trashed = true|false`, `starred = true`
- `mimeType = '...'`, `name = '...'`, `name contains '...'`
- Multiple clauses joined by ` and `.

## Seed data

- 1 root + 3 nested folders, 7 files
- 9 permission rows (owner / writer / commenter / domain reader)
