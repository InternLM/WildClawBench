#!/usr/bin/env python3
"""CLI helper for the Slack Web API (Mock) mock API.

Generated read/write helper: one flag per endpoint. Base URL comes from
$SLACK_API_URL (override with --url). POST/PUT/PATCH bodies are read from --data
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
    p = argparse.ArgumentParser(description="Query the Slack Web API (Mock) mock API")
    p.add_argument("--get-api-auth-test", action="store_true", help="GET /api/auth.test")
    p.add_argument("--post-api-auth-test", action="store_true", help="POST /api/auth.test")
    p.add_argument("--get-api-team-info", action="store_true", help="GET /api/team.info")
    p.add_argument("--get-api-users-list", action="store_true", help="GET /api/users.list")
    p.add_argument("--get-api-users-info", action="store_true", help="GET /api/users.info")
    p.add_argument("--post-api-users-setpresence", action="store_true", help="POST /api/users.setPresence")
    p.add_argument("--get-api-conversations-list", action="store_true", help="GET /api/conversations.list")
    p.add_argument("--get-api-conversations-info", action="store_true", help="GET /api/conversations.info")
    p.add_argument("--post-api-conversations-create", action="store_true", help="POST /api/conversations.create")
    p.add_argument("--post-api-conversations-archive", action="store_true", help="POST /api/conversations.archive")
    p.add_argument("--get-api-conversations-members", action="store_true", help="GET /api/conversations.members")
    p.add_argument("--post-api-conversations-invite", action="store_true", help="POST /api/conversations.invite")
    p.add_argument("--get-api-conversations-history", action="store_true", help="GET /api/conversations.history")
    p.add_argument("--get-api-conversations-replies", action="store_true", help="GET /api/conversations.replies")
    p.add_argument("--post-api-chat-postmessage", action="store_true", help="POST /api/chat.postMessage")
    p.add_argument("--post-api-chat-update", action="store_true", help="POST /api/chat.update")
    p.add_argument("--post-api-chat-delete", action="store_true", help="POST /api/chat.delete")
    p.add_argument("--post-api-reactions-add", action="store_true", help="POST /api/reactions.add")
    p.add_argument("--get-api-search-messages", action="store_true", help="GET /api/search.messages")
    p.add_argument("--data", metavar="JSON", help="Request body as a JSON string (POST/PUT/PATCH)")
    p.add_argument("--data-file", metavar="PATH", help="Request body from a JSON file (POST/PUT/PATCH)")
    p.add_argument("--url", default=os.environ.get("SLACK_API_URL", "http://localhost:8013"),
                   help="API base URL (default: $SLACK_API_URL or http://localhost:8013)")
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
    if args.get_api_auth_test:
        return show(api_get(base, "/api/auth.test"))
    if args.post_api_auth_test:
        return show(api_send(base, '/api/auth.test', 'POST', _body(args)))
    if args.get_api_team_info:
        return show(api_get(base, "/api/team.info"))
    if args.get_api_users_list:
        return show(api_get(base, "/api/users.list"))
    if args.get_api_users_info:
        return show(api_get(base, "/api/users.info"))
    if args.post_api_users_setpresence:
        return show(api_send(base, '/api/users.setPresence', 'POST', _body(args)))
    if args.get_api_conversations_list:
        return show(api_get(base, "/api/conversations.list"))
    if args.get_api_conversations_info:
        return show(api_get(base, "/api/conversations.info"))
    if args.post_api_conversations_create:
        return show(api_send(base, '/api/conversations.create', 'POST', _body(args)))
    if args.post_api_conversations_archive:
        return show(api_send(base, '/api/conversations.archive', 'POST', _body(args)))
    if args.get_api_conversations_members:
        return show(api_get(base, "/api/conversations.members"))
    if args.post_api_conversations_invite:
        return show(api_send(base, '/api/conversations.invite', 'POST', _body(args)))
    if args.get_api_conversations_history:
        return show(api_get(base, "/api/conversations.history"))
    if args.get_api_conversations_replies:
        return show(api_get(base, "/api/conversations.replies"))
    if args.post_api_chat_postmessage:
        return show(api_send(base, '/api/chat.postMessage', 'POST', _body(args)))
    if args.post_api_chat_update:
        return show(api_send(base, '/api/chat.update', 'POST', _body(args)))
    if args.post_api_chat_delete:
        return show(api_send(base, '/api/chat.delete', 'POST', _body(args)))
    if args.post_api_reactions_add:
        return show(api_send(base, '/api/reactions.add', 'POST', _body(args)))
    if args.get_api_search_messages:
        return show(api_get(base, "/api/search.messages"))
    print("No endpoint flag provided. Use -h to list available endpoints.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
