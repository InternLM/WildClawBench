#!/usr/bin/env python3
"""CLI helper for the Square API (Mock) mock API.

Generated read/write helper: one flag per endpoint. Base URL comes from
$SQUARE_API_URL (override with --url). POST/PUT/PATCH bodies are read from --data
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
    p = argparse.ArgumentParser(description="Query the Square API (Mock) mock API")
    p.add_argument("--get-merchants-me", action="store_true", help="GET /v2/merchants/me")
    p.add_argument("--get-payments", action="store_true", help="GET /v2/payments")
    p.add_argument("--get-payments-payment-id", metavar="PAYMENT_ID", nargs=1, help="GET /v2/payments/{payment_id}")
    p.add_argument("--post-payments", action="store_true", help="POST /v2/payments")
    p.add_argument("--post-refunds", action="store_true", help="POST /v2/refunds")
    p.add_argument("--get-customers", action="store_true", help="GET /v2/customers")
    p.add_argument("--get-customers-customer-id", metavar="CUSTOMER_ID", nargs=1, help="GET /v2/customers/{customer_id}")
    p.add_argument("--post-customers", action="store_true", help="POST /v2/customers")
    p.add_argument("--get-catalog-list", action="store_true", help="GET /v2/catalog/list")
    p.add_argument("--post-orders", action="store_true", help="POST /v2/orders")
    p.add_argument("--get-orders-order-id", metavar="ORDER_ID", nargs=1, help="GET /v2/orders/{order_id}")
    p.add_argument("--get-inventory-catalog-object-id", metavar="CATALOG_OBJECT_ID", nargs=1, help="GET /v2/inventory/{catalog_object_id}")
    p.add_argument("--data", metavar="JSON", help="Request body as a JSON string (POST/PUT/PATCH)")
    p.add_argument("--data-file", metavar="PATH", help="Request body from a JSON file (POST/PUT/PATCH)")
    p.add_argument("--url", default=os.environ.get("SQUARE_API_URL", "http://localhost:8041"),
                   help="API base URL (default: $SQUARE_API_URL or http://localhost:8041)")
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
    if args.get_merchants_me:
        return show(api_get(base, "/v2/merchants/me"))
    if args.get_payments:
        return show(api_get(base, "/v2/payments"))
    if args.get_payments_payment_id:
        return show(api_get(base, _fill('/v2/payments/{payment_id}', args.get_payments_payment_id)))
    if args.post_payments:
        return show(api_send(base, '/v2/payments', 'POST', _body(args)))
    if args.post_refunds:
        return show(api_send(base, '/v2/refunds', 'POST', _body(args)))
    if args.get_customers:
        return show(api_get(base, "/v2/customers"))
    if args.get_customers_customer_id:
        return show(api_get(base, _fill('/v2/customers/{customer_id}', args.get_customers_customer_id)))
    if args.post_customers:
        return show(api_send(base, '/v2/customers', 'POST', _body(args)))
    if args.get_catalog_list:
        return show(api_get(base, "/v2/catalog/list"))
    if args.post_orders:
        return show(api_send(base, '/v2/orders', 'POST', _body(args)))
    if args.get_orders_order_id:
        return show(api_get(base, _fill('/v2/orders/{order_id}', args.get_orders_order_id)))
    if args.get_inventory_catalog_object_id:
        return show(api_get(base, _fill('/v2/inventory/{catalog_object_id}', args.get_inventory_catalog_object_id)))
    print("No endpoint flag provided. Use -h to list available endpoints.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
