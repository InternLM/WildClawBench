"""Data access module for the LinkedIn API v2 mock service."""

import csv
import json
import uuid
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).parent

import sys as _sys
_sys.path.insert(0, str(DATA_DIR.parent))
from _mutable_store import (  # noqa: E402
    read_seed_with_ctx, get_store, opt_csv_list, strict_int)

_store = get_store("linkedin-api")
_API = "linkedin-api"


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
_store.register("organizations", primary_key="id",
                initial_loader=lambda: _coerce_orgs(_load("organizations.json", "organizations")))
_store.register("jobs", primary_key="id",
                initial_loader=lambda: _coerce_jobs(_load("jobs.json", "jobs")))
_store.register("connections", primary_key="id",
                initial_loader=lambda: [_strip_ctx(r) for r in _load("connections.json", "connections")])
_store.register_document("profile", initial_loader=lambda: __import__('json').load(open(DATA_DIR / "profile.json", encoding="utf-8")))


def _posts_rows():
    return _store.table("posts").rows()


def _organizations_rows():
    return _store.table("organizations").rows()


def _jobs_rows():
    return _store.table("jobs").rows()


def _connections_rows():
    return _store.table("connections").rows()


def _profile_doc():
    return _store.document("profile").get()



def _load(filename, table):
    return read_seed_with_ctx(DATA_DIR / filename, _API, table)


def _strip_ctx(r):
    return {k: v for k, v in r.items() if not k.startswith("__")}


def _now():
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000Z")


# ---------------------------------------------------------------------------
# Load + coerce
# ---------------------------------------------------------------------------

def _coerce_posts(rows):
    out = []
    for r in rows:
        out.append({
            **_strip_ctx(r),
            "socialDetail": {
                "likeCount": strict_int(r, "like_count"),
                "commentCount": strict_int(r, "comment_count"),
                "shareCount": strict_int(r, "share_count"),
            },
        })
        # Drop the flat metric columns now that they are nested.
        for k in ("like_count", "comment_count", "share_count"):
            out[-1].pop(k, None)
    return out


def _coerce_orgs(rows):
    out = []
    for r in rows:
        out.append({
            **_strip_ctx(r),
            "followerCount": strict_int(r, "followerCount"),
        })
    return out


def _coerce_jobs(rows):
    out = []
    for r in rows:
        out.append({
            **_strip_ctx(r),
            "applicants": strict_int(r, "applicants"),
            "keywords": [k for k in opt_csv_list(r, "keywords", sep=" ") if k],
        })
    return out




def _new_id():
    return str(uuid.uuid4().int % (10 ** 10))


# ---------------------------------------------------------------------------
# Profile / connections
# ---------------------------------------------------------------------------

def get_me():
    return _profile_doc()


def list_connections(start=0, count=50):
    sliced = _connections_rows()[start: start + count]
    return {
        "elements": sliced,
        "paging": {"start": start, "count": count, "total": len(_connections_rows())},
    }


# ---------------------------------------------------------------------------
# Posts
# ---------------------------------------------------------------------------

def list_posts(author_id=None, start=0, count=50):
    posts = list(_posts_rows())
    if author_id:
        posts = [p for p in posts if p["author_id"] == author_id]
    posts.sort(key=lambda p: p["created_at"], reverse=True)
    sliced = posts[start: start + count]
    return {
        "elements": sliced,
        "paging": {"start": start, "count": count, "total": len(posts)},
    }


def get_post(post_id):
    for p in _posts_rows():
        if p["id"] == post_id:
            return p
    return {"error": f"Post {post_id} not found"}


def create_post(commentary, author_id=None, visibility="PUBLIC"):
    author_id = author_id or _profile_doc()["id"]
    post = {
        "id": _new_id(),
        "author_id": author_id,
        "commentary": commentary,
        "visibility": visibility,
        "created_at": _now(),
        "socialDetail": {"likeCount": 0, "commentCount": 0, "shareCount": 0},
    }
    _store_insert("posts", post)
    return post


# ---------------------------------------------------------------------------
# Organizations
# ---------------------------------------------------------------------------

def get_organization(org_id):
    for o in _organizations_rows():
        if o["id"] == org_id:
            return o
    return {"error": f"Organization {org_id} not found"}


# ---------------------------------------------------------------------------
# Jobs
# ---------------------------------------------------------------------------

def search_jobs(keywords=None, location=None, start=0, count=50):
    jobs = list(_jobs_rows())
    if keywords:
        q = keywords.lower()
        jobs = [j for j in jobs
                if q in j["title"].lower()
                or q in j["description"].lower()
                or any(q in k.lower() for k in j["keywords"])]
    if location:
        loc = location.lower()
        jobs = [j for j in jobs if loc in j["location"].lower()]
    jobs.sort(key=lambda j: j["postedAt"], reverse=True)
    sliced = jobs[start: start + count]
    return {
        "elements": sliced,
        "paging": {"start": start, "count": count, "total": len(jobs)},
    }


def get_job(job_id):
    for j in _jobs_rows():
        if j["id"] == job_id:
            return j
    return {"error": f"Job {job_id} not found"}

_store.eager_load()
