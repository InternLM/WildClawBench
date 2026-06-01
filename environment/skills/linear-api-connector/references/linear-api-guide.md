# Linear API Guide

Detailed patterns and examples for working with the Linear project management API.

## Base URL

Set via the `LINEAR_API_URL` environment variable (e.g. `http://linear-api:8004`).

## Teams

```bash
# List all teams
curl "$LINEAR_API_URL/v1/teams"

# Get a specific team
curl "$LINEAR_API_URL/v1/teams/team-backend"

# List team members
curl "$LINEAR_API_URL/v1/teams/team-backend/members"

# List team issues
curl "$LINEAR_API_URL/v1/teams/team-frontend/issues"

# List team projects
curl "$LINEAR_API_URL/v1/teams/team-backend/projects"

# List team cycles
curl "$LINEAR_API_URL/v1/teams/team-backend/cycles"

# List team workflow states
curl "$LINEAR_API_URL/v1/teams/team-backend/workflow-states"

# List team labels (includes shared labels)
curl "$LINEAR_API_URL/v1/teams/team-frontend/labels"
```

## Users

```bash
# List all users
curl "$LINEAR_API_URL/v1/users"

# Get a specific user
curl "$LINEAR_API_URL/v1/users/user-01"

# List issues assigned to a user
curl "$LINEAR_API_URL/v1/users/user-01/issues"
```

## Workflow States

```bash
# List all workflow states
curl "$LINEAR_API_URL/v1/workflow-states"

# Filter by team
curl "$LINEAR_API_URL/v1/workflow-states?teamId=team-frontend"

# Get a specific state
curl "$LINEAR_API_URL/v1/workflow-states/state-bkd-inprogress"
```

## Labels

```bash
# List all labels
curl "$LINEAR_API_URL/v1/labels"

# Filter by team (includes shared labels)
curl "$LINEAR_API_URL/v1/labels?teamId=team-platform"

# Get a specific label
curl "$LINEAR_API_URL/v1/labels/label-bug"
```

## Creating Labels

```bash
curl -X POST "$LINEAR_API_URL/v1/labels" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "needs-review",
    "color": "#F2C94C",
    "description": "Issues requiring additional review",
    "teamId": "team-backend"
  }'
```

## Projects

```bash
# List all projects
curl "$LINEAR_API_URL/v1/projects"

# Get a specific project
curl "$LINEAR_API_URL/v1/projects/proj-api-v2"

# List issues for a project
curl "$LINEAR_API_URL/v1/projects/proj-api-v2/issues"
```

## Creating Projects

```bash
curl -X POST "$LINEAR_API_URL/v1/projects" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Mobile App MVP",
    "description": "Build first version of the mobile companion app",
    "state": "planned",
    "leadId": "user-06",
    "teamIds": ["team-frontend", "team-backend"],
    "startDate": "2025-06-01",
    "targetDate": "2025-09-30"
  }'
```

## Updating Projects

```bash
curl -X PUT "$LINEAR_API_URL/v1/projects/proj-dashboard" \
  -H "Content-Type: application/json" \
  -d '{"state": "completed", "targetDate": "2025-07-01"}'
```

## Cycles

```bash
# List all cycles
curl "$LINEAR_API_URL/v1/cycles"

# Filter by team
curl "$LINEAR_API_URL/v1/cycles?teamId=team-backend"

# Filter by status (current, past, upcoming)
curl "$LINEAR_API_URL/v1/cycles?status=current"
curl "$LINEAR_API_URL/v1/cycles?status=past"

# Get a specific cycle
curl "$LINEAR_API_URL/v1/cycles/cycle-bkd-2"

# List issues in a cycle
curl "$LINEAR_API_URL/v1/cycles/cycle-bkd-2/issues"
```

## Creating Cycles

```bash
curl -X POST "$LINEAR_API_URL/v1/cycles" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Sprint 25",
    "teamId": "team-backend",
    "startsAt": "2025-05-19",
    "endsAt": "2025-06-01"
  }'
```

## Issues

```bash
# List all issues (unfiltered)
curl "$LINEAR_API_URL/v1/issues"

# Filter by state
curl "$LINEAR_API_URL/v1/issues?stateId=state-bkd-inprogress"

# Filter by assignee
curl "$LINEAR_API_URL/v1/issues?assigneeId=user-01"

# Filter by project
curl "$LINEAR_API_URL/v1/issues?projectId=proj-api-v2"

# Filter by priority (1=Urgent)
curl "$LINEAR_API_URL/v1/issues?priority=1"

# Filter by label
curl "$LINEAR_API_URL/v1/issues?labelId=label-bug"

# Filter by team
curl "$LINEAR_API_URL/v1/issues?teamId=team-platform"

# Combined filters
curl "$LINEAR_API_URL/v1/issues?stateId=state-bkd-inprogress&assigneeId=user-01"
curl "$LINEAR_API_URL/v1/issues?projectId=proj-perf&priority=2"

# Pagination
curl "$LINEAR_API_URL/v1/issues?limit=5&offset=0"

# Get a specific issue
curl "$LINEAR_API_URL/v1/issues/issue-01"
```

