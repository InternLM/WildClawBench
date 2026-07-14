#!/usr/bin/env python3
"""CLI helper for the Trello API (Mock) mock API.

Generated read/write helper: one flag per endpoint. Base URL comes from
$TRELLO_API_URL (override with --url). POST/PUT/PATCH bodies are read from --data
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
    p = argparse.ArgumentParser(description="Query the Trello API (Mock) mock API")
    p.add_argument("--get-1-members-me", action="store_true", help="GET /1/members/me")
    p.add_argument("--get-1-members-me-boards", action="store_true", help="GET /1/members/me/boards")
    p.add_argument("--get-1-boards-board-id", metavar="BOARD_ID", nargs=1, help="GET /1/boards/{board_id}")
    p.add_argument("--get-1-boards-lists-board-id", metavar="BOARD_ID", nargs=1, help="GET /1/boards/{board_id}/lists")
    p.add_argument("--get-1-lists-cards-list-id", metavar="LIST_ID", nargs=1, help="GET /1/lists/{list_id}/cards")
    p.add_argument("--get-1-cards-card-id", metavar="CARD_ID", nargs=1, help="GET /1/cards/{card_id}")
    p.add_argument("--post-1-cards", action="store_true", help="POST /1/cards")
    p.add_argument("--put-1-cards-card-id", metavar="CARD_ID", nargs=1, help="PUT /1/cards/{card_id}")
    p.add_argument("--delete-1-cards-card-id", metavar="CARD_ID", nargs=1, help="DELETE /1/cards/{card_id}")
    p.add_argument("--get-1-cards-checklists-card-id", metavar="CARD_ID", nargs=1, help="GET /1/cards/{card_id}/checklists")
    p.add_argument("--post-1-checklists", action="store_true", help="POST /1/checklists")
    p.add_argument("--data", metavar="JSON", help="Request body as a JSON string (POST/PUT/PATCH)")
    p.add_argument("--data-file", metavar="PATH", help="Request body from a JSON file (POST/PUT/PATCH)")
    p.add_argument("--url", default=os.environ.get("TRELLO_API_URL", "http://localhost:8030"),
                   help="API base URL (default: $TRELLO_API_URL or http://localhost:8030)")
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
    if args.get_1_members_me:
        return show(api_get(base, "/1/members/me"))
    if args.get_1_members_me_boards:
        return show(api_get(base, "/1/members/me/boards"))
    if args.get_1_boards_board_id:
        return show(api_get(base, _fill('/1/boards/{board_id}', args.get_1_boards_board_id)))
    if args.get_1_boards_lists_board_id:
        return show(api_get(base, _fill('/1/boards/{board_id}/lists', args.get_1_boards_lists_board_id)))
    if args.get_1_lists_cards_list_id:
        return show(api_get(base, _fill('/1/lists/{list_id}/cards', args.get_1_lists_cards_list_id)))
    if args.get_1_cards_card_id:
        return show(api_get(base, _fill('/1/cards/{card_id}', args.get_1_cards_card_id)))
    if args.post_1_cards:
        return show(api_send(base, '/1/cards', 'POST', _body(args)))
    if args.put_1_cards_card_id:
        return show(api_send(base, _fill('/1/cards/{card_id}', args.put_1_cards_card_id), 'PUT', _body(args)))
    if args.delete_1_cards_card_id:
        return show(api_delete(base, _fill('/1/cards/{card_id}', args.delete_1_cards_card_id)))
    if args.get_1_cards_checklists_card_id:
        return show(api_get(base, _fill('/1/cards/{card_id}/checklists', args.get_1_cards_checklists_card_id)))
    if args.post_1_checklists:
        return show(api_send(base, '/1/checklists', 'POST', _body(args)))
    print("No endpoint flag provided. Use -h to list available endpoints.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
