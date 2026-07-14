"""Data access module for Instagram Graph API simulation."""

import csv
from copy import deepcopy
import json
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).parent

import sys as _sys
_sys.path.insert(0, str(DATA_DIR.parent))
from _mutable_store import (
    read_seed_with_ctx, get_store, opt_csv_list, opt_str, strict_int)
_store = get_store("instagram-api")
_API = "instagram-api"


def _load(filename, table):
    return read_seed_with_ctx(DATA_DIR / filename, _API, table)


def _strip_ctx(r):
    return {k: v for k, v in r.items() if not k.startswith("__")}


def _now():
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S+0000")


# ---------------------------------------------------------------------------
# Load and coerce data
# ---------------------------------------------------------------------------

def _coerce_media(rows):
    out = []
    for r in rows:
        out.append({
            "id": r["id"],
            "user_id": r["user_id"],
            "caption": opt_str(r, "caption", default="") or None,
            "media_type": r["media_type"],
            "media_url": r["media_url"],
            "permalink": r["permalink"],
            "thumbnail_url": opt_str(r, "thumbnail_url", default="") or None,
            "timestamp": r["timestamp"],
            "like_count": strict_int(r, "like_count"),
            "comments_count": strict_int(r, "comments_count"),
            "is_comment_enabled": r["is_comment_enabled"].lower() == "true",
        })
    return out


def _coerce_comments(rows):
    out = []
    for r in rows:
        out.append({
            "id": r["id"],
            "media_id": r["media_id"],
            "user_id": r["user_id"],
            "username": r["username"],
            "text": r["text"],
            "timestamp": r["timestamp"],
            "like_count": strict_int(r, "like_count"),
            "hidden": r["hidden"].lower() == "true",
            "parent_id": opt_str(r, "parent_id", default="") or None,
        })
    return out


def _coerce_stories(rows):
    out = []
    for r in rows:
        out.append({
            "id": r["id"],
            "user_id": r["user_id"],
            "media_type": r["media_type"],
            "media_url": r["media_url"],
            "timestamp": r["timestamp"],
            "expiring_at": r["expiring_at"],
            "caption": opt_str(r, "caption", default="") or None,
            "link": opt_str(r, "link", default="") or None,
            "poll_question": opt_str(r, "poll_question", default="") or None,
            "poll_options": (opt_csv_list(r, "poll_options", sep="|") or None),
        })
    return out


def _coerce_media_insights(rows):
    out = []
    for r in rows:
        out.append({
            "media_id": r["media_id"],
            "impressions": strict_int(r, "impressions"),
            "reach": strict_int(r, "reach"),
            "engagement": strict_int(r, "engagement"),
            "saves": strict_int(r, "saves"),
            "shares": strict_int(r, "shares"),
            "profile_visits": strict_int(r, "profile_visits"),
            "follows": strict_int(r, "follows"),
        })
    return out


def _coerce_carousel_children(rows):
    out = []
    for r in rows:
        out.append({
            "id": r["id"],
            "media_id": r["media_id"],
            "media_type": r["media_type"],
            "media_url": r["media_url"],
            "timestamp": r["timestamp"],
        })
    return out


def _coerce_hashtags(rows):
    out = []
    for r in rows:
        out.append({
            "id": r["id"],
            "name": r["name"],
            "media_count": strict_int(r, "media_count"),
        })
    return out


def _coerce_mentions(rows):
    out = []
    for r in rows:
        out.append({
            "id": r["id"],
            "media_id": r["media_id"],
            "mentioned_by_user_id": r["mentioned_by_user_id"],
            "mentioned_by_username": r["mentioned_by_username"],
            "media_url": r["media_url"],
            "timestamp": r["timestamp"],
            "caption": opt_str(r, "caption", default="") or None,
        })
    return out


def _load_users():
    return _load("user.json", "users")


_store.register("media", primary_key="id",
                initial_loader=lambda: _coerce_media(_load("media.json", "media")))
_store.register("comments", primary_key="id",
                initial_loader=lambda: _coerce_comments(_load("comments.json", "comments")))
_store.register("stories", primary_key="id",
                initial_loader=lambda: _coerce_stories(_load("stories.json", "stories")))
_store.register("media_insights", primary_key="media_id",
                initial_loader=lambda: _coerce_media_insights(_load("media_insights.json", "media_insights")))
