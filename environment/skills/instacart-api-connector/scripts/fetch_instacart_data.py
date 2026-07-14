#!/usr/bin/env python3
"""CLI helper for the Instacart API (Mock) mock API.

Generated read/write helper: one flag per endpoint. Base URL comes from
$INSTACART_API_URL (override with --url). POST/PUT/PATCH bodies are read from --data
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
    p = argparse.ArgumentParser(description="Query the Instacart API (Mock) mock API")
    p.add_argument("--get-users-me", action="store_true", help="GET /v1/users/me")
    p.add_argument("--get-retailers", action="store_true", help="GET /v1/retailers")
    p.add_argument("--get-retailers-retailer-id", metavar="RETAILER_ID", nargs=1, help="GET /v1/retailers/{retailer_id}")
    p.add_argument("--get-products", action="store_true", help="GET /v1/products")
    p.add_argument("--get-products-product-id", metavar="PRODUCT_ID", nargs=1, help="GET /v1/products/{product_id}")
    p.add_argument("--post-carts", action="store_true", help="POST /v1/carts")
    p.add_argument("--get-carts-cart-id", metavar="CART_ID", nargs=1, help="GET /v1/carts/{cart_id}")
    p.add_argument("--post-carts-items-cart-id", metavar="CART_ID", nargs=1, help="POST /v1/carts/{cart_id}/items")
    p.add_argument("--patch-carts-items-cart-id-product-id", metavar="CART_ID/PRODUCT_ID", nargs=2, help="PATCH /v1/carts/{cart_id}/items/{product_id}")
    p.add_argument("--post-carts-checkout-cart-id", metavar="CART_ID", nargs=1, help="POST /v1/carts/{cart_id}/checkout")
    p.add_argument("--get-orders", action="store_true", help="GET /v1/orders")
    p.add_argument("--get-orders-order-id", metavar="ORDER_ID", nargs=1, help="GET /v1/orders/{order_id}")
    p.add_argument("--post-orders-cancel-order-id", metavar="ORDER_ID", nargs=1, help="POST /v1/orders/{order_id}/cancel")
    p.add_argument("--data", metavar="JSON", help="Request body as a JSON string (POST/PUT/PATCH)")
    p.add_argument("--data-file", metavar="PATH", help="Request body from a JSON file (POST/PUT/PATCH)")
    p.add_argument("--url", default=os.environ.get("INSTACART_API_URL", "http://localhost:8012"),
                   help="API base URL (default: $INSTACART_API_URL or http://localhost:8012)")
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
    if args.get_users_me:
        return show(api_get(base, "/v1/users/me"))
    if args.get_retailers:
        return show(api_get(base, "/v1/retailers"))
    if args.get_retailers_retailer_id:
        return show(api_get(base, _fill('/v1/retailers/{retailer_id}', args.get_retailers_retailer_id)))
    if args.get_products:
        return show(api_get(base, "/v1/products"))
    if args.get_products_product_id:
        return show(api_get(base, _fill('/v1/products/{product_id}', args.get_products_product_id)))
    if args.post_carts:
        return show(api_send(base, '/v1/carts', 'POST', _body(args)))
    if args.get_carts_cart_id:
        return show(api_get(base, _fill('/v1/carts/{cart_id}', args.get_carts_cart_id)))
    if args.post_carts_items_cart_id:
        return show(api_send(base, _fill('/v1/carts/{cart_id}/items', args.post_carts_items_cart_id), 'POST', _body(args)))
    if args.patch_carts_items_cart_id_product_id:
        return show(api_send(base, _fill('/v1/carts/{cart_id}/items/{product_id}', args.patch_carts_items_cart_id_product_id), 'PATCH', _body(args)))
    if args.post_carts_checkout_cart_id:
        return show(api_send(base, _fill('/v1/carts/{cart_id}/checkout', args.post_carts_checkout_cart_id), 'POST', _body(args)))
    if args.get_orders:
        return show(api_get(base, "/v1/orders"))
    if args.get_orders_order_id:
        return show(api_get(base, _fill('/v1/orders/{order_id}', args.get_orders_order_id)))
    if args.post_orders_cancel_order_id:
        return show(api_send(base, _fill('/v1/orders/{order_id}/cancel', args.post_orders_cancel_order_id), 'POST', _body(args)))
    print("No endpoint flag provided. Use -h to list available endpoints.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
