"""FastAPI server wrapping instagram_data module as REST endpoints."""

from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List

import instagram_data
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

app = FastAPI(title="Instagram Graph API (Mock)", version="18.0")
install_tracker(app)
install_admin_plane(app, store=instagram_data._store)
@app.get("/health")
def health():
    return {"status": "ok"}


# --- Hashtags ---

@app.get("/ig_hashtag_search")
def search_hashtags(q: str = Query(...)):
    result = instagram_data.search_hashtags(q)
    if "error" in result:
        return JSONResponse(status_code=400, content=result)
    return result


@app.get("/hashtag/{hashtag_id}")
def get_hashtag(hashtag_id: str, fields: Optional[str] = Query(default=None)):
    result = instagram_data.get_hashtag(hashtag_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    if fields:
        field_list = [f.strip() for f in fields.split(",")]
        return {k: v for k, v in result.items() if k in field_list or k == "id"}
    return result


@app.get("/hashtag/{hashtag_id}/recent_media")
def get_hashtag_recent_media(
    hashtag_id: str,
    user_id: str = Query(...),
    fields: Optional[str] = Query(default=None),
    limit: int = Query(default=25, ge=1, le=50),
):
    result = instagram_data.get_hashtag_recent_media(hashtag_id, user_id, limit=limit)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    if fields:
        field_list = [f.strip() for f in fields.split(",")]
        result["data"] = [{k: v for k, v in m.items() if k in field_list or k == "id"} for m in result["data"]]
    return result


# --- Media (fixed paths) ---

@app.get("/media/{media_id}/children")
def get_media_children(media_id: str, fields: Optional[str] = Query(default=None)):
    result = instagram_data.get_media_children(media_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    if fields:
        field_list = [f.strip() for f in fields.split(",")]
        result["data"] = [{k: v for k, v in c.items() if k in field_list or k == "id"} for c in result["data"]]
    return result


@app.get("/media/{media_id}/comments")
def list_media_comments(
    media_id: str,
    fields: Optional[str] = Query(default=None),
    limit: int = Query(default=25, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    result = instagram_data.list_media_comments(media_id, limit=limit, offset=offset)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    if fields:
        field_list = [f.strip() for f in fields.split(",")]
        result["data"] = [{k: v for k, v in c.items() if k in field_list or k == "id"} for c in result["data"]]
    return result


@app.get("/media/{media_id}/insights")
def get_media_insights(
    media_id: str,
    metric: Optional[str] = Query(default=None),
):
    result = instagram_data.get_media_insights(media_id, metric=metric)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


class CommentCreateBody(BaseModel):
    message: str
    parent_id: Optional[str] = None


@app.post("/media/{media_id}/comments", status_code=201)
def create_comment(media_id: str, body: CommentCreateBody):
    result = instagram_data.create_comment(media_id, body.message, body.parent_id)
    if "error" in result:
        return JSONResponse(status_code=400, content=result)
    return result


@app.delete("/media/{media_id}/comments/{comment_id}")
def delete_comment(media_id: str, comment_id: str):
    result = instagram_data.delete_comment(media_id, comment_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


class CommentHideBody(BaseModel):
    hide: bool = True


@app.put("/media/{media_id}/comments/{comment_id}/hide")
def hide_comment(media_id: str, comment_id: str, body: CommentHideBody):
    result = instagram_data.hide_comment(media_id, comment_id, body.hide)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.get("/media/{media_id}")
def get_media(media_id: str, fields: Optional[str] = Query(default=None)):
    result = instagram_data.get_media(media_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    if fields:
        field_list = [f.strip() for f in fields.split(",")]
        return {k: v for k, v in result.items() if k in field_list or k == "id"}
    return result


@app.delete("/media/{media_id}")
def delete_media(media_id: str):
    result = instagram_data.delete_media(media_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Comments (fixed paths) ---

@app.get("/comment/{comment_id}/replies")
def get_comment_replies(
    comment_id: str,
    fields: Optional[str] = Query(default=None),
    limit: int = Query(default=25, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    result = instagram_data.get_comment_replies(comment_id, limit=limit, offset=offset)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    if fields:
        field_list = [f.strip() for f in fields.split(",")]
        result["data"] = [{k: v for k, v in c.items() if k in field_list or k == "id"} for c in result["data"]]
    return result


@app.get("/comment/{comment_id}")
def get_comment(comment_id: str, fields: Optional[str] = Query(default=None)):
    result = instagram_data.get_comment(comment_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    if fields:
        field_list = [f.strip() for f in fields.split(",")]
        return {k: v for k, v in result.items() if k in field_list or k == "id"}
    return result


# --- Stories (fixed paths) ---

@app.get("/stories/{story_id}")
def get_story(story_id: str, fields: Optional[str] = Query(default=None)):
    result = instagram_data.get_story(story_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    if fields:
        field_list = [f.strip() for f in fields.split(",")]
        return {k: v for k, v in result.items() if k in field_list or k == "id"}
    return result


# --- Container (fixed path) ---

@app.get("/container/{container_id}")
def get_container_status(container_id: str):
    result = instagram_data.get_media_container_status(container_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- User Search (fixed path - MUST come before parameterized /{user_id} routes) ---

@app.get("/ig_user_search")
def search_users(q: str = Query(...)):
    result = instagram_data.search_users(q)
    if "error" in result:
        return JSONResponse(status_code=400, content=result)
    return result


# --- User (parameterized paths - MUST come after fixed paths) ---

@app.get("/{user_id}/media")
def list_user_media(
    user_id: str,
    media_type: Optional[str] = Query(default=None),
    fields: Optional[str] = Query(default=None),
    limit: int = Query(default=25, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    result = instagram_data.list_user_media(user_id, media_type=media_type, limit=limit, offset=offset)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    if fields:
        field_list = [f.strip() for f in fields.split(",")]
        result["data"] = [{k: v for k, v in m.items() if k in field_list or k == "id"} for m in result["data"]]
    return result


@app.get("/{user_id}/stories")
def list_user_stories(user_id: str, fields: Optional[str] = Query(default=None)):
    result = instagram_data.list_user_stories(user_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    if fields:
        field_list = [f.strip() for f in fields.split(",")]
        result["data"] = [{k: v for k, v in s.items() if k in field_list or k == "id"} for s in result["data"]]
    return result


@app.get("/{user_id}/insights")
def get_user_insights(
    user_id: str,
    metric: Optional[str] = Query(default=None),
    period: Optional[str] = Query(default="day"),
):
    result = instagram_data.get_user_insights(user_id, metric=metric, period=period)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.get("/{user_id}/tags")
def list_user_mentions(
    user_id: str,
    fields: Optional[str] = Query(default=None),
    limit: int = Query(default=25, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    result = instagram_data.list_user_mentions(user_id, limit=limit, offset=offset)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    if fields:
        field_list = [f.strip() for f in fields.split(",")]
        result["data"] = [{k: v for k, v in m.items() if k in field_list or k == "id"} for m in result["data"]]
    return result


class MediaContainerCreateBody(BaseModel):
    image_url: Optional[str] = None
    video_url: Optional[str] = None
    caption: Optional[str] = None
    media_type: Optional[str] = "IMAGE"
    children: Optional[List[str]] = None


@app.post("/{user_id}/media", status_code=201)
def create_media_container(user_id: str, body: MediaContainerCreateBody):
    result = instagram_data.create_media_container(
        user_id,
        image_url=body.image_url,
        video_url=body.video_url,
        caption=body.caption,
        media_type=body.media_type,
        children=body.children,
    )
    if "error" in result:
        return JSONResponse(status_code=400, content=result)
    return result


class MediaPublishBody(BaseModel):
    creation_id: str


@app.post("/{user_id}/media_publish", status_code=201)
def publish_media_container(user_id: str, body: MediaPublishBody):
    result = instagram_data.publish_media_container(user_id, body.creation_id)
    if "error" in result:
        return JSONResponse(status_code=400, content=result)
    return result


class UserUpdateBody(BaseModel):
    biography: Optional[str] = None
    website: Optional[str] = None
    name: Optional[str] = None


@app.put("/{user_id}")
def update_user(user_id: str, body: UserUpdateBody):
    data = {k: v for k, v in body.model_dump().items() if v is not None}
    if not data:
        return JSONResponse(status_code=400, content={"error": {"message": "No updatable fields provided", "type": "IGApiException", "code": 100}})
    result = instagram_data.update_user(user_id, data)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.get("/{user_id}")
def get_user(user_id: str, fields: Optional[str] = Query(default=None)):
    result = instagram_data.get_user(user_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    if fields:
        field_list = [f.strip() for f in fields.split(",")]
        filtered = {k: v for k, v in result.items() if k in field_list or k == "id"}
        return filtered
    return result
