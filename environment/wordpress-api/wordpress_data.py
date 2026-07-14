"""Data access module for the WordPress REST API mock service.

Mirrors a subset of the wp/v2 surface.
"""

import csv
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).parent

import sys as _sys
_sys.path.insert(0, str(DATA_DIR.parent))
from _mutable_store import (  # noqa: E402
    read_seed_with_ctx, get_store,
    strict_int, opt_int,
)

_store = get_store("wordpress-api")
_API = "wordpress-api"



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

_store.register("posts", primary_key="id",
                initial_loader=lambda: _coerce_posts(_load("posts.json", "posts")))
_store.register("pages", primary_key="id",
                initial_loader=lambda: _coerce_pages(_load("pages.json", "pages")))
_store.register("categories", primary_key="id",
                initial_loader=lambda: _coerce_categories(_load("categories.json", "categories")))
_store.register("tags", primary_key="id",
                initial_loader=lambda: _coerce_tags(_load("tags.json", "tags")))
_store.register("comments", primary_key="id",
                initial_loader=lambda: _coerce_comments(_load("comments.json", "comments")))
_store.register("media", primary_key="id",
                initial_loader=lambda: _coerce_media(_load("media.json", "media")))
_store.register("users", primary_key="id",
                initial_loader=lambda: _coerce_users(_load("users.json", "users")))


def _posts_rows():
    return _store.table("posts").rows()


def _pages_rows():
    return _store.table("pages").rows()


def _categories_rows():
    return _store.table("categories").rows()


def _tags_rows():
    return _store.table("tags").rows()


def _comments_rows():
    return _store.table("comments").rows()


def _media_rows():
    return _store.table("media").rows()


def _users_rows():
    return _store.table("users").rows()



def _load(filename, table):
    return read_seed_with_ctx(DATA_DIR / filename, _API, table)


def _strip_ctx(r):
    return {k: v for k, v in r.items() if not k.startswith("__")}


def _now():
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")


def _split_ids(s):
    return [int(x) for x in (s or "").split(";") if x.strip()]


def _rendered(text):
    return {"rendered": text}


# ---------------------------------------------------------------------------
# Load + coerce
# ---------------------------------------------------------------------------

def _coerce_posts(rows):
    out = []
    for r in rows:
        out.append({
            "id": strict_int(r, "id"),
            "title": _rendered(r["title"]),
            "slug": r["slug"],
            "status": r["status"],
            "author": strict_int(r, "author"),
            "content": _rendered(r["content"]),
            "excerpt": _rendered(r["excerpt"]),
            "categories": _split_ids(r["category_ids"]),
            "tags": _split_ids(r["tag_ids"]),
            "comment_status": r["comment_status"],
            "date": r["date"],
            "modified": r["modified"],
            "type": "post",
        })
    return out


def _coerce_pages(rows):
    out = []
    for r in rows:
        out.append({
            "id": strict_int(r, "id"),
            "title": _rendered(r["title"]),
            "slug": r["slug"],
            "status": r["status"],
            "author": strict_int(r, "author"),
            "content": _rendered(r["content"]),
            "date": r["date"],
            "modified": r["modified"],
            "parent": strict_int(r, "parent"),
            "type": "page",
        })
    return out


def _coerce_categories(rows):
    out = []
    for r in rows:
        out.append({
            "id": strict_int(r, "id"),
            "name": r["name"],
            "slug": r["slug"],
            "description": r["description"],
            "parent": strict_int(r, "parent"),
            "count": strict_int(r, "count"),
            "taxonomy": "category",
        })
    return out


def _coerce_tags(rows):
    out = []
    for r in rows:
        out.append({
            "id": strict_int(r, "id"),
            "name": r["name"],
            "slug": r["slug"],
            "description": r["description"],
            "count": strict_int(r, "count"),
            "taxonomy": "post_tag",
        })
    return out


def _coerce_comments(rows):
    out = []
    for r in rows:
        out.append({
            "id": strict_int(r, "id"),
            "post": strict_int(r, "post"),
            "author_name": r["author_name"],
            "author_email": r["author_email"],
            "content": _rendered(r["content"]),
            "status": r["status"],
            "date": r["date"],
            "parent": strict_int(r, "parent"),
        })
    return out


def _coerce_media(rows):
    out = []
    for r in rows:
        out.append({
            "id": strict_int(r, "id"),
            "title": _rendered(r["title"]),
            "slug": r["slug"],
            "media_type": r["media_type"],
            "mime_type": r["mime_type"],
            "source_url": r["source_url"],
            "alt_text": r["alt_text"],
            "author": strict_int(r, "author"),
            "post": opt_int(r, "post", default=None) or None,
            "date": r["date"],
            "type": "attachment",
        })
    return out


