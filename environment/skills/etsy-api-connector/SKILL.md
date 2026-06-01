---
name: etsy-api-connector
description: Etsy Open API v3 REST interface for seller shop management, listings, orders, reviews, and policies.
---

# Etsy Open API v3

## Connection

| Variable | Purpose |
|----------|---------|
| `ETSY_API_URL` | Base URL for all requests |

---

## User

### `GET /v3/application/users/me`

Returns the currently authenticated user, including their associated shop identifier.

**Response fields:**

| Field | Type | Description |
|-------|------|-------------|
| `user_id` | integer | Unique user identifier |
| `login_name` | string | Account login name |
| `primary_email` | string or null | Primary email address |
| `create_timestamp` | string | ISO 8601 account creation date |
| `shop_id` | integer | The user's shop identifier, used as a path parameter in all shop-scoped endpoints |

---

## Health

### `GET /health`

Returns service availability status. Response contains a `status` field.

---

## Shop

### `GET /v3/application/shops/{shop_id}`

Retrieves the full profile for a shop, including name, title, announcement, vacation status, policy text, review statistics, and favorers count.

| Parameter | Type | In | Required | Description |
|-----------|------|----|----------|-------------|
| `shop_id` | integer | path | yes | Shop identifier |

### `PUT /v3/application/shops/{shop_id}`

Updates mutable shop profile fields. Only provided fields are modified; omitted fields remain unchanged.

| Parameter | Type | In | Required | Description |
|-----------|------|----|----------|-------------|
| `shop_id` | integer | path | yes | Shop identifier |

**Request body fields (all optional):**

| Field | Type | Description |
|-------|------|-------------|
| `title` | string | Shop headline/title |
| `announcement` | string | Shop announcement displayed to visitors |
| `sale_message` | string | Message sent to buyers after purchase |
| `is_vacation` | boolean | Whether vacation mode is enabled |
| `vacation_message` | string | Message displayed when vacation mode is active |
| `accepts_custom_requests` | boolean | Whether the shop accepts custom order requests |
| `policy_welcome` | string | Welcome section of shop policies |
| `policy_payment` | string | Payment policy text |
| `policy_shipping` | string | Shipping policy text |
| `policy_refunds` | string | Refund/return policy text |

---

## Shop Sections

### `GET /v3/application/shops/{shop_id}/sections`

Returns all sections defined for a shop. Sections organize listings into named categories within the storefront.

| Parameter | Type | In | Required | Description |
|-----------|------|----|----------|-------------|
| `shop_id` | integer | path | yes | Shop identifier |

### `GET /v3/application/shops/{shop_id}/sections/{section_id}`

Retrieves a single shop section by its identifier. Returns section title, rank, and active listing count.

| Parameter | Type | In | Required | Description |
|-----------|------|----|----------|-------------|
| `shop_id` | integer | path | yes | Shop identifier |
| `section_id` | integer | path | yes | Section identifier |

---

## Listings

### `GET /v3/application/shops/{shop_id}/listings`

Returns a paginated list of listings belonging to a shop. Supports filtering by state, section, and text search, with configurable sort order.

| Parameter | Type | In | Required | Description |
|-----------|------|----|----------|-------------|
| `shop_id` | integer | path | yes | Shop identifier |
| `state` | string | query | no | Filter by listing state: `active`, `draft`, `sold_out`, `expired`. Default: `active` |
| `sort_on` | string | query | no | Sort field: `created`, `price`, `updated`, `score`. Default: `created` |
| `sort_order` | string | query | no | Sort direction: `asc` or `desc`. Default: `desc` |
| `limit` | integer | query | no | Maximum results per page (1–100). Default: 25 |
| `offset` | integer | query | no | Number of results to skip. Default: 0 |
| `section_id` | integer | query | no | Filter by shop section identifier |
| `q` | string | query | no | Full-text search across listing title and description |

### `GET /v3/application/listings/{listing_id}`

Retrieves a single listing by its identifier. Returns full listing details including title, description, price, quantity, tags, materials, dimensions, weight, views, favorers, and state.

| Parameter | Type | In | Required | Description |
|-----------|------|----|----------|-------------|
| `listing_id` | integer | path | yes | Listing identifier |

### `POST /v3/application/shops/{shop_id}/listings`

Creates a new listing in the specified shop. Returns the created listing with a server-assigned `listing_id`. Returns `201` on success.

| Parameter | Type | In | Required | Description |
|-----------|------|----|----------|-------------|
| `shop_id` | integer | path | yes | Shop identifier |

