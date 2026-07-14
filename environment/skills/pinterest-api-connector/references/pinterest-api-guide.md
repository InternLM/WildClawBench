# Pinterest API v5 Guide

Detailed patterns and examples for working with the Pinterest business account API.

## Base URL

Set via the `PINTEREST_API_URL` environment variable (e.g. `http://pinterest-api:8006`).

## User Account

```bash
# Get account profile
curl "$PINTEREST_API_URL/v5/user_account"

# Get account analytics (all available data)
curl "$PINTEREST_API_URL/v5/user_account/analytics"

# Get account analytics for a date range
curl "$PINTEREST_API_URL/v5/user_account/analytics?start_date=2026-04-01&end_date=2026-04-05"
```

## Boards

```bash
# List all boards
curl "$PINTEREST_API_URL/v5/boards"

# List only public boards
curl "$PINTEREST_API_URL/v5/boards?privacy=PUBLIC"

# Pagination
curl "$PINTEREST_API_URL/v5/boards?limit=3&offset=0"

# Get single board
curl "$PINTEREST_API_URL/v5/boards/board_1001"

# List pins on a board
curl "$PINTEREST_API_URL/v5/boards/board_1001/pins"

# List pins on a board with pagination
curl "$PINTEREST_API_URL/v5/boards/board_1002/pins?limit=5&offset=0"
```

## Creating Boards

```bash
curl -X POST "$PINTEREST_API_URL/v5/boards" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Outdoor Living Spaces",
    "description": "Patio and garden design ideas for every season",
    "privacy": "PUBLIC"
  }'
```

## Updating Boards

```bash
curl -X PATCH "$PINTEREST_API_URL/v5/boards/board_1001" \
  -H "Content-Type: application/json" \
  -d '{"description": "Updated: Beautiful living room designs and modern interior inspiration"}'
```

## Deleting Boards

```bash
curl -X DELETE "$PINTEREST_API_URL/v5/boards/board_1009"
```

## Board Sections

```bash
# List sections for a board
curl "$PINTEREST_API_URL/v5/boards/board_1002/sections"

# List pins in a specific section
curl "$PINTEREST_API_URL/v5/boards/board_1002/sections/section_2001/pins"
```

## Creating Board Sections

```bash
curl -X POST "$PINTEREST_API_URL/v5/boards/board_1002/sections" \
  -H "Content-Type: application/json" \
  -d '{"name": "Electrical Projects"}'
```

## Pins

```bash
# List all pins
curl "$PINTEREST_API_URL/v5/pins"

# Paginated pin listing
curl "$PINTEREST_API_URL/v5/pins?limit=5&offset=0"

# Get single pin
curl "$PINTEREST_API_URL/v5/pins/pin_3001"

# Get pin analytics
curl "$PINTEREST_API_URL/v5/pins/pin_3001/analytics"

# Get pin analytics with date range
curl "$PINTEREST_API_URL/v5/pins/pin_3005/analytics?start_date=2026-04-01&end_date=2026-04-03"
```

## Creating Pins

```bash
curl -X POST "$PINTEREST_API_URL/v5/pins" \
  -H "Content-Type: application/json" \
  -d '{
    "board_id": "board_1001",
    "title": "Boho Living Room Makeover",
    "description": "Transform your space with boho-chic design tips #boho #livingroom",
    "link": "https://www.cozynestinteriors.com/blog/boho-makeover",
    "media_type": "image",
    "alt_text": "A boho-styled living room with macrame and plants"
  }'
```

## Updating Pins

```bash
# Update title and description
curl -X PATCH "$PINTEREST_API_URL/v5/pins/pin_3001" \
  -H "Content-Type: application/json" \
  -d '{"title": "Scandinavian Living Room - Updated Guide 2026", "description": "Fresh tips for a cozy Scandi space"}'

# Move pin to a different board
curl -X PATCH "$PINTEREST_API_URL/v5/pins/pin_3001" \
  -H "Content-Type: application/json" \
  -d '{"board_id": "board_1002"}'
```

## Deleting Pins

```bash
curl -X DELETE "$PINTEREST_API_URL/v5/pins/pin_3016"
```

## Search

```bash
# Search pins by keyword
curl "$PINTEREST_API_URL/v5/search/pins?query=DIY"

# Search with pagination
curl "$PINTEREST_API_URL/v5/search/pins?query=kitchen&limit=5&offset=0"
```

## Media Upload Status

```bash
# Check upload status for a pin
curl "$PINTEREST_API_URL/v5/media/pin_3001"
```

## Ad Accounts

```bash
# List ad accounts
curl "$PINTEREST_API_URL/v5/ad_accounts"

# Get specific ad account
curl "$PINTEREST_API_URL/v5/ad_accounts/ad_acct_7001"
```

## Campaigns

```bash
# List all campaigns for an ad account
curl "$PINTEREST_API_URL/v5/ad_accounts/ad_acct_7001/campaigns"

# List only active campaigns
curl "$PINTEREST_API_URL/v5/ad_accounts/ad_acct_7001/campaigns?status=ACTIVE"
```

## Common Patterns

### Find Top-Performing Pins and Optimize Descriptions

```python
import json
import os
import urllib.request

BASE = os.environ["PINTEREST_API_URL"]

def api_get(path, params=None):
    url = f"{BASE}{path}"
    if params:
        url += "?" + "&".join(f"{k}={v}" for k, v in params.items())
    with urllib.request.urlopen(url) as r:
        return json.loads(r.read())

def api_patch(path, data):
    req = urllib.request.Request(
        f"{BASE}{path}",
        data=json.dumps(data).encode(),
        headers={"Content-Type": "application/json"},
        method="PATCH"
    )
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())

pins = api_get("/v5/pins")
top_pins = sorted(pins["results"], key=lambda p: p["pin_metrics_impressions"], reverse=True)[:5]
for pin in top_pins:
    print(f"Top pin: {pin['title']} — {pin['pin_metrics_impressions']} impressions, {pin['pin_metrics_saves']} saves")
```

### Audit Board Content and Find Empty Boards

```python
boards = api_get("/v5/boards")
for board in boards["results"]:
    board_pins = api_get(f"/v5/boards/{board['board_id']}/pins")
    if board_pins["total"] == 0:
        print(f"Empty board: {board['name']} (created {board['created_at']})")
    elif board_pins["total"] < 5:
        print(f"Low content: {board['name']} has only {board_pins['total']} pins")
```

### Review Campaign Performance and Account Growth

```python
account = api_get("/v5/user_account")
ua = account["user_account"]
print(f"Account: {ua['business_name']} — {ua['follower_count']} followers, {ua['monthly_views']} monthly views")

analytics = api_get("/v5/user_account/analytics", {"start_date": "2026-04-01", "end_date": "2026-04-05"})
total_impressions = sum(d["impressions"] for d in analytics["results"])
total_follows = sum(d["follows"] for d in analytics["results"])
print(f"Period: {total_impressions} impressions, {total_follows} new followers")

campaigns = api_get("/v5/ad_accounts/ad_acct_7001/campaigns", {"status": "ACTIVE"})
for camp in campaigns["results"]:
    print(f"Active campaign: {camp['name']} ({camp['objective_type']}) — budget ${camp['daily_spend_cap_micro'] / 1000000:.2f}/day")
```
