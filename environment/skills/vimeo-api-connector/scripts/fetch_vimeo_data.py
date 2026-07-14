#!/usr/bin/env python3
"""CLI helper for the Vimeo API (Mock) mock API.

Generated read/write helper: one flag per endpoint. Base URL comes from
$VIMEO_API_URL (override with --url). POST/PUT/PATCH bodies are read from --data
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
    p = argparse.ArgumentParser(description="Query the Vimeo API (Mock) mock API")
    p.add_argument("--get-me", action="store_true", help="GET /me")
    p.add_argument("--get-me-videos", action="store_true", help="GET /me/videos")
    p.add_argument("--get-videos-video-id", metavar="VIDEO_ID", nargs=1, help="GET /videos/{video_id}")
    p.add_argument("--get-users-user-id", metavar="USER_ID", nargs=1, help="GET /users/{user_id}")
    p.add_argument("--get-users-videos-user-id", metavar="USER_ID", nargs=1, help="GET /users/{user_id}/videos")
    p.add_argument("--data", metavar="JSON", help="Request body as a JSON string (POST/PUT/PATCH)")
    p.add_argument("--data-file", metavar="PATH", help="Request body from a JSON file (POST/PUT/PATCH)")
    p.add_argument("--url", default=os.environ.get("VIMEO_API_URL", "http://localhost:8099"),
                   help="API base URL (default: $VIMEO_API_URL or http://localhost:8099)")
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
    if args.get_me:
        return show(api_get(base, "/me"))
    if args.get_me_videos:
        return show(api_get(base, "/me/videos"))
    if args.get_videos_video_id:
        return show(api_get(base, _fill('/videos/{video_id}', args.get_videos_video_id)))
    if args.get_users_user_id:
        return show(api_get(base, _fill('/users/{user_id}', args.get_users_user_id)))
    if args.get_users_videos_user_id:
        return show(api_get(base, _fill('/users/{user_id}/videos', args.get_users_videos_user_id)))
    print("No endpoint flag provided. Use -h to list available endpoints.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
