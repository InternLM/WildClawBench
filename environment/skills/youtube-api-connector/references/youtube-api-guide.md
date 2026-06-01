# YouTube Data API v3 Guide

Detailed patterns and examples for working with the YouTube channel management API.

## Base URL

Set via the `YOUTUBE_API_URL` environment variable (e.g. `http://youtube-api:8009`).

## Channel Info

```bash
# Get channel profile with all parts
curl "$YOUTUBE_API_URL/youtube/v3/channels?id=UC_TechCraftAcademy&part=snippet,contentDetails,statistics,brandingSettings"
```

## Videos

```bash
# List all channel videos
curl "$YOUTUBE_API_URL/youtube/v3/videos?channelId=UC_TechCraftAcademy&part=snippet,contentDetails,statistics,status&maxResults=10"

# Get a specific video by ID
curl "$YOUTUBE_API_URL/youtube/v3/videos?id=vid_001&part=snippet,contentDetails,statistics,status"

# Get multiple videos at once
curl "$YOUTUBE_API_URL/youtube/v3/videos?id=vid_001,vid_002,vid_003&part=snippet,statistics"
```

## Updating Videos

```bash
# Update video title, description, and tags
curl -X PUT "$YOUTUBE_API_URL/youtube/v3/videos?part=snippet,status" \
  -H "Content-Type: application/json" \
  -d '{
    "id": "vid_005",
    "snippet": {
      "title": "8 VS Code Extensions Senior Devs Use Daily",
      "description": "Updated description for better SEO.",
      "tags": ["vs code", "vscode extensions", "developer tools", "productivity", "2025"]
    }
  }'

# Change privacy status
curl -X PUT "$YOUTUBE_API_URL/youtube/v3/videos?part=status" \
  -H "Content-Type: application/json" \
  -d '{
    "id": "vid_028",
    "status": {
      "privacyStatus": "public"
    }
  }'
```

## Deleting Videos

```bash
curl -X DELETE "$YOUTUBE_API_URL/youtube/v3/videos?id=vid_030"
```

## Playlists

```bash
# List all channel playlists
curl "$YOUTUBE_API_URL/youtube/v3/playlists?channelId=UC_TechCraftAcademy&part=snippet,contentDetails,status&maxResults=10"

# Get a specific playlist
curl "$YOUTUBE_API_URL/youtube/v3/playlists?id=PL_001&part=snippet,contentDetails,status"
```

## Creating Playlists

```bash
curl -X POST "$YOUTUBE_API_URL/youtube/v3/playlists?part=snippet,status" \
  -H "Content-Type: application/json" \
  -d '{
    "snippet": {
      "title": "AI & Machine Learning",
      "description": "Tutorials on AI, ML, and LLMs for developers"
    },
    "status": {
      "privacyStatus": "public"
    }
  }'
```

## Updating Playlists

```bash
curl -X PUT "$YOUTUBE_API_URL/youtube/v3/playlists?part=snippet,status" \
  -H "Content-Type: application/json" \
  -d '{
    "id": "PL_005",
    "snippet": {
      "title": "Tool Reviews & Comparisons 2025",
      "description": "Updated reviews for the latest developer tools"
    }
  }'
```

## Deleting Playlists

```bash
curl -X DELETE "$YOUTUBE_API_URL/youtube/v3/playlists?id=PL_010"
```

## Playlist Items

```bash
# List items in a playlist
curl "$YOUTUBE_API_URL/youtube/v3/playlistItems?playlistId=PL_001&part=snippet,contentDetails&maxResults=10"
```

## Adding Videos to Playlists

```bash
curl -X POST "$YOUTUBE_API_URL/youtube/v3/playlistItems?part=snippet" \
  -H "Content-Type: application/json" \
  -d '{
    "snippet": {
      "playlistId": "PL_001",
      "resourceId": {
        "kind": "youtube#video",
        "videoId": "vid_020"
      },
      "position": 2
    }
  }'
```

## Reordering Playlist Items

```bash
curl -X PUT "$YOUTUBE_API_URL/youtube/v3/playlistItems?part=snippet" \
  -H "Content-Type: application/json" \
  -d '{
    "id": "PLI_003",
    "snippet": {
      "position": 5
    }
  }'
```

## Removing Playlist Items

```bash
curl -X DELETE "$YOUTUBE_API_URL/youtube/v3/playlistItems?id=PLI_025"
```

## Comment Threads

```bash
# List published comments for a video
curl "$YOUTUBE_API_URL/youtube/v3/commentThreads?videoId=vid_001&part=snippet,replies&maxResults=10"

# List comments held for review
curl "$YOUTUBE_API_URL/youtube/v3/commentThreads?videoId=vid_019&part=snippet,replies&moderationStatus=heldForReview"

# Post a new top-level comment
curl -X POST "$YOUTUBE_API_URL/youtube/v3/commentThreads?part=snippet" \
  -H "Content-Type: application/json" \
  -d '{
    "snippet": {
      "videoId": "vid_001",
      "topLevelComment": {
        "snippet": {
          "textOriginal": "Great video! Thanks for the project ideas."
        }
      }
    }
  }'
```

