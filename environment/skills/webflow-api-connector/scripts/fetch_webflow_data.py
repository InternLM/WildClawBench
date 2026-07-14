#!/usr/bin/env python3
"""CLI helper for the Webflow Data API (Mock) mock API.

Generated read/write helper: one flag per endpoint. Base URL comes from
$WEBFLOW_API_URL (override with --url). POST/PUT/PATCH bodies are read from --data
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
    p = argparse.ArgumentParser(description="Query the Webflow Data API (Mock) mock API")
    p.add_argument("--get-sites", action="store_true", help="GET /v2/sites")
    p.add_argument("--get-sites-site-id", metavar="SITE_ID", nargs=1, help="GET /v2/sites/{site_id}")
    p.add_argument("--get-sites-collections-site-id", metavar="SITE_ID", nargs=1, help="GET /v2/sites/{site_id}/collections")
    p.add_argument("--get-collections-items-collection-id", metavar="COLLECTION_ID", nargs=1, help="GET /v2/collections/{collection_id}/items")
    p.add_argument("--post-collections-items-collection-id", metavar="COLLECTION_ID", nargs=1, help="POST /v2/collections/{collection_id}/items")
    p.add_argument("--data", metavar="JSON", help="Request body as a JSON string (POST/PUT/PATCH)")
    p.add_argument("--data-file", metavar="PATH", help="Request body from a JSON file (POST/PUT/PATCH)")
    p.add_argument("--url", default=os.environ.get("WEBFLOW_API_URL", "http://localhost:8100"),
                   help="API base URL (default: $WEBFLOW_API_URL or http://localhost:8100)")
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
    if args.get_sites:
        return show(api_get(base, "/v2/sites"))
    if args.get_sites_site_id:
        return show(api_get(base, _fill('/v2/sites/{site_id}', args.get_sites_site_id)))
    if args.get_sites_collections_site_id:
        return show(api_get(base, _fill('/v2/sites/{site_id}/collections', args.get_sites_collections_site_id)))
    if args.get_collections_items_collection_id:
        return show(api_get(base, _fill('/v2/collections/{collection_id}/items', args.get_collections_items_collection_id)))
    if args.post_collections_items_collection_id:
        return show(api_send(base, _fill('/v2/collections/{collection_id}/items', args.post_collections_items_collection_id), 'POST', _body(args)))
    print("No endpoint flag provided. Use -h to list available endpoints.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
