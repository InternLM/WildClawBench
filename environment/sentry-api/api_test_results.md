# Sentry Mock API — Test Results

Base URL: `http://localhost:8047` (docker-compose: `http://sentry-api:8047`)

## Endpoints

| Method | Path                                                          | Status   |
|--------|---------------------------------------------------------------|----------|
| GET    | /health                                                       | 200      |
| GET    | /api/0/organizations/{org}/projects/                          | 200/404  |
| GET    | /api/0/projects/{org}/{project}/issues/                       | 200/404  |
| GET    | /api/0/organizations/{org}/issues/{issue_id}/                 | 200/404  |
| PUT    | /api/0/organizations/{org}/issues/{issue_id}/                 | 200/400/404 |
| GET    | /api/0/organizations/{org}/issues/{issue_id}/events/          | 200/404  |
| GET    | /api/0/organizations/{org}/releases/                          | 200/404  |

## Seed data

- 1 organization (`orbit-labs`)
- 3 projects (auth-service, web-frontend, billing-service)
- 8 issues (levels error/warning; statuses unresolved/resolved/ignored; with culprit, count, userCount)
- 5 events linked to issues
- 5 releases (with newGroups counts and release dates)

## Notes

- Mutations are held in process memory and reset on container restart.
- PUT issue accepts `status` of `resolved`, `ignored`, or `unresolved`; any other value returns 400.
- Issue list filters support `status` and `level` query params.
- Release list can be narrowed with the `project` query param.