_store.register("carousel_children", primary_key="id",
                initial_loader=lambda: _coerce_carousel_children(_load("carousel_children.json", "carousel_children")))
_store.register("hashtags", primary_key="id",
                initial_loader=lambda: _coerce_hashtags(_load("hashtags.json", "hashtags")))
_store.register("mentions", primary_key="id",
                initial_loader=lambda: _coerce_mentions(_load("mentions.json", "mentions")))
_store.register("users", primary_key="id", initial_loader=_load_users)


def _media_rows():
    return _store.table("media").rows()


def _comments_rows():
    return _store.table("comments").rows()


def _stories_rows():
    return _store.table("stories").rows()


def _media_insights_rows():
    return _store.table("media_insights").rows()


def _carousel_children_rows():
    return _store.table("carousel_children").rows()


def _hashtags_rows():
    return _store.table("hashtags").rows()


def _mentions_rows():
    return _store.table("mentions").rows()


def _users_dict():
    return {u["id"]: u for u in _store.table("users").rows()}


def _primary_user():
    rows = _store.table("users").rows()
    return rows[0] if rows else {}

_next_comment_id = 17800001051
_next_media_id = 17900001029
_next_container_id = 17920001001


# ---------------------------------------------------------------------------
# User / Account
# ---------------------------------------------------------------------------

def get_user(user_id: str):
    user = _users_dict().get(user_id)
    if not user:
        return {"error": {"message": f"User {user_id} not found", "type": "IGApiException", "code": 100}}
    return user


def update_user(user_id: str, data: dict):
    user = _users_dict().get(user_id)
    if not user:
        return {"error": {"message": f"User {user_id} not found", "type": "IGApiException", "code": 100}}
    updatable = {"biography", "website", "name"}
    for k, v in data.items():
        if k in updatable:
            user[k] = v
    return user


def search_users(q: str):
    if not q or not q.strip():
        return {"error": {"message": "Query parameter 'q' is required", "type": "IGApiException", "code": 100}}
    q_lower = q.strip().lower()
    results = []
    for u in _store.table("users").rows():
        if q_lower in u.get("username", "").lower() or q_lower in u.get("name", "").lower():
            results.append(deepcopy(u))
    return {"data": results}


# ---------------------------------------------------------------------------
# Media
# ---------------------------------------------------------------------------

def list_user_media(user_id: str, media_type: str = None, limit: int = 25, offset: int = 0):
    if user_id not in _users_dict():
        return {"error": {"message": f"User {user_id} not found", "type": "IGApiException", "code": 100}}

    results = [m for m in _media_rows() if m["user_id"] == user_id]

    if media_type:
        results = [m for m in results if m["media_type"] == media_type.upper()]

    results = sorted(results, key=lambda x: x["timestamp"], reverse=True)

    total = len(results)
    page_results = results[offset: offset + limit]

    paging = {}
    if offset + limit < total:
        paging["cursors"] = {"after": page_results[-1]["id"] if page_results else None}
        paging["next"] = f"https://graph.instagram.mock/{user_id}/media?limit={limit}&after={paging['cursors']['after']}"
    if offset > 0:
        paging.setdefault("cursors", {})["before"] = page_results[0]["id"] if page_results else None

    return {
        "data": page_results,
        "paging": paging,
    }


def get_media(media_id: str):
    for m in _media_rows():
        if m["id"] == media_id:
            return m
    return {"error": {"message": f"Media {media_id} not found", "type": "IGApiException", "code": 100}}


def delete_media(media_id: str):
    if _store.table("media").delete(media_id):
        return {"success": True}
    return {"error": {"message": f"Media {media_id} not found", "type": "IGApiException", "code": 100}}


# ---------------------------------------------------------------------------
# Carousel Children
# ---------------------------------------------------------------------------

def get_media_children(media_id: str):
    # Verify media exists and is a carousel
    media = None
    for m in _media_rows():
        if m["id"] == media_id:
            media = m
            break
    if not media:
        return {"error": {"message": f"Media {media_id} not found", "type": "IGApiException", "code": 100}}
    if media["media_type"] != "CAROUSEL_ALBUM":
        return {"error": {"message": f"Media {media_id} is not a carousel album", "type": "IGApiException", "code": 100}}

    children = [c for c in _carousel_children_rows() if c["media_id"] == media_id]
    return {"data": children}


# ---------------------------------------------------------------------------
# Comments
# ---------------------------------------------------------------------------

