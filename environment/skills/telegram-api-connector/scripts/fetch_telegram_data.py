#!/usr/bin/env python3
"""CLI helper for the Telegram Bot API (Mock) mock API.

Generated read/write helper: one flag per endpoint. Base URL comes from
$TELEGRAM_API_URL (override with --url). POST/PUT/PATCH bodies are read from --data
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
    p = argparse.ArgumentParser(description="Query the Telegram Bot API (Mock) mock API")
    p.add_argument("--get-bot-getme", action="store_true", help="GET /bot/getMe")
    p.add_argument("--post-bot-sendmessage", action="store_true", help="POST /bot/sendMessage")
    p.add_argument("--post-bot-sendphoto", action="store_true", help="POST /bot/sendPhoto")
    p.add_argument("--post-bot-editmessagetext", action="store_true", help="POST /bot/editMessageText")
    p.add_argument("--post-bot-deletemessage", action="store_true", help="POST /bot/deleteMessage")
    p.add_argument("--get-bot-getupdates", action="store_true", help="GET /bot/getUpdates")
    p.add_argument("--get-bot-getchat", action="store_true", help="GET /bot/getChat")
    p.add_argument("--get-bot-getchatmember", action="store_true", help="GET /bot/getChatMember")
    p.add_argument("--data", metavar="JSON", help="Request body as a JSON string (POST/PUT/PATCH)")
    p.add_argument("--data-file", metavar="PATH", help="Request body from a JSON file (POST/PUT/PATCH)")
    p.add_argument("--url", default=os.environ.get("TELEGRAM_API_URL", "http://localhost:8063"),
                   help="API base URL (default: $TELEGRAM_API_URL or http://localhost:8063)")
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
    if args.get_bot_getme:
        return show(api_get(base, "/bot/getMe"))
    if args.post_bot_sendmessage:
        return show(api_send(base, '/bot/sendMessage', 'POST', _body(args)))
    if args.post_bot_sendphoto:
        return show(api_send(base, '/bot/sendPhoto', 'POST', _body(args)))
    if args.post_bot_editmessagetext:
        return show(api_send(base, '/bot/editMessageText', 'POST', _body(args)))
    if args.post_bot_deletemessage:
        return show(api_send(base, '/bot/deleteMessage', 'POST', _body(args)))
    if args.get_bot_getupdates:
        return show(api_get(base, "/bot/getUpdates"))
    if args.get_bot_getchat:
        return show(api_get(base, "/bot/getChat"))
    if args.get_bot_getchatmember:
        return show(api_get(base, "/bot/getChatMember"))
    print("No endpoint flag provided. Use -h to list available endpoints.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
