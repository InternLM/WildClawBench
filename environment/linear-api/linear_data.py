"""Data access module for Linear API simulation."""

import csv
import json
from copy import deepcopy
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).parent


def _load(filename):
    with open(DATA_DIR / filename, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _now():
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")


# ---------------------------------------------------------------------------
# Load and coerce data
# ---------------------------------------------------------------------------

def _coerce_teams(rows):
    out = []
    for r in rows:
        out.append({
            **r,
            "id": r["id"],
            "name": r["name"],
            "key": r["key"],
            "description": r["description"],
            "color": r["color"],
            "createdAt": r["createdAt"],
            "updatedAt": r["updatedAt"],
        })
    return out


def _coerce_users(rows):
    out = []
    for r in rows:
        out.append({
            **r,
            "id": r["id"],
            "name": r["name"],
            "displayName": r["displayName"],
            "email": r["email"],
            "avatarUrl": r["avatarUrl"],
            "active": r["active"].lower() == "true",
            "admin": r["admin"].lower() == "true",
            "teamId": r["teamId"],
            "createdAt": r["createdAt"],
            "updatedAt": r["updatedAt"],
        })
    return out


def _coerce_workflow_states(rows):
    out = []
    for r in rows:
        out.append({
            **r,
            "id": r["id"],
            "name": r["name"],
            "type": r["type"],
            "color": r["color"],
            "position": int(r["position"]),
            "teamId": r["teamId"],
            "description": r["description"],
        })
    return out


def _coerce_labels(rows):
    out = []
    for r in rows:
        out.append({
            **r,
            "id": r["id"],
            "name": r["name"],
            "color": r["color"],
            "description": r["description"],
            "teamId": r["teamId"] if r["teamId"] else None,
            "createdAt": r["createdAt"],
            "updatedAt": r["updatedAt"],
        })
    return out


def _coerce_projects(rows):
    out = []
    for r in rows:
        out.append({
            **r,
            "id": r["id"],
            "name": r["name"],
            "description": r["description"],
            "state": r["state"],
            "leadId": r["leadId"] if r["leadId"] else None,
            "teamIds": [t.strip() for t in r["teamIds"].split(",")] if r["teamIds"] else [],
            "startDate": r["startDate"] if r["startDate"] else None,
            "targetDate": r["targetDate"] if r["targetDate"] else None,
            "createdAt": r["createdAt"],
            "updatedAt": r["updatedAt"],
        })
    return out


def _coerce_cycles(rows):
    out = []
    for r in rows:
        out.append({
            **r,
            "id": r["id"],
            "name": r["name"],
            "number": int(r["number"]),
            "teamId": r["teamId"],
            "startsAt": r["startsAt"],
            "endsAt": r["endsAt"],
            "completedAt": r["completedAt"] if r["completedAt"] else None,
            "createdAt": r["createdAt"],
            "updatedAt": r["updatedAt"],
        })
    return out


def _coerce_issues(rows):
    out = []
    for r in rows:
        out.append({
            **r,
            "id": r["id"],
            "identifier": r["identifier"],
            "number": int(r["number"]),
            "title": r["title"],
            "description": r["description"],
            "priority": int(r["priority"]),
            "estimate": int(r["estimate"]) if r["estimate"] else None,
            "stateId": r["stateId"],
            "assigneeId": r["assigneeId"] if r["assigneeId"] else None,
            "teamId": r["teamId"],
            "projectId": r["projectId"] if r["projectId"] else None,
            "cycleId": r["cycleId"] if r["cycleId"] else None,
            "labelIds": [l.strip() for l in r["labelIds"].split(",")] if r["labelIds"] else [],
            "dueDate": r["dueDate"] if r["dueDate"] else None,
            "sortOrder": float(r["sortOrder"]),
            "branchName": r["branchName"] if r["branchName"] else None,
            "createdAt": r["createdAt"],
            "updatedAt": r["updatedAt"],
            "startedAt": r["startedAt"] if r["startedAt"] else None,
            "completedAt": r["completedAt"] if r["completedAt"] else None,
            "canceledAt": r["canceledAt"] if r["canceledAt"] else None,
        })
    return out


def _coerce_comments(rows):
    out = []
    for r in rows:
        out.append({
            **r,
            "id": r["id"],
            "body": r["body"],
            "issueId": r["issueId"],
            "userId": r["userId"],
            "createdAt": r["createdAt"],
            "updatedAt": r["updatedAt"],
        })
    return out


# Load all data at module init
_teams = _coerce_teams(_load("teams.csv"))
_users = _coerce_users(_load("users.csv"))
_workflow_states = _coerce_workflow_states(_load("workflow_states.csv"))
_labels = _coerce_labels(_load("labels.csv"))
_projects = _coerce_projects(_load("projects.csv"))
_cycles = _coerce_cycles(_load("cycles.csv"))
_issues = _coerce_issues(_load("issues.csv"))
_comments = _coerce_comments(_load("comments.csv"))

with open(DATA_DIR / "workspace.json", encoding="utf-8") as _f:
    _workspace = json.load(_f)

# Mutable in-memory stores
_teams_store = deepcopy(_teams)
_users_store = deepcopy(_users)
_workflow_states_store = deepcopy(_workflow_states)
_labels_store = deepcopy(_labels)
_projects_store = deepcopy(_projects)
_cycles_store = deepcopy(_cycles)
_issues_store = deepcopy(_issues)
_comments_store = deepcopy(_comments)
_workspace_store = deepcopy(_workspace)

_next_issue_number = max(i["number"] for i in _issues_store) + 1
_next_comment_id = len(_comments_store) + 1


def _generate_id(prefix):
    """Generate a simple unique ID."""
    import uuid
    return f"{prefix}-{uuid.uuid4().hex[:8]}"


# ---------------------------------------------------------------------------
# Teams
# ---------------------------------------------------------------------------

def list_teams(limit: int = 50, offset: int = 0):
    results = list(_teams_store)
    total = len(results)
    page = results[offset: offset + limit]
    return {
        "type": "teams",
        "count": len(page),
        "total": total,
        "offset": offset,
        "limit": limit,
        "results": page,
    }


def get_team(team_id: str):
    for t in _teams_store:
        if t["id"] == team_id:
            return {"type": "team", "team": t}
    return {"error": f"Team {team_id} not found"}


def get_team_members(team_id: str):
    team = next((t for t in _teams_store if t["id"] == team_id), None)
    if not team:
        return {"error": f"Team {team_id} not found"}
    members = [u for u in _users_store if u["teamId"] == team_id]
    return {"type": "users", "count": len(members), "results": members}


def get_team_issues(team_id: str, limit: int = 50, offset: int = 0):
    team = next((t for t in _teams_store if t["id"] == team_id), None)
    if not team:
        return {"error": f"Team {team_id} not found"}
    issues = [i for i in _issues_store if i["teamId"] == team_id]
    total = len(issues)
    page = issues[offset: offset + limit]
    return {
        "type": "issues",
        "count": len(page),
        "total": total,
        "offset": offset,
        "limit": limit,
        "results": page,
    }


def get_team_projects(team_id: str):
    team = next((t for t in _teams_store if t["id"] == team_id), None)
    if not team:
        return {"error": f"Team {team_id} not found"}
    projects = [p for p in _projects_store if team_id in p["teamIds"]]
    return {"type": "projects", "count": len(projects), "results": projects}


def get_team_cycles(team_id: str):
    team = next((t for t in _teams_store if t["id"] == team_id), None)
    if not team:
        return {"error": f"Team {team_id} not found"}
    cycles = [c for c in _cycles_store if c["teamId"] == team_id]
    return {"type": "cycles", "count": len(cycles), "results": cycles}


def get_team_workflow_states(team_id: str):
    team = next((t for t in _teams_store if t["id"] == team_id), None)
    if not team:
        return {"error": f"Team {team_id} not found"}
    states = [s for s in _workflow_states_store if s["teamId"] == team_id]
    states = sorted(states, key=lambda x: x["position"])
    return {"type": "workflow_states", "count": len(states), "results": states}


def get_team_labels(team_id: str):
    team = next((t for t in _teams_store if t["id"] == team_id), None)
    if not team:
        return {"error": f"Team {team_id} not found"}
    labels = [l for l in _labels_store if l["teamId"] == team_id or l["teamId"] is None]
    return {"type": "labels", "count": len(labels), "results": labels}


# ---------------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------------

def list_users(limit: int = 50, offset: int = 0):
    results = list(_users_store)
    total = len(results)
    page = results[offset: offset + limit]
    return {
        "type": "users",
        "count": len(page),
        "total": total,
        "offset": offset,
        "limit": limit,
        "results": page,
    }


def get_user(user_id: str):
    for u in _users_store:
        if u["id"] == user_id:
            return {"type": "user", "user": u}
    return {"error": f"User {user_id} not found"}


def get_user_assigned_issues(user_id: str, limit: int = 50, offset: int = 0):
    user = next((u for u in _users_store if u["id"] == user_id), None)
    if not user:
        return {"error": f"User {user_id} not found"}
    issues = [i for i in _issues_store if i["assigneeId"] == user_id]
    total = len(issues)
    page = issues[offset: offset + limit]
    return {
        "type": "issues",
        "count": len(page),
        "total": total,
        "offset": offset,
        "limit": limit,
        "results": page,
    }


# ---------------------------------------------------------------------------
# Workflow States
# ---------------------------------------------------------------------------

def list_workflow_states(team_id: str = None, limit: int = 50, offset: int = 0):
    results = list(_workflow_states_store)
    if team_id:
        results = [s for s in results if s["teamId"] == team_id]
    results = sorted(results, key=lambda x: (x["teamId"], x["position"]))
    total = len(results)
    page = results[offset: offset + limit]
    return {
        "type": "workflow_states",
        "count": len(page),
        "total": total,
        "offset": offset,
        "limit": limit,
        "results": page,
    }


def get_workflow_state(state_id: str):
    for s in _workflow_states_store:
        if s["id"] == state_id:
            return {"type": "workflow_state", "workflowState": s}
    return {"error": f"Workflow state {state_id} not found"}


# ---------------------------------------------------------------------------
# Labels
# ---------------------------------------------------------------------------

def list_labels(team_id: str = None, limit: int = 50, offset: int = 0):
    results = list(_labels_store)
    if team_id:
        results = [l for l in results if l["teamId"] == team_id or l["teamId"] is None]
    total = len(results)
    page = results[offset: offset + limit]
    return {
        "type": "labels",
        "count": len(page),
        "total": total,
        "offset": offset,
        "limit": limit,
        "results": page,
    }


def get_label(label_id: str):
    for l in _labels_store:
        if l["id"] == label_id:
            return {"type": "label", "label": l}
    return {"error": f"Label {label_id} not found"}


def create_label(data: dict):
    required = ["name", "color"]
    for f in required:
        if f not in data or data[f] is None:
            return {"error": f"Missing required field: {f}"}

    now = _now()
    label = {
        "id": _generate_id("label"),
        "name": data["name"],
        "color": data["color"],
        "description": data.get("description", ""),
        "teamId": data.get("teamId"),
        "createdAt": now,
        "updatedAt": now,
    }
    _labels_store.append(label)
    return {"type": "label", "label": label}


# ---------------------------------------------------------------------------
# Projects
# ---------------------------------------------------------------------------

def list_projects(limit: int = 50, offset: int = 0):
    results = list(_projects_store)
    total = len(results)
    page = results[offset: offset + limit]
    return {
        "type": "projects",
        "count": len(page),
        "total": total,
        "offset": offset,
        "limit": limit,
        "results": page,
    }


def get_project(project_id: str):
    for p in _projects_store:
        if p["id"] == project_id:
            return {"type": "project", "project": p}
    return {"error": f"Project {project_id} not found"}


def create_project(data: dict):
    required = ["name"]
    for f in required:
        if f not in data or data[f] is None:
            return {"error": f"Missing required field: {f}"}

    now = _now()
    project = {
        "id": _generate_id("proj"),
        "name": data["name"],
        "description": data.get("description", ""),
        "state": data.get("state", "planned"),
        "leadId": data.get("leadId"),
        "teamIds": data.get("teamIds", []),
        "startDate": data.get("startDate"),
        "targetDate": data.get("targetDate"),
        "createdAt": now,
        "updatedAt": now,
    }
    _projects_store.append(project)
    return {"type": "project", "project": project}


def update_project(project_id: str, data: dict):
    for i, project in enumerate(_projects_store):
        if project["id"] == project_id:
            updatable = {"name", "description", "state", "leadId", "teamIds",
                         "startDate", "targetDate"}
            for k, v in data.items():
                if k in updatable:
                    _projects_store[i][k] = v
            _projects_store[i]["updatedAt"] = _now()
            return {"type": "project", "project": _projects_store[i]}
    return {"error": f"Project {project_id} not found"}


def get_project_issues(project_id: str, limit: int = 50, offset: int = 0):
    project = next((p for p in _projects_store if p["id"] == project_id), None)
    if not project:
        return {"error": f"Project {project_id} not found"}
    issues = [i for i in _issues_store if i["projectId"] == project_id]
    total = len(issues)
    page = issues[offset: offset + limit]
    return {
        "type": "issues",
        "count": len(page),
        "total": total,
        "offset": offset,
        "limit": limit,
        "results": page,
    }


# ---------------------------------------------------------------------------
# Cycles
# ---------------------------------------------------------------------------

def list_cycles(team_id: str = None, status: str = None, limit: int = 50, offset: int = 0):
    results = list(_cycles_store)
    if team_id:
        results = [c for c in results if c["teamId"] == team_id]
    if status:
        now_str = _now()
        if status == "current":
            results = [c for c in results if c["startsAt"] <= now_str[:10] and c["endsAt"] >= now_str[:10] and not c["completedAt"]]
        elif status == "past":
            results = [c for c in results if c["completedAt"] is not None]
        elif status == "upcoming":
            results = [c for c in results if c["startsAt"] > now_str[:10]]
    total = len(results)
    page = results[offset: offset + limit]
    return {
        "type": "cycles",
        "count": len(page),
        "total": total,
        "offset": offset,
        "limit": limit,
        "results": page,
    }


def get_cycle(cycle_id: str):
    for c in _cycles_store:
        if c["id"] == cycle_id:
            return {"type": "cycle", "cycle": c}
    return {"error": f"Cycle {cycle_id} not found"}


def create_cycle(data: dict):
    required = ["name", "teamId", "startsAt", "endsAt"]
    for f in required:
        if f not in data or data[f] is None:
            return {"error": f"Missing required field: {f}"}

    now = _now()
    # Determine next cycle number for this team
    team_cycles = [c for c in _cycles_store if c["teamId"] == data["teamId"]]
    next_num = max((c["number"] for c in team_cycles), default=0) + 1

    cycle = {
        "id": _generate_id("cycle"),
        "name": data["name"],
        "number": next_num,
        "teamId": data["teamId"],
        "startsAt": data["startsAt"],
        "endsAt": data["endsAt"],
        "completedAt": None,
        "createdAt": now,
        "updatedAt": now,
    }
    _cycles_store.append(cycle)
    return {"type": "cycle", "cycle": cycle}


def get_cycle_issues(cycle_id: str, limit: int = 50, offset: int = 0):
    cycle = next((c for c in _cycles_store if c["id"] == cycle_id), None)
    if not cycle:
        return {"error": f"Cycle {cycle_id} not found"}
    issues = [i for i in _issues_store if i["cycleId"] == cycle_id]
    total = len(issues)
    page = issues[offset: offset + limit]
    return {
        "type": "issues",
        "count": len(page),
        "total": total,
        "offset": offset,
        "limit": limit,
        "results": page,
    }


# ---------------------------------------------------------------------------
# Issues
# ---------------------------------------------------------------------------

def list_issues(
    state_id: str = None,
    assignee_id: str = None,
    project_id: str = None,
    cycle_id: str = None,
    team_id: str = None,
    priority: int = None,
    label_id: str = None,
    limit: int = 50,
    offset: int = 0,
):
    results = list(_issues_store)

    if state_id:
        results = [i for i in results if i["stateId"] == state_id]
    if assignee_id:
        results = [i for i in results if i["assigneeId"] == assignee_id]
    if project_id:
        results = [i for i in results if i["projectId"] == project_id]
    if cycle_id:
        results = [i for i in results if i["cycleId"] == cycle_id]
    if team_id:
        results = [i for i in results if i["teamId"] == team_id]
    if priority is not None:
        results = [i for i in results if i["priority"] == priority]
    if label_id:
        results = [i for i in results if label_id in i["labelIds"]]

    results = sorted(results, key=lambda x: x["sortOrder"])

    total = len(results)
    page = results[offset: offset + limit]
    return {
        "type": "issues",
        "count": len(page),
        "total": total,
        "offset": offset,
        "limit": limit,
        "results": page,
    }


def get_issue(issue_id: str):
    for i in _issues_store:
        if i["id"] == issue_id:
            return {"type": "issue", "issue": i}
    return {"error": f"Issue {issue_id} not found"}


def create_issue(data: dict):
    global _next_issue_number
    required = ["title", "teamId"]
    for f in required:
        if f not in data or data[f] is None:
            return {"error": f"Missing required field: {f}"}

    now = _now()
    number = _next_issue_number
    identifier = f"MER-{number}"

    # Generate branch name
    branch_name = None
    if data.get("assigneeId"):
        assignee = next((u for u in _users_store if u["id"] == data["assigneeId"]), None)
        if assignee:
            slug = data["title"].lower().replace(" ", "-")[:40]
            branch_name = f"{assignee['name']}/{identifier.lower()}-{slug}"

    # Determine initial stateId
    state_id = data.get("stateId")
    if not state_id:
        # Default to backlog for the team
        team_states = [s for s in _workflow_states_store if s["teamId"] == data["teamId"] and s["type"] == "backlog"]
        if team_states:
            state_id = team_states[0]["id"]

    issue = {
        "id": _generate_id("issue"),
        "identifier": identifier,
        "number": number,
        "title": data["title"],
        "description": data.get("description", ""),
        "priority": data.get("priority", 0),
        "estimate": data.get("estimate"),
        "stateId": state_id,
        "assigneeId": data.get("assigneeId"),
        "teamId": data["teamId"],
        "projectId": data.get("projectId"),
        "cycleId": data.get("cycleId"),
        "labelIds": data.get("labelIds", []),
        "dueDate": data.get("dueDate"),
        "sortOrder": float(number),
        "branchName": branch_name,
        "createdAt": now,
        "updatedAt": now,
        "startedAt": None,
        "completedAt": None,
        "canceledAt": None,
    }
    _issues_store.append(issue)
    _next_issue_number += 1
    return {"type": "issue", "issue": issue}


def update_issue(issue_id: str, data: dict):
    for i, issue in enumerate(_issues_store):
        if issue["id"] == issue_id:
            updatable = {"title", "description", "priority", "estimate", "stateId",
                         "assigneeId", "projectId", "cycleId", "labelIds", "dueDate",
                         "sortOrder"}
            for k, v in data.items():
                if k in updatable:
                    if k == "priority" and v is not None:
                        _issues_store[i][k] = int(v)
                    elif k == "estimate" and v is not None:
                        _issues_store[i][k] = int(v)
                    elif k == "sortOrder" and v is not None:
                        _issues_store[i][k] = float(v)
                    else:
                        _issues_store[i][k] = v

            # Handle state transitions
            if "stateId" in data:
                new_state = next((s for s in _workflow_states_store if s["id"] == data["stateId"]), None)
                if new_state:
                    now = _now()
                    if new_state["type"] == "started" and not _issues_store[i]["startedAt"]:
                        _issues_store[i]["startedAt"] = now
                    elif new_state["type"] == "completed":
                        _issues_store[i]["completedAt"] = now
                        if not _issues_store[i]["startedAt"]:
                            _issues_store[i]["startedAt"] = now
                    elif new_state["type"] == "cancelled":
                        _issues_store[i]["canceledAt"] = now

            _issues_store[i]["updatedAt"] = _now()

            # Update branch name if assignee changed
            if "assigneeId" in data and data["assigneeId"]:
                assignee = next((u for u in _users_store if u["id"] == data["assigneeId"]), None)
                if assignee:
                    slug = _issues_store[i]["title"].lower().replace(" ", "-")[:40]
                    _issues_store[i]["branchName"] = f"{assignee['name']}/{_issues_store[i]['identifier'].lower()}-{slug}"

            return {"type": "issue", "issue": _issues_store[i]}
    return {"error": f"Issue {issue_id} not found"}


def delete_issue(issue_id: str):
    for i, issue in enumerate(_issues_store):
        if issue["id"] == issue_id:
            removed = _issues_store.pop(i)
            return {"type": "issue", "deleted": True, "issueId": issue_id}
    return {"error": f"Issue {issue_id} not found"}


def search_issues(query: str, limit: int = 50, offset: int = 0):
    q = query.lower()
    results = [
        i for i in _issues_store
        if q in i["title"].lower() or q in i["description"].lower() or q in i["identifier"].lower()
    ]
    total = len(results)
    page = results[offset: offset + limit]
    return {
        "type": "issues",
        "count": len(page),
        "total": total,
        "offset": offset,
        "limit": limit,
        "results": page,
    }


# ---------------------------------------------------------------------------
# Comments
# ---------------------------------------------------------------------------

def list_comments(issue_id: str, limit: int = 50, offset: int = 0):
    issue = next((i for i in _issues_store if i["id"] == issue_id), None)
    if not issue:
        return {"error": f"Issue {issue_id} not found"}
    results = [c for c in _comments_store if c["issueId"] == issue_id]
    results = sorted(results, key=lambda x: x["createdAt"])
    total = len(results)
    page = results[offset: offset + limit]
    return {
        "type": "comments",
        "count": len(page),
        "total": total,
        "offset": offset,
        "limit": limit,
        "results": page,
    }


def get_comment(comment_id: str):
    for c in _comments_store:
        if c["id"] == comment_id:
            return {"type": "comment", "comment": c}
    return {"error": f"Comment {comment_id} not found"}


def create_comment(data: dict):
    global _next_comment_id
    required = ["body", "issueId"]
    for f in required:
        if f not in data or data[f] is None:
            return {"error": f"Missing required field: {f}"}

    # Verify issue exists
    issue = next((i for i in _issues_store if i["id"] == data["issueId"]), None)
    if not issue:
        return {"error": f"Issue {data['issueId']} not found"}

    now = _now()
    comment = {
        "id": f"comment-{_next_comment_id:02d}",
        "body": data["body"],
        "issueId": data["issueId"],
        "userId": data.get("userId", "user-01"),
        "createdAt": now,
        "updatedAt": now,
    }
    _comments_store.append(comment)
    _next_comment_id += 1
    return {"type": "comment", "comment": comment}


def update_comment(comment_id: str, data: dict):
    for i, comment in enumerate(_comments_store):
        if comment["id"] == comment_id:
            if "body" in data:
                _comments_store[i]["body"] = data["body"]
            _comments_store[i]["updatedAt"] = _now()
            return {"type": "comment", "comment": _comments_store[i]}
    return {"error": f"Comment {comment_id} not found"}


def delete_comment(comment_id: str):
    for i, comment in enumerate(_comments_store):
        if comment["id"] == comment_id:
            _comments_store.pop(i)
            return {"type": "comment", "deleted": True, "commentId": comment_id}
    return {"error": f"Comment {comment_id} not found"}