def list_media_comments(media_id: str, limit: int = 25, offset: int = 0):
    # Verify media exists
    if not any(m["id"] == media_id for m in _media_rows()):
        return {"error": {"message": f"Media {media_id} not found", "type": "IGApiException", "code": 100}}

    results = [c for c in _comments_rows() if c["media_id"] == media_id and not c["hidden"]]
    results = sorted(results, key=lambda x: x["timestamp"], reverse=True)

    total = len(results)
    page_results = results[offset: offset + limit]

    paging = {}
    if offset + limit < total:
        paging["cursors"] = {"after": page_results[-1]["id"] if page_results else None}
    if offset > 0:
        paging.setdefault("cursors", {})["before"] = page_results[0]["id"] if page_results else None

    return {
        "data": page_results,
        "paging": paging,
    }


def get_comment(comment_id: str):
    for c in _comments_rows():
        if c["id"] == comment_id:
            return c
    return {"error": {"message": f"Comment {comment_id} not found", "type": "IGApiException", "code": 100}}


def get_comment_replies(comment_id: str, limit: int = 25, offset: int = 0):
    if not any(c["id"] == comment_id for c in _comments_rows()):
        return {"error": {"message": f"Comment {comment_id} not found", "type": "IGApiException", "code": 100}}

    results = [c for c in _comments_rows() if c["parent_id"] == comment_id]
    results = sorted(results, key=lambda x: x["timestamp"])

    total = len(results)
    page_results = results[offset: offset + limit]

    paging = {}
    if offset + limit < total:
        paging["cursors"] = {"after": page_results[-1]["id"] if page_results else None}

    return {
        "data": page_results,
        "paging": paging,
    }


def create_comment(media_id: str, message: str, parent_id: str = None):
    global _next_comment_id

    # Verify media exists
    if not any(m["id"] == media_id for m in _media_rows()):
        return {"error": {"message": f"Media {media_id} not found", "type": "IGApiException", "code": 100}}

    # If replying, verify parent exists
    if parent_id and not any(c["id"] == parent_id for c in _comments_rows()):
        return {"error": {"message": f"Parent comment {parent_id} not found", "type": "IGApiException", "code": 100}}

    comment = {
        "id": str(_next_comment_id),
        "media_id": media_id,
        "user_id": _primary_user()["id"],
        "username": _primary_user()["username"],
        "text": message,
        "timestamp": _now(),
        "like_count": 0,
        "hidden": False,
        "parent_id": parent_id,
    }
    _store.table("comments").upsert(comment)
    _next_comment_id += 1

    # Update comments_count on media
    for m in _media_rows():
        if m["id"] == media_id:
            _store.table("media").patch(
                media_id, {"comments_count": m["comments_count"] + 1})
            break

    return comment


def delete_comment(media_id: str, comment_id: str):
    # Verify media exists
    if not any(m["id"] == media_id for m in _media_rows()):
        return {"error": {"message": f"Media {media_id} not found", "type": "IGApiException", "code": 100}}

    for c in _comments_rows():
        if c["id"] == comment_id and c["media_id"] == media_id:
            _store.table("comments").delete(comment_id)
            for m in _media_rows():
                if m["id"] == media_id:
                    _store.table("media").patch(
                        media_id, {"comments_count": m["comments_count"] - 1})
                    break
            return {"success": True}
    return {"error": {"message": f"Comment {comment_id} not found", "type": "IGApiException", "code": 100}}


def hide_comment(media_id: str, comment_id: str, hide: bool = True):
    # Verify media exists
    if not any(m["id"] == media_id for m in _media_rows()):
        return {"error": {"message": f"Media {media_id} not found", "type": "IGApiException", "code": 100}}

    for c in _comments_rows():
        if c["id"] == comment_id and c["media_id"] == media_id:
            _store.table("comments").patch(comment_id, {"hidden": hide})
            return {"success": True}
    return {"error": {"message": f"Comment {comment_id} not found", "type": "IGApiException", "code": 100}}


# ---------------------------------------------------------------------------
# Stories
# ---------------------------------------------------------------------------

def list_user_stories(user_id: str):
    if user_id not in _users_dict():
        return {"error": {"message": f"User {user_id} not found", "type": "IGApiException", "code": 100}}

    results = [s for s in _stories_rows() if s["user_id"] == user_id]
    results = sorted(results, key=lambda x: x["timestamp"], reverse=True)

    return {"data": results}


