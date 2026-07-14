"""FastAPI server wrapping twitter_data module as REST endpoints.

Implements a subset of the Twitter/X API v2 surface. Base path: /2
"""

from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List

import twitter_data
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

app = FastAPI(title="Twitter/X API v2 (Mock)", version="2.0.0")
install_tracker(app)
install_admin_plane(app, store=twitter_data._store)
@app.get("/health")
def health():
    return {"status": "ok"}


# --- Users ---

@app.get("/2/users/me")
def get_me():
    return twitter_data.get_me()


@app.get("/2/users/by/username/{username}")
def get_user_by_username(username: str):
    result = twitter_data.get_user_by_username(username)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.get("/2/users/{user_id}")
def get_user(user_id: str):
    result = twitter_data.get_user(user_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.get("/2/users/{user_id}/tweets")
def get_user_tweets(user_id: str, max_results: int = Query(10, ge=1, le=100)):
    result = twitter_data.get_user_tweets(user_id, max_results=max_results)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.get("/2/users/{user_id}/followers")
def get_followers(user_id: str, max_results: int = Query(100, ge=1, le=1000)):
    result = twitter_data.get_followers(user_id, max_results=max_results)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.get("/2/users/{user_id}/following")
def get_following(user_id: str, max_results: int = Query(100, ge=1, le=1000)):
    result = twitter_data.get_following(user_id, max_results=max_results)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Tweets ---

@app.get("/2/tweets")
def list_tweets(ids: Optional[str] = None, max_results: int = Query(10, ge=1, le=100)):
    id_list = [i.strip() for i in ids.split(",")] if ids else None
    return twitter_data.list_tweets(ids=id_list, max_results=max_results)


@app.get("/2/tweets/search/recent")
def search_recent(query: str = Query(...), max_results: int = Query(10, ge=1, le=100)):
    return twitter_data.search_recent(query, max_results=max_results)


@app.get("/2/tweets/{tweet_id}")
def get_tweet(tweet_id: str):
    result = twitter_data.get_tweet(tweet_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


class TweetCreateBody(BaseModel):
    text: str
    author_id: Optional[str] = None
    reply_to_tweet_id: Optional[str] = None


@app.post("/2/tweets", status_code=201)
def create_tweet(body: TweetCreateBody):
    result = twitter_data.create_tweet(
        text=body.text,
        author_id=body.author_id,
        reply_to_tweet_id=body.reply_to_tweet_id,
    )
    if "error" in result:
        return JSONResponse(status_code=400, content=result)
    return result


@app.delete("/2/tweets/{tweet_id}")
def delete_tweet(tweet_id: str):
    result = twitter_data.delete_tweet(tweet_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Likes / Retweets ---

class TweetRefBody(BaseModel):
    tweet_id: str


@app.post("/2/users/{user_id}/likes", status_code=200)
def like_tweet(user_id: str, body: TweetRefBody):
    result = twitter_data.like_tweet(user_id, body.tweet_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.post("/2/users/{user_id}/retweets", status_code=200)
def retweet(user_id: str, body: TweetRefBody):
    result = twitter_data.retweet(user_id, body.tweet_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result
