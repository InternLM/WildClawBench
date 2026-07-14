---
name: linear-api-connector
description: >
  Linear REST API HTTP endpoints for issue tracking, project management,
  sprint cycles, team workflows, and workspace organization.
---

# Linear API

## Base URL

| Variable | Purpose |
|----------|---------|
| `LINEAR_API_URL` | Base URL for all requests |

All paths below are relative to `LINEAR_API_URL`.

---

## Health

```
GET /health
```

Returns `{"status": "ok"}`.

---

## Teams

### List teams

Returns a paginated list of all teams in the workspace. Each team includes its ID, name, key prefix, description, and timezone.

```
GET /v1/teams
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `limit` | integer | query | no | Maximum results, 1-100. Default: 50 |
| `offset` | integer | query | no | Number of results to skip. Default: 0 |

### Get team

Returns the full details of a single team, including its name, key, description, timezone, member count, and associated workflow states.

```
GET /v1/teams/{team_id}
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `team_id` | string | path | yes | Team identifier |

### List team members

Returns the list of users who are members of a specific team. Each member includes their ID, name, display name, email, and role.

```
GET /v1/teams/{team_id}/members
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `team_id` | string | path | yes | Team identifier |

### List team issues

Returns a paginated list of all issues belonging to a team, regardless of state.

```
GET /v1/teams/{team_id}/issues
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `team_id` | string | path | yes | Team identifier |
| `limit` | integer | query | no | Maximum results, 1-100. Default: 50 |
| `offset` | integer | query | no | Number of results to skip. Default: 0 |

### List team projects

Returns all projects associated with a specific team.

```
GET /v1/teams/{team_id}/projects
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `team_id` | string | path | yes | Team identifier |

### List team cycles

Returns all sprint cycles belonging to a specific team.

```
GET /v1/teams/{team_id}/cycles
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `team_id` | string | path | yes | Team identifier |

### List team workflow states

Returns the workflow states defined for a specific team. States represent the lifecycle stages of an issue (e.g., Triage, Todo, In Progress, Done, Canceled). Each state includes its ID, name, type, color, and position.

```
GET /v1/teams/{team_id}/workflow-states
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `team_id` | string | path | yes | Team identifier |

### List team labels

Returns the labels available to a specific team, including both team-specific and shared workspace labels.

```
GET /v1/teams/{team_id}/labels
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `team_id` | string | path | yes | Team identifier |

---

## Users

### List users

Returns a paginated list of all users in the workspace. Each user includes their ID, name, display name, email, active status, and admin flag.

```
GET /v1/users
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `limit` | integer | query | no | Maximum results, 1-100. Default: 50 |
| `offset` | integer | query | no | Number of results to skip. Default: 0 |

### Get user

Returns the full profile of a single user, including their name, email, display name, avatar URL, active status, admin flag, and creation date.

```
GET /v1/users/{user_id}
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `user_id` | string | path | yes | User identifier |

### List user issues

Returns a paginated list of issues assigned to a specific user across all teams.

```
GET /v1/users/{user_id}/issues
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `user_id` | string | path | yes | User identifier |
| `limit` | integer | query | no | Maximum results, 1-100. Default: 50 |
| `offset` | integer | query | no | Number of results to skip. Default: 0 |

---

## Workflow States

### List workflow states

Returns a paginated list of all workflow states across the workspace. States can be filtered by team. Each state includes its ID, name, type (triage, backlog, unstarted, started, completed, canceled), color, position, and team ID.

```
GET /v1/workflow-states
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `teamId` | string | query | no | Filter states by team ID |
| `limit` | integer | query | no | Maximum results, 1-100. Default: 50 |
| `offset` | integer | query | no | Number of results to skip. Default: 0 |

### Get workflow state

Returns the details of a single workflow state, including its name, type, color, position, and associated team.

```
GET /v1/workflow-states/{state_id}
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `state_id` | string | path | yes | Workflow state identifier |

---

## Labels

### List labels

Returns a paginated list of all labels in the workspace. Labels can be filtered by team. Each label includes its ID, name, color, description, and whether it is scoped to a team or shared globally.

```
GET /v1/labels
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `teamId` | string | query | no | Filter by team ID (includes shared labels) |
| `limit` | integer | query | no | Maximum results, 1-100. Default: 50 |
| `offset` | integer | query | no | Number of results to skip. Default: 0 |

