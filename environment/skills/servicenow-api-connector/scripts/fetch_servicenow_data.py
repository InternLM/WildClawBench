#!/usr/bin/env python3
"""CLI helper for the ServiceNow Table API (Mock) mock API.

Generated read/write helper: one flag per endpoint. Base URL comes from
$SERVICENOW_API_URL (override with --url). POST/PUT/PATCH bodies are read from --data
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
    p = argparse.ArgumentParser(description="Query the ServiceNow Table API (Mock) mock API")
    p.add_argument("--get-api-now-table-incident", action="store_true", help="GET /api/now/table/incident")
    p.add_argument("--get-api-now-table-incident-sys-id", metavar="SYS_ID", nargs=1, help="GET /api/now/table/incident/{sys_id}")
    p.add_argument("--post-api-now-table-incident", action="store_true", help="POST /api/now/table/incident")
    p.add_argument("--patch-api-now-table-incident-sys-id", metavar="SYS_ID", nargs=1, help="PATCH /api/now/table/incident/{sys_id}")
    p.add_argument("--get-api-now-table-change-request", action="store_true", help="GET /api/now/table/change_request")
    p.add_argument("--get-api-now-table-change-request-sys-id", metavar="SYS_ID", nargs=1, help="GET /api/now/table/change_request/{sys_id}")
    p.add_argument("--get-api-now-table-problem", action="store_true", help="GET /api/now/table/problem")
    p.add_argument("--get-api-now-table-problem-sys-id", metavar="SYS_ID", nargs=1, help="GET /api/now/table/problem/{sys_id}")
    p.add_argument("--get-api-now-table-sys-user", action="store_true", help="GET /api/now/table/sys_user")
    p.add_argument("--get-api-now-table-sys-user-sys-id", metavar="SYS_ID", nargs=1, help="GET /api/now/table/sys_user/{sys_id}")
    p.add_argument("--data", metavar="JSON", help="Request body as a JSON string (POST/PUT/PATCH)")
    p.add_argument("--data-file", metavar="PATH", help="Request body from a JSON file (POST/PUT/PATCH)")
    p.add_argument("--url", default=os.environ.get("SERVICENOW_API_URL", "http://localhost:8071"),
                   help="API base URL (default: $SERVICENOW_API_URL or http://localhost:8071)")
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
    if args.get_api_now_table_incident:
        return show(api_get(base, "/api/now/table/incident"))
    if args.get_api_now_table_incident_sys_id:
        return show(api_get(base, _fill('/api/now/table/incident/{sys_id}', args.get_api_now_table_incident_sys_id)))
    if args.post_api_now_table_incident:
        return show(api_send(base, '/api/now/table/incident', 'POST', _body(args)))
    if args.patch_api_now_table_incident_sys_id:
        return show(api_send(base, _fill('/api/now/table/incident/{sys_id}', args.patch_api_now_table_incident_sys_id), 'PATCH', _body(args)))
    if args.get_api_now_table_change_request:
        return show(api_get(base, "/api/now/table/change_request"))
    if args.get_api_now_table_change_request_sys_id:
        return show(api_get(base, _fill('/api/now/table/change_request/{sys_id}', args.get_api_now_table_change_request_sys_id)))
    if args.get_api_now_table_problem:
        return show(api_get(base, "/api/now/table/problem"))
    if args.get_api_now_table_problem_sys_id:
        return show(api_get(base, _fill('/api/now/table/problem/{sys_id}', args.get_api_now_table_problem_sys_id)))
    if args.get_api_now_table_sys_user:
        return show(api_get(base, "/api/now/table/sys_user"))
    if args.get_api_now_table_sys_user_sys_id:
        return show(api_get(base, _fill('/api/now/table/sys_user/{sys_id}', args.get_api_now_table_sys_user_sys_id)))
    print("No endpoint flag provided. Use -h to list available endpoints.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
