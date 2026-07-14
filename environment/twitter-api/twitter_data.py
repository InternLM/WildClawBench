"""Data access module for the Twitter/X API v2 mock service."""

import csv
import uuid
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).parent

import sys as _sys
_sys.path.insert(0, str(DATA_DIR.parent))
from _mutable_store import (
    read_seed_with_ctx, get_store, opt_str, strict_bool, strict_int)

_store = get_store("twitter-api")
_API = "twitter-api"



def _store_patch(_table, _row_or_pk, _updates):
    """Persist field updates to a stored row (was: in-place mutation of a copy)."""
    _t = _store.table(_table)
    _pk = _row_or_pk.get(_t.primary_key, _row_or_pk.get("id")) if isinstance(_row_or_pk, dict) else _row_or_pk
    return _t.patch(_pk, _updates)


def _store_delete(_table, _row_or_pk):
    """Persist a row deletion (was: pop/remove on a copy)."""
    _t = _store.table(_table)
    _pk = _row_or_pk.get(_t.primary_key, _row_or_pk.get("id")) if isinstance(_row_or_pk, dict) else _row_or_pk
    return _t.delete(_pk)

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

_store.register("users", primary_key="id",
                initial_loader=lambda: _coerce_users(_load("users.json", "users")))
_store.register("tweets", primary_key="id",
                initial_loader=lambda: _coerce_tweets(_load("tweets.json", "tweets")))
_store.register("follows", primary_key="_pk",
                initial_loader=lambda: [{**r, "_pk": f"{r['follower_id']}@{r['following_id']}"} for r in (_strip_ctx(x) for x in _load("follows.json", "follows"))])
_store.register("likes", primary_key="_pk",
                initial_loader=lambda: [{**r, "_pk": f"{r['user_id']}@{r['tweet_id']}"} for r in (_strip_ctx(x) for x in _load("likes.json", "likes"))])
_store.register("retweets", primary_key="_pk",
                initial_loader=lambda: [{**r, "_pk": f"{r['user_id']}@{r['tweet_id']}"} for r in (_strip_ctx(x) for x in _load("retweets.json", "retweets"))])


def _users_rows():
    return _store.table("users").rows()


def _tweets_rows():
    return _store.table("tweets").rows()


def _follows_rows():
    return [{k: v for k, v in r.items() if k != "_pk"} for r in _store.table("follows").rows()]


def _likes_rows():
    return [{k: v for k, v in r.items() if k != "_pk"} for r in _store.table("likes").rows()]


def _retweets_rows():
    return [{k: v for k, v in r.items() if k != "_pk"} for r in _store.table("retweets").rows()]



def _load(filename, table):
    return read_seed_with_ctx(DATA_DIR / filename, _API, table)


def _strip_ctx(r):
    return {k: v for k, v in r.items() if not k.startswith("__")}


def _now():
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000Z")


def _to_bool(v):
    return str(v).strip().lower() == "true"


# ---------------------------------------------------------------------------
# Load + coerce
# ---------------------------------------------------------------------------

def _coerce_users(rows):
    # The metric columns live in the seed as strings; they belong only under
    # public_metrics (ints) per the Twitter v2 contract. Drop the raw top-level
    # copies so a user is not emitted with the same metric in two types.
    _metric_cols = ("followers_count", "following_count", "tweet_count")
    out = []
    for r in rows:
        base = {k: v for k, v in _strip_ctx(r).items() if k not in _metric_cols}
        out.append({
            **base,
            "verified": strict_bool(r, "verified"),
            "protected": strict_bool(r, "protected"),
            "public_metrics": {
                "followers_count": strict_int(r, "followers_count"),
                "following_count": strict_int(r, "following_count"),
                "tweet_count": strict_int(r, "tweet_count"),
            },
        })
    return out


def _coerce_tweets(rows):
    out = []
    for r in rows:
        out.append({
            "id": r["id"],
            "author_id": r["author_id"],
            "text": r["text"],
            "created_at": r["created_at"],
            "lang": r["lang"],
            "reply_to_tweet_id": opt_str(r, "reply_to_tweet_id", default="") or None,
            "public_metrics": {
                "like_count": strict_int(r, "like_count"),
                "retweet_count": strict_int(r, "retweet_count"),
                "reply_count": strict_int(r, "reply_count"),
                "quote_count": strict_int(r, "quote_count"),
            },
        })
    return out












# The authenticated user ("me") is the first seed user.
_ME_ID = _users_rows()[0]["id"]


def _new_id():
    # Numeric-string snowflake-like id
    return str(uuid.uuid4().int % (10 ** 18))


def _public_user(u):
    return dict(u)


# ---------------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------------

def get_me():
    for u in _users_rows():
        if u["id"] == _ME_ID:
            return {"data": _public_user(u)}
    return {"data": _public_user(_users_rows()[0])}


def get_user(user_id):
    for u in _users_rows():
        if u["id"] == user_id:
            return {"data": _public_user(u)}
    return {"error": f"User {user_id} not found"}


def get_user_by_username(username):
    for u in _users_rows():
        if u["username"].lower() == username.lower():
            return {"data": _public_user(u)}
    return {"error": f"User @{username} not found"}


