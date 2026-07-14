#!/usr/bin/env python3
"""CLI helper for the Google Drive API (Mock) mock API.

Generated read/write helper: one flag per endpoint. Base URL comes from
$GOOGLE_DRIVE_API_URL (override with --url). POST/PUT/PATCH bodies are read from --data
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
    p = argparse.ArgumentParser(description="Query the Google Drive API (Mock) mock API")
    p.add_argument("--get-drive-about", action="store_true", help="GET /drive/v3/about")
    p.add_argument("--get-drive-files", action="store_true", help="GET /drive/v3/files")
    p.add_argument("--get-drive-files-file-id", metavar="FILE_ID", nargs=1, help="GET /drive/v3/files/{file_id}")
    p.add_argument("--post-drive-files", action="store_true", help="POST /drive/v3/files")
    p.add_argument("--patch-drive-files-file-id", metavar="FILE_ID", nargs=1, help="PATCH /drive/v3/files/{file_id}")
    p.add_argument("--post-drive-files-trash-file-id", metavar="FILE_ID", nargs=1, help="POST /drive/v3/files/{file_id}/trash")
    p.add_argument("--delete-drive-files-file-id", metavar="FILE_ID", nargs=1, help="DELETE /drive/v3/files/{file_id}")
    p.add_argument("--get-drive-files-permissions-file-id", metavar="FILE_ID", nargs=1, help="GET /drive/v3/files/{file_id}/permissions")
    p.add_argument("--post-drive-files-permissions-file-id", metavar="FILE_ID", nargs=1, help="POST /drive/v3/files/{file_id}/permissions")
    p.add_argument("--delete-drive-files-permissions-file-id-permission-id", metavar="FILE_ID/PERMISSION_ID", nargs=2, help="DELETE /drive/v3/files/{file_id}/permissions/{permission_id}")
    p.add_argument("--data", metavar="JSON", help="Request body as a JSON string (POST/PUT/PATCH)")
    p.add_argument("--data-file", metavar="PATH", help="Request body from a JSON file (POST/PUT/PATCH)")
    p.add_argument("--url", default=os.environ.get("GOOGLE_DRIVE_API_URL", "http://localhost:8018"),
                   help="API base URL (default: $GOOGLE_DRIVE_API_URL or http://localhost:8018)")
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
    if args.get_drive_about:
        return show(api_get(base, "/drive/v3/about"))
    if args.get_drive_files:
        return show(api_get(base, "/drive/v3/files"))
    if args.get_drive_files_file_id:
        return show(api_get(base, _fill('/drive/v3/files/{file_id}', args.get_drive_files_file_id)))
    if args.post_drive_files:
        return show(api_send(base, '/drive/v3/files', 'POST', _body(args)))
    if args.patch_drive_files_file_id:
        return show(api_send(base, _fill('/drive/v3/files/{file_id}', args.patch_drive_files_file_id), 'PATCH', _body(args)))
    if args.post_drive_files_trash_file_id:
        return show(api_send(base, _fill('/drive/v3/files/{file_id}/trash', args.post_drive_files_trash_file_id), 'POST', _body(args)))
    if args.delete_drive_files_file_id:
        return show(api_delete(base, _fill('/drive/v3/files/{file_id}', args.delete_drive_files_file_id)))
    if args.get_drive_files_permissions_file_id:
        return show(api_get(base, _fill('/drive/v3/files/{file_id}/permissions', args.get_drive_files_permissions_file_id)))
    if args.post_drive_files_permissions_file_id:
        return show(api_send(base, _fill('/drive/v3/files/{file_id}/permissions', args.post_drive_files_permissions_file_id), 'POST', _body(args)))
    if args.delete_drive_files_permissions_file_id_permission_id:
        return show(api_delete(base, _fill('/drive/v3/files/{file_id}/permissions/{permission_id}', args.delete_drive_files_permissions_file_id_permission_id)))
    print("No endpoint flag provided. Use -h to list available endpoints.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
