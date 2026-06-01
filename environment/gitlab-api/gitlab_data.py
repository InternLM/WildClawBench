"""Data access module for the GitLab API mock service."""

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

def _coerce_projects(rows):
    out = []
    for r in rows:
        out.append({
            **r,
            "id": int(r["id"]),
            "star_count": int(r["star_count"]),
            "forks_count": int(r["forks_count"]),
            "open_issues_count": int(r["open_issues_count"]),
        })
    return out


def _coerce_issues(rows):
    out = []
    for r in rows:
        out.append({
            **r,
            "id": int(r["id"]),
            "iid": int(r["iid"]),
            "project_id": int(r["project_id"]),
            "labels": [l for l in r["labels"].split(";") if l],
            "closed_at": r["closed_at"] or None,
        })
    return out


def _coerce_merge_requests(rows):
    out = []
    for r in rows:
        out.append({
            **r,
            "id": int(r["id"]),
            "iid": int(r["iid"]),
            "project_id": int(r["project_id"]),
            "draft": _to_bool(r["draft"]),
            "merged_at": r["merged_at"] or None,
        })
    return out


def _coerce_pipelines(rows):
    out = []
    for r in rows:
        out.append({
            **r,
            "id": int(r["id"]),
            "project_id": int(r["project_id"]),
            "duration": int(r["duration"]),
        })
    return out


def _coerce_users(rows):
    out = []
    for r in rows:
        out.append({
            **r,
            "id": int(r["id"]),
            "is_admin": _to_bool(r["is_admin"]),
        })
    return out


_projects = _coerce_projects(_load("projects.csv"))
_issues = _coerce_issues(_load("issues.csv"))
_merge_requests = _coerce_merge_requests(_load("merge_requests.csv"))
_pipelines = _coerce_pipelines(_load("pipelines.csv"))
_users = _coerce_users(_load("users.csv"))

with open(DATA_DIR / "current_user.json", encoding="utf-8") as _f:
    _current_user = json.load(_f)

_projects_store = deepcopy(_projects)
_issues_store = deepcopy(_issues)
_merge_requests_store = deepcopy(_merge_requests)
_pipelines_store = deepcopy(_pipelines)
_users_store = deepcopy(_users)
_current_user_store = deepcopy(_current_user)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _find_project(project_id):
    try:
        pid = int(project_id)
    except (TypeError, ValueError):
        return None
    return next((p for p in _projects_store if p["id"] == pid), None)


def _new_numeric_id(store):
    return max((row["id"] for row in store), default=0) + 1


# ---------------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------------

def get_current_user():
    return _current_user_store


def list_users():
    return list(_users_store)


# ---------------------------------------------------------------------------
# Projects
# ---------------------------------------------------------------------------

def list_projects(visibility=None):
    results = list(_projects_store)
    if visibility:
        results = [p for p in results if p["visibility"] == visibility]
    return results


def get_project(project_id):
    project = _find_project(project_id)
    if not project:
        return {"error": f"Project {project_id} not found"}
    return project


# ---------------------------------------------------------------------------
# Issues
# ---------------------------------------------------------------------------

def list_issues(project_id, state=None, labels=None):
    project = _find_project(project_id)
    if not project:
        return {"error": f"Project {project_id} not found"}
    results = [i for i in _issues_store if i["project_id"] == project["id"]]
    if state and state != "all":
        results = [i for i in results if i["state"] == state]
    if labels:
        wanted = {l.strip().lower() for l in labels.split(",")}
        results = [i for i in results if {l.lower() for l in i["labels"]} & wanted]
    results.sort(key=lambda i: i["updated_at"], reverse=True)
    return results


def get_issue(project_id, issue_iid):
    project = _find_project(project_id)
    if not project:
        return {"error": f"Project {project_id} not found"}
    for i in _issues_store:
        if i["project_id"] == project["id"] and i["iid"] == int(issue_iid):
            return i
    return {"error": f"Issue {issue_iid} not found in project {project_id}"}


