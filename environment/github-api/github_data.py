"""Data access module for the GitHub REST API mock service."""

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
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


def _to_bool(v):
    return str(v).strip().lower() == "true"


def _coerce_repos(rows):
    out = []
    for r in rows:
        out.append({
            **r,
            "id": int(r["id"]),
            "private": _to_bool(r["private"]),
            "stars": int(r["stars"]),
            "forks": int(r["forks"]),
            "open_issues": int(r["open_issues"]),
        })
    return out


def _coerce_issues(rows):
    out = []
    for r in rows:
        out.append({
            **r,
            "id": int(r["id"]),
            "number": int(r["number"]),
            "is_pull_request": _to_bool(r["is_pull_request"]),
            "labels": [l for l in r["labels"].split(";") if l],
            "closed_at": r["closed_at"] or None,
            "milestone": r["milestone"] or None,
        })
    return out


def _coerce_pulls(rows):
    out = []
    for r in rows:
        out.append({
            **r,
            "number": int(r["number"]),
            "merged": _to_bool(r["merged"]),
            "mergeable": _to_bool(r["mergeable"]),
            "draft": _to_bool(r["draft"]),
            "additions": int(r["additions"]),
            "deletions": int(r["deletions"]),
            "changed_files": int(r["changed_files"]),
        })
    return out


def _coerce_comments(rows):
    return [{**r, "id": int(r["id"]), "issue_number": int(r["issue_number"])} for r in rows]


_repos = _coerce_repos(_load("repos.csv"))
_issues = _coerce_issues(_load("issues.csv"))
_pulls = _coerce_pulls(_load("pulls.csv"))
_comments = _coerce_comments(_load("comments.csv"))

with open(DATA_DIR / "user.json", encoding="utf-8") as _f:
    _user = json.load(_f)

_repos_store = deepcopy(_repos)
_issues_store = deepcopy(_issues)
_pulls_store = deepcopy(_pulls)
_comments_store = deepcopy(_comments)
_user_store = deepcopy(_user)


def _serialize_repo(r):
    return {
        "id": r["id"],
        "name": r["name"],
        "full_name": r["full_name"],
        "owner": {"login": r["owner"]},
        "private": r["private"],
        "description": r["description"],
        "default_branch": r["default_branch"],
        "language": r["language"],
        "stargazers_count": r["stars"],
        "forks_count": r["forks"],
        "open_issues_count": r["open_issues"],
        "created_at": r["created_at"],
        "updated_at": r["updated_at"],
    }


def _serialize_issue(i):
    return {
        "id": i["id"],
        "number": i["number"],
        "title": i["title"],
        "body": i["body"],
        "state": i["state"],
        "user": {"login": i["user"]},
        "assignee": {"login": i["assignee"]} if i["assignee"] else None,
        "labels": [{"name": l} for l in i["labels"]],
        "milestone": {"title": i["milestone"]} if i["milestone"] else None,
        "created_at": i["created_at"],
        "updated_at": i["updated_at"],
        "closed_at": i["closed_at"],
        "pull_request": {"url": f"/repos/{i['repo']}/pulls/{i['number']}"} if i["is_pull_request"] else None,
    }


# ---------------------------------------------------------------------------
# User
# ---------------------------------------------------------------------------

def get_user():
    return _user_store


# ---------------------------------------------------------------------------
# Repos
# ---------------------------------------------------------------------------

def list_repos(owner=None):
    results = list(_repos_store)
    if owner:
        results = [r for r in results if r["owner"] == owner]
    return [_serialize_repo(r) for r in results]


def get_repo(owner, repo_name):
    for r in _repos_store:
        if r["owner"] == owner and r["name"] == repo_name:
            return _serialize_repo(r)
    return {"error": f"Repo {owner}/{repo_name} not found"}


# ---------------------------------------------------------------------------
# Issues
# ---------------------------------------------------------------------------

def list_issues(owner, repo_name, state="open", labels=None, assignee=None,
                limit=30):
    if not any(r["owner"] == owner and r["name"] == repo_name for r in _repos_store):
        return {"error": f"Repo {owner}/{repo_name} not found"}
    results = [i for i in _issues_store if i["repo"] == repo_name]
    if state and state != "all":
        results = [i for i in results if i["state"] == state]
    if labels:
        wanted = {l.strip().lower() for l in labels.split(",")}
        results = [i for i in results if {l.lower() for l in i["labels"]} & wanted]
    if assignee:
        results = [i for i in results if i["assignee"] == assignee]
    results.sort(key=lambda i: i["updated_at"], reverse=True)
    return [_serialize_issue(i) for i in results[:limit]]


