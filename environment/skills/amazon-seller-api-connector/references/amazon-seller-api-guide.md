# Amazon Selling Partner API Guide

Detailed patterns and examples for working with the Amazon seller API.

## Base URL

Set via the `AMAZON_SELLER_API_URL` environment variable (e.g. `http://amazon-seller-api:8000`).

## Seller Account

```bash
# Get seller account profile
curl "$AMAZON_SELLER_API_URL/sellers/v1/account"

# Get account health metrics
curl "$AMAZON_SELLER_API_URL/sellers/v1/account/health"

# List all performance notifications
curl "$AMAZON_SELLER_API_URL/notifications/v1/notifications"

# Filter notifications by severity
curl "$AMAZON_SELLER_API_URL/notifications/v1/notifications?severity=CRITICAL"
```

## Catalog Items

```bash
# List all catalog items
curl "$AMAZON_SELLER_API_URL/catalog/2022-04-01/items?pageSize=20&marketplaceIds=ATVPDKIKX0DER"

# Search by keyword
curl "$AMAZON_SELLER_API_URL/catalog/2022-04-01/items?keywords=earbuds&pageSize=10"

# Search by ASIN identifiers
curl "$AMAZON_SELLER_API_URL/catalog/2022-04-01/items?identifiers=B0EXAMPLE01,B0EXAMPLE06&identifiersType=ASIN"

# Get single catalog item
curl "$AMAZON_SELLER_API_URL/catalog/2022-04-01/items/B0EXAMPLE06"
```

## Listings Items

```bash
# Get listing details
curl "$AMAZON_SELLER_API_URL/listings/2021-08-01/items/A3EXAMPLE1SELLER/VE-CASE-IP15"

# Delete a listing
curl -X DELETE "$AMAZON_SELLER_API_URL/listings/2021-08-01/items/A3EXAMPLE1SELLER/VE-CASE-IP15?marketplaceIds=ATVPDKIKX0DER"
```

## Creating Listings

```bash
curl -X PUT "$AMAZON_SELLER_API_URL/listings/2021-08-01/items/A3EXAMPLE1SELLER/VE-NEW-CABLE" \
  -H "Content-Type: application/json" \
  -d '{
    "productType": "USB_CABLE",
    "title": "VoltEdge Ultra 10ft USB-C Cable - 240W PD",
    "description": "Premium 10ft USB-C cable with 240W Power Delivery support.",
    "brand": "VoltEdge Tech",
    "bulletPoints": ["240W Power Delivery", "10ft braided cable", "USB 4.0 compatible"],
    "price": 24.99,
    "quantity": 100,
    "fulfillmentChannel": "MFN",
    "condition": "NEW",
    "category": "Electronics"
  }'
```

## Updating Listings

```bash
# Update price and quantity (PATCH)
curl -X PATCH "$AMAZON_SELLER_API_URL/listings/2021-08-01/items/A3EXAMPLE1SELLER/VE-EARBUD-PRO" \
  -H "Content-Type: application/json" \
  -d '{"price": 44.99, "quantity": 60}'

# Full update (PUT on existing listing)
curl -X PUT "$AMAZON_SELLER_API_URL/listings/2021-08-01/items/A3EXAMPLE1SELLER/VE-CASE-IP15" \
  -H "Content-Type: application/json" \
  -d '{"productType": "CELLULAR_PHONE_CASE", "price": 17.99, "quantity": 200}'
```

## Orders

```bash
# List all orders
curl "$AMAZON_SELLER_API_URL/orders/v0/orders?MarketplaceIds=ATVPDKIKX0DER"

# Filter by status
curl "$AMAZON_SELLER_API_URL/orders/v0/orders?OrderStatuses=Unshipped"

# Filter by fulfillment channel
curl "$AMAZON_SELLER_API_URL/orders/v0/orders?FulfillmentChannels=AFN"

# Date range filter
curl "$AMAZON_SELLER_API_URL/orders/v0/orders?CreatedAfter=2026-03-01T00:00:00Z&CreatedBefore=2026-04-01T00:00:00Z"

# Paginate
curl "$AMAZON_SELLER_API_URL/orders/v0/orders?MaxResultsPerPage=5"

# Get single order
curl "$AMAZON_SELLER_API_URL/orders/v0/orders/114-5578234-9921100"

# Get order line items
curl "$AMAZON_SELLER_API_URL/orders/v0/orders/114-5567890-3456700/orderItems"
```

## Confirming Shipment

```bash
curl -X POST "$AMAZON_SELLER_API_URL/orders/v0/orders/114-1678901-4567800/shipmentConfirmation" \
  -H "Content-Type: application/json" \
  -d '{
    "carrierCode": "UPS",
    "trackingNumber": "1Z999AA10123456784",
    "shipDate": "2026-04-29T10:00:00Z"
  }'
```

## Inventory

```bash
# List all inventory
curl "$AMAZON_SELLER_API_URL/fba/inventory/v1/summaries?granularityType=Marketplace&granularityId=ATVPDKIKX0DER"

# Filter by SKU
curl "$AMAZON_SELLER_API_URL/fba/inventory/v1/summaries?sellerSkus=VE-CASE-IP15,VE-EARBUD-PRO"

# Check out-of-stock item
curl "$AMAZON_SELLER_API_URL/fba/inventory/v1/summaries?sellerSkus=VE-USBHUB-7P"
```

