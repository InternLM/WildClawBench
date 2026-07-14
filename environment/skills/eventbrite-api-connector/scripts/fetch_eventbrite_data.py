#!/usr/bin/env python3
"""CLI helper for the Eventbrite API (Mock) mock API.

Generated read/write helper: one flag per endpoint. Base URL comes from
$EVENTBRITE_API_URL (override with --url). POST/PUT/PATCH bodies are read from --data
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
    p = argparse.ArgumentParser(description="Query the Eventbrite API (Mock) mock API")
    p.add_argument("--get-users-me-organizations", action="store_true", help="GET /v3/users/me/organizations")
    p.add_argument("--get-organizations-org-id", metavar="ORG_ID", nargs=1, help="GET /v3/organizations/{org_id}")
    p.add_argument("--get-organizations-events-org-id", metavar="ORG_ID", nargs=1, help="GET /v3/organizations/{org_id}/events")
    p.add_argument("--get-events-search", action="store_true", help="GET /v3/events/search")
    p.add_argument("--get-events-event-id", metavar="EVENT_ID", nargs=1, help="GET /v3/events/{event_id}")
    p.add_argument("--post-events", action="store_true", help="POST /v3/events")
    p.add_argument("--post-events-publish-event-id", metavar="EVENT_ID", nargs=1, help="POST /v3/events/{event_id}/publish")
    p.add_argument("--post-events-cancel-event-id", metavar="EVENT_ID", nargs=1, help="POST /v3/events/{event_id}/cancel")
    p.add_argument("--get-venues", action="store_true", help="GET /v3/venues")
    p.add_argument("--get-venues-venue-id", metavar="VENUE_ID", nargs=1, help="GET /v3/venues/{venue_id}")
    p.add_argument("--get-events-ticket-classes-event-id", metavar="EVENT_ID", nargs=1, help="GET /v3/events/{event_id}/ticket_classes")
    p.add_argument("--post-events-ticket-classes-event-id", metavar="EVENT_ID", nargs=1, help="POST /v3/events/{event_id}/ticket_classes")
    p.add_argument("--get-events-attendees-event-id", metavar="EVENT_ID", nargs=1, help="GET /v3/events/{event_id}/attendees")
    p.add_argument("--post-events-attendees-event-id", metavar="EVENT_ID", nargs=1, help="POST /v3/events/{event_id}/attendees")
    p.add_argument("--post-attendees-check-in-attendee-id", metavar="ATTENDEE_ID", nargs=1, help="POST /v3/attendees/{attendee_id}/check_in")
    p.add_argument("--data", metavar="JSON", help="Request body as a JSON string (POST/PUT/PATCH)")
    p.add_argument("--data-file", metavar="PATH", help="Request body from a JSON file (POST/PUT/PATCH)")
    p.add_argument("--url", default=os.environ.get("EVENTBRITE_API_URL", "http://localhost:8020"),
                   help="API base URL (default: $EVENTBRITE_API_URL or http://localhost:8020)")
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
    if args.get_users_me_organizations:
        return show(api_get(base, "/v3/users/me/organizations"))
    if args.get_organizations_org_id:
        return show(api_get(base, _fill('/v3/organizations/{org_id}', args.get_organizations_org_id)))
    if args.get_organizations_events_org_id:
        return show(api_get(base, _fill('/v3/organizations/{org_id}/events', args.get_organizations_events_org_id)))
    if args.get_events_search:
        return show(api_get(base, "/v3/events/search"))
    if args.get_events_event_id:
        return show(api_get(base, _fill('/v3/events/{event_id}', args.get_events_event_id)))
    if args.post_events:
        return show(api_send(base, '/v3/events', 'POST', _body(args)))
    if args.post_events_publish_event_id:
        return show(api_send(base, _fill('/v3/events/{event_id}/publish', args.post_events_publish_event_id), 'POST', _body(args)))
    if args.post_events_cancel_event_id:
        return show(api_send(base, _fill('/v3/events/{event_id}/cancel', args.post_events_cancel_event_id), 'POST', _body(args)))
    if args.get_venues:
        return show(api_get(base, "/v3/venues"))
    if args.get_venues_venue_id:
        return show(api_get(base, _fill('/v3/venues/{venue_id}', args.get_venues_venue_id)))
    if args.get_events_ticket_classes_event_id:
        return show(api_get(base, _fill('/v3/events/{event_id}/ticket_classes', args.get_events_ticket_classes_event_id)))
    if args.post_events_ticket_classes_event_id:
        return show(api_send(base, _fill('/v3/events/{event_id}/ticket_classes', args.post_events_ticket_classes_event_id), 'POST', _body(args)))
    if args.get_events_attendees_event_id:
        return show(api_get(base, _fill('/v3/events/{event_id}/attendees', args.get_events_attendees_event_id)))
    if args.post_events_attendees_event_id:
        return show(api_send(base, _fill('/v3/events/{event_id}/attendees', args.post_events_attendees_event_id), 'POST', _body(args)))
    if args.post_attendees_check_in_attendee_id:
        return show(api_send(base, _fill('/v3/attendees/{attendee_id}/check_in', args.post_attendees_check_in_attendee_id), 'POST', _body(args)))
    print("No endpoint flag provided. Use -h to list available endpoints.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