def get_issue(owner, repo_name, number):
    for i in _issues_store:
        if i["repo"] == repo_name and i["number"] == number:
            return _serialize_issue(i)
    return {"error": f"Issue {repo_name}#{number} not found"}


def create_issue(owner, repo_name, title, body, assignee=None, labels=None):
    if not any(r["owner"] == owner and r["name"] == repo_name for r in _repos_store):
        return {"error": f"Repo {owner}/{repo_name} not found"}
    next_number = max((i["number"] for i in _issues_store if i["repo"] == repo_name), default=0) + 1
    issue = {
        "id": max(i["id"] for i in _issues_store) + 1 if _issues_store else 1,
        "number": next_number,
        "repo": repo_name,
        "title": title,
        "body": body or "",
        "state": "open",
        "user": _user_store["login"],
        "assignee": assignee or "",
        "labels": labels or [],
        "milestone": None,
        "created_at": _now(),
        "updated_at": _now(),
        "closed_at": None,
        "is_pull_request": False,
    }
    _issues_store.append(issue)
    for j, r in enumerate(_repos_store):
        if r["owner"] == owner and r["name"] == repo_name:
            _repos_store[j]["open_issues"] += 1
    return _serialize_issue(issue)


def update_issue(owner, repo_name, number, title=None, body=None, state=None,
                 assignee=None, labels=None):
    for i, issue in enumerate(_issues_store):
        if issue["repo"] == repo_name and issue["number"] == number:
            if title is not None:
                _issues_store[i]["title"] = title
            if body is not None:
                _issues_store[i]["body"] = body
            if assignee is not None:
                _issues_store[i]["assignee"] = assignee
            if labels is not None:
                _issues_store[i]["labels"] = labels
            if state and state != _issues_store[i]["state"]:
                _issues_store[i]["state"] = state
                if state == "closed":
                    _issues_store[i]["closed_at"] = _now()
                    for j, r in enumerate(_repos_store):
                        if r["name"] == repo_name:
                            _repos_store[j]["open_issues"] = max(0, _repos_store[j]["open_issues"] - 1)
                else:
                    _issues_store[i]["closed_at"] = None
            _issues_store[i]["updated_at"] = _now()
            return _serialize_issue(_issues_store[i])
    return {"error": f"Issue {repo_name}#{number} not found"}


# ---------------------------------------------------------------------------
# Pulls
# ---------------------------------------------------------------------------

def list_pulls(owner, repo_name, state="open"):
    if not any(r["owner"] == owner and r["name"] == repo_name for r in _repos_store):
        return {"error": f"Repo {owner}/{repo_name} not found"}
    pulls = [p for p in _pulls_store if p["repo"] == repo_name]
    issues_by_number = {i["number"]: i for i in _issues_store if i["repo"] == repo_name}
    out = []
    for p in pulls:
        issue = issues_by_number.get(p["number"])
        if not issue:
            continue
        if state != "all" and issue["state"] != state:
            continue
        out.append({**_serialize_issue(issue), **p, "issue_state": issue["state"]})
    return out


def get_pull(owner, repo_name, number):
    pull = next((p for p in _pulls_store if p["repo"] == repo_name and p["number"] == number), None)
    issue = next((i for i in _issues_store if i["repo"] == repo_name and i["number"] == number), None)
    if not pull or not issue:
        return {"error": f"Pull {repo_name}#{number} not found"}
    return {**_serialize_issue(issue), **pull}


def merge_pull(owner, repo_name, number):
    for i, p in enumerate(_pulls_store):
        if p["repo"] == repo_name and p["number"] == number:
            if not p["mergeable"]:
                return {"error": "PR is not mergeable"}
            if p["draft"]:
                return {"error": "PR is a draft"}
            _pulls_store[i]["merged"] = True
            update_issue(owner, repo_name, number, state="closed")
            return {"merged": True, "sha": "deadbeefcafe123"}
    return {"error": f"Pull {repo_name}#{number} not found"}


# ---------------------------------------------------------------------------
# Comments
# ---------------------------------------------------------------------------

def list_comments(owner, repo_name, number):
    if not any(i["repo"] == repo_name and i["number"] == number for i in _issues_store):
        return {"error": f"Issue {repo_name}#{number} not found"}
    return [c for c in _comments_store if c["repo"] == repo_name and c["issue_number"] == number]


def create_comment(owner, repo_name, number, body):
    if not any(i["repo"] == repo_name and i["number"] == number for i in _issues_store):
        return {"error": f"Issue {repo_name}#{number} not found"}
    comment = {
        "id": max(c["id"] for c in _comments_store) + 1 if _comments_store else 1,
        "issue_number": number,
        "repo": repo_name,
        "user": _user_store["login"],
        "body": body,
        "created_at": _now(),
    }
    _comments_store.append(comment)
    return comment
