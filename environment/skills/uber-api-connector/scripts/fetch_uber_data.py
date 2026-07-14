#!/usr/bin/env python3
"""CLI helper for the Uber API (Mock) mock API.

Generated read/write helper: one flag per endpoint. Base URL comes from
$UBER_API_URL (override with --url). POST/PUT/PATCH bodies are read from --data
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
    p = argparse.ArgumentParser(description="Query the Uber API (Mock) mock API")
    p.add_argument("--get-v1-2-products", action="store_true", help="GET /v1.2/products")
    p.add_argument("--get-v1-2-products-product-id", metavar="PRODUCT_ID", nargs=1, help="GET /v1.2/products/{product_id}")
    p.add_argument("--get-v1-2-estimates-price", action="store_true", help="GET /v1.2/estimates/price")
    p.add_argument("--get-v1-2-estimates-time", action="store_true", help="GET /v1.2/estimates/time")
    p.add_argument("--post-v1-2-requests", action="store_true", help="POST /v1.2/requests")
    p.add_argument("--get-v1-2-requests-request-id", metavar="REQUEST_ID", nargs=1, help="GET /v1.2/requests/{request_id}")
    p.add_argument("--delete-v1-2-requests-request-id", metavar="REQUEST_ID", nargs=1, help="DELETE /v1.2/requests/{request_id}")
    p.add_argument("--get-v1-2-history", action="store_true", help="GET /v1.2/history")
    p.add_argument("--get-v1-2-me", action="store_true", help="GET /v1.2/me")
    p.add_argument("--data", metavar="JSON", help="Request body as a JSON string (POST/PUT/PATCH)")
    p.add_argument("--data-file", metavar="PATH", help="Request body from a JSON file (POST/PUT/PATCH)")
    p.add_argument("--url", default=os.environ.get("UBER_API_URL", "http://localhost:8036"),
                   help="API base URL (default: $UBER_API_URL or http://localhost:8036)")
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
    if args.get_v1_2_products:
        return show(api_get(base, "/v1.2/products"))
    if args.get_v1_2_products_product_id:
        return show(api_get(base, _fill('/v1.2/products/{product_id}', args.get_v1_2_products_product_id)))
    if args.get_v1_2_estimates_price:
        return show(api_get(base, "/v1.2/estimates/price"))
    if args.get_v1_2_estimates_time:
        return show(api_get(base, "/v1.2/estimates/time"))
    if args.post_v1_2_requests:
        return show(api_send(base, '/v1.2/requests', 'POST', _body(args)))
    if args.get_v1_2_requests_request_id:
        return show(api_get(base, _fill('/v1.2/requests/{request_id}', args.get_v1_2_requests_request_id)))
    if args.delete_v1_2_requests_request_id:
        return show(api_delete(base, _fill('/v1.2/requests/{request_id}', args.delete_v1_2_requests_request_id)))
    if args.get_v1_2_history:
        return show(api_get(base, "/v1.2/history"))
    if args.get_v1_2_me:
        return show(api_get(base, "/v1.2/me"))
    print("No endpoint flag provided. Use -h to list available endpoints.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
