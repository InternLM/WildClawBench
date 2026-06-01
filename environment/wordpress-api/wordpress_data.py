"""Data access module for the WordPress REST API mock service.

Mirrors a subset of the wp/v2 surface.
"""

import csv
from copy import deepcopy
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).parent


def _load(filename):
    with open(DATA_DIR / filename, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


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
            "id": int(r["id"]),
            "title": _rendered(r["title"]),
            "slug": r["slug"],
            "status": r["status"],
            "author": int(r["author"]),
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
            "id": int(r["id"]),
            "title": _rendered(r["title"]),
            "slug": r["slug"],
            "status": r["status"],
            "author": int(r["author"]),
            "content": _rendered(r["content"]),
            "date": r["date"],
            "modified": r["modified"],
            "parent": int(r["parent"]),
            "type": "page",
        })
    return out


def _coerce_categories(rows):
    out = []
    for r in rows:
        out.append({
            "id": int(r["id"]),
            "name": r["name"],
            "slug": r["slug"],
            "description": r["description"],
            "parent": int(r["parent"]),
            "count": int(r["count"]),
            "taxonomy": "category",
        })
    return out


def _coerce_tags(rows):
    out = []
    for r in rows:
        out.append({
            "id": int(r["id"]),
            "name": r["name"],
            "slug": r["slug"],
            "description": r["description"],
            "count": int(r["count"]),
            "taxonomy": "post_tag",
        })
    return out


def _coerce_comments(rows):
    out = []
    for r in rows:
        out.append({
            "id": int(r["id"]),
            "post": int(r["post"]),
            "author_name": r["author_name"],
            "author_email": r["author_email"],
            "content": _rendered(r["content"]),
            "status": r["status"],
            "date": r["date"],
            "parent": int(r["parent"]),
        })
    return out


def _coerce_media(rows):
    out = []
    for r in rows:
        out.append({
            "id": int(r["id"]),
            "title": _rendered(r["title"]),
            "slug": r["slug"],
            "media_type": r["media_type"],
            "mime_type": r["mime_type"],
            "source_url": r["source_url"],
            "alt_text": r["alt_text"],
            "author": int(r["author"]),
            "post": int(r["post"]) if r["post"] and r["post"] != "0" else None,
            "date": r["date"],
            "type": "attachment",
        })
    return out


def _coerce_users(rows):
    out = []
    for r in rows:
        out.append({
            "id": int(r["id"]),
            "name": r["name"],
            "slug": r["slug"],
            "description": r["description"],
            "url": r["url"],
            "roles": [r["roles"]],
            "avatar_urls": {"96": r["avatar_url"]},
        })
    return out


_posts = _coerce_posts(_load("posts.csv"))
_pages = _coerce_pages(_load("pages.csv"))
_categories = _coerce_categories(_load("categories.csv"))
_tags = _coerce_tags(_load("tags.csv"))
_comments = _coerce_comments(_load("comments.csv"))
_media = _coerce_media(_load("media.csv"))
_users = _coerce_users(_load("users.csv"))

_posts_store = deepcopy(_posts)
_pages_store = deepcopy(_pages)
_categories_store = deepcopy(_categories)
_tags_store = deepcopy(_tags)
_comments_store = deepcopy(_comments)
_media_store = deepcopy(_media)
_users_store = deepcopy(_users)


def _next_id(store):
    return max((item["id"] for item in store), default=0) + 1


# ---------------------------------------------------------------------------
# Posts
# ---------------------------------------------------------------------------

def list_posts(status=None, author=None, search=None, category=None, per_page=10):
    posts = list(_posts_store)
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
    for p in _posts_store:
        if p["id"] == int(post_id):
            return p
    return {"error": f"Post {post_id} not found", "code": "rest_post_invalid_id"}


def create_post(title, content, status="draft", author=1, excerpt="",
                categories=None, tags=None):
    now = _now()
    post = {
        "id": _next_id(_posts_store),
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
    _posts_store.append(post)
    return post


def update_post(post_id, title=None, content=None, status=None, excerpt=None,
                categories=None, tags=None):
    for p in _posts_store:
        if p["id"] == int(post_id):
            if title is not None:
                p["title"] = _rendered(title)
            if content is not None:
                p["content"] = _rendered(content)
            if excerpt is not None:
                p["excerpt"] = _rendered(excerpt)
            if status is not None:
                p["status"] = status
            if categories is not None:
                p["categories"] = [int(c) for c in categories]
            if tags is not None:
                p["tags"] = [int(t) for t in tags]
            p["modified"] = _now()
            return p
    return {"error": f"Post {post_id} not found", "code": "rest_post_invalid_id"}


def delete_post(post_id):
    for i, p in enumerate(_posts_store):
        if p["id"] == int(post_id):
            removed = _posts_store.pop(i)
            return {"deleted": True, "previous": removed}
    return {"error": f"Post {post_id} not found", "code": "rest_post_invalid_id"}


# ---------------------------------------------------------------------------
# Pages
# ---------------------------------------------------------------------------

def list_pages(status="publish", per_page=10):
    pages = [p for p in _pages_store if p["status"] == status]
    pages.sort(key=lambda p: p["date"], reverse=True)
    return pages[:per_page]


# ---------------------------------------------------------------------------
# Taxonomies
# ---------------------------------------------------------------------------

def list_categories():
    return list(_categories_store)


def list_tags():
    return list(_tags_store)


# ---------------------------------------------------------------------------
# Comments
# ---------------------------------------------------------------------------

def list_comments(post=None, status="approved"):
    comments = [c for c in _comments_store if c["status"] == status]
    if post is not None:
        comments = [c for c in comments if c["post"] == int(post)]
    comments.sort(key=lambda c: c["date"])
    return comments


def create_comment(post, author_name, author_email, content, parent=0):
    if not any(p["id"] == int(post) for p in _posts_store):
        return {"error": f"Post {post} not found", "code": "rest_comment_invalid_post_id"}
    comment = {
        "id": _next_id(_comments_store),
        "post": int(post),
        "author_name": author_name,
        "author_email": author_email,
        "content": _rendered(content),
        "status": "approved",
        "date": _now(),
        "parent": int(parent),
    }
    _comments_store.append(comment)
    return comment


# ---------------------------------------------------------------------------
# Media / users
# ---------------------------------------------------------------------------

def list_media():
    return list(_media_store)


def list_users():
    return list(_users_store)
