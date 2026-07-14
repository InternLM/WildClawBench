"""Data access module for YouTube Data API v3 simulation."""

import csv
import json
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).parent

import sys as _sys
_sys.path.insert(0, str(DATA_DIR.parent))
from _mutable_store import (
    read_seed_with_ctx, get_store, opt_csv_list, opt_str, strict_int)
_store = get_store("youtube-api")
_API = "youtube-api"

# channel.json loaded before _load helper because _coerce_videos references _CHANNEL_TITLE.
with open(DATA_DIR / "channel.json", encoding="utf-8") as _f:
    _channel_raw = json.load(_f)
_CHANNEL_ID = _channel_raw["id"]
_CHANNEL_TITLE = _channel_raw["snippet"]["title"]


def _load(filename, table):
    return read_seed_with_ctx(DATA_DIR / filename, _API, table)


def _strip_ctx(r):
    return {k: v for k, v in r.items() if not k.startswith("__")}


def _load_json(filename):
    with open(DATA_DIR / filename, encoding="utf-8") as f:
        return json.load(f)


def _now():
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


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
                "tags": [t.strip() for t in opt_csv_list(r, "tags", sep=",")] if r.get("tags") else [],
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
                "itemCount": strict_int(r, "itemCount"),
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
                "position": strict_int(r, "position"),
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
            "channelId": opt_str(r, "channelId", default="") or None,
            "parentId": opt_str(r, "parentId", default="") or None,
            "snippet": {
                "authorDisplayName": r["authorDisplayName"],
                "authorChannelId": {"value": r["authorChannelId"]},
                "textDisplay": r["textDisplay"],
                "textOriginal": r["textDisplay"],
                "likeCount": strict_int(r, "likeCount"),
                "publishedAt": r["publishedAt"],
                "updatedAt": r["updatedAt"],
                "videoId": r["videoId"],
                "parentId": opt_str(r, "parentId", default="") or None,
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


_store.register("videos", primary_key="id",
                initial_loader=lambda: _coerce_videos(_load("videos.json", "videos")))
_store.register("playlists", primary_key="id",
                initial_loader=lambda: _coerce_playlists(_load("playlists.json", "playlists")))
_store.register("playlist_items", primary_key="id",
                initial_loader=lambda: _coerce_playlist_items(_load("playlist_items.json", "playlist_items")))
_store.register("comments", primary_key="id",
                initial_loader=lambda: _coerce_comments(_load("comments.json", "comments")))
_store.register("captions", primary_key="id",
                initial_loader=lambda: _coerce_captions(_load("captions.json", "captions")))
_store.register_document("channel", initial_loader=lambda: _channel_raw)
_store.register_document("video_categories",
                         initial_loader=lambda: _load_json("video_categories.json"))
_store.register_document("channel_sections",
                         initial_loader=lambda: _load_json("channel_sections.json"))
_store.register_document("analytics", initial_loader=lambda: _load_json("analytics.json"))


def _videos_rows(): return _store.table("videos").rows()
def _playlists_rows(): return _store.table("playlists").rows()
def _playlist_items_rows(): return _store.table("playlist_items").rows()
def _comments_rows(): return _store.table("comments").rows()
def _captions_rows(): return _store.table("captions").rows()
def _channel(): return _store.document("channel").get()
def _video_categories_list(): return _store.document("video_categories").get()
def _channel_sections_list(): return _store.document("channel_sections").get()
def _analytics(): return _store.document("analytics").get()


def _next_id_counter(table_name, id_prefix, fallback_start, key=lambda row: row["id"]):
    rows = _store.table(table_name).rows()
    max_n = fallback_start - 1
    for r in rows:
        try:
            n = int(str(key(r)).split("_")[-1])
            if n > max_n:
                max_n = n
        except (ValueError, IndexError):
            continue
    return max_n + 1


def get_channel(channel_id: str):
    ch = _channel()
    if channel_id != ch["id"]:
        return {"error": f"Channel {channel_id} not found"}
    return {
        "kind": "youtube#channelListResponse",
        "pageInfo": {"totalResults": 1, "resultsPerPage": 1},
        "items": [ch],
    }


def list_videos(channel_id: str = None, video_id: str = None, max_results: int = 25, offset: int = 0):
    results = _videos_rows()
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
    v = _store.table("videos").get(video_id)
    if v:
        return {
            "kind": "youtube#videoListResponse",
            "pageInfo": {"totalResults": 1, "resultsPerPage": 1},
            "items": [v],
        }
    return {"error": f"Video {video_id} not found"}


def update_video(video_id: str, data: dict):
    v = _store.table("videos").get(video_id)
    if not v:
        return {"error": f"Video {video_id} not found"}

    snippet_updates = data.get("snippet", {})
    new_snippet = dict(v["snippet"])
    for k in ("title", "description", "tags", "categoryId", "defaultLanguage"):
        if k in snippet_updates:
            new_snippet[k] = snippet_updates[k]

    status_updates = data.get("status", {})
    new_status = dict(v["status"])
    for k in ("privacyStatus", "embeddable", "publishAt"):
        if k in status_updates:
            new_status[k] = status_updates[k]

    _store.table("videos").patch(video_id, {"snippet": new_snippet, "status": new_status})
    return {
        "kind": "youtube#video",
        "items": [_store.table("videos").get(video_id)],
    }


def delete_video(video_id: str):
    if _store.table("videos").delete(video_id):
        _store.table("playlist_items").delete_where(
            lambda pi: pi["contentDetails"]["videoId"] == video_id)
        return {"deleted": True, "videoId": video_id}
    return {"error": f"Video {video_id} not found"}


def list_playlists(channel_id: str = None, playlist_id: str = None, max_results: int = 25, offset: int = 0):
    results = _playlists_rows()
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
    p = _store.table("playlists").get(playlist_id)
    if p:
        return {
            "kind": "youtube#playlistListResponse",
            "pageInfo": {"totalResults": 1, "resultsPerPage": 1},
            "items": [p],
        }
    return {"error": f"Playlist {playlist_id} not found"}


def create_playlist(data: dict):
    snippet = data.get("snippet", {})
    if not snippet.get("title"):
        return {"error": "Missing required field: snippet.title"}

    n = _next_id_counter("playlists", "PL_", 11)
    now = _now()
    pid = f"PL_{n:03d}"
    playlist = {
        "id": pid,
        "snippet": {
            "publishedAt": now,
            "channelId": _CHANNEL_ID,
            "title": snippet["title"],
            "description": snippet.get("description", ""),
            "thumbnails": {
                "default": {"url": f"https://i.ytimg.com/vi/playlist_{pid}/default.jpg", "width": 120, "height": 90},
                "medium": {"url": f"https://i.ytimg.com/vi/playlist_{pid}/mqdefault.jpg", "width": 320, "height": 180},
                "high": {"url": f"https://i.ytimg.com/vi/playlist_{pid}/hqdefault.jpg", "width": 480, "height": 360},
            },
            "channelTitle": _CHANNEL_TITLE,
        },
        "status": {
            "privacyStatus": data.get("status", {}).get("privacyStatus", "public"),
        },
        "contentDetails": {"itemCount": 0},
    }
    _store.table("playlists").upsert(playlist)
    return {"kind": "youtube#playlist", "items": [playlist]}


def update_playlist(playlist_id: str, data: dict):
    p = _store.table("playlists").get(playlist_id)
    if not p:
        return {"error": f"Playlist {playlist_id} not found"}

    snippet_updates = data.get("snippet", {})
    new_snippet = dict(p["snippet"])
    for k in ("title", "description"):
        if k in snippet_updates:
            new_snippet[k] = snippet_updates[k]

    status_updates = data.get("status", {})
    new_status = dict(p["status"])
    if "privacyStatus" in status_updates:
        new_status["privacyStatus"] = status_updates["privacyStatus"]

    _store.table("playlists").patch(playlist_id, {"snippet": new_snippet, "status": new_status})
    return {"kind": "youtube#playlist", "items": [_store.table("playlists").get(playlist_id)]}


def delete_playlist(playlist_id: str):
    if _store.table("playlists").delete(playlist_id):
        _store.table("playlist_items").delete_where(
            lambda pi: pi["snippet"]["playlistId"] == playlist_id)
        return {"deleted": True, "playlistId": playlist_id}
    return {"error": f"Playlist {playlist_id} not found"}


def list_playlist_items(playlist_id: str, max_results: int = 25, offset: int = 0):
    results = [pi for pi in _playlist_items_rows()
               if pi["snippet"]["playlistId"] == playlist_id]
    results = sorted(results, key=lambda x: x["snippet"]["position"])
    total = len(results)
    page_results = results[offset: offset + max_results]
    return {
        "kind": "youtube#playlistItemListResponse",
        "pageInfo": {"totalResults": total, "resultsPerPage": max_results},
        "items": page_results,
    }


def insert_playlist_item(data: dict):
    snippet = data.get("snippet", {})
    playlist_id = snippet.get("playlistId")
    resource_id = snippet.get("resourceId", {})
    video_id = resource_id.get("videoId")

    if not playlist_id or not video_id:
        return {"error": "Missing required fields: snippet.playlistId and snippet.resourceId.videoId"}

    if not _store.table("playlists").get(playlist_id):
        return {"error": f"Playlist {playlist_id} not found"}

    existing = [pi for pi in _playlist_items_rows()
                if pi["snippet"]["playlistId"] == playlist_id]
    position = snippet.get("position", len(existing))

    n = _next_id_counter("playlist_items", "PLI_", 26)
    now = _now()
    item = {
        "id": f"PLI_{n:03d}",
        "snippet": {
            "publishedAt": now,
            "channelId": _CHANNEL_ID,
            "title": "",
            "playlistId": playlist_id,
            "position": position,
            "resourceId": {"kind": "youtube#video", "videoId": video_id},
            "thumbnails": {
                "default": {"url": f"https://i.ytimg.com/vi/{video_id}/default.jpg", "width": 120, "height": 90},
                "medium": {"url": f"https://i.ytimg.com/vi/{video_id}/mqdefault.jpg", "width": 320, "height": 180},
                "high": {"url": f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg", "width": 480, "height": 360},
            },
            "channelTitle": _CHANNEL_TITLE,
        },
        "contentDetails": {"videoId": video_id, "videoPublishedAt": now},
    }

    v = _store.table("videos").get(video_id)
    if v:
        item["snippet"]["title"] = v["snippet"]["title"]
        item["contentDetails"]["videoPublishedAt"] = v["snippet"]["publishedAt"]

    _store.table("playlist_items").upsert(item)

    parent = _store.table("playlists").get(playlist_id)
    if parent:
        new_cd = dict(parent["contentDetails"])
        new_cd["itemCount"] = new_cd.get("itemCount", 0) + 1
        _store.table("playlists").patch(playlist_id, {"contentDetails": new_cd})

    return {"kind": "youtube#playlistItem", "items": [item]}


def delete_playlist_item(playlist_item_id: str):
    pi = _store.table("playlist_items").get(playlist_item_id)
    if not pi:
        return {"error": f"Playlist item {playlist_item_id} not found"}
    playlist_id = pi["snippet"]["playlistId"]
    _store.table("playlist_items").delete(playlist_item_id)
    parent = _store.table("playlists").get(playlist_id)
    if parent:
        new_cd = dict(parent["contentDetails"])
        new_cd["itemCount"] = max(0, new_cd.get("itemCount", 0) - 1)
        _store.table("playlists").patch(playlist_id, {"contentDetails": new_cd})
    return {"deleted": True, "playlistItemId": playlist_item_id}


def update_playlist_item(playlist_item_id: str, data: dict):
    pi = _store.table("playlist_items").get(playlist_item_id)
    if not pi:
        return {"error": f"Playlist item {playlist_item_id} not found"}
    snippet_updates = data.get("snippet", {})
    if "position" in snippet_updates:
        new_snippet = dict(pi["snippet"])
        new_snippet["position"] = int(snippet_updates["position"])
        _store.table("playlist_items").patch(playlist_item_id, {"snippet": new_snippet})
    return {
        "kind": "youtube#playlistItem",
        "items": [_store.table("playlist_items").get(playlist_item_id)],
    }


def list_comment_threads(video_id: str = None, channel_id: str = None, max_results: int = 20, offset: int = 0, moderation_status: str = "published"):
    all_comments = _comments_rows()
    results = [c for c in all_comments if not c["parentId"]]
    if video_id:
        results = [c for c in results if c["videoId"] == video_id]
    results = [c for c in results if c["moderationStatus"] == moderation_status]
    results = sorted(results, key=lambda x: x["snippet"]["publishedAt"], reverse=True)

    total = len(results)
    page_results = results[offset: offset + max_results]

    threads = []
    for comment in page_results:
        replies = [c for c in all_comments if c["parentId"] == comment["id"]]
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
    c = _store.table("comments").get(comment_id)
    if not c or c["parentId"]:
        return {"error": f"Comment thread {comment_id} not found"}
    all_comments = _comments_rows()
    replies = [r for r in all_comments if r["parentId"] == comment_id]
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


def insert_comment_thread(data: dict):
    snippet = data.get("snippet", {})
    video_id = snippet.get("videoId")
    text = snippet.get("topLevelComment", {}).get("snippet", {}).get("textOriginal", "")

    if not video_id or not text:
        return {"error": "Missing required fields: snippet.videoId and snippet.topLevelComment.snippet.textOriginal"}

    n = _next_id_counter("comments", "cmt_", 51)
    now = _now()
    comment_id = f"cmt_{n:03d}"
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
    _store.table("comments").upsert(comment)

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
    return {"kind": "youtube#commentThread", "items": [thread]}


def list_comments(parent_id: str, max_results: int = 20, offset: int = 0):
    results = [c for c in _comments_rows() if c["parentId"] == parent_id]
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
    snippet = data.get("snippet", {})
    parent_id = snippet.get("parentId")
    text = snippet.get("textOriginal", "")

    if not parent_id or not text:
        return {"error": "Missing required fields: snippet.parentId and snippet.textOriginal"}

    parent = _store.table("comments").get(parent_id)
    if not parent:
        return {"error": f"Parent comment {parent_id} not found"}
    video_id = parent["videoId"]

    n = _next_id_counter("comments", "cmt_", 51)
    now = _now()
    comment_id = f"cmt_{n:03d}"
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
    _store.table("comments").upsert(comment)

    return {
        "kind": "youtube#comment",
        "items": [{
            "kind": "youtube#comment",
            "id": comment_id,
            "snippet": comment["snippet"],
        }],
    }


def update_comment(comment_id: str, data: dict):
    c = _store.table("comments").get(comment_id)
    if not c:
        return {"error": f"Comment {comment_id} not found"}
    snippet_updates = data.get("snippet", {})
    if "textOriginal" in snippet_updates:
        new_snippet = dict(c["snippet"])
        new_snippet["textOriginal"] = snippet_updates["textOriginal"]
        new_snippet["textDisplay"] = snippet_updates["textOriginal"]
        new_snippet["updatedAt"] = _now()
        _store.table("comments").patch(comment_id, {"snippet": new_snippet})
    updated = _store.table("comments").get(comment_id)
    return {
        "kind": "youtube#comment",
        "items": [{
            "kind": "youtube#comment",
            "id": comment_id,
            "snippet": updated["snippet"] if updated else c["snippet"],
        }],
    }


def delete_comment(comment_id: str):
    if not _store.table("comments").get(comment_id):
        return {"error": f"Comment {comment_id} not found"}
    _store.table("comments").delete(comment_id)
    _store.table("comments").delete_where(lambda r: r["parentId"] == comment_id)
    return {"deleted": True, "commentId": comment_id}


def set_moderation_status(comment_ids: list, moderation_status: str):
    updated = []
    for cid in comment_ids:
        c = _store.table("comments").get(cid)
        if c:
            _store.table("comments").patch(cid, {"moderationStatus": moderation_status})
            updated.append(cid)
    if not updated:
        return {"error": "No matching comments found"}
    return {"updated": updated, "moderationStatus": moderation_status}


def search_videos(channel_id: str = None, q: str = None, order: str = "relevance", max_results: int = 25, offset: int = 0):
    results = _videos_rows()
    if channel_id:
        results = [v for v in results if v["snippet"]["channelId"] == channel_id]
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

    if order == "date":
        results = sorted(results, key=lambda x: x["snippet"]["publishedAt"], reverse=True)
    elif order == "viewCount":
        results = sorted(results, key=lambda x: int(x["statistics"]["viewCount"]), reverse=True)
    elif order == "rating":
        results = sorted(results, key=lambda x: int(x["statistics"]["likeCount"]), reverse=True)

    total = len(results)
    page_results = results[offset: offset + max_results]

    items = []
    for v in page_results:
        items.append({
            "kind": "youtube#searchResult",
            "id": {"kind": "youtube#video", "videoId": v["id"]},
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


def list_video_categories():
    items = []
    for cat in _video_categories_list():
        items.append({
            "kind": "youtube#videoCategory",
            "id": cat["id"],
            "snippet": cat["snippet"],
        })
    return {"kind": "youtube#videoCategoryListResponse", "items": items}


def list_captions(video_id: str):
    results = [c for c in _captions_rows() if c["snippet"]["videoId"] == video_id]
    if not results:
        if not _store.table("videos").get(video_id):
            return {"error": f"Video {video_id} not found"}
    items = [{
        "kind": "youtube#caption",
        "id": c["id"],
        "snippet": c["snippet"],
    } for c in results]
    return {"kind": "youtube#captionListResponse", "items": items}


def list_channel_sections(channel_id: str):
    if channel_id != _CHANNEL_ID:
        return {"error": f"Channel {channel_id} not found"}
    items = [{
        "kind": "youtube#channelSection",
        "id": s["id"],
        "snippet": s["snippet"],
        "contentDetails": s["contentDetails"],
    } for s in _channel_sections_list()]
    return {"kind": "youtube#channelSectionListResponse", "items": items}


def get_channel_analytics():
    a = _analytics()
    return {
        "kind": "youtubeAnalytics#resultTable",
        "channelId": _CHANNEL_ID,
        "period": a["channel"]["period"],
        "metrics": a["channel"],
    }


def get_video_analytics(video_id: str):
    a = _analytics()
    for entry in a["videos"]:
        if entry["videoId"] == video_id:
            return {
                "kind": "youtubeAnalytics#resultTable",
                "videoId": video_id,
                "metrics": entry,
            }
    return {"error": f"Analytics for video {video_id} not found"}

_store.eager_load()
