"""Data access module for Linear API simulation."""

import csv
import json
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).parent

import sys as _sys
_sys.path.insert(0, str(DATA_DIR.parent))
from _mutable_store import (
    read_seed_with_ctx, # noqa: E402
    get_store,
    strict_int,
    strict_float,
    strict_bool,
    strict_str,
    opt_int,
    opt_float,
    opt_str,
    opt_csv_list,
)

_store = get_store("linear-api")
_API = "linear-api"



def _store_patch(_table, _row_or_pk, _updates):
    """Persist field updates to a stored row (was: in-place mutation of a copy)."""
    _t = _store.table(_table)
    _pk = _row_or_pk.get(_t.primary_key, _row_or_pk.get("id")) if isinstance(_row_or_pk, dict) else _row_or_pk
    return _t.patch(_pk, _updates)


def _store_delete(_table, _row_or_pk):
    """Persist a row deletion (was: pop/remove on a copy)."""
    _t = _store.table(_table)
    _pk = _row_or_pk.get(_t.primary_key, _row_or_pk.get("id")) if isinstance(_row_or_pk, dict) else _row_or_pk
    return _t.delete(_pk)

def _store_insert(_table, _row):
    """Persist a newly-created row into the shared store (drift/injection-safe).

    Synthesizes the table's registered primary key from the row's ``id`` field
    when the row doesn't already carry it, so creates work regardless of whether
    the table was registered with primary_key="id" or a domain-specific key.
    """
    _t = _store.table(_table)
    if _t.primary_key not in _row and "id" in _row:
        _row = {**_row, _t.primary_key: _row["id"]}
    return _t.upsert(_row)

_store.register("teams", primary_key="id",
                initial_loader=lambda: _coerce_teams(_load("teams.json", "teams")))
_store.register("users", primary_key="id",
                initial_loader=lambda: _coerce_users(_load("users.json", "users")))
_store.register("workflow_states", primary_key="id",
                initial_loader=lambda: _coerce_workflow_states(_load("workflow_states.json", "workflow_states")))
_store.register("labels", primary_key="id",
                initial_loader=lambda: _coerce_labels(_load("labels.json", "labels")))
_store.register("projects", primary_key="id",
                initial_loader=lambda: _coerce_projects(_load("projects.json", "projects")))
_store.register("cycles", primary_key="id",
                initial_loader=lambda: _coerce_cycles(_load("cycles.json", "cycles")))
_store.register("issues", primary_key="id",
                initial_loader=lambda: _coerce_issues(_load("issues.json", "issues")))
_store.register("comments", primary_key="id",
                initial_loader=lambda: _coerce_comments(_load("comments.json", "comments")))
_store.register_document("workspace", initial_loader=lambda: __import__('json').load(open(DATA_DIR / "workspace.json", encoding="utf-8")))


def _teams_rows():
    return _store.table("teams").rows()


def _users_rows():
    return _store.table("users").rows()


def _workflow_states_rows():
    return _store.table("workflow_states").rows()


def _labels_rows():
    return _store.table("labels").rows()


def _projects_rows():
    return _store.table("projects").rows()


def _cycles_rows():
    return _store.table("cycles").rows()


def _issues_rows():
    return _store.table("issues").rows()


def _comments_rows():
    return _store.table("comments").rows()


def _workspace_doc():
    return _store.document("workspace").get()



def _load(filename, table):
    return read_seed_with_ctx(DATA_DIR / filename, _API, table)


def _strip_ctx(r):
    return {k: v for k, v in r.items() if not k.startswith("__")}


def _now():
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")


# ---------------------------------------------------------------------------
# Load and coerce data
# ---------------------------------------------------------------------------

def _coerce_teams(rows):
    out = []
    for r in rows:
        out.append({
            **_strip_ctx(r),
            "id": strict_str(r, "id"),
            "name": strict_str(r, "name"),
            "key": strict_str(r, "key"),
            "description": strict_str(r, "description"),
            "color": strict_str(r, "color"),
            "createdAt": strict_str(r, "createdAt"),
            "updatedAt": strict_str(r, "updatedAt"),
        })
    return out


def _coerce_users(rows):
    out = []
    for r in rows:
        out.append({
            **_strip_ctx(r),
            "id": strict_str(r, "id"),
            "name": strict_str(r, "name"),
            "displayName": strict_str(r, "displayName"),
            "email": strict_str(r, "email"),
            "avatarUrl": strict_str(r, "avatarUrl"),
            "active": strict_bool(r, "active"),
            "admin": strict_bool(r, "admin"),
            "teamId": strict_str(r, "teamId"),
            "createdAt": strict_str(r, "createdAt"),
            "updatedAt": strict_str(r, "updatedAt"),
        })
    return out


