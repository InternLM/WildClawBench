"""Data access module for the Box API mock service.

Mirrors a subset of the Box Content API (api.box.com/2.0): users/me, folders,
folder items, files, and search. Uses Box-style `entries`/`total_count`
envelopes.
"""

import csv
from pathlib import Path

DATA_DIR = Path(__file__).parent
# File-content download fixtures live in `file_blobs/` next to the JSON
# seeds; basenames must match the `name` column of `files.json`. Bind-mount
# overlay path in mock_stack: /opt/mocks/box-api/file_blobs/<basename>.
# Per-task overrides via eval/run_batch.py:393-405 staging the same
# subpath under input/<task>/mock_data/box-api/file_blobs/<basename>.
BLOB_DIR = DATA_DIR / "file_blobs"

import sys as _sys
_sys.path.insert(0, str(DATA_DIR.parent))
from _mutable_store import (
    read_seed_with_ctx, get_store,
    opt_int,
    DownloadError, extract_file_content_text, guess_download_mime,
)

_store = get_store("box-api")
_API = "box-api"

_store.register("users", primary_key="id",
                initial_loader=lambda: _coerce_users(_load("users.json", "users")))
_store.register("folders", primary_key="id",
                initial_loader=lambda: _coerce_folders(_load("folders.json", "folders")))
_store.register("files", primary_key="id",
                initial_loader=lambda: _coerce_files(_load("files.json", "files")))


def _users_rows():
    return _store.table("users").rows()


def _folders_rows():
    return _store.table("folders").rows()


def _files_rows():
    return _store.table("files").rows()



def _load(filename, table):
    return read_seed_with_ctx(DATA_DIR / filename, _API, table)


def _strip_ctx(r):
    return {k: v for k, v in r.items() if not k.startswith("__")}


def _to_int(v):
    try:
        return int(v)
    except (TypeError, ValueError):
        return 0


# The user whose token is used (the "me" of /2.0/users/me).
_ME = "11446498"


# ---------------------------------------------------------------------------
# Load + coerce
# ---------------------------------------------------------------------------

def _coerce_users(rows):
    out = []
    for r in rows:
        out.append({
            "id": r["id"],
            "name": r["name"],
            "login": r["login"],
            "role": r["role"],
            "status": r["status"],
            "language": r["language"],
            "timezone": r["timezone"],
            "space_amount": opt_int(r, "space_amount", default=0),
            "space_used": opt_int(r, "space_used", default=0),
            "max_upload_size": opt_int(r, "max_upload_size", default=0),
            "job_title": r["job_title"],
            "phone": r["phone"],
            "created_at": r["created_at"],
        })
    return out


def _coerce_folders(rows):
    out = []
    for r in rows:
        out.append({
            "id": r["id"],
            "name": r["name"],
            "parent_id": r["parent_id"],
            "owner_id": r["owner_id"],
            "description": r["description"],
            "created_at": r["created_at"],
            "modified_at": r["modified_at"],
            "item_count": opt_int(r, "item_count", default=0),
        })
    return out


def _coerce_files(rows):
    out = []
    for r in rows:
        out.append({
            "id": r["id"],
            "name": r["name"],
            "parent_id": r["parent_id"],
            "owner_id": r["owner_id"],
            "description": r["description"],
            "size": opt_int(r, "size", default=0),
            "extension": r["extension"],
            "sha1": r["sha1"],
            "created_at": r["created_at"],
            "modified_at": r["modified_at"],
        })
    return out








# ---------------------------------------------------------------------------
# Serializers
# ---------------------------------------------------------------------------

def _user_mini(user_id):
    u = next((x for x in _users_rows() if x["id"] == user_id), None)
    if not u:
        return None
    return {"type": "user", "id": u["id"], "name": u["name"], "login": u["login"]}


def _folder_mini(folder_id):
    f = next((x for x in _folders_rows() if x["id"] == folder_id), None)
    if not f:
        return None
    return {"type": "folder", "id": f["id"], "name": f["name"]}


def _serialize_user(u):
    return {
        "type": "user",
        "id": u["id"],
        "name": u["name"],
        "login": u["login"],
        "role": u["role"],
        "status": u["status"],
        "language": u["language"],
        "timezone": u["timezone"],
        "space_amount": u["space_amount"],
        "space_used": u["space_used"],
        "max_upload_size": u["max_upload_size"],
        "job_title": u["job_title"],
        "phone": u["phone"],
        "created_at": u["created_at"],
    }


