"""FastAPI server wrapping reddit_data module as REST endpoints.

Implements a subset of Reddit's public/OAuth API with Listing envelopes.
"""

from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional

import reddit_data
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

app = FastAPI(title="Reddit API (Mock)", version="1.0.0")
install_tracker(app)
install_admin_plane(app, store=reddit_data._store)
@app.get("/health")
def health():
    return {"status": "ok"}


# --- Subreddits ---

@app.get("/r/{subreddit}/about")
def subreddit_about(subreddit: str):
    result = reddit_data.subreddit_about(subreddit)
    if isinstance(result, dict) and "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.get("/r/{subreddit}/hot")
def subreddit_hot(subreddit: str, limit: int = Query(25, ge=1, le=100)):
    result = reddit_data.subreddit_listing(subreddit, sort="hot", limit=limit)
    if isinstance(result, dict) and "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.get("/r/{subreddit}/new")
def subreddit_new(subreddit: str, limit: int = Query(25, ge=1, le=100)):
    result = reddit_data.subreddit_listing(subreddit, sort="new", limit=limit)
    if isinstance(result, dict) and "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Comments (post + tree) ---

@app.get("/comments/{post_id}")
def post_comments(post_id: str):
    result = reddit_data.post_comments(post_id)
    if isinstance(result, dict) and "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Submit ---

class SubmitBody(BaseModel):
    sr: str           # subreddit display name
    title: str
    kind: str = "self"  # "self" or "link"
    url: Optional[str] = None
    text: Optional[str] = None
    author: Optional[str] = "devkat"


@app.post("/api/submit")
def submit(body: SubmitBody):
    result = reddit_data.submit(
        subreddit=body.sr,
        title=body.title,
        kind=body.kind,
        url=body.url,
        text=body.text,
        author=body.author or "devkat",
    )
    if isinstance(result, dict) and "error" in result:
        return JSONResponse(status_code=400, content=result)
    return result


# --- Vote ---

class VoteBody(BaseModel):
    id: str   # fullname, e.g. t3_p001 or t1_c001
    dir: int  # -1, 0, or 1


@app.post("/api/vote")
def vote(body: VoteBody):
    result = reddit_data.vote(body.id, body.dir)
    if isinstance(result, dict) and "error" in result:
        code = 404 if "not found" in result["error"] else 400
        return JSONResponse(status_code=code, content=result)
    return result


# --- Users ---

@app.get("/user/{username}/about")
def user_about(username: str):
    result = reddit_data.user_about(username)
    if isinstance(result, dict) and "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result