def _coerce_workflow_states(rows):
    out = []
    for r in rows:
        out.append({
            **_strip_ctx(r),
            "id": strict_str(r, "id"),
            "name": strict_str(r, "name"),
            "type": strict_str(r, "type"),
            "color": strict_str(r, "color"),
            "position": strict_int(r, "position"),
            "teamId": strict_str(r, "teamId"),
            "description": strict_str(r, "description"),
        })
    return out


def _coerce_labels(rows):
    out = []
    for r in rows:
        out.append({
            **_strip_ctx(r),
            "id": strict_str(r, "id"),
            "name": strict_str(r, "name"),
            "color": strict_str(r, "color"),
            "description": strict_str(r, "description"),
            "teamId": opt_str(r, "teamId", default="") or None,
            "createdAt": strict_str(r, "createdAt"),
            "updatedAt": strict_str(r, "updatedAt"),
        })
    return out


def _coerce_projects(rows):
    out = []
    for r in rows:
        out.append({
            **_strip_ctx(r),
            "id": strict_str(r, "id"),
            "name": strict_str(r, "name"),
            "description": strict_str(r, "description"),
            "state": strict_str(r, "state"),
            "leadId": opt_str(r, "leadId", default="") or None,
            "teamIds": [t.strip() for t in opt_csv_list(r, "teamIds")],
            "startDate": opt_str(r, "startDate", default="") or None,
            "targetDate": opt_str(r, "targetDate", default="") or None,
            "createdAt": strict_str(r, "createdAt"),
            "updatedAt": strict_str(r, "updatedAt"),
        })
    return out


def _coerce_cycles(rows):
    out = []
    for r in rows:
        out.append({
            **_strip_ctx(r),
            "id": strict_str(r, "id"),
            "name": strict_str(r, "name"),
            "number": strict_int(r, "number"),
            "teamId": strict_str(r, "teamId"),
            "startsAt": strict_str(r, "startsAt"),
            "endsAt": strict_str(r, "endsAt"),
            "completedAt": opt_str(r, "completedAt", default="") or None,
            "createdAt": strict_str(r, "createdAt"),
            "updatedAt": strict_str(r, "updatedAt"),
        })
    return out


def _coerce_issues(rows):
    out = []
    for r in rows:
        out.append({
            **_strip_ctx(r),
            "id": strict_str(r, "id"),
            "identifier": strict_str(r, "identifier"),
            "number": strict_int(r, "number"),
            "title": strict_str(r, "title"),
            "description": strict_str(r, "description"),
            "priority": strict_int(r, "priority"),
            "estimate": opt_int(r, "estimate"),
            "stateId": strict_str(r, "stateId"),
            "assigneeId": opt_str(r, "assigneeId", default="") or None,
            "teamId": strict_str(r, "teamId"),
            "projectId": opt_str(r, "projectId", default="") or None,
            "cycleId": opt_str(r, "cycleId", default="") or None,
            "labelIds": [l.strip() for l in opt_csv_list(r, "labelIds")],
            "dueDate": opt_str(r, "dueDate", default="") or None,
            "sortOrder": opt_float(r, "sortOrder", default=0.0),
            "branchName": opt_str(r, "branchName", default="") or None,
            "createdAt": strict_str(r, "createdAt"),
            "updatedAt": strict_str(r, "updatedAt"),
            "startedAt": opt_str(r, "startedAt", default="") or None,
            "completedAt": opt_str(r, "completedAt", default="") or None,
            "canceledAt": opt_str(r, "canceledAt", default="") or None,
        })
    return out


def _coerce_comments(rows):
    out = []
    for r in rows:
        out.append({
            **_strip_ctx(r),
            "id": strict_str(r, "id"),
            "body": strict_str(r, "body"),
            "issueId": strict_str(r, "issueId"),
            "userId": strict_str(r, "userId"),
            "createdAt": strict_str(r, "createdAt"),
            "updatedAt": strict_str(r, "updatedAt"),
        })
    return out


# Load all data at module init









# Mutable in-memory stores









_store.eager_load()

_next_issue_number = max(i["number"] for i in _issues_rows()) + 1
_next_comment_id = len(_comments_rows()) + 1


def _generate_id(prefix):
    """Generate a simple unique ID."""
    import uuid
    return f"{prefix}-{uuid.uuid4().hex[:8]}"


# ---------------------------------------------------------------------------
# Teams
# ---------------------------------------------------------------------------

