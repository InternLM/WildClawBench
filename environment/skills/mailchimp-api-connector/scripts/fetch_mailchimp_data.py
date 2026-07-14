#!/usr/bin/env python3
"""CLI helper for the Mailchimp Marketing API (Mock) mock API.

Generated read/write helper: one flag per endpoint. Base URL comes from
$MAILCHIMP_API_URL (override with --url). POST/PUT/PATCH bodies are read from --data
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
    p = argparse.ArgumentParser(description="Query the Mailchimp Marketing API (Mock) mock API")
    p.add_argument("--get-3-0-lists", action="store_true", help="GET /3.0/lists")
    p.add_argument("--get-3-0-lists-list-id", metavar="LIST_ID", nargs=1, help="GET /3.0/lists/{list_id}")
    p.add_argument("--get-3-0-lists-members-list-id", metavar="LIST_ID", nargs=1, help="GET /3.0/lists/{list_id}/members")
    p.add_argument("--post-3-0-lists-members-list-id", metavar="LIST_ID", nargs=1, help="POST /3.0/lists/{list_id}/members")
    p.add_argument("--get-3-0-lists-members-list-id-subscriber-hash", metavar="LIST_ID/SUBSCRIBER_HASH", nargs=2, help="GET /3.0/lists/{list_id}/members/{subscriber_hash}")
    p.add_argument("--patch-3-0-lists-members-list-id-subscriber-hash", metavar="LIST_ID/SUBSCRIBER_HASH", nargs=2, help="PATCH /3.0/lists/{list_id}/members/{subscriber_hash}")
    p.add_argument("--get-3-0-campaigns", action="store_true", help="GET /3.0/campaigns")
    p.add_argument("--post-3-0-campaigns", action="store_true", help="POST /3.0/campaigns")
    p.add_argument("--get-3-0-campaigns-campaign-id", metavar="CAMPAIGN_ID", nargs=1, help="GET /3.0/campaigns/{campaign_id}")
    p.add_argument("--post-3-0-campaigns-actions-send-campaign-id", metavar="CAMPAIGN_ID", nargs=1, help="POST /3.0/campaigns/{campaign_id}/actions/send")
    p.add_argument("--get-3-0-reports-campaign-id", metavar="CAMPAIGN_ID", nargs=1, help="GET /3.0/reports/{campaign_id}")
    p.add_argument("--data", metavar="JSON", help="Request body as a JSON string (POST/PUT/PATCH)")
    p.add_argument("--data-file", metavar="PATH", help="Request body from a JSON file (POST/PUT/PATCH)")
    p.add_argument("--url", default=os.environ.get("MAILCHIMP_API_URL", "http://localhost:8081"),
                   help="API base URL (default: $MAILCHIMP_API_URL or http://localhost:8081)")
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
    if args.get_3_0_lists:
        return show(api_get(base, "/3.0/lists"))
    if args.get_3_0_lists_list_id:
        return show(api_get(base, _fill('/3.0/lists/{list_id}', args.get_3_0_lists_list_id)))
    if args.get_3_0_lists_members_list_id:
        return show(api_get(base, _fill('/3.0/lists/{list_id}/members', args.get_3_0_lists_members_list_id)))
    if args.post_3_0_lists_members_list_id:
        return show(api_send(base, _fill('/3.0/lists/{list_id}/members', args.post_3_0_lists_members_list_id), 'POST', _body(args)))
    if args.get_3_0_lists_members_list_id_subscriber_hash:
        return show(api_get(base, _fill('/3.0/lists/{list_id}/members/{subscriber_hash}', args.get_3_0_lists_members_list_id_subscriber_hash)))
    if args.patch_3_0_lists_members_list_id_subscriber_hash:
        return show(api_send(base, _fill('/3.0/lists/{list_id}/members/{subscriber_hash}', args.patch_3_0_lists_members_list_id_subscriber_hash), 'PATCH', _body(args)))
    if args.get_3_0_campaigns:
        return show(api_get(base, "/3.0/campaigns"))
    if args.post_3_0_campaigns:
        return show(api_send(base, '/3.0/campaigns', 'POST', _body(args)))
    if args.get_3_0_campaigns_campaign_id:
        return show(api_get(base, _fill('/3.0/campaigns/{campaign_id}', args.get_3_0_campaigns_campaign_id)))
    if args.post_3_0_campaigns_actions_send_campaign_id:
        return show(api_send(base, _fill('/3.0/campaigns/{campaign_id}/actions/send', args.post_3_0_campaigns_actions_send_campaign_id), 'POST', _body(args)))
    if args.get_3_0_reports_campaign_id:
        return show(api_get(base, _fill('/3.0/reports/{campaign_id}', args.get_3_0_reports_campaign_id)))
    print("No endpoint flag provided. Use -h to list available endpoints.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
