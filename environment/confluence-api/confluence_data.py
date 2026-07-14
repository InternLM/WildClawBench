"""Data access module for the Confluence Cloud REST API mock service.

Models spaces, pages (content type=page), comments, and labels with
parent/child relationships and version numbers. Mutations are held in
process memory and reset on restart.
"""

import csv
from copy import deepcopy
import uuid
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).parent

import sys as _sys
_sys.path.insert(0, str(DATA_DIR.parent))
from _mutable_store import (
    read_seed_with_ctx, get_store, opt_int, opt_str)

_store = get_store("confluence-api")
_API = "confluence-api"


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

_store.register("spaces", primary_key="id",
                initial_loader=lambda: _coerce_spaces(_load("spaces.json", "spaces")))
_store.register("pages", primary_key="id",
                initial_loader=lambda: _coerce_pages(_load("pages.json", "pages")))
_store.register("comments", primary_key="id",
                initial_loader=lambda: _coerce_comments(_load("comments.json", "comments")))
_store.register("labels", primary_key="id",
                initial_loader=lambda: _coerce_labels(_load("labels.json", "labels")))


def _spaces_rows():
    return _store.table("spaces").rows()


def _pages_rows():
    return _store.table("pages").rows()


def _comments_rows():
    return _store.table("comments").rows()


def _labels_rows():
    return _store.table("labels").rows()


BASE = "/wiki/rest/api"


def _load(filename, table):
    return read_seed_with_ctx(DATA_DIR / filename, _API, table)


def _strip_ctx(r):
    return {k: v for k, v in r.items() if not k.startswith("__")}


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
            "id": opt_int(r, "id", default=0),
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
            "parent_id": opt_str(r, "parent_id", default="") or None,
            "version": opt_int(r, "version", default=1),
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










# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _new_page_id():
    return str(uuid.uuid4().int % 9_000_000 + 1_000_000)


def _find_page(page_id):
    return next((p for p in _pages_rows() if p["id"] == page_id), None)


def _find_space(space_key):
    return next((s for s in _spaces_rows() if s["key"] == space_key), None)


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
        "results": [deepcopy(s) for s in _spaces_rows()[:limit]],
        "size": min(len(_spaces_rows()), limit),
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
    results = [p for p in _pages_rows() if p["type"] == type]
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
    _store_insert("pages", page)
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
    children = [p for p in _pages_rows() if p["parent_id"] == content_id and p["type"] == "page"]
    views = [_content_view(c, expand_body=False) for c in children[:limit]]
    return {"results": views, "size": len(views), "_links": {"base": BASE}}


def list_labels(content_id):
    if not _find_page(content_id):
        return {"error": f"No content with id: {content_id}"}
    labels = [
        {"id": l["id"], "name": l["name"], "prefix": l["prefix"], "label": l["name"]}
        for l in _labels_rows() if l["page_id"] == content_id
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
        for c in _comments_rows() if c["page_id"] == content_id
    ]
    return {"results": comments, "size": len(comments)}


# ---------------------------------------------------------------------------
# Search (simplified CQL)
# ---------------------------------------------------------------------------

def search(cql):
    if not cql:
        return {"error": "cql parameter is required"}
    results = list(_pages_rows())
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

_store.eager_load()