def get_story(story_id: str):
    for s in _stories_rows():
        if s["id"] == story_id:
            return s
    return {"error": {"message": f"Story {story_id} not found", "type": "IGApiException", "code": 100}}


# ---------------------------------------------------------------------------
# Insights / Analytics
# ---------------------------------------------------------------------------

def get_user_insights(user_id: str, metric: str = None, period: str = "day"):
    if user_id not in _users_dict():
        return {"error": {"message": f"User {user_id} not found", "type": "IGApiException", "code": 100}}

    # Aggregate from media insights for the account
    total_impressions = sum(i["impressions"] for i in _media_insights_rows())
    total_reach = sum(i["reach"] for i in _media_insights_rows())
    total_engagement = sum(i["engagement"] for i in _media_insights_rows())
    total_profile_visits = sum(i["profile_visits"] for i in _media_insights_rows())
    total_follows = sum(i["follows"] for i in _media_insights_rows())

    all_metrics = [
        {
            "name": "impressions",
            "period": period,
            "values": [{"value": total_impressions, "end_time": _now()}],
            "title": "Impressions",
            "description": "Total number of times your posts have been seen",
        },
        {
            "name": "reach",
            "period": period,
            "values": [{"value": total_reach, "end_time": _now()}],
            "title": "Reach",
            "description": "Total number of unique accounts that have seen your posts",
        },
        {
            "name": "follower_count",
            "period": period,
            "values": [{"value": _primary_user()["followers_count"], "end_time": _now()}],
            "title": "Follower Count",
            "description": "Total number of followers",
        },
        {
            "name": "profile_views",
            "period": period,
            "values": [{"value": total_profile_visits, "end_time": _now()}],
            "title": "Profile Views",
            "description": "Total number of profile views",
        },
        {
            "name": "website_clicks",
            "period": period,
            "values": [{"value": int(total_profile_visits * 0.12), "end_time": _now()}],
            "title": "Website Clicks",
            "description": "Total number of taps on the website link",
        },
    ]

    if metric:
        metrics = metric.split(",")
        all_metrics = [m for m in all_metrics if m["name"] in metrics]
        if not all_metrics:
            return {"error": {"message": f"Invalid metric: {metric}", "type": "IGApiException", "code": 100}}

    return {"data": all_metrics}


def get_media_insights(media_id: str, metric: str = None):
    # Verify media exists
    if not any(m["id"] == media_id for m in _media_rows()):
        return {"error": {"message": f"Media {media_id} not found", "type": "IGApiException", "code": 100}}

    insight = None
    for i in _media_insights_rows():
        if i["media_id"] == media_id:
            insight = i
            break

    if not insight:
        return {"error": {"message": f"No insights available for media {media_id}", "type": "IGApiException", "code": 100}}

    all_metrics = [
        {"name": "impressions", "period": "lifetime", "values": [{"value": insight["impressions"]}], "title": "Impressions"},
        {"name": "reach", "period": "lifetime", "values": [{"value": insight["reach"]}], "title": "Reach"},
        {"name": "engagement", "period": "lifetime", "values": [{"value": insight["engagement"]}], "title": "Engagement"},
        {"name": "saved", "period": "lifetime", "values": [{"value": insight["saves"]}], "title": "Saves"},
        {"name": "shares", "period": "lifetime", "values": [{"value": insight["shares"]}], "title": "Shares"},
        {"name": "profile_visits", "period": "lifetime", "values": [{"value": insight["profile_visits"]}], "title": "Profile Visits"},
        {"name": "follows", "period": "lifetime", "values": [{"value": insight["follows"]}], "title": "Follows"},
    ]

    if metric:
        metrics = metric.split(",")
        all_metrics = [m for m in all_metrics if m["name"] in metrics]
        if not all_metrics:
            return {"error": {"message": f"Invalid metric: {metric}", "type": "IGApiException", "code": 100}}

    return {"data": all_metrics}


# ---------------------------------------------------------------------------
# Hashtags
# ---------------------------------------------------------------------------

def search_hashtags(q: str):
    if not q:
        return {"error": {"message": "Query parameter is required", "type": "IGApiException", "code": 100}}

    q_lower = q.lower().replace("#", "")
    results = [h for h in _hashtags_rows() if q_lower in h["name"].lower()]

    return {"data": results}


