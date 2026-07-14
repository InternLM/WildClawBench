#!/usr/bin/env python3
"""CLI helper for the Twitter/X API v2 (Mock) mock API.

Generated read/write helper: one flag per endpoint. Base URL comes from
$TWITTER_API_URL (override with --url). POST/PUT/PATCH bodies are read from --data
(JSON string) or --data-file; DELETE/GET take only path params.
"""

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request


def _fill(path, values):
    """Substitute {placeholders} in path order with the provided positional values."""
    import re as _re
    it = iter(values or [])
    return _re.sub(r"\{[^}]+\}", lambda _m: urllib.parse.quote(str(next(it, "")), safe=""), path)


def _request(base, path, method, body=None):
    url = base.rstrip("/") + path
    data = json.dumps(body).encode() if body is not None else None
    headers = {"Content-Type": "application/json"} if data is not None else {}
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req) as resp:
        raw = resp.read().decode()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return raw


def api_get(base, path):
    return _request(base, path, "GET")


def api_delete(base, path):
    return _request(base, path, "DELETE")


def api_send(base, path, method, body):
    return _request(base, path, method, body if body is not None else {})


def _body(args):
    if getattr(args, "data_file", None):
        with open(args.data_file, "r", encoding="utf-8") as fh:
            return json.load(fh)
    if getattr(args, "data", None):
        return json.loads(args.data)
    return {}


def show(data):
    print(json.dumps(data, indent=2, ensure_ascii=False) if not isinstance(data, str) else data)
    return 0


def main():
    p = argparse.ArgumentParser(description="Query the Twitter/X API v2 (Mock) mock API")
    p.add_argument("--get-2-users-me", action="store_true", help="GET /2/users/me")
    p.add_argument("--get-2-users-by-username-username", metavar="USERNAME", nargs=1, help="GET /2/users/by/username/{username}")
    p.add_argument("--get-2-users-user-id", metavar="USER_ID", nargs=1, help="GET /2/users/{user_id}")
    p.add_argument("--get-2-users-tweets-user-id", metavar="USER_ID", nargs=1, help="GET /2/users/{user_id}/tweets")
    p.add_argument("--get-2-users-followers-user-id", metavar="USER_ID", nargs=1, help="GET /2/users/{user_id}/followers")
    p.add_argument("--get-2-users-following-user-id", metavar="USER_ID", nargs=1, help="GET /2/users/{user_id}/following")
    p.add_argument("--get-2-tweets", action="store_true", help="GET /2/tweets")
    p.add_argument("--get-2-tweets-search-recent", action="store_true", help="GET /2/tweets/search/recent")
    p.add_argument("--get-2-tweets-tweet-id", metavar="TWEET_ID", nargs=1, help="GET /2/tweets/{tweet_id}")
    p.add_argument("--post-2-tweets", action="store_true", help="POST /2/tweets")
    p.add_argument("--delete-2-tweets-tweet-id", metavar="TWEET_ID", nargs=1, help="DELETE /2/tweets/{tweet_id}")
    p.add_argument("--post-2-users-likes-user-id", metavar="USER_ID", nargs=1, help="POST /2/users/{user_id}/likes")
    p.add_argument("--post-2-users-retweets-user-id", metavar="USER_ID", nargs=1, help="POST /2/users/{user_id}/retweets")
    p.add_argument("--data", metavar="JSON", help="Request body as a JSON string (POST/PUT/PATCH)")
    p.add_argument("--data-file", metavar="PATH", help="Request body from a JSON file (POST/PUT/PATCH)")
    p.add_argument("--url", default=os.environ.get("TWITTER_API_URL", "http://localhost:8061"),
                   help="API base URL (default: $TWITTER_API_URL or http://localhost:8061)")
    args = p.parse_args()
    base = args.url.rstrip("/")

    try:
        return _dispatch(args, base)
    except urllib.error.HTTPError as e:
        print(f"HTTP {e.code}: {e.read().decode()}", file=sys.stderr)
        return 1
    except urllib.error.URLError as e:
        print(f"Connection error: {e.reason}", file=sys.stderr)
        return 1


def _dispatch(args, base):
    if args.get_2_users_me:
        return show(api_get(base, "/2/users/me"))
    if args.get_2_users_by_username_username:
        return show(api_get(base, _fill('/2/users/by/username/{username}', args.get_2_users_by_username_username)))
    if args.get_2_users_user_id:
        return show(api_get(base, _fill('/2/users/{user_id}', args.get_2_users_user_id)))
    if args.get_2_users_tweets_user_id:
        return show(api_get(base, _fill('/2/users/{user_id}/tweets', args.get_2_users_tweets_user_id)))
    if args.get_2_users_followers_user_id:
        return show(api_get(base, _fill('/2/users/{user_id}/followers', args.get_2_users_followers_user_id)))
    if args.get_2_users_following_user_id:
        return show(api_get(base, _fill('/2/users/{user_id}/following', args.get_2_users_following_user_id)))
    if args.get_2_tweets:
        return show(api_get(base, "/2/tweets"))
    if args.get_2_tweets_search_recent:
        return show(api_get(base, "/2/tweets/search/recent"))
    if args.get_2_tweets_tweet_id:
        return show(api_get(base, _fill('/2/tweets/{tweet_id}', args.get_2_tweets_tweet_id)))
    if args.post_2_tweets:
        return show(api_send(base, '/2/tweets', 'POST', _body(args)))
    if args.delete_2_tweets_tweet_id:
        return show(api_delete(base, _fill('/2/tweets/{tweet_id}', args.delete_2_tweets_tweet_id)))
    if args.post_2_users_likes_user_id:
        return show(api_send(base, _fill('/2/users/{user_id}/likes', args.post_2_users_likes_user_id), 'POST', _body(args)))
    if args.post_2_users_retweets_user_id:
        return show(api_send(base, _fill('/2/users/{user_id}/retweets', args.post_2_users_retweets_user_id), 'POST', _body(args)))
    print("No endpoint flag provided. Use -h to list available endpoints.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
