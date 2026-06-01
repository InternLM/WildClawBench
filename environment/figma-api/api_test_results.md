# Figma Mock API — Test Results

Base URL: `http://localhost:8079` (in docker-compose: `http://figma-api:8079`)

## Endpoints covered

| Method | Path                                  | Status  |
|--------|---------------------------------------|---------|
| GET    | /health                               | 200     |
| GET    | /v1/me                                | 200     |
| GET    | /v1/teams/{team_id}/projects          | 200/404 |
| GET    | /v1/projects/{project_id}/files       | 200/404 |
| GET    | /v1/files/{file_key}                  | 200/404 |
| GET    | /v1/files/{file_key}/nodes            | 200/404 |
| GET    | /v1/files/{file_key}/comments         | 200/404 |
| POST   | /v1/files/{file_key}/comments         | 201/404 |
| GET    | /v1/files/{file_key}/components       | 200/404 |

## Seed data summary

- Team: `team-501` (Orbit Labs Design); current user `user-1001` (Priya Nair) + 2 others.
- Projects: 3 (Mobile App, Marketing Website, Design System).
- Files: 4, each with a DOCUMENT > CANVAS > FRAME node tree (stored as JSON in `file_nodes.json`).
- Comments: 4 (with `node_id` and resolved flag).
- Components: 5 (buttons, text input, card, nav bar).

## Notes

- `/v1/files/{file_key}` returns the full document node tree plus a `components` map.
- `/v1/files/{file_key}/nodes?ids=` returns a `nodes` map keyed by node id; unknown ids map to `null`.
- Created comments are held in process memory and reset on container restart.
