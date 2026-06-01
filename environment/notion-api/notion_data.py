"""Data access module for the Notion API mock service."""

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
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000Z")


def _to_bool(v):
    return str(v).strip().lower() == "true"


# ---------------------------------------------------------------------------
# Load + coerce
# ---------------------------------------------------------------------------

def _coerce_users(rows):
    out = []
    for r in rows:
        out.append({
            **r,
            "bot": _to_bool(r["bot"]),
            "avatar_url": r["avatar_url"] or None,
            "email": r["email"] or None,
        })
    return out


def _coerce_databases(rows):
    out = []
    for r in rows:
        out.append({
            **r,
            "archived": _to_bool(r["archived"]),
        })
    return out


def _coerce_pages(rows):
    out = []
    for r in rows:
        out.append({
            **r,
            "archived": _to_bool(r["archived"]),
            "cover_url": r["cover_url"] or None,
        })
    return out


def _coerce_blocks(rows):
    out = []
    for r in rows:
        out.append({
            **r,
            "order": int(r["order"]),
            "has_children": _to_bool(r["has_children"]),
            "checked": _to_bool(r["checked"]) if r.get("checked") else None,
            "parent_block_id": r["parent_block_id"] or None,
        })
    return out


def _coerce_comments(rows):
    out = []
    for r in rows:
        out.append({
            **r,
            "resolved": _to_bool(r["resolved"]),
            "parent_block_id": r["parent_block_id"] or None,
        })
    return out


def _coerce_properties(rows):
    # Group by page_id -> {property_name: {type, value}}
    grouped = {}
    for r in rows:
        page_id = r["page_id"]
        grouped.setdefault(page_id, {})
        value = r["value"]
        # Coerce by type
        ptype = r["property_type"]
        if ptype == "number":
            try:
                value = float(value)
            except ValueError:
                pass
        grouped[page_id][r["property_name"]] = {
            "type": ptype,
            "value": value,
        }
    return grouped


_users = _coerce_users(_load("users.csv"))
_databases = _coerce_databases(_load("databases.csv"))
_pages = _coerce_pages(_load("pages.csv"))
_blocks = _coerce_blocks(_load("blocks.csv"))
_comments = _coerce_comments(_load("comments.csv"))
_properties = _coerce_properties(_load("page_properties.csv"))

with open(DATA_DIR / "workspace.json", encoding="utf-8") as _f:
    _workspace = json.load(_f)

_users_store = deepcopy(_users)
_databases_store = deepcopy(_databases)
_pages_store = deepcopy(_pages)
_blocks_store = deepcopy(_blocks)
_comments_store = deepcopy(_comments)
_properties_store = deepcopy(_properties)
_workspace_store = deepcopy(_workspace)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _new_id(prefix):
    return f"{prefix}-{uuid.uuid4().hex[:12]}"


def _attach_properties(page):
    page = dict(page)
    page["properties"] = _properties_store.get(page["id"], {})
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
    return _paginate(_users_store, start_cursor, page_size)


def get_user(user_id):
    for u in _users_store:
        if u["id"] == user_id:
            return u
    return {"error": f"User {user_id} not found"}


def get_me():
    # First non-bot user serves as the integration owner
    for u in _users_store:
        if not u["bot"]:
            return u
    return _users_store[0]


# ---------------------------------------------------------------------------
# Workspace / search
# ---------------------------------------------------------------------------

def get_workspace():
    return _workspace_store


def search(query=None, filter_value=None, start_cursor=None, page_size=50):
    pool = []
    if filter_value in (None, "page"):
        pool.extend({**_attach_properties(p), "object": "page"} for p in _pages_store if not p["archived"])
    if filter_value in (None, "database"):
        pool.extend({**d, "object": "database"} for d in _databases_store if not d["archived"])
    if query:
        q = query.lower()
        pool = [p for p in pool if q in p.get("title", "").lower()]
    return _paginate(pool, start_cursor, page_size)


# ---------------------------------------------------------------------------
# Databases
# ---------------------------------------------------------------------------

def get_database(database_id):
    for d in _databases_store:
        if d["id"] == database_id:
            return d
    return {"error": f"Database {database_id} not found"}


