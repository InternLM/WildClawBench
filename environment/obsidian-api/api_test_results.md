# Obsidian Mock API — Test Results

Base URL: `http://localhost:8014` (docker-compose: `http://obsidian-api:8014`)

## Endpoints

| Method | Path                              | Status   |
|--------|-----------------------------------|----------|
| GET    | /health                           | 200      |
| GET    | /vault                            | 200      |
| GET    | /vault/notes                      | 200      |
| GET    | /vault/notes/{path}               | 200/404  |
| POST   | /vault/notes                      | 201/409  |
| PUT    | /vault/notes/{path}               | 200/404  |
| DELETE | /vault/notes/{path}               | 200/404  |
| GET    | /vault/search?query=              | 200      |
| GET    | /vault/backlinks/{path}           | 200      |
| GET    | /vault/daily/{YYYY-MM-DD}         | 200/404  |

## Seed data

- Vault: `research-vault`
- Notes: 9 (Daily, Projects, References, Inbox folders)
- Wikilinks across project notes for backlink testing

## Notes

- `path` parameters accept the full vault-relative path including the `.md` extension.
- `PUT` accepts either `{"content": "..."}` to replace or `{"append": "..."}` to extend.
- Search runs against title, path, and body. Pass `content=true` to include a body snippet.
