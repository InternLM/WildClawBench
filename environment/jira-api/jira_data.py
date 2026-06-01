"""Data access module for the Jira API mock service."""

import csv
from copy import deepcopy
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).parent


def _load(filename):
    with open(DATA_DIR / filename, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


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
    return [{**r, "id": r["id"]} for r in rows]


def _coerce_users(rows):
    return [{**r, "active": _to_bool(r["active"])} for r in rows]


def _coerce_boards(rows):
    return [{**r, "id": int(r["id"])} for r in rows]


def _coerce_sprints(rows):
    out = []
    for r in rows:
        out.append({
            **r,
            "id": int(r["id"]),
            "board_id": int(r["board_id"]),
            "start_date": r["start_date"] or None,
            "end_date": r["end_date"] or None,
        })
    return out


def _coerce_issues(rows):
    out = []
    for r in rows:
        out.append({
            **r,
            "id": r["id"],
            "sprint_id": _to_int(r["sprint_id"]),
            "story_points": _to_int(r["story_points"]),
            "assignee": r["assignee"] or None,
        })
    return out


_projects = _coerce_projects(_load("projects.csv"))
_users = _coerce_users(_load("users.csv"))
_boards = _coerce_boards(_load("boards.csv"))
_sprints = _coerce_sprints(_load("sprints.csv"))
_issues = _coerce_issues(_load("issues.csv"))

_projects_store = deepcopy(_projects)
_users_store = deepcopy(_users)
_boards_store = deepcopy(_boards)
_sprints_store = deepcopy(_sprints)
_issues_store = deepcopy(_issues)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _user_obj(account_id):
    u = next((x for x in _users_store if x["account_id"] == account_id), None)
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
    for i in _issues_store:
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
    return [_serialize_project(p) for p in _projects_store]


# ---------------------------------------------------------------------------
# Issues
# ---------------------------------------------------------------------------

def get_issue(issue_key):
    for i in _issues_store:
        if i["key"] == issue_key:
            return _serialize_issue(i)
    return {"errorMessages": [f"Issue {issue_key} does not exist"], "errors": {}}


def create_issue(project_key, summary, issue_type="Task", description="",
                 priority="Medium", assignee=None, reporter="user-amelia"):
    proj = next((p for p in _projects_store if p["key"] == project_key), None)
    if not proj:
        return {"errorMessages": [f"Project {project_key} not found"], "errors": {}}
    if assignee and not any(u["account_id"] == assignee for u in _users_store):
        return {"errorMessages": [], "errors": {"assignee": "Invalid assignee"}}
    key = _next_issue_key(project_key)
    new_id = str(max(int(i["id"]) for i in _issues_store) + 1)
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
    _issues_store.append(issue)
    return {"id": new_id, "key": key, "self": f"/rest/api/3/issue/{new_id}"}


def update_issue(issue_key, summary=None, description=None, priority=None, assignee=None):
    for i, issue in enumerate(_issues_store):
        if issue["key"] == issue_key:
            if summary is not None:
                _issues_store[i]["summary"] = summary
            if description is not None:
                _issues_store[i]["description"] = description
            if priority is not None:
                _issues_store[i]["priority"] = priority
            if assignee is not None:
                _issues_store[i]["assignee"] = assignee or None
            _issues_store[i]["updated"] = _now()
            return {"key": issue_key, "updated": True}
    return {"errorMessages": [f"Issue {issue_key} does not exist"], "errors": {}}


def get_transitions(issue_key):
    issue = next((i for i in _issues_store if i["key"] == issue_key), None)
    if not issue:
        return {"errorMessages": [f"Issue {issue_key} does not exist"], "errors": {}}
    transitions = []
    for tid, target in _WORKFLOW.get(issue["status"], {}).items():
        transitions.append({"id": tid, "name": f"To {target}", "to": {"name": target}})
    return {"transitions": transitions}


def transition_issue(issue_key, transition_id):
    for i, issue in enumerate(_issues_store):
        if issue["key"] == issue_key:
            allowed = _WORKFLOW.get(issue["status"], {})
            if transition_id not in allowed:
                return {"errorMessages": [f"Transition {transition_id} not valid from {issue['status']}"], "errors": {}}
            _issues_store[i]["status"] = allowed[transition_id]
            _issues_store[i]["updated"] = _now()
            return {"key": issue_key, "status": allowed[transition_id], "transitioned": True}
    return {"errorMessages": [f"Issue {issue_key} does not exist"], "errors": {}}


def search(jql=None, max_results=50):
    results = list(_issues_store)
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
        "total": len(_boards_store),
        "values": [
            {"id": b["id"], "name": b["name"], "type": b["type"],
             "location": {"projectKey": b["project_key"]}}
            for b in _boards_store
        ],
    }


def list_sprints(board_id, state=None):
    if not any(b["id"] == board_id for b in _boards_store):
        return {"errorMessages": [f"Board {board_id} not found"], "errors": {}}
    sprints = [s for s in _sprints_store if s["board_id"] == board_id]
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