**Request body fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `title` | string | yes | Listing title |
| `description` | string | yes | Listing description |
| `price` | number | yes | Item price in shop currency |
| `quantity` | integer | yes | Available quantity |
| `who_made` | string | yes | Maker: `i_did`, `someone_else`, `collective` |
| `when_made` | string | yes | Production period, e.g. `2020_2026`, `made_to_order` |
| `taxonomy_id` | integer | yes | Etsy taxonomy category identifier |
| `tags` | string[] | no | List of search tags |
| `materials` | string[] | no | List of materials used |
| `shop_section_id` | integer | no | Section to place the listing in |
| `shipping_profile_id` | integer | no | Shipping profile identifier |
| `return_policy_id` | integer | no | Return policy identifier |
| `processing_min` | integer | no | Minimum processing days |
| `processing_max` | integer | no | Maximum processing days |
| `item_weight` | number | no | Item weight |
| `item_weight_unit` | string | no | Weight unit: `lb`, `oz`, `kg`, `g` |
| `item_length` | number | no | Item length |
| `item_width` | number | no | Item width |
| `item_height` | number | no | Item height |
| `item_dimensions_unit` | string | no | Dimension unit: `in`, `cm`, `mm` |
| `is_supply` | boolean | no | Whether item is a craft supply. Default: false |
| `is_customizable` | boolean | no | Whether seller accepts customization requests. Default: false |
| `is_personalizable` | boolean | no | Whether listing offers personalization. Default: false |

### `PUT /v3/application/listings/{listing_id}`

Updates an existing listing. Only provided fields are modified. Can be used to change state (e.g. `draft` → `active`), update pricing, adjust quantity, or edit any mutable listing field.

| Parameter | Type | In | Required | Description |
|-----------|------|----|----------|-------------|
| `listing_id` | integer | path | yes | Listing identifier |

**Request body:** Same fields as POST, all optional.

### `DELETE /v3/application/listings/{listing_id}`

Permanently removes a listing. Returns the deleted listing object on success.

| Parameter | Type | In | Required | Description |
|-----------|------|----|----------|-------------|
| `listing_id` | integer | path | yes | Listing identifier |

---

## Listing Images

### `GET /v3/application/listings/{listing_id}/images`

Returns all images associated with a listing, ordered by rank. Each image includes multiple resolution URLs (`url_75x75`, `url_170x135`, `url_570xN`, `url_fullxfull`) and alt text.

| Parameter | Type | In | Required | Description |
|-----------|------|----|----------|-------------|
| `listing_id` | integer | path | yes | Listing identifier |

### `GET /v3/application/listings/{listing_id}/images/{image_id}`

Retrieves a single listing image by its identifier.

| Parameter | Type | In | Required | Description |
|-----------|------|----|----------|-------------|
| `listing_id` | integer | path | yes | Listing identifier |
| `image_id` | integer | path | yes | Image identifier |

### `DELETE /v3/application/listings/{listing_id}/images/{image_id}`

Removes an image from a listing. Returns the deleted image object on success.

| Parameter | Type | In | Required | Description |
|-----------|------|----|----------|-------------|
| `listing_id` | integer | path | yes | Listing identifier |
| `image_id` | integer | path | yes | Image identifier |

---

## Receipts (Orders)

### `GET /v3/application/shops/{shop_id}/receipts`

Returns a paginated list of order receipts for a shop. Supports filtering by payment status, shipment status, date range, and sort order. Each receipt contains buyer info, shipping address, line items summary, payment totals, and fulfillment status.

| Parameter | Type | In | Required | Description |
|-----------|------|----|----------|-------------|
| `shop_id` | integer | path | yes | Shop identifier |
| `status` | string | query | no | Filter by receipt status: `paid`, `completed`, `shipped`, `open`, `cancelled`, `return_requested` |
| `min_created` | string | query | no | Filter receipts created on or after this date (ISO 8601) |
| `max_created` | string | query | no | Filter receipts created on or before this date (ISO 8601) |
| `was_shipped` | boolean | query | no | Filter by shipment status |
| `was_paid` | boolean | query | no | Filter by payment status |
| `sort_on` | string | query | no | Sort field: `created` or `updated`. Default: `created` |
| `sort_order` | string | query | no | Sort direction: `asc` or `desc`. Default: `desc` |
| `limit` | integer | query | no | Maximum results per page (1–100). Default: 25 |
| `offset` | integer | query | no | Number of results to skip. Default: 0 |

### `GET /v3/application/shops/{shop_id}/receipts/{receipt_id}`

