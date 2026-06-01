"""Data access module for the LinkedIn API v2 mock service."""

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


# ---------------------------------------------------------------------------
# Load + coerce
# ---------------------------------------------------------------------------

def _coerce_posts(rows):
    out = []
    for r in rows:
        out.append({
            **r,
            "socialDetail": {
                "likeCount": int(r["like_count"]),
                "commentCount": int(r["comment_count"]),
                "shareCount": int(r["share_count"]),
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
            **r,
            "followerCount": int(r["followerCount"]),
        })
    return out


def _coerce_jobs(rows):
    out = []
    for r in rows:
        out.append({
            **r,
            "applicants": int(r["applicants"]),
            "keywords": [k for k in r["keywords"].split(" ") if k],
        })
    return out


_connections = _load("connections.csv")
_posts = _coerce_posts(_load("posts.csv"))
_organizations = _coerce_orgs(_load("organizations.csv"))
_jobs = _coerce_jobs(_load("jobs.csv"))

with open(DATA_DIR / "profile.json", encoding="utf-8") as _f:
    _profile = json.load(_f)

_connections_store = deepcopy(_connections)
_posts_store = deepcopy(_posts)
_organizations_store = deepcopy(_organizations)
_jobs_store = deepcopy(_jobs)
_profile_store = deepcopy(_profile)


def _new_id():
    return str(uuid.uuid4().int % (10 ** 10))


# ---------------------------------------------------------------------------
# Profile / connections
# ---------------------------------------------------------------------------

def get_me():
    return _profile_store


def list_connections(start=0, count=50):
    sliced = _connections_store[start: start + count]
    return {
        "elements": sliced,
        "paging": {"start": start, "count": count, "total": len(_connections_store)},
    }


# ---------------------------------------------------------------------------
# Posts
# ---------------------------------------------------------------------------

def list_posts(author_id=None, start=0, count=50):
    posts = list(_posts_store)
    if author_id:
        posts = [p for p in posts if p["author_id"] == author_id]
    posts.sort(key=lambda p: p["created_at"], reverse=True)
    sliced = posts[start: start + count]
    return {
        "elements": sliced,
        "paging": {"start": start, "count": count, "total": len(posts)},
    }


def get_post(post_id):
    for p in _posts_store:
        if p["id"] == post_id:
            return p
    return {"error": f"Post {post_id} not found"}


def create_post(commentary, author_id=None, visibility="PUBLIC"):
    author_id = author_id or _profile_store["id"]
    post = {
        "id": _new_id(),
        "author_id": author_id,
        "commentary": commentary,
        "visibility": visibility,
        "created_at": _now(),
        "socialDetail": {"likeCount": 0, "commentCount": 0, "shareCount": 0},
    }
    _posts_store.append(post)
    return post


# ---------------------------------------------------------------------------
# Organizations
# ---------------------------------------------------------------------------

def get_organization(org_id):
    for o in _organizations_store:
        if o["id"] == org_id:
            return o
    return {"error": f"Organization {org_id} not found"}


# ---------------------------------------------------------------------------
# Jobs
# ---------------------------------------------------------------------------

def search_jobs(keywords=None, location=None, start=0, count=50):
    jobs = list(_jobs_store)
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
    for j in _jobs_store:
        if j["id"] == job_id:
            return j
    return {"error": f"Job {job_id} not found"}
