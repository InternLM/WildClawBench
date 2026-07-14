#!/usr/bin/env python3
"""CLI helper for the Contentful API (Mock) mock API.

Generated read/write helper: one flag per endpoint. Base URL comes from
$CONTENTFUL_API_URL (override with --url). POST/PUT/PATCH bodies are read from --data
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
    p = argparse.ArgumentParser(description="Query the Contentful API (Mock) mock API")
    p.add_argument("--get-spaces-space-id", metavar="SPACE_ID", nargs=1, help="GET /spaces/{space_id}")
    p.add_argument("--get-spaces-environments-content-types-space-id-env-id", metavar="SPACE_ID/ENV_ID", nargs=2, help="GET /spaces/{space_id}/environments/{env_id}/content_types")
    p.add_argument("--get-spaces-environments-content-types-space-id-env-id-content-type-id", metavar="SPACE_ID/ENV_ID/CONTENT_TYPE_ID", nargs=3, help="GET /spaces/{space_id}/environments/{env_id}/content_types/{content_type_id}")
    p.add_argument("--get-spaces-environments-entries-space-id-env-id", metavar="SPACE_ID/ENV_ID", nargs=2, help="GET /spaces/{space_id}/environments/{env_id}/entries")
    p.add_argument("--get-spaces-environments-entries-space-id-env-id-entry-id", metavar="SPACE_ID/ENV_ID/ENTRY_ID", nargs=3, help="GET /spaces/{space_id}/environments/{env_id}/entries/{entry_id}")
    p.add_argument("--post-spaces-environments-entries-space-id-env-id", metavar="SPACE_ID/ENV_ID", nargs=2, help="POST /spaces/{space_id}/environments/{env_id}/entries")
    p.add_argument("--put-spaces-environments-entries-space-id-env-id-entry-id", metavar="SPACE_ID/ENV_ID/ENTRY_ID", nargs=3, help="PUT /spaces/{space_id}/environments/{env_id}/entries/{entry_id}")
    p.add_argument("--delete-spaces-environments-entries-space-id-env-id-entry-id", metavar="SPACE_ID/ENV_ID/ENTRY_ID", nargs=3, help="DELETE /spaces/{space_id}/environments/{env_id}/entries/{entry_id}")
    p.add_argument("--get-spaces-environments-assets-space-id-env-id", metavar="SPACE_ID/ENV_ID", nargs=2, help="GET /spaces/{space_id}/environments/{env_id}/assets")
    p.add_argument("--get-spaces-environments-assets-space-id-env-id-asset-id", metavar="SPACE_ID/ENV_ID/ASSET_ID", nargs=3, help="GET /spaces/{space_id}/environments/{env_id}/assets/{asset_id}")
    p.add_argument("--data", metavar="JSON", help="Request body as a JSON string (POST/PUT/PATCH)")
    p.add_argument("--data-file", metavar="PATH", help="Request body from a JSON file (POST/PUT/PATCH)")
    p.add_argument("--url", default=os.environ.get("CONTENTFUL_API_URL", "http://localhost:8066"),
                   help="API base URL (default: $CONTENTFUL_API_URL or http://localhost:8066)")
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
    if args.get_spaces_space_id:
        return show(api_get(base, _fill('/spaces/{space_id}', args.get_spaces_space_id)))
    if args.get_spaces_environments_content_types_space_id_env_id:
        return show(api_get(base, _fill('/spaces/{space_id}/environments/{env_id}/content_types', args.get_spaces_environments_content_types_space_id_env_id)))
    if args.get_spaces_environments_content_types_space_id_env_id_content_type_id:
        return show(api_get(base, _fill('/spaces/{space_id}/environments/{env_id}/content_types/{content_type_id}', args.get_spaces_environments_content_types_space_id_env_id_content_type_id)))
    if args.get_spaces_environments_entries_space_id_env_id:
        return show(api_get(base, _fill('/spaces/{space_id}/environments/{env_id}/entries', args.get_spaces_environments_entries_space_id_env_id)))
    if args.get_spaces_environments_entries_space_id_env_id_entry_id:
        return show(api_get(base, _fill('/spaces/{space_id}/environments/{env_id}/entries/{entry_id}', args.get_spaces_environments_entries_space_id_env_id_entry_id)))
    if args.post_spaces_environments_entries_space_id_env_id:
        return show(api_send(base, _fill('/spaces/{space_id}/environments/{env_id}/entries', args.post_spaces_environments_entries_space_id_env_id), 'POST', _body(args)))
    if args.put_spaces_environments_entries_space_id_env_id_entry_id:
        return show(api_send(base, _fill('/spaces/{space_id}/environments/{env_id}/entries/{entry_id}', args.put_spaces_environments_entries_space_id_env_id_entry_id), 'PUT', _body(args)))
    if args.delete_spaces_environments_entries_space_id_env_id_entry_id:
        return show(api_delete(base, _fill('/spaces/{space_id}/environments/{env_id}/entries/{entry_id}', args.delete_spaces_environments_entries_space_id_env_id_entry_id)))
    if args.get_spaces_environments_assets_space_id_env_id:
        return show(api_get(base, _fill('/spaces/{space_id}/environments/{env_id}/assets', args.get_spaces_environments_assets_space_id_env_id)))
    if args.get_spaces_environments_assets_space_id_env_id_asset_id:
        return show(api_get(base, _fill('/spaces/{space_id}/environments/{env_id}/assets/{asset_id}', args.get_spaces_environments_assets_space_id_env_id_asset_id)))
    print("No endpoint flag provided. Use -h to list available endpoints.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