def query_database(database_id, filter_status=None, filter_assignee=None,
                   sort_by=None, start_cursor=None, page_size=50):
    if not any(d["id"] == database_id for d in _databases_store):
        return {"error": f"Database {database_id} not found"}
    pages = [p for p in _pages_store
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
    for p in _pages_store:
        if p["id"] == page_id:
            return _attach_properties(p)
    return {"error": f"Page {page_id} not found"}


def create_page(parent_type, parent_id, title, properties=None, created_by="user-amelia"):
    if parent_type == "database":
        if not any(d["id"] == parent_id for d in _databases_store):
            return {"error": f"Database {parent_id} not found"}
    elif parent_type == "page":
        if not any(p["id"] == parent_id for p in _pages_store):
            return {"error": f"Parent page {parent_id} not found"}
    elif parent_type == "workspace":
        if parent_id != _workspace_store["id"]:
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
    _pages_store.append(page)
    if properties:
        _properties_store[page["id"]] = {
            k: ({"type": v.get("type", "rich_text"), "value": v.get("value")}
                if isinstance(v, dict) else {"type": "rich_text", "value": v})
            for k, v in properties.items()
        }
    return _attach_properties(page)


def update_page(page_id, title=None, archived=None, properties=None):
    for i, p in enumerate(_pages_store):
        if p["id"] == page_id:
            if title is not None:
                _pages_store[i]["title"] = title
            if archived is not None:
                _pages_store[i]["archived"] = bool(archived)
            if properties:
                existing = _properties_store.setdefault(page_id, {})
                for k, v in properties.items():
                    if isinstance(v, dict):
                        existing[k] = {"type": v.get("type", "rich_text"), "value": v.get("value")}
                    else:
                        existing[k] = {"type": existing.get(k, {}).get("type", "rich_text"), "value": v}
            _pages_store[i]["last_edited_time"] = _now()
            return _attach_properties(_pages_store[i])
    return {"error": f"Page {page_id} not found"}


def delete_page(page_id):
    return update_page(page_id, archived=True)


# ---------------------------------------------------------------------------
# Blocks
# ---------------------------------------------------------------------------

def list_block_children(block_id, start_cursor=None, page_size=50):
    # block_id can be a page_id (root blocks of a page) or a block_id (nested)
    if any(p["id"] == block_id for p in _pages_store):
        children = [b for b in _blocks_store if b["page_id"] == block_id and not b["parent_block_id"]]
    else:
        children = [b for b in _blocks_store if b["parent_block_id"] == block_id]
    children = sorted(children, key=lambda b: b["order"])
    return _paginate(children, start_cursor, page_size)


def append_block_children(parent_id, blocks):
    if any(p["id"] == parent_id for p in _pages_store):
        page_id = parent_id
        parent_block_id = None
        siblings = [b for b in _blocks_store if b["page_id"] == page_id and not b["parent_block_id"]]
    else:
        parent_block = next((b for b in _blocks_store if b["id"] == parent_id), None)
        if not parent_block:
            return {"error": f"Parent {parent_id} not found"}
        page_id = parent_block["page_id"]
        parent_block_id = parent_id
        siblings = [b for b in _blocks_store if b["parent_block_id"] == parent_id]

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
        _blocks_store.append(new_block)
        created.append(new_block)
        next_order += 1
    return {"object": "list", "results": created}


def update_block(block_id, text=None, checked=None):
    for i, b in enumerate(_blocks_store):
        if b["id"] == block_id:
            if text is not None:
                _blocks_store[i]["text"] = text
            if checked is not None and b["type"] == "to_do":
                _blocks_store[i]["checked"] = bool(checked)
            _blocks_store[i]["last_edited_time"] = _now()
            return _blocks_store[i]
    return {"error": f"Block {block_id} not found"}


def delete_block(block_id):
    for i, b in enumerate(_blocks_store):
        if b["id"] == block_id:
            removed = _blocks_store.pop(i)
            return {"object": "block", "id": block_id, "deleted": True}
    return {"error": f"Block {block_id} not found"}


# ---------------------------------------------------------------------------
# Comments
# ---------------------------------------------------------------------------

def list_comments(block_id=None, page_id=None):
    results = list(_comments_store)
    if block_id:
        results = [c for c in results if c["parent_block_id"] == block_id]
    if page_id:
        results = [c for c in results if c["parent_page_id"] == page_id]
    return {"object": "list", "results": results}


def create_comment(parent_page_id, parent_block_id, author_id, text):
    if not any(p["id"] == parent_page_id for p in _pages_store):
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
    _comments_store.append(comment)
    return comment