def get_user_tweets(user_id, max_results=10):
    if not any(u["id"] == user_id for u in _users_rows()):
        return {"error": f"User {user_id} not found"}
    tweets = [t for t in _tweets_rows() if t["author_id"] == user_id]
    tweets.sort(key=lambda t: t["created_at"], reverse=True)
    sliced = tweets[:max_results]
    return {"data": sliced, "meta": {"result_count": len(sliced)}}


def get_followers(user_id, max_results=100):
    if not any(u["id"] == user_id for u in _users_rows()):
        return {"error": f"User {user_id} not found"}
    follower_ids = [f["follower_id"] for f in _follows_rows() if f["following_id"] == user_id]
    followers = [_public_user(u) for u in _users_rows() if u["id"] in follower_ids]
    sliced = followers[:max_results]
    return {"data": sliced, "meta": {"result_count": len(sliced)}}


def get_following(user_id, max_results=100):
    if not any(u["id"] == user_id for u in _users_rows()):
        return {"error": f"User {user_id} not found"}
    following_ids = [f["following_id"] for f in _follows_rows() if f["follower_id"] == user_id]
    following = [_public_user(u) for u in _users_rows() if u["id"] in following_ids]
    sliced = following[:max_results]
    return {"data": sliced, "meta": {"result_count": len(sliced)}}


# ---------------------------------------------------------------------------
# Tweets
# ---------------------------------------------------------------------------

def list_tweets(ids=None, max_results=10):
    if ids:
        wanted = {i.strip() for i in ids}
        tweets = [t for t in _tweets_rows() if t["id"] in wanted]
    else:
        tweets = sorted(_tweets_rows(), key=lambda t: t["created_at"], reverse=True)[:max_results]
    return {"data": tweets, "meta": {"result_count": len(tweets)}}


def get_tweet(tweet_id):
    for t in _tweets_rows():
        if t["id"] == tweet_id:
            return {"data": t}
    return {"error": f"Tweet {tweet_id} not found"}


def create_tweet(text, author_id=None, reply_to_tweet_id=None):
    author_id = author_id or _ME_ID
    if not any(u["id"] == author_id for u in _users_rows()):
        return {"error": f"User {author_id} not found"}
    if reply_to_tweet_id and not any(t["id"] == reply_to_tweet_id for t in _tweets_rows()):
        return {"error": f"Tweet {reply_to_tweet_id} not found"}
    tweet = {
        "id": _new_id(),
        "author_id": author_id,
        "text": text,
        "created_at": _now(),
        "lang": "en",
        "reply_to_tweet_id": reply_to_tweet_id,
        "public_metrics": {
            "like_count": 0,
            "retweet_count": 0,
            "reply_count": 0,
            "quote_count": 0,
        },
    }
    _store_insert("tweets", tweet)
    if reply_to_tweet_id:
        for t in _tweets_rows():
            if t["id"] == reply_to_tweet_id:
                t["public_metrics"]["reply_count"] += 1
                _store_patch("tweets", t, {"public_metrics": t["public_metrics"]})
    return {"data": tweet}


def delete_tweet(tweet_id):
    for t in _tweets_rows():
        if t["id"] == tweet_id:
            _store_delete("tweets", t)
            return {"data": {"deleted": True}}
    return {"error": f"Tweet {tweet_id} not found"}


def search_recent(query, max_results=10):
    q = (query or "").lower()
    matches = [t for t in _tweets_rows() if q in t["text"].lower()]
    matches.sort(key=lambda t: t["created_at"], reverse=True)
    sliced = matches[:max_results]
    return {"data": sliced, "meta": {"result_count": len(sliced), "query": query}}


# ---------------------------------------------------------------------------
# Likes / Retweets
# ---------------------------------------------------------------------------

def like_tweet(user_id, tweet_id):
    if not any(u["id"] == user_id for u in _users_rows()):
        return {"error": f"User {user_id} not found"}
    target = next((t for t in _tweets_rows() if t["id"] == tweet_id), None)
    if not target:
        return {"error": f"Tweet {tweet_id} not found"}
    if not any(l["user_id"] == user_id and l["tweet_id"] == tweet_id for l in _likes_rows()):
        _store_insert("likes", {"_pk": f"{user_id}@{tweet_id}",
                                "user_id": user_id, "tweet_id": tweet_id})
        target["public_metrics"]["like_count"] += 1
        _store_patch("tweets", target, {"public_metrics": target["public_metrics"]})
    return {"data": {"liked": True}}


def retweet(user_id, tweet_id):
    if not any(u["id"] == user_id for u in _users_rows()):
        return {"error": f"User {user_id} not found"}
    target = next((t for t in _tweets_rows() if t["id"] == tweet_id), None)
    if not target:
        return {"error": f"Tweet {tweet_id} not found"}
    if not any(r["user_id"] == user_id and r["tweet_id"] == tweet_id for r in _retweets_rows()):
        _store.table("retweets").upsert({
            "_pk": f"{user_id}@{tweet_id}",
            "user_id": user_id,
            "tweet_id": tweet_id,
        })
        target["public_metrics"]["retweet_count"] += 1
        _store_patch("tweets", target, {"public_metrics": target["public_metrics"]})
    return {"data": {"retweeted": True}}

_store.eager_load()
