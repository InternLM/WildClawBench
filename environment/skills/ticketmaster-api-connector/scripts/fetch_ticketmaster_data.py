#!/usr/bin/env python3
"""CLI helper for the Ticketmaster Discovery API (Mock) mock API.

Generated read/write helper: one flag per endpoint. Base URL comes from
$TICKETMASTER_API_URL (override with --url). POST/PUT/PATCH bodies are read from --data
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
    p = argparse.ArgumentParser(description="Query the Ticketmaster Discovery API (Mock) mock API")
    p.add_argument("--get-discovery-events", action="store_true", help="GET /discovery/v2/events")
    p.add_argument("--get-discovery-events-event-id", metavar="EVENT_ID", nargs=1, help="GET /discovery/v2/events/{event_id}")
    p.add_argument("--get-discovery-venues", action="store_true", help="GET /discovery/v2/venues")
    p.add_argument("--get-discovery-venues-venue-id", metavar="VENUE_ID", nargs=1, help="GET /discovery/v2/venues/{venue_id}")
    p.add_argument("--get-discovery-attractions", action="store_true", help="GET /discovery/v2/attractions")
    p.add_argument("--get-discovery-attractions-attraction-id", metavar="ATTRACTION_ID", nargs=1, help="GET /discovery/v2/attractions/{attraction_id}")
    p.add_argument("--get-discovery-classifications", action="store_true", help="GET /discovery/v2/classifications")
    p.add_argument("--data", metavar="JSON", help="Request body as a JSON string (POST/PUT/PATCH)")
    p.add_argument("--data-file", metavar="PATH", help="Request body from a JSON file (POST/PUT/PATCH)")
    p.add_argument("--url", default=os.environ.get("TICKETMASTER_API_URL", "http://localhost:8075"),
                   help="API base URL (default: $TICKETMASTER_API_URL or http://localhost:8075)")
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
    if args.get_discovery_events:
        return show(api_get(base, "/discovery/v2/events"))
    if args.get_discovery_events_event_id:
        return show(api_get(base, _fill('/discovery/v2/events/{event_id}', args.get_discovery_events_event_id)))
    if args.get_discovery_venues:
        return show(api_get(base, "/discovery/v2/venues"))
    if args.get_discovery_venues_venue_id:
        return show(api_get(base, _fill('/discovery/v2/venues/{venue_id}', args.get_discovery_venues_venue_id)))
    if args.get_discovery_attractions:
        return show(api_get(base, "/discovery/v2/attractions"))
    if args.get_discovery_attractions_attraction_id:
        return show(api_get(base, _fill('/discovery/v2/attractions/{attraction_id}', args.get_discovery_attractions_attraction_id)))
    if args.get_discovery_classifications:
        return show(api_get(base, "/discovery/v2/classifications"))
    print("No endpoint flag provided. Use -h to list available endpoints.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
