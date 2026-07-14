#!/usr/bin/env python3
"""CLI helper for the Intercom API (Mock) mock API.

Generated read/write helper: one flag per endpoint. Base URL comes from
$INTERCOM_API_URL (override with --url). POST/PUT/PATCH bodies are read from --data
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
    p = argparse.ArgumentParser(description="Query the Intercom API (Mock) mock API")
    p.add_argument("--get-contacts", action="store_true", help="GET /contacts")
    p.add_argument("--post-contacts", action="store_true", help="POST /contacts")
    p.add_argument("--get-contacts-contact-id", metavar="CONTACT_ID", nargs=1, help="GET /contacts/{contact_id}")
    p.add_argument("--get-conversations", action="store_true", help="GET /conversations")
    p.add_argument("--post-conversations", action="store_true", help="POST /conversations")
    p.add_argument("--get-conversations-conversation-id", metavar="CONVERSATION_ID", nargs=1, help="GET /conversations/{conversation_id}")
    p.add_argument("--post-conversations-reply-conversation-id", metavar="CONVERSATION_ID", nargs=1, help="POST /conversations/{conversation_id}/reply")
    p.add_argument("--post-conversations-parts-conversation-id", metavar="CONVERSATION_ID", nargs=1, help="POST /conversations/{conversation_id}/parts")
    p.add_argument("--get-companies", action="store_true", help="GET /companies")
    p.add_argument("--get-companies-company-id", metavar="COMPANY_ID", nargs=1, help="GET /companies/{company_id}")
    p.add_argument("--data", metavar="JSON", help="Request body as a JSON string (POST/PUT/PATCH)")
    p.add_argument("--data-file", metavar="PATH", help="Request body from a JSON file (POST/PUT/PATCH)")
    p.add_argument("--url", default=os.environ.get("INTERCOM_API_URL", "http://localhost:8070"),
                   help="API base URL (default: $INTERCOM_API_URL or http://localhost:8070)")
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
    if args.get_contacts:
        return show(api_get(base, "/contacts"))
    if args.post_contacts:
        return show(api_send(base, '/contacts', 'POST', _body(args)))
    if args.get_contacts_contact_id:
        return show(api_get(base, _fill('/contacts/{contact_id}', args.get_contacts_contact_id)))
    if args.get_conversations:
        return show(api_get(base, "/conversations"))
    if args.post_conversations:
        return show(api_send(base, '/conversations', 'POST', _body(args)))
    if args.get_conversations_conversation_id:
        return show(api_get(base, _fill('/conversations/{conversation_id}', args.get_conversations_conversation_id)))
    if args.post_conversations_reply_conversation_id:
        return show(api_send(base, _fill('/conversations/{conversation_id}/reply', args.post_conversations_reply_conversation_id), 'POST', _body(args)))
    if args.post_conversations_parts_conversation_id:
        return show(api_send(base, _fill('/conversations/{conversation_id}/parts', args.post_conversations_parts_conversation_id), 'POST', _body(args)))
    if args.get_companies:
        return show(api_get(base, "/companies"))
    if args.get_companies_company_id:
        return show(api_get(base, _fill('/companies/{company_id}', args.get_companies_company_id)))
    print("No endpoint flag provided. Use -h to list available endpoints.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
