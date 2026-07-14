"""Data access module for the Figma API mock service.

Mirrors a subset of the Figma REST API: user, teams/projects, files (document
node tree), nodes, comments, and components.
"""

import csv
import json
import uuid
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).parent

import sys as _sys
_sys.path.insert(0, str(DATA_DIR.parent))
from _mutable_store import read_seed_with_ctx, get_store, strict_bool  # noqa: E402

_store = get_store("figma-api")
_API = "figma-api"


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

_store.register("projects", primary_key="project_id",
                initial_loader=lambda: _coerce_projects(_load("projects.json", "projects")))
_store.register("files", primary_key="file_key",
                initial_loader=lambda: _coerce_files(_load("files.json", "files")))
_store.register("components", primary_key="component_key",
                initial_loader=lambda: _coerce_components(_load("components.json", "components")))
_store.register("comments", primary_key="comment_id",
                initial_loader=lambda: _coerce_comments(_load("comments.json", "comments")))
_store.register_document("team", initial_loader=lambda: __import__('json').load(open(DATA_DIR / "team.json", encoding="utf-8")))
_store.register_document("file_nodes", initial_loader=lambda: __import__('json').load(open(DATA_DIR / "file_nodes.json", encoding="utf-8")))


def _projects_rows():
    return _store.table("projects").rows()


def _files_rows():
    return _store.table("files").rows()


def _components_rows():
    return _store.table("components").rows()


def _comments_rows():
    return _store.table("comments").rows()


def _team_doc():
    return _store.document("team").get()


def _file_nodes_doc():
    return _store.document("file_nodes").get()



def _load(filename, table):
    return read_seed_with_ctx(DATA_DIR / filename, _API, table)


def _strip_ctx(r):
    return {k: v for k, v in r.items() if not k.startswith("__")}


def _now():
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


# ---------------------------------------------------------------------------
# Load + coerce
# ---------------------------------------------------------------------------

def _coerce_projects(rows):
    return [_strip_ctx(r) for r in rows]


def _coerce_files(rows):
    return [_strip_ctx(r) for r in rows]


def _coerce_components(rows):
    return [_strip_ctx(r) for r in rows]


def _coerce_comments(rows):
    out = []
    for r in rows:
        out.append({
            **_strip_ctx(r),
            "resolved": strict_bool(r, "resolved"),
        })
    return out








# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _find_file(file_key):
    return next((f for f in _files_rows() if f["file_key"] == file_key), None)


def _iter_nodes(node):
    yield node
    for child in node.get("children", []):
        yield from _iter_nodes(child)


def _user(user_id):
    return next((u for u in _team_doc()["users"] if u["id"] == user_id), None)


# ---------------------------------------------------------------------------
# User / teams / projects
# ---------------------------------------------------------------------------

def get_me():
    return _team_doc()["me"]


def get_team_projects(team_id):
    if team_id != _team_doc()["team"]["id"]:
        return {"error": f"Team {team_id} not found"}
    return {
        "name": _team_doc()["team"]["name"],
        "projects": [
            {"id": p["project_id"], "name": p["name"]}
            for p in _projects_rows() if p["team_id"] == team_id
        ],
    }


def get_project_files(project_id):
    if not any(p["project_id"] == project_id for p in _projects_rows()):
        return {"error": f"Project {project_id} not found"}
    files = [f for f in _files_rows() if f["project_id"] == project_id]
    return {
        "name": next(p["name"] for p in _projects_rows() if p["project_id"] == project_id),
        "files": [
            {
                "key": f["file_key"],
                "name": f["name"],
                "thumbnail_url": f["thumbnail_url"],
                "last_modified": f["last_modified"],
            }
            for f in files
        ],
    }


# ---------------------------------------------------------------------------
# Files / nodes
# ---------------------------------------------------------------------------

def get_file(file_key):
    f = _find_file(file_key)
    if not f:
        return {"error": f"File {file_key} not found"}
    return {
        "name": f["name"],
        "role": f["role"],
        "lastModified": f["last_modified"],
        "editorType": f["editor_type"],
        "thumbnailUrl": f["thumbnail_url"],
        "version": f["version"],
        "document": _file_nodes_doc().get(file_key, {"id": "0:0", "name": "Document", "type": "DOCUMENT", "children": []}),
        "components": {
            c["node_id"]: {"key": c["component_key"], "name": c["name"], "description": c["description"]}
            for c in _components_rows() if c["file_key"] == file_key
        },
    }


def get_file_nodes(file_key, ids):
    f = _find_file(file_key)
    if not f:
        return {"error": f"File {file_key} not found"}
    root = _file_nodes_doc().get(file_key)
    wanted = [i.strip() for i in (ids or "").split(",") if i.strip()]
    nodes = {}
    if root:
        index = {n["id"]: n for n in _iter_nodes(root)}
        for nid in wanted:
            if nid in index:
                nodes[nid] = {"document": index[nid]}
            else:
                nodes[nid] = None
    return {
        "name": f["name"],
        "lastModified": f["last_modified"],
        "version": f["version"],
        "nodes": nodes,
    }


# ---------------------------------------------------------------------------
# Comments
# ---------------------------------------------------------------------------

def _comment_view(c):
    user = _user(c["user_id"]) or {"id": c["user_id"], "handle": c["user_handle"]}
    return {
        "id": c["comment_id"],
        "file_key": c["file_key"],
        "message": c["message"],
        "client_meta": {"node_id": c["node_id"]},
        "user": {"id": user["id"], "handle": user["handle"], "img_url": user.get("img_url")},
        "resolved_at": c.get("created_at") if c["resolved"] else None,
        "created_at": c["created_at"],
    }


def get_comments(file_key):
    f = _find_file(file_key)
    if not f:
        return {"error": f"File {file_key} not found"}
    comments = [_comment_view(c) for c in _comments_rows() if c["file_key"] == file_key]
    return {"comments": comments}


def create_comment(file_key, message, node_id=None, user_id="user-1001"):
    f = _find_file(file_key)
    if not f:
        return {"error": f"File {file_key} not found"}
    user = _user(user_id) or _team_doc()["me"]
    comment = {
        "comment_id": f"cmt-{uuid.uuid4().hex[:8]}",
        "file_key": file_key,
        "user_id": user["id"],
        "user_handle": user["handle"],
        "message": message,
        "node_id": node_id or "",
        "resolved": False,
        "created_at": _now(),
    }
    _store_insert("comments", comment)
    return _comment_view(comment)


# ---------------------------------------------------------------------------
# Components
# ---------------------------------------------------------------------------

def get_components(file_key):
    f = _find_file(file_key)
    if not f:
        return {"error": f"File {file_key} not found"}
    comps = [c for c in _components_rows() if c["file_key"] == file_key]
    return {
        "meta": {
            "components": [
                {
                    "key": c["component_key"],
                    "file_key": c["file_key"],
                    "node_id": c["node_id"],
                    "name": c["name"],
                    "description": c["description"],
                }
                for c in comps
            ]
        }
    }


_store.eager_load()
