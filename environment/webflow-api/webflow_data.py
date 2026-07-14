"""Data access module for the Webflow API mock service (Data API v2).

Mirrors a subset of api.webflow.com/v2: sites, collections, and CMS collection
items (including item creation). Items carry a `fieldData` object as in the
real v2 API.
"""

import csv
import secrets
from datetime import datetime, timezone
from pathlib import Path

DATA_DIR = Path(__file__).parent

import sys as _sys
_sys.path.insert(0, str(DATA_DIR.parent))
from _mutable_store import (  # noqa: E402
    read_seed_with_ctx, get_store, opt_csv_list, strict_bool)

_store = get_store("webflow-api")
_API = "webflow-api"


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

_store.register("sites", primary_key="id",
                initial_loader=lambda: _coerce_sites(_load("sites.json", "sites")))
_store.register("collections", primary_key="id",
                initial_loader=lambda: _coerce_collections(_load("collections.json", "collections")))
_store.register("items", primary_key="id",
                initial_loader=lambda: _coerce_items(_load("items.json", "items")))


def _sites_rows():
    return _store.table("sites").rows()


def _collections_rows():
    return _store.table("collections").rows()


def _items_rows():
    return _store.table("items").rows()



def _load(filename, table):
    return read_seed_with_ctx(DATA_DIR / filename, _API, table)


def _strip_ctx(r):
    return {k: v for k, v in r.items() if not k.startswith("__")}


def _to_bool(v):
    return str(v).strip().lower() == "true"


def _now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")


def _slugify(value):
    out = []
    for ch in (value or "").lower():
        if ch.isalnum():
            out.append(ch)
        elif ch in " -_":
            out.append("-")
    slug = "".join(out).strip("-")
    while "--" in slug:
        slug = slug.replace("--", "-")
    return slug or "item"


# ---------------------------------------------------------------------------
# Load + coerce
# ---------------------------------------------------------------------------

def _coerce_sites(rows):
    out = []
    for r in rows:
        out.append({
            "id": r["id"],
            "workspace_id": r["workspace_id"],
            "display_name": r["display_name"],
            "short_name": r["short_name"],
            "preview_url": r["preview_url"],
            "time_zone": r["time_zone"],
            "created_on": r["created_on"],
            "last_published": r["last_published"],
            "custom_domains": [d for d in opt_csv_list(r, "custom_domains", sep=";") if d],
        })
    return out


def _coerce_collections(rows):
    out = []
    for r in rows:
        out.append({
            "id": r["id"],
            "site_id": r["site_id"],
            "display_name": r["display_name"],
            "singular_name": r["singular_name"],
            "slug": r["slug"],
            "created_on": r["created_on"],
            "last_updated": r["last_updated"],
        })
    return out


def _coerce_items(rows):
    out = []
    for r in rows:
        out.append({
            "id": r["id"],
            "collection_id": r["collection_id"],
            "name": r["name"],
            "slug": r["slug"],
            "is_draft": strict_bool(r, "is_draft"),
            "is_archived": strict_bool(r, "is_archived"),
            "summary": r["summary"],
            "created_on": r["created_on"],
            "last_updated": r["last_updated"],
        })
    return out








# ---------------------------------------------------------------------------
# Serializers
# ---------------------------------------------------------------------------

def _serialize_site(s):
    return {
        "id": s["id"],
        "workspaceId": s["workspace_id"],
        "displayName": s["display_name"],
        "shortName": s["short_name"],
        "previewUrl": s["preview_url"],
        "timeZone": s["time_zone"],
        "createdOn": s["created_on"],
        "lastPublished": s["last_published"],
        "customDomains": [{"id": secrets.token_hex(8), "url": d} for d in s["custom_domains"]],
    }


def _serialize_collection(c):
    return {
        "id": c["id"],
        "siteId": c["site_id"],
        "displayName": c["display_name"],
        "singularName": c["singular_name"],
        "slug": c["slug"],
        "createdOn": c["created_on"],
        "lastUpdated": c["last_updated"],
    }


def _serialize_item(i):
    return {
        "id": i["id"],
        "cmsLocaleId": None,
        "lastPublished": None,
        "lastUpdated": i["last_updated"],
        "createdOn": i["created_on"],
        "isArchived": i["is_archived"],
        "isDraft": i["is_draft"],
        "fieldData": {
            "name": i["name"],
            "slug": i["slug"],
            "summary": i["summary"],
        },
    }


# ---------------------------------------------------------------------------
# Sites
# ---------------------------------------------------------------------------

def list_sites():
    return {"sites": [_serialize_site(s) for s in _sites_rows()]}


def get_site(site_id):
    s = next((x for x in _sites_rows() if x["id"] == site_id), None)
    if not s:
        return {"error": "not_found", "message": f"Site {site_id} not found"}
    return _serialize_site(s)


# ---------------------------------------------------------------------------
# Collections
# ---------------------------------------------------------------------------

def list_collections(site_id):
    if not any(s["id"] == site_id for s in _sites_rows()):
        return {"error": "not_found", "message": f"Site {site_id} not found"}
    cols = [c for c in _collections_rows() if c["site_id"] == site_id]
    return {"collections": [_serialize_collection(c) for c in cols]}


# ---------------------------------------------------------------------------
# Collection items
# ---------------------------------------------------------------------------

def list_items(collection_id, limit=100, offset=0):
    if not any(c["id"] == collection_id for c in _collections_rows()):
        return {"error": "not_found", "message": f"Collection {collection_id} not found"}
    items = [i for i in _items_rows() if i["collection_id"] == collection_id]
    total = len(items)
    window = items[offset:offset + limit]
    return {
        "items": [_serialize_item(i) for i in window],
        "pagination": {"limit": limit, "offset": offset, "total": total},
    }


def create_item(collection_id, field_data, is_draft=False, is_archived=False):
    if not any(c["id"] == collection_id for c in _collections_rows()):
        return {"error": "not_found", "message": f"Collection {collection_id} not found"}
    field_data = field_data or {}
    name = field_data.get("name") or "Untitled"
    slug = field_data.get("slug") or _slugify(name)
    now = _now_iso()
    item = {
        "id": secrets.token_hex(12),
        "collection_id": collection_id,
        "name": name,
        "slug": slug,
        "is_draft": bool(is_draft),
        "is_archived": bool(is_archived),
        "summary": field_data.get("summary", ""),
        "created_on": now,
        "last_updated": now,
    }
    _store_insert("items", item)
    serialized = _serialize_item(item)
    # Surface any extra custom fields the caller supplied.
    for k, v in field_data.items():
        serialized["fieldData"].setdefault(k, v)
    return serialized

_store.eager_load()
