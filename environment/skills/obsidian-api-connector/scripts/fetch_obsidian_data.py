#!/usr/bin/env python3
"""CLI helper for the Obsidian API (Mock) mock API.

Generated read/write helper: one flag per endpoint. Base URL comes from
$OBSIDIAN_API_URL (override with --url). POST/PUT/PATCH bodies are read from --data
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
    p = argparse.ArgumentParser(description="Query the Obsidian API (Mock) mock API")
    p.add_argument("--get-vault", action="store_true", help="GET /vault")
    p.add_argument("--get-vault-notes", action="store_true", help="GET /vault/notes")
    p.add_argument("--get-vault-notes-path-path", metavar="PATH:PATH", nargs=1, help="GET /vault/notes/{path:path}")
    p.add_argument("--post-vault-notes", action="store_true", help="POST /vault/notes")
    p.add_argument("--put-vault-notes-path-path", metavar="PATH:PATH", nargs=1, help="PUT /vault/notes/{path:path}")
    p.add_argument("--delete-vault-notes-path-path", metavar="PATH:PATH", nargs=1, help="DELETE /vault/notes/{path:path}")
    p.add_argument("--get-vault-search", action="store_true", help="GET /vault/search")
    p.add_argument("--get-vault-backlinks-path-path", metavar="PATH:PATH", nargs=1, help="GET /vault/backlinks/{path:path}")
    p.add_argument("--get-vault-daily-date-str", metavar="DATE_STR", nargs=1, help="GET /vault/daily/{date_str}")
    p.add_argument("--data", metavar="JSON", help="Request body as a JSON string (POST/PUT/PATCH)")
    p.add_argument("--data-file", metavar="PATH", help="Request body from a JSON file (POST/PUT/PATCH)")
    p.add_argument("--url", default=os.environ.get("OBSIDIAN_API_URL", "http://localhost:8014"),
                   help="API base URL (default: $OBSIDIAN_API_URL or http://localhost:8014)")
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
    if args.get_vault:
        return show(api_get(base, "/vault"))
    if args.get_vault_notes:
        return show(api_get(base, "/vault/notes"))
    if args.get_vault_notes_path_path:
        return show(api_get(base, _fill('/vault/notes/{path:path}', args.get_vault_notes_path_path)))
    if args.post_vault_notes:
        return show(api_send(base, '/vault/notes', 'POST', _body(args)))
    if args.put_vault_notes_path_path:
        return show(api_send(base, _fill('/vault/notes/{path:path}', args.put_vault_notes_path_path), 'PUT', _body(args)))
    if args.delete_vault_notes_path_path:
        return show(api_delete(base, _fill('/vault/notes/{path:path}', args.delete_vault_notes_path_path)))
    if args.get_vault_search:
        return show(api_get(base, "/vault/search"))
    if args.get_vault_backlinks_path_path:
        return show(api_get(base, _fill('/vault/backlinks/{path:path}', args.get_vault_backlinks_path_path)))
    if args.get_vault_daily_date_str:
        return show(api_get(base, _fill('/vault/daily/{date_str}', args.get_vault_daily_date_str)))
    print("No endpoint flag provided. Use -h to list available endpoints.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
