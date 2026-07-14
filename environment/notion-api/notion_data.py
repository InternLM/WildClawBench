"""Data access module for the Notion API mock service."""

import csv
import json
import uuid
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).parent

import sys as _sys
_sys.path.insert(0, str(DATA_DIR.parent))
from _mutable_store import (
    read_seed_with_ctx, # noqa: E402
    get_store,
    strict_int,
    strict_bool,
    strict_str,
    opt_bool,
    opt_float,
    opt_str,
)

_store = get_store("notion-api")
_API = "notion-api"



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

_store.register("users", primary_key="id",
                initial_loader=lambda: _coerce_users(_load("users.json", "users")))
_store.register("databases", primary_key="id",
                initial_loader=lambda: _coerce_databases(_load("databases.json", "databases")))
_store.register("pages", primary_key="id",
                initial_loader=lambda: _coerce_pages(_load("pages.json", "pages")))
_store.register("blocks", primary_key="id",
                initial_loader=lambda: _coerce_blocks(_load("blocks.json", "blocks")))
_store.register("comments", primary_key="id",
                initial_loader=lambda: _coerce_comments(_load("comments.json", "comments")))
_store.register_document("properties", initial_loader=lambda: _coerce_properties(_load("page_properties.json", "page_properties")))
_store.register_document("workspace", initial_loader=lambda: __import__('json').load(open(DATA_DIR / "workspace.json", encoding="utf-8")))


def _users_rows():
    return _store.table("users").rows()


def _databases_rows():
    return _store.table("databases").rows()


def _pages_rows():
    return _store.table("pages").rows()


def _blocks_rows():
    return _store.table("blocks").rows()


def _comments_rows():
    return _store.table("comments").rows()


def _properties_doc():
    return _store.document("properties").get()


def _workspace_doc():
    return _store.document("workspace").get()



def _load(filename, table):
    return read_seed_with_ctx(DATA_DIR / filename, _API, table)


def _strip_ctx(r):
    return {k: v for k, v in r.items() if not k.startswith("__")}


def _now():
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000Z")


# ---------------------------------------------------------------------------
# Load + coerce
# ---------------------------------------------------------------------------

def _coerce_users(rows):
    out = []
    for r in rows:
        out.append({
            **_strip_ctx(r),
            "bot": strict_bool(r, "bot"),
            "avatar_url": opt_str(r, "avatar_url", default="") or None,
            "email": opt_str(r, "email", default="") or None,
        })
    return out


def _coerce_databases(rows):
    out = []
    for r in rows:
        out.append({
            **_strip_ctx(r),
            "archived": strict_bool(r, "archived"),
        })
    return out


def _coerce_pages(rows):
    out = []
    for r in rows:
        out.append({
            **_strip_ctx(r),
            "archived": strict_bool(r, "archived"),
            "cover_url": opt_str(r, "cover_url", default="") or None,
        })
    return out


def _coerce_blocks(rows):
    out = []
    for r in rows:
        out.append({
            **_strip_ctx(r),
            "order": strict_int(r, "order"),
            "has_children": strict_bool(r, "has_children"),
            "checked": opt_bool(r, "checked", default=None) if r.get("checked") else None,
            "parent_block_id": opt_str(r, "parent_block_id", default="") or None,
        })
    return out


def _coerce_comments(rows):
    out = []
    for r in rows:
        out.append({
            **_strip_ctx(r),
            "resolved": strict_bool(r, "resolved"),
            "parent_block_id": opt_str(r, "parent_block_id", default="") or None,
        })
    return out


def _coerce_properties(rows):
    # Group by page_id -> {property_name: {type, value}}
    grouped = {}
    for r in rows:
        page_id = strict_str(r, "page_id")
        grouped.setdefault(page_id, {})
        value = strict_str(r, "value")
        # Coerce by type
        ptype = strict_str(r, "property_type")
        if ptype == "number":
            try:
                value = float(value)
            except ValueError:
                pass
        grouped[page_id][strict_str(r, "property_name")] = {
            "type": ptype,
            "value": value,
        }
    return grouped









# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _new_id(prefix):
    return f"{prefix}-{uuid.uuid4().hex[:12]}"


def _attach_properties(page):
    page = dict(page)
    page["properties"] = _properties_doc().get(page["id"], {})
    return page


