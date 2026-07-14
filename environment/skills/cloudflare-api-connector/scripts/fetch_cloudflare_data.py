#!/usr/bin/env python3
"""CLI helper for the Cloudflare API (Mock) mock API.

Generated read/write helper: one flag per endpoint. Base URL comes from
$CLOUDFLARE_API_URL (override with --url). POST/PUT/PATCH bodies are read from --data
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
    p = argparse.ArgumentParser(description="Query the Cloudflare API (Mock) mock API")
    p.add_argument("--get-client-zones", action="store_true", help="GET /client/v4/zones")
    p.add_argument("--get-client-zones-zone-id", metavar="ZONE_ID", nargs=1, help="GET /client/v4/zones/{zone_id}")
    p.add_argument("--get-client-zones-dns-records-zone-id", metavar="ZONE_ID", nargs=1, help="GET /client/v4/zones/{zone_id}/dns_records")
    p.add_argument("--get-client-zones-dns-records-zone-id-record-id", metavar="ZONE_ID/RECORD_ID", nargs=2, help="GET /client/v4/zones/{zone_id}/dns_records/{record_id}")
    p.add_argument("--post-client-zones-dns-records-zone-id", metavar="ZONE_ID", nargs=1, help="POST /client/v4/zones/{zone_id}/dns_records")
    p.add_argument("--put-client-zones-dns-records-zone-id-record-id", metavar="ZONE_ID/RECORD_ID", nargs=2, help="PUT /client/v4/zones/{zone_id}/dns_records/{record_id}")
    p.add_argument("--delete-client-zones-dns-records-zone-id-record-id", metavar="ZONE_ID/RECORD_ID", nargs=2, help="DELETE /client/v4/zones/{zone_id}/dns_records/{record_id}")
    p.add_argument("--get-client-zones-firewall-rules-zone-id", metavar="ZONE_ID", nargs=1, help="GET /client/v4/zones/{zone_id}/firewall/rules")
    p.add_argument("--data", metavar="JSON", help="Request body as a JSON string (POST/PUT/PATCH)")
    p.add_argument("--data-file", metavar="PATH", help="Request body from a JSON file (POST/PUT/PATCH)")
    p.add_argument("--url", default=os.environ.get("CLOUDFLARE_API_URL", "http://localhost:8050"),
                   help="API base URL (default: $CLOUDFLARE_API_URL or http://localhost:8050)")
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
    if args.get_client_zones:
        return show(api_get(base, "/client/v4/zones"))
    if args.get_client_zones_zone_id:
        return show(api_get(base, _fill('/client/v4/zones/{zone_id}', args.get_client_zones_zone_id)))
    if args.get_client_zones_dns_records_zone_id:
        return show(api_get(base, _fill('/client/v4/zones/{zone_id}/dns_records', args.get_client_zones_dns_records_zone_id)))
    if args.get_client_zones_dns_records_zone_id_record_id:
        return show(api_get(base, _fill('/client/v4/zones/{zone_id}/dns_records/{record_id}', args.get_client_zones_dns_records_zone_id_record_id)))
    if args.post_client_zones_dns_records_zone_id:
        return show(api_send(base, _fill('/client/v4/zones/{zone_id}/dns_records', args.post_client_zones_dns_records_zone_id), 'POST', _body(args)))
    if args.put_client_zones_dns_records_zone_id_record_id:
        return show(api_send(base, _fill('/client/v4/zones/{zone_id}/dns_records/{record_id}', args.put_client_zones_dns_records_zone_id_record_id), 'PUT', _body(args)))
    if args.delete_client_zones_dns_records_zone_id_record_id:
        return show(api_delete(base, _fill('/client/v4/zones/{zone_id}/dns_records/{record_id}', args.delete_client_zones_dns_records_zone_id_record_id)))
    if args.get_client_zones_firewall_rules_zone_id:
        return show(api_get(base, _fill('/client/v4/zones/{zone_id}/firewall/rules', args.get_client_zones_firewall_rules_zone_id)))
    print("No endpoint flag provided. Use -h to list available endpoints.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