## Searching Issues

```bash
# Search by keyword (matches title, description, identifier)
curl "$LINEAR_API_URL/v1/issues/search?q=rate+limiting"

# Search by identifier
curl "$LINEAR_API_URL/v1/issues/search?q=MER-5"
```

## Creating Issues

```bash
curl -X POST "$LINEAR_API_URL/v1/issues" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Add rate limit headers to API responses",
    "teamId": "team-backend",
    "description": "Include X-RateLimit-Limit, X-RateLimit-Remaining, and X-RateLimit-Reset headers",
    "priority": 3,
    "estimate": 2,
    "stateId": "state-bkd-todo",
    "assigneeId": "user-02",
    "projectId": "proj-api-v2",
    "cycleId": "cycle-bkd-2",
    "labelIds": ["label-feature", "label-api"],
    "dueDate": "2025-05-10"
  }'
```

## Updating Issues

```bash
# Move to In Progress and assign
curl -X PUT "$LINEAR_API_URL/v1/issues/issue-09" \
  -H "Content-Type: application/json" \
  -d '{"stateId": "state-bkd-inprogress", "assigneeId": "user-05"}'

# Update priority and estimate
curl -X PUT "$LINEAR_API_URL/v1/issues/issue-15" \
  -H "Content-Type: application/json" \
  -d '{"priority": 3, "estimate": 5, "dueDate": "2025-06-15"}'

# Update labels
curl -X PUT "$LINEAR_API_URL/v1/issues/issue-07" \
  -H "Content-Type: application/json" \
  -d '{"labelIds": ["label-feature", "label-frontend", "label-blocked"]}'
```

## Deleting Issues

```bash
curl -X DELETE "$LINEAR_API_URL/v1/issues/issue-26"
```

## Comments

```bash
# List comments for an issue
curl "$LINEAR_API_URL/v1/issues/issue-01/comments"

# Get a specific comment
curl "$LINEAR_API_URL/v1/comments/comment-01"
```

## Creating Comments

```bash
curl -X POST "$LINEAR_API_URL/v1/comments" \
  -H "Content-Type: application/json" \
  -d '{
    "body": "Started working on this. PR coming by end of day.",
    "issueId": "issue-01",
    "userId": "user-02"
  }'
```

## Updating Comments

```bash
curl -X PUT "$LINEAR_API_URL/v1/comments/comment-01" \
  -H "Content-Type: application/json" \
  -d '{"body": "Updated: PR is ready for review at github.com/meridian-labs/api/pull/456"}'
```

## Deleting Comments

```bash
curl -X DELETE "$LINEAR_API_URL/v1/comments/comment-25"
```

## Common Patterns

### Triage Urgent Issues Across All Teams

```python
import json
import os
import urllib.request

BASE = os.environ["LINEAR_API_URL"]

def api_get(path, params=None):
    url = f"{BASE}{path}"
    if params:
        url += "?" + "&".join(f"{k}={v}" for k, v in params.items())
    with urllib.request.urlopen(url) as r:
        return json.loads(r.read())

def api_put(path, data):
    req = urllib.request.Request(
        f"{BASE}{path}",
        data=json.dumps(data).encode(),
        headers={"Content-Type": "application/json"},
        method="PUT"
    )
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())

urgent_issues = api_get("/v1/issues", {"priority": "1"})
for issue in urgent_issues.get("results", []):
    state = api_get(f"/v1/workflow-states/{issue['stateId']}")
    state_name = state["workflowState"]["name"]
    assignee = issue.get("assigneeId") or "unassigned"
    print(f"[URGENT] {issue['identifier']}: {issue['title']} ({state_name}, {assignee})")
```

### Sprint Progress Report

```python
teams = api_get("/v1/teams")
for team in teams.get("results", []):
    cycles = api_get(f"/v1/teams/{team['id']}/cycles")
    states = api_get(f"/v1/teams/{team['id']}/workflow-states")
    done_states = [s["id"] for s in states["results"] if s["type"] == "completed"]

    for cycle in cycles.get("results", []):
        if cycle.get("completedAt"):
            continue
        issues = api_get(f"/v1/cycles/{cycle['id']}/issues")
        total = issues["total"]
        done = sum(1 for i in issues["results"] if i["stateId"] in done_states)
        print(f"{team['name']} - {cycle['name']}: {done}/{total} complete ({100*done//max(total,1)}%)")
```

### Find Overdue Issues and Escalate

```python
from datetime import datetime

today = datetime.utcnow().strftime("%Y-%m-%d")
all_issues = api_get("/v1/issues")
overdue = []
for issue in all_issues.get("results", []):
    due = issue.get("dueDate")
    if due and due < today:
        state = api_get(f"/v1/workflow-states/{issue['stateId']}")
        if state["workflowState"]["type"] not in ("completed", "cancelled"):
            overdue.append(issue)
            print(f"OVERDUE: {issue['identifier']} - {issue['title']} (due {due})")
            if issue["priority"] > 2:
                api_put(f"/v1/issues/{issue['id']}", {"priority": 2})
                print(f"  -> Escalated to High priority")
```
