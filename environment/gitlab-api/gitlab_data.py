"""Data access module for the GitLab API mock service."""

import csv
import json
import uuid
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).parent

import sys as _sys
_sys.path.insert(0, str(DATA_DIR.parent))
from _mutable_store import (
    read_seed_with_ctx, get_store, opt_csv_list, opt_str, strict_bool, strict_int)

_store = get_store("gitlab-api")
_API = "gitlab-api"



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

_store.register("projects", primary_key="id",
                initial_loader=lambda: _coerce_projects(_load("projects.json", "projects")))
_store.register("issues", primary_key="id",
                initial_loader=lambda: _coerce_issues(_load("issues.json", "issues")))
_store.register("merge_requests", primary_key="id",
                initial_loader=lambda: _coerce_merge_requests(_load("merge_requests.json", "merge_requests")))
_store.register("pipelines", primary_key="id",
                initial_loader=lambda: _coerce_pipelines(_load("pipelines.json", "pipelines")))
_store.register("users", primary_key="id",
                initial_loader=lambda: _coerce_users(_load("users.json", "users")))
_store.register_document("current_user", initial_loader=lambda: __import__('json').load(open(DATA_DIR / "current_user.json", encoding="utf-8")))


def _projects_rows():
    return _store.table("projects").rows()


def _issues_rows():
    return _store.table("issues").rows()


def _merge_requests_rows():
    return _store.table("merge_requests").rows()


def _pipelines_rows():
    return _store.table("pipelines").rows()


def _users_rows():
    return _store.table("users").rows()


def _current_user_doc():
    return _store.document("current_user").get()



def _load(filename, table):
    return read_seed_with_ctx(DATA_DIR / filename, _API, table)


def _strip_ctx(r):
    return {k: v for k, v in r.items() if not k.startswith("__")}


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
            **_strip_ctx(r),
            "id": strict_int(r, "id"),
            "star_count": strict_int(r, "star_count"),
            "forks_count": strict_int(r, "forks_count"),
            "open_issues_count": strict_int(r, "open_issues_count"),
        })
    return out


def _coerce_issues(rows):
    out = []
    for r in rows:
        out.append({
            **_strip_ctx(r),
            "id": strict_int(r, "id"),
            "iid": strict_int(r, "iid"),
            "project_id": strict_int(r, "project_id"),
            "labels": [l for l in opt_csv_list(r, "labels", sep=";") if l],
            "closed_at": opt_str(r, "closed_at", default="") or None,
        })
    return out


def _coerce_merge_requests(rows):
    out = []
    for r in rows:
        out.append({
            **_strip_ctx(r),
            "id": strict_int(r, "id"),
            "iid": strict_int(r, "iid"),
            "project_id": strict_int(r, "project_id"),
            "draft": strict_bool(r, "draft"),
            "merged_at": opt_str(r, "merged_at", default="") or None,
        })
    return out


def _coerce_pipelines(rows):
    out = []
    for r in rows:
        out.append({
            **_strip_ctx(r),
            "id": strict_int(r, "id"),
            "project_id": strict_int(r, "project_id"),
            "duration": strict_int(r, "duration"),
        })
    return out


def _coerce_users(rows):
    out = []
    for r in rows:
        out.append({
            **_strip_ctx(r),
            "id": strict_int(r, "id"),
            "is_admin": strict_bool(r, "is_admin"),
        })
    return out








# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _find_project(project_id):
    try:
        pid = int(project_id)
    except (TypeError, ValueError):
        return None
    return next((p for p in _projects_rows() if p["id"] == pid), None)


def _new_numeric_id(store):
    return max((row["id"] for row in store), default=0) + 1


# ---------------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------------

def get_current_user():
    return _current_user_doc()


def list_users():
    return list(_users_rows())


# ---------------------------------------------------------------------------
# Projects
# ---------------------------------------------------------------------------

def list_projects(visibility=None):
    results = list(_projects_rows())
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
    results = [i for i in _issues_rows() if i["project_id"] == project["id"]]
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
    for i in _issues_rows():
        if i["project_id"] == project["id"] and i["iid"] == int(issue_iid):
            return i
    return {"error": f"Issue {issue_iid} not found in project {project_id}"}


