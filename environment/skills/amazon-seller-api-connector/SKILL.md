---
name: amazon-seller-api-connector
description: >
  Amazon Selling Partner API HTTP endpoints for product catalog, listings,
  order management, inventory, pricing, returns, and reporting.
---

# Amazon Selling Partner API

## Base URL

| Variable | Purpose |
|----------|---------|
| `AMAZON_SELLER_API_URL` | Base URL for all requests |

All paths below are relative to `AMAZON_SELLER_API_URL`.

---

## Health

```
GET /health
```

Returns `{"status": "ok"}`.

---

## Seller Account

### Get account info

Returns the authenticated seller's account profile, including seller ID, marketplace participations, business name, and registration details.

```
GET /sellers/v1/account
```

### Get account health

Returns the seller's account health metrics, including order defect rate, late shipment rate, pre-fulfillment cancel rate, and policy compliance status. Each metric includes its current value and the performance target threshold.

```
GET /sellers/v1/account/health
```

### List notifications

Returns a list of seller notifications such as listing policy violations, account health alerts, and fulfillment issues. Notifications include severity level, type, message, creation date, and related entity references.

```
GET /notifications/v1/notifications
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `severity` | string | query | no | Filter by severity: `WARNING`, `CRITICAL`, `INFO` |

---

## Catalog Items

### Search catalog items

Searches the Amazon product catalog by keywords or identifiers. Returns matching items with summary information including ASIN, title, brand, images, and product attributes based on the requested data inclusions.

```
GET /catalog/2022-04-01/items
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `keywords` | string | query | no | Search terms matching title and description |
| `identifiers` | string | query | no | Comma-separated ASINs or SKUs to look up |
| `identifiersType` | string | query | no | Type of identifiers provided: `ASIN` or `SKU` |
| `pageSize` | integer | query | no | Maximum results, 1-20. Default: 10 |
| `marketplaceIds` | string | query | no | Marketplace ID. Default: `ATVPDKIKX0DER` |
| `includedData` | string | query | no | Comma-separated data sets to include: `summaries`, `images`, `attributes` |

### Get catalog item

Returns the full details of a single catalog item identified by its ASIN. Includes product title, brand, manufacturer, category, images, and all available attributes.

```
GET /catalog/2022-04-01/items/{asin}
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `asin` | string | path | yes | Amazon Standard Identification Number |

---

## Listings

### Get listing

Returns the details of a specific listing owned by the seller, identified by seller ID and SKU. Includes product type, title, description, price, quantity, fulfillment channel, condition, bullet points, and current status.

```
GET /listings/2021-08-01/items/{sellerId}/{sku}
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `sellerId` | string | path | yes | Seller identifier |
| `sku` | string | path | yes | Seller-defined SKU |

### Create or update listing

Creates a new listing or performs a full replacement of an existing listing's data. All product attributes must be provided — omitted fields are cleared. Returns the resulting listing object.

```
PUT /listings/2021-08-01/items/{sellerId}/{sku}
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `sellerId` | string | path | yes | Seller identifier |
| `sku` | string | path | yes | Seller-defined SKU |

**Request body**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `productType` | string | yes | Amazon product type classification |
| `title` | string | no | Product title |
| `description` | string | no | Product description |
| `brand` | string | no | Brand name |
| `bulletPoints` | array of strings | no | Feature bullet points |
| `price` | number | no | Listing price |
| `quantity` | integer | no | Available quantity |
| `fulfillmentChannel` | string | no | `AFN` (Fulfillment by Amazon) or `MFN` (Merchant Fulfilled) |
| `condition` | string | no | Item condition: `NEW`, `USED_LIKE_NEW`, `USED_VERY_GOOD`, `USED_GOOD`, `USED_ACCEPTABLE` |
| `category` | string | no | Product category |

### Partial update listing

Applies a partial update to an existing listing. Only the specified fields are modified; all other fields remain unchanged. Returns the updated listing.

```
PATCH /listings/2021-08-01/items/{sellerId}/{sku}
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `sellerId` | string | path | yes | Seller identifier |
| `sku` | string | path | yes | Seller-defined SKU |

**Request body**

Any subset of the fields from the PUT request body. Only provided fields are updated.

### Delete listing

Deletes an existing listing. The product is removed from the seller's active inventory. This action cannot be undone.

```
DELETE /listings/2021-08-01/items/{sellerId}/{sku}
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `sellerId` | string | path | yes | Seller identifier |
| `sku` | string | path | yes | Seller-defined SKU |

---

## Orders

### List orders

Returns a paginated list of orders matching the specified filters. Each order includes order ID, status, fulfillment channel, purchase date, amounts, shipping address, and buyer info.

```
GET /orders/v0/orders
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `CreatedAfter` | string | query | no | Filter orders created after this date (ISO 8601) |
| `CreatedBefore` | string | query | no | Filter orders created before this date (ISO 8601) |
| `OrderStatuses` | string | query | no | Comma-separated status filter: `Pending`, `Unshipped`, `Shipped`, `Canceled` |
| `FulfillmentChannels` | string | query | no | `AFN` (FBA) or `MFN` (Merchant Fulfilled) |
| `MarketplaceIds` | string | query | no | Marketplace ID filter |
| `MaxResultsPerPage` | integer | query | no | Maximum results, 1-100. Default: 100 |

### Get order

Returns the full details of a single order identified by its Amazon order ID. Includes order status, dates, amounts, shipping address, fulfillment channel, and buyer information.

