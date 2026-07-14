#!/usr/bin/env python3
"""CLI helper for the Notion API (Mock) mock API.

Generated read/write helper: one flag per endpoint. Base URL comes from
$NOTION_API_URL (override with --url). POST/PUT/PATCH bodies are read from --data
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
    p = argparse.ArgumentParser(description="Query the Notion API (Mock) mock API")
    p.add_argument("--get-users", action="store_true", help="GET /v1/users")
    p.add_argument("--get-users-me", action="store_true", help="GET /v1/users/me")
    p.add_argument("--get-users-user-id", metavar="USER_ID", nargs=1, help="GET /v1/users/{user_id}")
    p.add_argument("--get-workspace", action="store_true", help="GET /v1/workspace")
    p.add_argument("--post-search", action="store_true", help="POST /v1/search")
    p.add_argument("--get-databases-database-id", metavar="DATABASE_ID", nargs=1, help="GET /v1/databases/{database_id}")
    p.add_argument("--post-databases-query-database-id", metavar="DATABASE_ID", nargs=1, help="POST /v1/databases/{database_id}/query")
    p.add_argument("--get-pages-page-id", metavar="PAGE_ID", nargs=1, help="GET /v1/pages/{page_id}")
    p.add_argument("--post-pages", action="store_true", help="POST /v1/pages")
    p.add_argument("--patch-pages-page-id", metavar="PAGE_ID", nargs=1, help="PATCH /v1/pages/{page_id}")
    p.add_argument("--delete-pages-page-id", metavar="PAGE_ID", nargs=1, help="DELETE /v1/pages/{page_id}")
    p.add_argument("--get-blocks-children-block-id", metavar="BLOCK_ID", nargs=1, help="GET /v1/blocks/{block_id}/children")
    p.add_argument("--patch-blocks-children-block-id", metavar="BLOCK_ID", nargs=1, help="PATCH /v1/blocks/{block_id}/children")
    p.add_argument("--patch-blocks-block-id", metavar="BLOCK_ID", nargs=1, help="PATCH /v1/blocks/{block_id}")
    p.add_argument("--delete-blocks-block-id", metavar="BLOCK_ID", nargs=1, help="DELETE /v1/blocks/{block_id}")
    p.add_argument("--get-comments", action="store_true", help="GET /v1/comments")
    p.add_argument("--post-comments", action="store_true", help="POST /v1/comments")
    p.add_argument("--data", metavar="JSON", help="Request body as a JSON string (POST/PUT/PATCH)")
    p.add_argument("--data-file", metavar="PATH", help="Request body from a JSON file (POST/PUT/PATCH)")
    p.add_argument("--url", default=os.environ.get("NOTION_API_URL", "http://localhost:8010"),
                   help="API base URL (default: $NOTION_API_URL or http://localhost:8010)")
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
    if args.get_users:
        return show(api_get(base, "/v1/users"))
    if args.get_users_me:
        return show(api_get(base, "/v1/users/me"))
    if args.get_users_user_id:
        return show(api_get(base, _fill('/v1/users/{user_id}', args.get_users_user_id)))
    if args.get_workspace:
        return show(api_get(base, "/v1/workspace"))
    if args.post_search:
        return show(api_send(base, '/v1/search', 'POST', _body(args)))
    if args.get_databases_database_id:
        return show(api_get(base, _fill('/v1/databases/{database_id}', args.get_databases_database_id)))
    if args.post_databases_query_database_id:
        return show(api_send(base, _fill('/v1/databases/{database_id}/query', args.post_databases_query_database_id), 'POST', _body(args)))
    if args.get_pages_page_id:
        return show(api_get(base, _fill('/v1/pages/{page_id}', args.get_pages_page_id)))
    if args.post_pages:
        return show(api_send(base, '/v1/pages', 'POST', _body(args)))
    if args.patch_pages_page_id:
        return show(api_send(base, _fill('/v1/pages/{page_id}', args.patch_pages_page_id), 'PATCH', _body(args)))
    if args.delete_pages_page_id:
        return show(api_delete(base, _fill('/v1/pages/{page_id}', args.delete_pages_page_id)))
    if args.get_blocks_children_block_id:
        return show(api_get(base, _fill('/v1/blocks/{block_id}/children', args.get_blocks_children_block_id)))
    if args.patch_blocks_children_block_id:
        return show(api_send(base, _fill('/v1/blocks/{block_id}/children', args.patch_blocks_children_block_id), 'PATCH', _body(args)))
    if args.patch_blocks_block_id:
        return show(api_send(base, _fill('/v1/blocks/{block_id}', args.patch_blocks_block_id), 'PATCH', _body(args)))
    if args.delete_blocks_block_id:
        return show(api_delete(base, _fill('/v1/blocks/{block_id}', args.delete_blocks_block_id)))
    if args.get_comments:
        return show(api_get(base, "/v1/comments"))
    if args.post_comments:
        return show(api_send(base, '/v1/comments', 'POST', _body(args)))
    print("No endpoint flag provided. Use -h to list available endpoints.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
