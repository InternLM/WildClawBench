"""Data access module for the Confluence Cloud REST API mock service.

Models spaces, pages (content type=page), comments, and labels with
parent/child relationships and version numbers. Mutations are held in
process memory and reset on restart.
"""

import csv
import uuid
from copy import deepcopy
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).parent

BASE = "/wiki/rest/api"


def _load(filename):
    with open(DATA_DIR / filename, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _now():
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000Z")


def _to_int(v, default=0):
    try:
        return int(v)
    except (TypeError, ValueError):
        return default


# ---------------------------------------------------------------------------
# Load + coerce
# ---------------------------------------------------------------------------

def _coerce_spaces(rows):
    out = []
    for r in rows:
        out.append({
            "id": _to_int(r["id"]),
            "key": r["key"],
            "name": r["name"],
            "type": r["type"],
            "status": r["status"],
            "description": {"plain": {"value": r["description"], "representation": "plain"}},
        })
    return out


def _coerce_pages(rows):
    out = []
    for r in rows:
        out.append({
            "id": r["id"],
            "type": r["type"],
            "status": r["status"],
            "title": r["title"],
            "space_key": r["space_key"],
            "parent_id": r["parent_id"] or None,
            "version": _to_int(r["version"], 1),
            "body": r["body"],
            "created_by": r["created_by"],
            "created_at": r["created_at"],
        })
    return out


def _coerce_comments(rows):
    out = []
    for r in rows:
        out.append({
            "id": r["id"],
            "page_id": r["page_id"],
            "author": r["author"],
            "body": r["body"],
            "created_at": r["created_at"],
        })
    return out


def _coerce_labels(rows):
    out = []
    for r in rows:
        out.append({
            "id": r["id"],
            "page_id": r["page_id"],
            "name": r["name"],
            "prefix": r["prefix"],
        })
    return out


_spaces = _coerce_spaces(_load("spaces.csv"))
_pages = _coerce_pages(_load("pages.csv"))
_comments = _coerce_comments(_load("comments.csv"))
_labels = _coerce_labels(_load("labels.csv"))

_spaces_store = deepcopy(_spaces)
_pages_store = deepcopy(_pages)
_comments_store = deepcopy(_comments)
_labels_store = deepcopy(_labels)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _new_page_id():
    return str(uuid.uuid4().int % 9_000_000 + 1_000_000)


def _find_page(page_id):
    return next((p for p in _pages_store if p["id"] == page_id), None)


def _find_space(space_key):
    return next((s for s in _spaces_store if s["key"] == space_key), None)


def _content_view(page, expand_body=True):
    """Render an internal page record into a Confluence content envelope."""
    view = {
        "id": page["id"],
        "type": page["type"],
        "status": page["status"],
        "title": page["title"],
        "space": {"key": page["space_key"]},
        "version": {"number": page["version"]},
        "history": {"createdBy": {"username": page["created_by"]}, "createdDate": page["created_at"]},
        "_links": {"webui": f"/spaces/{page['space_key']}/pages/{page['id']}"},
    }
    if page["parent_id"]:
        view["ancestors"] = [{"id": page["parent_id"], "type": "page"}]
    if expand_body:
        view["body"] = {"storage": {"value": page["body"], "representation": "storage"}}
    return view


# ---------------------------------------------------------------------------
# Spaces
# ---------------------------------------------------------------------------

def list_spaces(limit=25):
    return {
        "results": [deepcopy(s) for s in _spaces_store[:limit]],
        "size": min(len(_spaces_store), limit),
        "_links": {"base": BASE},
    }


def get_space(space_key):
    s = _find_space(space_key)
    if not s:
        return {"error": f"No space with key: {space_key}"}
    return deepcopy(s)


# ---------------------------------------------------------------------------
# Content (pages)
# ---------------------------------------------------------------------------

def list_content(type="page", space_key=None, limit=25):
    results = [p for p in _pages_store if p["type"] == type]
    if space_key:
        results = [p for p in results if p["space_key"] == space_key]
    views = [_content_view(p) for p in results[:limit]]
    return {"results": views, "size": len(views), "_links": {"base": BASE}}


def get_content(content_id):
    p = _find_page(content_id)
    if not p:
        return {"error": f"No content with id: {content_id}"}
    return _content_view(p)


def create_content(title, space_key, body="", parent_id=None, created_by="apiuser"):
    if not _find_space(space_key):
        return {"error": f"No space with key: {space_key}"}
    if parent_id and not _find_page(parent_id):
        return {"error": f"No parent content with id: {parent_id}"}
    page = {
        "id": _new_page_id(),
        "type": "page",
        "status": "current",
        "title": title,
        "space_key": space_key,
        "parent_id": parent_id,
        "version": 1,
        "body": body or "",
        "created_by": created_by,
        "created_at": _now(),
    }
    _pages_store.append(page)
    return _content_view(page)


def update_content(content_id, title=None, body=None, version_number=None):
    page = _find_page(content_id)
    if not page:
        return {"error": f"No content with id: {content_id}"}
    expected = page["version"] + 1
    if version_number is not None and version_number != expected:
        return {
            "error": f"Version must be incremented; expected {expected}, got {version_number}",
            "conflict": True,
        }
    if title is not None:
        page["title"] = title
    if body is not None:
        page["body"] = body
    page["version"] = expected
    return _content_view(page)


def list_child_pages(content_id, limit=25):
    if not _find_page(content_id):
        return {"error": f"No content with id: {content_id}"}
    children = [p for p in _pages_store if p["parent_id"] == content_id and p["type"] == "page"]
    views = [_content_view(c, expand_body=False) for c in children[:limit]]
    return {"results": views, "size": len(views), "_links": {"base": BASE}}


def list_labels(content_id):
    if not _find_page(content_id):
        return {"error": f"No content with id: {content_id}"}
    labels = [
        {"id": l["id"], "name": l["name"], "prefix": l["prefix"], "label": l["name"]}
        for l in _labels_store if l["page_id"] == content_id
    ]
    return {"results": labels, "size": len(labels)}


def list_comments(content_id):
    if not _find_page(content_id):
        return {"error": f"No content with id: {content_id}"}
    comments = [
        {
            "id": c["id"],
            "type": "comment",
            "container": {"id": content_id, "type": "page"},
            "history": {"createdBy": {"username": c["author"]}, "createdDate": c["created_at"]},
            "body": {"storage": {"value": c["body"], "representation": "storage"}},
        }
        for c in _comments_store if c["page_id"] == content_id
    ]
    return {"results": comments, "size": len(comments)}


# ---------------------------------------------------------------------------
# Search (simplified CQL)
# ---------------------------------------------------------------------------

def search(cql):
    if not cql:
        return {"error": "cql parameter is required"}
    results = list(_pages_store)
    parts = [p.strip() for p in cql.split(" AND ")]
    for part in parts:
        if part.startswith("space="):
            key = part.split("=", 1)[1].strip().strip('"').strip("'")
            results = [p for p in results if p["space_key"] == key]
        elif part.startswith("title~"):
            term = part.split("~", 1)[1].strip().strip('"').strip("'").lower()
            results = [p for p in results if term in p["title"].lower()]
        elif part.startswith("type="):
            t = part.split("=", 1)[1].strip().strip('"').strip("'")
            results = [p for p in results if p["type"] == t]
    views = [_content_view(p, expand_body=False) for p in results]
    return {
        "results": [{"content": v, "title": v["title"]} for v in views],
        "size": len(views),
        "totalSize": len(views),
        "cqlQuery": cql,
    }
