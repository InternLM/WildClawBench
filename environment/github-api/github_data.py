"""Data access module for the GitHub REST API mock service."""

import csv
import json
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).parent

import sys as _sys
_sys.path.insert(0, str(DATA_DIR.parent))
from _mutable_store import (
    read_seed_with_ctx, get_store, opt_csv_list, opt_str, strict_bool, strict_int)

_store = get_store("github-api")
_API = "github-api"



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

_store.register("repos", primary_key="id",
                initial_loader=lambda: _coerce_repos(_load("repos.json", "repos")))
_store.register("issues", primary_key="id",
                initial_loader=lambda: _coerce_issues(_load("issues.json", "issues")))
_store.register("pulls", primary_key="number",
                initial_loader=lambda: _coerce_pulls(_load("pulls.json", "pulls")))
_store.register("comments", primary_key="id",
                initial_loader=lambda: _coerce_comments(_load("comments.json", "comments")))
_store.register_document("user", initial_loader=lambda: __import__('json').load(open(DATA_DIR / "user.json", encoding="utf-8")))


def _repos_rows():
    return _store.table("repos").rows()


def _issues_rows():
    return _store.table("issues").rows()


def _pulls_rows():
    return _store.table("pulls").rows()


def _comments_rows():
    return _store.table("comments").rows()


def _user_doc():
    return _store.document("user").get()



def _load(filename, table):
    return read_seed_with_ctx(DATA_DIR / filename, _API, table)


def _strip_ctx(r):
    return {k: v for k, v in r.items() if not k.startswith("__")}


def _now():
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


def _to_bool(v):
    return str(v).strip().lower() == "true"


def _coerce_repos(rows):
    out = []
    for r in rows:
        out.append({
            **_strip_ctx(r),
            "id": strict_int(r, "id"),
            "private": strict_bool(r, "private"),
            "stars": strict_int(r, "stars"),
            "forks": strict_int(r, "forks"),
            "open_issues": strict_int(r, "open_issues"),
        })
    return out


def _coerce_issues(rows):
    out = []
    for r in rows:
        out.append({
            **_strip_ctx(r),
            "id": strict_int(r, "id"),
            "number": strict_int(r, "number"),
            "is_pull_request": strict_bool(r, "is_pull_request"),
            "labels": [l for l in opt_csv_list(r, "labels", sep=";") if l],
            "closed_at": opt_str(r, "closed_at", default="") or None,
            "milestone": opt_str(r, "milestone", default="") or None,
        })
    return out


def _coerce_pulls(rows):
    out = []
    for r in rows:
        out.append({
            **_strip_ctx(r),
            "number": strict_int(r, "number"),
            "merged": strict_bool(r, "merged"),
            "mergeable": strict_bool(r, "mergeable"),
            "draft": strict_bool(r, "draft"),
            "additions": strict_int(r, "additions"),
            "deletions": strict_int(r, "deletions"),
            "changed_files": strict_int(r, "changed_files"),
        })
    return out


def _coerce_comments(rows):
    return [{**_strip_ctx(r), "id": strict_int(r, "id"), "issue_number": strict_int(r, "issue_number")} for r in rows]







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
    return _user_doc()


# ---------------------------------------------------------------------------
# Repos
# ---------------------------------------------------------------------------

def list_repos(owner=None):
    results = list(_repos_rows())
    if owner:
        results = [r for r in results if r["owner"] == owner]
    return [_serialize_repo(r) for r in results]


def get_repo(owner, repo_name):
    for r in _repos_rows():
        if r["owner"] == owner and r["name"] == repo_name:
            return _serialize_repo(r)
    return {"error": f"Repo {owner}/{repo_name} not found"}


# ---------------------------------------------------------------------------
# Issues
# ---------------------------------------------------------------------------

def list_issues(owner, repo_name, state="open", labels=None, assignee=None,
                limit=30):
    if not any(r["owner"] == owner and r["name"] == repo_name for r in _repos_rows()):
        return {"error": f"Repo {owner}/{repo_name} not found"}
    results = [i for i in _issues_rows() if i["repo"] == repo_name]
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
    for i in _issues_rows():
        if i["repo"] == repo_name and i["number"] == number:
            return _serialize_issue(i)
    return {"error": f"Issue {repo_name}#{number} not found"}


