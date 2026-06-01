"""Data access module for the Google Drive API mock service."""

import csv
import json
import re
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


def _coerce_files(rows):
    out = []
    for r in rows:
        out.append({
            **r,
            "size": int(r["size"]) if r["size"] else 0,
            "starred": _to_bool(r["starred"]),
            "trashed": _to_bool(r["trashed"]),
            "parent_id": r["parent_id"] or None,
        })
    return out


_files = _coerce_files(_load("files.csv"))
_permissions = _load("permissions.csv")

with open(DATA_DIR / "about.json", encoding="utf-8") as _f:
    _about = json.load(_f)

_files_store = deepcopy(_files)
_permissions_store = deepcopy(_permissions)
_about_store = deepcopy(_about)


def _new_id(prefix="file"):
    return f"{prefix}-{uuid.uuid4().hex[:10]}"


def _serialize_file(f):
    return {
        "kind": "drive#file",
        "id": f["id"],
        "name": f["name"],
        "mimeType": f["mime_type"],
        "parents": [f["parent_id"]] if f["parent_id"] else [],
        "size": str(f["size"]) if f["size"] else "0",
        "createdTime": f["created_time"],
        "modifiedTime": f["modified_time"],
        "owners": [{"emailAddress": f["owner_email"]}],
        "starred": f["starred"],
        "trashed": f["trashed"],
        "webViewLink": f["web_view_link"] or None,
    }


# ---------------------------------------------------------------------------
# About
# ---------------------------------------------------------------------------

def get_about():
    return _about_store


# ---------------------------------------------------------------------------
# Files
# ---------------------------------------------------------------------------

_Q_TOKEN = re.compile(r"(\w+)\s*=\s*'([^']*)'")


def _matches_query(file, q):
    if not q:
        return True
    # Boolean AND of clauses separated by " and "
    clauses = [c.strip() for c in q.split(" and ")]
    for clause in clauses:
        if not clause:
            continue
        if clause == "trashed = false":
            if file["trashed"]:
                return False
            continue
        if clause == "trashed = true":
            if not file["trashed"]:
                return False
            continue
        if clause == "starred = true":
            if not file["starred"]:
                return False
            continue
        m = _Q_TOKEN.match(clause)
        if m:
            key, val = m.group(1), m.group(2)
            if key == "mimeType" and file["mime_type"] != val:
                return False
            if key == "name" and file["name"] != val:
                return False
            continue
        # "<parent_id>" in parents
        m_in = re.match(r"'([^']*)'\s+in\s+parents", clause)
        if m_in:
            if file["parent_id"] != m_in.group(1):
                return False
            continue
        # name contains 'foo'
        m_contains = re.match(r"name\s+contains\s+'([^']*)'", clause)
        if m_contains:
            if m_contains.group(1).lower() not in file["name"].lower():
                return False
            continue
    return True


def list_files(q="", page_size=100, page_token=None, order_by="modifiedTime desc"):
    results = [f for f in _files_store if _matches_query(f, q)]

    if order_by:
        order_map = {
            "modifiedTime": "modified_time",
            "createdTime": "created_time",
            "name": "name",
        }
        field, _, direction = order_by.partition(" ")
        key = order_map.get(field, "modified_time")
        results.sort(key=lambda f: f[key], reverse=(direction.lower() == "desc"))

    try:
        offset = int(page_token or 0)
    except ValueError:
        offset = 0
    page = results[offset: offset + page_size]
    next_token = str(offset + page_size) if offset + page_size < len(results) else None
    return {
        "kind": "drive#fileList",
        "files": [_serialize_file(f) for f in page],
        "nextPageToken": next_token,
    }


def get_file(file_id):
    for f in _files_store:
        if f["id"] == file_id:
            return _serialize_file(f)
    return {"error": f"File {file_id} not found"}


def create_file(name, mime_type, parent_id=None, owner_email="amelia@orbit-labs.com",
                size=0):
    if parent_id and not any(f["id"] == parent_id for f in _files_store):
        return {"error": f"Parent {parent_id} not found"}
    now = _now()
    new_file = {
        "id": _new_id("file"),
        "name": name,
        "mime_type": mime_type,
        "parent_id": parent_id,
        "size": int(size),
        "created_time": now,
        "modified_time": now,
        "owner_email": owner_email,
        "starred": False,
        "trashed": False,
        "web_view_link": "",
    }
    _files_store.append(new_file)
    _permissions_store.append({
        "id": f"perm-{uuid.uuid4().hex[:6]}",
        "file_id": new_file["id"],
        "type": "user",
        "role": "owner",
        "email": owner_email,
        "display_name": owner_email,
    })
    return _serialize_file(new_file)


def update_file(file_id, name=None, parent_id=None, starred=None, trashed=None):
    for i, f in enumerate(_files_store):
        if f["id"] == file_id:
            if name is not None:
                _files_store[i]["name"] = name
            if parent_id is not None:
                _files_store[i]["parent_id"] = parent_id
            if starred is not None:
                _files_store[i]["starred"] = bool(starred)
            if trashed is not None:
                _files_store[i]["trashed"] = bool(trashed)
            _files_store[i]["modified_time"] = _now()
            return _serialize_file(_files_store[i])
    return {"error": f"File {file_id} not found"}


def trash_file(file_id):
    return update_file(file_id, trashed=True)


def delete_file(file_id):
    for i, f in enumerate(_files_store):
        if f["id"] == file_id:
            _files_store.pop(i)
            _permissions_store[:] = [p for p in _permissions_store if p["file_id"] != file_id]
            return {"deleted": True, "id": file_id}
    return {"error": f"File {file_id} not found"}


# ---------------------------------------------------------------------------
# Permissions
# ---------------------------------------------------------------------------

def list_permissions(file_id):
    if not any(f["id"] == file_id for f in _files_store):
        return {"error": f"File {file_id} not found"}
    perms = [p for p in _permissions_store if p["file_id"] == file_id]
    return {"kind": "drive#permissionList", "permissions": perms}


def create_permission(file_id, type, role, email_address=None, display_name=None):
    if not any(f["id"] == file_id for f in _files_store):
        return {"error": f"File {file_id} not found"}
    perm = {
        "id": f"perm-{uuid.uuid4().hex[:6]}",
        "file_id": file_id,
        "type": type,
        "role": role,
        "email": email_address or "",
        "display_name": display_name or email_address or "",
    }
    _permissions_store.append(perm)
    return perm


def delete_permission(file_id, permission_id):
    for i, p in enumerate(_permissions_store):
        if p["id"] == permission_id and p["file_id"] == file_id:
            _permissions_store.pop(i)
            return {"deleted": True, "id": permission_id}
    return {"error": f"Permission {permission_id} not found on {file_id}"}
