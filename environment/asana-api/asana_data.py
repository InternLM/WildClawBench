"""Data access module for the Asana API mock service."""

import csv
import json
import uuid
from copy import deepcopy
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).parent


def _load(filename):
    with open(DATA_DIR / filename, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _now():
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000Z")


def _to_bool(v):
    return str(v).strip().lower() == "true"


# ---------------------------------------------------------------------------
# Load + coerce
# ---------------------------------------------------------------------------

def _coerce_users(rows):
    return [dict(r) for r in rows]


def _coerce_projects(rows):
    out = []
    for r in rows:
        out.append({
            **r,
            "archived": _to_bool(r["archived"]),
        })
    return out


def _coerce_sections(rows):
    return [dict(r) for r in rows]


def _coerce_tasks(rows):
    out = []
    for r in rows:
        out.append({
            **r,
            "completed": _to_bool(r["completed"]),
            "assignee_gid": r["assignee_gid"] or None,
            "due_on": r["due_on"] or None,
            "section_gid": r["section_gid"] or None,
        })
    return out


_users = _coerce_users(_load("users.csv"))
_projects = _coerce_projects(_load("projects.csv"))
_sections = _coerce_sections(_load("sections.csv"))
_tasks = _coerce_tasks(_load("tasks.csv"))

with open(DATA_DIR / "workspace.json", encoding="utf-8") as _f:
    _workspace = json.load(_f)

_users_store = deepcopy(_users)
_projects_store = deepcopy(_projects)
_sections_store = deepcopy(_sections)
_tasks_store = deepcopy(_tasks)
_workspace_store = deepcopy(_workspace)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _new_gid():
    return str(uuid.uuid4().int)[:16]


def _user_compact(gid):
    if not gid:
        return None
    for u in _users_store:
        if u["gid"] == gid:
            return {"gid": u["gid"], "resource_type": "user", "name": u["name"]}
    return {"gid": gid, "resource_type": "user"}


def _project_compact(gid):
    if not gid:
        return None
    for p in _projects_store:
        if p["gid"] == gid:
            return {"gid": p["gid"], "resource_type": "project", "name": p["name"]}
    return {"gid": gid, "resource_type": "project"}


def _section_compact(gid):
    if not gid:
        return None
    for s in _sections_store:
        if s["gid"] == gid:
            return {"gid": s["gid"], "resource_type": "section", "name": s["name"]}
    return {"gid": gid, "resource_type": "section"}


def _task_view(t):
    return {
        "gid": t["gid"],
        "resource_type": "task",
        "name": t["name"],
        "completed": t["completed"],
        "due_on": t["due_on"],
        "notes": t["notes"],
        "created_at": t["created_at"],
        "modified_at": t["modified_at"],
        "assignee": _user_compact(t["assignee_gid"]),
        "memberships": [{
            "project": _project_compact(t["project_gid"]),
            "section": _section_compact(t["section_gid"]),
        }],
    }


# ---------------------------------------------------------------------------
# Workspaces
# ---------------------------------------------------------------------------

def list_workspaces():
    ws = _workspace_store
    return {"data": [{
        "gid": ws["gid"],
        "resource_type": "workspace",
        "name": ws["name"],
    }]}


# ---------------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------------

def list_users(workspace_gid=None):
    rows = _users_store
    if workspace_gid:
        rows = [u for u in rows if u["workspace_gid"] == workspace_gid]
    return {"data": [{
        "gid": u["gid"], "resource_type": "user", "name": u["name"], "email": u["email"],
    } for u in rows]}


# ---------------------------------------------------------------------------
# Projects
# ---------------------------------------------------------------------------

def list_projects(workspace_gid=None, archived=None):
    rows = list(_projects_store)
    if workspace_gid:
        rows = [p for p in rows if p["workspace_gid"] == workspace_gid]
    if archived is not None:
        rows = [p for p in rows if p["archived"] == archived]
    return {"data": [{
        "gid": p["gid"], "resource_type": "project", "name": p["name"],
        "owner": _user_compact(p["owner_gid"]), "color": p["color"],
        "archived": p["archived"], "notes": p["notes"], "created_at": p["created_at"],
    } for p in rows]}


def get_project(project_gid):
    for p in _projects_store:
        if p["gid"] == project_gid:
            return {"data": {
                "gid": p["gid"], "resource_type": "project", "name": p["name"],
                "owner": _user_compact(p["owner_gid"]), "color": p["color"],
                "archived": p["archived"], "notes": p["notes"], "created_at": p["created_at"],
            }}
    return {"error": f"Project {project_gid} not found"}


def list_project_sections(project_gid):
    if not any(p["gid"] == project_gid for p in _projects_store):
        return {"error": f"Project {project_gid} not found"}
    rows = [s for s in _sections_store if s["project_gid"] == project_gid]
    return {"data": [{
        "gid": s["gid"], "resource_type": "section", "name": s["name"],
        "project": _project_compact(project_gid), "created_at": s["created_at"],
    } for s in rows]}


def list_project_tasks(project_gid, completed_since=None):
    if not any(p["gid"] == project_gid for p in _projects_store):
        return {"error": f"Project {project_gid} not found"}
    rows = [t for t in _tasks_store if t["project_gid"] == project_gid]
    return {"data": [_task_view(t) for t in rows]}


# ---------------------------------------------------------------------------
# Tasks
# ---------------------------------------------------------------------------

def list_tasks(project_gid=None, assignee_gid=None, completed=None):
    rows = list(_tasks_store)
    if project_gid:
        rows = [t for t in rows if t["project_gid"] == project_gid]
    if assignee_gid:
        rows = [t for t in rows if t["assignee_gid"] == assignee_gid]
    if completed is not None:
        rows = [t for t in rows if t["completed"] == completed]
    return {"data": [_task_view(t) for t in rows]}


def get_task(task_gid):
    for t in _tasks_store:
        if t["gid"] == task_gid:
            return {"data": _task_view(t)}
    return {"error": f"Task {task_gid} not found"}


def create_task(name, project_gid=None, section_gid=None, assignee_gid=None,
                due_on=None, notes="", completed=False):
    if project_gid and not any(p["gid"] == project_gid for p in _projects_store):
        return {"error": f"Project {project_gid} not found"}
    now = _now()
    task = {
        "gid": _new_gid(),
        "name": name,
        "project_gid": project_gid or "",
        "section_gid": section_gid,
        "assignee_gid": assignee_gid,
        "completed": bool(completed),
        "due_on": due_on,
        "notes": notes or "",
        "created_at": now,
        "modified_at": now,
    }
    _tasks_store.append(task)
    return {"data": _task_view(task)}


def update_task(task_gid, name=None, completed=None, assignee_gid=None,
                due_on=None, section_gid=None, notes=None):
    for i, t in enumerate(_tasks_store):
        if t["gid"] == task_gid:
            if name is not None:
                _tasks_store[i]["name"] = name
            if completed is not None:
                _tasks_store[i]["completed"] = bool(completed)
            if assignee_gid is not None:
                _tasks_store[i]["assignee_gid"] = assignee_gid or None
            if due_on is not None:
                _tasks_store[i]["due_on"] = due_on or None
            if section_gid is not None:
                _tasks_store[i]["section_gid"] = section_gid or None
            if notes is not None:
                _tasks_store[i]["notes"] = notes
            _tasks_store[i]["modified_at"] = _now()
            return {"data": _task_view(_tasks_store[i])}
    return {"error": f"Task {task_gid} not found"}
