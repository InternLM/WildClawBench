# Instagram Graph API Guide

Detailed patterns and examples for working with the Instagram Business/Creator account API.

## Base URL

Set via the `INSTAGRAM_API_URL` environment variable (e.g. `http://instagram-api:8003`).

## User / Account

```bash
# Get full account profile
curl "$INSTAGRAM_API_URL/17841400123456789"

# Get specific fields only
curl "$INSTAGRAM_API_URL/17841400123456789?fields=id,username,name,followers_count,media_count"

# Search users by username or name (partial match, case-insensitive)
curl "$INSTAGRAM_API_URL/ig_user_search?q=brewed"
curl "$INSTAGRAM_API_URL/ig_user_search?q=gallery"
```

## Media

```bash
# List all recent media
curl "$INSTAGRAM_API_URL/17841400123456789/media"

# List with pagination
curl "$INSTAGRAM_API_URL/17841400123456789/media?limit=5&offset=10"

# Filter by media type
curl "$INSTAGRAM_API_URL/17841400123456789/media?media_type=VIDEO"
curl "$INSTAGRAM_API_URL/17841400123456789/media?media_type=CAROUSEL_ALBUM"

# Select specific fields
curl "$INSTAGRAM_API_URL/17841400123456789/media?fields=id,caption,media_type,like_count,timestamp"

# Get a single media post
curl "$INSTAGRAM_API_URL/media/17900001002"

# Get media with specific fields
curl "$INSTAGRAM_API_URL/media/17900001002?fields=id,caption,like_count,comments_count"
```

## Deleting Media

```bash
curl -X DELETE "$INSTAGRAM_API_URL/media/17900001028"
```

## Carousel Children

```bash
# List children of a carousel post
curl "$INSTAGRAM_API_URL/media/17900001005/children"

# With fields filter
curl "$INSTAGRAM_API_URL/media/17900001005/children?fields=id,media_type,media_url"
```

## Comments

```bash
# List comments on a post
curl "$INSTAGRAM_API_URL/media/17900001002/comments"

# With pagination
curl "$INSTAGRAM_API_URL/media/17900001002/comments?limit=5"

# Get a single comment
curl "$INSTAGRAM_API_URL/comment/17800001001"

# Get replies to a comment
curl "$INSTAGRAM_API_URL/comment/17800001001/replies"
```

## Posting Comments

```bash
# Reply to an existing comment
curl -X POST "$INSTAGRAM_API_URL/media/17900001002/comments" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Thanks for the love! Come visit us this weekend!",
    "parent_id": "17800001003"
  }'

# Post a new top-level comment
curl -X POST "$INSTAGRAM_API_URL/media/17900001001/comments" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Fresh beans dropping next week! Stay tuned."
  }'
```

## Deleting Comments

```bash
curl -X DELETE "$INSTAGRAM_API_URL/media/17900001002/comments/17800001006"
```

## Hiding / Unhiding Comments

```bash
# Hide a spam comment
curl -X PUT "$INSTAGRAM_API_URL/media/17900001002/comments/17800001006/hide" \
  -H "Content-Type: application/json" \
  -d '{"hide": true}'

# Unhide a comment
curl -X PUT "$INSTAGRAM_API_URL/media/17900001002/comments/17800001003/hide" \
  -H "Content-Type: application/json" \
  -d '{"hide": false}'
```

## Stories

```bash
# List current stories
curl "$INSTAGRAM_API_URL/17841400123456789/stories"

# Get a single story
curl "$INSTAGRAM_API_URL/stories/17950001001"

# With fields filter
curl "$INSTAGRAM_API_URL/stories/17950001001?fields=id,media_type,timestamp,caption"
```

## Insights / Analytics

```bash
# Get all account-level insights
curl "$INSTAGRAM_API_URL/17841400123456789/insights"

# Get specific metrics
curl "$INSTAGRAM_API_URL/17841400123456789/insights?metric=impressions,reach"

# Get insights for a specific post
curl "$INSTAGRAM_API_URL/media/17900001002/insights"

# Filter post insights by metric
curl "$INSTAGRAM_API_URL/media/17900001002/insights?metric=impressions,reach,saved,shares"
```

## Hashtags