def _paginate(items, start_cursor=None, page_size=50):
    if start_cursor:
        try:
            offset = int(start_cursor)
        except (TypeError, ValueError):
            offset = 0
    else:
        offset = 0
    page_size = max(1, min(page_size, 100))
    sliced = items[offset: offset + page_size]
    next_cursor = str(offset + page_size) if offset + page_size < len(items) else None
    return {
        "object": "list",
        "results": sliced,
        "next_cursor": next_cursor,
        "has_more": next_cursor is not None,
    }


# ---------------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------------

def list_users(start_cursor=None, page_size=50):
    return _paginate(_users_rows(), start_cursor, page_size)


def get_user(user_id):
    for u in _users_rows():
        if u["id"] == user_id:
            return u
    return {"error": f"User {user_id} not found"}


def get_me():
    # First non-bot user serves as the integration owner
    for u in _users_rows():
        if not u["bot"]:
            return u
    return _users_rows()[0]


# ---------------------------------------------------------------------------
# Workspace / search
# ---------------------------------------------------------------------------

def get_workspace():
    return _workspace_doc()


def search(query=None, filter_value=None, start_cursor=None, page_size=50):
    pool = []
    if filter_value in (None, "page"):
        pool.extend({**_attach_properties(p), "object": "page"} for p in _pages_rows() if not p["archived"])
    if filter_value in (None, "database"):
        pool.extend({**d, "object": "database"} for d in _databases_rows() if not d["archived"])
    if query:
        q = query.lower()
        pool = [p for p in pool if q in p.get("title", "").lower()]
    return _paginate(pool, start_cursor, page_size)


# ---------------------------------------------------------------------------
# Databases
# ---------------------------------------------------------------------------

def get_database(database_id):
    for d in _databases_rows():
        if d["id"] == database_id:
            return d
    return {"error": f"Database {database_id} not found"}


def query_database(database_id, filter_status=None, filter_assignee=None,
                   sort_by=None, start_cursor=None, page_size=50):
    if not any(d["id"] == database_id for d in _databases_rows()):
        return {"error": f"Database {database_id} not found"}
    pages = [p for p in _pages_rows()
             if p["parent_type"] == "database" and p["parent_id"] == database_id and not p["archived"]]
    pages = [_attach_properties(p) for p in pages]

    if filter_status:
        pages = [p for p in pages
                 if p["properties"].get("Status", {}).get("value", "").lower() == filter_status.lower()]
    if filter_assignee:
        pages = [p for p in pages
                 if p["properties"].get("Assignee", {}).get("value") == filter_assignee]
    if sort_by == "last_edited_time":
        pages.sort(key=lambda p: p["last_edited_time"], reverse=True)
    elif sort_by == "created_time":
        pages.sort(key=lambda p: p["created_time"], reverse=True)
    return _paginate(pages, start_cursor, page_size)


# ---------------------------------------------------------------------------
# Pages
# ---------------------------------------------------------------------------

def get_page(page_id):
    for p in _pages_rows():
        if p["id"] == page_id:
            return _attach_properties(p)
    return {"error": f"Page {page_id} not found"}


def create_page(parent_type, parent_id, title, properties=None, created_by="user-amelia"):
    if parent_type == "database":
        if not any(d["id"] == parent_id for d in _databases_rows()):
            return {"error": f"Database {parent_id} not found"}
    elif parent_type == "page":
        if not any(p["id"] == parent_id for p in _pages_rows()):
            return {"error": f"Parent page {parent_id} not found"}
    elif parent_type == "workspace":
        if parent_id != _workspace_doc()["id"]:
            return {"error": f"Workspace {parent_id} not found"}
    else:
        return {"error": f"Unsupported parent_type: {parent_type}"}

    now = _now()
    page = {
        "id": _new_id("page"),
        "parent_type": parent_type,
        "parent_id": parent_id,
        "title": title,
        "created_time": now,
        "last_edited_time": now,
        "created_by": created_by,
        "archived": False,
        "icon": "",
        "cover_url": None,
    }
    _store_insert("pages", page)
    if properties:
        _properties_doc()[page["id"]] = {
            k: ({"type": v.get("type", "rich_text"), "value": v.get("value")}
                if isinstance(v, dict) else {"type": "rich_text", "value": v})
            for k, v in properties.items()
        }
    return _attach_properties(page)


