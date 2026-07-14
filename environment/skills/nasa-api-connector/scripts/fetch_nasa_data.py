#!/usr/bin/env python3
"""CLI helper for the NASA Open API (Mock) mock API.

Generated read/write helper: one flag per endpoint. Base URL comes from
$NASA_API_URL (override with --url). POST/PUT/PATCH bodies are read from --data
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
    p = argparse.ArgumentParser(description="Query the NASA Open API (Mock) mock API")
    p.add_argument("--get-planetary-apod", action="store_true", help="GET /planetary/apod")
    p.add_argument("--get-mars-photos-api-rovers-photos-rover", metavar="ROVER", nargs=1, help="GET /mars-photos/api/v1/rovers/{rover}/photos")
    p.add_argument("--get-mars-photos-api-rovers-rover", metavar="ROVER", nargs=1, help="GET /mars-photos/api/v1/rovers/{rover}")
    p.add_argument("--get-neo-rest-feed", action="store_true", help="GET /neo/rest/v1/feed")
    p.add_argument("--get-neo-rest-neo-neo-id", metavar="NEO_ID", nargs=1, help="GET /neo/rest/v1/neo/{neo_id}")
    p.add_argument("--get-epic-api-natural", action="store_true", help="GET /EPIC/api/natural")
    p.add_argument("--data", metavar="JSON", help="Request body as a JSON string (POST/PUT/PATCH)")
    p.add_argument("--data-file", metavar="PATH", help="Request body from a JSON file (POST/PUT/PATCH)")
    p.add_argument("--url", default=os.environ.get("NASA_API_URL", "http://localhost:8077"),
                   help="API base URL (default: $NASA_API_URL or http://localhost:8077)")
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
    if args.get_planetary_apod:
        return show(api_get(base, "/planetary/apod"))
    if args.get_mars_photos_api_rovers_photos_rover:
        return show(api_get(base, _fill('/mars-photos/api/v1/rovers/{rover}/photos', args.get_mars_photos_api_rovers_photos_rover)))
    if args.get_mars_photos_api_rovers_rover:
        return show(api_get(base, _fill('/mars-photos/api/v1/rovers/{rover}', args.get_mars_photos_api_rovers_rover)))
    if args.get_neo_rest_feed:
        return show(api_get(base, "/neo/rest/v1/feed"))
    if args.get_neo_rest_neo_neo_id:
        return show(api_get(base, _fill('/neo/rest/v1/neo/{neo_id}', args.get_neo_rest_neo_neo_id)))
    if args.get_epic_api_natural:
        return show(api_get(base, "/EPIC/api/natural"))
    print("No endpoint flag provided. Use -h to list available endpoints.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