def create_issue(owner, repo_name, title, body, assignee=None, labels=None):
    if not any(r["owner"] == owner and r["name"] == repo_name for r in _repos_rows()):
        return {"error": f"Repo {owner}/{repo_name} not found"}
    next_number = max((i["number"] for i in _issues_rows() if i["repo"] == repo_name), default=0) + 1
    issue = {
        "id": max(i["id"] for i in _issues_rows()) + 1 if _issues_rows() else 1,
        "number": next_number,
        "repo": repo_name,
        "title": title,
        "body": body or "",
        "state": "open",
        "user": _user_doc()["login"],
        "assignee": assignee or "",
        "labels": labels or [],
        "milestone": None,
        "created_at": _now(),
        "updated_at": _now(),
        "closed_at": None,
        "is_pull_request": False,
    }
    _store_insert("issues", issue)
    for r in _repos_rows():
        if r["owner"] == owner and r["name"] == repo_name:
            _changes = {"open_issues": r["open_issues"] + 1}
            r.update(_changes)
            _store_patch("repos", r, _changes)
    return _serialize_issue(issue)


def update_issue(owner, repo_name, number, title=None, body=None, state=None,
                 assignee=None, labels=None):
    for issue in _issues_rows():
        if issue["repo"] == repo_name and issue["number"] == number:
            _changes = {}
            if title is not None:
                _changes["title"] = title
            if body is not None:
                _changes["body"] = body
            if assignee is not None:
                _changes["assignee"] = assignee
            if labels is not None:
                _changes["labels"] = labels
            if state and state != issue["state"]:
                _changes["state"] = state
                if state == "closed":
                    _changes["closed_at"] = _now()
                    for r in _repos_rows():
                        if r["name"] == repo_name:
                            _repo_changes = {"open_issues": max(0, r["open_issues"] - 1)}
                            r.update(_repo_changes)
                            _store_patch("repos", r, _repo_changes)
                else:
                    _changes["closed_at"] = None
            _changes["updated_at"] = _now()
            issue.update(_changes)
            _store_patch("issues", issue, _changes)
            return _serialize_issue(issue)
    return {"error": f"Issue {repo_name}#{number} not found"}


# ---------------------------------------------------------------------------
# Pulls
# ---------------------------------------------------------------------------

def list_pulls(owner, repo_name, state="open"):
    if not any(r["owner"] == owner and r["name"] == repo_name for r in _repos_rows()):
        return {"error": f"Repo {owner}/{repo_name} not found"}
    pulls = [p for p in _pulls_rows() if p["repo"] == repo_name]
    issues_by_number = {i["number"]: i for i in _issues_rows() if i["repo"] == repo_name}
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
    pull = next((p for p in _pulls_rows() if p["repo"] == repo_name and p["number"] == number), None)
    issue = next((i for i in _issues_rows() if i["repo"] == repo_name and i["number"] == number), None)
    if not pull or not issue:
        return {"error": f"Pull {repo_name}#{number} not found"}
    return {**_serialize_issue(issue), **pull}


def merge_pull(owner, repo_name, number):
    for p in _pulls_rows():
        if p["repo"] == repo_name and p["number"] == number:
            if not p["mergeable"]:
                return {"error": "PR is not mergeable"}
            if p["draft"]:
                return {"error": "PR is a draft"}
            _changes = {"merged": True}
            p.update(_changes)
            _store_patch("pulls", p, _changes)
            update_issue(owner, repo_name, number, state="closed")
            return {"merged": True, "sha": "deadbeefcafe123"}
    return {"error": f"Pull {repo_name}#{number} not found"}


# ---------------------------------------------------------------------------
# Comments
# ---------------------------------------------------------------------------

def list_comments(owner, repo_name, number):
    if not any(i["repo"] == repo_name and i["number"] == number for i in _issues_rows()):
        return {"error": f"Issue {repo_name}#{number} not found"}
    return [c for c in _comments_rows() if c["repo"] == repo_name and c["issue_number"] == number]


def create_comment(owner, repo_name, number, body):
    if not any(i["repo"] == repo_name and i["number"] == number for i in _issues_rows()):
        return {"error": f"Issue {repo_name}#{number} not found"}
    comment = {
        "id": max(c["id"] for c in _comments_rows()) + 1 if _comments_rows() else 1,
        "issue_number": number,
        "repo": repo_name,
        "user": _user_doc()["login"],
        "body": body,
        "created_at": _now(),
    }
    _store_insert("comments", comment)
    return comment

_store.eager_load()