def _coerce_users(rows):
    out = []
    for r in rows:
        out.append({
            "id": strict_int(r, "id"),
            "name": r["name"],
            "slug": r["slug"],
            "description": r["description"],
            "url": r["url"],
            "roles": [r["roles"]],
            "avatar_urls": {"96": r["avatar_url"]},
        })
    return out
















def _next_id(store):
    return max((item["id"] for item in store), default=0) + 1


# ---------------------------------------------------------------------------
# Posts
# ---------------------------------------------------------------------------

def list_posts(status=None, author=None, search=None, category=None, per_page=10):
    posts = list(_posts_rows())
    # Default WP behavior: only published posts unless a status is requested.
    posts = [p for p in posts if p["status"] == (status or "publish")]
    if author:
        posts = [p for p in posts if p["author"] == int(author)]
    if category:
        posts = [p for p in posts if int(category) in p["categories"]]
    if search:
        q = search.lower()
        posts = [p for p in posts
                 if q in p["title"]["rendered"].lower() or q in p["content"]["rendered"].lower()]
    posts.sort(key=lambda p: p["date"], reverse=True)
    return posts[:per_page]


def get_post(post_id):
    for p in _posts_rows():
        if p["id"] == int(post_id):
            return p
    return {"error": f"Post {post_id} not found", "code": "rest_post_invalid_id"}


def create_post(title, content, status="draft", author=1, excerpt="",
                categories=None, tags=None):
    now = _now()
    post = {
        "id": _next_id(_posts_rows()),
        "title": _rendered(title),
        "slug": title.lower().replace(" ", "-")[:60],
        "status": status,
        "author": int(author),
        "content": _rendered(content),
        "excerpt": _rendered(excerpt),
        "categories": [int(c) for c in (categories or [])],
        "tags": [int(t) for t in (tags or [])],
        "comment_status": "open",
        "date": now,
        "modified": now,
        "type": "post",
    }
    _store_insert("posts", post)
    return post


def update_post(post_id, title=None, content=None, status=None, excerpt=None,
                categories=None, tags=None):
    for p in _posts_rows():
        if p["id"] == int(post_id):
            _changes = {}
            if title is not None:
                _changes["title"] = _rendered(title)
            if content is not None:
                _changes["content"] = _rendered(content)
            if excerpt is not None:
                _changes["excerpt"] = _rendered(excerpt)
            if status is not None:
                _changes["status"] = status
            if categories is not None:
                _changes["categories"] = [int(c) for c in categories]
            if tags is not None:
                _changes["tags"] = [int(t) for t in tags]
            _changes["modified"] = _now()
            p.update(_changes)
            _store_patch("posts", p, _changes)
            return p
    return {"error": f"Post {post_id} not found", "code": "rest_post_invalid_id"}


def delete_post(post_id):
    for p in _posts_rows():
        if p["id"] == int(post_id):
            removed = p
            _store_delete("posts", p)
            return {"deleted": True, "previous": removed}
    return {"error": f"Post {post_id} not found", "code": "rest_post_invalid_id"}


# ---------------------------------------------------------------------------
# Pages
# ---------------------------------------------------------------------------

def list_pages(status="publish", per_page=10):
    pages = [p for p in _pages_rows() if p["status"] == status]
    pages.sort(key=lambda p: p["date"], reverse=True)
    return pages[:per_page]


# ---------------------------------------------------------------------------
# Taxonomies
# ---------------------------------------------------------------------------

def list_categories():
    return list(_categories_rows())


def list_tags():
    return list(_tags_rows())


# ---------------------------------------------------------------------------
# Comments
# ---------------------------------------------------------------------------

def list_comments(post=None, status="approved"):
    comments = [c for c in _comments_rows() if c["status"] == status]
    if post is not None:
        comments = [c for c in comments if c["post"] == int(post)]
    comments.sort(key=lambda c: c["date"])
    return comments


def create_comment(post, author_name, author_email, content, parent=0):
    if not any(p["id"] == int(post) for p in _posts_rows()):
        return {"error": f"Post {post} not found", "code": "rest_comment_invalid_post_id"}
    comment = {
        "id": _next_id(_comments_rows()),
        "post": int(post),
        "author_name": author_name,
        "author_email": author_email,
        "content": _rendered(content),
        "status": "approved",
        "date": _now(),
        "parent": int(parent),
    }
    _store_insert("comments", comment)
    return comment


# ---------------------------------------------------------------------------
# Media / users
# ---------------------------------------------------------------------------

def list_media():
    return list(_media_rows())


def list_users():
    return list(_users_rows())

_store.eager_load()
