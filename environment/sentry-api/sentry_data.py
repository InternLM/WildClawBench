"""Data access module for the Sentry API mock service."""

import csv
from copy import deepcopy
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).parent


def _load(filename):
    with open(DATA_DIR / filename, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _now():
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000Z")


# ---------------------------------------------------------------------------
# Load + coerce
# ---------------------------------------------------------------------------

def _coerce_organizations(rows):
    return [{**r, "id": int(r["id"])} for r in rows]


def _coerce_projects(rows):
    return [{**r, "id": int(r["id"])} for r in rows]


def _coerce_issues(rows):
    out = []
    for r in rows:
        out.append({
            **r,
            "id": int(r["id"]),
            "count": int(r["count"]),
            "user_count": int(r["user_count"]),
        })
    return out


def _coerce_events(rows):
    out = []
    for r in rows:
        out.append({
            **r,
            "id": int(r["id"]),
            "issue_id": int(r["issue_id"]),
        })
    return out


def _coerce_releases(rows):
    out = []
    for r in rows:
        out.append({
            **r,
            "new_groups": int(r["new_groups"]),
            "date_released": r["date_released"] or None,
        })
    return out


_organizations = _coerce_organizations(_load("organizations.csv"))
_projects = _coerce_projects(_load("projects.csv"))
_issues = _coerce_issues(_load("issues.csv"))
_events = _coerce_events(_load("events.csv"))
_releases = _coerce_releases(_load("releases.csv"))

_organizations_store = deepcopy(_organizations)
_projects_store = deepcopy(_projects)
_issues_store = deepcopy(_issues)
_events_store = deepcopy(_events)
_releases_store = deepcopy(_releases)

_VALID_STATUSES = {"resolved", "ignored", "unresolved"}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _org_exists(org_slug):
    return any(o["slug"] == org_slug for o in _organizations_store)


def _serialize_issue(i):
    return {
        "id": str(i["id"]),
        "shortId": i["short_id"],
        "title": i["title"],
        "culprit": i["culprit"],
        "level": i["level"],
        "status": i["status"],
        "count": i["count"],
        "userCount": i["user_count"],
        "project": {"slug": i["project_slug"]},
        "firstSeen": i["first_seen"],
        "lastSeen": i["last_seen"],
    }


def _serialize_event(e):
    return {
        "id": str(e["id"]),
        "eventID": e["event_id"],
        "message": e["message"],
        "platform": e["platform"],
        "environment": e["environment"],
        "release": e["release"],
        "user": {"email": e["user_email"]},
        "dateCreated": e["date_created"],
    }


def _serialize_release(r):
    return {
        "version": r["version"],
        "ref": r["ref"],
        "status": r["status"],
        "newGroups": r["new_groups"],
        "projects": [{"slug": r["project_slug"]}],
        "dateCreated": r["date_created"],
        "dateReleased": r["date_released"],
    }


# ---------------------------------------------------------------------------
# Projects
# ---------------------------------------------------------------------------

def list_org_projects(org_slug):
    if not _org_exists(org_slug):
        return {"error": f"Organization {org_slug} not found"}
    return [
        {
            "id": str(p["id"]),
            "slug": p["slug"],
            "name": p["name"],
            "platform": p["platform"],
            "status": p["status"],
            "dateCreated": p["date_created"],
        }
        for p in _projects_store if p["org_slug"] == org_slug
    ]


# ---------------------------------------------------------------------------
# Issues
# ---------------------------------------------------------------------------

def list_project_issues(org_slug, project_slug, status=None, level=None):
    if not _org_exists(org_slug):
        return {"error": f"Organization {org_slug} not found"}
    if not any(p["org_slug"] == org_slug and p["slug"] == project_slug for p in _projects_store):
        return {"error": f"Project {project_slug} not found"}
    results = [i for i in _issues_store
               if i["org_slug"] == org_slug and i["project_slug"] == project_slug]
    if status:
        results = [i for i in results if i["status"] == status]
    if level:
        results = [i for i in results if i["level"] == level]
    results.sort(key=lambda i: i["last_seen"], reverse=True)
    return [_serialize_issue(i) for i in results]


def get_issue(org_slug, issue_id):
    if not _org_exists(org_slug):
        return {"error": f"Organization {org_slug} not found"}
    for i in _issues_store:
        if i["org_slug"] == org_slug and str(i["id"]) == str(issue_id):
            return _serialize_issue(i)
    return {"error": f"Issue {issue_id} not found"}


def update_issue_status(org_slug, issue_id, status):
    if not _org_exists(org_slug):
        return {"error": f"Organization {org_slug} not found"}
    if status not in _VALID_STATUSES:
        return {"error": f"Invalid status {status}", "valid": sorted(_VALID_STATUSES)}
    for idx, i in enumerate(_issues_store):
        if i["org_slug"] == org_slug and str(i["id"]) == str(issue_id):
            _issues_store[idx]["status"] = status
            _issues_store[idx]["last_seen"] = _now()
            return _serialize_issue(_issues_store[idx])
    return {"error": f"Issue {issue_id} not found"}


def list_issue_events(org_slug, issue_id):
    if not _org_exists(org_slug):
        return {"error": f"Organization {org_slug} not found"}
    if not any(i["org_slug"] == org_slug and str(i["id"]) == str(issue_id) for i in _issues_store):
        return {"error": f"Issue {issue_id} not found"}
    events = [e for e in _events_store if str(e["issue_id"]) == str(issue_id)]
    events.sort(key=lambda e: e["date_created"], reverse=True)
    return [_serialize_event(e) for e in events]


# ---------------------------------------------------------------------------
# Releases
# ---------------------------------------------------------------------------

def list_releases(org_slug, project_slug=None):
    if not _org_exists(org_slug):
        return {"error": f"Organization {org_slug} not found"}
    results = [r for r in _releases_store if r["org_slug"] == org_slug]
    if project_slug:
        results = [r for r in results if r["project_slug"] == project_slug]
    results.sort(key=lambda r: r["date_created"], reverse=True)
    return [_serialize_release(r) for r in results]
