"""Data access module for the Dropbox API v2 mock service.

Mirrors a subset of api.dropboxapi.com (v2): users/get_current_account,
files/list_folder, files/get_metadata, files/search_v2, and
sharing/list_shared_links.
"""

import csv
from copy import deepcopy
from pathlib import Path

DATA_DIR = Path(__file__).parent
BLOB_DIR = DATA_DIR / "file_blobs"

import sys as _sys
_sys.path.insert(0, str(DATA_DIR.parent))
from _mutable_store import (
    read_seed_with_ctx, get_store,
    strict_bool,
    opt_int,
    DownloadError, extract_file_content_text, guess_download_mime,
)

_store = get_store("dropbox-api")
_API = "dropbox-api"

_store.register_document("account", initial_loader=lambda: _coerce_account(_load("account.json", "account")))
_store.register("files", primary_key="id",
                initial_loader=lambda: _coerce_files(_load("files.json", "files")))
_store.register("shared_links", primary_key="id",
                initial_loader=lambda: _coerce_shared_links(_load("shared_links.json", "shared_links")))


def _account_doc():
    return _store.document("account").get()


def _files_rows():
    return _store.table("files").rows()


def _shared_links_rows():
    return _store.table("shared_links").rows()



def _load(filename, table):
    return read_seed_with_ctx(DATA_DIR / filename, _API, table)


def _strip_ctx(r):
    return {k: v for k, v in r.items() if not k.startswith("__")}


def _to_bool(v):
    return str(v).strip().lower() == "true"


def _to_int(v):
    try:
        return int(v)
    except (TypeError, ValueError):
        return 0


# ---------------------------------------------------------------------------
# Load + coerce
# ---------------------------------------------------------------------------

def _coerce_account(rows):
    r = rows[0]
    return {
        "account_id": r["account_id"],
        "name": {
            "given_name": r["name_given"],
            "surname": r["name_surname"],
            "display_name": r["name_display"],
            "familiar_name": r["name_given"],
            "abbreviated_name": (r["name_given"][:1] + r["name_surname"][:1]).upper(),
        },
        "email": r["email"],
        "email_verified": strict_bool(r, "email_verified"),
        "country": r["country"],
        "locale": r["locale"],
        "account_type": {".tag": r["account_type"]},
        "is_paired": False,
        "disabled": False,
    }


def _coerce_files(rows):
    out = []
    for r in rows:
        out.append({
            "id": r["id"],
            "name": r["name"],
            "path_lower": r["path_lower"],
            "path_display": r["path_display"],
            "is_folder": strict_bool(r, "is_folder"),
            "size": opt_int(r, "size", default=0),
            "client_modified": r["client_modified"],
            "rev": r["rev"],
        })
    return out


def _coerce_shared_links(rows):
    out = []
    for r in rows:
        out.append({
            "id": r["id"],
            "url": r["url"],
            "name": r["name"],
            "path_lower": r["path_lower"],
            "visibility": r["visibility"],
            "file_id": r["file_id"],
        })
    return out








# ---------------------------------------------------------------------------
# Serializers
# ---------------------------------------------------------------------------

def _serialize_entry(f):
    if f["is_folder"]:
        return {
            ".tag": "folder",
            "id": f["id"],
            "name": f["name"],
            "path_lower": f["path_lower"],
            "path_display": f["path_display"],
        }
    return {
        ".tag": "file",
        "id": f["id"],
        "name": f["name"],
        "path_lower": f["path_lower"],
        "path_display": f["path_display"],
        "size": f["size"],
        "client_modified": f["client_modified"],
        "server_modified": f["client_modified"],
        "rev": f["rev"],
        "is_downloadable": True,
    }


def _serialize_link(s):
    return {
        ".tag": "file",
        "id": s["id"],
        "url": s["url"],
        "name": s["name"],
        "path_lower": s["path_lower"],
        "link_permissions": {
            "resolved_visibility": {".tag": s["visibility"]},
            "can_revoke": True,
        },
    }


def _norm_path(path):
    """Normalize a Dropbox path. Root is '' or '/'; everything else lower-cased."""
    if path in (None, "", "/"):
        return ""
    p = path.lower()
    if not p.startswith("/"):
        p = "/" + p
    return p.rstrip("/")


# ---------------------------------------------------------------------------
# users/get_current_account
# ---------------------------------------------------------------------------

def get_current_account():
    return deepcopy(_account_doc())


# ---------------------------------------------------------------------------
# files/list_folder
# ---------------------------------------------------------------------------

def list_folder(path="", recursive=False):
    parent = _norm_path(path)
    entries = []
    for f in _files_rows():
        child = f["path_lower"]
        if child == parent:
            continue
        if recursive:
            if parent == "" or child.startswith(parent + "/"):
                entries.append(f)
        else:
            # direct children only: the segment before the file's name equals parent
            head, _, _ = child.rpartition("/")
            if head == parent:
                entries.append(f)
    return {
        "entries": [_serialize_entry(f) for f in entries],
        "cursor": "AAH4f99T0taONIb-mock-cursor",
        "has_more": False,
    }


# ---------------------------------------------------------------------------
# files/get_metadata
# ---------------------------------------------------------------------------

def get_metadata(path=None):
    if not path:
        return {"error_summary": "path/not_found/", "error": {".tag": "path"}}
    target = _norm_path(path)
    for f in _files_rows():
        if f["path_lower"] == target or f["id"] == path:
            return _serialize_entry(f)
    return {
        "error_summary": "path/not_found/",
        "error": {".tag": "path", "path": {".tag": "not_found"}},
    }


def download_file_content(path=None):
    if not path:
        raise DownloadError(http_status=400, code="bad_request",
                            message="path is required")
    target = _norm_path(path)
    row = next((f for f in _files_rows()
                if f["path_lower"] == target or f["id"] == path), None)
    if row is None:
        raise DownloadError(http_status=404, code="not_found",
                            message=f"path {path!r} not found")
    if row.get("is_folder"):
        raise DownloadError(http_status=415, code="unsupported_mime",
                            message=f"path {path!r} is a folder")
    name = row["name"]
    mime_type = guess_download_mime(name)
    text = extract_file_content_text(BLOB_DIR, name, mime_type)
    return {
        "file_id": row["id"],
        "name": name,
        "path_display": row["path_display"],
        "mime_type": mime_type,
        "size_bytes": len(text.encode("utf-8")),
        "content": text,
    }


# ---------------------------------------------------------------------------
# files/search_v2
# ---------------------------------------------------------------------------

def search_v2(query=None, path=""):
    q = (query or "").lower()
    scope = _norm_path(path)
    matches = []
    for f in _files_rows():
        if scope and not (f["path_lower"] == scope or f["path_lower"].startswith(scope + "/")):
            continue
        if q and q not in f["name"].lower():
            continue
        matches.append(f)
    return {
        "matches": [
            {
                "match_type": {".tag": "filename"},
                "metadata": {".tag": "metadata", "metadata": _serialize_entry(f)},
            }
            for f in matches
        ],
        "has_more": False,
    }


# ---------------------------------------------------------------------------
# sharing/list_shared_links
# ---------------------------------------------------------------------------

def list_shared_links(path=None):
    links = _shared_links_rows()
    if path:
        target = _norm_path(path)
        links = [s for s in links if s["path_lower"] == target]
    return {
        "links": [_serialize_link(s) for s in links],
        "has_more": False,
    }

_store.eager_load()