def update_page(page_id, title=None, archived=None, properties=None):
    for p in _pages_rows():
        if p["id"] == page_id:
            _changes = {}
            if title is not None:
                _changes["title"] = title
            if archived is not None:
                _changes["archived"] = bool(archived)
            if properties:
                existing = _properties_doc().setdefault(page_id, {})
                for k, v in properties.items():
                    if isinstance(v, dict):
                        existing[k] = {"type": v.get("type", "rich_text"), "value": v.get("value")}
                    else:
                        existing[k] = {"type": existing.get(k, {}).get("type", "rich_text"), "value": v}
            _changes["last_edited_time"] = _now()
            p.update(_changes)
            _store_patch("pages", p, _changes)
            return _attach_properties(p)
    return {"error": f"Page {page_id} not found"}


def delete_page(page_id):
    return update_page(page_id, archived=True)


# ---------------------------------------------------------------------------
# Blocks
# ---------------------------------------------------------------------------

def list_block_children(block_id, start_cursor=None, page_size=50):
    # block_id can be a page_id (root blocks of a page) or a block_id (nested)
    if any(p["id"] == block_id for p in _pages_rows()):
        children = [b for b in _blocks_rows() if b["page_id"] == block_id and not b["parent_block_id"]]
    else:
        children = [b for b in _blocks_rows() if b["parent_block_id"] == block_id]
    children = sorted(children, key=lambda b: b["order"])
    return _paginate(children, start_cursor, page_size)


def append_block_children(parent_id, blocks):
    if any(p["id"] == parent_id for p in _pages_rows()):
        page_id = parent_id
        parent_block_id = None
        siblings = [b for b in _blocks_rows() if b["page_id"] == page_id and not b["parent_block_id"]]
    else:
        parent_block = next((b for b in _blocks_rows() if b["id"] == parent_id), None)
        if not parent_block:
            return {"error": f"Parent {parent_id} not found"}
        page_id = parent_block["page_id"]
        parent_block_id = parent_id
        siblings = [b for b in _blocks_rows() if b["parent_block_id"] == parent_id]

    next_order = max((b["order"] for b in siblings), default=-1) + 1
    now = _now()
    created = []
    for blk in blocks:
        new_block = {
            "id": _new_id("block"),
            "page_id": page_id,
            "parent_block_id": parent_block_id,
            "type": blk.get("type", "paragraph"),
            "text": blk.get("text", ""),
            "order": next_order,
            "created_time": now,
            "last_edited_time": now,
            "has_children": False,
            "checked": blk.get("checked") if blk.get("type") == "to_do" else None,
        }
        _store_insert("blocks", new_block)
        created.append(new_block)
        next_order += 1
    return {"object": "list", "results": created}


def update_block(block_id, text=None, checked=None):
    for b in _blocks_rows():
        if b["id"] == block_id:
            _changes = {}
            if text is not None:
                _changes["text"] = text
            if checked is not None and b["type"] == "to_do":
                _changes["checked"] = bool(checked)
            _changes["last_edited_time"] = _now()
            b.update(_changes)
            _store_patch("blocks", b, _changes)
            return b
    return {"error": f"Block {block_id} not found"}


def delete_block(block_id):
    for b in _blocks_rows():
        if b["id"] == block_id:
            removed = b
            _store_delete("blocks", b)
            return {"object": "block", "id": block_id, "deleted": True}
    return {"error": f"Block {block_id} not found"}


# ---------------------------------------------------------------------------
# Comments
# ---------------------------------------------------------------------------

def list_comments(block_id=None, page_id=None):
    results = list(_comments_rows())
    if block_id:
        results = [c for c in results if c["parent_block_id"] == block_id]
    if page_id:
        results = [c for c in results if c["parent_page_id"] == page_id]
    return {"object": "list", "results": results}


def create_comment(parent_page_id, parent_block_id, author_id, text):
    if not any(p["id"] == parent_page_id for p in _pages_rows()):
        return {"error": f"Page {parent_page_id} not found"}
    comment = {
        "id": _new_id("comment"),
        "parent_page_id": parent_page_id,
        "parent_block_id": parent_block_id,
        "author_id": author_id,
        "text": text,
        "created_time": _now(),
        "resolved": False,
    }
    _store_insert("comments", comment)
    return comment


_store.eager_load()
