# GitHub REST API Mock — Test Results

Base URL: `http://localhost:8019` (docker-compose: `http://github-api:8019`)

## Endpoints

| Method | Path                                              | Status   |
|--------|---------------------------------------------------|----------|
| GET    | /health                                           | 200      |
| GET    | /user                                             | 200      |
| GET    | /users/{owner}/repos                              | 200      |
| GET    | /orgs/{owner}/repos                               | 200      |
| GET    | /repos/{owner}/{repo}                             | 200/404  |
| GET    | /repos/{owner}/{repo}/issues                      | 200/404  |
| GET    | /repos/{owner}/{repo}/issues/{number}             | 200/404  |
| POST   | /repos/{owner}/{repo}/issues                      | 201/404  |
| PATCH  | /repos/{owner}/{repo}/issues/{number}             | 200/404  |
| GET    | /repos/{owner}/{repo}/pulls                       | 200/404  |
| GET    | /repos/{owner}/{repo}/pulls/{number}              | 200/404  |
| PUT    | /repos/{owner}/{repo}/pulls/{number}/merge        | 200/405  |
| GET    | /repos/{owner}/{repo}/issues/{number}/comments    | 200/404  |
| POST   | /repos/{owner}/{repo}/issues/{number}/comments    | 201/404  |

## Seed data

- 5 repos under `orbit-labs`
- 8 issues (4 open across auth/billing/web/infra; 1 closed)
- 2 pull requests (one in APPROVED, one draft)
- 5 issue comments

## Notes

- PR merge will 405 with `"PR is not mergeable"` for draft PRs.
- Closing an issue updates `closed_at` and decrements the repo's `open_issues`.