```
GET /orders/v0/orders/{orderId}
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `orderId` | string | path | yes | Amazon order ID |

### List order items

Returns the line items for a specific order. Each item includes the ASIN, seller SKU, title, quantity ordered, quantity shipped, item price, and shipping details.

```
GET /orders/v0/orders/{orderId}/orderItems
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `orderId` | string | path | yes | Amazon order ID |

### Confirm shipment

Records a shipment confirmation for an order. Updates the order status to shipped and stores the carrier and tracking information. Returns the updated order.

```
POST /orders/v0/orders/{orderId}/shipmentConfirmation
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `orderId` | string | path | yes | Amazon order ID |

**Request body**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `packageReferenceId` | string | no | Seller-defined package reference |
| `carrierCode` | string | yes | Shipping carrier code (e.g. `UPS`, `USPS`, `FedEx`) |
| `trackingNumber` | string | yes | Carrier tracking number |
| `shipDate` | string | yes | Ship date (ISO 8601) |

---

## Inventory

### Get inventory summaries

Returns inventory summary data for the seller's products. Each summary includes the seller SKU, ASIN, fulfillable quantity, inbound quantities, reserved quantities, and total supply quantity.

```
GET /fba/inventory/v1/summaries
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `sellerSkus` | string | query | no | Comma-separated SKUs to filter |
| `granularityType` | string | query | no | Granularity level: `Marketplace`. Default: `Marketplace` |
| `granularityId` | string | query | no | Marketplace ID for granularity |
| `marketplaceIds` | string | query | no | Marketplace ID filter |

### Update inventory quantity

Updates the available quantity for a specific seller SKU. Returns the updated inventory summary.

```
PUT /fba/inventory/v1/items/{sellerSku}
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `sellerSku` | string | path | yes | Seller-defined SKU |

**Request body**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `sellerSku` | string | yes | Seller-defined SKU (must match path) |
| `quantity` | integer | yes | New available quantity |

---

## Reports

### List reports

Returns a list of reports that have been requested. Results can be filtered by report type and processing status. Each report includes its ID, type, processing status, creation date, and availability.

```
GET /reports/2021-06-30/reports
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `reportTypes` | string | query | no | Comma-separated report type codes to filter |
| `processingStatuses` | string | query | no | Filter by status: `DONE`, `IN_PROGRESS`, `IN_QUEUE` |

### Get report

Returns the details and status of a specific report, including its processing status, data hash, and download URL when complete.

```
GET /reports/2021-06-30/reports/{reportId}
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `reportId` | string | path | yes | Report identifier |

### Create report

Requests the generation of a new report. The report is processed asynchronously and can be polled for completion. Returns the report ID for status tracking.

```
POST /reports/2021-06-30/reports
```

**Request body**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `reportType` | string | yes | Report type code (e.g. `GET_FLAT_FILE_OPEN_LISTINGS_DATA`) |
| `dataStartTime` | string | no | Report data start time (ISO 8601) |
| `dataEndTime` | string | no | Report data end time (ISO 8601) |
| `marketplaceIds` | array of strings | no | Marketplace IDs to include in the report |

---

## Product Pricing

### Get competitive price

Returns the competitive pricing data for a product, including the landed price, listing price, shipping cost, and the number of competing offers. Can be queried by ASIN or SKU.

```
GET /products/pricing/v0/competitivePrice
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `Asin` | string | query | no | Product ASIN (use with `ItemType=Asin`) |
| `Sku` | string | query | no | Seller SKU (use with `ItemType=Sku`) |
| `MarketplaceId` | string | query | no | Marketplace ID |
| `ItemType` | string | query | no | Identifier type: `Asin` or `Sku` |

### Get item offers

Returns the list of active offers for a product from all sellers. Each offer includes the seller ID, condition, price, shipping, fulfillment channel, and whether it holds the Buy Box.

```
GET /products/pricing/v0/items/{Asin}/offers
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `Asin` | string | path | yes | Product ASIN |
| `MarketplaceId` | string | query | no | Marketplace ID |
| `ItemCondition` | string | query | no | Item condition filter: `New`, `Used`, `Collectible`, `Refurbished` |

---

## Returns

### List returns

Returns a list of return requests matching the specified filters. Each return includes the return ID, order ID, status, reason, customer comments, and associated item details.

```
GET /returns/v0/returns
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `status` | string | query | no | Filter by status: `Authorized`, `Completed`, `Closed` |
| `orderId` | string | query | no | Filter by Amazon order ID |

### Get return

Returns the full details of a single return request, including the return reason, customer comments, status, item details, and all timestamps.

```
GET /returns/v0/returns/{returnId}
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `returnId` | string | path | yes | Return identifier |

### Authorize return

Approves a return request, authorizing the customer to ship the item back. The return status transitions to `Authorized`.

```
POST /returns/v0/returns/{returnId}/authorize
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `returnId` | string | path | yes | Return identifier |

### Close return

Closes a return request. A closed return can no longer be modified. The return status transitions to `Closed`.

```
POST /returns/v0/returns/{returnId}/close
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `returnId` | string | path | yes | Return identifier |

---

## Errors

Error responses follow this format:

```json
{
  "errors": [
    {
      "code": "NOT_FOUND",
      "message": "The resource was not found",
      "details": "Order 123-456-789 does not exist"
    }
  ]
}
```

Common HTTP status codes:

| Code | Meaning |
|------|---------|
| 400 | Bad request (invalid parameters or malformed body) |
| 404 | Resource not found |
| 409 | Conflict (concurrent modification) |
