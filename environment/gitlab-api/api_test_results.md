# GitLab Mock API — Test Results

Base URL: `http://localhost:8046` (docker-compose: `http://gitlab-api:8046`)

## Endpoints

| Method | Path                                                       | Status   |
|--------|------------------------------------------------------------|----------|
| GET    | /health                                                    | 200      |
| GET    | /api/v4/user                                               | 200      |
| GET    | /api/v4/projects                                           | 200      |
| GET    | /api/v4/projects/{id}                                       | 200/404  |
| GET    | /api/v4/projects/{id}/issues                                | 200/404  |
| GET    | /api/v4/projects/{id}/issues/{iid}                          | 200/404  |
| POST   | /api/v4/projects/{id}/issues                                | 201/404  |
| PUT    | /api/v4/projects/{id}/issues/{iid}                          | 200/404  |
| GET    | /api/v4/projects/{id}/merge_requests                        | 200/404  |
| POST   | /api/v4/projects/{id}/merge_requests                        | 201/404  |
| PUT    | /api/v4/projects/{id}/merge_requests/{iid}/merge            | 200/404/405 |
| GET    | /api/v4/projects/{id}/pipelines                             | 200/404  |

## Seed data

- 3 projects under `orbit-labs` (auth-service, billing-service, web-frontend)
- 7 issues across the projects (mix of opened and closed)
- 5 merge requests (opened and merged)
- 7 pipelines (success, failed, running)
- 5 users (active and blocked); current user is `amelia-ortega`

## Notes

- Mutations are held in process memory and reset on container restart.
- `state` filters accept `opened`, `closed`, or `all` for issues and merge requests.
- Issue updates use `state_event` of `close` or `reopen`; closing decrements `open_issues_count`.
- Merging a draft or non-mergeable MR returns 405; an unknown project/MR returns 404.
- Project lookups accept the numeric project id.
