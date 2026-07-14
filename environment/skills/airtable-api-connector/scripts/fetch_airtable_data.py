#!/usr/bin/env python3
"""CLI helper for the Airtable API (Mock) mock API.

Generated read/write helper: one flag per endpoint. Base URL comes from
$AIRTABLE_API_URL (override with --url). POST/PUT/PATCH bodies are read from --data
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
    p = argparse.ArgumentParser(description="Query the Airtable API (Mock) mock API")
    p.add_argument("--get-meta-bases", action="store_true", help="GET /v0/meta/bases")
    p.add_argument("--get-meta-bases-tables-base-id", metavar="BASE_ID", nargs=1, help="GET /v0/meta/bases/{base_id}/tables")
    p.add_argument("--get-root-base-id-table-id-or-name", metavar="BASE_ID/TABLE_ID_OR_NAME", nargs=2, help="GET /v0/{base_id}/{table_id_or_name}")
    p.add_argument("--get-root-base-id-table-id-or-name-record-id", metavar="BASE_ID/TABLE_ID_OR_NAME/RECORD_ID", nargs=3, help="GET /v0/{base_id}/{table_id_or_name}/{record_id}")
    p.add_argument("--post-root-base-id-table-id-or-name", metavar="BASE_ID/TABLE_ID_OR_NAME", nargs=2, help="POST /v0/{base_id}/{table_id_or_name}")
    p.add_argument("--patch-root-base-id-table-id-or-name-record-id", metavar="BASE_ID/TABLE_ID_OR_NAME/RECORD_ID", nargs=3, help="PATCH /v0/{base_id}/{table_id_or_name}/{record_id}")
    p.add_argument("--delete-root-base-id-table-id-or-name-record-id", metavar="BASE_ID/TABLE_ID_OR_NAME/RECORD_ID", nargs=3, help="DELETE /v0/{base_id}/{table_id_or_name}/{record_id}")
    p.add_argument("--data", metavar="JSON", help="Request body as a JSON string (POST/PUT/PATCH)")
    p.add_argument("--data-file", metavar="PATH", help="Request body from a JSON file (POST/PUT/PATCH)")
    p.add_argument("--url", default=os.environ.get("AIRTABLE_API_URL", "http://localhost:8032"),
                   help="API base URL (default: $AIRTABLE_API_URL or http://localhost:8032)")
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
    if args.get_meta_bases:
        return show(api_get(base, "/v0/meta/bases"))
    if args.get_meta_bases_tables_base_id:
        return show(api_get(base, _fill('/v0/meta/bases/{base_id}/tables', args.get_meta_bases_tables_base_id)))
    if args.get_root_base_id_table_id_or_name:
        return show(api_get(base, _fill('/v0/{base_id}/{table_id_or_name}', args.get_root_base_id_table_id_or_name)))
    if args.get_root_base_id_table_id_or_name_record_id:
        return show(api_get(base, _fill('/v0/{base_id}/{table_id_or_name}/{record_id}', args.get_root_base_id_table_id_or_name_record_id)))
    if args.post_root_base_id_table_id_or_name:
        return show(api_send(base, _fill('/v0/{base_id}/{table_id_or_name}', args.post_root_base_id_table_id_or_name), 'POST', _body(args)))
    if args.patch_root_base_id_table_id_or_name_record_id:
        return show(api_send(base, _fill('/v0/{base_id}/{table_id_or_name}/{record_id}', args.patch_root_base_id_table_id_or_name_record_id), 'PATCH', _body(args)))
    if args.delete_root_base_id_table_id_or_name_record_id:
        return show(api_delete(base, _fill('/v0/{base_id}/{table_id_or_name}/{record_id}', args.delete_root_base_id_table_id_or_name_record_id)))
    print("No endpoint flag provided. Use -h to list available endpoints.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
