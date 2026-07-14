#!/usr/bin/env python3
"""CLI helper for the Algolia API (Mock) mock API.

Generated read/write helper: one flag per endpoint. Base URL comes from
$ALGOLIA_API_URL (override with --url). POST/PUT/PATCH bodies are read from --data
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
    p = argparse.ArgumentParser(description="Query the Algolia API (Mock) mock API")
    p.add_argument("--get-1-indexes", action="store_true", help="GET /1/indexes")
    p.add_argument("--get-1-indexes-settings-index", metavar="INDEX", nargs=1, help="GET /1/indexes/{index}/settings")
    p.add_argument("--post-1-indexes-query-index", metavar="INDEX", nargs=1, help="POST /1/indexes/{index}/query")
    p.add_argument("--get-1-indexes-index-object-id", metavar="INDEX/OBJECT_ID", nargs=2, help="GET /1/indexes/{index}/{object_id}")
    p.add_argument("--post-1-indexes-index", metavar="INDEX", nargs=1, help="POST /1/indexes/{index}")
    p.add_argument("--put-1-indexes-index-object-id", metavar="INDEX/OBJECT_ID", nargs=2, help="PUT /1/indexes/{index}/{object_id}")
    p.add_argument("--delete-1-indexes-index-object-id", metavar="INDEX/OBJECT_ID", nargs=2, help="DELETE /1/indexes/{index}/{object_id}")
    p.add_argument("--data", metavar="JSON", help="Request body as a JSON string (POST/PUT/PATCH)")
    p.add_argument("--data-file", metavar="PATH", help="Request body from a JSON file (POST/PUT/PATCH)")
    p.add_argument("--url", default=os.environ.get("ALGOLIA_API_URL", "http://localhost:8067"),
                   help="API base URL (default: $ALGOLIA_API_URL or http://localhost:8067)")
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
    if args.get_1_indexes:
        return show(api_get(base, "/1/indexes"))
    if args.get_1_indexes_settings_index:
        return show(api_get(base, _fill('/1/indexes/{index}/settings', args.get_1_indexes_settings_index)))
    if args.post_1_indexes_query_index:
        return show(api_send(base, _fill('/1/indexes/{index}/query', args.post_1_indexes_query_index), 'POST', _body(args)))
    if args.get_1_indexes_index_object_id:
        return show(api_get(base, _fill('/1/indexes/{index}/{object_id}', args.get_1_indexes_index_object_id)))
    if args.post_1_indexes_index:
        return show(api_send(base, _fill('/1/indexes/{index}', args.post_1_indexes_index), 'POST', _body(args)))
    if args.put_1_indexes_index_object_id:
        return show(api_send(base, _fill('/1/indexes/{index}/{object_id}', args.put_1_indexes_index_object_id), 'PUT', _body(args)))
    if args.delete_1_indexes_index_object_id:
        return show(api_delete(base, _fill('/1/indexes/{index}/{object_id}', args.delete_1_indexes_index_object_id)))
    print("No endpoint flag provided. Use -h to list available endpoints.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
