"""Data access module for the Figma API mock service.

Mirrors a subset of the Figma REST API: user, teams/projects, files (document
node tree), nodes, comments, and components.
"""

import csv
import json
import uuid
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


# ---------------------------------------------------------------------------
# Load + coerce
# ---------------------------------------------------------------------------

def _coerce_projects(rows):
    return [dict(r) for r in rows]


def _coerce_files(rows):
    return [dict(r) for r in rows]


def _coerce_components(rows):
    return [dict(r) for r in rows]


def _coerce_comments(rows):
    out = []
    for r in rows:
        out.append({
            **r,
            "resolved": _to_bool(r["resolved"]),
        })
    return out


_projects = _coerce_projects(_load("projects.csv"))
_files = _coerce_files(_load("files.csv"))
_components = _coerce_components(_load("components.csv"))
_comments = _coerce_comments(_load("comments.csv"))

with open(DATA_DIR / "team.json", encoding="utf-8") as _f:
    _team = json.load(_f)
with open(DATA_DIR / "file_nodes.json", encoding="utf-8") as _f:
    _file_nodes = json.load(_f)

_projects_store = deepcopy(_projects)
_files_store = deepcopy(_files)
_components_store = deepcopy(_components)
_comments_store = deepcopy(_comments)
_team_store = deepcopy(_team)
_file_nodes_store = deepcopy(_file_nodes)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _find_file(file_key):
    return next((f for f in _files_store if f["file_key"] == file_key), None)


def _iter_nodes(node):
    yield node
    for child in node.get("children", []):
        yield from _iter_nodes(child)


def _user(user_id):
    return next((u for u in _team_store["users"] if u["id"] == user_id), None)


# ---------------------------------------------------------------------------
# User / teams / projects
# ---------------------------------------------------------------------------

def get_me():
    return _team_store["me"]


def get_team_projects(team_id):
    if team_id != _team_store["team"]["id"]:
        return {"error": f"Team {team_id} not found"}
    return {
        "name": _team_store["team"]["name"],
        "projects": [
            {"id": p["project_id"], "name": p["name"]}
            for p in _projects_store if p["team_id"] == team_id
        ],
    }


def get_project_files(project_id):
    if not any(p["project_id"] == project_id for p in _projects_store):
        return {"error": f"Project {project_id} not found"}
    files = [f for f in _files_store if f["project_id"] == project_id]
    return {
        "name": next(p["name"] for p in _projects_store if p["project_id"] == project_id),
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
        "document": _file_nodes_store.get(file_key, {"id": "0:0", "name": "Document", "type": "DOCUMENT", "children": []}),
        "components": {
            c["node_id"]: {"key": c["component_key"], "name": c["name"], "description": c["description"]}
            for c in _components_store if c["file_key"] == file_key
        },
    }


def get_file_nodes(file_key, ids):
    f = _find_file(file_key)
    if not f:
        return {"error": f"File {file_key} not found"}
    root = _file_nodes_store.get(file_key)
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
    comments = [_comment_view(c) for c in _comments_store if c["file_key"] == file_key]
    return {"comments": comments}


def create_comment(file_key, message, node_id=None, user_id="user-1001"):
    f = _find_file(file_key)
    if not f:
        return {"error": f"File {file_key} not found"}
    user = _user(user_id) or _team_store["me"]
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
    _comments_store.append(comment)
    return _comment_view(comment)


# ---------------------------------------------------------------------------
# Components
# ---------------------------------------------------------------------------

def get_components(file_key):
    f = _find_file(file_key)
    if not f:
        return {"error": f"File {file_key} not found"}
    comps = [c for c in _components_store if c["file_key"] == file_key]
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
