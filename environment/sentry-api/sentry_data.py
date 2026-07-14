"""Data access module for the Sentry API mock service."""

import csv
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).parent

import sys as _sys
_sys.path.insert(0, str(DATA_DIR.parent))
from _mutable_store import (  # noqa: E402
    read_seed_with_ctx, get_store, opt_str, strict_int)

_store = get_store("sentry-api")
_API = "sentry-api"


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

_store.register("organizations", primary_key="id",
                initial_loader=lambda: _coerce_organizations(_load("organizations.json", "organizations")))
_store.register("projects", primary_key="id",
                initial_loader=lambda: _coerce_projects(_load("projects.json", "projects")))
_store.register("issues", primary_key="id",
                initial_loader=lambda: _coerce_issues(_load("issues.json", "issues")))
_store.register("events", primary_key="event_id",
                initial_loader=lambda: _coerce_events(_load("events.json", "events")))
_store.register("releases", primary_key="version",
                initial_loader=lambda: _coerce_releases(_load("releases.json", "releases")))


def _organizations_rows():
    return _store.table("organizations").rows()


def _projects_rows():
    return _store.table("projects").rows()


def _issues_rows():
    return _store.table("issues").rows()


def _events_rows():
    return _store.table("events").rows()


def _releases_rows():
    return _store.table("releases").rows()



def _load(filename, table):
    return read_seed_with_ctx(DATA_DIR / filename, _API, table)


def _strip_ctx(r):
    return {k: v for k, v in r.items() if not k.startswith("__")}


def _now():
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000Z")


# ---------------------------------------------------------------------------
# Load + coerce
# ---------------------------------------------------------------------------

def _coerce_organizations(rows):
    return [{**_strip_ctx(r), "id": strict_int(r, "id")} for r in rows]


def _coerce_projects(rows):
    return [{**_strip_ctx(r), "id": strict_int(r, "id")} for r in rows]


def _coerce_issues(rows):
    out = []
    for r in rows:
        out.append({
            **_strip_ctx(r),
            "id": strict_int(r, "id"),
            "count": strict_int(r, "count"),
            "user_count": strict_int(r, "user_count"),
        })
    return out


def _coerce_events(rows):
    out = []
    for r in rows:
        out.append({
            **_strip_ctx(r),
            "id": strict_int(r, "id"),
            "issue_id": strict_int(r, "issue_id"),
        })
    return out


def _coerce_releases(rows):
    out = []
    for r in rows:
        out.append({
            **_strip_ctx(r),
            "new_groups": strict_int(r, "new_groups"),
            "date_released": opt_str(r, "date_released", default="") or None,
        })
    return out












_VALID_STATUSES = {"resolved", "ignored", "unresolved"}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _org_exists(org_slug):
    return any(o["slug"] == org_slug for o in _organizations_rows())


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
        for p in _projects_rows() if p["org_slug"] == org_slug
    ]


# ---------------------------------------------------------------------------
# Issues
# ---------------------------------------------------------------------------

def list_project_issues(org_slug, project_slug, status=None, level=None):
    if not _org_exists(org_slug):
        return {"error": f"Organization {org_slug} not found"}
    if not any(p["org_slug"] == org_slug and p["slug"] == project_slug for p in _projects_rows()):
        return {"error": f"Project {project_slug} not found"}
    results = [i for i in _issues_rows()
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
    for i in _issues_rows():
        if i["org_slug"] == org_slug and str(i["id"]) == str(issue_id):
            return _serialize_issue(i)
    return {"error": f"Issue {issue_id} not found"}


def update_issue_status(org_slug, issue_id, status):
    if not _org_exists(org_slug):
        return {"error": f"Organization {org_slug} not found"}
    if status not in _VALID_STATUSES:
        return {"error": f"Invalid status {status}", "valid": sorted(_VALID_STATUSES)}
    for i in _issues_rows():
        if i["org_slug"] == org_slug and str(i["id"]) == str(issue_id):
            _changes = {"status": status, "last_seen": _now()}
            i.update(_changes)
            _store_patch("issues", i, _changes)
            return _serialize_issue(i)
    return {"error": f"Issue {issue_id} not found"}


def list_issue_events(org_slug, issue_id):
    if not _org_exists(org_slug):
        return {"error": f"Organization {org_slug} not found"}
    if not any(i["org_slug"] == org_slug and str(i["id"]) == str(issue_id) for i in _issues_rows()):
        return {"error": f"Issue {issue_id} not found"}
    events = [e for e in _events_rows() if str(e["issue_id"]) == str(issue_id)]
    events.sort(key=lambda e: e["date_created"], reverse=True)
    return [_serialize_event(e) for e in events]


# ---------------------------------------------------------------------------
# Releases
# ---------------------------------------------------------------------------

def list_releases(org_slug, project_slug=None):
    if not _org_exists(org_slug):
        return {"error": f"Organization {org_slug} not found"}
    results = [r for r in _releases_rows() if r["org_slug"] == org_slug]
    if project_slug:
        results = [r for r in results if r["project_slug"] == project_slug]
    results.sort(key=lambda r: r["date_created"], reverse=True)
    return [_serialize_release(r) for r in results]

_store.eager_load()