## Updating Inventory

```bash
curl -X PUT "$AMAZON_SELLER_API_URL/fba/inventory/v1/items/VE-CHRG-USB3" \
  -H "Content-Type: application/json" \
  -d '{"sellerSku": "VE-CHRG-USB3", "quantity": 75}'
```

## Reports

```bash
# List all reports
curl "$AMAZON_SELLER_API_URL/reports/2021-06-30/reports"

# Filter by type
curl "$AMAZON_SELLER_API_URL/reports/2021-06-30/reports?reportTypes=GET_FBA_MYI_UNSUPPRESSED_INVENTORY_DATA"

# Filter by processing status
curl "$AMAZON_SELLER_API_URL/reports/2021-06-30/reports?processingStatuses=DONE"

# Get single report
curl "$AMAZON_SELLER_API_URL/reports/2021-06-30/reports/REP-001"
```

## Creating Reports

```bash
curl -X POST "$AMAZON_SELLER_API_URL/reports/2021-06-30/reports" \
  -H "Content-Type: application/json" \
  -d '{
    "reportType": "GET_FLAT_FILE_OPEN_LISTINGS_DATA",
    "dataStartTime": "2026-05-01T00:00:00Z",
    "dataEndTime": "2026-05-06T23:59:59Z",
    "marketplaceIds": ["ATVPDKIKX0DER"]
  }'
```

## Product Pricing

```bash
# Get competitive pricing by ASIN
curl "$AMAZON_SELLER_API_URL/products/pricing/v0/competitivePrice?Asin=B0EXAMPLE06&MarketplaceId=ATVPDKIKX0DER"

# Get competitive pricing by SKU
curl "$AMAZON_SELLER_API_URL/products/pricing/v0/competitivePrice?Sku=VE-CASE-IP15&MarketplaceId=ATVPDKIKX0DER"

# Get item offers
curl "$AMAZON_SELLER_API_URL/products/pricing/v0/items/B0EXAMPLE06/offers?MarketplaceId=ATVPDKIKX0DER&ItemCondition=New"
```

## Returns

```bash
# List all returns
curl "$AMAZON_SELLER_API_URL/returns/v0/returns"

# Filter by status
curl "$AMAZON_SELLER_API_URL/returns/v0/returns?status=Authorized"

# Filter by order ID
curl "$AMAZON_SELLER_API_URL/returns/v0/returns?orderId=114-3941689-8772200"

# Get single return
curl "$AMAZON_SELLER_API_URL/returns/v0/returns/RET-001"

# Authorize a return
curl -X POST "$AMAZON_SELLER_API_URL/returns/v0/returns/RET-003/authorize"

# Close a return
curl -X POST "$AMAZON_SELLER_API_URL/returns/v0/returns/RET-005/close"
```

## Common Patterns

### Find and Process Pending Orders

```python
import json
import os
import urllib.request

BASE = os.environ.get("AMAZON_SELLER_API_URL", "http://localhost:8000")

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

# Find unshipped orders
orders = api_get("/orders/v0/orders", {"OrderStatuses": "Unshipped"})
for order in orders["payload"]["Orders"]:
    order_id = order["AmazonOrderId"]
    items = api_get(f"/orders/v0/orders/{order_id}/orderItems")
    print(f"Order {order_id} for {order['BuyerInfo']['BuyerName']}:")
    for item in items["payload"]["OrderItems"]:
        print(f"  - {item['Title']} (qty: {item['QuantityOrdered']})")
```

### Check for Items Needing Attention

```python
# Check inventory levels
inventory = api_get("/fba/inventory/v1/summaries")
for item in inventory["payload"]["inventorySummaries"]:
    qty = item["inventoryDetails"]["fulfillableQuantity"]
    if qty <= 15:
        print(f"LOW STOCK: {item['sellerSku']} ({item['productName']}) — {qty} units remaining")
    if qty == 0:
        print(f"  OUT OF STOCK — consider restocking or deactivating listing")

# Check for critical notifications
notifications = api_get("/notifications/v1/notifications", {"severity": "CRITICAL"})
for notif in notifications["results"]:
    print(f"CRITICAL: {notif['title']} — {notif['message']}")
```

### Generate a Pricing Competitiveness Summary

```python
# Check Buy Box status across all products
catalog = api_get("/catalog/2022-04-01/items", {"pageSize": "20"})
winning = 0
losing = 0
for item in catalog["items"]:
    asin = item["asin"]
    pricing = api_get("/products/pricing/v0/competitivePrice", {"Asin": asin})
    payload = pricing["payload"]
    if isinstance(payload, dict):
        is_winner = payload["Product"]["CompetitivePricing"]["CompetitivePrices"][0]["belongsToRequester"]
        name = item["summaries"][0]["itemName"][:50]
        if is_winner:
            winning += 1
        else:
            losing += 1
            buy_box = payload["Product"]["Offers"][0]["BuyBoxPrices"][0]["LandedPrice"]["Amount"]
            our_price = payload["Product"]["CompetitivePricing"]["CompetitivePrices"][0]["Price"]["ListingPrice"]["Amount"]
            print(f"LOSING Buy Box: {name} (ours: ${our_price}, BB: ${buy_box})")

print(f"\nBuy Box Summary: {winning} winning, {losing} losing out of {winning + losing} products")
```
