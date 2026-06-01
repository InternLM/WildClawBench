#!/usr/bin/env python3
"""CLI helper for reading Etsy shop data — listings, receipts, reviews, and shop info."""

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
    parser = argparse.ArgumentParser(description="Query an Etsy Open API v3 service")
    parser.add_argument("--shop", metavar="SHOP_ID",
                        help="Fetch shop profile")
    parser.add_argument("--sections", metavar="SHOP_ID",
                        help="List shop sections")
    parser.add_argument("--listings", metavar="SHOP_ID",
                        help="List active listings for a shop")
    parser.add_argument("--listing", metavar="LISTING_ID",
                        help="Fetch details for a specific listing")
    parser.add_argument("--receipts", metavar="SHOP_ID",
                        help="List receipts/orders for a shop")
    parser.add_argument("--receipt", metavar="RECEIPT_ID",
                        help="Fetch details for a specific receipt (requires --shop-id)")
    parser.add_argument("--reviews", metavar="SHOP_ID",
                        help="List reviews for a shop")
    parser.add_argument("--listing-reviews", metavar="LISTING_ID",
                        help="List reviews for a specific listing")
    parser.add_argument("--images", metavar="LISTING_ID",
                        help="List images for a listing")
    parser.add_argument("--shipping-profiles", metavar="SHOP_ID",
                        help="List shipping profiles")
    parser.add_argument("--shop-id", metavar="SHOP_ID",
                        help="Shop ID (used with --receipt)")
    parser.add_argument("--state",
                        help="Filter listings by state (active, draft, sold_out, expired)")
    parser.add_argument("--status",
                        help="Filter receipts by status (paid, shipped, completed, cancelled)")
    parser.add_argument("--q", metavar="QUERY",
                        help="Search query for listings")
    parser.add_argument("--limit", type=int,
                        help="Maximum results to return")

    args = parser.parse_args()
    base_url = os.environ.get("ETSY_API_URL", "http://localhost:8001")

    try:
        if args.shop:
            print_json(api_get(base_url, f"/v3/application/shops/{args.shop}"))
            return

        if args.sections:
            print_json(api_get(base_url, f"/v3/application/shops/{args.sections}/sections"))
            return

        if args.listings:
            params = {}
            if args.state:
                params["state"] = args.state
            if args.q:
                params["q"] = args.q
            if args.limit:
                params["limit"] = str(args.limit)
            print_json(api_get(base_url, f"/v3/application/shops/{args.listings}/listings", params or None))
            return

        if args.listing:
            print_json(api_get(base_url, f"/v3/application/listings/{args.listing}"))
            return

        if args.receipts:
            params = {}
            if args.status:
                params["status"] = args.status
            if args.limit:
                params["limit"] = str(args.limit)
            print_json(api_get(base_url, f"/v3/application/shops/{args.receipts}/receipts", params or None))
            return

        if args.receipt:
            shop_id = args.shop_id or "29457183"
            print_json(api_get(base_url, f"/v3/application/shops/{shop_id}/receipts/{args.receipt}"))
            return

        if args.reviews:
            params = {}
            if args.limit:
                params["limit"] = str(args.limit)
            print_json(api_get(base_url, f"/v3/application/shops/{args.reviews}/reviews", params or None))
            return

        if args.listing_reviews:
            print_json(api_get(base_url, f"/v3/application/listings/{args.listing_reviews}/reviews"))
            return

        if args.images:
            print_json(api_get(base_url, f"/v3/application/listings/{args.images}/images"))
            return

        if args.shipping_profiles:
            print_json(api_get(base_url, f"/v3/application/shops/{args.shipping_profiles}/shipping-profiles"))
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
