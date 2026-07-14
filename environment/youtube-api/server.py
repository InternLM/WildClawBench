"""FastAPI server wrapping youtube_data module as REST endpoints."""

from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List

import youtube_data
try:
    from tracking_middleware import install_tracker
    from admin_plane import install_admin_plane
except ModuleNotFoundError as _shared_plane_err:  # standalone run without the shared module on sys.path
    import logging as _logging
    _logging.error("SHARED PLANE MISSING - audit + admin disabled: %s", _shared_plane_err)
    def install_tracker(app):  # no-op fallback: audit endpoints disabled
        return None

    def install_admin_plane(app, store=None, one_shot_registry=None):
        return None

app = FastAPI(title="YouTube Data API v3 (Mock)", version="3.0")
install_tracker(app)
install_admin_plane(app, store=youtube_data._store)
@app.get("/health")
def health():
    return {"status": "ok"}


# --- Channels ---

@app.get("/youtube/v3/channels")
def list_channels(
    id: Optional[str] = Query(default=None),
    part: Optional[str] = Query(default="snippet,contentDetails,statistics,brandingSettings"),
):
    channel_id = id if id else youtube_data._CHANNEL_ID
    result = youtube_data.get_channel(channel_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Videos ---

@app.get("/youtube/v3/videos")
def list_videos(
    id: Optional[str] = Query(default=None),
    channelId: Optional[str] = Query(default=None),
    part: Optional[str] = Query(default="snippet,contentDetails,statistics,status"),
    maxResults: int = Query(default=25, ge=1, le=50),
    pageToken: Optional[str] = Query(default=None),
):
    if id:
        result = youtube_data.list_videos(video_id=id, max_results=maxResults)
    elif channelId:
        result = youtube_data.list_videos(channel_id=channelId, max_results=maxResults)
    else:
        result = youtube_data.list_videos(channel_id=youtube_data._CHANNEL_ID, max_results=maxResults)
    return result


class VideoUpdateBody(BaseModel):
    id: str
    snippet: Optional[dict] = None
    status: Optional[dict] = None


@app.put("/youtube/v3/videos")
def update_video(body: VideoUpdateBody, part: Optional[str] = Query(default="snippet,status")):
    data = {}
    if body.snippet:
        data["snippet"] = body.snippet
    if body.status:
        data["status"] = body.status
    result = youtube_data.update_video(body.id, data)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.delete("/youtube/v3/videos")
def delete_video(id: str = Query(...)):
    result = youtube_data.delete_video(id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return JSONResponse(status_code=204, content=None)


# --- Playlists ---

@app.get("/youtube/v3/playlists")
def list_playlists(
    id: Optional[str] = Query(default=None),
    channelId: Optional[str] = Query(default=None),
    part: Optional[str] = Query(default="snippet,contentDetails,status"),
    maxResults: int = Query(default=25, ge=1, le=50),
    pageToken: Optional[str] = Query(default=None),
):
    if id:
        result = youtube_data.list_playlists(playlist_id=id, max_results=maxResults)
    elif channelId:
        result = youtube_data.list_playlists(channel_id=channelId, max_results=maxResults)
    else:
        result = youtube_data.list_playlists(channel_id=youtube_data._CHANNEL_ID, max_results=maxResults)
    return result


class PlaylistCreateBody(BaseModel):
    snippet: dict
    status: Optional[dict] = None


@app.post("/youtube/v3/playlists", status_code=201)
def create_playlist(body: PlaylistCreateBody, part: Optional[str] = Query(default="snippet,status")):
    data = {"snippet": body.snippet}
    if body.status:
        data["status"] = body.status
    result = youtube_data.create_playlist(data)
    if "error" in result:
        return JSONResponse(status_code=400, content=result)
    return result


class PlaylistUpdateBody(BaseModel):
    id: str
    snippet: Optional[dict] = None
    status: Optional[dict] = None


@app.put("/youtube/v3/playlists")
def update_playlist(body: PlaylistUpdateBody, part: Optional[str] = Query(default="snippet,status")):
    data = {}
    if body.snippet:
        data["snippet"] = body.snippet
    if body.status:
        data["status"] = body.status
    result = youtube_data.update_playlist(body.id, data)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.delete("/youtube/v3/playlists")
def delete_playlist(id: str = Query(...)):
    result = youtube_data.delete_playlist(id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return JSONResponse(status_code=204, content=None)


# --- Playlist Items ---

@app.get("/youtube/v3/playlistItems")
def list_playlist_items(
    playlistId: str = Query(...),
    part: Optional[str] = Query(default="snippet,contentDetails"),
    maxResults: int = Query(default=25, ge=1, le=50),
    pageToken: Optional[str] = Query(default=None),
):
    return youtube_data.list_playlist_items(playlistId, max_results=maxResults)


class PlaylistItemInsertBody(BaseModel):
    snippet: dict


@app.post("/youtube/v3/playlistItems", status_code=201)
def insert_playlist_item(body: PlaylistItemInsertBody, part: Optional[str] = Query(default="snippet")):
    result = youtube_data.insert_playlist_item({"snippet": body.snippet})
    if "error" in result:
        return JSONResponse(status_code=400, content=result)
    return result


class PlaylistItemUpdateBody(BaseModel):
    id: str
    snippet: Optional[dict] = None


@app.put("/youtube/v3/playlistItems")
def update_playlist_item(body: PlaylistItemUpdateBody, part: Optional[str] = Query(default="snippet")):
    data = {}
    if body.snippet:
        data["snippet"] = body.snippet
    result = youtube_data.update_playlist_item(body.id, data)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.delete("/youtube/v3/playlistItems")
def delete_playlist_item(id: str = Query(...)):
    result = youtube_data.delete_playlist_item(id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return JSONResponse(status_code=204, content=None)


# --- Comment Threads ---

@app.get("/youtube/v3/commentThreads")
def list_comment_threads(
    videoId: Optional[str] = Query(default=None),
    channelId: Optional[str] = Query(default=None),
    part: Optional[str] = Query(default="snippet,replies"),
    maxResults: int = Query(default=20, ge=1, le=100),
    moderationStatus: Optional[str] = Query(default="published"),
    pageToken: Optional[str] = Query(default=None),
):
    return youtube_data.list_comment_threads(
        video_id=videoId, channel_id=channelId,
        max_results=maxResults, moderation_status=moderationStatus,
    )


class CommentThreadInsertBody(BaseModel):
    snippet: dict


@app.post("/youtube/v3/commentThreads", status_code=201)
def insert_comment_thread(body: CommentThreadInsertBody, part: Optional[str] = Query(default="snippet")):
    result = youtube_data.insert_comment_thread({"snippet": body.snippet})
    if "error" in result:
        return JSONResponse(status_code=400, content=result)
    return result


# --- Comments ---

@app.get("/youtube/v3/comments")
def list_comments(
    parentId: str = Query(...),
    part: Optional[str] = Query(default="snippet"),
    maxResults: int = Query(default=20, ge=1, le=100),
    pageToken: Optional[str] = Query(default=None),
):
    return youtube_data.list_comments(parentId, max_results=maxResults)


class CommentInsertBody(BaseModel):
    snippet: dict


@app.post("/youtube/v3/comments", status_code=201)
def insert_comment(body: CommentInsertBody, part: Optional[str] = Query(default="snippet")):
    result = youtube_data.insert_comment({"snippet": body.snippet})
    if "error" in result:
        return JSONResponse(status_code=400, content=result)
    return result


class CommentUpdateBody(BaseModel):
    id: str
    snippet: Optional[dict] = None


@app.put("/youtube/v3/comments")
def update_comment(body: CommentUpdateBody, part: Optional[str] = Query(default="snippet")):
    data = {}
    if body.snippet:
        data["snippet"] = body.snippet
    result = youtube_data.update_comment(body.id, data)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.delete("/youtube/v3/comments")
def delete_comment(id: str = Query(...)):
    result = youtube_data.delete_comment(id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return JSONResponse(status_code=204, content=None)


@app.post("/youtube/v3/comments/setModerationStatus")
def set_moderation_status(
    id: str = Query(...),
    moderationStatus: str = Query(...),
):
    comment_ids = [cid.strip() for cid in id.split(",")]
    result = youtube_data.set_moderation_status(comment_ids, moderationStatus)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return JSONResponse(status_code=204, content=None)


# --- Search ---

@app.get("/youtube/v3/search")
def search(
    q: Optional[str] = Query(default=None),
    channelId: Optional[str] = Query(default=None),
    part: Optional[str] = Query(default="snippet"),
    order: Optional[str] = Query(default="relevance"),
    maxResults: int = Query(default=25, ge=1, le=50),
    pageToken: Optional[str] = Query(default=None),
    type: Optional[str] = Query(default="video"),
):
    return youtube_data.search_videos(
        channel_id=channelId, q=q, order=order, max_results=maxResults,
    )


# --- Video Categories ---

@app.get("/youtube/v3/videoCategories")
def list_video_categories(
    regionCode: Optional[str] = Query(default="US"),
    part: Optional[str] = Query(default="snippet"),
):
    return youtube_data.list_video_categories()


# --- Captions ---

@app.get("/youtube/v3/captions")
def list_captions(
    videoId: str = Query(...),
    part: Optional[str] = Query(default="snippet"),
):
    result = youtube_data.list_captions(videoId)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Channel Sections ---

@app.get("/youtube/v3/channelSections")
def list_channel_sections(
    channelId: str = Query(...),
    part: Optional[str] = Query(default="snippet,contentDetails"),
):
    result = youtube_data.list_channel_sections(channelId)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Analytics (simplified) ---

@app.get("/youtube/analytics/v2/reports")
def get_analytics(
    ids: Optional[str] = Query(default=None),
    metrics: Optional[str] = Query(default="views,estimatedMinutesWatched,subscribersGained"),
    dimensions: Optional[str] = Query(default=None),
    filters: Optional[str] = Query(default=None),
    startDate: Optional[str] = Query(default=None),
    endDate: Optional[str] = Query(default=None),
):
    if filters and "video==" in filters:
        video_id = filters.split("video==")[1].split(";")[0]
        result = youtube_data.get_video_analytics(video_id)
        if "error" in result:
            return JSONResponse(status_code=404, content=result)
        return result
    return youtube_data.get_channel_analytics()
