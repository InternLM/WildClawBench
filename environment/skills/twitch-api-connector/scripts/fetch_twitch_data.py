#!/usr/bin/env python3
"""CLI helper for the Twitch Helix API (Mock) mock API.

Generated read/write helper: one flag per endpoint. Base URL comes from
$TWITCH_API_URL (override with --url). POST/PUT/PATCH bodies are read from --data
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
    p = argparse.ArgumentParser(description="Query the Twitch Helix API (Mock) mock API")
    p.add_argument("--get-helix-users", action="store_true", help="GET /helix/users")
    p.add_argument("--get-helix-streams", action="store_true", help="GET /helix/streams")
    p.add_argument("--get-helix-channels", action="store_true", help="GET /helix/channels")
    p.add_argument("--get-helix-channels-followers", action="store_true", help="GET /helix/channels/followers")
    p.add_argument("--get-helix-games-top", action="store_true", help="GET /helix/games/top")
    p.add_argument("--get-helix-games", action="store_true", help="GET /helix/games")
    p.add_argument("--get-helix-clips", action="store_true", help="GET /helix/clips")
    p.add_argument("--data", metavar="JSON", help="Request body as a JSON string (POST/PUT/PATCH)")
    p.add_argument("--data-file", metavar="PATH", help="Request body from a JSON file (POST/PUT/PATCH)")
    p.add_argument("--url", default=os.environ.get("TWITCH_API_URL", "http://localhost:8064"),
                   help="API base URL (default: $TWITCH_API_URL or http://localhost:8064)")
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
    if args.get_helix_users:
        return show(api_get(base, "/helix/users"))
    if args.get_helix_streams:
        return show(api_get(base, "/helix/streams"))
    if args.get_helix_channels:
        return show(api_get(base, "/helix/channels"))
    if args.get_helix_channels_followers:
        return show(api_get(base, "/helix/channels/followers"))
    if args.get_helix_games_top:
        return show(api_get(base, "/helix/games/top"))
    if args.get_helix_games:
        return show(api_get(base, "/helix/games"))
    if args.get_helix_clips:
        return show(api_get(base, "/helix/clips"))
    print("No endpoint flag provided. Use -h to list available endpoints.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
