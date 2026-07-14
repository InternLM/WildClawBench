#!/usr/bin/env python3
"""CLI helper for the Zillow API (Mock) mock API.

Generated read/write helper: one flag per endpoint. Base URL comes from
$ZILLOW_API_URL (override with --url). POST/PUT/PATCH bodies are read from --data
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
    p = argparse.ArgumentParser(description="Query the Zillow API (Mock) mock API")
    p.add_argument("--get-properties-search", action="store_true", help="GET /v1/properties/search")
    p.add_argument("--get-properties-zpid", metavar="ZPID", nargs=1, help="GET /v1/properties/{zpid}")
    p.add_argument("--get-properties-zestimate-zpid", metavar="ZPID", nargs=1, help="GET /v1/properties/{zpid}/zestimate")
    p.add_argument("--get-properties-price-history-zpid", metavar="ZPID", nargs=1, help="GET /v1/properties/{zpid}/price-history")
    p.add_argument("--get-agents", action="store_true", help="GET /v1/agents")
    p.add_argument("--get-agents-agent-id", metavar="AGENT_ID", nargs=1, help="GET /v1/agents/{agent_id}")
    p.add_argument("--get-users-saved-searches-user-id", metavar="USER_ID", nargs=1, help="GET /v1/users/{user_id}/saved-searches")
    p.add_argument("--post-users-saved-searches-user-id", metavar="USER_ID", nargs=1, help="POST /v1/users/{user_id}/saved-searches")
    p.add_argument("--delete-saved-searches-search-id", metavar="SEARCH_ID", nargs=1, help="DELETE /v1/saved-searches/{search_id}")
    p.add_argument("--data", metavar="JSON", help="Request body as a JSON string (POST/PUT/PATCH)")
    p.add_argument("--data-file", metavar="PATH", help="Request body from a JSON file (POST/PUT/PATCH)")
    p.add_argument("--url", default=os.environ.get("ZILLOW_API_URL", "http://localhost:8011"),
                   help="API base URL (default: $ZILLOW_API_URL or http://localhost:8011)")
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
    if args.get_properties_search:
        return show(api_get(base, "/v1/properties/search"))
    if args.get_properties_zpid:
        return show(api_get(base, _fill('/v1/properties/{zpid}', args.get_properties_zpid)))
    if args.get_properties_zestimate_zpid:
        return show(api_get(base, _fill('/v1/properties/{zpid}/zestimate', args.get_properties_zestimate_zpid)))
    if args.get_properties_price_history_zpid:
        return show(api_get(base, _fill('/v1/properties/{zpid}/price-history', args.get_properties_price_history_zpid)))
    if args.get_agents:
        return show(api_get(base, "/v1/agents"))
    if args.get_agents_agent_id:
        return show(api_get(base, _fill('/v1/agents/{agent_id}', args.get_agents_agent_id)))
    if args.get_users_saved_searches_user_id:
        return show(api_get(base, _fill('/v1/users/{user_id}/saved-searches', args.get_users_saved_searches_user_id)))
    if args.post_users_saved_searches_user_id:
        return show(api_send(base, _fill('/v1/users/{user_id}/saved-searches', args.post_users_saved_searches_user_id), 'POST', _body(args)))
    if args.delete_saved_searches_search_id:
        return show(api_delete(base, _fill('/v1/saved-searches/{search_id}', args.delete_saved_searches_search_id)))
    print("No endpoint flag provided. Use -h to list available endpoints.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