def list_teams(limit: int = 50, offset: int = 0):
    results = list(_teams_rows())
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
    for t in _teams_rows():
        if t["id"] == team_id:
            return {"type": "team", "team": t}
    return {"error": f"Team {team_id} not found"}


def get_team_members(team_id: str):
    team = next((t for t in _teams_rows() if t["id"] == team_id), None)
    if not team:
        return {"error": f"Team {team_id} not found"}
    members = [u for u in _users_rows() if u["teamId"] == team_id]
    return {"type": "users", "count": len(members), "results": members}


def get_team_issues(team_id: str, limit: int = 50, offset: int = 0):
    team = next((t for t in _teams_rows() if t["id"] == team_id), None)
    if not team:
        return {"error": f"Team {team_id} not found"}
    issues = [i for i in _issues_rows() if i["teamId"] == team_id]
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
    team = next((t for t in _teams_rows() if t["id"] == team_id), None)
    if not team:
        return {"error": f"Team {team_id} not found"}
    projects = [p for p in _projects_rows() if team_id in p["teamIds"]]
    return {"type": "projects", "count": len(projects), "results": projects}


def get_team_cycles(team_id: str):
    team = next((t for t in _teams_rows() if t["id"] == team_id), None)
    if not team:
        return {"error": f"Team {team_id} not found"}
    cycles = [c for c in _cycles_rows() if c["teamId"] == team_id]
    return {"type": "cycles", "count": len(cycles), "results": cycles}


def get_team_workflow_states(team_id: str):
    team = next((t for t in _teams_rows() if t["id"] == team_id), None)
    if not team:
        return {"error": f"Team {team_id} not found"}
    states = [s for s in _workflow_states_rows() if s["teamId"] == team_id]
    states = sorted(states, key=lambda x: x["position"])
    return {"type": "workflow_states", "count": len(states), "results": states}


def get_team_labels(team_id: str):
    team = next((t for t in _teams_rows() if t["id"] == team_id), None)
    if not team:
        return {"error": f"Team {team_id} not found"}
    labels = [l for l in _labels_rows() if l["teamId"] == team_id or l["teamId"] is None]
    return {"type": "labels", "count": len(labels), "results": labels}


# ---------------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------------

def list_users(limit: int = 50, offset: int = 0):
    results = list(_users_rows())
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
    for u in _users_rows():
        if u["id"] == user_id:
            return {"type": "user", "user": u}
    return {"error": f"User {user_id} not found"}


def get_user_assigned_issues(user_id: str, limit: int = 50, offset: int = 0):
    user = next((u for u in _users_rows() if u["id"] == user_id), None)
    if not user:
        return {"error": f"User {user_id} not found"}
    issues = [i for i in _issues_rows() if i["assigneeId"] == user_id]
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
    results = list(_workflow_states_rows())
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
    for s in _workflow_states_rows():
        if s["id"] == state_id:
            return {"type": "workflow_state", "workflowState": s}
    return {"error": f"Workflow state {state_id} not found"}


# ---------------------------------------------------------------------------
# Labels
# ---------------------------------------------------------------------------

def list_labels(team_id: str = None, limit: int = 50, offset: int = 0):
    results = list(_labels_rows())
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
    for l in _labels_rows():
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
    _store_insert("labels", label)
    return {"type": "label", "label": label}


# ---------------------------------------------------------------------------
# Projects
# ---------------------------------------------------------------------------

def list_projects(limit: int = 50, offset: int = 0):
    results = list(_projects_rows())
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
    for p in _projects_rows():
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
    _store_insert("projects", project)
    return {"type": "project", "project": project}


def update_project(project_id: str, data: dict):
    for project in _projects_rows():
        if project["id"] == project_id:
            updatable = {"name", "description", "state", "leadId", "teamIds",
                         "startDate", "targetDate"}
            _changes = {}
            for k, v in data.items():
                if k in updatable:
                    _changes[k] = v
            _changes["updatedAt"] = _now()
            project.update(_changes)
            _store_patch("projects", project, _changes)
            return {"type": "project", "project": project}
    return {"error": f"Project {project_id} not found"}


def get_project_issues(project_id: str, limit: int = 50, offset: int = 0):
    project = next((p for p in _projects_rows() if p["id"] == project_id), None)
    if not project:
        return {"error": f"Project {project_id} not found"}
    issues = [i for i in _issues_rows() if i["projectId"] == project_id]
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
    results = list(_cycles_rows())
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
    for c in _cycles_rows():
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
    team_cycles = [c for c in _cycles_rows() if c["teamId"] == data["teamId"]]
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
    _store_insert("cycles", cycle)
    return {"type": "cycle", "cycle": cycle}


