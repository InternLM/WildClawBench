#!/usr/bin/env python3
"""CLI helper for reading QuickBooks Online data — invoices, customers, vendors, bills, and reports."""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error
import urllib.parse


def api_get(base_url, realm_id, path, params=None):
    url = f"{base_url}/v3/company/{realm_id}/{path}"
    if params:
        filtered = {k: v for k, v in params.items() if v is not None}
        if filtered:
            url += "?" + urllib.parse.urlencode(filtered)
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())


def api_post(base_url, realm_id, path, body):
    url = f"{base_url}/v3/company/{realm_id}/{path}"
    data = json.dumps(body).encode()
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())


def print_json(data):
    print(json.dumps(data, indent=2))


def main():
    parser = argparse.ArgumentParser(description="Query a QuickBooks Online API v3 service")
    parser.add_argument("--customers", action="store_true", help="List all customers")
    parser.add_argument("--customer", metavar="ID", help="Get customer by ID")
    parser.add_argument("--vendors", action="store_true", help="List all vendors")
    parser.add_argument("--vendor", metavar="ID", help="Get vendor by ID")
    parser.add_argument("--items", action="store_true", help="List all items")
    parser.add_argument("--item", metavar="ID", help="Get item by ID")
    parser.add_argument("--invoices", action="store_true", help="List all invoices")
    parser.add_argument("--invoice", metavar="ID", help="Get invoice by ID")
    parser.add_argument("--unpaid", action="store_true", help="List unpaid invoices (Balance > 0)")
    parser.add_argument("--bills", action="store_true", help="List all bills")
    parser.add_argument("--bill", metavar="ID", help="Get bill by ID")
    parser.add_argument("--payments", action="store_true", help="List all payments")
    parser.add_argument("--payment", metavar="ID", help="Get payment by ID")
    parser.add_argument("--estimates", action="store_true", help="List all estimates")
    parser.add_argument("--estimate", metavar="ID", help="Get estimate by ID")
    parser.add_argument("--expenses", action="store_true", help="List all expenses/purchases")
    parser.add_argument("--expense", metavar="ID", help="Get expense by ID")
    parser.add_argument("--accounts", action="store_true", help="List chart of accounts")
    parser.add_argument("--company", action="store_true", help="Get company info")
    parser.add_argument("--pnl", action="store_true", help="Profit & Loss report")
    parser.add_argument("--balance-sheet", action="store_true", help="Balance Sheet report")
    parser.add_argument("--ar-aging", action="store_true", help="AR Aging report")
    parser.add_argument("--ap-aging", action="store_true", help="AP Aging report")
    parser.add_argument("--query", metavar="SQL", help="Execute raw query (e.g. \"SELECT * FROM Invoice WHERE Balance > '0'\")")
    parser.add_argument("--start-date", metavar="DATE", help="Report start date (YYYY-MM-DD)")
    parser.add_argument("--end-date", metavar="DATE", help="Report end date (YYYY-MM-DD)")
    parser.add_argument("--url", default=os.environ.get("QUICKBOOKS_API_URL", "http://localhost:8007"),
                        help="API base URL (default: $QUICKBOOKS_API_URL or http://localhost:8007)")
    parser.add_argument("--realm-id", default=os.environ.get("REALM_ID", "4620816365272861350"),
                        help="Company realm ID (default: $REALM_ID)")

    args = parser.parse_args()
    base_url = args.url.rstrip("/")
    realm_id = args.realm_id

    try:
        if args.company:
            print_json(api_get(base_url, realm_id, "companyinfo/1"))
        elif args.customers:
            print_json(api_get(base_url, realm_id, "query", {"query": "SELECT * FROM Customer"}))
        elif args.customer:
            print_json(api_get(base_url, realm_id, f"customer/{args.customer}"))
        elif args.vendors:
            print_json(api_get(base_url, realm_id, "query", {"query": "SELECT * FROM Vendor"}))
        elif args.vendor:
            print_json(api_get(base_url, realm_id, f"vendor/{args.vendor}"))
        elif args.items:
            print_json(api_get(base_url, realm_id, "query", {"query": "SELECT * FROM Item"}))
        elif args.item:
            print_json(api_get(base_url, realm_id, f"item/{args.item}"))
        elif args.invoices:
            print_json(api_get(base_url, realm_id, "query", {"query": "SELECT * FROM Invoice"}))
        elif args.invoice:
            print_json(api_get(base_url, realm_id, f"invoice/{args.invoice}"))
        elif args.unpaid:
            print_json(api_get(base_url, realm_id, "query", {"query": "SELECT * FROM Invoice WHERE Balance > '0'"}))
        elif args.bills:
            print_json(api_get(base_url, realm_id, "query", {"query": "SELECT * FROM Bill"}))
        elif args.bill:
            print_json(api_get(base_url, realm_id, f"bill/{args.bill}"))
        elif args.payments:
            print_json(api_get(base_url, realm_id, "query", {"query": "SELECT * FROM Payment"}))
        elif args.payment:
            print_json(api_get(base_url, realm_id, f"payment/{args.payment}"))
        elif args.estimates:
            print_json(api_get(base_url, realm_id, "query", {"query": "SELECT * FROM Estimate"}))
        elif args.estimate:
            print_json(api_get(base_url, realm_id, f"estimate/{args.estimate}"))
        elif args.expenses:
            print_json(api_get(base_url, realm_id, "query", {"query": "SELECT * FROM Purchase"}))
        elif args.expense:
            print_json(api_get(base_url, realm_id, f"purchase/{args.expense}"))
        elif args.accounts:
            print_json(api_get(base_url, realm_id, "query", {"query": "SELECT * FROM Account"}))
        elif args.pnl:
            params = {}
            if args.start_date:
                params["start_date"] = args.start_date
            if args.end_date:
                params["end_date"] = args.end_date
            print_json(api_get(base_url, realm_id, "reports/ProfitAndLoss", params))
        elif args.balance_sheet:
            params = {}
            if args.start_date:
                params["start_date"] = args.start_date
            if args.end_date:
                params["end_date"] = args.end_date
            print_json(api_get(base_url, realm_id, "reports/BalanceSheet", params))
        elif args.ar_aging:
            print_json(api_get(base_url, realm_id, "reports/AgedReceivableDetail"))
        elif args.ap_aging:
            print_json(api_get(base_url, realm_id, "reports/AgedPayableDetail"))
        elif args.query:
            print_json(api_get(base_url, realm_id, "query", {"query": args.query}))
        else:
            parser.print_help()
            sys.exit(0)
    except urllib.error.HTTPError as e:
        print(f"HTTP {e.code}: {e.read().decode()}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"Connection error: {e.reason}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
