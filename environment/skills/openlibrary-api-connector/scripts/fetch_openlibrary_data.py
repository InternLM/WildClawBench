#!/usr/bin/env python3
"""CLI helper for the Open Library API (Mock) mock API.

Generated read/write helper: one flag per endpoint. Base URL comes from
$OPENLIBRARY_API_URL (override with --url). POST/PUT/PATCH bodies are read from --data
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
    p = argparse.ArgumentParser(description="Query the Open Library API (Mock) mock API")
    p.add_argument("--get-search-json", action="store_true", help="GET /search.json")
    p.add_argument("--get-works-work-id", metavar="WORK_ID", nargs=1, help="GET /works/{work_id}.json")
    p.add_argument("--get-works-editions-json-work-id", metavar="WORK_ID", nargs=1, help="GET /works/{work_id}/editions.json")
    p.add_argument("--get-authors-author-id", metavar="AUTHOR_ID", nargs=1, help="GET /authors/{author_id}.json")
    p.add_argument("--get-authors-works-json-author-id", metavar="AUTHOR_ID", nargs=1, help="GET /authors/{author_id}/works.json")
    p.add_argument("--get-subjects-subject", metavar="SUBJECT", nargs=1, help="GET /subjects/{subject}.json")
    p.add_argument("--get-isbn-isbn", metavar="ISBN", nargs=1, help="GET /isbn/{isbn}.json")
    p.add_argument("--data", metavar="JSON", help="Request body as a JSON string (POST/PUT/PATCH)")
    p.add_argument("--data-file", metavar="PATH", help="Request body from a JSON file (POST/PUT/PATCH)")
    p.add_argument("--url", default=os.environ.get("OPENLIBRARY_API_URL", "http://localhost:8078"),
                   help="API base URL (default: $OPENLIBRARY_API_URL or http://localhost:8078)")
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
    if args.get_search_json:
        return show(api_get(base, "/search.json"))
    if args.get_works_work_id:
        return show(api_get(base, _fill('/works/{work_id}.json', args.get_works_work_id)))
    if args.get_works_editions_json_work_id:
        return show(api_get(base, _fill('/works/{work_id}/editions.json', args.get_works_editions_json_work_id)))
    if args.get_authors_author_id:
        return show(api_get(base, _fill('/authors/{author_id}.json', args.get_authors_author_id)))
    if args.get_authors_works_json_author_id:
        return show(api_get(base, _fill('/authors/{author_id}/works.json', args.get_authors_works_json_author_id)))
    if args.get_subjects_subject:
        return show(api_get(base, _fill('/subjects/{subject}.json', args.get_subjects_subject)))
    if args.get_isbn_isbn:
        return show(api_get(base, _fill('/isbn/{isbn}.json', args.get_isbn_isbn)))
    print("No endpoint flag provided. Use -h to list available endpoints.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