### Get label

Returns the details of a single label, including its name, color, description, team scope, and creation date.

```
GET /v1/labels/{label_id}
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `label_id` | string | path | yes | Label identifier |

### Create label

Creates a new label in the workspace. Labels can be scoped to a specific team or shared globally. Returns the created label with a server-generated ID.

```
POST /v1/labels
```

**Request body**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | yes | Label name |
| `color` | string | no | Hex color code (e.g. `#F2C94C`) |
| `description` | string | no | Label description |
| `teamId` | string | no | Team ID to scope the label to. Omit for a workspace-wide label. |

---

## Projects

### List projects

Returns a paginated list of all projects in the workspace. Each project includes its ID, name, description, state (planned, started, paused, completed, canceled), lead, target date, and progress metrics.

```
GET /v1/projects
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `limit` | integer | query | no | Maximum results, 1-100. Default: 50 |
| `offset` | integer | query | no | Number of results to skip. Default: 0 |

### Get project

Returns the full details of a single project, including its name, description, state, lead user, associated teams, start and target dates, issue counts, and progress percentage.

```
GET /v1/projects/{project_id}
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `project_id` | string | path | yes | Project identifier |

### Create project

Creates a new project in the workspace. Projects group related issues across one or more teams. Returns the created project with a server-generated ID.

```
POST /v1/projects
```

**Request body**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | yes | Project name |
| `description` | string | no | Project description |
| `state` | string | no | Initial state: `planned`, `started`, `paused`, `completed`, `canceled`. Default: `planned` |
| `leadId` | string | no | User ID of the project lead |
| `teamIds` | array of strings | no | Team IDs associated with this project |
| `startDate` | string | no | Project start date (YYYY-MM-DD) |
| `targetDate` | string | no | Target completion date (YYYY-MM-DD) |

### Update project

Updates an existing project's properties. Only the provided fields are modified. Returns the updated project.

```
PUT /v1/projects/{project_id}
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `project_id` | string | path | yes | Project identifier |

**Request body**

Same fields as Create project. All fields are optional.

### List project issues

Returns a paginated list of issues belonging to a specific project.

```
GET /v1/projects/{project_id}/issues
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `project_id` | string | path | yes | Project identifier |
| `limit` | integer | query | no | Maximum results, 1-100. Default: 50 |
| `offset` | integer | query | no | Number of results to skip. Default: 0 |

---

## Cycles

### List cycles

Returns a paginated list of sprint cycles across the workspace. Cycles can be filtered by team and lifecycle status. Each cycle includes its ID, name, team, start/end dates, status, and issue count.

```
GET /v1/cycles
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `teamId` | string | query | no | Filter by team ID |
| `status` | string | query | no | Filter by status: `current`, `past`, `upcoming` |
| `limit` | integer | query | no | Maximum results, 1-100. Default: 50 |
| `offset` | integer | query | no | Number of results to skip. Default: 0 |

### Get cycle

Returns the full details of a single cycle, including its name, team, start and end dates, status, completed issue count, total scope, and progress metrics.

```
GET /v1/cycles/{cycle_id}
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `cycle_id` | string | path | yes | Cycle identifier |

### Create cycle

Creates a new sprint cycle for a team. Returns the created cycle with a server-generated ID.

```
POST /v1/cycles
```

**Request body**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | yes | Cycle name |
| `teamId` | string | yes | Team ID the cycle belongs to |
| `startsAt` | string | yes | Cycle start date (YYYY-MM-DD) |
| `endsAt` | string | yes | Cycle end date (YYYY-MM-DD) |

### List cycle issues

Returns a paginated list of issues assigned to a specific cycle.

```
GET /v1/cycles/{cycle_id}/issues
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `cycle_id` | string | path | yes | Cycle identifier |
| `limit` | integer | query | no | Maximum results, 1-100. Default: 50 |
| `offset` | integer | query | no | Number of results to skip. Default: 0 |

---

## Issues

### List issues

Returns a paginated list of issues across the workspace. Supports extensive filtering by workflow state, assignee, project, cycle, team, priority, and label. Each issue includes its ID, identifier, title, description, priority, estimate, state, assignee, project, cycle, labels, due date, and timestamps.

```
GET /v1/issues
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `stateId` | string | query | no | Filter by workflow state ID |
| `assigneeId` | string | query | no | Filter by assignee user ID |
| `projectId` | string | query | no | Filter by project ID |
| `cycleId` | string | query | no | Filter by cycle ID |
| `teamId` | string | query | no | Filter by team ID |
| `priority` | integer | query | no | Filter by priority: 0 (None), 1 (Urgent), 2 (High), 3 (Medium), 4 (Low) |
| `labelId` | string | query | no | Filter by label ID |
| `limit` | integer | query | no | Maximum results, 1-100. Default: 50 |
| `offset` | integer | query | no | Number of results to skip. Default: 0 |