def get_hashtag(hashtag_id: str):
    for h in _hashtags_rows():
        if h["id"] == hashtag_id:
            return h
    return {"error": {"message": f"Hashtag {hashtag_id} not found", "type": "IGApiException", "code": 100}}


def get_hashtag_recent_media(hashtag_id: str, user_id: str, limit: int = 25):
    # Verify hashtag exists
    hashtag = None
    for h in _hashtags_rows():
        if h["id"] == hashtag_id:
            hashtag = h
            break
    if not hashtag:
        return {"error": {"message": f"Hashtag {hashtag_id} not found", "type": "IGApiException", "code": 100}}

    # Return user's media that contains this hashtag in caption
    tag_name = hashtag["name"]
    results = []
    for m in _media_rows():
        if m["user_id"] == user_id and m["caption"]:
            if f"#{tag_name}" in m["caption"].lower():
                results.append(m)

    results = sorted(results, key=lambda x: x["timestamp"], reverse=True)[:limit]

    return {"data": results}


# ---------------------------------------------------------------------------
# Mentions
# ---------------------------------------------------------------------------

def list_user_mentions(user_id: str, limit: int = 25, offset: int = 0):
    if user_id not in _users_dict():
        return {"error": {"message": f"User {user_id} not found", "type": "IGApiException", "code": 100}}

    results = sorted(_mentions_rows(), key=lambda x: x["timestamp"], reverse=True)

    total = len(results)
    page_results = results[offset: offset + limit]

    paging = {}
    if offset + limit < total:
        paging["cursors"] = {"after": page_results[-1]["id"] if page_results else None}

    return {
        "data": page_results,
        "paging": paging,
    }


# ---------------------------------------------------------------------------
# Content Publishing (Mock)
# ---------------------------------------------------------------------------

_media_containers = []


def create_media_container(user_id: str, image_url: str = None, video_url: str = None,
                           caption: str = None, media_type: str = "IMAGE",
                           children: list = None):
    global _next_container_id

    if user_id not in _users_dict():
        return {"error": {"message": f"User {user_id} not found", "type": "IGApiException", "code": 100}}

    if media_type == "CAROUSEL_ALBUM" and not children:
        return {"error": {"message": "Carousel albums require children containers", "type": "IGApiException", "code": 100}}

    container = {
        "id": str(_next_container_id),
        "status": "FINISHED",
        "media_type": media_type,
        "image_url": image_url,
        "video_url": video_url,
        "caption": caption,
        "children": children,
        "created_at": _now(),
    }
    _media_containers.append(container)
    _next_container_id += 1

    return {"id": container["id"]}


def publish_media_container(user_id: str, creation_id: str):
    global _next_media_id

    if user_id not in _users_dict():
        return {"error": {"message": f"User {user_id} not found", "type": "IGApiException", "code": 100}}

    # Find the container
    container = None
    for c in _media_containers:
        if c["id"] == creation_id:
            container = c
            break
    if not container:
        return {"error": {"message": f"Container {creation_id} not found", "type": "IGApiException", "code": 100}}

    if container["status"] != "FINISHED":
        return {"error": {"message": f"Container {creation_id} is not ready for publishing", "type": "IGApiException", "code": 100}}

    # Create the media entry
    now = _now()
    media = {
        "id": str(_next_media_id),
        "user_id": user_id,
        "caption": container["caption"],
        "media_type": container["media_type"],
        "media_url": container["image_url"] or container["video_url"] or "",
        "permalink": f"https://instagram.mock/p/new_{_next_media_id}/",
        "thumbnail_url": None,
        "timestamp": now,
        "like_count": 0,
        "comments_count": 0,
        "is_comment_enabled": True,
    }
    _store.table("media").upsert(media)
    _next_media_id += 1

    # Update user media count
    primary = _primary_user()
    _store.table("users").patch(
        primary["id"], {"media_count": primary["media_count"] + 1})

    # Remove the container
    _media_containers.remove(container)

    return {"id": media["id"]}


def get_media_container_status(container_id: str):
    for c in _media_containers:
        if c["id"] == container_id:
            return {"id": c["id"], "status": c["status"], "status_code": "PUBLISHED" if c["status"] == "FINISHED" else "IN_PROGRESS"}
    return {"error": {"message": f"Container {container_id} not found", "type": "IGApiException", "code": 100}}

_store.eager_load()
