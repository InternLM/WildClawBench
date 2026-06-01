"""Data access module for the Reddit API mock service.

Mirrors a subset of Reddit's public/OAuth surface: subreddits, link posts,
comment trees, users, and voting. Uses Reddit fullnames (t5_/t3_/t1_/t2_).
"""

import csv
import time
import uuid
from copy import deepcopy
from pathlib import Path

DATA_DIR = Path(__file__).parent


def _load(filename):
    with open(DATA_DIR / filename, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _to_bool(v):
    return str(v).strip().lower() == "true"


# ---------------------------------------------------------------------------
# Load + coerce
# ---------------------------------------------------------------------------

def _coerce_subreddits(rows):
    out = []
    for r in rows:
        out.append({
            "id": r["id"],
            "display_name": r["name"],
            "title": r["title"],
            "public_description": r["public_description"],
            "subscribers": int(r["subscribers"]),
            "created_utc": float(r["created_utc"]),
            "over18": _to_bool(r["over18"]),
        })
    return out


def _coerce_posts(rows):
    out = []
    for r in rows:
        out.append({
            "id": r["id"],
            "subreddit": r["subreddit"],
            "title": r["title"],
            "author": r["author"],
            "url": r["url"] or None,
            "selftext": r["selftext"],
            "score": int(r["score"]),
            "ups": int(r["score"]),
            "num_comments": int(r["num_comments"]),
            "created_utc": float(r["created_utc"]),
            "is_self": _to_bool(r["is_self"]),
            "_likes": None,  # local per-process vote direction tracker
        })
    return out


def _coerce_comments(rows):
    out = []
    for r in rows:
        out.append({
            "id": r["id"],
            "post_id": r["post_id"],
            "parent_id": r["parent_id"],
            "author": r["author"],
            "body": r["body"],
            "score": int(r["score"]),
            "ups": int(r["score"]),
            "created_utc": float(r["created_utc"]),
        })
    return out


def _coerce_users(rows):
    out = []
    for r in rows:
        out.append({
            "name": r["name"],
            "id": r["id"],
            "link_karma": int(r["link_karma"]),
            "comment_karma": int(r["comment_karma"]),
            "created_utc": float(r["created_utc"]),
            "is_gold": _to_bool(r["is_gold"]),
            "is_mod": _to_bool(r["is_mod"]),
        })
    return out


_subreddits = _coerce_subreddits(_load("subreddits.csv"))
_posts = _coerce_posts(_load("posts.csv"))
_comments = _coerce_comments(_load("comments.csv"))
_users = _coerce_users(_load("users.csv"))

_subreddits_store = deepcopy(_subreddits)
_posts_store = deepcopy(_posts)
_comments_store = deepcopy(_comments)
_users_store = deepcopy(_users)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _find_subreddit(name):
    return next((s for s in _subreddits_store if s["display_name"].lower() == name.lower()), None)


def _post_thing(p):
    return {"kind": "t3", "data": p}


def _listing(children, kind="t3"):
    return {
        "kind": "Listing",
        "data": {
            "after": None,
            "before": None,
            "children": [{"kind": kind, "data": c} for c in children],
        },
    }


# ---------------------------------------------------------------------------
# Subreddits
# ---------------------------------------------------------------------------

def subreddit_about(name):
    s = _find_subreddit(name)
    if not s:
        return {"error": f"subreddit {name} not found"}
    return {"kind": "t5", "data": s}


def subreddit_listing(name, sort="hot", limit=25):
    s = _find_subreddit(name)
    if not s:
        return {"error": f"subreddit {name} not found"}
    posts = [p for p in _posts_store if p["subreddit"].lower() == name.lower()]
    if sort == "new":
        posts.sort(key=lambda p: p["created_utc"], reverse=True)
    else:  # hot: score-weighted
        posts.sort(key=lambda p: p["score"], reverse=True)
    return _listing(posts[: max(1, limit)], kind="t3")


# ---------------------------------------------------------------------------
# Comments (post + tree)
# ---------------------------------------------------------------------------

def post_comments(post_id):
    if not post_id.startswith("t3_"):
        post_id = f"t3_{post_id}"
    post = next((p for p in _posts_store if p["id"] == post_id), None)
    if not post:
        return {"error": f"post {post_id} not found"}
    post_listing = _listing([post], kind="t3")
    comments = [c for c in _comments_store if c["post_id"] == post_id]
    comments.sort(key=lambda c: c["score"], reverse=True)
    comment_listing = _listing(comments, kind="t1")
    return [post_listing, comment_listing]


# ---------------------------------------------------------------------------
# Submit + vote
# ---------------------------------------------------------------------------

def submit(subreddit, title, kind="self", url=None, text=None, author="devkat"):
    s = _find_subreddit(subreddit)
    if not s:
        return {"error": f"subreddit {subreddit} not found"}
    if not title:
        return {"error": "title is required"}
    post = {
        "id": f"t3_{uuid.uuid4().hex[:6]}",
        "subreddit": s["display_name"],
        "title": title,
        "author": author,
        "url": url if kind == "link" else None,
        "selftext": text or "" if kind == "self" else "",
        "score": 1,
        "ups": 1,
        "num_comments": 0,
        "created_utc": float(int(time.time())),
        "is_self": kind == "self",
        "_likes": True,
    }
    _posts_store.append(post)
    return {"json": {"errors": [], "data": {"id": post["id"], "name": post["id"], "url": post["url"]}}}


def _adjust(thing, direction):
    """Adjust a thing's score for a vote direction (-1, 0, 1) relative to prior vote."""
    prev = thing.get("_likes")
    prev_val = {True: 1, False: -1, None: 0}.get(prev, 0)
    new_val = {1: 1, -1: -1, 0: 0}.get(direction, 0)
    thing["score"] += new_val - prev_val
    thing["ups"] = thing["score"]
    thing["_likes"] = {1: True, -1: False, 0: None}.get(direction, None)


def vote(fullname, direction):
    if direction not in (-1, 0, 1):
        return {"error": "dir must be -1, 0, or 1"}
    target = None
    if fullname.startswith("t3_"):
        target = next((p for p in _posts_store if p["id"] == fullname), None)
    elif fullname.startswith("t1_"):
        target = next((c for c in _comments_store if c["id"] == fullname), None)
        if target is not None and "_likes" not in target:
            target["_likes"] = None
    if target is None:
        return {"error": f"thing {fullname} not found"}
    _adjust(target, direction)
    return {"name": fullname, "score": target["score"], "likes": target["_likes"]}


# ---------------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------------

def user_about(username):
    u = next((u for u in _users_store if u["name"].lower() == username.lower()), None)
    if not u:
        return {"error": f"user {username} not found"}
    return {"kind": "t2", "data": u}
