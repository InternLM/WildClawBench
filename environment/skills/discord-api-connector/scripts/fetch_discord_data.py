#!/usr/bin/env python3
"""CLI helper for the Discord API (Mock) mock API.

Generated read/write helper: one flag per endpoint. Base URL comes from
$DISCORD_API_URL (override with --url). POST/PUT/PATCH bodies are read from --data
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
    p = argparse.ArgumentParser(description="Query the Discord API (Mock) mock API")
    p.add_argument("--get-api-users-me", action="store_true", help="GET /api/v10/users/@me")
    p.add_argument("--get-api-users-me-guilds", action="store_true", help="GET /api/v10/users/@me/guilds")
    p.add_argument("--get-api-guilds-guild-id", metavar="GUILD_ID", nargs=1, help="GET /api/v10/guilds/{guild_id}")
    p.add_argument("--get-api-guilds-channels-guild-id", metavar="GUILD_ID", nargs=1, help="GET /api/v10/guilds/{guild_id}/channels")
    p.add_argument("--get-api-guilds-members-guild-id", metavar="GUILD_ID", nargs=1, help="GET /api/v10/guilds/{guild_id}/members")
    p.add_argument("--get-api-guilds-roles-guild-id", metavar="GUILD_ID", nargs=1, help="GET /api/v10/guilds/{guild_id}/roles")
    p.add_argument("--get-api-channels-channel-id", metavar="CHANNEL_ID", nargs=1, help="GET /api/v10/channels/{channel_id}")
    p.add_argument("--get-api-channels-messages-channel-id", metavar="CHANNEL_ID", nargs=1, help="GET /api/v10/channels/{channel_id}/messages")
    p.add_argument("--post-api-channels-messages-channel-id", metavar="CHANNEL_ID", nargs=1, help="POST /api/v10/channels/{channel_id}/messages")
    p.add_argument("--data", metavar="JSON", help="Request body as a JSON string (POST/PUT/PATCH)")
    p.add_argument("--data-file", metavar="PATH", help="Request body from a JSON file (POST/PUT/PATCH)")
    p.add_argument("--url", default=os.environ.get("DISCORD_API_URL", "http://localhost:8057"),
                   help="API base URL (default: $DISCORD_API_URL or http://localhost:8057)")
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
    if args.get_api_users_me:
        return show(api_get(base, "/api/v10/users/@me"))
    if args.get_api_users_me_guilds:
        return show(api_get(base, "/api/v10/users/@me/guilds"))
    if args.get_api_guilds_guild_id:
        return show(api_get(base, _fill('/api/v10/guilds/{guild_id}', args.get_api_guilds_guild_id)))
    if args.get_api_guilds_channels_guild_id:
        return show(api_get(base, _fill('/api/v10/guilds/{guild_id}/channels', args.get_api_guilds_channels_guild_id)))
    if args.get_api_guilds_members_guild_id:
        return show(api_get(base, _fill('/api/v10/guilds/{guild_id}/members', args.get_api_guilds_members_guild_id)))
    if args.get_api_guilds_roles_guild_id:
        return show(api_get(base, _fill('/api/v10/guilds/{guild_id}/roles', args.get_api_guilds_roles_guild_id)))
    if args.get_api_channels_channel_id:
        return show(api_get(base, _fill('/api/v10/channels/{channel_id}', args.get_api_channels_channel_id)))
    if args.get_api_channels_messages_channel_id:
        return show(api_get(base, _fill('/api/v10/channels/{channel_id}/messages', args.get_api_channels_messages_channel_id)))
    if args.post_api_channels_messages_channel_id:
        return show(api_send(base, _fill('/api/v10/channels/{channel_id}/messages', args.post_api_channels_messages_channel_id), 'POST', _body(args)))
    print("No endpoint flag provided. Use -h to list available endpoints.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
