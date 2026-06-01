#!/usr/bin/env python3
"""CLI helper for reading Pinterest business account data — pins, boards, analytics, and ads."""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error
import urllib.parse


def api_get(base_url, path, params=None):
    url = f"{base_url}{path}"
    if params:
        filtered = {k: v for k, v in params.items() if v is not None}
        if filtered:
            url += "?" + urllib.parse.urlencode(filtered)
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())


def print_json(data):
    print(json.dumps(data, indent=2))


def main():
    parser = argparse.ArgumentParser(description="Query a Pinterest API v5 service")
    parser.add_argument("--account",
                        action="store_true",
                        help="Fetch user account profile")
    parser.add_argument("--account-analytics",
                        action="store_true",
                        help="Fetch user account analytics")
    parser.add_argument("--boards",
                        action="store_true",
                        help="List all boards")
    parser.add_argument("--board", metavar="BOARD_ID",
                        help="Fetch details for a specific board")
    parser.add_argument("--board-pins", metavar="BOARD_ID",
                        help="List pins on a specific board")
    parser.add_argument("--board-sections", metavar="BOARD_ID",
                        help="List sections for a board")
    parser.add_argument("--section-pins", metavar="SECTION_ID",
                        help="List pins in a section (requires --board-id)")
    parser.add_argument("--pins",
                        action="store_true",
                        help="List all pins")
    parser.add_argument("--pin", metavar="PIN_ID",
                        help="Fetch details for a specific pin")
    parser.add_argument("--pin-analytics", metavar="PIN_ID",
                        help="Fetch analytics for a specific pin")
    parser.add_argument("--search", metavar="QUERY",
                        help="Search pins by keyword")
    parser.add_argument("--media", metavar="MEDIA_ID",
                        help="Get media upload status")
    parser.add_argument("--ad-accounts",
                        action="store_true",
                        help="List ad accounts")
    parser.add_argument("--ad-account", metavar="AD_ACCOUNT_ID",
                        help="Fetch details for an ad account")
    parser.add_argument("--campaigns", metavar="AD_ACCOUNT_ID",
                        help="List campaigns for an ad account")
    parser.add_argument("--board-id", metavar="BOARD_ID",
                        help="Board ID (used with --section-pins)")
    parser.add_argument("--privacy",
                        help="Filter boards by privacy (PUBLIC, SECRET)")
    parser.add_argument("--status",
                        help="Filter campaigns by status (ACTIVE, PAUSED)")
    parser.add_argument("--start-date", metavar="DATE",
                        help="Start date for analytics (YYYY-MM-DD)")
    parser.add_argument("--end-date", metavar="DATE",
                        help="End date for analytics (YYYY-MM-DD)")
    parser.add_argument("--limit", type=int,
                        help="Maximum results to return")

    args = parser.parse_args()
    base_url = os.environ.get("PINTEREST_API_URL", "http://localhost:8006")

    try:
        if args.account:
            print_json(api_get(base_url, "/v5/user_account"))
            return

        if args.account_analytics:
            params = {}
            if args.start_date:
                params["start_date"] = args.start_date
            if args.end_date:
                params["end_date"] = args.end_date
            print_json(api_get(base_url, "/v5/user_account/analytics", params or None))
            return

        if args.boards:
            params = {}
            if args.privacy:
                params["privacy"] = args.privacy
            if args.limit:
                params["limit"] = str(args.limit)
            print_json(api_get(base_url, "/v5/boards", params or None))
            return

        if args.board:
            print_json(api_get(base_url, f"/v5/boards/{args.board}"))
            return

        if args.board_pins:
            params = {}
            if args.limit:
                params["limit"] = str(args.limit)
            print_json(api_get(base_url, f"/v5/boards/{args.board_pins}/pins", params or None))
            return

        if args.board_sections:
            print_json(api_get(base_url, f"/v5/boards/{args.board_sections}/sections"))
            return

        if args.section_pins:
            board_id = args.board_id or "board_1002"
            params = {}
            if args.limit:
                params["limit"] = str(args.limit)
            print_json(api_get(base_url, f"/v5/boards/{board_id}/sections/{args.section_pins}/pins", params or None))
            return

        if args.pins:
            params = {}
            if args.limit:
                params["limit"] = str(args.limit)
            print_json(api_get(base_url, "/v5/pins", params or None))
            return

        if args.pin:
            print_json(api_get(base_url, f"/v5/pins/{args.pin}"))
            return

        if args.pin_analytics:
            params = {}
            if args.start_date:
                params["start_date"] = args.start_date
            if args.end_date:
                params["end_date"] = args.end_date
            print_json(api_get(base_url, f"/v5/pins/{args.pin_analytics}/analytics", params or None))
            return

        if args.search:
            params = {"query": args.search}
            if args.limit:
                params["limit"] = str(args.limit)
            print_json(api_get(base_url, "/v5/search/pins", params))
            return

        if args.media:
            print_json(api_get(base_url, f"/v5/media/{args.media}"))
            return

        if args.ad_accounts:
            print_json(api_get(base_url, "/v5/ad_accounts"))
            return

        if args.ad_account:
            print_json(api_get(base_url, f"/v5/ad_accounts/{args.ad_account}"))
            return

        if args.campaigns:
            params = {}
            if args.status:
                params["status"] = args.status
            if args.limit:
                params["limit"] = str(args.limit)
            print_json(api_get(base_url, f"/v5/ad_accounts/{args.campaigns}/campaigns", params or None))
            return

        parser.print_help()

    except urllib.error.HTTPError as exc:
        print(f"HTTP {exc.code}: {exc.reason}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as exc:
        print(f"Connection error: {exc.reason}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