```bash
# Search for hashtags
curl "$INSTAGRAM_API_URL/ig_hashtag_search?q=coffee"
curl "$INSTAGRAM_API_URL/ig_hashtag_search?q=latteart"

# Get hashtag details
curl "$INSTAGRAM_API_URL/hashtag/17840001001"

# Get recent media for a hashtag (from our account)
curl "$INSTAGRAM_API_URL/hashtag/17840001001/recent_media?user_id=17841400123456789"
curl "$INSTAGRAM_API_URL/hashtag/17840001002/recent_media?user_id=17841400123456789&limit=5"
```

## Mentions / Tags

```bash
# List media where the account is tagged
curl "$INSTAGRAM_API_URL/17841400123456789/tags"

# With limit
curl "$INSTAGRAM_API_URL/17841400123456789/tags?limit=3"
```

## Content Publishing

```bash
# Step 1: Create a media container
curl -X POST "$INSTAGRAM_API_URL/17841400123456789/media" \
  -H "Content-Type: application/json" \
  -d '{
    "image_url": "https://example.com/new_coffee_photo.jpg",
    "caption": "Fresh roast Friday! Our new Costa Rica Tarrazu is here \u2615\n\n#specialtycoffee #freshroast #costarica",
    "media_type": "IMAGE"
  }'

# Step 1b: Create a video container
curl -X POST "$INSTAGRAM_API_URL/17841400123456789/media" \
  -H "Content-Type: application/json" \
  -d '{
    "video_url": "https://example.com/latte_art_reel.mp4",
    "caption": "Sunday latte art session \ud83c\udf37\n\n#latteart #baristalife",
    "media_type": "VIDEO"
  }'

# Step 2: Check container status
curl "$INSTAGRAM_API_URL/container/17920001001"

# Step 3: Publish the container
curl -X POST "$INSTAGRAM_API_URL/17841400123456789/media_publish" \
  -H "Content-Type: application/json" \
  -d '{"creation_id": "17920001001"}'
```

## Common Patterns

### Monitor Engagement and Reply to Comments

```python
import json
import os
import urllib.request

BASE = os.environ["INSTAGRAM_API_URL"]
USER_ID = "17841400123456789"

def api_get(path, params=None):
    url = f"{BASE}{path}"
    if params:
        url += "?" + "&".join(f"{k}={v}" for k, v in params.items())
    with urllib.request.urlopen(url) as r:
        return json.loads(r.read())

def api_post(path, data):
    req = urllib.request.Request(
        f"{BASE}{path}",
        data=json.dumps(data).encode(),
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())

media_resp = api_get(f"/{USER_ID}/media", {"limit": "10"})
for post in media_resp["data"]:
    if post["comments_count"] > 0:
        comments = api_get(f"/media/{post['id']}/comments")
        for comment in comments["data"]:
            if comment["username"] != "brewedawakening_" and "?" in comment["text"]:
                print(f"Unanswered question on post {post['id']}: {comment['text'][:80]}")
```

### Identify Top-Performing Content

```python
media_resp = api_get(f"/{USER_ID}/media", {"limit": "100"})
posts_with_insights = []
for post in media_resp["data"]:
    insights = api_get(f"/media/{post['id']}/insights")
    reach = next(m for m in insights["data"] if m["name"] == "reach")["values"][0]["value"]
    saves = next(m for m in insights["data"] if m["name"] == "saved")["values"][0]["value"]
    posts_with_insights.append({"id": post["id"], "type": post["media_type"], "reach": reach, "saves": saves})

top_posts = sorted(posts_with_insights, key=lambda x: x["reach"], reverse=True)[:5]
for p in top_posts:
    print(f"Top post {p['id']} ({p['type']}): reach={p['reach']}, saves={p['saves']}")
```

### Publish New Content and Verify

```python
container = api_post(f"/{USER_ID}/media", {
    "image_url": "https://example.com/morning_brew.jpg",
    "caption": "Monday morning motivation \u2615\n\n#mondaycoffee #morningroutine",
    "media_type": "IMAGE"
})
container_id = container["id"]
print(f"Container created: {container_id}")

status = api_get(f"/container/{container_id}")
if status["status"] == "FINISHED":
    published = api_post(f"/{USER_ID}/media_publish", {"creation_id": container_id})
    print(f"Published! New media ID: {published['id']}")
    new_post = api_get(f"/media/{published['id']}")
    print(f"Verified: {new_post['caption'][:60]}...")
```
