#!/usr/bin/env python3
"""CLI helper for reading Ring home security data — devices, events, recordings, and health."""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error
import urllib.parse


def api_get(base_url, path, params=None):
    url = f"{base_url}{path}"
    if params:
        filtered = {k: v for k, v in params.items() if v is not None}
        if filtered:
            url += "?" + urllib.parse.urlencode(filtered)
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())


def print_json(data):
    print(json.dumps(data, indent=2))


def main():
    parser = argparse.ArgumentParser(description="Query a Ring API service")
    parser.add_argument("--devices",
                        action="store_true",
                        help="List all Ring devices")
    parser.add_argument("--device", metavar="DEVICE_ID",
                        help="Get details for a specific device")
    parser.add_argument("--health", metavar="DEVICE_ID",
                        help="Get health/battery info for a device")
    parser.add_argument("--history", metavar="DEVICE_ID",
                        help="List event history for a device")
    parser.add_argument("--event", metavar="EVENT_ID",
                        help="Get details for a specific event")
    parser.add_argument("--recording", metavar="EVENT_ID",
                        help="Get recording URL for an event")
    parser.add_argument("--recordings", metavar="DEVICE_ID",
                        help="List recordings for a device")
    parser.add_argument("--active-dings",
                        action="store_true",
                        help="List currently active alerts")
    parser.add_argument("--location", metavar="LOCATION_ID",
                        help="Get location details")
    parser.add_argument("--mode", metavar="LOCATION_ID",
                        help="Get current security mode for a location")
    parser.add_argument("--users", metavar="LOCATION_ID",
                        help="List shared users for a location")
    parser.add_argument("--zones", metavar="DEVICE_ID",
                        help="List motion zones for a device")
    parser.add_argument("--notifications",
                        action="store_true",
                        help="List all notification preferences")
    parser.add_argument("--notification", metavar="DEVICE_ID",
                        help="Get notification preferences for a device")
    parser.add_argument("--chime", metavar="DEVICE_ID",
                        help="Get chime settings for a device")
    parser.add_argument("--kind",
                        help="Filter events by kind (motion, ding, person_detected, package_detected)")
    parser.add_argument("--date-from",
                        help="Filter events from date (ISO format)")
    parser.add_argument("--date-to",
                        help="Filter events to date (ISO format)")
    parser.add_argument("--limit", type=int,
                        help="Maximum results to return")

    args = parser.parse_args()
    base_url = os.environ.get("RING_API_URL", "http://localhost:8008")

    try:
        if args.devices:
            print_json(api_get(base_url, "/clients_api/ring_devices"))
            return

        if args.device:
            print_json(api_get(base_url, f"/clients_api/doorbots/{args.device}"))
            return

        if args.health:
            print_json(api_get(base_url, f"/clients_api/doorbots/{args.health}/health"))
            return

        if args.history:
            params = {}
            if args.kind:
                params["kind"] = args.kind
            if args.date_from:
                params["date_from"] = args.date_from
            if args.date_to:
                params["date_to"] = args.date_to
            if args.limit:
                params["limit"] = str(args.limit)
            print_json(api_get(base_url, f"/clients_api/doorbots/{args.history}/history", params or None))
            return

        if args.event:
            print_json(api_get(base_url, f"/clients_api/dings/{args.event}"))
            return

        if args.recording:
            print_json(api_get(base_url, f"/clients_api/dings/{args.recording}/recording"))
            return

        if args.recordings:
            params = {}
            if args.date_from:
                params["date_from"] = args.date_from
            if args.date_to:
                params["date_to"] = args.date_to
            print_json(api_get(base_url, f"/clients_api/doorbots/{args.recordings}/recordings", params or None))
            return

        if args.active_dings:
            print_json(api_get(base_url, "/clients_api/dings/active"))
            return

        if args.location:
            print_json(api_get(base_url, f"/clients_api/locations/{args.location}"))
            return

        if args.mode:
            print_json(api_get(base_url, f"/clients_api/locations/{args.mode}/mode"))
            return

        if args.users:
            print_json(api_get(base_url, f"/clients_api/locations/{args.users}/users"))
            return

        if args.zones:
            print_json(api_get(base_url, f"/clients_api/doorbots/{args.zones}/motion_zones"))
            return

        if args.notifications:
            print_json(api_get(base_url, "/clients_api/notifications"))
            return

        if args.notification:
            print_json(api_get(base_url, f"/clients_api/notifications/{args.notification}"))
            return

        if args.chime:
            print_json(api_get(base_url, f"/clients_api/chimes/{args.chime}/settings"))
            return

        parser.print_help()

    except urllib.error.HTTPError as exc:
        print(f"HTTP {exc.code}: {exc.reason}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as exc:
        print(f"Connection error: {exc.reason}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
