# Asana Mock API — Test Results

Base URL: `http://localhost:8031` (in docker-compose: `http://asana-api:8031`)

## Endpoints covered

| Method | Path                                      | Status  |
|--------|-------------------------------------------|---------|
| GET    | /health                                   | 200     |
| GET    | /api/1.0/workspaces                       | 200     |
| GET    | /api/1.0/users                            | 200     |
| GET    | /api/1.0/projects                         | 200     |
| GET    | /api/1.0/projects/{project_gid}           | 200/404 |
| GET    | /api/1.0/projects/{project_gid}/sections  | 200/404 |
| GET    | /api/1.0/projects/{project_gid}/tasks     | 200/404 |
| GET    | /api/1.0/tasks                            | 200     |
| POST   | /api/1.0/tasks                            | 201/400 |
| GET    | /api/1.0/tasks/{task_gid}                 | 200/404 |
| PUT    | /api/1.0/tasks/{task_gid}                 | 200/404 |

## Seed data summary

- Workspace: `1201990000000001` (Northwind Studio)
- Users: 5
- Projects: 3 (Website Redesign, Mobile App v2, Customer Onboarding)
- Sections: 8 (across the 3 projects)
- Tasks: 12 (mixed completed flags, assignees, and due dates)

## Notes

- Resource IDs are Asana-style `gid` strings.
- Responses wrap payloads in a `data` envelope to match the real API.
- `PUT /api/1.0/tasks/{task_gid}` accepts `completed`, `assignee`, `due_on`,
  `section`, `name`, and `notes` inside the `data` body.
- `POST /api/1.0/tasks` accepts either `project` or a `projects` array.
- Mutations are held in process memory and reset on container restart.
