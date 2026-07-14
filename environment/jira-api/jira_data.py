"""Data access module for the Jira API mock service."""

import csv
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).parent

import sys as _sys
_sys.path.insert(0, str(DATA_DIR.parent))
from _mutable_store import (
    read_seed_with_ctx, get_store, opt_int, opt_str, strict_bool, strict_int)

_store = get_store("jira-api")
_API = "jira-api"



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
_store.register("users", primary_key="account_id",
                initial_loader=lambda: _coerce_users(_load("users.json", "users")))
_store.register("boards", primary_key="id",
                initial_loader=lambda: _coerce_boards(_load("boards.json", "boards")))
_store.register("sprints", primary_key="id",
                initial_loader=lambda: _coerce_sprints(_load("sprints.json", "sprints")))
_store.register("issues", primary_key="id",
                initial_loader=lambda: _coerce_issues(_load("issues.json", "issues")))


def _projects_rows():
    return _store.table("projects").rows()


def _users_rows():
    return _store.table("users").rows()


def _boards_rows():
    return _store.table("boards").rows()


def _sprints_rows():
    return _store.table("sprints").rows()


def _issues_rows():
    return _store.table("issues").rows()



def _load(filename, table):
    return read_seed_with_ctx(DATA_DIR / filename, _API, table)


def _strip_ctx(r):
    return {k: v for k, v in r.items() if not k.startswith("__")}


def _now():
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000+0000")


def _to_bool(v):
    return str(v).strip().lower() == "true"


def _to_int(v):
    try:
        return int(v)
    except (TypeError, ValueError):
        return None


# Workflow: status name -> {transition_id: target_status}
_WORKFLOW = {
    "To Do": {"11": "In Progress"},
    "In Progress": {"21": "Done", "31": "To Do"},
    "Done": {"41": "In Progress"},
}

_STATUS_CATEGORY = {
    "To Do": {"id": 2, "key": "new", "name": "To Do"},
    "In Progress": {"id": 4, "key": "indeterminate", "name": "In Progress"},
    "Done": {"id": 3, "key": "done", "name": "Done"},
}


# ---------------------------------------------------------------------------
# Load + coerce
# ---------------------------------------------------------------------------

def _coerce_projects(rows):
    return [{**_strip_ctx(r), "id": r["id"]} for r in rows]


def _coerce_users(rows):
    return [{**_strip_ctx(r), "active": strict_bool(r, "active")} for r in rows]


def _coerce_boards(rows):
    return [{**_strip_ctx(r), "id": strict_int(r, "id")} for r in rows]


def _coerce_sprints(rows):
    out = []
    for r in rows:
        out.append({
            **_strip_ctx(r),
            "id": strict_int(r, "id"),
            "board_id": strict_int(r, "board_id"),
            "start_date": opt_str(r, "start_date", default="") or None,
            "end_date": opt_str(r, "end_date", default="") or None,
        })
    return out


def _coerce_issues(rows):
    out = []
    for r in rows:
        out.append({
            **_strip_ctx(r),
            "id": r["id"],
            "sprint_id": opt_int(r, "sprint_id", default=0),
            "story_points": opt_int(r, "story_points", default=0),
            "assignee": opt_str(r, "assignee", default="") or None,
        })
    return out












# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _user_obj(account_id):
    u = next((x for x in _users_rows() if x["account_id"] == account_id), None)
    if not u:
        return None
    return {
        "accountId": u["account_id"],
        "displayName": u["display_name"],
        "emailAddress": u["email"],
        "active": u["active"],
    }


def _serialize_issue(i):
    status_cat = _STATUS_CATEGORY.get(i["status"], _STATUS_CATEGORY["To Do"])
    return {
        "id": i["id"],
        "key": i["key"],
        "fields": {
            "summary": i["summary"],
            "description": i["description"],
            "issuetype": {"name": i["issue_type"]},
            "project": {"key": i["project_key"]},
            "status": {"name": i["status"], "statusCategory": status_cat},
            "priority": {"name": i["priority"]},
            "assignee": _user_obj(i["assignee"]) if i["assignee"] else None,
            "reporter": _user_obj(i["reporter"]),
            "customfield_10016": i["story_points"],
            "created": i["created"],
            "updated": i["updated"],
        },
    }


def _serialize_project(p):
    return {
        "id": p["id"],
        "key": p["key"],
        "name": p["name"],
        "projectTypeKey": p["project_type_key"],
        "lead": _user_obj(p["lead"]),
        "description": p["description"],
    }


def _next_issue_key(project_key):
    nums = []
    for i in _issues_rows():
        if i["project_key"] == project_key and "-" in i["key"]:
            try:
                nums.append(int(i["key"].split("-")[1]))
            except ValueError:
                pass
    return f"{project_key}-{max(nums, default=100) + 1}"


# ---------------------------------------------------------------------------
# Projects
# ---------------------------------------------------------------------------

def list_projects():
    return [_serialize_project(p) for p in _projects_rows()]


