#!/usr/bin/env python3
"""CLI helper for reading YouTube channel data — videos, playlists, comments, search, and analytics."""

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
    parser = argparse.ArgumentParser(description="Query a YouTube Data API v3 service")
    parser.add_argument("--channel", metavar="CHANNEL_ID",
                        help="Fetch channel profile and statistics")
    parser.add_argument("--videos", metavar="CHANNEL_ID",
                        help="List videos for a channel")
    parser.add_argument("--video", metavar="VIDEO_ID",
                        help="Fetch details for a specific video")
    parser.add_argument("--playlists", metavar="CHANNEL_ID",
                        help="List playlists for a channel")
    parser.add_argument("--playlist-items", metavar="PLAYLIST_ID",
                        help="List items in a playlist")
    parser.add_argument("--comments", metavar="VIDEO_ID",
                        help="List comment threads for a video")
    parser.add_argument("--replies", metavar="COMMENT_ID",
                        help="List replies to a comment")
    parser.add_argument("--search", metavar="QUERY",
                        help="Search videos by keyword")
    parser.add_argument("--captions", metavar="VIDEO_ID",
                        help="List captions for a video")
    parser.add_argument("--channel-sections", metavar="CHANNEL_ID",
                        help="List channel sections")
    parser.add_argument("--categories", action="store_true",
                        help="List video categories")
    parser.add_argument("--analytics", metavar="VIDEO_ID", nargs="?", const="channel",
                        help="Get analytics (no arg=channel, or pass video ID)")
    parser.add_argument("--channel-id", metavar="CHANNEL_ID",
                        help="Channel ID for search (default: UC_TechCraftAcademy)")
    parser.add_argument("--order", choices=["relevance", "date", "viewCount", "rating"],
                        help="Sort order for search results")
    parser.add_argument("--moderation-status", choices=["published", "heldForReview", "rejected"],
                        help="Filter comments by moderation status")
    parser.add_argument("--max-results", type=int,
                        help="Maximum results to return")

    args = parser.parse_args()
    base_url = os.environ.get("YOUTUBE_API_URL", "http://localhost:8009")

    try:
        if args.channel:
            print_json(api_get(base_url, "/youtube/v3/channels", {"id": args.channel, "part": "snippet,contentDetails,statistics,brandingSettings"}))
            return

        if args.videos:
            params = {"channelId": args.videos, "part": "snippet,contentDetails,statistics,status"}
            if args.max_results:
                params["maxResults"] = str(args.max_results)
            print_json(api_get(base_url, "/youtube/v3/videos", params))
            return

        if args.video:
            print_json(api_get(base_url, "/youtube/v3/videos", {"id": args.video, "part": "snippet,contentDetails,statistics,status"}))
            return

        if args.playlists:
            params = {"channelId": args.playlists, "part": "snippet,contentDetails,status"}
            if args.max_results:
                params["maxResults"] = str(args.max_results)
            print_json(api_get(base_url, "/youtube/v3/playlists", params))
            return

        if args.playlist_items:
            params = {"playlistId": args.playlist_items, "part": "snippet,contentDetails"}
            if args.max_results:
                params["maxResults"] = str(args.max_results)
            print_json(api_get(base_url, "/youtube/v3/playlistItems", params))
            return

        if args.comments:
            params = {"videoId": args.comments, "part": "snippet,replies"}
            if args.max_results:
                params["maxResults"] = str(args.max_results)
            if args.moderation_status:
                params["moderationStatus"] = args.moderation_status
            print_json(api_get(base_url, "/youtube/v3/commentThreads", params))
            return

        if args.replies:
            params = {"parentId": args.replies, "part": "snippet"}
            if args.max_results:
                params["maxResults"] = str(args.max_results)
            print_json(api_get(base_url, "/youtube/v3/comments", params))
            return

        if args.search:
            channel_id = args.channel_id or "UC_TechCraftAcademy"
            params = {"q": args.search, "channelId": channel_id, "part": "snippet"}
            if args.order:
                params["order"] = args.order
            if args.max_results:
                params["maxResults"] = str(args.max_results)
            print_json(api_get(base_url, "/youtube/v3/search", params))
            return

        if args.captions:
            print_json(api_get(base_url, "/youtube/v3/captions", {"videoId": args.captions, "part": "snippet"}))
            return

        if args.channel_sections:
            print_json(api_get(base_url, "/youtube/v3/channelSections", {"channelId": args.channel_sections, "part": "snippet,contentDetails"}))
            return

        if args.categories:
            print_json(api_get(base_url, "/youtube/v3/videoCategories", {"regionCode": "US", "part": "snippet"}))
            return

        if args.analytics is not None:
            if args.analytics == "channel":
                print_json(api_get(base_url, "/youtube/analytics/v2/reports", {"ids": "channel==UC_TechCraftAcademy", "metrics": "views,estimatedMinutesWatched,subscribersGained"}))
            else:
                print_json(api_get(base_url, "/youtube/analytics/v2/reports", {"ids": "channel==UC_TechCraftAcademy", "filters": f"video=={args.analytics}", "metrics": "views,estimatedMinutesWatched,likes"}))
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
