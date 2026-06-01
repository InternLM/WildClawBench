"""Data access module for the Twitter/X API v2 mock service."""

import csv
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


def _to_bool(v):
    return str(v).strip().lower() == "true"


# ---------------------------------------------------------------------------
# Load + coerce
# ---------------------------------------------------------------------------

def _coerce_users(rows):
    out = []
    for r in rows:
        out.append({
            **r,
            "verified": _to_bool(r["verified"]),
            "protected": _to_bool(r["protected"]),
            "public_metrics": {
                "followers_count": int(r["followers_count"]),
                "following_count": int(r["following_count"]),
                "tweet_count": int(r["tweet_count"]),
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
            "reply_to_tweet_id": r["reply_to_tweet_id"] or None,
            "public_metrics": {
                "like_count": int(r["like_count"]),
                "retweet_count": int(r["retweet_count"]),
                "reply_count": int(r["reply_count"]),
                "quote_count": int(r["quote_count"]),
            },
        })
    return out


_users = _coerce_users(_load("users.csv"))
_tweets = _coerce_tweets(_load("tweets.csv"))
_follows = _load("follows.csv")
_likes = _load("likes.csv")
_retweets = _load("retweets.csv")

_users_store = deepcopy(_users)
_tweets_store = deepcopy(_tweets)
_follows_store = deepcopy(_follows)
_likes_store = deepcopy(_likes)
_retweets_store = deepcopy(_retweets)

# The authenticated user ("me") is the first seed user.
_ME_ID = _users_store[0]["id"]


def _new_id():
    # Numeric-string snowflake-like id
    return str(uuid.uuid4().int % (10 ** 18))


def _public_user(u):
    return dict(u)


# ---------------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------------

def get_me():
    for u in _users_store:
        if u["id"] == _ME_ID:
            return {"data": _public_user(u)}
    return {"data": _public_user(_users_store[0])}


def get_user(user_id):
    for u in _users_store:
        if u["id"] == user_id:
            return {"data": _public_user(u)}
    return {"error": f"User {user_id} not found"}


def get_user_by_username(username):
    for u in _users_store:
        if u["username"].lower() == username.lower():
            return {"data": _public_user(u)}
    return {"error": f"User @{username} not found"}


def get_user_tweets(user_id, max_results=10):
    if not any(u["id"] == user_id for u in _users_store):
        return {"error": f"User {user_id} not found"}
    tweets = [t for t in _tweets_store if t["author_id"] == user_id]
    tweets.sort(key=lambda t: t["created_at"], reverse=True)
    sliced = tweets[:max_results]
    return {"data": sliced, "meta": {"result_count": len(sliced)}}


def get_followers(user_id, max_results=100):
    if not any(u["id"] == user_id for u in _users_store):
        return {"error": f"User {user_id} not found"}
    follower_ids = [f["follower_id"] for f in _follows_store if f["following_id"] == user_id]
    followers = [_public_user(u) for u in _users_store if u["id"] in follower_ids]
    sliced = followers[:max_results]
    return {"data": sliced, "meta": {"result_count": len(sliced)}}


def get_following(user_id, max_results=100):
    if not any(u["id"] == user_id for u in _users_store):
        return {"error": f"User {user_id} not found"}
    following_ids = [f["following_id"] for f in _follows_store if f["follower_id"] == user_id]
    following = [_public_user(u) for u in _users_store if u["id"] in following_ids]
    sliced = following[:max_results]
    return {"data": sliced, "meta": {"result_count": len(sliced)}}


# ---------------------------------------------------------------------------
# Tweets
# ---------------------------------------------------------------------------

def list_tweets(ids=None, max_results=10):
    if ids:
        wanted = {i.strip() for i in ids}
        tweets = [t for t in _tweets_store if t["id"] in wanted]
    else:
        tweets = sorted(_tweets_store, key=lambda t: t["created_at"], reverse=True)[:max_results]
    return {"data": tweets, "meta": {"result_count": len(tweets)}}


def get_tweet(tweet_id):
    for t in _tweets_store:
        if t["id"] == tweet_id:
            return {"data": t}
    return {"error": f"Tweet {tweet_id} not found"}


def create_tweet(text, author_id=None, reply_to_tweet_id=None):
    author_id = author_id or _ME_ID
    if not any(u["id"] == author_id for u in _users_store):
        return {"error": f"User {author_id} not found"}
    if reply_to_tweet_id and not any(t["id"] == reply_to_tweet_id for t in _tweets_store):
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
    _tweets_store.append(tweet)
    if reply_to_tweet_id:
        for t in _tweets_store:
            if t["id"] == reply_to_tweet_id:
                t["public_metrics"]["reply_count"] += 1
    return {"data": tweet}


def delete_tweet(tweet_id):
    for i, t in enumerate(_tweets_store):
        if t["id"] == tweet_id:
            _tweets_store.pop(i)
            return {"data": {"deleted": True}}
    return {"error": f"Tweet {tweet_id} not found"}


def search_recent(query, max_results=10):
    q = (query or "").lower()
    matches = [t for t in _tweets_store if q in t["text"].lower()]
    matches.sort(key=lambda t: t["created_at"], reverse=True)
    sliced = matches[:max_results]
    return {"data": sliced, "meta": {"result_count": len(sliced), "query": query}}


# ---------------------------------------------------------------------------
# Likes / Retweets
# ---------------------------------------------------------------------------

def like_tweet(user_id, tweet_id):
    if not any(u["id"] == user_id for u in _users_store):
        return {"error": f"User {user_id} not found"}
    target = next((t for t in _tweets_store if t["id"] == tweet_id), None)
    if not target:
        return {"error": f"Tweet {tweet_id} not found"}
    if not any(l["user_id"] == user_id and l["tweet_id"] == tweet_id for l in _likes_store):
        _likes_store.append({"user_id": user_id, "tweet_id": tweet_id})
        target["public_metrics"]["like_count"] += 1
    return {"data": {"liked": True}}


def retweet(user_id, tweet_id):
    if not any(u["id"] == user_id for u in _users_store):
        return {"error": f"User {user_id} not found"}
    target = next((t for t in _tweets_store if t["id"] == tweet_id), None)
    if not target:
        return {"error": f"Tweet {tweet_id} not found"}
    if not any(r["user_id"] == user_id and r["tweet_id"] == tweet_id for r in _retweets_store):
        _retweets_store.append({"user_id": user_id, "tweet_id": tweet_id})
        target["public_metrics"]["retweet_count"] += 1
    return {"data": {"retweeted": True}}
