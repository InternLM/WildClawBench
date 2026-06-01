# Jira Mock API — Test Results

Base URL: `http://localhost:8029` (in docker-compose: `http://jira-api:8029`)

## Endpoints covered

| Method | Path                                          | Status  |
|--------|-----------------------------------------------|---------|
| GET    | /health                                       | 200     |
| GET    | /rest/api/3/project                           | 200     |
| POST   | /rest/api/3/issue                             | 201/400 |
| GET    | /rest/api/3/issue/{issueKey}                  | 200/404 |
| PUT    | /rest/api/3/issue/{issueKey}                  | 204/404 |
| GET    | /rest/api/3/issue/{issueKey}/transitions      | 200/404 |
| POST   | /rest/api/3/issue/{issueKey}/transitions      | 204/400/404 |
| GET    | /rest/api/3/search?jql=                        | 200     |
| GET    | /rest/agile/1.0/board                          | 200     |
| GET    | /rest/agile/1.0/board/{boardId}/sprint         | 200/404 |

## Seed data summary

- Projects: 2 (ENG Engineering, OPS Operations)
- Users: 5 (Amelia, Jonas, Helena, Rohit, Noor)
- Boards: 2 (ENG scrum, OPS kanban)
- Sprints: 4 (ENG closed/active/future + 1 OPS continuous)
- Issues: 10 across `To Do` / `In Progress` / `Done` with story points, priorities,
  assignees and sprint links. Keys like `ENG-101`, `OPS-201`.

## Notes

- Mutations are held in process memory and reset on container restart.
- Created issues start in `To Do` and are returned in the lightweight
  `{id, key, self}` shape, matching the real create response.
- Transition workflow: `To Do` --11--> `In Progress` --21--> `Done`
  (with `31` back to `To Do` and `41` reopen from `Done`). Invalid transitions 400.
- `GET /rest/api/3/search` parses a small JQL subset: `project = X` and/or
  `status = Y` joined by `AND` (values may be quoted).
- Story points are exposed as `customfield_10016`.