def create_issue(project_id, title, description="", assignee=None, labels=None):
    project = _find_project(project_id)
    if not project:
        return {"error": f"Project {project_id} not found"}
    next_iid = max((i["iid"] for i in _issues_store if i["project_id"] == project["id"]), default=0) + 1
    issue = {
        "id": _new_numeric_id(_issues_store),
        "iid": next_iid,
        "project_id": project["id"],
        "title": title,
        "description": description or "",
        "state": "opened",
        "author": _current_user_store["username"],
        "assignee": assignee or "",
        "labels": labels or [],
        "created_at": _now(),
        "updated_at": _now(),
        "closed_at": None,
    }
    _issues_store.append(issue)
    project["open_issues_count"] += 1
    return issue


def update_issue(project_id, issue_iid, title=None, description=None,
                 state_event=None, assignee=None, labels=None):
    project = _find_project(project_id)
    if not project:
        return {"error": f"Project {project_id} not found"}
    for idx, i in enumerate(_issues_store):
        if i["project_id"] == project["id"] and i["iid"] == int(issue_iid):
            if title is not None:
                _issues_store[idx]["title"] = title
            if description is not None:
                _issues_store[idx]["description"] = description
            if assignee is not None:
                _issues_store[idx]["assignee"] = assignee
            if labels is not None:
                _issues_store[idx]["labels"] = labels
            if state_event == "close" and i["state"] != "closed":
                _issues_store[idx]["state"] = "closed"
                _issues_store[idx]["closed_at"] = _now()
                project["open_issues_count"] = max(0, project["open_issues_count"] - 1)
            elif state_event == "reopen" and i["state"] != "opened":
                _issues_store[idx]["state"] = "opened"
                _issues_store[idx]["closed_at"] = None
                project["open_issues_count"] += 1
            _issues_store[idx]["updated_at"] = _now()
            return _issues_store[idx]
    return {"error": f"Issue {issue_iid} not found in project {project_id}"}


# ---------------------------------------------------------------------------
# Merge requests
# ---------------------------------------------------------------------------

def list_merge_requests(project_id, state=None):
    project = _find_project(project_id)
    if not project:
        return {"error": f"Project {project_id} not found"}
    results = [m for m in _merge_requests_store if m["project_id"] == project["id"]]
    if state and state != "all":
        results = [m for m in results if m["state"] == state]
    results.sort(key=lambda m: m["updated_at"], reverse=True)
    return results


def create_merge_request(project_id, title, source_branch, target_branch="main",
                         description="", assignee=None):
    project = _find_project(project_id)
    if not project:
        return {"error": f"Project {project_id} not found"}
    next_iid = max((m["iid"] for m in _merge_requests_store if m["project_id"] == project["id"]), default=0) + 1
    mr = {
        "id": _new_numeric_id(_merge_requests_store),
        "iid": next_iid,
        "project_id": project["id"],
        "title": title,
        "description": description or "",
        "state": "opened",
        "source_branch": source_branch,
        "target_branch": target_branch,
        "author": _current_user_store["username"],
        "assignee": assignee or "",
        "merge_status": "can_be_merged",
        "draft": False,
        "created_at": _now(),
        "updated_at": _now(),
        "merged_at": None,
    }
    _merge_requests_store.append(mr)
    return mr


def merge_merge_request(project_id, mr_iid):
    project = _find_project(project_id)
    if not project:
        return {"error": f"Project {project_id} not found"}
    for idx, m in enumerate(_merge_requests_store):
        if m["project_id"] == project["id"] and m["iid"] == int(mr_iid):
            if m["draft"]:
                return {"error": "Draft merge request cannot be merged"}
            if m["merge_status"] != "can_be_merged":
                return {"error": "Merge request cannot be merged"}
            if m["state"] == "merged":
                return {"error": "Merge request already merged"}
            _merge_requests_store[idx]["state"] = "merged"
            _merge_requests_store[idx]["merged_at"] = _now()
            _merge_requests_store[idx]["updated_at"] = _now()
            return _merge_requests_store[idx]
    return {"error": f"Merge request {mr_iid} not found in project {project_id}"}


# ---------------------------------------------------------------------------
# Pipelines
# ---------------------------------------------------------------------------

def list_pipelines(project_id, status=None):
    project = _find_project(project_id)
    if not project:
        return {"error": f"Project {project_id} not found"}
    results = [p for p in _pipelines_store if p["project_id"] == project["id"]]
    if status:
        results = [p for p in results if p["status"] == status]
    results.sort(key=lambda p: p["created_at"], reverse=True)
    return results
