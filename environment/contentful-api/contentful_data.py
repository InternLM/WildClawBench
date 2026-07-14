"""Data access module for the Contentful API mock service.

Models headless-CMS objects (content types, entries, assets) Contentful-style
with a ``sys`` envelope (id/type/contentType) plus a ``fields`` payload.
"""

import csv
from copy import deepcopy
import json
import uuid
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).parent

import sys as _sys
_sys.path.insert(0, str(DATA_DIR.parent))
from _mutable_store import (
    read_seed_with_ctx, get_store,
    opt_int,
)

_store = get_store("contentful-api")
_API = "contentful-api"



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

_store.register("content_types", primary_key="id",
                initial_loader=lambda: _coerce_content_types(_load("content_types.json", "content_types")))
_store.register("entries", primary_key="id",
                initial_loader=lambda: _coerce_entries(_load("entries.json", "entries")))
_store.register("assets", primary_key="id",
                initial_loader=lambda: _coerce_assets(_load("assets.json", "assets")))
_store.register_document("space", initial_loader=lambda: __import__('json').load(open(DATA_DIR / "space.json", encoding="utf-8")))


def _content_types_rows():
    return _store.table("content_types").rows()


def _entries_rows():
    return _store.table("entries").rows()


def _assets_rows():
    return _store.table("assets").rows()


def _space_doc():
    return _store.document("space").get()



def _load(filename, table):
    return read_seed_with_ctx(DATA_DIR / filename, _API, table)


def _strip_ctx(r):
    return {k: v for k, v in r.items() if not k.startswith("__")}


def _now():
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000Z")


def _to_bool(v):
    return str(v).strip().lower() == "true"


def _to_int(v, default=0):
    try:
        return int(v)
    except (TypeError, ValueError):
        return default


def _parse_json(v, default=None):
    if not v:
        return default if default is not None else {}
    return json.loads(v)


# ---------------------------------------------------------------------------
# Load + coerce
# ---------------------------------------------------------------------------

def _coerce_content_types(rows):
    out = []
    for r in rows:
        out.append({
            "id": r["id"],
            "name": r["name"],
            "displayField": r["displayField"],
            "description": r["description"],
            "fields": _parse_json(r["fields_json"], []),
        })
    return out


def _coerce_entries(rows):
    out = []
    for r in rows:
        out.append({
            "id": r["id"],
            "content_type": r["content_type"],
            "created_at": r["created_at"],
            "updated_at": r["updated_at"],
            "published_version": opt_int(r, "published_version", default=0),
            "fields": _parse_json(r["fields_json"], {}),
        })
    return out


def _coerce_assets(rows):
    out = []
    for r in rows:
        out.append({
            "id": r["id"],
            "created_at": r["created_at"],
            "updated_at": r["updated_at"],
            "published_version": opt_int(r, "published_version", default=0),
            "title": r["title"],
            "description": r["description"],
            "file_url": r["file_url"],
            "content_type": r["content_type"],
            "file_name": r["file_name"],
            "size": opt_int(r, "size", default=0),
        })
    return out






# ---------------------------------------------------------------------------
# Serialization (sys envelope)
# ---------------------------------------------------------------------------

def _new_id():
    return uuid.uuid4().hex[:16]


def _content_type_obj(ct):
    return {
        "sys": {"id": ct["id"], "type": "ContentType"},
        "name": ct["name"],
        "displayField": ct["displayField"],
        "description": ct["description"],
        "fields": ct["fields"],
    }


def _entry_obj(e):
    return {
        "sys": {
            "id": e["id"],
            "type": "Entry",
            "createdAt": e["created_at"],
            "updatedAt": e["updated_at"],
            "publishedVersion": e["published_version"],
            "contentType": {
                "sys": {"type": "Link", "linkType": "ContentType", "id": e["content_type"]}
            },
        },
        "fields": deepcopy(e["fields"]),
    }


def _asset_obj(a):
    return {
        "sys": {
            "id": a["id"],
            "type": "Asset",
            "createdAt": a["created_at"],
            "updatedAt": a["updated_at"],
            "publishedVersion": a["published_version"],
        },
        "fields": {
            "title": a["title"],
            "description": a["description"],
            "file": {
                "url": a["file_url"],
                "fileName": a["file_name"],
                "contentType": a["content_type"],
                "details": {"size": a["size"]},
            },
        },
    }


def _collection(items):
    return {
        "sys": {"type": "Array"},
        "total": len(items),
        "skip": 0,
        "limit": len(items),
        "items": items,
    }


# ---------------------------------------------------------------------------
# Content types
# ---------------------------------------------------------------------------

def list_content_types():
    items = [_content_type_obj(ct) for ct in _content_types_rows()]
    return _collection(items)


def get_content_type(content_type_id):
    for ct in _content_types_rows():
        if ct["id"] == content_type_id:
            return _content_type_obj(ct)
    return {"error": f"Content type {content_type_id} not found"}


# ---------------------------------------------------------------------------
# Entries
# ---------------------------------------------------------------------------

def list_entries(content_type=None, field_filters=None, limit=100, skip=0):
    entries = list(_entries_rows())
    if content_type:
        entries = [e for e in entries if e["content_type"] == content_type]
    if field_filters:
        for fname, fvalue in field_filters.items():
            entries = [e for e in entries if str(e["fields"].get(fname)) == str(fvalue)]
    total = len(entries)
    try:
        skip = max(0, int(skip))
    except (TypeError, ValueError):
        skip = 0
    try:
        limit = max(1, min(int(limit), 1000))
    except (TypeError, ValueError):
        limit = 100
    page = entries[skip: skip + limit]
    coll = _collection([_entry_obj(e) for e in page])
    coll["total"] = total
    coll["skip"] = skip
    coll["limit"] = limit
    return coll


def get_entry(entry_id):
    for e in _entries_rows():
        if e["id"] == entry_id:
            return _entry_obj(e)
    return {"error": f"Entry {entry_id} not found"}


def create_entry(content_type, fields):
    if not any(ct["id"] == content_type for ct in _content_types_rows()):
        return {"error": f"Content type {content_type} not found"}
    now = _now()
    entry = {
        "id": _new_id(),
        "content_type": content_type,
        "created_at": now,
        "updated_at": now,
        "published_version": 0,
        "fields": dict(fields or {}),
    }
    _store_insert("entries", entry)
    return _entry_obj(entry)


def update_entry(entry_id, fields):
    for e in _entries_rows():
        if e["id"] == entry_id:
            if fields:
                e["fields"].update(fields)
            e["updated_at"] = _now()
            _store_patch("entries", e, {"fields": e["fields"], "updated_at": e["updated_at"]})
            return _entry_obj(e)
    return {"error": f"Entry {entry_id} not found"}


def delete_entry(entry_id):
    for e in _entries_rows():
        if e["id"] == entry_id:
            _store_delete("entries", e)
            return {"id": entry_id, "deleted": True}
    return {"error": f"Entry {entry_id} not found"}


# ---------------------------------------------------------------------------
# Assets
# ---------------------------------------------------------------------------

def list_assets():
    items = [_asset_obj(a) for a in _assets_rows()]
    return _collection(items)


def get_asset(asset_id):
    for a in _assets_rows():
        if a["id"] == asset_id:
            return _asset_obj(a)
    return {"error": f"Asset {asset_id} not found"}


# ---------------------------------------------------------------------------
# Space
# ---------------------------------------------------------------------------

def get_space():
    return deepcopy(_space_doc())

_store.eager_load()
