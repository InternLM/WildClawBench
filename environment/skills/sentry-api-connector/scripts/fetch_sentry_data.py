#!/usr/bin/env python3
"""CLI helper for the Sentry API (Mock) mock API.

Generated read/write helper: one flag per endpoint. Base URL comes from
$SENTRY_API_URL (override with --url). POST/PUT/PATCH bodies are read from --data
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
    p = argparse.ArgumentParser(description="Query the Sentry API (Mock) mock API")
    p.add_argument("--get-api-0-organizations-projects-org-slug", metavar="ORG_SLUG", nargs=1, help="GET /api/0/organizations/{org_slug}/projects/")
    p.add_argument("--get-api-0-projects-issues-org-slug-project-slug", metavar="ORG_SLUG/PROJECT_SLUG", nargs=2, help="GET /api/0/projects/{org_slug}/{project_slug}/issues/")
    p.add_argument("--get-api-0-organizations-issues-org-slug-issue-id", metavar="ORG_SLUG/ISSUE_ID", nargs=2, help="GET /api/0/organizations/{org_slug}/issues/{issue_id}/")
    p.add_argument("--put-api-0-organizations-issues-org-slug-issue-id", metavar="ORG_SLUG/ISSUE_ID", nargs=2, help="PUT /api/0/organizations/{org_slug}/issues/{issue_id}/")
    p.add_argument("--get-api-0-organizations-issues-events-org-slug-issue-id", metavar="ORG_SLUG/ISSUE_ID", nargs=2, help="GET /api/0/organizations/{org_slug}/issues/{issue_id}/events/")
    p.add_argument("--get-api-0-organizations-releases-org-slug", metavar="ORG_SLUG", nargs=1, help="GET /api/0/organizations/{org_slug}/releases/")
    p.add_argument("--data", metavar="JSON", help="Request body as a JSON string (POST/PUT/PATCH)")
    p.add_argument("--data-file", metavar="PATH", help="Request body from a JSON file (POST/PUT/PATCH)")
    p.add_argument("--url", default=os.environ.get("SENTRY_API_URL", "http://localhost:8047"),
                   help="API base URL (default: $SENTRY_API_URL or http://localhost:8047)")
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
    if args.get_api_0_organizations_projects_org_slug:
        return show(api_get(base, _fill('/api/0/organizations/{org_slug}/projects/', args.get_api_0_organizations_projects_org_slug)))
    if args.get_api_0_projects_issues_org_slug_project_slug:
        return show(api_get(base, _fill('/api/0/projects/{org_slug}/{project_slug}/issues/', args.get_api_0_projects_issues_org_slug_project_slug)))
    if args.get_api_0_organizations_issues_org_slug_issue_id:
        return show(api_get(base, _fill('/api/0/organizations/{org_slug}/issues/{issue_id}/', args.get_api_0_organizations_issues_org_slug_issue_id)))
    if args.put_api_0_organizations_issues_org_slug_issue_id:
        return show(api_send(base, _fill('/api/0/organizations/{org_slug}/issues/{issue_id}/', args.put_api_0_organizations_issues_org_slug_issue_id), 'PUT', _body(args)))
    if args.get_api_0_organizations_issues_events_org_slug_issue_id:
        return show(api_get(base, _fill('/api/0/organizations/{org_slug}/issues/{issue_id}/events/', args.get_api_0_organizations_issues_events_org_slug_issue_id)))
    if args.get_api_0_organizations_releases_org_slug:
        return show(api_get(base, _fill('/api/0/organizations/{org_slug}/releases/', args.get_api_0_organizations_releases_org_slug)))
    print("No endpoint flag provided. Use -h to list available endpoints.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
