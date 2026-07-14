#!/usr/bin/env python3
"""CLI helper for the Gmail API (Mock) mock API.

Generated read/write helper: one flag per endpoint. Base URL comes from
$GMAIL_API_URL (override with --url). POST/PUT/PATCH bodies are read from --data
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
    p = argparse.ArgumentParser(description="Query the Gmail API (Mock) mock API")
    p.add_argument("--get-gmail-users-me-profile", action="store_true", help="GET /gmail/v1/users/me/profile")
    p.add_argument("--get-gmail-users-me-labels", action="store_true", help="GET /gmail/v1/users/me/labels")
    p.add_argument("--get-gmail-users-me-labels-label-id", metavar="LABEL_ID", nargs=1, help="GET /gmail/v1/users/me/labels/{label_id}")
    p.add_argument("--post-gmail-users-me-labels", action="store_true", help="POST /gmail/v1/users/me/labels")
    p.add_argument("--get-gmail-users-me-messages", action="store_true", help="GET /gmail/v1/users/me/messages")
    p.add_argument("--get-gmail-users-me-messages-message-id", metavar="MESSAGE_ID", nargs=1, help="GET /gmail/v1/users/me/messages/{message_id}")
    p.add_argument("--post-gmail-users-me-messages-send", action="store_true", help="POST /gmail/v1/users/me/messages/send")
    p.add_argument("--post-gmail-users-me-messages-modify-message-id", metavar="MESSAGE_ID", nargs=1, help="POST /gmail/v1/users/me/messages/{message_id}/modify")
    p.add_argument("--post-gmail-users-me-messages-trash-message-id", metavar="MESSAGE_ID", nargs=1, help="POST /gmail/v1/users/me/messages/{message_id}/trash")
    p.add_argument("--delete-gmail-users-me-messages-message-id", metavar="MESSAGE_ID", nargs=1, help="DELETE /gmail/v1/users/me/messages/{message_id}")
    p.add_argument("--get-gmail-users-me-threads", action="store_true", help="GET /gmail/v1/users/me/threads")
    p.add_argument("--get-gmail-users-me-threads-thread-id", metavar="THREAD_ID", nargs=1, help="GET /gmail/v1/users/me/threads/{thread_id}")
    p.add_argument("--get-gmail-users-me-drafts", action="store_true", help="GET /gmail/v1/users/me/drafts")
    p.add_argument("--get-gmail-users-me-drafts-draft-id", metavar="DRAFT_ID", nargs=1, help="GET /gmail/v1/users/me/drafts/{draft_id}")
    p.add_argument("--post-gmail-users-me-drafts", action="store_true", help="POST /gmail/v1/users/me/drafts")
    p.add_argument("--post-gmail-users-me-drafts-send-draft-id", metavar="DRAFT_ID", nargs=1, help="POST /gmail/v1/users/me/drafts/{draft_id}/send")
    p.add_argument("--data", metavar="JSON", help="Request body as a JSON string (POST/PUT/PATCH)")
    p.add_argument("--data-file", metavar="PATH", help="Request body from a JSON file (POST/PUT/PATCH)")
    p.add_argument("--url", default=os.environ.get("GMAIL_API_URL", "http://localhost:8017"),
                   help="API base URL (default: $GMAIL_API_URL or http://localhost:8017)")
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
    if args.get_gmail_users_me_profile:
        return show(api_get(base, "/gmail/v1/users/me/profile"))
    if args.get_gmail_users_me_labels:
        return show(api_get(base, "/gmail/v1/users/me/labels"))
    if args.get_gmail_users_me_labels_label_id:
        return show(api_get(base, _fill('/gmail/v1/users/me/labels/{label_id}', args.get_gmail_users_me_labels_label_id)))
    if args.post_gmail_users_me_labels:
        return show(api_send(base, '/gmail/v1/users/me/labels', 'POST', _body(args)))
    if args.get_gmail_users_me_messages:
        return show(api_get(base, "/gmail/v1/users/me/messages"))
    if args.get_gmail_users_me_messages_message_id:
        return show(api_get(base, _fill('/gmail/v1/users/me/messages/{message_id}', args.get_gmail_users_me_messages_message_id)))
    if args.post_gmail_users_me_messages_send:
        return show(api_send(base, '/gmail/v1/users/me/messages/send', 'POST', _body(args)))
    if args.post_gmail_users_me_messages_modify_message_id:
        return show(api_send(base, _fill('/gmail/v1/users/me/messages/{message_id}/modify', args.post_gmail_users_me_messages_modify_message_id), 'POST', _body(args)))
    if args.post_gmail_users_me_messages_trash_message_id:
        return show(api_send(base, _fill('/gmail/v1/users/me/messages/{message_id}/trash', args.post_gmail_users_me_messages_trash_message_id), 'POST', _body(args)))
    if args.delete_gmail_users_me_messages_message_id:
        return show(api_delete(base, _fill('/gmail/v1/users/me/messages/{message_id}', args.delete_gmail_users_me_messages_message_id)))
    if args.get_gmail_users_me_threads:
        return show(api_get(base, "/gmail/v1/users/me/threads"))
    if args.get_gmail_users_me_threads_thread_id:
        return show(api_get(base, _fill('/gmail/v1/users/me/threads/{thread_id}', args.get_gmail_users_me_threads_thread_id)))
    if args.get_gmail_users_me_drafts:
        return show(api_get(base, "/gmail/v1/users/me/drafts"))
    if args.get_gmail_users_me_drafts_draft_id:
        return show(api_get(base, _fill('/gmail/v1/users/me/drafts/{draft_id}', args.get_gmail_users_me_drafts_draft_id)))
    if args.post_gmail_users_me_drafts:
        return show(api_send(base, '/gmail/v1/users/me/drafts', 'POST', _body(args)))
    if args.post_gmail_users_me_drafts_send_draft_id:
        return show(api_send(base, _fill('/gmail/v1/users/me/drafts/{draft_id}/send', args.post_gmail_users_me_drafts_send_draft_id), 'POST', _body(args)))
    print("No endpoint flag provided. Use -h to list available endpoints.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