# ---------------------------------------------------------------------------
# Issues
# ---------------------------------------------------------------------------

def get_issue(issue_key):
    for i in _issues_rows():
        if i["key"] == issue_key:
            return _serialize_issue(i)
    return {"errorMessages": [f"Issue {issue_key} does not exist"], "errors": {}}


def create_issue(project_key, summary, issue_type="Task", description="",
                 priority="Medium", assignee=None, reporter="user-amelia"):
    proj = next((p for p in _projects_rows() if p["key"] == project_key), None)
    if not proj:
        return {"errorMessages": [f"Project {project_key} not found"], "errors": {}}
    if assignee and not any(u["account_id"] == assignee for u in _users_rows()):
        return {"errorMessages": [], "errors": {"assignee": "Invalid assignee"}}
    key = _next_issue_key(project_key)
    new_id = str(max(int(i["id"]) for i in _issues_rows()) + 1)
    issue = {
        "id": new_id,
        "key": key,
        "project_key": project_key,
        "issue_type": issue_type,
        "summary": summary,
        "description": description or "",
        "status": "To Do",
        "priority": priority,
        "assignee": assignee,
        "reporter": reporter,
        "sprint_id": None,
        "story_points": None,
        "created": _now(),
        "updated": _now(),
    }
    _store_insert("issues", issue)
    return {"id": new_id, "key": key, "self": f"/rest/api/3/issue/{new_id}"}


def update_issue(issue_key, summary=None, description=None, priority=None, assignee=None):
    for issue in _issues_rows():
        if issue["key"] == issue_key:
            _changes = {}
            if summary is not None:
                _changes["summary"] = summary
            if description is not None:
                _changes["description"] = description
            if priority is not None:
                _changes["priority"] = priority
            if assignee is not None:
                _changes["assignee"] = assignee or None
            _changes["updated"] = _now()
            issue.update(_changes)
            _store_patch("issues", issue, _changes)
            return {"key": issue_key, "updated": True}
    return {"errorMessages": [f"Issue {issue_key} does not exist"], "errors": {}}


def get_transitions(issue_key):
    issue = next((i for i in _issues_rows() if i["key"] == issue_key), None)
    if not issue:
        return {"errorMessages": [f"Issue {issue_key} does not exist"], "errors": {}}
    transitions = []
    for tid, target in _WORKFLOW.get(issue["status"], {}).items():
        transitions.append({"id": tid, "name": f"To {target}", "to": {"name": target}})
    return {"transitions": transitions}


def transition_issue(issue_key, transition_id):
    for issue in _issues_rows():
        if issue["key"] == issue_key:
            allowed = _WORKFLOW.get(issue["status"], {})
            if transition_id not in allowed:
                return {"errorMessages": [f"Transition {transition_id} not valid from {issue['status']}"], "errors": {}}
            _changes = {"status": allowed[transition_id], "updated": _now()}
            issue.update(_changes)
            _store_patch("issues", issue, _changes)
            return {"key": issue_key, "status": allowed[transition_id], "transitioned": True}
    return {"errorMessages": [f"Issue {issue_key} does not exist"], "errors": {}}


def search(jql=None, max_results=50):
    results = list(_issues_rows())
    project = None
    status = None
    if jql:
        # Very small JQL parser: supports "project = X" and "status = Y" joined by AND
        for clause in jql.split("AND"):
            clause = clause.strip()
            if "=" not in clause:
                continue
            field, _, value = clause.partition("=")
            field = field.strip().lower()
            value = value.strip().strip('"').strip("'")
            if field == "project":
                project = value
            elif field == "status":
                status = value
    if project:
        results = [i for i in results if i["project_key"] == project]
    if status:
        results = [i for i in results if i["status"].lower() == status.lower()]
    results = results[:max_results]
    return {
        "expand": "schema,names",
        "startAt": 0,
        "maxResults": max_results,
        "total": len(results),
        "issues": [_serialize_issue(i) for i in results],
    }


# ---------------------------------------------------------------------------
# Agile: boards + sprints
# ---------------------------------------------------------------------------

def list_boards():
    return {
        "maxResults": 50,
        "startAt": 0,
        "total": len(_boards_rows()),
        "values": [
            {"id": b["id"], "name": b["name"], "type": b["type"],
             "location": {"projectKey": b["project_key"]}}
            for b in _boards_rows()
        ],
    }


def list_sprints(board_id, state=None):
    if not any(b["id"] == board_id for b in _boards_rows()):
        return {"errorMessages": [f"Board {board_id} not found"], "errors": {}}
    sprints = [s for s in _sprints_rows() if s["board_id"] == board_id]
    if state:
        sprints = [s for s in sprints if s["state"] == state]
    return {
        "maxResults": 50,
        "startAt": 0,
        "total": len(sprints),
        "values": [
            {"id": s["id"], "name": s["name"], "state": s["state"],
             "originBoardId": s["board_id"], "startDate": s["start_date"],
             "endDate": s["end_date"], "goal": s["goal"]}
            for s in sprints
        ],
    }

_store.eager_load()
