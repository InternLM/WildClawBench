#!/usr/bin/env python3
"""CLI helper for the Calendly API (Mock) mock API.

Generated read/write helper: one flag per endpoint. Base URL comes from
$CALENDLY_API_URL (override with --url). POST/PUT/PATCH bodies are read from --data
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
    p = argparse.ArgumentParser(description="Query the Calendly API (Mock) mock API")
    p.add_argument("--get-users-me", action="store_true", help="GET /users/me")
    p.add_argument("--get-event-types", action="store_true", help="GET /event_types")
    p.add_argument("--get-event-types-uuid", metavar="UUID", nargs=1, help="GET /event_types/{uuid}")
    p.add_argument("--get-scheduled-events", action="store_true", help="GET /scheduled_events")
    p.add_argument("--get-scheduled-events-uuid", metavar="UUID", nargs=1, help="GET /scheduled_events/{uuid}")
    p.add_argument("--get-scheduled-events-invitees-uuid", metavar="UUID", nargs=1, help="GET /scheduled_events/{uuid}/invitees")
    p.add_argument("--post-scheduled-events", action="store_true", help="POST /scheduled_events")
    p.add_argument("--post-scheduled-events-cancellation-uuid", metavar="UUID", nargs=1, help="POST /scheduled_events/{uuid}/cancellation")
    p.add_argument("--data", metavar="JSON", help="Request body as a JSON string (POST/PUT/PATCH)")
    p.add_argument("--data-file", metavar="PATH", help="Request body from a JSON file (POST/PUT/PATCH)")
    p.add_argument("--url", default=os.environ.get("CALENDLY_API_URL", "http://localhost:8054"),
                   help="API base URL (default: $CALENDLY_API_URL or http://localhost:8054)")
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
        return show(api_get(base, "/users/me"))
    if args.get_event_types:
        return show(api_get(base, "/event_types"))
    if args.get_event_types_uuid:
        return show(api_get(base, _fill('/event_types/{uuid}', args.get_event_types_uuid)))
    if args.get_scheduled_events:
        return show(api_get(base, "/scheduled_events"))
    if args.get_scheduled_events_uuid:
        return show(api_get(base, _fill('/scheduled_events/{uuid}', args.get_scheduled_events_uuid)))
    if args.get_scheduled_events_invitees_uuid:
        return show(api_get(base, _fill('/scheduled_events/{uuid}/invitees', args.get_scheduled_events_invitees_uuid)))
    if args.post_scheduled_events:
        return show(api_send(base, '/scheduled_events', 'POST', _body(args)))
    if args.post_scheduled_events_cancellation_uuid:
        return show(api_send(base, _fill('/scheduled_events/{uuid}/cancellation', args.post_scheduled_events_cancellation_uuid), 'POST', _body(args)))
    print("No endpoint flag provided. Use -h to list available endpoints.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
