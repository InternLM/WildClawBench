#!/usr/bin/env python3
"""CLI helper for the LinkedIn API v2 (Mock) mock API.

Generated read/write helper: one flag per endpoint. Base URL comes from
$LINKEDIN_API_URL (override with --url). POST/PUT/PATCH bodies are read from --data
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
    p = argparse.ArgumentParser(description="Query the LinkedIn API v2 (Mock) mock API")
    p.add_argument("--get-me", action="store_true", help="GET /v2/me")
    p.add_argument("--get-connections", action="store_true", help="GET /v2/connections")
    p.add_argument("--get-posts", action="store_true", help="GET /v2/posts")
    p.add_argument("--post-posts", action="store_true", help="POST /v2/posts")
    p.add_argument("--get-posts-post-id", metavar="POST_ID", nargs=1, help="GET /v2/posts/{post_id}")
    p.add_argument("--get-organizations-org-id", metavar="ORG_ID", nargs=1, help="GET /v2/organizations/{org_id}")
    p.add_argument("--get-jobs", action="store_true", help="GET /v2/jobs")
    p.add_argument("--get-jobs-job-id", metavar="JOB_ID", nargs=1, help="GET /v2/jobs/{job_id}")
    p.add_argument("--data", metavar="JSON", help="Request body as a JSON string (POST/PUT/PATCH)")
    p.add_argument("--data-file", metavar="PATH", help="Request body from a JSON file (POST/PUT/PATCH)")
    p.add_argument("--url", default=os.environ.get("LINKEDIN_API_URL", "http://localhost:8062"),
                   help="API base URL (default: $LINKEDIN_API_URL or http://localhost:8062)")
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
    if args.get_me:
        return show(api_get(base, "/v2/me"))
    if args.get_connections:
        return show(api_get(base, "/v2/connections"))
    if args.get_posts:
        return show(api_get(base, "/v2/posts"))
    if args.post_posts:
        return show(api_send(base, '/v2/posts', 'POST', _body(args)))
    if args.get_posts_post_id:
        return show(api_get(base, _fill('/v2/posts/{post_id}', args.get_posts_post_id)))
    if args.get_organizations_org_id:
        return show(api_get(base, _fill('/v2/organizations/{org_id}', args.get_organizations_org_id)))
    if args.get_jobs:
        return show(api_get(base, "/v2/jobs"))
    if args.get_jobs_job_id:
        return show(api_get(base, _fill('/v2/jobs/{job_id}', args.get_jobs_job_id)))
    print("No endpoint flag provided. Use -h to list available endpoints.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
