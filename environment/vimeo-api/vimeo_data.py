"""Data access module for the Vimeo API mock service.

Mirrors a subset of the Vimeo API (api.vimeo.com): the authenticated user
(/me), their videos, individual videos, other users, and a user's videos.
List endpoints use Vimeo's paged envelope:
    {"total": N, "page": 1, "per_page": 25, "data": [...]}
"""

import csv
from pathlib import Path

DATA_DIR = Path(__file__).parent

import sys as _sys
_sys.path.insert(0, str(DATA_DIR.parent))
from _mutable_store import (
    read_seed_with_ctx, get_store, opt_csv_list, strict_int)

_store = get_store("vimeo-api")
_API = "vimeo-api"

_store.register("users", primary_key="id",
                initial_loader=lambda: _coerce_users(_load("users.json", "users")))
_store.register("videos", primary_key="id",
                initial_loader=lambda: _coerce_videos(_load("videos.json", "videos")))


def _users_rows():
    return _store.table("users").rows()


def _videos_rows():
    return _store.table("videos").rows()


# The user whose token is in use (the "me" of /me).
_ME = "12000001"


def _load(filename, table):
    return read_seed_with_ctx(DATA_DIR / filename, _API, table)


def _strip_ctx(r):
    return {k: v for k, v in r.items() if not k.startswith("__")}


# ---------------------------------------------------------------------------
# Load + coerce
# ---------------------------------------------------------------------------

def _coerce_users(rows):
    out = []
    for r in rows:
        out.append({
            "id": r["id"],
            "name": r["name"],
            "link": r["link"],
            "location": r["location"],
            "bio": r["bio"],
            "account": r["account"],
            "created_time": r["created_time"],
            "websites": [x for x in opt_csv_list(r, "websites", sep=";") if x],
        })
    return out


def _coerce_videos(rows):
    out = []
    for r in rows:
        out.append({
            "id": r["id"],
            "user_id": r["user_id"],
            "name": r["name"],
            "description": r["description"],
            "duration": strict_int(r, "duration"),
            "width": strict_int(r, "width"),
            "height": strict_int(r, "height"),
            "privacy": r["privacy"],
            "status": r["status"],
            "plays": strict_int(r, "plays"),
            "likes": strict_int(r, "likes"),
            "created_time": r["created_time"],
            "modified_time": r["modified_time"],
            "link": r["link"],
        })
    return out






# ---------------------------------------------------------------------------
# Serializers
# ---------------------------------------------------------------------------

def _serialize_user(u):
    return {
        "uri": f"/users/{u['id']}",
        "name": u["name"],
        "link": u["link"],
        "location": u["location"],
        "bio": u["bio"],
        "account": u["account"],
        "created_time": u["created_time"],
        "websites": [{"uri": "", "link": w} for w in u["websites"]],
        "metadata": {
            "connections": {
                "videos": {
                    "uri": f"/users/{u['id']}/videos",
                    "total": sum(1 for v in _videos_rows() if v["user_id"] == u["id"]),
                }
            }
        },
    }


def _serialize_video(v):
    owner = next((u for u in _users_rows() if u["id"] == v["user_id"]), None)
    return {
        "uri": f"/videos/{v['id']}",
        "name": v["name"],
        "description": v["description"],
        "link": v["link"],
        "duration": v["duration"],
        "width": v["width"],
        "height": v["height"],
        "created_time": v["created_time"],
        "modified_time": v["modified_time"],
        "privacy": {"view": v["privacy"]},
        "status": v["status"],
        "stats": {"plays": v["plays"]},
        "metadata": {"connections": {"likes": {"total": v["likes"]}}},
        "user": {
            "uri": f"/users/{owner['id']}",
            "name": owner["name"],
            "link": owner["link"],
        } if owner else None,
    }


def _paged(items, page=1, per_page=25):
    return {
        "total": len(items),
        "page": page,
        "per_page": per_page,
        "paging": {"next": None, "previous": None, "first": "?page=1", "last": "?page=1"},
        "data": items,
    }


# ---------------------------------------------------------------------------
# Me
# ---------------------------------------------------------------------------

def get_me():
    me = next((u for u in _users_rows() if u["id"] == _ME), _users_rows()[0])
    return _serialize_user(me)


def get_my_videos(page=1, per_page=25):
    videos = [v for v in _videos_rows() if v["user_id"] == _ME]
    videos = sorted(videos, key=lambda v: v["created_time"], reverse=True)
    return _paged([_serialize_video(v) for v in videos], page=page, per_page=per_page)


# ---------------------------------------------------------------------------
# Videos
# ---------------------------------------------------------------------------

def get_video(video_id):
    v = next((x for x in _videos_rows() if x["id"] == str(video_id)), None)
    if not v:
        return {"error": f"The requested video could not be found.", "video_id": str(video_id)}
    return _serialize_video(v)


# ---------------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------------

def get_user(user_id):
    u = next((x for x in _users_rows() if x["id"] == str(user_id)), None)
    if not u:
        return {"error": f"The requested user could not be found.", "user_id": str(user_id)}
    return _serialize_user(u)


def get_user_videos(user_id, page=1, per_page=25):
    if not any(u["id"] == str(user_id) for u in _users_rows()):
        return {"error": f"The requested user could not be found.", "user_id": str(user_id)}
    videos = [v for v in _videos_rows() if v["user_id"] == str(user_id)]
    videos = sorted(videos, key=lambda v: v["created_time"], reverse=True)
    return _paged([_serialize_video(v) for v in videos], page=page, per_page=per_page)

_store.eager_load()
