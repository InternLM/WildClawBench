"""Data access module for YouTube Data API v3 simulation."""

import csv
import json
from copy import deepcopy
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).parent

# Load channel data early so coerce functions can reference it
with open(DATA_DIR / "channel.json", encoding="utf-8") as _f:
    _channel_raw = json.load(_f)
_CHANNEL_ID = _channel_raw["id"]
_CHANNEL_TITLE = _channel_raw["snippet"]["title"]


def _load(filename):
    with open(DATA_DIR / filename, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _now():
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


# ---------------------------------------------------------------------------
# Load and coerce data
# ---------------------------------------------------------------------------

def _coerce_videos(rows):
    out = []
    for r in rows:
        thumb = r.get("thumbnailUrl") or ""
        out.append({
            "id": r["video_id"],
            "snippet": {
                "publishedAt": r.get("publishedAt") or "",
                "channelId": r.get("channelId") or "",
                "title": r.get("title") or "",
                "description": r.get("description") or "",
                "thumbnails": {
                    "default": {"url": thumb.replace("maxresdefault", "default") if thumb else "", "width": 120, "height": 90},
                    "medium": {"url": thumb.replace("maxresdefault", "mqdefault") if thumb else "", "width": 320, "height": 180},
                    "high": {"url": thumb.replace("maxresdefault", "hqdefault") if thumb else "", "width": 480, "height": 360},
                    "maxres": {"url": thumb, "width": 1280, "height": 720},
                },
                "channelTitle": _CHANNEL_TITLE,
                "tags": [t.strip() for t in r["tags"].split(",")] if r.get("tags") else [],
                "categoryId": r.get("categoryId") or "",
                "liveBroadcastContent": r.get("liveBroadcastContent") or "none",
                "defaultLanguage": r.get("defaultLanguage") or None,
                "defaultAudioLanguage": r.get("defaultAudioLanguage") or None,
            },
            "contentDetails": {
                "duration": r.get("duration") or "PT0S",
                "dimension": r.get("dimension") or "2d",
                "definition": r.get("definition") or "hd",
                "caption": "true",
                "licensedContent": True,
                "projection": "rectangular",
            },
            "statistics": {
                "viewCount": r.get("viewCount") or "0",
                "likeCount": r.get("likeCount") or "0",
                "dislikeCount": r.get("dislikeCount") or "0",
                "commentCount": r.get("commentCount") or "0",
            },
            "status": {
                "uploadStatus": "processed",
                "privacyStatus": r.get("privacyStatus") or "public",
                "publishAt": r.get("publishAt") or None,
                "license": "youtube",
                "embeddable": (r.get("embeddable") or "true").lower() == "true",
                "publicStatsViewable": True,
                "madeForKids": False,
            },
        })
    return out


def _coerce_playlists(rows):
    out = []
    for r in rows:
        out.append({
            "id": r["playlist_id"],
            "snippet": {
                "publishedAt": r["publishedAt"],
                "channelId": r["channelId"],
                "title": r["title"],
                "description": r["description"],
                "thumbnails": {
                    "default": {"url": f"https://i.ytimg.com/vi/playlist_{r['playlist_id']}/default.jpg", "width": 120, "height": 90},
                    "medium": {"url": f"https://i.ytimg.com/vi/playlist_{r['playlist_id']}/mqdefault.jpg", "width": 320, "height": 180},
                    "high": {"url": f"https://i.ytimg.com/vi/playlist_{r['playlist_id']}/hqdefault.jpg", "width": 480, "height": 360},
                },
                "channelTitle": _CHANNEL_TITLE,
            },
            "status": {
                "privacyStatus": r["privacyStatus"],
            },
            "contentDetails": {
                "itemCount": int(r["itemCount"]),
            },
        })
    return out


def _coerce_playlist_items(rows):
    out = []
    for r in rows:
        out.append({
            "id": r["playlist_item_id"],
            "snippet": {
                "publishedAt": r["publishedAt"],
                "channelId": r["channelId"],
                "title": r["title"],
                "playlistId": r["playlistId"],
                "position": int(r["position"]),
                "resourceId": {
                    "kind": "youtube#video",
                    "videoId": r["videoId"],
                },
                "thumbnails": {
                    "default": {"url": f"https://i.ytimg.com/vi/{r['videoId']}/default.jpg", "width": 120, "height": 90},
                    "medium": {"url": f"https://i.ytimg.com/vi/{r['videoId']}/mqdefault.jpg", "width": 320, "height": 180},
                    "high": {"url": f"https://i.ytimg.com/vi/{r['videoId']}/hqdefault.jpg", "width": 480, "height": 360},
                },
                "channelTitle": _CHANNEL_TITLE,
            },
            "contentDetails": {
                "videoId": r["videoId"],
                "videoPublishedAt": r["publishedAt"],
            },
        })
    return out


def _coerce_comments(rows):
    out = []
    for r in rows:
        out.append({
            "id": r["comment_id"],
            "videoId": r["videoId"],
            "channelId": r["channelId"] if r["channelId"] else None,
            "parentId": r["parentId"] if r["parentId"] else None,
            "snippet": {
                "authorDisplayName": r["authorDisplayName"],
                "authorChannelId": {"value": r["authorChannelId"]},
                "textDisplay": r["textDisplay"],
                "textOriginal": r["textDisplay"],
                "likeCount": int(r["likeCount"]),
                "publishedAt": r["publishedAt"],
                "updatedAt": r["updatedAt"],
                "videoId": r["videoId"],
                "parentId": r["parentId"] if r["parentId"] else None,
            },
            "moderationStatus": r["moderationStatus"],
        })
    return out


def _coerce_captions(rows):
    out = []
    for r in rows:
        out.append({
            "id": r["caption_id"],
            "snippet": {
                "videoId": r["videoId"],
                "lastUpdated": r["lastUpdated"],
                "trackKind": r["trackKind"],
                "language": r["language"],
                "name": r["name"],
                "isDraft": r["isDraft"].lower() == "true",
            },
        })
    return out


# Load all data at module init
_videos = _coerce_videos(_load("videos.csv"))
_playlists = _coerce_playlists(_load("playlists.csv"))
_playlist_items = _coerce_playlist_items(_load("playlist_items.csv"))
_comments = _coerce_comments(_load("comments.csv"))
_captions = _coerce_captions(_load("captions.csv"))

with open(DATA_DIR / "video_categories.json", encoding="utf-8") as _f:
    _video_categories = json.load(_f)

with open(DATA_DIR / "channel_sections.json", encoding="utf-8") as _f:
    _channel_sections = json.load(_f)

with open(DATA_DIR / "analytics.json", encoding="utf-8") as _f:
    _analytics = json.load(_f)

_videos_store = deepcopy(_videos)
_playlists_store = deepcopy(_playlists)
_playlist_items_store = deepcopy(_playlist_items)
_comments_store = deepcopy(_comments)
_captions_store = deepcopy(_captions)
_channel_store = deepcopy(_channel_raw)
_video_categories_store = deepcopy(_video_categories)
_channel_sections_store = deepcopy(_channel_sections)
_analytics_store = deepcopy(_analytics)

_next_playlist_id = 11
_next_playlist_item_id = 26
_next_comment_id = 51


# ---------------------------------------------------------------------------
# Channels
# ---------------------------------------------------------------------------

def get_channel(channel_id: str):
    if channel_id != _channel_store["id"]:
        return {"error": f"Channel {channel_id} not found"}
    return {
        "kind": "youtube#channelListResponse",
        "pageInfo": {"totalResults": 1, "resultsPerPage": 1},
        "items": [_channel_store],
    }


# ---------------------------------------------------------------------------
# Videos
# ---------------------------------------------------------------------------

def list_videos(channel_id: str = None, video_id: str = None, max_results: int = 25, offset: int = 0):
    results = list(_videos_store)

    if video_id:
        ids = [v.strip() for v in video_id.split(",")]
        results = [v for v in results if v["id"] in ids]
    elif channel_id:
        results = [v for v in results if v["snippet"]["channelId"] == channel_id]

    total = len(results)
    page_results = results[offset: offset + max_results]
    return {
        "kind": "youtube#videoListResponse",
        "pageInfo": {"totalResults": total, "resultsPerPage": max_results},
        "items": page_results,
    }


def get_video(video_id: str):
    for v in _videos_store:
        if v["id"] == video_id:
            return {
                "kind": "youtube#videoListResponse",
                "pageInfo": {"totalResults": 1, "resultsPerPage": 1},
                "items": [v],
            }
    return {"error": f"Video {video_id} not found"}


def update_video(video_id: str, data: dict):
    for i, v in enumerate(_videos_store):
        if v["id"] == video_id:
            snippet_updates = data.get("snippet", {})
            if "title" in snippet_updates:
                _videos_store[i]["snippet"]["title"] = snippet_updates["title"]
            if "description" in snippet_updates:
                _videos_store[i]["snippet"]["description"] = snippet_updates["description"]
            if "tags" in snippet_updates:
                _videos_store[i]["snippet"]["tags"] = snippet_updates["tags"]
            if "categoryId" in snippet_updates:
                _videos_store[i]["snippet"]["categoryId"] = snippet_updates["categoryId"]
            if "defaultLanguage" in snippet_updates:
                _videos_store[i]["snippet"]["defaultLanguage"] = snippet_updates["defaultLanguage"]

            status_updates = data.get("status", {})
            if "privacyStatus" in status_updates:
                _videos_store[i]["status"]["privacyStatus"] = status_updates["privacyStatus"]
            if "embeddable" in status_updates:
                _videos_store[i]["status"]["embeddable"] = status_updates["embeddable"]
            if "publishAt" in status_updates:
                _videos_store[i]["status"]["publishAt"] = status_updates["publishAt"]

            return {
                "kind": "youtube#video",
                "items": [_videos_store[i]],
            }
    return {"error": f"Video {video_id} not found"}


def delete_video(video_id: str):
    for i, v in enumerate(_videos_store):
        if v["id"] == video_id:
            _videos_store.pop(i)
            # Also remove from playlist items
            global _playlist_items_store
            _playlist_items_store = [pi for pi in _playlist_items_store
                                     if pi["contentDetails"]["videoId"] != video_id]
            return {"deleted": True, "videoId": video_id}
    return {"error": f"Video {video_id} not found"}


# ---------------------------------------------------------------------------
# Playlists
# ---------------------------------------------------------------------------

def list_playlists(channel_id: str = None, playlist_id: str = None, max_results: int = 25, offset: int = 0):
    results = list(_playlists_store)

    if playlist_id:
        ids = [p.strip() for p in playlist_id.split(",")]
        results = [p for p in results if p["id"] in ids]
    elif channel_id:
        results = [p for p in results if p["snippet"]["channelId"] == channel_id]

    total = len(results)
    page_results = results[offset: offset + max_results]
    return {
        "kind": "youtube#playlistListResponse",
        "pageInfo": {"totalResults": total, "resultsPerPage": max_results},
        "items": page_results,
    }


def get_playlist(playlist_id: str):
    for p in _playlists_store:
        if p["id"] == playlist_id:
            return {
                "kind": "youtube#playlistListResponse",
                "pageInfo": {"totalResults": 1, "resultsPerPage": 1},
                "items": [p],
            }
    return {"error": f"Playlist {playlist_id} not found"}


def create_playlist(data: dict):
    global _next_playlist_id
    snippet = data.get("snippet", {})
    if not snippet.get("title"):
        return {"error": "Missing required field: snippet.title"}

    now = _now()
    playlist = {
        "id": f"PL_{_next_playlist_id:03d}",
        "snippet": {
            "publishedAt": now,
            "channelId": _CHANNEL_ID,
            "title": snippet["title"],
            "description": snippet.get("description", ""),
            "thumbnails": {
                "default": {"url": f"https://i.ytimg.com/vi/playlist_PL_{_next_playlist_id:03d}/default.jpg", "width": 120, "height": 90},
                "medium": {"url": f"https://i.ytimg.com/vi/playlist_PL_{_next_playlist_id:03d}/mqdefault.jpg", "width": 320, "height": 180},
                "high": {"url": f"https://i.ytimg.com/vi/playlist_PL_{_next_playlist_id:03d}/hqdefault.jpg", "width": 480, "height": 360},
            },
            "channelTitle": _CHANNEL_TITLE,
        },
        "status": {
            "privacyStatus": data.get("status", {}).get("privacyStatus", "public"),
        },
        "contentDetails": {
            "itemCount": 0,
        },
    }
    _playlists_store.append(playlist)
    _next_playlist_id += 1
    return {
        "kind": "youtube#playlist",
        "items": [playlist],
    }


def update_playlist(playlist_id: str, data: dict):
    for i, p in enumerate(_playlists_store):
        if p["id"] == playlist_id:
            snippet_updates = data.get("snippet", {})
            if "title" in snippet_updates:
                _playlists_store[i]["snippet"]["title"] = snippet_updates["title"]
            if "description" in snippet_updates:
                _playlists_store[i]["snippet"]["description"] = snippet_updates["description"]

            status_updates = data.get("status", {})
            if "privacyStatus" in status_updates:
                _playlists_store[i]["status"]["privacyStatus"] = status_updates["privacyStatus"]

            return {
                "kind": "youtube#playlist",
                "items": [_playlists_store[i]],
            }
    return {"error": f"Playlist {playlist_id} not found"}


def delete_playlist(playlist_id: str):
    for i, p in enumerate(_playlists_store):
        if p["id"] == playlist_id:
            _playlists_store.pop(i)
            # Remove associated playlist items
            global _playlist_items_store
            _playlist_items_store = [pi for pi in _playlist_items_store
                                     if pi["snippet"]["playlistId"] != playlist_id]
            return {"deleted": True, "playlistId": playlist_id}
    return {"error": f"Playlist {playlist_id} not found"}


# ---------------------------------------------------------------------------
# Playlist Items
# ---------------------------------------------------------------------------

def list_playlist_items(playlist_id: str, max_results: int = 25, offset: int = 0):
    results = [pi for pi in _playlist_items_store if pi["snippet"]["playlistId"] == playlist_id]
    results = sorted(results, key=lambda x: x["snippet"]["position"])

    total = len(results)
    page_results = results[offset: offset + max_results]
    return {
        "kind": "youtube#playlistItemListResponse",
        "pageInfo": {"totalResults": total, "resultsPerPage": max_results},
        "items": page_results,
    }


def insert_playlist_item(data: dict):
    global _next_playlist_item_id
    snippet = data.get("snippet", {})
    playlist_id = snippet.get("playlistId")
    resource_id = snippet.get("resourceId", {})
    video_id = resource_id.get("videoId")

    if not playlist_id or not video_id:
        return {"error": "Missing required fields: snippet.playlistId and snippet.resourceId.videoId"}

    # Verify playlist exists
    if not any(p["id"] == playlist_id for p in _playlists_store):
        return {"error": f"Playlist {playlist_id} not found"}

    # Get current max position
    existing = [pi for pi in _playlist_items_store if pi["snippet"]["playlistId"] == playlist_id]
    position = snippet.get("position", len(existing))

    now = _now()
    item = {
        "id": f"PLI_{_next_playlist_item_id:03d}",
        "snippet": {
            "publishedAt": now,
            "channelId": _CHANNEL_ID,
            "title": "",
            "playlistId": playlist_id,
            "position": position,
            "resourceId": {
                "kind": "youtube#video",
                "videoId": video_id,
            },
            "thumbnails": {
                "default": {"url": f"https://i.ytimg.com/vi/{video_id}/default.jpg", "width": 120, "height": 90},
                "medium": {"url": f"https://i.ytimg.com/vi/{video_id}/mqdefault.jpg", "width": 320, "height": 180},
                "high": {"url": f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg", "width": 480, "height": 360},
            },
            "channelTitle": _CHANNEL_TITLE,
        },
        "contentDetails": {
            "videoId": video_id,
            "videoPublishedAt": now,
        },
    }

    # Find video title
    for v in _videos_store:
        if v["id"] == video_id:
            item["snippet"]["title"] = v["snippet"]["title"]
            item["contentDetails"]["videoPublishedAt"] = v["snippet"]["publishedAt"]
            break

    _playlist_items_store.append(item)
    _next_playlist_item_id += 1

    # Update playlist item count
    for p in _playlists_store:
        if p["id"] == playlist_id:
            p["contentDetails"]["itemCount"] += 1
            break

    return {
        "kind": "youtube#playlistItem",
        "items": [item],
    }


def delete_playlist_item(playlist_item_id: str):
    for i, pi in enumerate(_playlist_items_store):
        if pi["id"] == playlist_item_id:
            playlist_id = pi["snippet"]["playlistId"]
            _playlist_items_store.pop(i)
            # Update playlist item count
            for p in _playlists_store:
                if p["id"] == playlist_id:
                    p["contentDetails"]["itemCount"] = max(0, p["contentDetails"]["itemCount"] - 1)
                    break
            return {"deleted": True, "playlistItemId": playlist_item_id}
    return {"error": f"Playlist item {playlist_item_id} not found"}


def update_playlist_item(playlist_item_id: str, data: dict):
    for i, pi in enumerate(_playlist_items_store):
        if pi["id"] == playlist_item_id:
            snippet_updates = data.get("snippet", {})
            if "position" in snippet_updates:
                _playlist_items_store[i]["snippet"]["position"] = int(snippet_updates["position"])
            return {
                "kind": "youtube#playlistItem",
                "items": [_playlist_items_store[i]],
            }
    return {"error": f"Playlist item {playlist_item_id} not found"}


# ---------------------------------------------------------------------------
# Comment Threads
# ---------------------------------------------------------------------------

def list_comment_threads(video_id: str = None, channel_id: str = None, max_results: int = 20, offset: int = 0, moderation_status: str = "published"):
    # Get top-level comments (no parentId)
    results = [c for c in _comments_store if not c["parentId"]]

    if video_id:
        results = [c for c in results if c["videoId"] == video_id]

    # Filter by moderation status
    results = [c for c in results if c["moderationStatus"] == moderation_status]

    # Sort by published date desc
    results = sorted(results, key=lambda x: x["snippet"]["publishedAt"], reverse=True)

    total = len(results)
    page_results = results[offset: offset + max_results]

    # Build comment thread structure
    threads = []
    for comment in page_results:
        # Find replies
        replies = [c for c in _comments_store if c["parentId"] == comment["id"]]
        thread = {
            "kind": "youtube#commentThread",
            "id": comment["id"],
            "snippet": {
                "channelId": _CHANNEL_ID,
                "videoId": comment["videoId"],
                "topLevelComment": {
                    "kind": "youtube#comment",
                    "id": comment["id"],
                    "snippet": comment["snippet"],
                },
                "canReply": True,
                "totalReplyCount": len(replies),
                "isPublic": True,
            },
        }
        if replies:
            thread["replies"] = {
                "comments": [{
                    "kind": "youtube#comment",
                    "id": r["id"],
                    "snippet": r["snippet"],
                } for r in replies]
            }
        threads.append(thread)

    return {
        "kind": "youtube#commentThreadListResponse",
        "pageInfo": {"totalResults": total, "resultsPerPage": max_results},
        "items": threads,
    }


def get_comment_thread(comment_id: str):
    for c in _comments_store:
        if c["id"] == comment_id and not c["parentId"]:
            replies = [r for r in _comments_store if r["parentId"] == comment_id]
            thread = {
                "kind": "youtube#commentThread",
                "id": c["id"],
                "snippet": {
                    "channelId": _CHANNEL_ID,
                    "videoId": c["videoId"],
                    "topLevelComment": {
                        "kind": "youtube#comment",
                        "id": c["id"],
                        "snippet": c["snippet"],
                    },
                    "canReply": True,
                    "totalReplyCount": len(replies),
                    "isPublic": True,
                },
            }
            if replies:
                thread["replies"] = {
                    "comments": [{
                        "kind": "youtube#comment",
                        "id": r["id"],
                        "snippet": r["snippet"],
                    } for r in replies]
                }
            return {
                "kind": "youtube#commentThreadListResponse",
                "pageInfo": {"totalResults": 1, "resultsPerPage": 1},
                "items": [thread],
            }
    return {"error": f"Comment thread {comment_id} not found"}


def insert_comment_thread(data: dict):
    global _next_comment_id
    snippet = data.get("snippet", {})
    video_id = snippet.get("videoId")
    text = snippet.get("topLevelComment", {}).get("snippet", {}).get("textOriginal", "")

    if not video_id or not text:
        return {"error": "Missing required fields: snippet.videoId and snippet.topLevelComment.snippet.textOriginal"}

    now = _now()
    comment_id = f"cmt_{_next_comment_id:03d}"
    comment = {
        "id": comment_id,
        "videoId": video_id,
        "channelId": _CHANNEL_ID,
        "parentId": None,
        "snippet": {
            "authorDisplayName": _CHANNEL_TITLE,
            "authorChannelId": {"value": _CHANNEL_ID},
            "textDisplay": text,
            "textOriginal": text,
            "likeCount": 0,
            "publishedAt": now,
            "updatedAt": now,
            "videoId": video_id,
            "parentId": None,
        },
        "moderationStatus": "published",
    }
    _comments_store.append(comment)
    _next_comment_id += 1

    thread = {
        "kind": "youtube#commentThread",
        "id": comment_id,
        "snippet": {
            "channelId": _CHANNEL_ID,
            "videoId": video_id,
            "topLevelComment": {
                "kind": "youtube#comment",
                "id": comment_id,
                "snippet": comment["snippet"],
            },
            "canReply": True,
            "totalReplyCount": 0,
            "isPublic": True,
        },
    }
    return {
        "kind": "youtube#commentThread",
        "items": [thread],
    }


# ---------------------------------------------------------------------------
# Comments
# ---------------------------------------------------------------------------

def list_comments(parent_id: str, max_results: int = 20, offset: int = 0):
    results = [c for c in _comments_store if c["parentId"] == parent_id]
    results = sorted(results, key=lambda x: x["snippet"]["publishedAt"])

    total = len(results)
    page_results = results[offset: offset + max_results]

    items = [{
        "kind": "youtube#comment",
        "id": c["id"],
        "snippet": c["snippet"],
    } for c in page_results]

    return {
        "kind": "youtube#commentListResponse",
        "pageInfo": {"totalResults": total, "resultsPerPage": max_results},
        "items": items,
    }


def insert_comment(data: dict):
    global _next_comment_id
    snippet = data.get("snippet", {})
    parent_id = snippet.get("parentId")
    text = snippet.get("textOriginal", "")

    if not parent_id or not text:
        return {"error": "Missing required fields: snippet.parentId and snippet.textOriginal"}

    # Find parent comment to get videoId
    video_id = None
    for c in _comments_store:
        if c["id"] == parent_id:
            video_id = c["videoId"]
            break
    if not video_id:
        return {"error": f"Parent comment {parent_id} not found"}

    now = _now()
    comment_id = f"cmt_{_next_comment_id:03d}"
    comment = {
        "id": comment_id,
        "videoId": video_id,
        "channelId": _CHANNEL_ID,
        "parentId": parent_id,
        "snippet": {
            "authorDisplayName": _CHANNEL_TITLE,
            "authorChannelId": {"value": _CHANNEL_ID},
            "textDisplay": text,
            "textOriginal": text,
            "likeCount": 0,
            "publishedAt": now,
            "updatedAt": now,
            "videoId": video_id,
            "parentId": parent_id,
        },
        "moderationStatus": "published",
    }
    _comments_store.append(comment)
    _next_comment_id += 1

    return {
        "kind": "youtube#comment",
        "items": [{
            "kind": "youtube#comment",
            "id": comment_id,
            "snippet": comment["snippet"],
        }],
    }


def update_comment(comment_id: str, data: dict):
    for i, c in enumerate(_comments_store):
        if c["id"] == comment_id:
            snippet_updates = data.get("snippet", {})
            if "textOriginal" in snippet_updates:
                _comments_store[i]["snippet"]["textOriginal"] = snippet_updates["textOriginal"]
                _comments_store[i]["snippet"]["textDisplay"] = snippet_updates["textOriginal"]
                _comments_store[i]["snippet"]["updatedAt"] = _now()
            return {
                "kind": "youtube#comment",
                "items": [{
                    "kind": "youtube#comment",
                    "id": comment_id,
                    "snippet": _comments_store[i]["snippet"],
                }],
            }
    return {"error": f"Comment {comment_id} not found"}


def delete_comment(comment_id: str):
    for i, c in enumerate(_comments_store):
        if c["id"] == comment_id:
            _comments_store.pop(i)
            # Also remove replies to this comment
            global _next_comment_id
            to_remove = [j for j, r in enumerate(_comments_store) if r["parentId"] == comment_id]
            for j in reversed(to_remove):
                _comments_store.pop(j)
            return {"deleted": True, "commentId": comment_id}
    return {"error": f"Comment {comment_id} not found"}


def set_moderation_status(comment_ids: list, moderation_status: str):
    updated = []
    for cid in comment_ids:
        for i, c in enumerate(_comments_store):
            if c["id"] == cid:
                _comments_store[i]["moderationStatus"] = moderation_status
                updated.append(cid)
                break
    if not updated:
        return {"error": "No matching comments found"}
    return {"updated": updated, "moderationStatus": moderation_status}


# ---------------------------------------------------------------------------
# Search
# ---------------------------------------------------------------------------

def search_videos(channel_id: str = None, q: str = None, order: str = "relevance", max_results: int = 25, offset: int = 0):
    results = list(_videos_store)

    if channel_id:
        results = [v for v in results if v["snippet"]["channelId"] == channel_id]

    # Only show public/unlisted videos in search
    results = [v for v in results if v["status"]["privacyStatus"] in ("public", "unlisted")]

    if q:
        q_lower = q.lower()
        scored = []
        for v in results:
            score = 0
            title = v["snippet"]["title"].lower()
            desc = v["snippet"]["description"].lower()
            tags = [t.lower() for t in v["snippet"].get("tags", [])]
            if q_lower in title:
                score += 10
            if q_lower in desc:
                score += 5
            if any(q_lower in tag for tag in tags):
                score += 3
            if score > 0:
                scored.append((score, v))
        results = [v for _, v in sorted(scored, key=lambda x: x[0], reverse=True)]

    # Sort
    if order == "date":
        results = sorted(results, key=lambda x: x["snippet"]["publishedAt"], reverse=True)
    elif order == "viewCount":
        results = sorted(results, key=lambda x: int(x["statistics"]["viewCount"]), reverse=True)
    elif order == "rating":
        results = sorted(results, key=lambda x: int(x["statistics"]["likeCount"]), reverse=True)
    # "relevance" is default (already sorted by score if q was given)

    total = len(results)
    page_results = results[offset: offset + max_results]

    items = []
    for v in page_results:
        items.append({
            "kind": "youtube#searchResult",
            "id": {
                "kind": "youtube#video",
                "videoId": v["id"],
            },
            "snippet": {
                "publishedAt": v["snippet"]["publishedAt"],
                "channelId": v["snippet"]["channelId"],
                "title": v["snippet"]["title"],
                "description": v["snippet"]["description"][:200],
                "thumbnails": v["snippet"]["thumbnails"],
                "channelTitle": v["snippet"]["channelTitle"],
                "liveBroadcastContent": v["snippet"]["liveBroadcastContent"],
            },
        })

    return {
        "kind": "youtube#searchListResponse",
        "pageInfo": {"totalResults": total, "resultsPerPage": max_results},
        "items": items,
    }


# ---------------------------------------------------------------------------
# Video Categories
# ---------------------------------------------------------------------------

def list_video_categories():
    items = []
    for cat in _video_categories_store:
        items.append({
            "kind": "youtube#videoCategory",
            "id": cat["id"],
            "snippet": cat["snippet"],
        })
    return {
        "kind": "youtube#videoCategoryListResponse",
        "items": items,
    }


# ---------------------------------------------------------------------------
# Captions
# ---------------------------------------------------------------------------

def list_captions(video_id: str):
    results = [c for c in _captions_store if c["snippet"]["videoId"] == video_id]
    if not results:
        # Check if video exists
        if not any(v["id"] == video_id for v in _videos_store):
            return {"error": f"Video {video_id} not found"}
    items = [{
        "kind": "youtube#caption",
        "id": c["id"],
        "snippet": c["snippet"],
    } for c in results]

    return {
        "kind": "youtube#captionListResponse",
        "items": items,
    }


# ---------------------------------------------------------------------------
# Channel Sections
# ---------------------------------------------------------------------------

def list_channel_sections(channel_id: str):
    if channel_id != _CHANNEL_ID:
        return {"error": f"Channel {channel_id} not found"}
    items = [{
        "kind": "youtube#channelSection",
        "id": s["id"],
        "snippet": s["snippet"],
        "contentDetails": s["contentDetails"],
    } for s in _channel_sections_store]

    return {
        "kind": "youtube#channelSectionListResponse",
        "items": items,
    }


# ---------------------------------------------------------------------------
# Analytics (simplified)
# ---------------------------------------------------------------------------

def get_channel_analytics():
    return {
        "kind": "youtubeAnalytics#resultTable",
        "channelId": _CHANNEL_ID,
        "period": _analytics_store["channel"]["period"],
        "metrics": _analytics_store["channel"],
    }


def get_video_analytics(video_id: str):
    for entry in _analytics_store["videos"]:
        if entry["videoId"] == video_id:
            return {
                "kind": "youtubeAnalytics#resultTable",
                "videoId": video_id,
                "metrics": entry,
            }
    return {"error": f"Analytics for video {video_id} not found"}
