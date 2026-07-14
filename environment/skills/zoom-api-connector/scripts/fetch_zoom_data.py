#!/usr/bin/env python3
"""CLI helper for the Zoom API (Mock) mock API.

Generated read/write helper: one flag per endpoint. Base URL comes from
$ZOOM_API_URL (override with --url). POST/PUT/PATCH bodies are read from --data
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
    p = argparse.ArgumentParser(description="Query the Zoom API (Mock) mock API")
    p.add_argument("--get-users-me", action="store_true", help="GET /v2/users/me")
    p.add_argument("--get-users-meetings-user-id", metavar="USER_ID", nargs=1, help="GET /v2/users/{user_id}/meetings")
    p.add_argument("--post-users-meetings-user-id", metavar="USER_ID", nargs=1, help="POST /v2/users/{user_id}/meetings")
    p.add_argument("--get-meetings-meeting-id", metavar="MEETING_ID", nargs=1, help="GET /v2/meetings/{meeting_id}")
    p.add_argument("--patch-meetings-meeting-id", metavar="MEETING_ID", nargs=1, help="PATCH /v2/meetings/{meeting_id}")
    p.add_argument("--delete-meetings-meeting-id", metavar="MEETING_ID", nargs=1, help="DELETE /v2/meetings/{meeting_id}")
    p.add_argument("--get-meetings-recordings-meeting-id", metavar="MEETING_ID", nargs=1, help="GET /v2/meetings/{meeting_id}/recordings")
    p.add_argument("--get-meetings-registrants-meeting-id", metavar="MEETING_ID", nargs=1, help="GET /v2/meetings/{meeting_id}/registrants")
    p.add_argument("--data", metavar="JSON", help="Request body as a JSON string (POST/PUT/PATCH)")
    p.add_argument("--data-file", metavar="PATH", help="Request body from a JSON file (POST/PUT/PATCH)")
    p.add_argument("--url", default=os.environ.get("ZOOM_API_URL", "http://localhost:8028"),
                   help="API base URL (default: $ZOOM_API_URL or http://localhost:8028)")
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
    if args.get_users_me:
        return show(api_get(base, "/v2/users/me"))
    if args.get_users_meetings_user_id:
        return show(api_get(base, _fill('/v2/users/{user_id}/meetings', args.get_users_meetings_user_id)))
    if args.post_users_meetings_user_id:
        return show(api_send(base, _fill('/v2/users/{user_id}/meetings', args.post_users_meetings_user_id), 'POST', _body(args)))
    if args.get_meetings_meeting_id:
        return show(api_get(base, _fill('/v2/meetings/{meeting_id}', args.get_meetings_meeting_id)))
    if args.patch_meetings_meeting_id:
        return show(api_send(base, _fill('/v2/meetings/{meeting_id}', args.patch_meetings_meeting_id), 'PATCH', _body(args)))
    if args.delete_meetings_meeting_id:
        return show(api_delete(base, _fill('/v2/meetings/{meeting_id}', args.delete_meetings_meeting_id)))
    if args.get_meetings_recordings_meeting_id:
        return show(api_get(base, _fill('/v2/meetings/{meeting_id}/recordings', args.get_meetings_recordings_meeting_id)))
    if args.get_meetings_registrants_meeting_id:
        return show(api_get(base, _fill('/v2/meetings/{meeting_id}/registrants', args.get_meetings_registrants_meeting_id)))
    print("No endpoint flag provided. Use -h to list available endpoints.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