## Comments (Replies)

```bash
# List replies to a comment
curl "$YOUTUBE_API_URL/youtube/v3/comments?parentId=cmt_002&part=snippet"

# Reply to a comment
curl -X POST "$YOUTUBE_API_URL/youtube/v3/comments?part=snippet" \
  -H "Content-Type: application/json" \
  -d '{
    "snippet": {
      "parentId": "cmt_005",
      "textOriginal": "Thanks for asking! I used Next.js with the app router."
    }
  }'

# Edit a comment
curl -X PUT "$YOUTUBE_API_URL/youtube/v3/comments?part=snippet" \
  -H "Content-Type: application/json" \
  -d '{
    "id": "cmt_003",
    "snippet": {
      "textOriginal": "Updated reply: Socket.io is great! Also check out the ws library."
    }
  }'

# Delete a comment
curl -X DELETE "$YOUTUBE_API_URL/youtube/v3/comments?id=cmt_026"
```

## Comment Moderation

```bash
# Approve a held comment
curl -X POST "$YOUTUBE_API_URL/youtube/v3/comments/setModerationStatus?id=cmt_028&moderationStatus=published"

# Reject a spam comment
curl -X POST "$YOUTUBE_API_URL/youtube/v3/comments/setModerationStatus?id=cmt_029&moderationStatus=rejected"
```

## Search

```bash
# Search by keyword
curl "$YOUTUBE_API_URL/youtube/v3/search?q=python&channelId=UC_TechCraftAcademy&part=snippet&maxResults=10"

# Search sorted by view count
curl "$YOUTUBE_API_URL/youtube/v3/search?q=career&channelId=UC_TechCraftAcademy&part=snippet&order=viewCount&maxResults=5"

# List recent uploads (search ordered by date)
curl "$YOUTUBE_API_URL/youtube/v3/search?channelId=UC_TechCraftAcademy&part=snippet&order=date&maxResults=5"
```

## Video Categories

```bash
curl "$YOUTUBE_API_URL/youtube/v3/videoCategories?regionCode=US&part=snippet"
```

## Captions

```bash
# List captions for a video
curl "$YOUTUBE_API_URL/youtube/v3/captions?videoId=vid_002&part=snippet"
```

## Channel Sections

```bash
curl "$YOUTUBE_API_URL/youtube/v3/channelSections?channelId=UC_TechCraftAcademy&part=snippet,contentDetails"
```

## Analytics

```bash
# Channel-level analytics (last 28 days)
curl "$YOUTUBE_API_URL/youtube/analytics/v2/reports?ids=channel==UC_TechCraftAcademy&metrics=views,estimatedMinutesWatched,subscribersGained&startDate=2025-03-01&endDate=2025-03-31"

# Video-level analytics
curl "$YOUTUBE_API_URL/youtube/analytics/v2/reports?ids=channel==UC_TechCraftAcademy&filters=video==vid_001&metrics=views,estimatedMinutesWatched,likes&startDate=2025-03-01&endDate=2025-03-31"
```

## Common Patterns

### Find Videos Needing SEO Improvement (Low Views, Good Content)

```python
import json
import os
import urllib.request

BASE = os.environ["YOUTUBE_API_URL"]
CHANNEL_ID = "UC_TechCraftAcademy"

def api_get(path, params=None):
    url = f"{BASE}{path}"
    if params:
        url += "?" + "&".join(f"{k}={v}" for k, v in params.items())
    with urllib.request.urlopen(url) as r:
        return json.loads(r.read())

videos = api_get("/youtube/v3/videos", {"channelId": CHANNEL_ID, "maxResults": "50"})
for item in videos["items"]:
    views = int(item["statistics"]["viewCount"])
    likes = int(item["statistics"]["likeCount"])
    if views < 50000 and likes > 1000:
        title = item["snippet"]["title"]
        print(f"Underperforming: '{title}' — {views} views but {likes} likes. Consider SEO update.")
```

### Moderate Held Comments and Reply to Questions

```python
threads = api_get("/youtube/v3/commentThreads", {
    "videoId": "vid_001",
    "moderationStatus": "heldForReview",
    "maxResults": "50"
})
for thread in threads["items"]:
    text = thread["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
    cid = thread["id"]
    if "?" in text:
        print(f"Question held for review (cmt {cid}): {text[:80]}...")
    else:
        print(f"Non-question held (cmt {cid}): {text[:80]}...")
```

### Generate Channel Performance Summary

```python
channel = api_get("/youtube/v3/channels", {"id": CHANNEL_ID})
stats = channel["items"][0]["statistics"]
analytics = api_get("/youtube/analytics/v2/reports", {
    "ids": f"channel=={CHANNEL_ID}",
    "metrics": "views,estimatedMinutesWatched,subscribersGained"
})
metrics = analytics["metrics"]

print(f"Channel: {channel['items'][0]['snippet']['title']}")
print(f"Total subscribers: {stats['subscriberCount']}")
print(f"Last 28 days: {metrics['views']} views, {metrics['subscribersGained']} new subs")
print(f"Watch time: {metrics['estimatedMinutesWatched']} minutes")
```
