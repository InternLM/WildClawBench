# Documentation Faithfulness Check

## Source
- https://studio.apollographql.com/public/Linear-API/variant/current/schema/reference (Linear GraphQL Schema Explorer)
- https://developers.linear.app/docs/graphql (Getting Started)
- https://developers.linear.app/docs/graphql/working-with-the-graphql-api
- https://github.com/linear/linear/issues/600 (stateId field confirmation)

## Note on REST vs GraphQL
Linear uses a **GraphQL API only** — there is no official REST API. Our mock intentionally exposes Linear's data model via RESTful endpoints (as stated in the project spec). The entity names, field names, and relationships are taken directly from Linear's GraphQL schema. The endpoint paths (`/v1/issues`, `/v1/teams`, etc.) are our own REST translation — there is no "official REST path" to compare against.

## Entity Field Names Comparison

| # | Entity | Our Field | Linear Schema Field | Match? | Notes |
|---|--------|-----------|---------------------|--------|-------|
| 1 | Issue | id | id (ID!) | ✓ | |
| 2 | Issue | identifier | identifier (String!) | ✓ | e.g. "ENG-123" |
| 3 | Issue | number | number (Float) | ✓ | We use int, Linear uses Float |
| 4 | Issue | title | title (String!) | ✓ | |
| 5 | Issue | description | description (String) | ✓ | |
| 6 | Issue | priority | priority (Float!) | ✓ | 0=None, 1=Urgent, 2=High, 3=Normal, 4=Low |
| 7 | Issue | estimate | estimate (Float) | ✓ | |
| 8 | Issue | stateId | state (WorkflowState!) / stateId on input | ✓ | Schema exposes relation; SDK exposes stateId |
| 9 | Issue | assigneeId | assignee (User) / assigneeId on input | ✓ | Same pattern as stateId |
| 10 | Issue | teamId | team (Team!) | ✓ | Input field for create |
| 11 | Issue | projectId | project (Project) | ✓ | |
| 12 | Issue | cycleId | cycle (Cycle) | ✓ | |
| 13 | Issue | labelIds | labels (IssueLabelConnection) | ✓ | Input uses labelIds array |
| 14 | Issue | dueDate | dueDate (TimelessDate) | ✓ | |
| 15 | Issue | sortOrder | sortOrder (Float!) | ✓ | boardOrder deprecated in favor of sortOrder |
| 16 | Issue | branchName | branchName (String!) | ✓ | |
| 17 | Issue | createdAt | createdAt (DateTime!) | ✓ | |
| 18 | Issue | updatedAt | updatedAt (DateTime!) | ✓ | |
| 19 | Issue | startedAt | startedAt (DateTime) | ✓ | |
| 20 | Issue | completedAt | completedAt (DateTime) | ✓ | |
| 21 | Issue | canceledAt | canceledAt (DateTime) | ✓ | Fixed: was "cancelledAt", Linear uses single L |
| 22 | Team | id, name, key, description, color | id, name, key, description, color | ✓ | |
| 23 | User | id, name, displayName, email, active, admin | id, name, displayName, email, active, admin | ✓ | |
| 24 | WorkflowState | id, name, type, color, position, description | id, name, type, color, position, description | ✓ | Types: triage, backlog, unstarted, started, completed, cancelled |
| 25 | Label | id, name, color, description | id, name, color, description | ✓ | |
| 26 | Project | id, name, description, state, startDate, targetDate | id, name, description, state, startDate, targetDate | ✓ | |
| 27 | Cycle | id, name, number, startsAt, endsAt, completedAt | id, name, number, startsAt, endsAt, completedAt | ✓ | |
| 28 | Comment | id, body, createdAt, updatedAt | id, body, createdAt, updatedAt | ✓ | |

## Endpoint Paths (REST Translation)

| # | Endpoint | Our Path | Notes |
|---|----------|----------|-------|
| 1 | Health | GET /health | Standard pattern from reference |
| 2 | List teams | GET /v1/teams | Maps to `teams` query |
| 3 | Get team | GET /v1/teams/{id} | Maps to `team(id:)` query |
| 4 | Team members | GET /v1/teams/{id}/members | Maps to team.members |
| 5 | Team issues | GET /v1/teams/{id}/issues | Maps to team.issues |
| 6 | Team projects | GET /v1/teams/{id}/projects | Maps to team.projects |
| 7 | Team cycles | GET /v1/teams/{id}/cycles | Maps to team.cycles |
| 8 | Team states | GET /v1/teams/{id}/workflow-states | Maps to team.states |
| 9 | Team labels | GET /v1/teams/{id}/labels | Maps to team.labels |
| 10 | List users | GET /v1/users | Maps to `users` query |
| 11 | Get user | GET /v1/users/{id} | Maps to `user(id:)` query |
| 12 | User issues | GET /v1/users/{id}/issues | Maps to user.assignedIssues |
| 13 | List states | GET /v1/workflow-states | Maps to `workflowStates` query |
| 14 | Get state | GET /v1/workflow-states/{id} | Maps to `workflowState(id:)` |
| 15 | List labels | GET /v1/labels | Maps to `issueLabels` query |
| 16 | Get label | GET /v1/labels/{id} | Maps to `issueLabel(id:)` |
| 17 | Create label | POST /v1/labels | Maps to `issueLabelCreate` mutation |
| 18 | List projects | GET /v1/projects | Maps to `projects` query |
| 19 | Get project | GET /v1/projects/{id} | Maps to `project(id:)` |
| 20 | Create project | POST /v1/projects | Maps to `projectCreate` mutation |
| 21 | Update project | PUT /v1/projects/{id} | Maps to `projectUpdate` mutation |
| 22 | Project issues | GET /v1/projects/{id}/issues | Maps to project.issues |
| 23 | List cycles | GET /v1/cycles | Maps to `cycles` query |
| 24 | Get cycle | GET /v1/cycles/{id} | Maps to `cycle(id:)` |
| 25 | Create cycle | POST /v1/cycles | Maps to `cycleCreate` mutation |
| 26 | Cycle issues | GET /v1/cycles/{id}/issues | Maps to cycle.issues |
| 27 | List issues | GET /v1/issues | Maps to `issues` query with filters |
| 28 | Get issue | GET /v1/issues/{id} | Maps to `issue(id:)` |
| 29 | Search issues | GET /v1/issues/search | Maps to `issueSearch` query |
| 30 | Create issue | POST /v1/issues | Maps to `issueCreate` mutation |
| 31 | Update issue | PUT /v1/issues/{id} | Maps to `issueUpdate` mutation |
| 32 | Delete issue | DELETE /v1/issues/{id} | Maps to `issueArchive` mutation |
| 33 | List comments | GET /v1/issues/{id}/comments | Maps to issue.comments |
| 34 | Get comment | GET /v1/comments/{id} | Maps to `comment(id:)` |
| 35 | Create comment | POST /v1/comments | Maps to `commentCreate` mutation |
| 36 | Update comment | PUT /v1/comments/{id} | Maps to `commentUpdate` mutation |
| 37 | Delete comment | DELETE /v1/comments/{id} | Maps to `commentDelete` mutation |

## Issues Found and Fixed

| # | Issue | Fix Applied |
|---|-------|-------------|
| 1 | `cancelledAt` used double-L spelling | Changed to `canceledAt` to match Linear's schema |

## Summary
- **28 field names checked** — all match Linear's GraphQL schema (after fix)
- **37 endpoint paths verified** — all correctly map to Linear's GraphQL operations
- **1 issue found and fixed** — `cancelledAt` → `canceledAt`
