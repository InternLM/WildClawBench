#!/usr/bin/env python3
"""CLI helper for reading Amazon Seller data — catalog, orders, inventory, pricing, and account info."""

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
    parser = argparse.ArgumentParser(description="Query an Amazon Selling Partner API service")
    parser.add_argument("--account",
                        action="store_true",
                        help="Fetch seller account profile")
    parser.add_argument("--health",
                        action="store_true",
                        help="Fetch account health metrics")
    parser.add_argument("--notifications",
                        action="store_true",
                        help="List performance notifications")
    parser.add_argument("--catalog",
                        action="store_true",
                        help="List catalog items")
    parser.add_argument("--catalog-item", metavar="ASIN",
                        help="Fetch details for a specific ASIN")
    parser.add_argument("--listing", metavar="SKU",
                        help="Fetch listing details for a SKU (requires --seller-id)")
    parser.add_argument("--orders",
                        action="store_true",
                        help="List orders")
    parser.add_argument("--order", metavar="ORDER_ID",
                        help="Fetch details for a specific order")
    parser.add_argument("--order-items", metavar="ORDER_ID",
                        help="Fetch line items for a specific order")
    parser.add_argument("--inventory",
                        action="store_true",
                        help="List inventory summaries")
    parser.add_argument("--pricing", metavar="ASIN",
                        help="Get competitive pricing for an ASIN")
    parser.add_argument("--offers", metavar="ASIN",
                        help="Get item offers for an ASIN")
    parser.add_argument("--reports",
                        action="store_true",
                        help="List reports")
    parser.add_argument("--report", metavar="REPORT_ID",
                        help="Fetch details for a specific report")
    parser.add_argument("--returns",
                        action="store_true",
                        help="List returns")
    parser.add_argument("--return-item", metavar="RETURN_ID",
                        help="Fetch details for a specific return")
    parser.add_argument("--seller-id", metavar="SELLER_ID",
                        help="Seller ID (used with --listing, default A3EXAMPLE1SELLER)")
    parser.add_argument("--keywords", metavar="QUERY",
                        help="Search keywords for catalog")
    parser.add_argument("--status",
                        help="Filter by status (orders: Pending/Unshipped/Shipped/Canceled; returns: Authorized/Completed)")
    parser.add_argument("--fulfillment",
                        help="Filter orders by fulfillment channel: AFN or MFN")
    parser.add_argument("--skus", metavar="SKUS",
                        help="Comma-separated SKUs for inventory filter")
    parser.add_argument("--severity",
                        help="Filter notifications by severity: WARNING, CRITICAL, INFO")
    parser.add_argument("--limit", type=int,
                        help="Maximum results to return")

    args = parser.parse_args()
    base_url = os.environ.get("AMAZON_SELLER_API_URL", "http://localhost:8000")

    try:
        if args.account:
            print_json(api_get(base_url, "/sellers/v1/account"))
            return

        if args.health:
            print_json(api_get(base_url, "/sellers/v1/account/health"))
            return

        if args.notifications:
            params = {}
            if args.severity:
                params["severity"] = args.severity
            print_json(api_get(base_url, "/notifications/v1/notifications", params or None))
            return

        if args.catalog:
            params = {"pageSize": "20"}
            if args.keywords:
                params["keywords"] = args.keywords
            if args.limit:
                params["pageSize"] = str(min(args.limit, 20))
            print_json(api_get(base_url, "/catalog/2022-04-01/items", params))
            return

        if args.catalog_item:
            print_json(api_get(base_url, f"/catalog/2022-04-01/items/{args.catalog_item}"))
            return

        if args.listing:
            seller_id = args.seller_id or "A3EXAMPLE1SELLER"
            print_json(api_get(base_url, f"/listings/2021-08-01/items/{seller_id}/{args.listing}"))
            return

        if args.orders:
            params = {}
            if args.status:
                params["OrderStatuses"] = args.status
            if args.fulfillment:
                params["FulfillmentChannels"] = args.fulfillment
            if args.limit:
                params["MaxResultsPerPage"] = str(args.limit)
            print_json(api_get(base_url, "/orders/v0/orders", params or None))
            return

        if args.order:
            print_json(api_get(base_url, f"/orders/v0/orders/{args.order}"))
            return

        if args.order_items:
            print_json(api_get(base_url, f"/orders/v0/orders/{args.order_items}/orderItems"))
            return

        if args.inventory:
            params = {}
            if args.skus:
                params["sellerSkus"] = args.skus
            print_json(api_get(base_url, "/fba/inventory/v1/summaries", params or None))
            return

        if args.pricing:
            print_json(api_get(base_url, f"/products/pricing/v0/competitivePrice", {"Asin": args.pricing}))
            return

        if args.offers:
            print_json(api_get(base_url, f"/products/pricing/v0/items/{args.offers}/offers"))
            return

        if args.reports:
            params = {}
            if args.status:
                params["processingStatuses"] = args.status
            print_json(api_get(base_url, "/reports/2021-06-30/reports", params or None))
            return

        if args.report:
            print_json(api_get(base_url, f"/reports/2021-06-30/reports/{args.report}"))
            return

        if args.returns:
            params = {}
            if args.status:
                params["status"] = args.status
            print_json(api_get(base_url, "/returns/v0/returns", params or None))
            return

        if args.return_item:
            print_json(api_get(base_url, f"/returns/v0/returns/{args.return_item}"))
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