Retrieves a single receipt by its identifier. Returns full order details including buyer information, shipping address, payment breakdown, gift message, and fulfillment timestamps.

| Parameter | Type | In | Required | Description |
|-----------|------|----|----------|-------------|
| `shop_id` | integer | path | yes | Shop identifier |
| `receipt_id` | integer | path | yes | Receipt identifier |

### `PUT /v3/application/shops/{shop_id}/receipts/{receipt_id}`

Updates fulfillment information on a receipt. Used to record shipping carrier, tracking code, and mark an order as shipped.

| Parameter | Type | In | Required | Description |
|-----------|------|----|----------|-------------|
| `shop_id` | integer | path | yes | Shop identifier |
| `receipt_id` | integer | path | yes | Receipt identifier |

**Request body fields (all optional):**

| Field | Type | Description |
|-------|------|-------------|
| `shipping_carrier` | string | Carrier name (e.g. `USPS`, `UPS`, `FedEx`) |
| `tracking_code` | string | Shipment tracking number |
| `was_shipped` | boolean | Set to `true` to mark the order as shipped |

---

## Transactions (Line Items)

### `GET /v3/application/shops/{shop_id}/receipts/{receipt_id}/transactions`

Returns all transaction line items for a specific receipt. Each transaction represents a single purchased listing with its quantity, price, shipping cost, and any selected variations.

| Parameter | Type | In | Required | Description |
|-----------|------|----|----------|-------------|
| `shop_id` | integer | path | yes | Shop identifier |
| `receipt_id` | integer | path | yes | Receipt identifier |

### `GET /v3/application/shops/{shop_id}/transactions/{transaction_id}`

Retrieves a single transaction by its identifier. Returns the listing title, quantity, price, shipping cost, digital status, and variation details.

| Parameter | Type | In | Required | Description |
|-----------|------|----|----------|-------------|
| `shop_id` | integer | path | yes | Shop identifier |
| `transaction_id` | integer | path | yes | Transaction identifier |

---

## Reviews

### `GET /v3/application/shops/{shop_id}/reviews`

Returns a paginated list of reviews for a shop. Can be filtered by listing and minimum rating. Each review includes the rating (1–5), review text, reviewer identifier, optional image URL, and timestamps.

| Parameter | Type | In | Required | Description |
|-----------|------|----|----------|-------------|
| `shop_id` | integer | path | yes | Shop identifier |
| `listing_id` | integer | query | no | Filter reviews for a specific listing |
| `min_rating` | integer | query | no | Minimum star rating (1–5) |
| `limit` | integer | query | no | Maximum results per page (1–100). Default: 25 |
| `offset` | integer | query | no | Number of results to skip. Default: 0 |

### `GET /v3/application/listings/{listing_id}/reviews`

Returns reviews for a specific listing. Same response format as shop-level reviews but scoped to a single listing.

| Parameter | Type | In | Required | Description |
|-----------|------|----|----------|-------------|
| `listing_id` | integer | path | yes | Listing identifier |
| `min_rating` | integer | query | no | Minimum star rating (1–5) |
| `limit` | integer | query | no | Maximum results per page (1–100). Default: 25 |
| `offset` | integer | query | no | Number of results to skip. Default: 0 |

---

## Shipping Profiles

### `GET /v3/application/shops/{shop_id}/shipping-profiles`

Returns all shipping profiles defined for a shop. Each profile specifies origin country, processing times, delivery estimates, and shipping costs.

| Parameter | Type | In | Required | Description |
|-----------|------|----|----------|-------------|
| `shop_id` | integer | path | yes | Shop identifier |

### `GET /v3/application/shops/{shop_id}/shipping-profiles/{profile_id}`

Retrieves a single shipping profile by its identifier.

| Parameter | Type | In | Required | Description |
|-----------|------|----|----------|-------------|
| `shop_id` | integer | path | yes | Shop identifier |
| `profile_id` | integer | path | yes | Shipping profile identifier |

---

## Return Policies

### `GET /v3/application/shops/{shop_id}/return-policies`

Returns all return policies defined for a shop. Each policy specifies whether returns and exchanges are accepted and the return deadline.

| Parameter | Type | In | Required | Description |
|-----------|------|----|----------|-------------|
| `shop_id` | integer | path | yes | Shop identifier |

### `GET /v3/application/shops/{shop_id}/return-policies/{policy_id}`

Retrieves a single return policy by its identifier.

| Parameter | Type | In | Required | Description |
|-----------|------|----|----------|-------------|
| `shop_id` | integer | path | yes | Shop identifier |
| `policy_id` | integer | path | yes | Return policy identifier |