def get_cycle_issues(cycle_id: str, limit: int = 50, offset: int = 0):
    cycle = next((c for c in _cycles_rows() if c["id"] == cycle_id), None)
    if not cycle:
        return {"error": f"Cycle {cycle_id} not found"}
    issues = [i for i in _issues_rows() if i["cycleId"] == cycle_id]
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
    results = list(_issues_rows())

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
    for i in _issues_rows():
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
        assignee = next((u for u in _users_rows() if u["id"] == data["assigneeId"]), None)
        if assignee:
            slug = data["title"].lower().replace(" ", "-")[:40]
            branch_name = f"{assignee['name']}/{identifier.lower()}-{slug}"

    # Determine initial stateId
    state_id = data.get("stateId")
    if not state_id:
        # Default to backlog for the team
        team_states = [s for s in _workflow_states_rows() if s["teamId"] == data["teamId"] and s["type"] == "backlog"]
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
    _store_insert("issues", issue)
    _next_issue_number += 1
    return {"type": "issue", "issue": issue}


def update_issue(issue_id: str, data: dict):
    for issue in _issues_rows():
        if issue["id"] == issue_id:
            _changes = {}
            updatable = {"title", "description", "priority", "estimate", "stateId",
                         "assigneeId", "projectId", "cycleId", "labelIds", "dueDate",
                         "sortOrder"}
            for k, v in data.items():
                if k in updatable:
                    if k == "priority" and v is not None:
                        _changes[k] = int(v)
                    elif k == "estimate" and v is not None:
                        _changes[k] = int(v)
                    elif k == "sortOrder" and v is not None:
                        _changes[k] = float(v)
                    else:
                        _changes[k] = v
            issue.update(_changes)

            # Handle state transitions
            if "stateId" in data:
                new_state = next((s for s in _workflow_states_rows() if s["id"] == data["stateId"]), None)
                if new_state:
                    now = _now()
                    if new_state["type"] == "started" and not issue["startedAt"]:
                        _changes["startedAt"] = now
                    elif new_state["type"] == "completed":
                        _changes["completedAt"] = now
                        if not issue["startedAt"]:
                            _changes["startedAt"] = now
                    elif new_state["type"] == "cancelled":
                        _changes["canceledAt"] = now
                    issue.update(_changes)

            _changes["updatedAt"] = _now()
            issue.update(_changes)

            # Update branch name if assignee changed
            if "assigneeId" in data and data["assigneeId"]:
                assignee = next((u for u in _users_rows() if u["id"] == data["assigneeId"]), None)
                if assignee:
                    slug = issue["title"].lower().replace(" ", "-")[:40]
                    _changes["branchName"] = f"{assignee['name']}/{issue['identifier'].lower()}-{slug}"
                    issue.update(_changes)

            _store_patch("issues", issue, _changes)
            return {"type": "issue", "issue": issue}
    return {"error": f"Issue {issue_id} not found"}


def delete_issue(issue_id: str):
    for issue in _issues_rows():
        if issue["id"] == issue_id:
            removed = issue
            _store_delete("issues", issue)
            return {"type": "issue", "deleted": True, "issueId": issue_id}
    return {"error": f"Issue {issue_id} not found"}


def search_issues(query: str, limit: int = 50, offset: int = 0):
    q = query.lower()
    results = [
        i for i in _issues_rows()
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
    issue = next((i for i in _issues_rows() if i["id"] == issue_id), None)
    if not issue:
        return {"error": f"Issue {issue_id} not found"}
    results = [c for c in _comments_rows() if c["issueId"] == issue_id]
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
    for c in _comments_rows():
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
    issue = next((i for i in _issues_rows() if i["id"] == data["issueId"]), None)
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
    _store_insert("comments", comment)
    _next_comment_id += 1
    return {"type": "comment", "comment": comment}


def update_comment(comment_id: str, data: dict):
    for comment in _comments_rows():
        if comment["id"] == comment_id:
            _changes = {}
            if "body" in data:
                _changes["body"] = data["body"]
            _changes["updatedAt"] = _now()
            comment.update(_changes)
            _store_patch("comments", comment, _changes)
            return {"type": "comment", "comment": comment}
    return {"error": f"Comment {comment_id} not found"}


def delete_comment(comment_id: str):
    for comment in _comments_rows():
        if comment["id"] == comment_id:
            _store_delete("comments", comment)
            return {"type": "comment", "deleted": True, "commentId": comment_id}
    return {"error": f"Comment {comment_id} not found"}
