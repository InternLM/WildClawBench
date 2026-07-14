#!/usr/bin/env python3
"""CLI helper for the PayPal API (Mock) mock API.

Generated read/write helper: one flag per endpoint. Base URL comes from
$PAYPAL_API_URL (override with --url). POST/PUT/PATCH bodies are read from --data
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
    p = argparse.ArgumentParser(description="Query the PayPal API (Mock) mock API")
    p.add_argument("--post-checkout-orders", action="store_true", help="POST /v2/checkout/orders")
    p.add_argument("--get-checkout-orders-order-id", metavar="ORDER_ID", nargs=1, help="GET /v2/checkout/orders/{order_id}")
    p.add_argument("--post-checkout-orders-capture-order-id", metavar="ORDER_ID", nargs=1, help="POST /v2/checkout/orders/{order_id}/capture")
    p.add_argument("--post-payments-refunds", action="store_true", help="POST /v2/payments/refunds")
    p.add_argument("--get-payments-refunds-refund-id", metavar="REFUND_ID", nargs=1, help="GET /v2/payments/refunds/{refund_id}")
    p.add_argument("--get-invoicing-invoices", action="store_true", help="GET /v2/invoicing/invoices")
    p.add_argument("--post-invoicing-invoices", action="store_true", help="POST /v2/invoicing/invoices")
    p.add_argument("--post-payments-payouts", action="store_true", help="POST /v1/payments/payouts")
    p.add_argument("--data", metavar="JSON", help="Request body as a JSON string (POST/PUT/PATCH)")
    p.add_argument("--data-file", metavar="PATH", help="Request body from a JSON file (POST/PUT/PATCH)")
    p.add_argument("--url", default=os.environ.get("PAYPAL_API_URL", "http://localhost:8042"),
                   help="API base URL (default: $PAYPAL_API_URL or http://localhost:8042)")
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
    if args.post_checkout_orders:
        return show(api_send(base, '/v2/checkout/orders', 'POST', _body(args)))
    if args.get_checkout_orders_order_id:
        return show(api_get(base, _fill('/v2/checkout/orders/{order_id}', args.get_checkout_orders_order_id)))
    if args.post_checkout_orders_capture_order_id:
        return show(api_send(base, _fill('/v2/checkout/orders/{order_id}/capture', args.post_checkout_orders_capture_order_id), 'POST', _body(args)))
    if args.post_payments_refunds:
        return show(api_send(base, '/v2/payments/refunds', 'POST', _body(args)))
    if args.get_payments_refunds_refund_id:
        return show(api_get(base, _fill('/v2/payments/refunds/{refund_id}', args.get_payments_refunds_refund_id)))
    if args.get_invoicing_invoices:
        return show(api_get(base, "/v2/invoicing/invoices"))
    if args.post_invoicing_invoices:
        return show(api_send(base, '/v2/invoicing/invoices', 'POST', _body(args)))
    if args.post_payments_payouts:
        return show(api_send(base, '/v1/payments/payouts', 'POST', _body(args)))
    print("No endpoint flag provided. Use -h to list available endpoints.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
