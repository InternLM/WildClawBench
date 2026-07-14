# Etsy Open API v3 Guide

Detailed patterns and examples for working with the Etsy seller API.

## Base URL

Set via the `ETSY_API_URL` environment variable (e.g. `http://etsy-api:8001`).

## Current User

```bash
curl "$ETSY_API_URL/v3/application/users/me"
```

## Shop Info

```bash
curl "$ETSY_API_URL/v3/application/shops/29457183"

# Update shop announcement
curl -X PUT "$ETSY_API_URL/v3/application/shops/29457183" \
  -H "Content-Type: application/json" \
  -d '{"announcement": "Summer sale — 20% off all mugs this week!"}'
```

## Shop Sections

```bash
# List all sections
curl "$ETSY_API_URL/v3/application/shops/29457183/sections"

# Get a specific section
curl "$ETSY_API_URL/v3/application/shops/29457183/sections/40001"
```

## Listings

```bash
# List active listings (default)
curl "$ETSY_API_URL/v3/application/shops/29457183/listings"

# List draft listings
curl "$ETSY_API_URL/v3/application/shops/29457183/listings?state=draft"

# Search listings
curl "$ETSY_API_URL/v3/application/shops/29457183/listings?q=mug"

# Filter by section, sort by price ascending
curl "$ETSY_API_URL/v3/application/shops/29457183/listings?section_id=40001&sort_on=price&sort_order=asc"

# Pagination
curl "$ETSY_API_URL/v3/application/shops/29457183/listings?limit=5&offset=10"

# Get single listing
curl "$ETSY_API_URL/v3/application/listings/1001"
```

## Creating Listings

```bash
curl -X POST "$ETSY_API_URL/v3/application/shops/29457183/listings" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Ceramic Candle Holder - Crescent Moon",
    "description": "Hand-thrown crescent moon candle holder in matte black glaze.",
    "price": 30.00,
    "quantity": 8,
    "who_made": "i_did",
    "when_made": "2020_2026",
    "taxonomy_id": 2078,
    "tags": ["candle holder", "ceramic", "moon", "handmade"],
    "materials": ["stoneware clay", "matte black glaze"],
    "shipping_profile_id": 50001,
    "return_policy_id": 60001,
    "processing_min": 7,
    "processing_max": 14
  }'
```

## Updating Listings

```bash
# Update price and quantity
curl -X PUT "$ETSY_API_URL/v3/application/listings/1001" \
  -H "Content-Type: application/json" \
  -d '{"price": 35.00, "quantity": 15}'

# Activate a draft listing
curl -X PUT "$ETSY_API_URL/v3/application/listings/1020" \
  -H "Content-Type: application/json" \
  -d '{"state": "active", "quantity": 5}'
```

## Deleting Listings

```bash
curl -X DELETE "$ETSY_API_URL/v3/application/listings/1017"
```

## Listing Images

```bash
# List images for a listing
curl "$ETSY_API_URL/v3/application/listings/1001/images"

# Get single image
curl "$ETSY_API_URL/v3/application/listings/1001/images/90001"

# Delete an image
curl -X DELETE "$ETSY_API_URL/v3/application/listings/1001/images/90003"
```

## Receipts (Orders)

```bash
# List all receipts
curl "$ETSY_API_URL/v3/application/shops/29457183/receipts"

# Filter by status
curl "$ETSY_API_URL/v3/application/shops/29457183/receipts?status=paid"

# Find unshipped orders
curl "$ETSY_API_URL/v3/application/shops/29457183/receipts?was_shipped=false"

# Date range filter
curl "$ETSY_API_URL/v3/application/shops/29457183/receipts?min_created=2025-04-01&max_created=2025-04-30"

# Get single receipt with transactions
curl "$ETSY_API_URL/v3/application/shops/29457183/receipts/2003"
```

## Marking Orders as Shipped

```bash
curl -X PUT "$ETSY_API_URL/v3/application/shops/29457183/receipts/2007" \
  -H "Content-Type: application/json" \
  -d '{
    "shipping_carrier": "USPS",
    "tracking_code": "9400111899223100456789",
    "was_shipped": true
  }'
```

## Transactions (Line Items)

```bash
# List transactions for a receipt
curl "$ETSY_API_URL/v3/application/shops/29457183/receipts/2003/transactions"

# Get single transaction
curl "$ETSY_API_URL/v3/application/shops/29457183/transactions/3001"
```

## Reviews

```bash
# All shop reviews
curl "$ETSY_API_URL/v3/application/shops/29457183/reviews"

# Filter by minimum rating
curl "$ETSY_API_URL/v3/application/shops/29457183/reviews?min_rating=5"

# Reviews for a specific listing
curl "$ETSY_API_URL/v3/application/listings/1001/reviews"
```

## Shipping Profiles

```bash
# List all profiles
curl "$ETSY_API_URL/v3/application/shops/29457183/shipping-profiles"

# Get single profile
curl "$ETSY_API_URL/v3/application/shops/29457183/shipping-profiles/50001"
```

## Return Policies

```bash
# List policies
curl "$ETSY_API_URL/v3/application/shops/29457183/return-policies"

# Get single policy
curl "$ETSY_API_URL/v3/application/shops/29457183/return-policies/60001"
```

## Common Patterns

### Find and Ship Unshipped Paid Orders

```python
import json
import os
import urllib.request

BASE = os.environ["ETSY_API_URL"]
SHOP_ID = "29457183"

def api_get(path, params=None):
    url = f"{BASE}{path}"
    if params:
        url += "?" + "&".join(f"{k}={v}" for k, v in params.items())
    with urllib.request.urlopen(url) as r:
        return json.loads(r.read())

def api_put(path, data):
    req = urllib.request.Request(
        f"{BASE}{path}",
        data=json.dumps(data).encode(),
        headers={"Content-Type": "application/json"},
        method="PUT"
    )
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())

# Find paid but unshipped receipts
receipts = api_get(f"/v3/application/shops/{SHOP_ID}/receipts", {"status": "paid", "was_shipped": "false"})
for receipt in receipts.get("results", []):
    receipt_id = receipt["receipt_id"]
    print(f"Order {receipt_id} for {receipt['name']} needs shipping")
```

### Check for Low-Rating Reviews

```python
reviews = api_get(f"/v3/application/shops/{SHOP_ID}/reviews")
for review in reviews.get("results", []):
    if review["rating"] <= 3:
        print(f"⚠ Low review ({review['rating']}★) on listing {review['listing_id']}: {review['review'][:80]}...")
```

### Audit Listing Inventory

```python
listings = api_get(f"/v3/application/shops/{SHOP_ID}/listings")
for listing in listings.get("results", []):
    if listing["quantity"] <= 2:
        print(f"Low stock: {listing['title']} — only {listing['quantity']} remaining (${listing['price']})")
```