def create_issue(project_id, title, description="", assignee=None, labels=None):
    project = _find_project(project_id)
    if not project:
        return {"error": f"Project {project_id} not found"}
    next_iid = max((i["iid"] for i in _issues_rows() if i["project_id"] == project["id"]), default=0) + 1
    issue = {
        "id": _new_numeric_id(_issues_rows()),
        "iid": next_iid,
        "project_id": project["id"],
        "title": title,
        "description": description or "",
        "state": "opened",
        "author": _current_user_doc()["username"],
        "assignee": assignee or "",
        "labels": labels or [],
        "created_at": _now(),
        "updated_at": _now(),
        "closed_at": None,
    }
    _store_insert("issues", issue)
    _proj_changes = {"open_issues_count": project["open_issues_count"] + 1}
    project.update(_proj_changes)
    _store_patch("projects", project, _proj_changes)
    return issue


def update_issue(project_id, issue_iid, title=None, description=None,
                 state_event=None, assignee=None, labels=None):
    project = _find_project(project_id)
    if not project:
        return {"error": f"Project {project_id} not found"}
    for i in _issues_rows():
        if i["project_id"] == project["id"] and i["iid"] == int(issue_iid):
            _changes = {}
            if title is not None:
                _changes["title"] = title
            if description is not None:
                _changes["description"] = description
            if assignee is not None:
                _changes["assignee"] = assignee
            if labels is not None:
                _changes["labels"] = labels
            if state_event == "close" and i["state"] != "closed":
                _changes["state"] = "closed"
                _changes["closed_at"] = _now()
                _proj_changes = {"open_issues_count": max(0, project["open_issues_count"] - 1)}
                project.update(_proj_changes)
                _store_patch("projects", project, _proj_changes)
            elif state_event == "reopen" and i["state"] != "opened":
                _changes["state"] = "opened"
                _changes["closed_at"] = None
                _proj_changes = {"open_issues_count": project["open_issues_count"] + 1}
                project.update(_proj_changes)
                _store_patch("projects", project, _proj_changes)
            _changes["updated_at"] = _now()
            i.update(_changes)
            _store_patch("issues", i, _changes)
            return i
    return {"error": f"Issue {issue_iid} not found in project {project_id}"}


# ---------------------------------------------------------------------------
# Merge requests
# ---------------------------------------------------------------------------

def list_merge_requests(project_id, state=None):
    project = _find_project(project_id)
    if not project:
        return {"error": f"Project {project_id} not found"}
    results = [m for m in _merge_requests_rows() if m["project_id"] == project["id"]]
    if state and state != "all":
        results = [m for m in results if m["state"] == state]
    results.sort(key=lambda m: m["updated_at"], reverse=True)
    return results


def create_merge_request(project_id, title, source_branch, target_branch="main",
                         description="", assignee=None):
    project = _find_project(project_id)
    if not project:
        return {"error": f"Project {project_id} not found"}
    next_iid = max((m["iid"] for m in _merge_requests_rows() if m["project_id"] == project["id"]), default=0) + 1
    mr = {
        "id": _new_numeric_id(_merge_requests_rows()),
        "iid": next_iid,
        "project_id": project["id"],
        "title": title,
        "description": description or "",
        "state": "opened",
        "source_branch": source_branch,
        "target_branch": target_branch,
        "author": _current_user_doc()["username"],
        "assignee": assignee or "",
        "merge_status": "can_be_merged",
        "draft": False,
        "created_at": _now(),
        "updated_at": _now(),
        "merged_at": None,
    }
    _store_insert("merge_requests", mr)
    return mr


def merge_merge_request(project_id, mr_iid):
    project = _find_project(project_id)
    if not project:
        return {"error": f"Project {project_id} not found"}
    for m in _merge_requests_rows():
        if m["project_id"] == project["id"] and m["iid"] == int(mr_iid):
            if m["draft"]:
                return {"error": "Draft merge request cannot be merged"}
            if m["merge_status"] != "can_be_merged":
                return {"error": "Merge request cannot be merged"}
            if m["state"] == "merged":
                return {"error": "Merge request already merged"}
            _changes = {"state": "merged", "merged_at": _now(), "updated_at": _now()}
            m.update(_changes)
            _store_patch("merge_requests", m, _changes)
            return m
    return {"error": f"Merge request {mr_iid} not found in project {project_id}"}


# ---------------------------------------------------------------------------
# Pipelines
# ---------------------------------------------------------------------------

def list_pipelines(project_id, status=None):
    project = _find_project(project_id)
    if not project:
        return {"error": f"Project {project_id} not found"}
    results = [p for p in _pipelines_rows() if p["project_id"] == project["id"]]
    if status:
        results = [p for p in results if p["status"] == status]
    results.sort(key=lambda p: p["created_at"], reverse=True)
    return results

_store.eager_load()