### Search issues

Performs a full-text search across issue titles, descriptions, and identifiers. Returns matching issues ranked by relevance.

```
GET /v1/issues/search
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `q` | string | query | yes | Search query string |
| `limit` | integer | query | no | Maximum results |
| `offset` | integer | query | no | Number of results to skip |

### Get issue

Returns the full details of a single issue, including its identifier, title, description, priority, estimate, workflow state, assignee, project, cycle, labels, due date, sort order, and all timestamps.

```
GET /v1/issues/{issue_id}
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `issue_id` | string | path | yes | Issue identifier |

### Create issue

Creates a new issue in the specified team. Returns the created issue with a server-generated ID and team-prefixed identifier.

```
POST /v1/issues
```

**Request body**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `title` | string | yes | Issue title |
| `teamId` | string | yes | Team ID the issue belongs to |
| `description` | string | no | Issue description (Markdown supported) |
| `priority` | integer | no | Priority: 0 (None), 1 (Urgent), 2 (High), 3 (Medium), 4 (Low) |
| `estimate` | number | no | Effort estimate in story points |
| `stateId` | string | no | Initial workflow state ID |
| `assigneeId` | string | no | Assigned user ID |
| `projectId` | string | no | Project ID |
| `cycleId` | string | no | Cycle ID |
| `labelIds` | array of strings | no | Label IDs to apply |
| `dueDate` | string | no | Due date (YYYY-MM-DD) |

### Update issue

Updates an existing issue's properties. Only the provided fields are modified. Returns the updated issue.

```
PUT /v1/issues/{issue_id}
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `issue_id` | string | path | yes | Issue identifier |

**Request body**

Same fields as Create issue (except `teamId` cannot be changed). Additional field:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `sortOrder` | number | no | Custom sort position within lists |

### Delete issue

Permanently deletes an issue and all associated comments. This action cannot be undone.

```
DELETE /v1/issues/{issue_id}
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `issue_id` | string | path | yes | Issue identifier |

---

## Comments

### List issue comments

Returns a paginated list of comments on a specific issue. Each comment includes its ID, body text, author, creation time, and update time.

```
GET /v1/issues/{issue_id}/comments
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `issue_id` | string | path | yes | Issue identifier |
| `limit` | integer | query | no | Maximum results, 1-100. Default: 50 |
| `offset` | integer | query | no | Number of results to skip. Default: 0 |

### Get comment

Returns the full details of a single comment, including its body, author user ID, associated issue ID, and timestamps.

```
GET /v1/comments/{comment_id}
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `comment_id` | string | path | yes | Comment identifier |

### Create comment

Adds a new comment to an issue. Returns the created comment with a server-generated ID.

```
POST /v1/comments
```

**Request body**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `body` | string | yes | Comment text (Markdown supported) |
| `issueId` | string | yes | Issue ID to comment on |
| `userId` | string | no | Author user ID. Defaults to the authenticated user. |

### Update comment

Edits the text of an existing comment. Returns the updated comment.

```
PUT /v1/comments/{comment_id}
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `comment_id` | string | path | yes | Comment identifier |

**Request body**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `body` | string | yes | Updated comment text |

### Delete comment

Permanently deletes a comment. This action cannot be undone.

```
DELETE /v1/comments/{comment_id}
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `comment_id` | string | path | yes | Comment identifier |

---

## Errors

Error responses follow this format:

```json
{
  "error": {
    "message": "Description of the error",
    "code": "NOT_FOUND"
  }
}
```

Common HTTP status codes:

| Code | Meaning |
|------|---------|
| 400 | Bad request (invalid parameters or malformed body) |
| 404 | Resource not found |
| 409 | Conflict (duplicate resource) |