def _serialize_folder(f):
    return {
        "type": "folder",
        "id": f["id"],
        "name": f["name"],
        "description": f["description"],
        "size": sum(x["size"] for x in _files_rows() if x["parent_id"] == f["id"]),
        "created_at": f["created_at"],
        "modified_at": f["modified_at"],
        "item_count": f["item_count"],
        "parent": _folder_mini(f["parent_id"]) if f["parent_id"] else None,
        "owned_by": _user_mini(f["owner_id"]),
    }


def _serialize_file(f):
    return {
        "type": "file",
        "id": f["id"],
        "name": f["name"],
        "description": f["description"],
        "size": f["size"],
        "extension": f["extension"],
        "sha1": f["sha1"],
        "created_at": f["created_at"],
        "modified_at": f["modified_at"],
        "parent": _folder_mini(f["parent_id"]),
        "owned_by": _user_mini(f["owner_id"]),
    }


# ---------------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------------

def get_me():
    u = next((x for x in _users_rows() if x["id"] == _ME), _users_rows()[0])
    return _serialize_user(u)


# ---------------------------------------------------------------------------
# Folders
# ---------------------------------------------------------------------------

def get_folder(folder_id):
    f = next((x for x in _folders_rows() if x["id"] == str(folder_id)), None)
    if not f:
        return {"error": "not_found", "type": "error", "status": 404,
                "code": "not_found", "message": f"Folder {folder_id} not found"}
    return _serialize_folder(f)


def get_folder_items(folder_id, limit=100, offset=0):
    if not any(x["id"] == str(folder_id) for x in _folders_rows()):
        return {"error": "not_found", "type": "error", "status": 404,
                "code": "not_found", "message": f"Folder {folder_id} not found"}
    folders = [_serialize_folder(x) for x in _folders_rows()
               if x["parent_id"] == str(folder_id)]
    files = [_serialize_file(x) for x in _files_rows()
             if x["parent_id"] == str(folder_id)]
    entries = folders + files
    total = len(entries)
    page = entries[offset:offset + limit]
    return {
        "total_count": total,
        "entries": page,
        "offset": offset,
        "limit": limit,
    }


# ---------------------------------------------------------------------------
# Files
# ---------------------------------------------------------------------------

def get_file(file_id):
    f = next((x for x in _files_rows() if x["id"] == str(file_id)), None)
    if not f:
        return {"error": "not_found", "type": "error", "status": 404,
                "code": "not_found", "message": f"File {file_id} not found"}
    return _serialize_file(f)


def download_file_content(file_id):
    """Return raw text content for box file `file_id`.

    Returns a dict with `{file_id, name, mime_type, size_bytes, content}` on
    success. Raises `DownloadError` on 404/415/413; the route handler
    translates the exception into a Box-style error envelope. Mime is
    resolved via `guess_download_mime(name)` because Box's seed rows
    have no explicit mime column; allow-list lives in `_mutable_store.py`.
    """
    f = next((x for x in _files_rows() if x["id"] == str(file_id)), None)
    if not f:
        raise DownloadError(http_status=404, code="not_found",
                            message=f"File {file_id} not found")
    name = f["name"]
    mime_type = guess_download_mime(name)
    text = extract_file_content_text(BLOB_DIR, name, mime_type)
    return {
        "file_id": str(file_id),
        "name": name,
        "mime_type": mime_type,
        "size_bytes": len(text.encode("utf-8")),
        "content": text,
    }


# ---------------------------------------------------------------------------
# Search
# ---------------------------------------------------------------------------

def search(query=None, type_filter=None, limit=100, offset=0):
    q = (query or "").lower()
    entries = []
    if type_filter in (None, "folder"):
        for f in _folders_rows():
            if q in f["name"].lower():
                entries.append(_serialize_folder(f))
    if type_filter in (None, "file"):
        for f in _files_rows():
            if q in f["name"].lower():
                entries.append(_serialize_file(f))
    total = len(entries)
    page = entries[offset:offset + limit]
    return {
        "total_count": total,
        "entries": page,
        "offset": offset,
        "limit": limit,
    }

_store.eager_load()
