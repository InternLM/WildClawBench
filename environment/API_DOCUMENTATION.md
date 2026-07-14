# Mock API Services Documentation

## Table of Contents

1. [Amazon Seller API](#1-amazon-seller-api)
2. [Etsy API](#2-etsy-api)
3. [Google Classroom API](#3-google-classroom-api)
4. [Instagram Graph API](#4-instagram-graph-api)
5. [Linear API](#5-linear-api)
6. [MyFitnessPal API](#6-myfitnesspal-api)
7. [Pinterest API](#7-pinterest-api)
8. [QuickBooks Online API](#8-quickbooks-online-api)
9. [Ring API](#9-ring-api)
10. [YouTube Data API](#10-youtube-data-api)
11. [Notion API](#11-notion-api)
12. [Zillow API](#12-zillow-api)
13. [Instacart API](#13-instacart-api)
14. [Slack API](#14-slack-api)
15. [Obsidian API](#15-obsidian-api)
16. [Whatsapp API](#16-whatsapp-api)
17. [Google Calendar API](#17-google-calendar-api)
18. [Gmail API](#18-gmail-api)
19. [Google Drive API](#19-google-drive-api)
20. [Github API](#20-github-api)
21. [Eventbrite API](#21-eventbrite-api)
22. [Stripe API](#22-stripe-api)
23. [Plaid API](#23-plaid-api)
24. [Coinbase API](#24-coinbase-api)
25. [Hubspot API](#25-hubspot-api)
26. [Zendesk API](#26-zendesk-api)
27. [Twilio API](#27-twilio-api)
28. [Sendgrid API](#28-sendgrid-api)
29. [Zoom API](#29-zoom-api)
30. [Jira API](#30-jira-api)
31. [Trello API](#31-trello-api)
32. [Asana API](#32-asana-api)
33. [Airtable API](#33-airtable-api)
34. [Google Maps API](#34-google-maps-api)
35. [Yelp API](#35-yelp-api)
36. [Openweather API](#36-openweather-api)
37. [Uber API](#37-uber-api)
38. [Doordash API](#38-doordash-api)
39. [Airbnb API](#39-airbnb-api)
40. [Spotify API](#40-spotify-api)
41. [Pagerduty API](#41-pagerduty-api)
42. [Square API](#42-square-api)
43. [Paypal API](#43-paypal-api)
44. [Alpaca API](#44-alpaca-api)
45. [Salesforce API](#45-salesforce-api)
46. [Confluence API](#46-confluence-api)
47. [Gitlab API](#47-gitlab-api)
48. [Sentry API](#48-sentry-api)
49. [Datadog API](#49-datadog-api)
50. [Okta API](#50-okta-api)
51. [Cloudflare API](#51-cloudflare-api)
52. [Kubernetes API](#52-kubernetes-api)
53. [Shippo API](#53-shippo-api)
54. [Docusign API](#54-docusign-api)
55. [Calendly API](#55-calendly-api)
56. [Typeform API](#56-typeform-api)
57. [Mixpanel API](#57-mixpanel-api)
58. [Discord API](#58-discord-api)
59. [Reddit API](#59-reddit-api)
60. [Tmdb API](#60-tmdb-api)
61. [Strava API](#61-strava-api)
62. [Twitter API](#62-twitter-api)
63. [Linkedin API](#63-linkedin-api)
64. [Telegram API](#64-telegram-api)
65. [Twitch API](#65-twitch-api)
66. [Wordpress API](#66-wordpress-api)
67. [Contentful API](#67-contentful-api)
68. [Algolia API](#68-algolia-api)
69. [Google Analytics API](#69-google-analytics-api)
70. [Intercom API](#70-intercom-api)
71. [Servicenow API](#71-servicenow-api)
72. [Bamboohr API](#72-bamboohr-api)
73. [Greenhouse API](#73-greenhouse-api)
74. [Gusto API](#74-gusto-api)
75. [Ticketmaster API](#75-ticketmaster-api)
76. [Amadeus API](#76-amadeus-api)
77. [Nasa API](#77-nasa-api)
78. [Openlibrary API](#78-openlibrary-api)
79. [Figma API](#79-figma-api)
80. [Monday API](#80-monday-api)
81. [Mailchimp API](#81-mailchimp-api)
82. [Dropbox API](#82-dropbox-api)
83. [Box API](#83-box-api)
84. [Bigcommerce API](#84-bigcommerce-api)
85. [Woocommerce API](#85-woocommerce-api)
86. [Microsoft Teams API](#86-microsoft-teams-api)
87. [Outlook API](#87-outlook-api)
88. [Xero API](#88-xero-api)
89. [Klaviyo API](#89-klaviyo-api)
90. [Segment API](#90-segment-api)
91. [Amplitude API](#91-amplitude-api)
92. [Posthog API](#92-posthog-api)
93. [Freshdesk API](#93-freshdesk-api)
94. [Mailgun API](#94-mailgun-api)
95. [Fedex API](#95-fedex-api)
96. [Ups API](#96-ups-api)
97. [Binance API](#97-binance-api)
98. [Kraken API](#98-kraken-api)
99. [Vimeo API](#99-vimeo-api)
100. [Webflow API](#100-webflow-api)
101. [Activecampaign API](#101-activecampaign-api)

---

## Service Overview

| Service | Port | Env Var | App Title | Version |
|---------|------|---------|-----------|---------|
| amazon-seller-api | 8000 | `AMAZON_SELLER_API_URL` | Amazon Seller API | v1.0.0 |
| etsy-api | 8001 | `ETSY_API_URL` | Etsy API | v1.0.0 |
| google-classroom-api | 8002 | `GOOGLE_CLASSROOM_API_URL` | Google Classroom API | v1.0.0 |
| instagram-api | 8003 | `INSTAGRAM_API_URL` | Instagram Graph API | v1.0.0 |
| linear-api | 8004 | `LINEAR_API_URL` | Linear API | v1.0.0 |
| myfitnesspal-api | 8005 | `MYFITNESSPAL_API_URL` | MyFitnessPal API | v1.0.0 |
| pinterest-api | 8006 | `PINTEREST_API_URL` | Pinterest API | v1.0.0 |
| quickbooks-api | 8007 | `QUICKBOOKS_API_URL` | QuickBooks Online API | v1.0.0 |
| ring-api | 8008 | `RING_API_URL` | Ring API | v1.0.0 |
| youtube-api | 8009 | `YOUTUBE_API_URL` | YouTube Data API | v1.0.0 |
| notion-api | 8010 | `NOTION_API_URL` | Notion API | v1.0.0 |
| zillow-api | 8011 | `ZILLOW_API_URL` | Zillow API | v1.0.0 |
| instacart-api | 8012 | `INSTACART_API_URL` | Instacart API | v1.0.0 |
| slack-api | 8013 | `SLACK_API_URL` | Slack API | v1.0.0 |
| obsidian-api | 8014 | `OBSIDIAN_API_URL` | Obsidian API | v1.0.0 |
| whatsapp-api | 8015 | `WHATSAPP_API_URL` | Whatsapp API | v1.0.0 |
| google-calendar-api | 8016 | `GOOGLE_CALENDAR_API_URL` | Google Calendar API | v1.0.0 |
| gmail-api | 8017 | `GMAIL_API_URL` | Gmail API | v1.0.0 |
| google-drive-api | 8018 | `GOOGLE_DRIVE_API_URL` | Google Drive API | v1.0.0 |
| github-api | 8019 | `GITHUB_API_URL` | Github API | v1.0.0 |
| eventbrite-api | 8020 | `EVENTBRITE_API_URL` | Eventbrite API | v1.0.0 |
| stripe-api | 8021 | `STRIPE_API_URL` | Stripe API | v1.0.0 |
| plaid-api | 8022 | `PLAID_API_URL` | Plaid API | v1.0.0 |
| coinbase-api | 8023 | `COINBASE_API_URL` | Coinbase API | v1.0.0 |
| hubspot-api | 8024 | `HUBSPOT_API_URL` | Hubspot API | v1.0.0 |
| zendesk-api | 8025 | `ZENDESK_API_URL` | Zendesk API | v1.0.0 |
| twilio-api | 8026 | `TWILIO_API_URL` | Twilio API | v1.0.0 |
| sendgrid-api | 8027 | `SENDGRID_API_URL` | Sendgrid API | v1.0.0 |
| zoom-api | 8028 | `ZOOM_API_URL` | Zoom API | v1.0.0 |
| jira-api | 8029 | `JIRA_API_URL` | Jira API | v1.0.0 |
| trello-api | 8030 | `TRELLO_API_URL` | Trello API | v1.0.0 |
| asana-api | 8031 | `ASANA_API_URL` | Asana API | v1.0.0 |
| airtable-api | 8032 | `AIRTABLE_API_URL` | Airtable API | v1.0.0 |
| google-maps-api | 8033 | `GOOGLE_MAPS_API_URL` | Google Maps API | v1.0.0 |
| yelp-api | 8034 | `YELP_API_URL` | Yelp API | v1.0.0 |
| openweather-api | 8035 | `OPENWEATHER_API_URL` | Openweather API | v1.0.0 |
| uber-api | 8036 | `UBER_API_URL` | Uber API | v1.0.0 |
| doordash-api | 8037 | `DOORDASH_API_URL` | Doordash API | v1.0.0 |
| airbnb-api | 8038 | `AIRBNB_API_URL` | Airbnb API | v1.0.0 |
| spotify-api | 8039 | `SPOTIFY_API_URL` | Spotify API | v1.0.0 |
| pagerduty-api | 8040 | `PAGERDUTY_API_URL` | Pagerduty API | v1.0.0 |
| square-api | 8041 | `SQUARE_API_URL` | Square API | v1.0.0 |
| paypal-api | 8042 | `PAYPAL_API_URL` | Paypal API | v1.0.0 |
| alpaca-api | 8043 | `ALPACA_API_URL` | Alpaca API | v1.0.0 |
| salesforce-api | 8044 | `SALESFORCE_API_URL` | Salesforce API | v1.0.0 |
| confluence-api | 8045 | `CONFLUENCE_API_URL` | Confluence API | v1.0.0 |
| gitlab-api | 8046 | `GITLAB_API_URL` | Gitlab API | v1.0.0 |
| sentry-api | 8047 | `SENTRY_API_URL` | Sentry API | v1.0.0 |
| datadog-api | 8048 | `DATADOG_API_URL` | Datadog API | v1.0.0 |
| okta-api | 8049 | `OKTA_API_URL` | Okta API | v1.0.0 |
| cloudflare-api | 8050 | `CLOUDFLARE_API_URL` | Cloudflare API | v1.0.0 |
| kubernetes-api | 8051 | `KUBERNETES_API_URL` | Kubernetes API | v1.0.0 |
| shippo-api | 8052 | `SHIPPO_API_URL` | Shippo API | v1.0.0 |
| docusign-api | 8053 | `DOCUSIGN_API_URL` | Docusign API | v1.0.0 |
| calendly-api | 8054 | `CALENDLY_API_URL` | Calendly API | v1.0.0 |
| typeform-api | 8055 | `TYPEFORM_API_URL` | Typeform API | v1.0.0 |
| mixpanel-api | 8056 | `MIXPANEL_API_URL` | Mixpanel API | v1.0.0 |
| discord-api | 8057 | `DISCORD_API_URL` | Discord API | v1.0.0 |
| reddit-api | 8058 | `REDDIT_API_URL` | Reddit API | v1.0.0 |
| tmdb-api | 8059 | `TMDB_API_URL` | Tmdb API | v1.0.0 |
| strava-api | 8060 | `STRAVA_API_URL` | Strava API | v1.0.0 |
| twitter-api | 8061 | `TWITTER_API_URL` | Twitter API | v1.0.0 |
| linkedin-api | 8062 | `LINKEDIN_API_URL` | Linkedin API | v1.0.0 |
| telegram-api | 8063 | `TELEGRAM_API_URL` | Telegram API | v1.0.0 |
| twitch-api | 8064 | `TWITCH_API_URL` | Twitch API | v1.0.0 |
| wordpress-api | 8065 | `WORDPRESS_API_URL` | Wordpress API | v1.0.0 |
| contentful-api | 8066 | `CONTENTFUL_API_URL` | Contentful API | v1.0.0 |
| algolia-api | 8067 | `ALGOLIA_API_URL` | Algolia API | v1.0.0 |
| google-analytics-api | 8068 | `GOOGLE_ANALYTICS_API_URL` | Google Analytics API | v1.0.0 |
| intercom-api | 8070 | `INTERCOM_API_URL` | Intercom API | v1.0.0 |
| servicenow-api | 8071 | `SERVICENOW_API_URL` | Servicenow API | v1.0.0 |
| bamboohr-api | 8072 | `BAMBOOHR_API_URL` | Bamboohr API | v1.0.0 |
| greenhouse-api | 8073 | `GREENHOUSE_API_URL` | Greenhouse API | v1.0.0 |
| gusto-api | 8074 | `GUSTO_API_URL` | Gusto API | v1.0.0 |
| ticketmaster-api | 8075 | `TICKETMASTER_API_URL` | Ticketmaster API | v1.0.0 |
| amadeus-api | 8076 | `AMADEUS_API_URL` | Amadeus API | v1.0.0 |
| nasa-api | 8077 | `NASA_API_URL` | Nasa API | v1.0.0 |
| openlibrary-api | 8078 | `OPENLIBRARY_API_URL` | Openlibrary API | v1.0.0 |
| figma-api | 8079 | `FIGMA_API_URL` | Figma API | v1.0.0 |
| monday-api | 8080 | `MONDAY_API_URL` | Monday API | v1.0.0 |
| mailchimp-api | 8081 | `MAILCHIMP_API_URL` | Mailchimp API | v1.0.0 |
| dropbox-api | 8082 | `DROPBOX_API_URL` | Dropbox API | v1.0.0 |
| box-api | 8083 | `BOX_API_URL` | Box API | v1.0.0 |
| bigcommerce-api | 8084 | `BIGCOMMERCE_API_URL` | Bigcommerce API | v1.0.0 |
| woocommerce-api | 8085 | `WOOCOMMERCE_API_URL` | Woocommerce API | v1.0.0 |
| microsoft-teams-api | 8086 | `MICROSOFT_TEAMS_API_URL` | Microsoft Teams API | v1.0.0 |
| outlook-api | 8087 | `OUTLOOK_API_URL` | Outlook API | v1.0.0 |
| xero-api | 8088 | `XERO_API_URL` | Xero API | v1.0.0 |
| klaviyo-api | 8089 | `KLAVIYO_API_URL` | Klaviyo API | v1.0.0 |
| segment-api | 8090 | `SEGMENT_API_URL` | Segment API | v1.0.0 |
| amplitude-api | 8091 | `AMPLITUDE_API_URL` | Amplitude API | v1.0.0 |
| posthog-api | 8092 | `POSTHOG_API_URL` | Posthog API | v1.0.0 |
| freshdesk-api | 8093 | `FRESHDESK_API_URL` | Freshdesk API | v1.0.0 |
| mailgun-api | 8094 | `MAILGUN_API_URL` | Mailgun API | v1.0.0 |
| fedex-api | 8095 | `FEDEX_API_URL` | Fedex API | v1.0.0 |
| ups-api | 8096 | `UPS_API_URL` | Ups API | v1.0.0 |
| binance-api | 8097 | `BINANCE_API_URL` | Binance API | v1.0.0 |
| kraken-api | 8098 | `KRAKEN_API_URL` | Kraken API | v1.0.0 |
| vimeo-api | 8099 | `VIMEO_API_URL` | Vimeo API | v1.0.0 |
| webflow-api | 8100 | `WEBFLOW_API_URL` | Webflow API | v1.0.0 |
| activecampaign-api | 8101 | `ACTIVECAMPAIGN_API_URL` | Activecampaign API | v1.0.0 |
---

## Shared Tracking/Audit Endpoints

All 10 services include tracking middleware that exposes these endpoints:

#### `GET /health`
Health check.

**Response:** `200`
```json
{"status": "ok"}
```

#### `GET /audit/requests`
Returns full audit log of all requests.

**Response:** `200`
```json
{"total": 42, "requests": [...]}
```

#### `GET /audit/requests/clear`
Clears the audit log.

**Response:** `200`
```json
{"cleared": 42}
```

#### `GET /audit/summary`
Aggregated request summary by endpoint.

**Response:** `200`
```json
{"total_requests": 42, "endpoints": {"GET /some/path": {"count": 10, "statuses": {"200": 8, "404": 2}}}}
```

Each value in `endpoints` is a dict with `count` (integer) and `statuses` (map of status code → count). Use `endpoint_data["count"]` to get the call count.

**Audit Log Entry Format:**
```json
{
  "timestamp": 1234567890.123,
  "timestamp_iso": "2026-05-07T10:30:00",
  "method": "GET",
  "path": "/some/path",
  "query_params": {"key": "value"},
  "request_body": "..." ,
  "status_code": 200,
  "response_body": "...",
  "duration_ms": 12.34
}
```

---

## 1. Amazon Seller API

**Port:** 8000 | **Env Var:** `AMAZON_SELLER_API_URL` | **Version:** v1.0.0

### Seller Account

#### `GET /sellers/v1/account`
Returns seller account information.

**Response:** `200`

#### `GET /sellers/v1/account/health`
Returns account health metrics.

**Response:** `200`

#### `GET /notifications/v1/notifications`
Lists seller notifications.

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| severity | str | — | — | Filter by severity level |

**Response:** `200`

---

### Catalog Items

#### `GET /catalog/2022-04-01/items`
Search the Amazon catalog.

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| keywords | str | — | — | Search keywords |
| identifiers | str | — | — | Product identifiers |
| identifiersType | str | — | — | Type of identifiers |
| pageSize | int | 10 | ge=1, le=20 | Results per page |
| marketplaceIds | str | "ATVPDKIKX0DER" | — | Marketplace ID |
| includedData | str | "summaries" | — | Data sets to include |

**Response:** `200`

#### `GET /catalog/2022-04-01/items/{asin}`
Get a single catalog item by ASIN.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| asin | str | Amazon Standard Identification Number |

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| marketplaceIds | str | — | — | Marketplace ID |
| includedData | str | — | — | Data sets to include |

**Response:** `200`

---

### Listings Items

#### `GET /listings/2021-08-01/items/{sellerId}/{sku}`
Get a listing by seller ID and SKU.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| sellerId | str | Seller identifier |
| sku | str | Stock Keeping Unit |

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| marketplaceIds | str | — | — | Marketplace ID |
| includedData | str | "attributes,issues" | — | Data sets to include |

**Response:** `200`

#### `PUT /listings/2021-08-01/items/{sellerId}/{sku}`
Create or update a listing. Returns 201 if created, 200 if updated.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| sellerId | str | Seller identifier |
| sku | str | Stock Keeping Unit |

**Request Body:**
```json
{
  "productType": "str (required)",
  "title": "str (optional)",
  "description": "str (optional)",
  "brand": "str (optional)",
  "bulletPoints": ["str"] ,
  "price": "float (optional)",
  "quantity": "int (optional)",
  "fulfillmentChannel": "str (optional)",
  "condition": "str (optional)",
  "mainImageUrl": "str (optional)",
  "category": "str (optional)",
  "asin": "str (optional)",
  "itemWeight": "float (optional)",
  "itemWeightUnit": "str (optional)",
  "itemLength": "str (optional)",
  "itemWidth": "str (optional)",
  "itemHeight": "str (optional)",
  "itemDimensionsUnit": "str (optional)"
}
```

**Response:** `200` (updated) or `201` (created)

#### `PATCH /listings/2021-08-01/items/{sellerId}/{sku}`
Partially update a listing.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| sellerId | str | Seller identifier |
| sku | str | Stock Keeping Unit |

**Request Body:**
```json
{
  "title": "str (optional)",
  "description": "str (optional)",
  "brand": "str (optional)",
  "bulletPoints": ["str"],
  "price": "float (optional)",
  "quantity": "int (optional)",
  "fulfillmentChannel": "str (optional)",
  "status": "str (optional)",
  "condition": "str (optional)",
  "mainImageUrl": "str (optional)",
  "category": "str (optional)"
}
```

**Response:** `200`

#### `DELETE /listings/2021-08-01/items/{sellerId}/{sku}`
Delete a listing.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| sellerId | str | Seller identifier |
| sku | str | Stock Keeping Unit |

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| marketplaceIds | str | — | — | Marketplace ID |

**Response:** `200`

---

### Orders

#### `GET /orders/v0/orders`
List orders with filters.

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| CreatedAfter | str | — | — | Filter orders created after date |
| CreatedBefore | str | — | — | Filter orders created before date |
| OrderStatuses | str | — | — | Filter by order status |
| FulfillmentChannels | str | — | — | Filter by fulfillment channel |
| MarketplaceIds | str | "ATVPDKIKX0DER" | — | Marketplace ID |
| MaxResultsPerPage | int | 100 | ge=1, le=100 | Max results per page |

**Response:** `200`

#### `GET /orders/v0/orders/{orderId}`
Get a single order.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| orderId | str | Order identifier |

**Response:** `200`

#### `GET /orders/v0/orders/{orderId}/orderItems`
Get items for an order.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| orderId | str | Order identifier |

**Response:** `200`

#### `POST /orders/v0/orders/{orderId}/shipmentConfirmation`
Confirm shipment for an order.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| orderId | str | Order identifier |

**Request Body:**
```json
{
  "packageReferenceId": "str (optional)",
  "carrierCode": "str (optional)",
  "trackingNumber": "str (optional)",
  "shipDate": "str (optional)"
}
```

**Response:** `200`

---

### Inventory

#### `GET /fba/inventory/v1/summaries`
Get FBA inventory summaries.

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| sellerSkus | str | — | — | Filter by seller SKUs |
| granularityType | str | "Marketplace" | — | Granularity type |
| granularityId | str | "ATVPDKIKX0DER" | — | Granularity ID |
| marketplaceIds | str | — | — | Marketplace ID |

**Response:** `200`

#### `PUT /fba/inventory/v1/items/{sellerSku}`
Update inventory for a SKU.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| sellerSku | str | Seller SKU |

**Request Body:**
```json
{
  "sellerSku": "str (required)",
  "quantity": "int (required)"
}
```

**Response:** `200`

---

### Reports

#### `GET /reports/2021-06-30/reports`
List reports.

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| reportTypes | str | — | — | Filter by report type |
| processingStatuses | str | — | — | Filter by processing status |

**Response:** `200`

#### `GET /reports/2021-06-30/reports/{reportId}`
Get a single report.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| reportId | str | Report identifier |

**Response:** `200`

#### `POST /reports/2021-06-30/reports`
Create a new report.

**Request Body:**
```json
{
  "reportType": "str (required)",
  "dataStartTime": "str (required)",
  "dataEndTime": "str (required)",
  "marketplaceIds": ["str"]
}
```

**Response:** `202`

---

### Product Pricing

#### `GET /products/pricing/v0/competitivePrice`
Get competitive pricing data.

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| Asin | str | — | — | ASIN to look up |
| Sku | str | — | — | SKU to look up |
| MarketplaceId | str | — | — | Marketplace ID |
| ItemType | str | "Asin" | — | Item type for lookup |

**Response:** `200`

#### `GET /products/pricing/v0/items/{Asin}/offers`
Get offers for a product.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| Asin | str | Amazon Standard Identification Number |

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| MarketplaceId | str | — | — | Marketplace ID |
| ItemCondition | str | "New" | — | Item condition filter |

**Response:** `200`

---

### Returns

#### `GET /returns/v0/returns`
List returns.

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| status | str | — | — | Filter by return status |
| orderId | str | — | — | Filter by order ID |

**Response:** `200`

#### `GET /returns/v0/returns/{returnId}`
Get a single return.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| returnId | str | Return identifier |

**Response:** `200`

#### `POST /returns/v0/returns/{returnId}/authorize`
Authorize a return.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| returnId | str | Return identifier |

**Response:** `200`

#### `POST /returns/v0/returns/{returnId}/close`
Close a return.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| returnId | str | Return identifier |

**Response:** `200`

---

## 2. Etsy API

**Port:** 8001 | **Env Var:** `ETSY_API_URL` | **Version:** v3.0.0

### Shop

#### `GET /v3/application/shops/{shop_id}`
Get shop details.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| shop_id | int | Shop identifier |

**Response:** `200`

#### `PUT /v3/application/shops/{shop_id}`
Update shop details.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| shop_id | int | Shop identifier |

**Request Body:**
```json
{
  "title": "str (optional)",
  "announcement": "str (optional)",
  "sale_message": "str (optional)",
  "is_vacation": "bool (optional)",
  "vacation_message": "str (optional)",
  "accepts_custom_requests": "bool (optional)",
  "policy_welcome": "str (optional)",
  "policy_payment": "str (optional)",
  "policy_shipping": "str (optional)",
  "policy_refunds": "str (optional)"
}
```

**Response:** `200`

---

### Shop Sections

#### `GET /v3/application/shops/{shop_id}/sections`
List all sections for a shop.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| shop_id | int | Shop identifier |

**Response:** `200`

#### `GET /v3/application/shops/{shop_id}/sections/{section_id}`
Get a single shop section.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| shop_id | int | Shop identifier |
| section_id | int | Section identifier |

**Response:** `200`

---

### Listings

#### `GET /v3/application/shops/{shop_id}/listings`
List shop listings with filters.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| shop_id | int | Shop identifier |

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| state | str | "active" | — | Listing state filter |
| sort_on | str | "created" | — | Sort field |
| sort_order | str | "desc" | — | Sort direction |
| limit | int | 25 | ge=1, le=100 | Results per page |
| offset | int | — | ge=0 | Pagination offset |
| section_id | int | — | — | Filter by section |
| q | str | — | — | Search query |

**Response:** `200`

#### `GET /v3/application/listings/{listing_id}`
Get a single listing.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| listing_id | int | Listing identifier |

**Response:** `200`

#### `POST /v3/application/shops/{shop_id}/listings`
Create a new listing.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| shop_id | int | Shop identifier |

**Request Body:**
```json
{
  "title": "str (required)",
  "description": "str (required)",
  "price": "float (required)",
  "quantity": "int (required)",
  "who_made": "str (required)",
  "when_made": "str (required)",
  "taxonomy_id": "int (required)",
  "tags": ["str"],
  "materials": ["str"],
  "shop_section_id": "int (optional)",
  "shipping_profile_id": "int (optional)",
  "return_policy_id": "int (optional)",
  "processing_min": "int (optional)",
  "processing_max": "int (optional)",
  "item_weight": "optional",
  "item_weight_unit": "optional",
  "item_length": "optional",
  "item_width": "optional",
  "item_height": "optional",
  "item_dimensions_unit": "optional",
  "is_supply": "bool (optional, default=false)",
  "is_customizable": "bool (optional, default=false)",
  "is_personalizable": "bool (optional, default=false)"
}
```

**Response:** `201`

#### `PUT /v3/application/listings/{listing_id}`
Update a listing.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| listing_id | int | Listing identifier |

**Request Body:**
All fields from create body (all optional), plus:
```json
{
  "state": "str (optional)"
}
```

**Response:** `200`

#### `DELETE /v3/application/listings/{listing_id}`
Delete a listing.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| listing_id | int | Listing identifier |

**Response:** `200`

---

### Listing Images

#### `GET /v3/application/listings/{listing_id}/images`
List images for a listing.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| listing_id | int | Listing identifier |

**Response:** `200`

#### `GET /v3/application/listings/{listing_id}/images/{image_id}`
Get a single listing image.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| listing_id | int | Listing identifier |
| image_id | int | Image identifier |

**Response:** `200`

#### `DELETE /v3/application/listings/{listing_id}/images/{image_id}`
Delete a listing image.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| listing_id | int | Listing identifier |
| image_id | int | Image identifier |

**Response:** `200`

---

### Receipts (Orders)

#### `GET /v3/application/shops/{shop_id}/receipts`
List shop receipts (orders).

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| shop_id | int | Shop identifier |

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| status | str | — | — | Filter by status |
| min_created | str | — | — | Minimum creation date |
| max_created | str | — | — | Maximum creation date |
| sort_on | str | "created" | — | Sort field |
| sort_order | str | "desc" | — | Sort direction |
| limit | int | 25 | ge=1, le=100 | Results per page |
| offset | int | — | ge=0 | Pagination offset |
| was_shipped | bool | — | — | Filter by shipped status |
| was_paid | bool | — | — | Filter by paid status |

**Response:** `200`

#### `GET /v3/application/shops/{shop_id}/receipts/{receipt_id}`
Get a single receipt.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| shop_id | int | Shop identifier |
| receipt_id | int | Receipt identifier |

**Response:** `200`

#### `PUT /v3/application/shops/{shop_id}/receipts/{receipt_id}`
Update a receipt (e.g., mark as shipped).

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| shop_id | int | Shop identifier |
| receipt_id | int | Receipt identifier |

**Request Body:**
```json
{
  "shipping_carrier": "str (optional)",
  "tracking_code": "str (optional)",
  "was_shipped": "bool (optional)"
}
```

**Response:** `200`

---

### Transactions

#### `GET /v3/application/shops/{shop_id}/receipts/{receipt_id}/transactions`
List transactions for a receipt.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| shop_id | int | Shop identifier |
| receipt_id | int | Receipt identifier |

**Response:** `200`

#### `GET /v3/application/shops/{shop_id}/transactions/{transaction_id}`
Get a single transaction.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| shop_id | int | Shop identifier |
| transaction_id | int | Transaction identifier |

**Response:** `200`

---

### Reviews

#### `GET /v3/application/shops/{shop_id}/reviews`
List reviews for a shop.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| shop_id | int | Shop identifier |

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| listing_id | int | — | — | Filter by listing |
| min_rating | int | — | ge=1, le=5 | Minimum rating |
| limit | int | 25 | ge=1, le=100 | Results per page |
| offset | int | — | ge=0 | Pagination offset |

**Response:** `200`

#### `GET /v3/application/listings/{listing_id}/reviews`
List reviews for a specific listing.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| listing_id | int | Listing identifier |

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| min_rating | int | — | ge=1, le=5 | Minimum rating |
| limit | int | 25 | ge=1, le=100 | Results per page |
| offset | int | — | ge=0 | Pagination offset |

**Response:** `200`

---

### Shipping Profiles

#### `GET /v3/application/shops/{shop_id}/shipping-profiles`
List shipping profiles for a shop.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| shop_id | int | Shop identifier |

**Response:** `200`

#### `GET /v3/application/shops/{shop_id}/shipping-profiles/{profile_id}`
Get a single shipping profile.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| shop_id | int | Shop identifier |
| profile_id | int | Profile identifier |

**Response:** `200`

---

### Return Policies

#### `GET /v3/application/shops/{shop_id}/return-policies`
List return policies for a shop.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| shop_id | int | Shop identifier |

**Response:** `200`

#### `GET /v3/application/shops/{shop_id}/return-policies/{policy_id}`
Get a single return policy.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| shop_id | int | Shop identifier |
| policy_id | int | Policy identifier |

**Response:** `200`

---

## 3. Google Classroom API

**Port:** 8002 | **Env Var:** `GOOGLE_CLASSROOM_API_URL` | **Version:** v1.0

### Courses

#### `GET /v1/courses`
List courses.

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| courseStates | str | — | — | Filter by course state |
| pageSize | int | 20 | ge=1, le=100 | Results per page |
| pageToken | str | — | — | Pagination token (parsed as int) |

**Response:** `200`

#### `GET /v1/courses/{course_id}`
Get a single course.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| course_id | str | Course identifier |

**Response:** `200`

#### `POST /v1/courses`
Create a new course.

**Request Body:**
```json
{
  "name": "str (required)",
  "section": "str (optional)",
  "descriptionHeading": "str (optional)",
  "description": "str (optional)",
  "room": "str (optional)",
  "ownerId": "str (optional)"
}
```

**Response:** `201`

#### `PATCH /v1/courses/{course_id}`
Update a course.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| course_id | str | Course identifier |

**Request Body:**
```json
{
  "name": "str (optional)",
  "section": "str (optional)",
  "descriptionHeading": "str (optional)",
  "description": "str (optional)",
  "room": "str (optional)",
  "courseState": "str (optional)"
}
```

**Response:** `200`

#### `POST /v1/courses/{course_id}:archive`
Archive a course.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| course_id | str | Course identifier |

**Response:** `200`

---

### Course Work

#### `GET /v1/courses/{course_id}/courseWork`
List course work for a course.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| course_id | str | Course identifier |

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| topicId | str | — | — | Filter by topic |
| courseWorkStates | str | — | — | Filter by state |
| orderBy | str | — | — | Order results |
| pageSize | int | 20 | ge=1, le=100 | Results per page |
| pageToken | str | — | — | Pagination token |

**Response:** `200`

#### `GET /v1/courses/{course_id}/courseWork/{coursework_id}`
Get a single course work item.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| course_id | str | Course identifier |
| coursework_id | str | Course work identifier |

**Response:** `200`

#### `POST /v1/courses/{course_id}/courseWork`
Create course work.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| course_id | str | Course identifier |

**Request Body:**
```json
{
  "title": "str (required)",
  "description": "str (optional)",
  "workType": "str (required)",
  "state": "str (optional)",
  "maxPoints": "float (optional)",
  "topicId": "str (optional)",
  "dueDate": {
    "year": "int",
    "month": "int",
    "day": "int"
  },
  "dueTime": {
    "hours": "int",
    "minutes": "int"
  }
}
```

**Response:** `201`

#### `PATCH /v1/courses/{course_id}/courseWork/{coursework_id}`
Update course work.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| course_id | str | Course identifier |
| coursework_id | str | Course work identifier |

**Request Body:**
```json
{
  "title": "str (optional)",
  "description": "str (optional)",
  "state": "str (optional)",
  "maxPoints": "float (optional)",
  "topicId": "str (optional)",
  "dueDate": "object (optional)",
  "dueTime": "object (optional)"
}
```

**Response:** `200`

#### `DELETE /v1/courses/{course_id}/courseWork/{coursework_id}`
Delete course work.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| course_id | str | Course identifier |
| coursework_id | str | Course work identifier |

**Response:** `200`

---

### Topics

#### `GET /v1/courses/{course_id}/topics`
List topics for a course.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| course_id | str | Course identifier |

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| pageSize | int | 20 | ge=1, le=100 | Results per page |
| pageToken | str | — | — | Pagination token |

**Response:** `200`

#### `GET /v1/courses/{course_id}/topics/{topic_id}`
Get a single topic.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| course_id | str | Course identifier |
| topic_id | str | Topic identifier |

**Response:** `200`

#### `POST /v1/courses/{course_id}/topics`
Create a topic.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| course_id | str | Course identifier |

**Request Body:**
```json
{
  "name": "str (required)"
}
```

**Response:** `201`

#### `PATCH /v1/courses/{course_id}/topics/{topic_id}`
Update a topic.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| course_id | str | Course identifier |
| topic_id | str | Topic identifier |

**Request Body:**
```json
{
  "name": "str (optional)"
}
```

**Response:** `200`

#### `DELETE /v1/courses/{course_id}/topics/{topic_id}`
Delete a topic.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| course_id | str | Course identifier |
| topic_id | str | Topic identifier |

**Response:** `200`

---

### Student Submissions

#### `GET /v1/courses/{course_id}/courseWork/{coursework_id}/studentSubmissions`
List student submissions.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| course_id | str | Course identifier |
| coursework_id | str | Course work identifier |

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| states | str | — | — | Filter by submission state |
| late | bool | — | — | Filter late submissions |
| pageSize | int | 20 | ge=1, le=100 | Results per page |
| pageToken | str | — | — | Pagination token |

**Response:** `200`

#### `GET /v1/courses/{course_id}/courseWork/{coursework_id}/studentSubmissions/{submission_id}`
Get a single submission.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| course_id | str | Course identifier |
| coursework_id | str | Course work identifier |
| submission_id | str | Submission identifier |

**Response:** `200`

#### `PATCH /v1/courses/{course_id}/courseWork/{coursework_id}/studentSubmissions/{submission_id}`
Grade a submission.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| course_id | str | Course identifier |
| coursework_id | str | Course work identifier |
| submission_id | str | Submission identifier |

**Request Body:**
```json
{
  "assignedGrade": "float (optional)",
  "draftGrade": "float (optional)"
}
```

**Response:** `200`

#### `POST /v1/courses/{course_id}/courseWork/{coursework_id}/studentSubmissions/{submission_id}:return`
Return a submission to the student.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| course_id | str | Course identifier |
| coursework_id | str | Course work identifier |
| submission_id | str | Submission identifier |

**Response:** `200`

#### `POST /v1/courses/{course_id}/courseWork/{coursework_id}/studentSubmissions/{submission_id}:reclaim`
Reclaim a submission.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| course_id | str | Course identifier |
| coursework_id | str | Course work identifier |
| submission_id | str | Submission identifier |

**Response:** `200`

---

### Students

#### `GET /v1/courses/{course_id}/students`
List students in a course.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| course_id | str | Course identifier |

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| pageSize | int | 30 | ge=1, le=100 | Results per page |
| pageToken | str | — | — | Pagination token |

**Response:** `200`

#### `GET /v1/courses/{course_id}/students/{user_id}`
Get a single student.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| course_id | str | Course identifier |
| user_id | str | User identifier |

**Response:** `200`

#### `POST /v1/courses/{course_id}/students`
Enroll a student.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| course_id | str | Course identifier |

**Request Body:**
```json
{
  "emailAddress": "str (required)",
  "fullName": "str (optional)"
}
```

**Response:** `201`

#### `DELETE /v1/courses/{course_id}/students/{user_id}`
Remove a student from a course.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| course_id | str | Course identifier |
| user_id | str | User identifier |

**Response:** `200`

---

### Teachers

#### `GET /v1/courses/{course_id}/teachers`
List teachers for a course.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| course_id | str | Course identifier |

**Response:** `200`

#### `GET /v1/courses/{course_id}/teachers/{user_id}`
Get a single teacher.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| course_id | str | Course identifier |
| user_id | str | User identifier |

**Response:** `200`

---

### Announcements

#### `GET /v1/courses/{course_id}/announcements`
List announcements for a course.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| course_id | str | Course identifier |

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| announcementStates | str | — | — | Filter by state |
| pageSize | int | 20 | ge=1, le=100 | Results per page |
| pageToken | str | — | — | Pagination token |

**Response:** `200`

#### `GET /v1/courses/{course_id}/announcements/{announcement_id}`
Get a single announcement.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| course_id | str | Course identifier |
| announcement_id | str | Announcement identifier |

**Response:** `200`

#### `POST /v1/courses/{course_id}/announcements`
Create an announcement.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| course_id | str | Course identifier |

**Request Body:**
```json
{
  "text": "str (required)",
  "state": "str (optional)"
}
```

**Response:** `201`

#### `PATCH /v1/courses/{course_id}/announcements/{announcement_id}`
Update an announcement.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| course_id | str | Course identifier |
| announcement_id | str | Announcement identifier |

**Request Body:**
```json
{
  "text": "str (optional)",
  "state": "str (optional)"
}
```

**Response:** `200`

#### `DELETE /v1/courses/{course_id}/announcements/{announcement_id}`
Delete an announcement.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| course_id | str | Course identifier |
| announcement_id | str | Announcement identifier |

**Response:** `200`

---

### Course Work Materials

#### `GET /v1/courses/{course_id}/courseWorkMaterials`
List course work materials.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| course_id | str | Course identifier |

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| pageSize | int | 20 | ge=1, le=100 | Results per page |
| pageToken | str | — | — | Pagination token |

**Response:** `200`

#### `GET /v1/courses/{course_id}/courseWorkMaterials/{material_id}`
Get a single course work material.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| course_id | str | Course identifier |
| material_id | str | Material identifier |

**Response:** `200`

#### `POST /v1/courses/{course_id}/courseWorkMaterials`
Create a course work material.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| course_id | str | Course identifier |

**Request Body:**
```json
{
  "title": "str (required)",
  "description": "str (optional)",
  "topicId": "str (optional)",
  "materials": [
    {
      "link": {
        "url": "str (required)",
        "title": "str (optional)"
      }
    }
  ]
}
```

**Response:** `201`

---

## 4. Instagram Graph API

**Port:** 8003 | **Env Var:** `INSTAGRAM_API_URL` | **Version:** v18.0

### Hashtags

#### `GET /ig_hashtag_search`
Search for hashtags.

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| q | str | — | required | Hashtag search query |

**Response:** `200`

#### `GET /hashtag/{hashtag_id}`
Get hashtag details.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| hashtag_id | str | Hashtag identifier |

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| fields | str | — | — | Comma-separated field names |

**Response:** `200`

#### `GET /hashtag/{hashtag_id}/recent_media`
Get recent media for a hashtag.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| hashtag_id | str | Hashtag identifier |

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| user_id | str | — | required | User ID for context |
| fields | str | — | — | Comma-separated field names |
| limit | int | 25 | ge=1, le=50 | Results per page |

**Response:** `200`

---

### Media

#### `GET /media/{media_id}/children`
Get children of a carousel media.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| media_id | str | Media identifier |

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| fields | str | — | — | Comma-separated field names |

**Response:** `200`

#### `GET /media/{media_id}/comments`
Get comments on a media object.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| media_id | str | Media identifier |

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| fields | str | — | — | Comma-separated field names |
| limit | int | 25 | ge=1, le=100 | Results per page |
| offset | int | — | ge=0 | Pagination offset |

**Response:** `200`

#### `GET /media/{media_id}/insights`
Get insights for a media object.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| media_id | str | Media identifier |

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| metric | str | — | — | Metric to retrieve |

**Response:** `200`

#### `GET /media/{media_id}`
Get a single media object.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| media_id | str | Media identifier |

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| fields | str | — | — | Comma-separated field names |

**Response:** `200`

#### `DELETE /media/{media_id}`
Delete a media object.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| media_id | str | Media identifier |

**Response:** `200`

---

### Comments

#### `POST /media/{media_id}/comments`
Post a comment on media.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| media_id | str | Media identifier |

**Request Body:**
```json
{
  "message": "str (required)",
  "parent_id": "str (optional)"
}
```

**Response:** `201`

#### `DELETE /media/{media_id}/comments/{comment_id}`
Delete a comment.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| media_id | str | Media identifier |
| comment_id | str | Comment identifier |

**Response:** `200`

#### `PUT /media/{media_id}/comments/{comment_id}/hide`
Hide or unhide a comment.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| media_id | str | Media identifier |
| comment_id | str | Comment identifier |

**Request Body:**
```json
{
  "hide": "bool (optional, default=true)"
}
```

**Response:** `200`

#### `GET /comment/{comment_id}/replies`
Get replies to a comment.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| comment_id | str | Comment identifier |

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| fields | str | — | — | Comma-separated field names |
| limit | int | 25 | ge=1, le=100 | Results per page |
| offset | int | — | ge=0 | Pagination offset |

**Response:** `200`

#### `GET /comment/{comment_id}`
Get a single comment.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| comment_id | str | Comment identifier |

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| fields | str | — | — | Comma-separated field names |

**Response:** `200`

---

### Stories

#### `GET /stories/{story_id}`
Get a single story.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| story_id | str | Story identifier |

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| fields | str | — | — | Comma-separated field names |

**Response:** `200`

---

### Container

#### `GET /container/{container_id}`
Get container publish status.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| container_id | str | Container identifier |

**Response:** `200`

---

### User

#### `GET /{user_id}/media`
Get media for a user.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| user_id | str | User identifier |

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| media_type | str | — | — | Filter by media type |
| fields | str | — | — | Comma-separated field names |
| limit | int | 25 | ge=1, le=100 | Results per page |
| offset | int | — | ge=0 | Pagination offset |

**Response:** `200`

#### `GET /{user_id}/stories`
Get stories for a user.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| user_id | str | User identifier |

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| fields | str | — | — | Comma-separated field names |

**Response:** `200`

#### `GET /{user_id}/insights`
Get insights for a user.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| user_id | str | User identifier |

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| metric | str | — | — | Metric to retrieve |
| period | str | "day" | — | Time period |

**Response:** `200`

#### `GET /{user_id}/tags`
Get tagged media for a user.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| user_id | str | User identifier |

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| fields | str | — | — | Comma-separated field names |
| limit | int | 25 | ge=1, le=100 | Results per page |
| offset | int | — | ge=0 | Pagination offset |

**Response:** `200`

#### `POST /{user_id}/media`
Create a media container.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| user_id | str | User identifier |

**Request Body:**
```json
{
  "image_url": "str (optional)",
  "video_url": "str (optional)",
  "caption": "str (optional)",
  "media_type": "str (optional, default='IMAGE')",
  "children": ["str"]
}
```

**Response:** `201`

#### `POST /{user_id}/media_publish`
Publish a media container.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| user_id | str | User identifier |

**Request Body:**
```json
{
  "creation_id": "str (required)"
}
```

**Response:** `201`

#### `GET /{user_id}`
Get user profile information.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| user_id | str | User identifier |

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| fields | str | — | — | Comma-separated field names |

**Response:** `200`

---

## 5. Linear API

**Port:** 8004 | **Env Var:** `LINEAR_API_URL` | **Version:** v2024.01

### Teams

#### `GET /v1/teams`
List all teams.

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| limit | int | 50 | ge=1, le=100 | Results per page |
| offset | int | — | ge=0 | Pagination offset |

**Response:** `200`

#### `GET /v1/teams/{team_id}`
Get a single team.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| team_id | str | Team identifier |

**Response:** `200`

#### `GET /v1/teams/{team_id}/members`
List team members.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| team_id | str | Team identifier |

**Response:** `200`

#### `GET /v1/teams/{team_id}/issues`
List issues for a team.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| team_id | str | Team identifier |

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| limit | int | 50 | ge=1, le=100 | Results per page |
| offset | int | — | ge=0 | Pagination offset |

**Response:** `200`

#### `GET /v1/teams/{team_id}/projects`
List projects for a team.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| team_id | str | Team identifier |

**Response:** `200`

#### `GET /v1/teams/{team_id}/cycles`
List cycles for a team.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| team_id | str | Team identifier |

**Response:** `200`

#### `GET /v1/teams/{team_id}/workflow-states`
List workflow states for a team.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| team_id | str | Team identifier |

**Response:** `200`

#### `GET /v1/teams/{team_id}/labels`
List labels for a team.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| team_id | str | Team identifier |

**Response:** `200`

---

### Users

#### `GET /v1/users`
List all users.

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| limit | int | 50 | ge=1, le=100 | Results per page |
| offset | int | — | ge=0 | Pagination offset |

**Response:** `200`

#### `GET /v1/users/{user_id}`
Get a single user.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| user_id | str | User identifier |

**Response:** `200`

#### `GET /v1/users/{user_id}/issues`
List issues assigned to a user.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| user_id | str | User identifier |

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| limit | int | 50 | ge=1, le=100 | Results per page |
| offset | int | — | ge=0 | Pagination offset |

**Response:** `200`

---

### Workflow States

#### `GET /v1/workflow-states`
List all workflow states.

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| teamId | str | — | — | Filter by team |
| limit | int | 50 | ge=1, le=100 | Results per page |
| offset | int | — | ge=0 | Pagination offset |

**Response:** `200`

#### `GET /v1/workflow-states/{state_id}`
Get a single workflow state.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| state_id | str | State identifier |

**Response:** `200`

---

### Labels

#### `GET /v1/labels`
List all labels.

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| teamId | str | — | — | Filter by team |
| limit | int | 50 | ge=1, le=100 | Results per page |
| offset | int | — | ge=0 | Pagination offset |

**Response:** `200`

#### `GET /v1/labels/{label_id}`
Get a single label.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| label_id | str | Label identifier |

**Response:** `200`

#### `POST /v1/labels`
Create a label.

**Request Body:**
```json
{
  "name": "str (required)",
  "color": "str (required)",
  "description": "str (optional)",
  "teamId": "str (optional)"
}
```

**Response:** `201`

---

### Projects

#### `GET /v1/projects`
List all projects.

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| limit | int | 50 | ge=1, le=100 | Results per page |
| offset | int | — | ge=0 | Pagination offset |

**Response:** `200`

#### `GET /v1/projects/{project_id}`
Get a single project.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| project_id | str | Project identifier |

**Response:** `200`

#### `POST /v1/projects`
Create a project.

**Request Body:**
```json
{
  "name": "str (required)",
  "description": "str (optional)",
  "state": "str (optional)",
  "leadId": "str (optional)",
  "teamIds": ["str"],
  "startDate": "str (optional)",
  "targetDate": "str (optional)"
}
```

**Response:** `201`

#### `PUT /v1/projects/{project_id}`
Update a project.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| project_id | str | Project identifier |

**Request Body:**
Same fields as create, all optional.

**Response:** `200`

#### `GET /v1/projects/{project_id}/issues`
List issues for a project.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| project_id | str | Project identifier |

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| limit | int | 50 | ge=1, le=100 | Results per page |
| offset | int | — | ge=0 | Pagination offset |

**Response:** `200`

---

### Cycles

#### `GET /v1/cycles`
List all cycles.

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| teamId | str | — | — | Filter by team |
| status | str | — | — | Filter by status |
| limit | int | 50 | ge=1, le=100 | Results per page |
| offset | int | — | ge=0 | Pagination offset |

**Response:** `200`

#### `GET /v1/cycles/{cycle_id}`
Get a single cycle.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| cycle_id | str | Cycle identifier |

**Response:** `200`

#### `POST /v1/cycles`
Create a cycle.

**Request Body:**
```json
{
  "name": "str (required)",
  "teamId": "str (required)",
  "startsAt": "str (required)",
  "endsAt": "str (required)"
}
```

**Response:** `201`

#### `GET /v1/cycles/{cycle_id}/issues`
List issues in a cycle.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| cycle_id | str | Cycle identifier |

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| limit | int | 50 | ge=1, le=100 | Results per page |
| offset | int | — | ge=0 | Pagination offset |

**Response:** `200`

---

### Issues

#### `GET /v1/issues`
List all issues with filters.

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| stateId | str | — | — | Filter by workflow state |
| assigneeId | str | — | — | Filter by assignee |
| projectId | str | — | — | Filter by project |
| cycleId | str | — | — | Filter by cycle |
| teamId | str | — | — | Filter by team |
| priority | int | — | — | Filter by priority |
| labelId | str | — | — | Filter by label |
| limit | int | 50 | ge=1, le=100 | Results per page |
| offset | int | — | ge=0 | Pagination offset |

**Response:** `200`

#### `GET /v1/issues/search`
Search issues.

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| q | str | — | required | Search query |
| limit | int | 50 | ge=1, le=100 | Results per page |
| offset | int | — | ge=0 | Pagination offset |

**Response:** `200`

#### `GET /v1/issues/{issue_id}`
Get a single issue.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| issue_id | str | Issue identifier |

**Response:** `200`

#### `POST /v1/issues`
Create an issue.

**Request Body:**
```json
{
  "title": "str (required)",
  "teamId": "str (required)",
  "description": "str (optional)",
  "priority": "int (optional)",
  "estimate": "int (optional)",
  "stateId": "str (optional)",
  "assigneeId": "str (optional)",
  "projectId": "str (optional)",
  "cycleId": "str (optional)",
  "labelIds": ["str"],
  "dueDate": "str (optional)"
}
```

**Response:** `201`

#### `PUT /v1/issues/{issue_id}`
Update an issue.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| issue_id | str | Issue identifier |

**Request Body:**
Same fields as create (all optional), plus:
```json
{
  "sortOrder": "float (optional)"
}
```

**Response:** `200`

#### `DELETE /v1/issues/{issue_id}`
Delete an issue.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| issue_id | str | Issue identifier |

**Response:** `200`

---

### Comments

#### `GET /v1/issues/{issue_id}/comments`
List comments on an issue.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| issue_id | str | Issue identifier |

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| limit | int | 50 | ge=1, le=100 | Results per page |
| offset | int | — | ge=0 | Pagination offset |

**Response:** `200`

#### `GET /v1/comments/{comment_id}`
Get a single comment.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| comment_id | str | Comment identifier |

**Response:** `200`

#### `POST /v1/comments`
Create a comment.

**Request Body:**
```json
{
  "body": "str (required)",
  "issueId": "str (required)",
  "userId": "str (optional)"
}
```

**Response:** `201`

#### `PUT /v1/comments/{comment_id}`
Update a comment.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| comment_id | str | Comment identifier |

**Request Body:**
```json
{
  "body": "str (required)"
}
```

**Response:** `200`

#### `DELETE /v1/comments/{comment_id}`
Delete a comment.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| comment_id | str | Comment identifier |

**Response:** `200`

---

## 6. MyFitnessPal API

**Port:** 8005 | **Env Var:** `MYFITNESSPAL_API_URL` | **Version:** v1.0.0

### User Profile

#### `GET /v1/user/profile`
Get user profile.

**Response:** `200`

#### `PUT /v1/user/profile`
Update user profile.

**Request Body:**
```json
{
  "display_name": "str (optional)",
  "daily_calorie_goal": "int (optional)",
  "activity_level": "str (optional)",
  "current_weight_lbs": "float (optional)",
  "goal_weight_lbs": "float (optional)",
  "weekly_weight_goal_lbs": "float (optional)"
}
```

**Response:** `200`

---

### Goals

#### `GET /v1/user/goals`
Get user goals.

**Response:** `200`

#### `PUT /v1/user/goals`
Update user goals.

**Request Body:**
```json
{
  "daily_calorie_goal": "int (optional)",
  "macro_goals": {
    "carbs_pct": "int",
    "fat_pct": "int",
    "protein_pct": "int"
  },
  "goal_weight_lbs": "float (optional)",
  "weekly_weight_goal_lbs": "float (optional)"
}
```

**Response:** `200`

---

### Food Database

#### `GET /v1/foods/search`
Search the food database.

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| q | str | — | — | Search query |
| limit | int | 25 | ge=1, le=100 | Results per page |
| offset | int | — | ge=0 | Pagination offset |

**Response:** `200`

#### `GET /v1/foods/{food_id}`
Get a single food item.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| food_id | int | Food identifier |

**Response:** `200`

---

### Food Diary

#### `GET /v1/user/diary/{date}`
Get diary entries for a specific date.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| date | str | Date string |

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| meal | str | — | — | Filter by meal |

**Response:** `200`

#### `GET /v1/user/diary`
Get diary entries for a date range.

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| start_date | str | — | required | Start date |
| end_date | str | — | required | End date |

**Response:** `200`

#### `POST /v1/user/diary`
Log a food diary entry.

**Request Body:**
```json
{
  "date": "str (required)",
  "meal": "str (required)",
  "food_id": "int (required)",
  "servings": "float (required)"
}
```

**Response:** `201`

#### `PUT /v1/user/diary/{entry_id}`
Update a diary entry.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| entry_id | int | Diary entry identifier |

**Request Body:**
```json
{
  "servings": "float (optional)",
  "meal": "str (optional)"
}
```

**Response:** `200`

#### `DELETE /v1/user/diary/{entry_id}`
Delete a diary entry.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| entry_id | int | Diary entry identifier |

**Response:** `200`

---

### Nutrition Summary

#### `GET /v1/user/nutrition/{date}`
Get daily nutrition totals.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| date | str | Date string |

**Response:** `200`

#### `GET /v1/user/nutrition/weekly/{end_date}`
Get weekly nutrition summary.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| end_date | str | End date for the week |

**Response:** `200`

#### `GET /v1/user/progress`
Get progress over time.

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| days | int | 30 | ge=1, le=90 | Number of days |

**Response:** `200`

---

### Exercise Types

#### `GET /v1/exercises/types`
List exercise types.

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| category | str | — | — | Filter by category |
| limit | int | 25 | ge=1, le=100 | Results per page |
| offset | int | — | ge=0 | Pagination offset |

**Response:** `200`

#### `GET /v1/exercises/types/{exercise_type_id}`
Get a single exercise type.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| exercise_type_id | int | Exercise type identifier |

**Response:** `200`

---

### Exercise Log

#### `GET /v1/user/exercises`
List logged exercises.

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| start_date | str | — | — | Filter start date |
| end_date | str | — | — | Filter end date |
| limit | int | 25 | ge=1, le=100 | Results per page |
| offset | int | — | ge=0 | Pagination offset |

**Response:** `200`

#### `GET /v1/user/exercises/{exercise_id}`
Get a single exercise log entry.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| exercise_id | int | Exercise log identifier |

**Response:** `200`

#### `POST /v1/user/exercises`
Log an exercise.

**Request Body:**
```json
{
  "date": "str (required)",
  "exercise_type_id": "int (required)",
  "duration_minutes": "int (required)",
  "calories_burned": "int (required)",
  "notes": "str (optional)"
}
```

**Response:** `201`

---

### Weight Log

#### `GET /v1/user/weight`
List weight entries.

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| limit | int | 25 | ge=1, le=100 | Results per page |
| offset | int | — | ge=0 | Pagination offset |

**Response:** `200`

#### `GET /v1/user/weight/{weight_id}`
Get a single weight entry.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| weight_id | int | Weight entry identifier |

**Response:** `200`

#### `POST /v1/user/weight`
Log a weight entry.

**Request Body:**
```json
{
  "date": "str (required)",
  "weight_lbs": "float (required)",
  "notes": "str (optional)"
}
```

**Response:** `201`

---

### Water Intake

#### `GET /v1/user/water/{date}`
Get water intake for a date.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| date | str | Date string |

**Response:** `200`

#### `POST /v1/user/water`
Log water intake.

**Request Body:**
```json
{
  "date": "str (required)",
  "cups": "int (required)",
  "notes": "str (optional)"
}
```

**Response:** `201`

#### `PUT /v1/user/water/{date}`
Update water intake for a date.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| date | str | Date string |

**Request Body:**
```json
{
  "cups": "int (optional)",
  "notes": "str (optional)"
}
```

**Response:** `200`

---

## 7. Pinterest API

**Port:** 8006 | **Env Var:** `PINTEREST_API_URL` | **Version:** v5.0.0

### User Account

#### `GET /v5/user_account`
Get authenticated user account info.

**Response:** `200`

#### `GET /v5/user_account/analytics`
Get user account analytics.

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| start_date | str | — | — | Analytics start date |
| end_date | str | — | — | Analytics end date |

**Response:** `200`

---

### Boards

#### `GET /v5/boards`
List boards.

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| privacy | str | — | — | Filter by privacy setting |
| limit | int | 25 | ge=1, le=100 | Results per page |
| offset | int | — | ge=0 | Pagination offset |

**Response:** `200`

#### `GET /v5/boards/{board_id}`
Get a single board.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| board_id | str | Board identifier |

**Response:** `200`

#### `POST /v5/boards`
Create a board.

**Request Body:**
```json
{
  "name": "str (required)",
  "description": "str (optional)",
  "privacy": "str (optional)"
}
```

**Response:** `201`

#### `PATCH /v5/boards/{board_id}`
Update a board.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| board_id | str | Board identifier |

**Request Body:**
```json
{
  "name": "str (optional)",
  "description": "str (optional)",
  "privacy": "str (optional)"
}
```

**Response:** `200`

#### `DELETE /v5/boards/{board_id}`
Delete a board.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| board_id | str | Board identifier |

**Response:** `200`

#### `GET /v5/boards/{board_id}/pins`
List pins on a board.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| board_id | str | Board identifier |

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| limit | int | 25 | ge=1, le=100 | Results per page |
| offset | int | — | ge=0 | Pagination offset |

**Response:** `200`

---

### Board Sections

#### `GET /v5/boards/{board_id}/sections`
List sections on a board.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| board_id | str | Board identifier |

**Response:** `200`

#### `POST /v5/boards/{board_id}/sections`
Create a board section.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| board_id | str | Board identifier |

**Request Body:**
```json
{
  "name": "str (required)"
}
```

**Response:** `201`

#### `GET /v5/boards/{board_id}/sections/{section_id}/pins`
List pins in a board section.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| board_id | str | Board identifier |
| section_id | str | Section identifier |

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| limit | int | 25 | ge=1, le=100 | Results per page |
| offset | int | — | ge=0 | Pagination offset |

**Response:** `200`

---

### Pins

#### `GET /v5/pins`
List user's pins.

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| limit | int | 25 | ge=1, le=100 | Results per page |
| offset | int | — | ge=0 | Pagination offset |

**Response:** `200`

#### `GET /v5/pins/{pin_id}`
Get a single pin.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| pin_id | str | Pin identifier |

**Response:** `200`

#### `POST /v5/pins`
Create a pin.

**Request Body:**
```json
{
  "board_id": "str (required)",
  "title": "str (required)",
  "description": "str (optional)",
  "link": "str (optional)",
  "media_type": "str (optional)",
  "board_section_id": "str (optional)",
  "dominant_color": "str (optional)",
  "alt_text": "str (optional)"
}
```

**Response:** `201`

#### `PATCH /v5/pins/{pin_id}`
Update a pin.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| pin_id | str | Pin identifier |

**Request Body:**
```json
{
  "title": "str (optional)",
  "description": "str (optional)",
  "link": "str (optional)",
  "board_id": "str (optional)",
  "board_section_id": "str (optional)",
  "alt_text": "str (optional)"
}
```

**Response:** `200`

#### `DELETE /v5/pins/{pin_id}`
Delete a pin.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| pin_id | str | Pin identifier |

**Response:** `200`

#### `GET /v5/pins/{pin_id}/analytics`
Get analytics for a pin.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| pin_id | str | Pin identifier |

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| start_date | str | — | — | Analytics start date |
| end_date | str | — | — | Analytics end date |

**Response:** `200`

---

### Search

#### `GET /v5/search/pins`
Search pins.

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| query | str | — | required | Search query |
| limit | int | 25 | ge=1, le=100 | Results per page |
| offset | int | — | ge=0 | Pagination offset |

**Response:** `200`

---

### Media

#### `GET /v5/media/{media_id}`
Get media upload status.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| media_id | str | Media identifier |

**Response:** `200`

---

### Ad Accounts

#### `GET /v5/ad_accounts`
List ad accounts.

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| limit | int | 25 | ge=1, le=100 | Results per page |
| offset | int | — | ge=0 | Pagination offset |

**Response:** `200`

#### `GET /v5/ad_accounts/{ad_account_id}`
Get a single ad account.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| ad_account_id | str | Ad account identifier |

**Response:** `200`

#### `GET /v5/ad_accounts/{ad_account_id}/campaigns`
List campaigns for an ad account.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| ad_account_id | str | Ad account identifier |

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| status | str | — | — | Filter by campaign status |
| limit | int | 25 | ge=1, le=100 | Results per page |
| offset | int | — | ge=0 | Pagination offset |

**Response:** `200`

---

## 8. QuickBooks Online API

**Port:** 8007 | **Env Var:** `QUICKBOOKS_API_URL` | **Version:** v3.0

All entity endpoints use the path prefix `/v3/company/{realm_id}/`.

### Company Info

#### `GET /v3/company/{realm_id}/companyinfo/{company_id}`
Get company information.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| realm_id | str | Company realm ID |
| company_id | str | Company identifier |

**Response:** `200`

---

### Customers

#### `GET /v3/company/{realm_id}/customer/{customer_id}`
Get a single customer.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| realm_id | str | Company realm ID |
| customer_id | str | Customer identifier |

**Response:** `200`

#### `POST /v3/company/{realm_id}/customer`
Create or update a customer. If `Id` is present in the body, it updates; otherwise it creates.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| realm_id | str | Company realm ID |

**Request Body:**
```json
{
  "Id": "str (optional, include to update)",
  "DisplayName": "str (optional)",
  "GivenName": "str (optional)",
  "FamilyName": "str (optional)",
  "CompanyName": "str (optional)",
  "PrimaryEmailAddr": {"Address": "str"},
  "PrimaryPhone": {"FreeFormNumber": "str"},
  "BillAddr": {"Line1": "str", "City": "str"},
  "Active": "bool (optional)",
  "Notes": "str (optional)",
  "SyncToken": "str (optional)"
}
```

**Response:** `201` (created) or `200` (updated)

---

### Vendors

#### `GET /v3/company/{realm_id}/vendor/{vendor_id}`
Get a single vendor.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| realm_id | str | Company realm ID |
| vendor_id | str | Vendor identifier |

**Response:** `200`

#### `POST /v3/company/{realm_id}/vendor`
Create or update a vendor.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| realm_id | str | Company realm ID |

**Request Body:**
```json
{
  "Id": "str (optional, include to update)",
  "DisplayName": "str (optional)",
  "CompanyName": "str (optional)",
  "PrimaryEmailAddr": "object (optional)",
  "PrimaryPhone": "object (optional)",
  "BillAddr": "object (optional)",
  "Active": "bool (optional)",
  "AcctNum": "str (optional)",
  "Vendor1099": "bool (optional)",
  "SyncToken": "str (optional)"
}
```

**Response:** `201` (created) or `200` (updated)

---

### Items

#### `GET /v3/company/{realm_id}/item/{item_id}`
Get a single item.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| realm_id | str | Company realm ID |
| item_id | str | Item identifier |

**Response:** `200`

#### `POST /v3/company/{realm_id}/item`
Create or update an item.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| realm_id | str | Company realm ID |

**Request Body:**
```json
{
  "Id": "str (optional, include to update)",
  "Name": "str (optional)",
  "Description": "str (optional)",
  "Type": "str (optional)",
  "UnitPrice": "float (optional)",
  "IncomeAccountRef": {"value": "str", "name": "str"},
  "Active": "bool (optional)",
  "Taxable": "bool (optional)",
  "SyncToken": "str (optional)"
}
```

**Response:** `201` (created) or `200` (updated)

---

### Accounts

#### `GET /v3/company/{realm_id}/account/{account_id}`
Get a single account.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| realm_id | str | Company realm ID |
| account_id | str | Account identifier |

**Response:** `200`

---

### Invoices

#### `GET /v3/company/{realm_id}/invoice/{invoice_id}`
Get a single invoice.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| realm_id | str | Company realm ID |
| invoice_id | str | Invoice identifier |

**Response:** `200`

#### `GET /v3/company/{realm_id}/invoice/{invoice_id}/pdf`
Get invoice as PDF.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| realm_id | str | Company realm ID |
| invoice_id | str | Invoice identifier |

**Response:** `200`

#### `POST /v3/company/{realm_id}/invoice`
Create or update an invoice. If `Id` is present in the body, it updates.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| realm_id | str | Company realm ID |

**Request Body:**
```json
{
  "Id": "str (optional, include to update)",
  "CustomerRef": {"value": "str"},
  "Line": [{}],
  "TxnDate": "str (optional)",
  "DueDate": "str (optional)",
  "BillEmail": {"Address": "str"},
  "PrintStatus": "str (optional)",
  "EmailStatus": "str (optional)",
  "SyncToken": "str (optional)"
}
```

**Response:** `201` (created) or `200` (updated)

#### `POST /v3/company/{realm_id}/invoice/{invoice_id}`
Perform an operation on an invoice (void, delete, or send).

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| realm_id | str | Company realm ID |
| invoice_id | str | Invoice identifier |

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| operation | str | — | — | Operation: "void", "delete", or "send" |
| include | str | — | — | Set to "send" to email invoice |

**Response:** `200`

---

### Bills

#### `GET /v3/company/{realm_id}/bill/{bill_id}`
Get a single bill.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| realm_id | str | Company realm ID |
| bill_id | str | Bill identifier |

**Response:** `200`

#### `POST /v3/company/{realm_id}/bill`
Create a bill.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| realm_id | str | Company realm ID |

**Request Body:**
```json
{
  "VendorRef": "dict (required)",
  "Line": "list (required)",
  "TxnDate": "str (optional)",
  "DueDate": "str (optional)",
  "DocNumber": "str (optional)"
}
```

**Response:** `201`

#### `POST /v3/company/{realm_id}/bill/{bill_id}`
Pay a bill.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| realm_id | str | Company realm ID |
| bill_id | str | Bill identifier |

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| operation | str | — | — | Set to "pay" |

**Response:** `200`

---

### Payments

#### `GET /v3/company/{realm_id}/payment/{payment_id}`
Get a single payment.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| realm_id | str | Company realm ID |
| payment_id | str | Payment identifier |

**Response:** `200`

#### `POST /v3/company/{realm_id}/payment`
Create a payment.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| realm_id | str | Company realm ID |

**Request Body:**
```json
{
  "CustomerRef": "dict (required)",
  "TotalAmt": "float (required)",
  "Line": "list (required)",
  "TxnDate": "str (optional)"
}
```

**Response:** `201`

---

### Estimates

#### `GET /v3/company/{realm_id}/estimate/{estimate_id}`
Get a single estimate.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| realm_id | str | Company realm ID |
| estimate_id | str | Estimate identifier |

**Response:** `200`

#### `POST /v3/company/{realm_id}/estimate`
Create an estimate.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| realm_id | str | Company realm ID |

**Request Body:**
```json
{
  "CustomerRef": "dict (required)",
  "Line": "list (required)",
  "TxnDate": "str (optional)",
  "ExpirationDate": "str (optional)"
}
```

**Response:** `201`

#### `POST /v3/company/{realm_id}/estimate/{estimate_id}`
Convert an estimate to an invoice.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| realm_id | str | Company realm ID |
| estimate_id | str | Estimate identifier |

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| operation | str | — | — | Set to "convert" |

**Response:** `200`

---

### Expenses (Purchases)

#### `GET /v3/company/{realm_id}/purchase/{expense_id}`
Get a single expense/purchase.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| realm_id | str | Company realm ID |
| expense_id | str | Expense identifier |

**Response:** `200`

#### `POST /v3/company/{realm_id}/purchase`
Create an expense/purchase.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| realm_id | str | Company realm ID |

**Request Body:**
```json
{
  "AccountRef": "dict (required)",
  "PaymentType": "str (optional, default='CreditCard')",
  "Line": "list (required)",
  "TxnDate": "str (optional)"
}
```

**Response:** `201`

---

### Query

#### `GET /v3/company/{realm_id}/query`
Execute a SQL-like query against QuickBooks entities.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| realm_id | str | Company realm ID |

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| query | str | — | required | SQL-like query string |

**Response:** `200`

---

### Reports

#### `GET /v3/company/{realm_id}/reports/ProfitAndLoss`
Get Profit and Loss report.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| realm_id | str | Company realm ID |

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| start_date | str | — | — | Report start date |
| end_date | str | — | — | Report end date |

**Response:** `200`

#### `GET /v3/company/{realm_id}/reports/BalanceSheet`
Get Balance Sheet report.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| realm_id | str | Company realm ID |

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| start_date | str | — | — | Report start date |
| end_date | str | — | — | Report end date |

**Response:** `200`

#### `GET /v3/company/{realm_id}/reports/AgedReceivableDetail`
Get Aged Receivable Detail report.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| realm_id | str | Company realm ID |

**Response:** `200`

#### `GET /v3/company/{realm_id}/reports/AgedPayableDetail`
Get Aged Payable Detail report.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| realm_id | str | Company realm ID |

**Response:** `200`

---

## 9. Ring API

**Port:** 8008 | **Env Var:** `RING_API_URL` | **Version:** v1.0.0

### Devices

#### `GET /clients_api/ring_devices`
List all Ring devices.

**Response:** `200`

#### `GET /clients_api/doorbots/{device_id}`
Get a single device.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| device_id | int | Device identifier |

**Response:** `200`

#### `GET /clients_api/doorbots/{device_id}/health`
Get device health status.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| device_id | int | Device identifier |

**Response:** `200`

#### `PUT /clients_api/doorbots/{device_id}/settings`
Update device settings.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| device_id | int | Device identifier |

**Request Body:**
```json
{
  "motion_sensitivity": "int (optional)",
  "motion_detection_enabled": "bool (optional)",
  "people_detection_enabled": "bool (optional)",
  "package_detection_enabled": "bool (optional)",
  "led_status": "str (optional)",
  "light_schedule_enabled": "bool (optional)",
  "light_on_duration_seconds": "int (optional)"
}
```

**Response:** `200`

---

### Locations

#### `GET /clients_api/locations/{location_id}`
Get a single location.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| location_id | str | Location identifier |

**Response:** `200`

#### `GET /clients_api/locations/{location_id}/devices`
List devices at a location.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| location_id | str | Location identifier |

**Response:** `200`

#### `GET /clients_api/locations/{location_id}/mode`
Get current mode for a location.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| location_id | str | Location identifier |

**Response:** `200`

#### `PUT /clients_api/locations/{location_id}/mode`
Set mode for a location.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| location_id | str | Location identifier |

**Request Body:**
```json
{
  "mode": "str (required)"
}
```

**Response:** `200`

---

### Active Dings

#### `GET /clients_api/dings/active`
Get currently active dings (live events).

**Response:** `200`

---

### Event History

#### `GET /clients_api/doorbots/{device_id}/history`
Get event history for a device.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| device_id | int | Device identifier |

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| kind | str | — | — | Filter by event kind |
| date_from | str | — | — | Start date filter |
| date_to | str | — | — | End date filter |
| limit | int | 20 | ge=1, le=100 | Results per page |
| offset | int | — | ge=0 | Pagination offset |

**Response:** `200`

#### `GET /clients_api/dings/{event_id}`
Get a single event.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| event_id | int | Event identifier |

**Response:** `200`

---

### Recordings

#### `GET /clients_api/dings/{event_id}/recording`
Get recording for an event.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| event_id | int | Event identifier |

**Response:** `200`

#### `GET /clients_api/doorbots/{device_id}/recordings`
List recordings for a device.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| device_id | int | Device identifier |

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| date_from | str | — | — | Start date filter |
| date_to | str | — | — | End date filter |

**Response:** `200`

---

### Shared Users

#### `GET /clients_api/locations/{location_id}/users`
List shared users at a location.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| location_id | str | Location identifier |

**Response:** `200`

#### `GET /clients_api/locations/{location_id}/users/{user_id}`
Get a single shared user.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| location_id | str | Location identifier |
| user_id | int | User identifier |

**Response:** `200`

---

### Chime Settings

#### `GET /clients_api/chimes/{device_id}/settings`
Get chime settings.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| device_id | int | Chime device identifier |

**Response:** `200`

#### `PUT /clients_api/chimes/{device_id}/link`
Link a chime to a doorbell.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| device_id | int | Chime device identifier |

**Request Body:**
```json
{
  "doorbell_id": "int (required)"
}
```

**Response:** `200`

#### `PUT /clients_api/chimes/{device_id}/unlink`
Unlink a chime from a doorbell.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| device_id | int | Chime device identifier |

**Request Body:**
```json
{
  "doorbell_id": "int (required)"
}
```

**Response:** `200`

---

### Motion Zones

#### `GET /clients_api/doorbots/{device_id}/motion_zones`
Get motion zones for a device.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| device_id | int | Device identifier |

**Response:** `200`

---

### Notification Preferences

#### `GET /clients_api/notifications`
Get all notification preferences.

**Response:** `200`

#### `GET /clients_api/notifications/{device_id}`
Get notification preferences for a device.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| device_id | int | Device identifier |

**Response:** `200`

#### `PUT /clients_api/notifications/{device_id}`
Update notification preferences for a device.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| device_id | int | Device identifier |

**Request Body:**
```json
{
  "motion_alerts": "bool (optional)",
  "ding_alerts": "bool (optional)",
  "person_alerts": "bool (optional)",
  "package_alerts": "bool (optional)"
}
```

**Response:** `200`

---

### Siren

#### `POST /clients_api/doorbots/{device_id}/siren_on`
Activate siren on a device.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| device_id | int | Device identifier |

**Request Body:**
```json
{
  "duration_seconds": "int (optional, default=30)"
}
```

**Response:** `200`

#### `POST /clients_api/doorbots/{device_id}/siren_off`
Deactivate siren on a device.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| device_id | int | Device identifier |

**Response:** `200`

---

### Floodlight

#### `PUT /clients_api/doorbots/{device_id}/floodlight_light_on`
Control floodlight on a device.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| device_id | int | Device identifier |

**Request Body:**
```json
{
  "on": "bool (required)"
}
```

**Response:** `200`

---

## 10. YouTube Data API

**Port:** 8009 | **Env Var:** `YOUTUBE_API_URL` | **Version:** v3.0

### Channels

#### `GET /youtube/v3/channels`
List channels.

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| id | str | — | — | Channel ID |
| part | str | "snippet,contentDetails,statistics,brandingSettings" | — | Resource parts to include |

**Response:** `200`

---

### Videos

#### `GET /youtube/v3/videos`
List videos.

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| id | str | — | — | Video ID |
| channelId | str | — | — | Filter by channel |
| part | str | "snippet,contentDetails,statistics,status" | — | Resource parts to include |
| maxResults | int | 25 | ge=1, le=50 | Max results |
| pageToken | str | — | — | Pagination token |

**Response:** `200`

#### `PUT /youtube/v3/videos`
Update a video.

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| part | str | — | — | Resource parts to update |

**Request Body:**
```json
{
  "id": "str (required)",
  "snippet": "dict (optional)",
  "status": "dict (optional)"
}
```

**Response:** `200`

#### `DELETE /youtube/v3/videos`
Delete a video.

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| id | str | — | required | Video ID to delete |

**Response:** `200`

---

### Playlists

#### `GET /youtube/v3/playlists`
List playlists.

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| id | str | — | — | Playlist ID |
| channelId | str | — | — | Filter by channel |
| part | str | — | — | Resource parts to include |
| maxResults | int | 25 | ge=1, le=50 | Max results |
| pageToken | str | — | — | Pagination token |

**Response:** `200`

#### `POST /youtube/v3/playlists`
Create a playlist.

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| part | str | — | — | Resource parts |

**Request Body:**
```json
{
  "snippet": "dict (required)",
  "status": "dict (optional)"
}
```

**Response:** `201`

#### `PUT /youtube/v3/playlists`
Update a playlist.

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| part | str | — | — | Resource parts to update |

**Request Body:**
```json
{
  "id": "str (required)",
  "snippet": "dict (optional)",
  "status": "dict (optional)"
}
```

**Response:** `200`

#### `DELETE /youtube/v3/playlists`
Delete a playlist.

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| id | str | — | required | Playlist ID to delete |

**Response:** `200`

---

### Playlist Items

#### `GET /youtube/v3/playlistItems`
List items in a playlist.

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| playlistId | str | — | required | Playlist ID |
| part | str | — | — | Resource parts to include |
| maxResults | int | 25 | ge=1, le=50 | Max results |
| pageToken | str | — | — | Pagination token |

**Response:** `200`

#### `POST /youtube/v3/playlistItems`
Add an item to a playlist.

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| part | str | — | — | Resource parts |

**Request Body:**
```json
{
  "snippet": "dict (required)"
}
```

**Response:** `201`

#### `PUT /youtube/v3/playlistItems`
Update a playlist item.

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| part | str | — | — | Resource parts to update |

**Request Body:**
```json
{
  "id": "str (required)",
  "snippet": "dict (optional)"
}
```

**Response:** `200`

#### `DELETE /youtube/v3/playlistItems`
Remove an item from a playlist.

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| id | str | — | required | Playlist item ID to delete |

**Response:** `200`

---

### Comment Threads

#### `GET /youtube/v3/commentThreads`
List comment threads.

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| videoId | str | — | — | Filter by video |
| channelId | str | — | — | Filter by channel |
| part | str | — | — | Resource parts to include |
| maxResults | int | 20 | ge=1, le=100 | Max results |
| moderationStatus | str | "published" | — | Filter by moderation status |
| pageToken | str | — | — | Pagination token |

**Response:** `200`

#### `POST /youtube/v3/commentThreads`
Create a new top-level comment thread.

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| part | str | — | — | Resource parts |

**Request Body:**
```json
{
  "snippet": "dict (required)"
}
```

**Response:** `201`

---

### Comments

#### `GET /youtube/v3/comments`
List replies to a comment.

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| parentId | str | — | required | Parent comment ID |
| part | str | — | — | Resource parts to include |
| maxResults | int | 20 | ge=1, le=100 | Max results |
| pageToken | str | — | — | Pagination token |

**Response:** `200`

#### `POST /youtube/v3/comments`
Post a reply to a comment.

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| part | str | — | — | Resource parts |

**Request Body:**
```json
{
  "snippet": "dict (required)"
}
```

**Response:** `201`

#### `PUT /youtube/v3/comments`
Update a comment.

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| part | str | — | — | Resource parts to update |

**Request Body:**
```json
{
  "id": "str (required)",
  "snippet": "dict (optional)"
}
```

**Response:** `200`

#### `DELETE /youtube/v3/comments`
Delete a comment.

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| id | str | — | required | Comment ID to delete |

**Response:** `200`

#### `POST /youtube/v3/comments/setModerationStatus`
Set moderation status for one or more comments.

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| id | str | — | required | Comma-separated comment IDs |
| moderationStatus | str | — | required | New moderation status |

**Response:** `200`

---

### Search

#### `GET /youtube/v3/search`
Search YouTube.

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| q | str | — | — | Search query |
| channelId | str | — | — | Filter by channel |
| part | str | — | — | Resource parts to include |
| order | str | "relevance" | — | Sort order |
| maxResults | int | 25 | ge=1, le=50 | Max results |
| pageToken | str | — | — | Pagination token |
| type | str | "video" | — | Resource type filter |

**Response:** `200`

---

### Video Categories

#### `GET /youtube/v3/videoCategories`
List video categories.

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| regionCode | str | "US" | — | Region code |
| part | str | — | — | Resource parts to include |

**Response:** `200`

---

### Captions

#### `GET /youtube/v3/captions`
List captions for a video.

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| videoId | str | — | required | Video ID |
| part | str | — | — | Resource parts to include |

**Response:** `200`

---

### Channel Sections

#### `GET /youtube/v3/channelSections`
List channel sections.

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| channelId | str | — | required | Channel ID |
| part | str | "snippet,contentDetails" | — | Resource parts to include |

**Response:** `200`

---

### Analytics

#### `GET /youtube/analytics/v2/reports`
Get YouTube Analytics reports.

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| ids | str | "channel==UC_TechCraftAcademy" | — | Channel identifier |
| metrics | str | "views,estimatedMinutesWatched,subscribersGained" | — | Comma-separated metrics |
| dimensions | str | — | — | Report dimensions |
| filters | str | — | — | Filters (e.g. "video==VIDEO_ID") |
| startDate | str | — | — | Report start date |
| endDate | str | — | — | Report end date |

**Response:** `200`

## 11. Notion API

**Service**: `notion-api` · **Port**: 8010 · **Env**: `NOTION_API_URL`

Mock service mirroring Notion API endpoints. See `notion-api/notion-api_postman_collection.json`*` for the runnable request collection.

### Endpoints

#### Endpoints

- `GET {{baseUrl}}/health` — health
- `GET {{baseUrl}}/v1/users?page_size=10` — list users
- `GET {{baseUrl}}/v1/users/me` — get me
- `GET {{baseUrl}}/v1/users/user-amelia` — get user
- `GET {{baseUrl}}/v1/workspace` — get workspace
- `POST {{baseUrl}}/v1/search` — search
- `GET {{baseUrl}}/v1/databases/db-tasks` — get database
- `POST {{baseUrl}}/v1/databases/db-tasks/query` — query database
- `GET {{baseUrl}}/v1/pages/page-task-001` — get page
- `POST {{baseUrl}}/v1/pages` — create page
- `PATCH {{baseUrl}}/v1/pages/page-task-003` — update page
- `DELETE {{baseUrl}}/v1/pages/page-task-004` — archive page
- `GET {{baseUrl}}/v1/blocks/page-task-001/children` — list block children
- `PATCH {{baseUrl}}/v1/blocks/page-task-001/children` — append blocks
- `PATCH {{baseUrl}}/v1/blocks/block-005` — update block
- `DELETE {{baseUrl}}/v1/blocks/block-201` — delete block
- `GET {{baseUrl}}/v1/comments?page_id=page-task-001` — list comments
- `POST {{baseUrl}}/v1/comments` — create comment

---

## 12. Zillow API

**Service**: `zillow-api` · **Port**: 8011 · **Env**: `ZILLOW_API_URL`

Mock service mirroring Zillow API endpoints. See `zillow-api/zillow-api_postman_collection.json`*` for the runnable request collection.

### Endpoints

#### Endpoints

- `GET {{baseUrl}}/health` — health
- `GET {{baseUrl}}/v1/properties/search?city=Bellevue&state=WA&min_beds=4&max_price=2000000` — search Bellevue family
- `GET {{baseUrl}}/v1/properties/84120001` — get property
- `GET {{baseUrl}}/v1/properties/84120001/zestimate` — zestimate
- `GET {{baseUrl}}/v1/properties/84120001/price-history` — price history
- `GET {{baseUrl}}/v1/agents?city=Bellevue` — list agents
- `GET {{baseUrl}}/v1/agents/agent-001` — get agent
- `GET {{baseUrl}}/v1/users/user-buyer-001/saved-searches` — list saved searches
- `POST {{baseUrl}}/v1/users/user-buyer-001/saved-searches` — create saved search
- `DELETE {{baseUrl}}/v1/saved-searches/search-003` — delete saved search

---

## 13. Instacart API

**Service**: `instacart-api` · **Port**: 8012 · **Env**: `INSTACART_API_URL`

Mock service mirroring Instacart API endpoints. See `instacart-api/instacart-api_postman_collection.json`*` for the runnable request collection.

### Endpoints

#### Endpoints

- `GET {{baseUrl}}/health` — health
- `GET {{baseUrl}}/v1/users/me` — get me
- `GET {{baseUrl}}/v1/retailers?zip=94110` — list retailers by zip
- `GET {{baseUrl}}/v1/retailers/ret-safeway` — get retailer
- `GET {{baseUrl}}/v1/products?retailer_id=ret-safeway&q=milk` — search products
- `GET {{baseUrl}}/v1/products/prod-safe-002` — get product
- `POST {{baseUrl}}/v1/carts` — create cart
- `POST {{baseUrl}}/v1/carts/{{cart_id}}/items` — add to cart
- `POST {{baseUrl}}/v1/carts/{{cart_id}}/checkout` — checkout
- `GET {{baseUrl}}/v1/orders?user_id=user-emily` — list orders
- `GET {{baseUrl}}/v1/orders/order-001` — get order
- `POST {{baseUrl}}/v1/orders/order-003/cancel` — cancel order

---

## 14. Slack API

**Service**: `slack-api` · **Port**: 8013 · **Env**: `SLACK_API_URL`

Mock service mirroring Slack API endpoints. See `slack-api/slack-api_postman_collection.json`*` for the runnable request collection.

### Endpoints

#### Endpoints

- `GET {{baseUrl}}/health` — health
- `GET {{baseUrl}}/api/auth.test` — auth.test
- `GET {{baseUrl}}/api/team.info` — team.info
- `GET {{baseUrl}}/api/users.list` — users.list
- `GET {{baseUrl}}/api/users.info?user=U01AMELIA` — users.info
- `POST {{baseUrl}}/api/users.setPresence` — users.setPresence
- `GET {{baseUrl}}/api/conversations.list` — conversations.list
- `GET {{baseUrl}}/api/conversations.info?channel=C01ENG` — conversations.info
- `POST {{baseUrl}}/api/conversations.create` — conversations.create
- `GET {{baseUrl}}/api/conversations.history?channel=C01ENG&limit=5` — conversations.history
- `GET {{baseUrl}}/api/conversations.replies?channel=C01ENG&ts=1748210000.000100` — conversations.replies
- `POST {{baseUrl}}/api/conversations.invite` — conversations.invite
- `POST {{baseUrl}}/api/chat.postMessage` — chat.postMessage
- `POST {{baseUrl}}/api/chat.update` — chat.update
- `POST {{baseUrl}}/api/reactions.add` — reactions.add
- `GET {{baseUrl}}/api/search.messages?query=cutover` — search.messages

---

## 15. Obsidian API

**Service**: `obsidian-api` · **Port**: 8014 · **Env**: `OBSIDIAN_API_URL`

Mock service mirroring Obsidian API endpoints. See `obsidian-api/obsidian-api_postman_collection.json`*` for the runnable request collection.

### Endpoints

#### Endpoints

- `GET {{baseUrl}}/health` — health
- `GET {{baseUrl}}/vault` — vault info
- `GET {{baseUrl}}/vault/notes?folder=Projects` — list notes
- `GET {{baseUrl}}/vault/notes/Projects/Auth%20v2.md` — get note
- `POST {{baseUrl}}/vault/notes` — create note
- `PUT {{baseUrl}}/vault/notes/Daily/2026-05-26.md` — append to note
- `DELETE {{baseUrl}}/vault/notes/Inbox/quick%20capture.md` — delete note
- `GET {{baseUrl}}/vault/search?query=failover&content=true` — search
- `GET {{baseUrl}}/vault/backlinks/Projects/Auth%20v2.md` — backlinks
- `GET {{baseUrl}}/vault/daily/2026-05-26` — daily note

---

## 16. Whatsapp API

**Service**: `whatsapp-api` · **Port**: 8015 · **Env**: `WHATSAPP_API_URL`

Mock service mirroring Whatsapp API endpoints. See `whatsapp-api/whatsapp-api_postman_collection.json`*` for the runnable request collection.

### Endpoints

#### Endpoints

- `GET {{baseUrl}}/health` — health
- `GET {{baseUrl}}/v17.0/business` — business
- `GET {{baseUrl}}/v17.0/contacts?opted_in_only=true` — list contacts opted in
- `GET {{baseUrl}}/v17.0/contacts/15551550101` — get contact
- `GET {{baseUrl}}/v17.0/message_templates?status=APPROVED` — list approved templates
- `GET {{baseUrl}}/v17.0/message_templates/order_shipped` — get template
- `GET {{baseUrl}}/v17.0/conversations` — list conversations
- `GET {{baseUrl}}/v17.0/messages?conversation_id=conv-001` — list messages
- `POST {{baseUrl}}/v17.0/messages` — send text
- `POST {{baseUrl}}/v17.0/messages` — send template
- `POST {{baseUrl}}/v17.0/messages/status` — mark read

---

## 17. Google Calendar API

**Service**: `google-calendar-api` · **Port**: 8016 · **Env**: `GOOGLE_CALENDAR_API_URL`

Mock service mirroring Google Calendar API endpoints. See `google-calendar-api/google-calendar-api_postman_collection.json`*` for the runnable request collection.

### Endpoints

#### Endpoints

- `GET {{baseUrl}}/health` — health
- `GET {{baseUrl}}/calendar/v3/users/me/calendarList` — list calendars
- `GET {{baseUrl}}/calendar/v3/calendars/primary` — get primary calendar
- `GET {{baseUrl}}/calendar/v3/calendars/primary/events?timeMin=2026-05-26T00:00:00Z&timeMax=2026-05-31T23:59:59Z&orderBy=startTime` — list events this week
- `GET {{baseUrl}}/calendar/v3/calendars/primary/events?q=auth` — search events
- `GET {{baseUrl}}/calendar/v3/calendars/primary/events/evt-003` — get event
- `POST {{baseUrl}}/calendar/v3/calendars/primary/events` — create event
- `PATCH {{baseUrl}}/calendar/v3/calendars/primary/events/evt-003` — patch event
- `DELETE {{baseUrl}}/calendar/v3/calendars/amelia.personal@gmail.com/events/evt-006` — delete event
- `POST {{baseUrl}}/calendar/v3/freeBusy` — freeBusy

---

## 18. Gmail API

**Service**: `gmail-api` · **Port**: 8017 · **Env**: `GMAIL_API_URL`

Mock service mirroring Gmail API endpoints. See `gmail-api/gmail-api_postman_collection.json`*` for the runnable request collection.

### Endpoints

#### Endpoints

- `GET {{baseUrl}}/health` — health
- `GET {{baseUrl}}/gmail/v1/users/me/profile` — profile
- `GET {{baseUrl}}/gmail/v1/users/me/labels` — labels
- `POST {{baseUrl}}/gmail/v1/users/me/labels` — create label
- `GET {{baseUrl}}/gmail/v1/users/me/messages?labelIds=INBOX` — list inbox
- `GET {{baseUrl}}/gmail/v1/users/me/messages?q=is:unread%20from:jonas` — search unread from jonas
- `GET {{baseUrl}}/gmail/v1/users/me/messages/msg-100` — get message
- `POST {{baseUrl}}/gmail/v1/users/me/messages/send` — send message
- `POST {{baseUrl}}/gmail/v1/users/me/messages/msg-101/modify` — mark message read
- `POST {{baseUrl}}/gmail/v1/users/me/messages/msg-105/modify` — star message
- `POST {{baseUrl}}/gmail/v1/users/me/messages/msg-104/trash` — trash spam
- `GET {{baseUrl}}/gmail/v1/users/me/threads?q=label:Orbit%20Labs` — list threads
- `GET {{baseUrl}}/gmail/v1/users/me/threads/thr-100` — get thread
- `POST {{baseUrl}}/gmail/v1/users/me/drafts` — create draft
- `POST {{baseUrl}}/gmail/v1/users/me/drafts/draft-001/send` — send draft

---

## 19. Google Drive API

**Service**: `google-drive-api` · **Port**: 8018 · **Env**: `GOOGLE_DRIVE_API_URL`

Mock service mirroring Google Drive API endpoints. See `google-drive-api/google-drive-api_postman_collection.json`*` for the runnable request collection.

### Endpoints

#### Endpoints

- `GET {{baseUrl}}/health` — health
- `GET {{baseUrl}}/drive/v3/about` — about
- `GET {{baseUrl}}/drive/v3/files?q='folder-eng' in parents and trashed = false` — list files in Engineering
- `GET {{baseUrl}}/drive/v3/files?q=mimeType = 'application/pdf' and trashed = false` — search PDFs
- `GET {{baseUrl}}/drive/v3/files?q=starred = true` — search starred
- `GET {{baseUrl}}/drive/v3/files/file-rfc-auth` — get file
- `POST {{baseUrl}}/drive/v3/files` — create folder
- `PATCH {{baseUrl}}/drive/v3/files/file-trace` — rename file
- `PATCH {{baseUrl}}/drive/v3/files/file-budget` — star file
- `POST {{baseUrl}}/drive/v3/files/file-personal/trash` — trash file
- `DELETE {{baseUrl}}/drive/v3/files/file-trashed` — delete file
- `GET {{baseUrl}}/drive/v3/files/file-rfc-auth/permissions` — list permissions
- `POST {{baseUrl}}/drive/v3/files/file-rfc-auth/permissions` — share with writer
- `DELETE {{baseUrl}}/drive/v3/files/file-budget/permissions/perm-008` — remove permission

---

## 20. Github API

**Service**: `github-api` · **Port**: 8019 · **Env**: `GITHUB_API_URL`

Mock service mirroring Github API endpoints. See `github-api/github-api_postman_collection.json`*` for the runnable request collection.

### Endpoints

#### Endpoints

- `GET {{baseUrl}}/health` — health
- `GET {{baseUrl}}/user` — authenticated user
- `GET {{baseUrl}}/orgs/orbit-labs/repos` — org repos
- `GET {{baseUrl}}/repos/orbit-labs/auth-api` — repo
- `GET {{baseUrl}}/repos/orbit-labs/auth-api/issues?state=open&labels=bug` — open issues with bug label
- `GET {{baseUrl}}/repos/orbit-labs/auth-api/issues/142` — get issue
- `POST {{baseUrl}}/repos/orbit-labs/auth-api/issues` — create issue
- `PATCH {{baseUrl}}/repos/orbit-labs/docs/issues/7` — close issue
- `GET {{baseUrl}}/repos/orbit-labs/auth-api/pulls?state=open` — list open pulls
- `GET {{baseUrl}}/repos/orbit-labs/auth-api/pulls/144` — get pull
- `PUT {{baseUrl}}/repos/orbit-labs/auth-api/pulls/144/merge` — merge pull
- `GET {{baseUrl}}/repos/orbit-labs/auth-api/issues/142/comments` — list issue comments
- `POST {{baseUrl}}/repos/orbit-labs/auth-api/issues/142/comments` — post issue comment

---

## 21. Eventbrite API

**Service**: `eventbrite-api` · **Port**: 8020 · **Env**: `EVENTBRITE_API_URL`

Mock service mirroring Eventbrite API endpoints. See `eventbrite-api/eventbrite-api_postman_collection.json`*` for the runnable request collection.

### Endpoints

#### Endpoints

- `GET {{baseUrl}}/health` — health
- `GET {{baseUrl}}/v3/users/me/organizations` — my organizations
- `GET {{baseUrl}}/v3/organizations/org-cascade/events?status=live` — org events
- `GET {{baseUrl}}/v3/events/search?q=postgres` — search events
- `GET {{baseUrl}}/v3/events/evt-7000001` — get event
- `POST {{baseUrl}}/v3/events` — create draft event
- `POST {{baseUrl}}/v3/events/evt-7000003/publish` — publish event
- `POST {{baseUrl}}/v3/events/evt-7000004/cancel` — cancel event
- `GET {{baseUrl}}/v3/venues` — list venues
- `GET {{baseUrl}}/v3/events/evt-7000001/ticket_classes` — ticket classes
- `POST {{baseUrl}}/v3/events/evt-7000003/ticket_classes` — create ticket class
- `GET {{baseUrl}}/v3/events/evt-7000001/attendees` — list attendees
- `POST {{baseUrl}}/v3/events/evt-7000004/attendees` — register attendee
- `POST {{baseUrl}}/v3/attendees/att-001/check_in` — check in

---

## 22. Stripe API

**Service**: `stripe-api` · **Port**: 8021 · **Env**: `STRIPE_API_URL`

Mock service mirroring Stripe API endpoints. See `stripe-api/stripe-api_postman_collection.json`*` for the runnable request collection.

### Endpoints

#### Endpoints

- `GET {{baseUrl}}/health` — health
- `GET {{baseUrl}}/v1/customers?limit=5` — list customers
- `GET {{baseUrl}}/v1/customers/cus_Nb1Aurora` — get customer
- `POST {{baseUrl}}/v1/customers` — create customer
- `GET {{baseUrl}}/v1/products` — list products
- `GET {{baseUrl}}/v1/prices?product=prod_Pro` — list prices
- `POST {{baseUrl}}/v1/payment_intents` — create payment intent
- `GET {{baseUrl}}/v1/payment_intents/pi_example` — get payment intent (404 expected - placeholder ID)
- `GET {{baseUrl}}/v1/charges?customer=cus_Nb1Aurora` — list charges
- `GET {{baseUrl}}/v1/charges/ch_3Aurora01` — get charge
- `POST {{baseUrl}}/v1/charges` — create charge
- `POST {{baseUrl}}/v1/refunds` — create refund
- `GET {{baseUrl}}/v1/invoices?status=open` — list invoices
- `GET {{baseUrl}}/v1/invoices/in_Aurora001` — get invoice
- `POST {{baseUrl}}/v1/invoices` — create invoice
- `GET {{baseUrl}}/v1/subscriptions?status=active` — list subscriptions
- `GET {{baseUrl}}/v1/subscriptions/sub_Aurora` — get subscription
- `POST {{baseUrl}}/v1/subscriptions` — create subscription
- `GET {{baseUrl}}/v1/balance` — get balance

---

## 23. Plaid API

**Service**: `plaid-api` · **Port**: 8022 · **Env**: `PLAID_API_URL`

Mock service mirroring Plaid API endpoints. See `plaid-api/plaid-api_postman_collection.json`*` for the runnable request collection.

### Endpoints

#### Endpoints

- `GET {{baseUrl}}/health` — health
- `POST {{baseUrl}}/accounts/get` — accounts get
- `POST {{baseUrl}}/accounts/balance/get` — accounts balance get
- `POST {{baseUrl}}/transactions/get` — transactions get
- `POST {{baseUrl}}/institutions/get_by_id` — institutions get by id
- `POST {{baseUrl}}/identity/get` — identity get

---

## 24. Coinbase API

**Service**: `coinbase-api` · **Port**: 8023 · **Env**: `COINBASE_API_URL`

Mock service mirroring Coinbase API endpoints. See `coinbase-api/coinbase-api_postman_collection.json`*` for the runnable request collection.

### Endpoints

#### Endpoints

- `GET {{baseUrl}}/health` — health
- `GET {{baseUrl}}/v2/user` — get user
- `GET {{baseUrl}}/v2/accounts` — list accounts
- `GET {{baseUrl}}/v2/accounts/acct-btc-001` — get account
- `GET {{baseUrl}}/v2/prices/BTC-USD/spot` — get spot price BTC-USD
- `GET {{baseUrl}}/v2/prices/ETH-USD/spot` — get spot price ETH-USD
- `POST {{baseUrl}}/v2/accounts/acct-btc-001/buys` — create buy
- `POST {{baseUrl}}/v2/accounts/acct-eth-002/sells` — create sell
- `GET {{baseUrl}}/v2/accounts/acct-btc-001/transactions` — list transactions

---

## 25. Hubspot API

**Service**: `hubspot-api` · **Port**: 8024 · **Env**: `HUBSPOT_API_URL`

Mock service mirroring Hubspot API endpoints. See `hubspot-api/hubspot-api_postman_collection.json`*` for the runnable request collection.

### Endpoints

#### Endpoints

- `GET {{baseUrl}}/health` — health
- `GET {{baseUrl}}/crm/v3/objects/contacts?limit=5` — list contacts
- `GET {{baseUrl}}/crm/v3/objects/contacts/201` — get contact
- `POST {{baseUrl}}/crm/v3/objects/contacts` — create contact
- `PATCH {{baseUrl}}/crm/v3/objects/contacts/204` — update contact
- `GET {{baseUrl}}/crm/v3/objects/companies` — list companies
- `GET {{baseUrl}}/crm/v3/objects/deals?limit=10` — list deals
- `GET {{baseUrl}}/crm/v3/objects/deals/402` — get deal
- `POST {{baseUrl}}/crm/v3/objects/deals` — create deal
- `PATCH {{baseUrl}}/crm/v3/objects/deals/403` — move deal to new stage
- `GET {{baseUrl}}/crm/v3/pipelines/deals` — list deal pipelines

---

## 26. Zendesk API

**Service**: `zendesk-api` · **Port**: 8025 · **Env**: `ZENDESK_API_URL`

Mock service mirroring Zendesk API endpoints. See `zendesk-api/zendesk-api_postman_collection.json`*` for the runnable request collection.

### Endpoints

#### Endpoints

- `GET {{baseUrl}}/health` — health
- `GET {{baseUrl}}/api/v2/tickets?status=open` — list tickets
- `GET {{baseUrl}}/api/v2/tickets/701` — get ticket
- `POST {{baseUrl}}/api/v2/tickets` — create ticket
- `PUT {{baseUrl}}/api/v2/tickets/704` — update ticket (status/assignee/priority)
- `GET {{baseUrl}}/api/v2/tickets/701/comments` — list ticket comments
- `POST {{baseUrl}}/api/v2/tickets/701/comments` — create comment
- `GET {{baseUrl}}/api/v2/users?role=agent` — list users
- `GET {{baseUrl}}/api/v2/users/602` — get user
- `GET {{baseUrl}}/api/v2/organizations` — list organizations

---

## 27. Twilio API

**Service**: `twilio-api` · **Port**: 8026 · **Env**: `TWILIO_API_URL`

Mock service mirroring Twilio API endpoints. See `twilio-api/twilio-api_postman_collection.json`*` for the runnable request collection.

### Endpoints

#### Endpoints

- `GET {{baseUrl}}/health` — health
- `GET {{baseUrl}}/2010-04-01/Accounts/{{accountSid}}/Messages.json?PageSize=10` — list messages
- `GET {{baseUrl}}/2010-04-01/Accounts/{{accountSid}}/Messages.json?Status=received` — list inbound messages
- `GET {{baseUrl}}/2010-04-01/Accounts/{{accountSid}}/Messages/SM0a1b2c3d4e5f60718293a4b5c6d7e801.json` — get message
- `POST {{baseUrl}}/2010-04-01/Accounts/{{accountSid}}/Messages.json?To=%2B14155557777&From=%2B14155550123&Body=Hello%20from%20the%20mock` — create message
- `GET {{baseUrl}}/2010-04-01/Accounts/{{accountSid}}/Calls.json` — list calls
- `POST {{baseUrl}}/2010-04-01/Accounts/{{accountSid}}/Calls.json?To=%2B14155557777&From=%2B14155550123` — create call
- `GET {{baseUrl}}/2010-04-01/Accounts/{{accountSid}}/IncomingPhoneNumbers.json` — list incoming phone numbers
- `GET {{baseUrl}}/v1/PhoneNumbers/+14155550123` — lookup phone number

---

## 28. Sendgrid API

**Service**: `sendgrid-api` · **Port**: 8027 · **Env**: `SENDGRID_API_URL`

Mock service mirroring Sendgrid API endpoints. See `sendgrid-api/sendgrid-api_postman_collection.json`*` for the runnable request collection.

### Endpoints

#### Endpoints

- `GET {{baseUrl}}/health` — health
- `POST {{baseUrl}}/v3/mail/send` — send mail
- `GET {{baseUrl}}/v3/templates?generations=dynamic` — list templates
- `GET {{baseUrl}}/v3/templates/d-1a2b3c4d5e6f7081` — get template
- `POST {{baseUrl}}/v3/templates` — create template
- `GET {{baseUrl}}/v3/marketing/contacts` — list marketing contacts
- `POST {{baseUrl}}/v3/marketing/contacts` — upsert marketing contacts
- `GET {{baseUrl}}/v3/marketing/lists` — list lists
- `GET {{baseUrl}}/v3/stats?start_date=2026-05-20&end_date=2026-05-26` — get stats

---

## 29. Zoom API

**Service**: `zoom-api` · **Port**: 8028 · **Env**: `ZOOM_API_URL`

Mock service mirroring Zoom API endpoints. See `zoom-api/zoom-api_postman_collection.json`*` for the runnable request collection.

### Endpoints

#### Endpoints

- `GET {{baseUrl}}/health` — health
- `GET {{baseUrl}}/v2/users/me` — get me
- `GET {{baseUrl}}/v2/users/me/meetings?type=scheduled` — list scheduled meetings
- `GET {{baseUrl}}/v2/users/me/meetings?type=previous_meetings` — list previous meetings
- `POST {{baseUrl}}/v2/users/me/meetings` — create meeting
- `GET {{baseUrl}}/v2/meetings/85012345678` — get meeting
- `PATCH {{baseUrl}}/v2/meetings/85012345678` — update meeting
- `DELETE {{baseUrl}}/v2/meetings/85012345680` — delete meeting
- `GET {{baseUrl}}/v2/meetings/85012345670/recordings` — get recordings
- `GET {{baseUrl}}/v2/meetings/85012345679/registrants?status=approved` — list registrants

---

## 30. Jira API

**Service**: `jira-api` · **Port**: 8029 · **Env**: `JIRA_API_URL`

Mock service mirroring Jira API endpoints. See `jira-api/jira-api_postman_collection.json`*` for the runnable request collection.

### Endpoints

#### Endpoints

- `GET {{baseUrl}}/health` — health
- `GET {{baseUrl}}/rest/api/3/project` — list projects
- `POST {{baseUrl}}/rest/api/3/issue` — create issue
- `GET {{baseUrl}}/rest/api/3/issue/ENG-102` — get issue
- `PUT {{baseUrl}}/rest/api/3/issue/ENG-102` — update issue
- `GET {{baseUrl}}/rest/api/3/issue/ENG-104/transitions` — get transitions
- `POST {{baseUrl}}/rest/api/3/issue/ENG-104/transitions` — transition issue
- `GET {{baseUrl}}/rest/api/3/search?jql=project %3D ENG AND status %3D "In Progress"` — search jql
- `GET {{baseUrl}}/rest/agile/1.0/board` — list boards
- `GET {{baseUrl}}/rest/agile/1.0/board/1/sprint?state=active` — list sprints

---

## 31. Trello API

**Service**: `trello-api` · **Port**: 8030 · **Env**: `TRELLO_API_URL`

Mock service mirroring Trello API endpoints. See `trello-api/trello-api_postman_collection.json`*` for the runnable request collection.

### Endpoints

#### Endpoints

- `GET {{baseUrl}}/health` — health
- `GET {{baseUrl}}/1/members/me/boards` — list my boards
- `GET {{baseUrl}}/1/boards/60b1000000000000000000b1` — get board
- `GET {{baseUrl}}/1/boards/60b1000000000000000000b1/lists` — list board lists
- `GET {{baseUrl}}/1/lists/61c1000000000000000000c1/cards` — list cards in list
- `POST {{baseUrl}}/1/cards?idList=61c1000000000000000000c1&name=Investigate%20webhook%20retries&desc=Add%20exponential%20backoff` — create card
- `PUT {{baseUrl}}/1/cards/62d1000000000000000000d4?idList=61c1000000000000000000c2` — move card to Doing
- `DELETE {{baseUrl}}/1/cards/62d1000000000000000000da` — delete card
- `GET {{baseUrl}}/1/cards/62d1000000000000000000d2/checklists` — list card checklists
- `POST {{baseUrl}}/1/checklists?idCard=62d1000000000000000000d4&name=Spike%20tasks` — create checklist

---

## 32. Asana API

**Service**: `asana-api` · **Port**: 8031 · **Env**: `ASANA_API_URL`

Mock service mirroring Asana API endpoints. See `asana-api/asana-api_postman_collection.json`*` for the runnable request collection.

### Endpoints

#### Endpoints

- `GET {{baseUrl}}/health` — health
- `GET {{baseUrl}}/api/1.0/workspaces` — list workspaces
- `GET {{baseUrl}}/api/1.0/users?workspace=1201990000000001` — list users
- `GET {{baseUrl}}/api/1.0/projects?workspace=1201990000000001` — list projects
- `GET {{baseUrl}}/api/1.0/projects/1203000000002001` — get project
- `GET {{baseUrl}}/api/1.0/projects/1203000000002001/sections` — list project sections
- `GET {{baseUrl}}/api/1.0/projects/1203000000002001/tasks` — list project tasks
- `GET {{baseUrl}}/api/1.0/tasks?project=1203000000002002&completed=false` — list tasks
- `GET {{baseUrl}}/api/1.0/tasks/1205000000004001` — get task
- `POST {{baseUrl}}/api/1.0/tasks` — create task
- `PUT {{baseUrl}}/api/1.0/tasks/1205000000004002` — complete task

---

## 33. Airtable API

**Service**: `airtable-api` · **Port**: 8032 · **Env**: `AIRTABLE_API_URL`

Mock service mirroring Airtable API endpoints. See `airtable-api/airtable-api_postman_collection.json`*` for the runnable request collection.

### Endpoints

#### Endpoints

- `GET {{baseUrl}}/health` — health
- `GET {{baseUrl}}/v0/meta/bases` — list bases
- `GET {{baseUrl}}/v0/meta/bases/appNW1studio0001/tables` — list tables
- `GET {{baseUrl}}/v0/appNW1studio0001/Tasks?pageSize=5` — list records
- `GET {{baseUrl}}/v0/appNW1studio0001/Tasks?filterByFormula={Status}='Done'` — list records filtered
- `GET {{baseUrl}}/v0/appNW1studio0001/Contacts?pageSize=3&offset=3` — list records paginated
- `GET {{baseUrl}}/v0/appNW1studio0001/Tasks/recTask0000000001` — get record
- `POST {{baseUrl}}/v0/appNW1studio0001/Tasks` — create records
- `PATCH {{baseUrl}}/v0/appNW1studio0001/Tasks/recTask0000000002` — update record
- `DELETE {{baseUrl}}/v0/appNW1studio0001/Tasks/recTask0000000010` — delete record

---

## 34. Google Maps API

**Service**: `google-maps-api` · **Port**: 8033 · **Env**: `GOOGLE_MAPS_API_URL`

Mock service mirroring Google Maps API endpoints. See `google-maps-api/google-maps-api_postman_collection.json`*` for the runnable request collection.

### Endpoints

#### Endpoints

- `GET {{baseUrl}}/health` — health
- `GET {{baseUrl}}/maps/api/place/textsearch/json?query=coffee` — text search
- `GET {{baseUrl}}/maps/api/place/details/json?place_id=ChIJplace0000001` — place details
- `GET {{baseUrl}}/maps/api/place/nearbysearch/json?location=37.7825,-122.4061&radius=3000&type=cafe` — nearby search
- `GET {{baseUrl}}/maps/api/geocode/json?address=union square` — geocode
- `GET {{baseUrl}}/maps/api/directions/json?origin=union square&destination=fishermans wharf&mode=driving` — directions
- `GET {{baseUrl}}/maps/api/distancematrix/json?origins=san francisco|oakland&destinations=berkeley|palo alto&mode=driving` — distance matrix

---

## 35. Yelp API

**Service**: `yelp-api` · **Port**: 8034 · **Env**: `YELP_API_URL`

Mock service mirroring Yelp API endpoints. See `yelp-api/yelp-api_postman_collection.json`*` for the runnable request collection.

### Endpoints

#### Endpoints

- `GET {{baseUrl}}/health` — health
- `GET {{baseUrl}}/v3/businesses/search?location=San Francisco&term=cafe&sort_by=rating&limit=10` — search businesses
- `GET {{baseUrl}}/v3/businesses/search?categories=restaurants&price=3,4&sort_by=review_count` — search by category and price
- `GET {{baseUrl}}/v3/businesses/biz-tartine-0002` — get business
- `GET {{baseUrl}}/v3/businesses/biz-tartine-0002/reviews` — get business reviews
- `GET {{baseUrl}}/v3/categories` — list categories

---

## 36. Openweather API

**Service**: `openweather-api` · **Port**: 8035 · **Env**: `OPENWEATHER_API_URL`

Mock service mirroring Openweather API endpoints. See `openweather-api/openweather-api_postman_collection.json`*` for the runnable request collection.

### Endpoints

#### Endpoints

- `GET {{baseUrl}}/health` — health
- `GET {{baseUrl}}/data/2.5/weather?q=London` — current weather by city
- `GET {{baseUrl}}/data/2.5/weather?lat=40.7143&lon=-74.0060` — current weather by coords
- `GET {{baseUrl}}/data/2.5/forecast?q=Tokyo` — forecast
- `GET {{baseUrl}}/geo/1.0/direct?q=Paris&limit=5` — geocode direct

---

## 37. Uber API

**Service**: `uber-api` · **Port**: 8036 · **Env**: `UBER_API_URL`

Mock service mirroring Uber API endpoints. See `uber-api/uber-api_postman_collection.json`*` for the runnable request collection.

### Endpoints

#### Endpoints

- `GET {{baseUrl}}/health` — health
- `GET {{baseUrl}}/v1.2/products?latitude=37.7752&longitude=-122.4180` — list products
- `GET {{baseUrl}}/v1.2/products/uberx` — get product
- `GET {{baseUrl}}/v1.2/estimates/price?start_latitude=37.7752&start_longitude=-122.4180&end_latitude=37.7956&end_longitude=-122.3934` — price estimates
- `GET {{baseUrl}}/v1.2/estimates/time?start_latitude=37.7752&start_longitude=-122.4180` — time estimates
- `POST {{baseUrl}}/v1.2/requests` — request ride
- `GET {{baseUrl}}/v1.2/requests/req-7f0011aa` — get request
- `DELETE {{baseUrl}}/v1.2/requests/req-7f0011aa` — cancel request (400 expected - already-completed ride)
- `GET {{baseUrl}}/v1.2/history?limit=10` — ride history
- `GET {{baseUrl}}/v1.2/me` — rider profile

---

## 38. Doordash API

**Service**: `doordash-api` · **Port**: 8037 · **Env**: `DOORDASH_API_URL`

Mock service mirroring Doordash API endpoints. See `doordash-api/doordash-api_postman_collection.json`*` for the runnable request collection.

### Endpoints

#### Endpoints

- `GET {{baseUrl}}/health` — health
- `GET {{baseUrl}}/v1/stores?latitude=37.7842&longitude=-122.4078` — list stores
- `GET {{baseUrl}}/v1/stores?cuisine=Japanese` — list stores by cuisine
- `GET {{baseUrl}}/v1/stores/store-sakura` — get store
- `GET {{baseUrl}}/v1/stores/store-sakura/menu` — get menu
- `POST {{baseUrl}}/v1/carts` — create cart
- `POST {{baseUrl}}/v1/carts/{{cartId}}/items` — add cart item
- `GET {{baseUrl}}/v1/carts/{{cartId}}` — get cart
- `POST {{baseUrl}}/v1/carts/{{cartId}}/checkout` — checkout
- `GET {{baseUrl}}/v1/orders/order-90aa12` — get order

---

## 39. Airbnb API

**Service**: `airbnb-api` · **Port**: 8038 · **Env**: `AIRBNB_API_URL`

Mock service mirroring Airbnb API endpoints. See `airbnb-api/airbnb-api_postman_collection.json`*` for the runnable request collection.

### Endpoints

#### Endpoints

- `GET {{baseUrl}}/health` — health
- `GET {{baseUrl}}/v2/listings/search?location=San Francisco&checkin=2026-06-05&checkout=2026-06-09&guests=2&max_price=400` — search listings
- `GET {{baseUrl}}/v2/listings/lst-101` — get listing
- `GET {{baseUrl}}/v2/listings/lst-101/availability` — get availability
- `GET {{baseUrl}}/v2/listings/lst-101/reviews` — get reviews
- `POST {{baseUrl}}/v2/reservations` — create reservation
- `GET {{baseUrl}}/v2/reservations/{{reservationId}}` — get reservation
- `DELETE {{baseUrl}}/v2/reservations/{{reservationId}}` — cancel reservation

---

## 40. Spotify API

**Service**: `spotify-api` · **Port**: 8039 · **Env**: `SPOTIFY_API_URL`

Mock service mirroring Spotify API endpoints. See `spotify-api/spotify-api_postman_collection.json`*` for the runnable request collection.

### Endpoints

#### Endpoints

- `GET {{baseUrl}}/health` — health
- `GET {{baseUrl}}/v1/me` — get me
- `GET {{baseUrl}}/v1/me/playlists` — my playlists
- `GET {{baseUrl}}/v1/playlists/37i9dQZF1DXcBWIGoYBM5M` — get playlist
- `GET {{baseUrl}}/v1/playlists/37i9dQZF1DXcBWIGoYBM5M/tracks` — playlist tracks
- `POST {{baseUrl}}/v1/users/user-leo/playlists` — create playlist
- `POST {{baseUrl}}/v1/playlists/2v3iNvBX8Ay1Gt2uXtUKUg/tracks` — add tracks
- `GET {{baseUrl}}/v1/search?q=neon&type=track,artist` — search
- `GET {{baseUrl}}/v1/me/player` — player state
- `PUT {{baseUrl}}/v1/me/player/play` — play

---

## 41. Pagerduty API

**Service**: `pagerduty-api` · **Port**: 8040 · **Env**: `PAGERDUTY_API_URL`

Mock service mirroring Pagerduty API endpoints. See `pagerduty-api/pagerduty-api_postman_collection.json`*` for the runnable request collection.

### Endpoints

#### Endpoints

- `GET {{baseUrl}}/health` — health
- `GET {{baseUrl}}/services` — list services
- `GET {{baseUrl}}/services/PS001` — get service
- `GET {{baseUrl}}/incidents?statuses[]=triggered&statuses[]=acknowledged` — list incidents (open)
- `GET {{baseUrl}}/incidents/PI001` — get incident
- `POST {{baseUrl}}/incidents` — trigger incident
- `PUT {{baseUrl}}/incidents/PI001` — acknowledge incident
- `PUT {{baseUrl}}/incidents/PI001` — resolve incident
- `POST {{baseUrl}}/incidents/PI001/notes` — add incident note
- `GET {{baseUrl}}/oncalls` — list oncalls
- `GET {{baseUrl}}/schedules` — list schedules
- `GET {{baseUrl}}/escalation_policies` — list escalation policies
- `GET {{baseUrl}}/users` — list users

---

## 42. Square API

**Service**: `square-api` · **Port**: 8041 · **Env**: `SQUARE_API_URL`

Mock service mirroring Square API endpoints. See `square-api/square-api_postman_collection.json`*` for the runnable request collection.

### Endpoints

#### Endpoints

- `GET {{baseUrl}}/health` — health
- `GET {{baseUrl}}/v2/merchants/me` — get merchant
- `GET {{baseUrl}}/v2/payments?limit=10` — list payments
- `GET {{baseUrl}}/v2/payments/PAY_AURORA01` — get payment
- `POST {{baseUrl}}/v2/payments` — create payment
- `POST {{baseUrl}}/v2/refunds` — create refund
- `GET {{baseUrl}}/v2/customers?limit=10` — list customers
- `GET {{baseUrl}}/v2/customers/CUST_MAYA03` — get customer
- `POST {{baseUrl}}/v2/customers` — create customer
- `GET {{baseUrl}}/v2/catalog/list?types=ITEM` — list catalog
- `POST {{baseUrl}}/v2/orders` — create order
- `GET {{baseUrl}}/v2/orders/ORD_AURORA01` — get order
- `GET {{baseUrl}}/v2/inventory/VAR_BEANS_12` — get inventory

---

## 43. Paypal API

**Service**: `paypal-api` · **Port**: 8042 · **Env**: `PAYPAL_API_URL`

Mock service mirroring Paypal API endpoints. See `paypal-api/paypal-api_postman_collection.json`*` for the runnable request collection.

### Endpoints

#### Endpoints

- `GET {{baseUrl}}/health` — health
- `POST {{baseUrl}}/v2/checkout/orders` — create checkout order
- `GET {{baseUrl}}/v2/checkout/orders/ORDER-8AB54321CD987654E` — get checkout order
- `POST {{baseUrl}}/v2/checkout/orders/ORDER-8AB54321CD987654E/capture` — capture order
- `POST {{baseUrl}}/v2/payments/refunds` — create refund
- `GET {{baseUrl}}/v2/payments/refunds/REF_1A234567BC890123` — get refund
- `GET {{baseUrl}}/v2/invoicing/invoices?status=PAID` — list invoices
- `POST {{baseUrl}}/v2/invoicing/invoices` — create invoice
- `POST {{baseUrl}}/v1/payments/payouts` — create payout

---

## 44. Alpaca API

**Service**: `alpaca-api` · **Port**: 8043 · **Env**: `ALPACA_API_URL`

Mock service mirroring Alpaca API endpoints. See `alpaca-api/alpaca-api_postman_collection.json`*` for the runnable request collection.

### Endpoints

#### Endpoints

- `GET {{baseUrl}}/health` — health
- `GET {{baseUrl}}/v2/account` — get account
- `GET {{baseUrl}}/v2/positions` — list positions
- `GET {{baseUrl}}/v2/positions/AAPL` — get position
- `GET {{baseUrl}}/v2/orders?status=open` — list orders
- `GET {{baseUrl}}/v2/orders/ORD-aurora-0001` — get order
- `POST {{baseUrl}}/v2/orders` — create buy order
- `POST {{baseUrl}}/v2/orders` — create sell order
- `DELETE {{baseUrl}}/v2/orders/ORD-delta-0004` — cancel order
- `GET {{baseUrl}}/v2/assets?asset_class=us_equity` — list assets
- `GET {{baseUrl}}/v2/stocks/AAPL/quotes/latest` — latest quote

---

## 45. Salesforce API

**Service**: `salesforce-api` · **Port**: 8044 · **Env**: `SALESFORCE_API_URL`

Mock service mirroring Salesforce API endpoints. See `salesforce-api/salesforce-api_postman_collection.json`*` for the runnable request collection.

### Endpoints

#### Endpoints

- `GET {{baseUrl}}/health` — health
- `GET {{baseUrl}}/services/data/v59.0/sobjects/Account` — list accounts
- `GET {{baseUrl}}/services/data/v59.0/sobjects/Account/001Ax000001AAAAAA1` — get account
- `POST {{baseUrl}}/services/data/v59.0/sobjects/Account` — create account
- `PATCH {{baseUrl}}/services/data/v59.0/sobjects/Account/001Ax000001AAAAAA1` — update account
- `GET {{baseUrl}}/services/data/v59.0/sobjects/Contact` — list contacts
- `GET {{baseUrl}}/services/data/v59.0/sobjects/Contact/003Ax000002BBBBBB2` — get contact
- `POST {{baseUrl}}/services/data/v59.0/sobjects/Contact` — create contact
- `GET {{baseUrl}}/services/data/v59.0/sobjects/Lead` — list leads
- `GET {{baseUrl}}/services/data/v59.0/sobjects/Lead/00QAx000001AAAAAA1` — get lead
- `POST {{baseUrl}}/services/data/v59.0/sobjects/Lead` — create lead
- `PATCH {{baseUrl}}/services/data/v59.0/sobjects/Lead/00QAx000001AAAAAA1` — update lead
- `GET {{baseUrl}}/services/data/v59.0/sobjects/Opportunity` — list opportunities
- `GET {{baseUrl}}/services/data/v59.0/sobjects/Opportunity/006Ax000001AAAAAA1` — get opportunity
- `POST {{baseUrl}}/services/data/v59.0/sobjects/Opportunity` — create opportunity
- `GET {{baseUrl}}/services/data/v59.0/query?q=SELECT Id, Name, Industry FROM Account WHERE Industry = 'Technology'` — soql query accounts
- `GET {{baseUrl}}/services/data/v59.0/query?q=SELECT Id, Name, Amount FROM Opportunity WHERE StageName = 'Closed Won'` — soql query opportunities

---

## 46. Confluence API

**Service**: `confluence-api` · **Port**: 8045 · **Env**: `CONFLUENCE_API_URL`

Mock service mirroring Confluence API endpoints. See `confluence-api/confluence-api_postman_collection.json`*` for the runnable request collection.

### Endpoints

#### Endpoints

- `GET {{baseUrl}}/health` — health
- `GET {{baseUrl}}/wiki/rest/api/space` — list spaces
- `GET {{baseUrl}}/wiki/rest/api/space/ENG` — get space
- `GET {{baseUrl}}/wiki/rest/api/content?type=page&spaceKey=ENG` — list content
- `POST {{baseUrl}}/wiki/rest/api/content` — create content
- `GET {{baseUrl}}/wiki/rest/api/content/100103` — get content
- `PUT {{baseUrl}}/wiki/rest/api/content/100103` — update content
- `GET {{baseUrl}}/wiki/rest/api/content/100101/child/page` — list child pages
- `GET {{baseUrl}}/wiki/rest/api/content/100103/label` — list labels
- `GET {{baseUrl}}/wiki/rest/api/content/100103/child/comment` — list comments
- `GET {{baseUrl}}/wiki/rest/api/content/search?cql=space=ENG` — search by space
- `GET {{baseUrl}}/wiki/rest/api/content/search?cql=title~"Runbook"` — search by title

---

## 47. Gitlab API

**Service**: `gitlab-api` · **Port**: 8046 · **Env**: `GITLAB_API_URL`

Mock service mirroring Gitlab API endpoints. See `gitlab-api/gitlab-api_postman_collection.json`*` for the runnable request collection.

### Endpoints

#### Endpoints

- `GET {{baseUrl}}/health` — health
- `GET {{baseUrl}}/api/v4/user` — get current user
- `GET {{baseUrl}}/api/v4/projects` — list projects
- `GET {{baseUrl}}/api/v4/projects/101` — get project
- `GET {{baseUrl}}/api/v4/projects/101/issues?state=opened` — list issues
- `GET {{baseUrl}}/api/v4/projects/101/issues/1` — get issue
- `POST {{baseUrl}}/api/v4/projects/101/issues` — create issue
- `PUT {{baseUrl}}/api/v4/projects/101/issues/2` — update issue (close)
- `GET {{baseUrl}}/api/v4/projects/101/merge_requests?state=opened` — list merge requests
- `POST {{baseUrl}}/api/v4/projects/101/merge_requests` — create merge request
- `PUT {{baseUrl}}/api/v4/projects/101/merge_requests/1/merge` — merge merge request
- `GET {{baseUrl}}/api/v4/projects/101/pipelines` — list pipelines

---

## 48. Sentry API

**Service**: `sentry-api` · **Port**: 8047 · **Env**: `SENTRY_API_URL`

Mock service mirroring Sentry API endpoints. See `sentry-api/sentry-api_postman_collection.json`*` for the runnable request collection.

### Endpoints

#### Endpoints

- `GET {{baseUrl}}/health` — health
- `GET {{baseUrl}}/api/0/organizations/orbit-labs/projects/` — list org projects
- `GET {{baseUrl}}/api/0/projects/orbit-labs/auth-service/issues/?status=unresolved` — list project issues
- `GET {{baseUrl}}/api/0/projects/orbit-labs/web-frontend/issues/?level=error` — list project issues by level
- `GET {{baseUrl}}/api/0/organizations/orbit-labs/issues/40001/` — get issue
- `PUT {{baseUrl}}/api/0/organizations/orbit-labs/issues/40001/` — resolve issue
- `PUT {{baseUrl}}/api/0/organizations/orbit-labs/issues/40002/` — ignore issue
- `GET {{baseUrl}}/api/0/organizations/orbit-labs/issues/40001/events/` — list issue events
- `GET {{baseUrl}}/api/0/organizations/orbit-labs/releases/` — list releases
- `GET {{baseUrl}}/api/0/organizations/orbit-labs/releases/?project=auth-service` — list releases for project

---

## 49. Datadog API

**Service**: `datadog-api` · **Port**: 8048 · **Env**: `DATADOG_API_URL`

Mock service mirroring Datadog API endpoints. See `datadog-api/datadog-api_postman_collection.json`*` for the runnable request collection.

### Endpoints

#### Endpoints

- `GET {{baseUrl}}/health` — health
- `GET {{baseUrl}}/api/v1/query?from=1748160000&to=1748250600&query=avg:trace.http.request.duration{service:auth-service}` — query metric series
- `GET {{baseUrl}}/api/v1/monitor` — list monitors
- `GET {{baseUrl}}/api/v1/monitor?overall_state=Alert` — list monitors alerting
- `GET {{baseUrl}}/api/v1/monitor/1001` — get monitor
- `POST {{baseUrl}}/api/v1/monitor` — create monitor
- `PUT {{baseUrl}}/api/v1/monitor/1001` — update monitor (mute via state)
- `GET {{baseUrl}}/api/v1/dashboard` — list dashboards
- `GET {{baseUrl}}/api/v1/dashboard/abc-123-def` — get dashboard
- `GET {{baseUrl}}/api/v1/events` — list events
- `POST {{baseUrl}}/api/v1/events` — create event
- `GET {{baseUrl}}/api/v1/hosts` — list hosts

---

## 50. Okta API

**Service**: `okta-api` · **Port**: 8049 · **Env**: `OKTA_API_URL`

Mock service mirroring Okta API endpoints. See `okta-api/okta-api_postman_collection.json`*` for the runnable request collection.

### Endpoints

#### Endpoints

- `GET {{baseUrl}}/health` — health
- `GET {{baseUrl}}/api/v1/users` — list users
- `GET {{baseUrl}}/api/v1/users?status=ACTIVE` — list users by status
- `GET {{baseUrl}}/api/v1/users/00u1amelia` — get user
- `POST {{baseUrl}}/api/v1/users?activate=true` — create user
- `POST {{baseUrl}}/api/v1/users/00u5noor/lifecycle/activate` — activate user
- `POST {{baseUrl}}/api/v1/users/00u1amelia/lifecycle/suspend` — suspend user
- `POST {{baseUrl}}/api/v1/users/00u4rohit/lifecycle/deactivate` — deactivate user
- `GET {{baseUrl}}/api/v1/groups` — list groups
- `GET {{baseUrl}}/api/v1/groups/00g1eng` — get group
- `GET {{baseUrl}}/api/v1/groups/00g1eng/users` — list group users
- `GET {{baseUrl}}/api/v1/apps` — list apps

---

## 51. Cloudflare API

**Service**: `cloudflare-api` · **Port**: 8050 · **Env**: `CLOUDFLARE_API_URL`

Mock service mirroring Cloudflare API endpoints. See `cloudflare-api/cloudflare-api_postman_collection.json`*` for the runnable request collection.

### Endpoints

#### Endpoints

- `GET {{baseUrl}}/health` — health
- `GET {{baseUrl}}/client/v4/zones` — list zones
- `GET {{baseUrl}}/client/v4/zones/{{zoneId}}` — get zone
- `GET {{baseUrl}}/client/v4/zones/{{zoneId}}/dns_records` — list dns records
- `GET {{baseUrl}}/client/v4/zones/{{zoneId}}/dns_records?type=A` — list dns records by type
- `GET {{baseUrl}}/client/v4/zones/{{zoneId}}/dns_records/rec0001aaaa` — get dns record
- `POST {{baseUrl}}/client/v4/zones/{{zoneId}}/dns_records` — create dns record
- `PUT {{baseUrl}}/client/v4/zones/{{zoneId}}/dns_records/rec0001aaaa` — update dns record
- `DELETE {{baseUrl}}/client/v4/zones/{{zoneId}}/dns_records/rec0005eeee` — delete dns record
- `GET {{baseUrl}}/client/v4/zones/{{zoneId}}/firewall/rules` — list firewall rules

---

## 52. Kubernetes API

**Service**: `kubernetes-api` · **Port**: 8051 · **Env**: `KUBERNETES_API_URL`

Mock service mirroring Kubernetes API endpoints. See `kubernetes-api/kubernetes-api_postman_collection.json`*` for the runnable request collection.

### Endpoints

#### Endpoints

- `GET {{baseUrl}}/health` — health
- `GET {{baseUrl}}/api/v1/namespaces` — list namespaces
- `GET {{baseUrl}}/api/v1/namespaces/prod/pods` — list pods
- `GET {{baseUrl}}/api/v1/namespaces/prod/pods/api-gateway-5d8f7c` — get pod
- `DELETE {{baseUrl}}/api/v1/namespaces/prod/pods/billing-worker-9af21` — delete pod
- `GET {{baseUrl}}/apis/apps/v1/namespaces/prod/deployments` — list deployments
- `GET {{baseUrl}}/apis/apps/v1/namespaces/prod/deployments/api-gateway` — get deployment
- `PATCH {{baseUrl}}/apis/apps/v1/namespaces/prod/deployments/api-gateway/scale` — scale deployment
- `GET {{baseUrl}}/api/v1/namespaces/prod/services` — list services
- `GET {{baseUrl}}/api/v1/nodes` — list nodes

---

## 53. Shippo API

**Service**: `shippo-api` · **Port**: 8052 · **Env**: `SHIPPO_API_URL`

Mock service mirroring Shippo API endpoints. See `shippo-api/shippo-api_postman_collection.json`*` for the runnable request collection.

### Endpoints

#### Endpoints

- `GET {{baseUrl}}/health` — health
- `POST {{baseUrl}}/addresses` — create address
- `GET {{baseUrl}}/addresses/addr-recv-01` — get address
- `POST {{baseUrl}}/shipments` — create shipment
- `GET {{baseUrl}}/shipments/ship-1001` — get shipment
- `GET {{baseUrl}}/shipments/ship-1001/rates` — list shipment rates
- `POST {{baseUrl}}/transactions` — buy label
- `GET {{baseUrl}}/transactions/txn-9001` — get transaction
- `GET {{baseUrl}}/tracks/USPS/9400111202555842761023` — track shipment

---

## 54. Docusign API

**Service**: `docusign-api` · **Port**: 8053 · **Env**: `DOCUSIGN_API_URL`

Mock service mirroring Docusign API endpoints. See `docusign-api/docusign-api_postman_collection.json`*` for the runnable request collection.

### Endpoints

#### Endpoints

- `GET {{baseUrl}}/health` — health
- `GET {{baseUrl}}/restapi/v2.1/accounts/{{accountId}}/envelopes?status=sent` — list envelopes
- `POST {{baseUrl}}/restapi/v2.1/accounts/{{accountId}}/envelopes` — create envelope
- `GET {{baseUrl}}/restapi/v2.1/accounts/{{accountId}}/envelopes/env-2001` — get envelope
- `PUT {{baseUrl}}/restapi/v2.1/accounts/{{accountId}}/envelopes/env-2001` — void envelope
- `GET {{baseUrl}}/restapi/v2.1/accounts/{{accountId}}/envelopes/env-2003/recipients` — list recipients
- `GET {{baseUrl}}/restapi/v2.1/accounts/{{accountId}}/envelopes/env-2001/documents` — list documents
- `GET {{baseUrl}}/restapi/v2.1/accounts/{{accountId}}/templates` — list templates

---

## 55. Calendly API

**Service**: `calendly-api` · **Port**: 8054 · **Env**: `CALENDLY_API_URL`

Mock service mirroring Calendly API endpoints. See `calendly-api/calendly-api_postman_collection.json`*` for the runnable request collection.

### Endpoints

#### Endpoints

- `GET {{baseUrl}}/health` — health
- `GET {{baseUrl}}/users/me` — get me
- `GET {{baseUrl}}/event_types?user=user-amelia-ortega` — list event types
- `GET {{baseUrl}}/event_types/et-discovery-30` — get event type
- `GET {{baseUrl}}/scheduled_events?user=user-amelia-ortega&status=active` — list scheduled events
- `GET {{baseUrl}}/scheduled_events/sev-1001` — get scheduled event
- `GET {{baseUrl}}/scheduled_events/sev-1001/invitees` — list invitees
- `POST {{baseUrl}}/scheduled_events` — book event
- `POST {{baseUrl}}/scheduled_events/sev-1002/cancellation` — cancel event

---

## 56. Typeform API

**Service**: `typeform-api` · **Port**: 8055 · **Env**: `TYPEFORM_API_URL`

Mock service mirroring Typeform API endpoints. See `typeform-api/typeform-api_postman_collection.json`*` for the runnable request collection.

### Endpoints

#### Endpoints

- `GET {{baseUrl}}/health` — health
- `GET {{baseUrl}}/forms` — list forms
- `POST {{baseUrl}}/forms` — create form
- `GET {{baseUrl}}/forms/frm-csat-01` — get form
- `PUT {{baseUrl}}/forms/frm-csat-01` — update form
- `DELETE {{baseUrl}}/forms/frm-event-03` — delete form
- `GET {{baseUrl}}/forms/frm-csat-01/responses` — list responses
- `GET {{baseUrl}}/forms/frm-csat-01/insights/summary` — insights summary

---

## 57. Mixpanel API

**Service**: `mixpanel-api` · **Port**: 8056 · **Env**: `MIXPANEL_API_URL`

Mock service mirroring Mixpanel API endpoints. See `mixpanel-api/mixpanel-api_postman_collection.json`*` for the runnable request collection.

### Endpoints

#### Endpoints

- `GET {{baseUrl}}/health` — health
- `POST {{baseUrl}}/track` — track event
- `GET {{baseUrl}}/api/2.0/events?event=App Open,Checkout&from_date=2025-05-01&to_date=2025-05-04` — events counts
- `GET {{baseUrl}}/api/2.0/funnels/list` — funnels list
- `GET {{baseUrl}}/api/2.0/funnels?funnel_id=7461001` — funnel
- `GET {{baseUrl}}/api/2.0/segmentation?event=App Open&from_date=2025-05-01&to_date=2025-05-04&on=country` — segmentation
- `GET {{baseUrl}}/api/2.0/engage?where=plan==paid` — engage profiles
- `GET {{baseUrl}}/api/2.0/engage?distinct_id=user-aria` — engage one profile

---

## 58. Discord API

**Service**: `discord-api` · **Port**: 8057 · **Env**: `DISCORD_API_URL`

Mock service mirroring Discord API endpoints. See `discord-api/discord-api_postman_collection.json`*` for the runnable request collection.

### Endpoints

#### Endpoints

- `GET {{baseUrl}}/health` — health
- `GET {{baseUrl}}/api/v10/users/@me` — get me
- `GET {{baseUrl}}/api/v10/users/@me/guilds` — my guilds
- `GET {{baseUrl}}/api/v10/guilds/900100200300400001` — get guild
- `GET {{baseUrl}}/api/v10/guilds/900100200300400001/channels` — guild channels
- `GET {{baseUrl}}/api/v10/guilds/900100200300400001/members?limit=10` — guild members
- `GET {{baseUrl}}/api/v10/guilds/900100200300400001/roles` — guild roles
- `GET {{baseUrl}}/api/v10/channels/800100200300400001` — get channel
- `GET {{baseUrl}}/api/v10/channels/800100200300400001/messages?limit=10` — channel messages
- `POST {{baseUrl}}/api/v10/channels/800100200300400001/messages` — create message

---

## 59. Reddit API

**Service**: `reddit-api` · **Port**: 8058 · **Env**: `REDDIT_API_URL`

Mock service mirroring Reddit API endpoints. See `reddit-api/reddit-api_postman_collection.json`*` for the runnable request collection.

### Endpoints

#### Endpoints

- `GET {{baseUrl}}/health` — health
- `GET {{baseUrl}}/r/programming/about` — subreddit about
- `GET {{baseUrl}}/r/programming/hot?limit=10` — subreddit hot
- `GET {{baseUrl}}/r/homelab/new?limit=10` — subreddit new
- `GET {{baseUrl}}/comments/t3_p001` — post comments
- `POST {{baseUrl}}/api/submit` — submit post
- `POST {{baseUrl}}/api/vote` — vote up
- `GET {{baseUrl}}/user/devkat/about` — user about

---

## 60. Tmdb API

**Service**: `tmdb-api` · **Port**: 8059 · **Env**: `TMDB_API_URL`

Mock service mirroring Tmdb API endpoints. See `tmdb-api/tmdb-api_postman_collection.json`*` for the runnable request collection.

### Endpoints

#### Endpoints

- `GET {{baseUrl}}/health` — health
- `GET {{baseUrl}}/3/search/movie?query=orbit` — search movie
- `GET {{baseUrl}}/3/movie/popular` — movie popular
- `GET {{baseUrl}}/3/movie/101` — get movie
- `GET {{baseUrl}}/3/movie/101/credits` — movie credits
- `GET {{baseUrl}}/3/tv/201` — get tv
- `GET {{baseUrl}}/3/genre/movie/list` — genre movie list
- `GET {{baseUrl}}/3/trending/all/week` — trending all week

---

## 61. Strava API

**Service**: `strava-api` · **Port**: 8060 · **Env**: `STRAVA_API_URL`

Mock service mirroring Strava API endpoints. See `strava-api/strava-api_postman_collection.json`*` for the runnable request collection.

### Endpoints

#### Endpoints

- `GET {{baseUrl}}/health` — health
- `GET {{baseUrl}}/api/v3/athlete` — get athlete
- `GET {{baseUrl}}/api/v3/athlete/activities?per_page=5` — list activities
- `GET {{baseUrl}}/api/v3/activities/9002` — get activity
- `PUT {{baseUrl}}/api/v3/activities/9002` — update activity
- `GET {{baseUrl}}/api/v3/activities/9002/kudos` — activity kudos
- `GET {{baseUrl}}/api/v3/segments/3302` — get segment
- `GET {{baseUrl}}/api/v3/athletes/4410022/stats` — athlete stats

---

## 62. Twitter API

**Service**: `twitter-api` · **Port**: 8061 · **Env**: `TWITTER_API_URL`

Mock service mirroring Twitter API endpoints. See `twitter-api/twitter-api_postman_collection.json`*` for the runnable request collection.

### Endpoints

#### Endpoints

- `GET {{baseUrl}}/health` — health
- `GET {{baseUrl}}/2/users/me` — get me
- `GET {{baseUrl}}/2/users/2002` — get user
- `GET {{baseUrl}}/2/users/by/username/orbit_labs` — get user by username
- `GET {{baseUrl}}/2/users/2001/tweets?max_results=5` — get user tweets
- `GET {{baseUrl}}/2/users/2001/followers` — get followers
- `GET {{baseUrl}}/2/tweets?max_results=5` — list tweets
- `GET {{baseUrl}}/2/tweets/3002` — get tweet
- `GET {{baseUrl}}/2/tweets/search/recent?query=SLO` — search recent
- `POST {{baseUrl}}/2/tweets` — create tweet
- `DELETE {{baseUrl}}/2/tweets/3008` — delete tweet
- `POST {{baseUrl}}/2/users/2001/likes` — like tweet
- `POST {{baseUrl}}/2/users/2001/retweets` — retweet

---

## 63. Linkedin API

**Service**: `linkedin-api` · **Port**: 8062 · **Env**: `LINKEDIN_API_URL`

Mock service mirroring Linkedin API endpoints. See `linkedin-api/linkedin-api_postman_collection.json`*` for the runnable request collection.

### Endpoints

#### Endpoints

- `GET {{baseUrl}}/health` — health
- `GET {{baseUrl}}/v2/me` — get me
- `GET {{baseUrl}}/v2/connections?count=10` — list connections
- `GET {{baseUrl}}/v2/posts` — list posts
- `GET {{baseUrl}}/v2/posts?author_id=urn:li:person:amelia-ortega` — list posts by author
- `GET {{baseUrl}}/v2/posts/6003` — get post
- `POST {{baseUrl}}/v2/posts` — create post
- `GET {{baseUrl}}/v2/organizations/5001` — get organization
- `GET {{baseUrl}}/v2/jobs?keywords=backend&location=Remote` — search jobs
- `GET {{baseUrl}}/v2/jobs/7001` — get job

---

## 64. Telegram API

**Service**: `telegram-api` · **Port**: 8063 · **Env**: `TELEGRAM_API_URL`

Mock service mirroring Telegram API endpoints. See `telegram-api/telegram-api_postman_collection.json`*` for the runnable request collection.

### Endpoints

#### Endpoints

- `GET {{baseUrl}}/health` — health
- `GET {{baseUrl}}/bot/getMe` — getMe
- `GET {{baseUrl}}/bot/getUpdates?limit=10` — getUpdates
- `GET {{baseUrl}}/bot/getChat?chat_id=-200500` — getChat
- `GET {{baseUrl}}/bot/getChatMember?chat_id=-200500&user_id=9002` — getChatMember
- `POST {{baseUrl}}/bot/sendMessage` — sendMessage
- `POST {{baseUrl}}/bot/sendPhoto` — sendPhoto
- `POST {{baseUrl}}/bot/editMessageText` — editMessageText
- `POST {{baseUrl}}/bot/deleteMessage` — deleteMessage

---

## 65. Twitch API

**Service**: `twitch-api` · **Port**: 8064 · **Env**: `TWITCH_API_URL`

Mock service mirroring Twitch API endpoints. See `twitch-api/twitch-api_postman_collection.json`*` for the runnable request collection.

### Endpoints

#### Endpoints

- `GET {{baseUrl}}/health` — health
- `GET {{baseUrl}}/helix/users?login=pixelpaladin` — get users
- `GET {{baseUrl}}/helix/streams` — get streams (live)
- `GET {{baseUrl}}/helix/streams?user_login=sprintqueen` — get streams by login
- `GET {{baseUrl}}/helix/channels?broadcaster_id=40001` — get channel
- `GET {{baseUrl}}/helix/channels/followers?broadcaster_id=40003` — get channel followers
- `GET {{baseUrl}}/helix/games/top?first=5` — get top games
- `GET {{baseUrl}}/helix/games?name=Elden Ring` — get game by name
- `GET {{baseUrl}}/helix/clips?broadcaster_id=40001` — get clips by broadcaster

---

## 66. Wordpress API

**Service**: `wordpress-api` · **Port**: 8065 · **Env**: `WORDPRESS_API_URL`

Mock service mirroring Wordpress API endpoints. See `wordpress-api/wordpress-api_postman_collection.json`*` for the runnable request collection.

### Endpoints

#### Endpoints

- `GET {{baseUrl}}/health` — health
- `GET {{baseUrl}}/wp-json/wp/v2/posts?per_page=5` — list posts
- `GET {{baseUrl}}/wp-json/wp/v2/posts?categories=11` — list posts by category
- `GET {{baseUrl}}/wp-json/wp/v2/posts/101` — get post
- `POST {{baseUrl}}/wp-json/wp/v2/posts` — create post
- `PUT {{baseUrl}}/wp-json/wp/v2/posts/106` — update post
- `DELETE {{baseUrl}}/wp-json/wp/v2/posts/108` — delete post
- `GET {{baseUrl}}/wp-json/wp/v2/pages` — list pages
- `GET {{baseUrl}}/wp-json/wp/v2/categories` — list categories
- `GET {{baseUrl}}/wp-json/wp/v2/tags` — list tags
- `GET {{baseUrl}}/wp-json/wp/v2/comments?post=101` — list comments for post
- `POST {{baseUrl}}/wp-json/wp/v2/comments` — create comment
- `GET {{baseUrl}}/wp-json/wp/v2/media` — list media
- `GET {{baseUrl}}/wp-json/wp/v2/users` — list users

---

## 67. Contentful API

**Service**: `contentful-api` · **Port**: 8066 · **Env**: `CONTENTFUL_API_URL`

Mock service mirroring Contentful API endpoints. See `contentful-api/contentful-api_postman_collection.json`*` for the runnable request collection.

### Endpoints

#### Endpoints

- `GET {{baseUrl}}/health` — health
- `GET {{baseUrl}}/spaces/space-orbit-cms` — get space
- `GET {{baseUrl}}/spaces/space-orbit-cms/environments/master/content_types` — list content types
- `GET {{baseUrl}}/spaces/space-orbit-cms/environments/master/content_types/blogPost` — get content type
- `GET {{baseUrl}}/spaces/space-orbit-cms/environments/master/entries?content_type=blogPost&limit=10` — list entries
- `GET {{baseUrl}}/spaces/space-orbit-cms/environments/master/entries?content_type=blogPost&fields.slug=getting-started` — list entries by field
- `GET {{baseUrl}}/spaces/space-orbit-cms/environments/master/entries/post-getting-started` — get entry
- `POST {{baseUrl}}/spaces/space-orbit-cms/environments/master/entries` — create entry
- `PUT {{baseUrl}}/spaces/space-orbit-cms/environments/master/entries/post-draft-webhooks` — update entry
- `DELETE {{baseUrl}}/spaces/space-orbit-cms/environments/master/entries/post-content-modeling` — delete entry
- `GET {{baseUrl}}/spaces/space-orbit-cms/environments/master/assets` — list assets
- `GET {{baseUrl}}/spaces/space-orbit-cms/environments/master/assets/asset-hero-1` — get asset

---

## 68. Algolia API

**Service**: `algolia-api` · **Port**: 8067 · **Env**: `ALGOLIA_API_URL`

Mock service mirroring Algolia API endpoints. See `algolia-api/algolia-api_postman_collection.json`*` for the runnable request collection.

### Endpoints

#### Endpoints

- `GET {{baseUrl}}/health` — health
- `GET {{baseUrl}}/1/indexes` — list indexes
- `POST {{baseUrl}}/1/indexes/products/query` — query products
- `POST {{baseUrl}}/1/indexes/products/query` — query products with filter
- `POST {{baseUrl}}/1/indexes/docs/query` — query docs
- `GET {{baseUrl}}/1/indexes/products/prod-001` — get object
- `GET {{baseUrl}}/1/indexes/products/settings` — get settings
- `POST {{baseUrl}}/1/indexes/products` — add object
- `PUT {{baseUrl}}/1/indexes/products/prod-004` — update object
- `DELETE {{baseUrl}}/1/indexes/products/prod-008` — delete object

---

## 69. Google Analytics API

**Service**: `google-analytics-api` · **Port**: 8068 · **Env**: `GOOGLE_ANALYTICS_API_URL`

Mock service mirroring Google Analytics API endpoints. See `google-analytics-api/google-analytics-api_postman_collection.json`*` for the runnable request collection.

### Endpoints

#### Endpoints

- `GET {{baseUrl}}/health` — health
- `GET {{baseUrl}}/v1beta/properties/412233445` — get property
- `GET {{baseUrl}}/v1beta/properties/412233445/metadata` — get metadata
- `POST {{baseUrl}}/v1beta/properties/412233445:runReport` — run report by country
- `POST {{baseUrl}}/v1beta/properties/412233445:runReport` — run report by date and device
- `POST {{baseUrl}}/v1beta/properties/412233445:runRealtimeReport` — run realtime report
- `POST {{baseUrl}}/v1beta/properties/412233445:batchRunReports` — batch run reports

---

## 70. Intercom API

**Service**: `intercom-api` · **Port**: 8070 · **Env**: `INTERCOM_API_URL`

Mock service mirroring Intercom API endpoints. See `intercom-api/intercom-api_postman_collection.json`*` for the runnable request collection.

### Endpoints

#### Endpoints

- `GET {{baseUrl}}/health` — health
- `GET {{baseUrl}}/contacts?role=user` — list contacts
- `GET {{baseUrl}}/contacts/contact-mara` — get contact
- `POST {{baseUrl}}/contacts` — create contact
- `GET {{baseUrl}}/conversations?state=open` — list conversations
- `GET {{baseUrl}}/conversations/conv-1001` — get conversation
- `POST {{baseUrl}}/conversations` — create conversation
- `POST {{baseUrl}}/conversations/conv-1001/reply` — reply to conversation
- `POST {{baseUrl}}/conversations/conv-1003/parts` — assign conversation
- `POST {{baseUrl}}/conversations/conv-1001/parts` — close conversation
- `GET {{baseUrl}}/companies` — list companies
- `GET {{baseUrl}}/companies/company-brightpath` — get company

---

## 71. Servicenow API

**Service**: `servicenow-api` · **Port**: 8071 · **Env**: `SERVICENOW_API_URL`

Mock service mirroring Servicenow API endpoints. See `servicenow-api/servicenow-api_postman_collection.json`*` for the runnable request collection.

### Endpoints

#### Endpoints

- `GET {{baseUrl}}/health` — health
- `GET {{baseUrl}}/api/now/table/incident` — list incidents
- `GET {{baseUrl}}/api/now/table/incident?sysparm_query=state=2^priority=1&sysparm_limit=5` — list incidents filtered
- `GET {{baseUrl}}/api/now/table/incident/inc-0001001` — get incident
- `POST {{baseUrl}}/api/now/table/incident` — create incident
- `PATCH {{baseUrl}}/api/now/table/incident/inc-0001003` — update incident
- `GET {{baseUrl}}/api/now/table/change_request` — list change requests
- `GET {{baseUrl}}/api/now/table/change_request/chg-0002001` — get change request
- `GET {{baseUrl}}/api/now/table/problem` — list problems
- `GET {{baseUrl}}/api/now/table/problem/prb-0003001` — get problem
- `GET {{baseUrl}}/api/now/table/sys_user` — list users
- `GET {{baseUrl}}/api/now/table/sys_user/usr-amelia` — get user

---

## 72. Bamboohr API

**Service**: `bamboohr-api` · **Port**: 8072 · **Env**: `BAMBOOHR_API_URL`

Mock service mirroring Bamboohr API endpoints. See `bamboohr-api/bamboohr-api_postman_collection.json`*` for the runnable request collection.

### Endpoints

#### Endpoints

- `GET {{baseUrl}}/health` — health
- `GET {{baseUrl}}/api/gateway.php/{{company}}/v1/company` — get company
- `GET {{baseUrl}}/api/gateway.php/{{company}}/v1/employees/directory` — employees directory
- `GET {{baseUrl}}/api/gateway.php/{{company}}/v1/employees/emp-102` — get employee
- `POST {{baseUrl}}/api/gateway.php/{{company}}/v1/employees` — create employee
- `GET {{baseUrl}}/api/gateway.php/{{company}}/v1/time_off/requests?status=requested` — list time off requests
- `POST {{baseUrl}}/api/gateway.php/{{company}}/v1/time_off/requests` — create time off request
- `PUT {{baseUrl}}/api/gateway.php/{{company}}/v1/time_off/requests/tor-5003/status` — approve time off request
- `GET {{baseUrl}}/api/gateway.php/{{company}}/v1/time_off/whos_out` — whos out
- `GET {{baseUrl}}/api/gateway.php/{{company}}/v1/reports/1` — get report

---

## 73. Greenhouse API

**Service**: `greenhouse-api` · **Port**: 8073 · **Env**: `GREENHOUSE_API_URL`

Mock service mirroring Greenhouse API endpoints. See `greenhouse-api/greenhouse-api_postman_collection.json`*` for the runnable request collection.

### Endpoints

#### Endpoints

- `GET {{baseUrl}}/health` — health
- `GET {{baseUrl}}/v1/candidates` — list candidates
- `GET {{baseUrl}}/v1/candidates/cand-7001` — get candidate
- `POST {{baseUrl}}/v1/candidates` — create candidate
- `GET {{baseUrl}}/v1/jobs?status=open` — list jobs open
- `GET {{baseUrl}}/v1/jobs/job-3001` — get job
- `GET {{baseUrl}}/v1/applications?job_id=job-3001` — list applications
- `GET {{baseUrl}}/v1/applications/app-4001` — get application
- `POST {{baseUrl}}/v1/applications/app-4001/advance` — advance application
- `POST {{baseUrl}}/v1/applications/app-4007/reject` — reject application
- `GET {{baseUrl}}/v1/scorecards?application_id=app-4002` — list scorecards

---

## 74. Gusto API

**Service**: `gusto-api` · **Port**: 8074 · **Env**: `GUSTO_API_URL`

Mock service mirroring Gusto API endpoints. See `gusto-api/gusto-api_postman_collection.json`*` for the runnable request collection.

### Endpoints

#### Endpoints

- `GET {{baseUrl}}/health` — health
- `GET {{baseUrl}}/v1/companies/{{companyId}}` — get company
- `GET {{baseUrl}}/v1/companies/{{companyId}}/employees` — list company employees
- `GET {{baseUrl}}/v1/employees/gemp-202` — get employee
- `GET {{baseUrl}}/v1/companies/{{companyId}}/payrolls` — list company payrolls
- `GET {{baseUrl}}/v1/companies/{{companyId}}/payrolls?processed=false` — list unprocessed payrolls
- `GET {{baseUrl}}/v1/payrolls/pay-401` — get payroll
- `POST {{baseUrl}}/v1/companies/{{companyId}}/payrolls` — create payroll
- `PUT {{baseUrl}}/v1/payrolls/pay-404/submit` — submit payroll
- `GET {{baseUrl}}/v1/companies/{{companyId}}/contractors` — list company contractors

---

## 75. Ticketmaster API

**Service**: `ticketmaster-api` · **Port**: 8075 · **Env**: `TICKETMASTER_API_URL`

Mock service mirroring Ticketmaster API endpoints. See `ticketmaster-api/ticketmaster-api_postman_collection.json`*` for the runnable request collection.

### Endpoints

#### Endpoints

- `GET {{baseUrl}}/health` — health
- `GET {{baseUrl}}/discovery/v2/events` — search events
- `GET {{baseUrl}}/discovery/v2/events?keyword=Aria` — search events by keyword
- `GET {{baseUrl}}/discovery/v2/events?city=New York&classificationName=Music` — search events by city + classification
- `GET {{baseUrl}}/discovery/v2/events?startDateTime=2026-09-01T00:00:00Z` — search events by startDateTime
- `GET {{baseUrl}}/discovery/v2/events/evt-1001` — get event
- `GET {{baseUrl}}/discovery/v2/venues?keyword=Arena` — search venues
- `GET {{baseUrl}}/discovery/v2/venues/ven-001` — get venue
- `GET {{baseUrl}}/discovery/v2/attractions?keyword=Echoes` — search attractions
- `GET {{baseUrl}}/discovery/v2/attractions/att-001` — get attraction
- `GET {{baseUrl}}/discovery/v2/classifications` — list classifications

---

## 76. Amadeus API

**Service**: `amadeus-api` · **Port**: 8076 · **Env**: `AMADEUS_API_URL`

Mock service mirroring Amadeus API endpoints. See `amadeus-api/amadeus-api_postman_collection.json`*` for the runnable request collection.

### Endpoints

#### Endpoints

- `GET {{baseUrl}}/health` — health
- `GET {{baseUrl}}/v2/shopping/flight-offers?originLocationCode=JFK&destinationLocationCode=LHR&departureDate=2026-06-15&adults=2` — flight offers search
- `GET {{baseUrl}}/v2/shopping/flight-offers?originLocationCode=LAX&destinationLocationCode=NRT&adults=1` — flight offers search (no date)
- `POST {{baseUrl}}/v1/shopping/flight-offers/pricing` — price flight offer
- `GET {{baseUrl}}/v1/reference-data/locations?keyword=London&subType=AIRPORT,CITY` — search locations
- `GET {{baseUrl}}/v1/reference-data/locations/AJFK` — get location
- `GET {{baseUrl}}/v1/reference-data/airlines?airlineCodes=BA,AF` — get airlines

---

## 77. Nasa API

**Service**: `nasa-api` · **Port**: 8077 · **Env**: `NASA_API_URL`

Mock service mirroring Nasa API endpoints. See `nasa-api/nasa-api_postman_collection.json`*` for the runnable request collection.

### Endpoints

#### Endpoints

- `GET {{baseUrl}}/health` — health
- `GET {{baseUrl}}/planetary/apod` — apod latest
- `GET {{baseUrl}}/planetary/apod?date=2026-05-24` — apod by date
- `GET {{baseUrl}}/planetary/apod?start_date=2026-05-20&end_date=2026-05-23` — apod range
- `GET {{baseUrl}}/mars-photos/api/v1/rovers/curiosity/photos?sol=4100&camera=MAST` — rover photos
- `GET {{baseUrl}}/mars-photos/api/v1/rovers/perseverance` — rover manifest
- `GET {{baseUrl}}/neo/rest/v1/feed?start_date=2026-05-20&end_date=2026-05-21` — neo feed
- `GET {{baseUrl}}/neo/rest/v1/neo/3726710` — neo by id
- `GET {{baseUrl}}/EPIC/api/natural` — epic natural

---

## 78. Openlibrary API

**Service**: `openlibrary-api` · **Port**: 8078 · **Env**: `OPENLIBRARY_API_URL`

Mock service mirroring Openlibrary API endpoints. See `openlibrary-api/openlibrary-api_postman_collection.json`*` for the runnable request collection.

### Endpoints

#### Endpoints

- `GET {{baseUrl}}/health` — health
- `GET {{baseUrl}}/search.json?q=foundation` — search by q
- `GET {{baseUrl}}/search.json?author=Le%20Guin` — search by author
- `GET {{baseUrl}}/search.json?title=Dune` — search by title
- `GET {{baseUrl}}/works/OL893415W.json` — get work
- `GET {{baseUrl}}/works/OL27448W/editions.json` — get work editions
- `GET {{baseUrl}}/authors/OL26320A.json` — get author
- `GET {{baseUrl}}/authors/OL34184A/works.json` — get author works
- `GET {{baseUrl}}/subjects/science_fiction.json` — get subject
- `GET {{baseUrl}}/isbn/9780441013593.json` — get isbn

---

## 79. Figma API

**Service**: `figma-api` · **Port**: 8079 · **Env**: `FIGMA_API_URL`

Mock service mirroring Figma API endpoints. See `figma-api/figma-api_postman_collection.json`*` for the runnable request collection.

### Endpoints

#### Endpoints

- `GET {{baseUrl}}/health` — health
- `GET {{baseUrl}}/v1/me` — get me
- `GET {{baseUrl}}/v1/teams/team-501/projects` — team projects
- `GET {{baseUrl}}/v1/projects/proj-201/files` — project files
- `GET {{baseUrl}}/v1/files/FK001abcdefg` — get file
- `GET {{baseUrl}}/v1/files/FK001abcdefg/nodes?ids=5:10,5:20` — get file nodes
- `GET {{baseUrl}}/v1/files/FK001abcdefg/comments` — get comments
- `POST {{baseUrl}}/v1/files/FK001abcdefg/comments` — create comment
- `GET {{baseUrl}}/v1/files/FK004vwxyz12/components` — get components

---

## 80. Monday API

**Service**: `monday-api` · **Port**: 8080 · **Env**: `MONDAY_API_URL`

Mock service mirroring Monday API endpoints. See `monday-api/monday-api_postman_collection.json`*` for the runnable request collection.

### Endpoints

#### Endpoints

- `GET {{baseUrl}}/health` — health
- `GET {{baseUrl}}/v2/workspaces` — list workspaces
- `GET {{baseUrl}}/v2/boards?workspace_id=ws-1` — list boards
- `GET {{baseUrl}}/v2/boards/board-101` — get board
- `GET {{baseUrl}}/v2/boards/board-101/items` — board items
- `GET {{baseUrl}}/v2/items?board_id=board-101&group_id=grp-todo` — list items
- `GET {{baseUrl}}/v2/items/item-1001` — get item
- `POST {{baseUrl}}/v2/items` — create item
- `PUT {{baseUrl}}/v2/items/item-1002` — update item (change status)
- `PUT {{baseUrl}}/v2/items/item-1002` — update item (move group)
- `DELETE {{baseUrl}}/v2/items/item-1004` — delete item
- `GET {{baseUrl}}/v2/users` — list users

---

## 81. Mailchimp API

**Service**: `mailchimp-api` · **Port**: 8081 · **Env**: `MAILCHIMP_API_URL`

Mock service mirroring Mailchimp API endpoints. See `mailchimp-api/mailchimp-api_postman_collection.json`*` for the runnable request collection.

### Endpoints

#### Endpoints

- `GET {{baseUrl}}/health` — health
- `GET {{baseUrl}}/3.0/lists` — list lists
- `GET {{baseUrl}}/3.0/lists/list-newsletter` — get list
- `GET {{baseUrl}}/3.0/lists/list-newsletter/members?status=subscribed` — list members
- `POST {{baseUrl}}/3.0/lists/list-newsletter/members` — create member
- `GET {{baseUrl}}/3.0/lists/list-newsletter/members/mara@brightpath.io` — get member
- `PATCH {{baseUrl}}/3.0/lists/list-newsletter/members/tomas@brightpath.io` — update member
- `GET {{baseUrl}}/3.0/campaigns?status=sent` — list campaigns
- `POST {{baseUrl}}/3.0/campaigns` — create campaign
- `GET {{baseUrl}}/3.0/campaigns/camp-sep-news` — get campaign
- `POST {{baseUrl}}/3.0/campaigns/camp-nov-draft/actions/send` — send campaign
- `GET {{baseUrl}}/3.0/reports/camp-oct-news` — get report

---

## 82. Dropbox API

**Service**: `dropbox-api` · **Port**: 8082 · **Env**: `DROPBOX_API_URL`

Mock service mirroring Dropbox API endpoints. See `dropbox-api/dropbox-api_postman_collection.json`*` for the runnable request collection.

### Endpoints

#### Endpoints

- `GET {{baseUrl}}/health` — health
- `POST {{baseUrl}}/2/users/get_current_account` — get current account
- `POST {{baseUrl}}/2/files/list_folder` — list folder root
- `POST {{baseUrl}}/2/files/list_folder` — list folder documents
- `POST {{baseUrl}}/2/files/get_metadata` — get metadata
- `POST {{baseUrl}}/2/files/search_v2` — search v2
- `POST {{baseUrl}}/2/sharing/list_shared_links` — list shared links

---

## 83. Box API

**Service**: `box-api` · **Port**: 8083 · **Env**: `BOX_API_URL`

Mock service mirroring Box API endpoints. See `box-api/box-api_postman_collection.json`*` for the runnable request collection.

### Endpoints

#### Endpoints

- `GET {{baseUrl}}/health` — health
- `GET {{baseUrl}}/2.0/users/me` — current user
- `GET {{baseUrl}}/2.0/folders/0` — get root folder
- `GET {{baseUrl}}/2.0/folders/0/items?limit=10&offset=0` — get folder items
- `GET {{baseUrl}}/2.0/folders/160001/items` — get marketing folder items
- `GET {{baseUrl}}/2.0/files/500001` — get file
- `GET {{baseUrl}}/2.0/search?query=campaign&type=file` — search

---

## 84. Bigcommerce API

**Service**: `bigcommerce-api` · **Port**: 8084 · **Env**: `BIGCOMMERCE_API_URL`

Mock service mirroring Bigcommerce API endpoints. See `bigcommerce-api/bigcommerce-api_postman_collection.json`*` for the runnable request collection.

### Endpoints

#### Endpoints

- `GET {{baseUrl}}/health` — health
- `GET {{baseUrl}}/v3/catalog/products?limit=5&page=1` — list products
- `GET {{baseUrl}}/v3/catalog/products?name=wireless` — filter products by name
- `GET {{baseUrl}}/v3/catalog/products/101` — get product
- `GET {{baseUrl}}/v2/orders?customer_id=1001` — list orders
- `GET {{baseUrl}}/v2/orders/2001` — get order
- `POST {{baseUrl}}/v2/orders` — create order
- `GET {{baseUrl}}/v3/customers?email=olivia` — list customers

---

## 85. Woocommerce API

**Service**: `woocommerce-api` · **Port**: 8085 · **Env**: `WOOCOMMERCE_API_URL`

Mock service mirroring Woocommerce API endpoints. See `woocommerce-api/woocommerce-api_postman_collection.json`*` for the runnable request collection.

### Endpoints

#### Endpoints

- `GET {{baseUrl}}/health` — health
- `GET {{baseUrl}}/wp-json/wc/v3/products?per_page=5&page=1` — list products
- `GET {{baseUrl}}/wp-json/wc/v3/products?search=mug` — search products
- `GET {{baseUrl}}/wp-json/wc/v3/products/201` — get product
- `GET {{baseUrl}}/wp-json/wc/v3/orders?customer=301` — list orders
- `GET {{baseUrl}}/wp-json/wc/v3/orders/401` — get order
- `POST {{baseUrl}}/wp-json/wc/v3/orders` — create order
- `GET {{baseUrl}}/wp-json/wc/v3/customers?email=emma` — list customers

---

## 86. Microsoft Teams API

**Service**: `microsoft-teams-api` · **Port**: 8086 · **Env**: `MICROSOFT_TEAMS_API_URL`

Mock service mirroring Microsoft Teams API endpoints. See `microsoft-teams-api/microsoft-teams-api_postman_collection.json`*` for the runnable request collection.

### Endpoints

#### Endpoints

- `GET {{baseUrl}}/health` — health
- `GET {{baseUrl}}/v1.0/me/joinedTeams` — joined teams
- `GET {{baseUrl}}/v1.0/teams/19:team-eng0001@thread.tacv2` — get team
- `GET {{baseUrl}}/v1.0/teams/19:team-eng0001@thread.tacv2/channels` — list channels
- `GET {{baseUrl}}/v1.0/teams/19:team-eng0001@thread.tacv2/channels/19:chan-eng-gen01@thread.tacv2/messages` — list channel messages
- `POST {{baseUrl}}/v1.0/teams/19:team-eng0001@thread.tacv2/channels/19:chan-eng-gen01@thread.tacv2/messages` — send channel message

---

## 87. Outlook API

**Service**: `outlook-api` · **Port**: 8087 · **Env**: `OUTLOOK_API_URL`

Mock service mirroring Outlook API endpoints. See `outlook-api/outlook-api_postman_collection.json`*` for the runnable request collection.

### Endpoints

#### Endpoints

- `GET {{baseUrl}}/health` — health
- `GET {{baseUrl}}/v1.0/me/messages` — list messages
- `GET {{baseUrl}}/v1.0/me/messages?isRead=false` — list unread messages
- `GET {{baseUrl}}/v1.0/me/messages/AAMkAGmsg0000001` — get message
- `POST {{baseUrl}}/v1.0/me/sendMail` — send mail
- `GET {{baseUrl}}/v1.0/me/events` — list events
- `GET {{baseUrl}}/v1.0/me/contacts` — list contacts

---

## 88. Xero API

**Service**: `xero-api` · **Port**: 8088 · **Env**: `XERO_API_URL`

Mock service mirroring Xero API endpoints. See `xero-api/xero-api_postman_collection.json`*` for the runnable request collection.

### Endpoints

#### Endpoints

- `GET {{baseUrl}}/health` — health
- `GET {{baseUrl}}/api.xro/2.0/Invoices` — list invoices
- `GET {{baseUrl}}/api.xro/2.0/Invoices?Status=AUTHORISED` — list authorised invoices
- `GET {{baseUrl}}/api.xro/2.0/Invoices/i0000001-0000-0000-0000-000000000001` — get invoice
- `POST {{baseUrl}}/api.xro/2.0/Invoices` — create invoice
- `GET {{baseUrl}}/api.xro/2.0/Contacts` — list contacts
- `GET {{baseUrl}}/api.xro/2.0/Accounts` — list accounts

---

## 89. Klaviyo API

**Service**: `klaviyo-api` · **Port**: 8089 · **Env**: `KLAVIYO_API_URL`

Mock service mirroring Klaviyo API endpoints. See `klaviyo-api/klaviyo-api_postman_collection.json`*` for the runnable request collection.

### Endpoints

#### Endpoints

- `GET {{baseUrl}}/health` — health
- `GET {{baseUrl}}/api/profiles` — list profiles
- `GET {{baseUrl}}/api/profiles?email=jane.doe@example.com` — filter profiles by email
- `GET {{baseUrl}}/api/profiles/01HZPROF000000000000000001` — get profile
- `POST {{baseUrl}}/api/profiles` — create profile
- `GET {{baseUrl}}/api/lists` — list lists
- `GET {{baseUrl}}/api/campaigns` — list campaigns
- `GET {{baseUrl}}/api/campaigns?status=Sent&channel=email` — list sent email campaigns

---

## 90. Segment API

**Service**: `segment-api` · **Port**: 8090 · **Env**: `SEGMENT_API_URL`

Mock service mirroring Segment API endpoints. See `segment-api/segment-api_postman_collection.json`*` for the runnable request collection.

### Endpoints

#### Endpoints

- `GET {{baseUrl}}/health` — health
- `POST {{baseUrl}}/v1/track` — track
- `POST {{baseUrl}}/v1/identify` — identify
- `POST {{baseUrl}}/v1/page` — page
- `POST {{baseUrl}}/v1/batch` — batch
- `GET {{baseUrl}}/v1/events` — events
- `GET {{baseUrl}}/v1/events?type=track&userId=user_1001` — events by type
- `GET {{baseUrl}}/v1/sources` — sources
- `GET {{baseUrl}}/v1/destinations` — destinations

---

## 91. Amplitude API

**Service**: `amplitude-api` · **Port**: 8091 · **Env**: `AMPLITUDE_API_URL`

Mock service mirroring Amplitude API endpoints. See `amplitude-api/amplitude-api_postman_collection.json`*` for the runnable request collection.

### Endpoints

#### Endpoints

- `GET {{baseUrl}}/health` — health
- `POST {{baseUrl}}/2/httpapi` — httpapi upload
- `GET {{baseUrl}}/api/2/events/segmentation?e=purchase&start=2026-05-02&end=2026-05-06` — segmentation
- `GET {{baseUrl}}/api/2/events/segmentation` — segmentation all
- `GET {{baseUrl}}/api/2/useractivity?user=user_2001` — user activity

---

## 92. Posthog API

**Service**: `posthog-api` · **Port**: 8092 · **Env**: `POSTHOG_API_URL`

Mock service mirroring Posthog API endpoints. See `posthog-api/posthog-api_postman_collection.json`*` for the runnable request collection.

### Endpoints

#### Endpoints

- `GET {{baseUrl}}/health` — health
- `POST {{baseUrl}}/capture` — capture
- `POST {{baseUrl}}/decide` — decide
- `GET {{baseUrl}}/api/projects/1/events` — events
- `GET {{baseUrl}}/api/projects/1/events?event=$pageview&distinct_id=user_3001` — events filtered
- `GET {{baseUrl}}/api/projects/1/feature_flags` — feature flags
- `GET {{baseUrl}}/api/projects/1/persons` — persons

---

## 93. Freshdesk API

**Service**: `freshdesk-api` · **Port**: 8093 · **Env**: `FRESHDESK_API_URL`

Mock service mirroring Freshdesk API endpoints. See `freshdesk-api/freshdesk-api_postman_collection.json`*` for the runnable request collection.

### Endpoints

#### Endpoints

- `GET {{baseUrl}}/health` — health
- `GET {{baseUrl}}/api/v2/tickets` — list tickets
- `GET {{baseUrl}}/api/v2/tickets?status=2&priority=2` — list tickets filtered
- `GET {{baseUrl}}/api/v2/tickets/70001` — get ticket
- `POST {{baseUrl}}/api/v2/tickets` — create ticket
- `PUT {{baseUrl}}/api/v2/tickets/70001` — update ticket
- `GET {{baseUrl}}/api/v2/contacts` — list contacts
- `GET {{baseUrl}}/api/v2/agents` — list agents

---

## 94. Mailgun API

**Service**: `mailgun-api` · **Port**: 8094 · **Env**: `MAILGUN_API_URL`

Mock service mirroring Mailgun API endpoints. See `mailgun-api/mailgun-api_postman_collection.json`*` for the runnable request collection.

### Endpoints

#### Endpoints

- `GET {{baseUrl}}/health` — health
- `POST {{baseUrl}}/v3/sandbox.mailgun.org/messages` — send message
- `GET {{baseUrl}}/v3/sandbox.mailgun.org/events` — events
- `GET {{baseUrl}}/v3/sandbox.mailgun.org/events?event=delivered` — events by type
- `GET {{baseUrl}}/v3/sandbox.mailgun.org/stats/total` — stats total
- `GET {{baseUrl}}/v3/lists/newsletter@sandbox.mailgun.org/members` — list members
- `GET {{baseUrl}}/v3/lists/newsletter@sandbox.mailgun.org/members?subscribed=true` — list members subscribed

---

## 95. Fedex API

**Service**: `fedex-api` · **Port**: 8095 · **Env**: `FEDEX_API_URL`

Mock service mirroring Fedex API endpoints. See `fedex-api/fedex-api_postman_collection.json`*` for the runnable request collection.

### Endpoints

#### Endpoints

- `GET {{baseUrl}}/health` — health
- `POST {{baseUrl}}/rate/v1/rates/quotes` — rate quote
- `POST {{baseUrl}}/ship/v1/shipments` — create shipment
- `POST {{baseUrl}}/track/v1/trackingnumbers` — track

---

## 96. Ups API

**Service**: `ups-api` · **Port**: 8096 · **Env**: `UPS_API_URL`

Mock service mirroring Ups API endpoints. See `ups-api/ups-api_postman_collection.json`*` for the runnable request collection.

### Endpoints

#### Endpoints

- `GET {{baseUrl}}/health` — health
- `POST {{baseUrl}}/api/rating/v1/Rate` — rate
- `POST {{baseUrl}}/api/shipments/v1/ship` — ship
- `GET {{baseUrl}}/api/track/v1/details/1Z999AA10123456784` — track

---

## 97. Binance API

**Service**: `binance-api` · **Port**: 8097 · **Env**: `BINANCE_API_URL`

Mock service mirroring Binance API endpoints. See `binance-api/binance-api_postman_collection.json`*` for the runnable request collection.

### Endpoints

#### Endpoints

- `GET {{baseUrl}}/health` — health
- `GET {{baseUrl}}/api/v3/ticker/price` — ticker price all
- `GET {{baseUrl}}/api/v3/ticker/price?symbol=BTCUSDT` — ticker price symbol
- `GET {{baseUrl}}/api/v3/ticker/24hr?symbol=ETHUSDT` — ticker 24hr
- `GET {{baseUrl}}/api/v3/depth?symbol=BTCUSDT&limit=5` — depth
- `GET {{baseUrl}}/api/v3/klines?symbol=BTCUSDT&interval=1h` — klines
- `GET {{baseUrl}}/api/v3/account` — account

---

## 98. Kraken API

**Service**: `kraken-api` · **Port**: 8098 · **Env**: `KRAKEN_API_URL`

Mock service mirroring Kraken API endpoints. See `kraken-api/kraken-api_postman_collection.json`*` for the runnable request collection.

### Endpoints

#### Endpoints

- `GET {{baseUrl}}/health` — health
- `GET {{baseUrl}}/0/public/Ticker?pair=XBTUSD` — ticker single
- `GET {{baseUrl}}/0/public/Ticker?pair=XBTUSD,ETHUSD` — ticker multi
- `GET {{baseUrl}}/0/public/Ticker` — ticker all
- `GET {{baseUrl}}/0/public/OHLC?pair=XBTUSD&interval=60` — ohlc
- `GET {{baseUrl}}/0/public/AssetPairs` — asset pairs all
- `GET {{baseUrl}}/0/public/AssetPairs?pair=ETHUSD` — asset pairs filter
- `GET {{baseUrl}}/0/public/Assets` — assets all
- `GET {{baseUrl}}/0/public/Assets?asset=XBT,ETH` — assets filter
- `POST {{baseUrl}}/0/private/Balance` — balance

---

## 99. Vimeo API

**Service**: `vimeo-api` · **Port**: 8099 · **Env**: `VIMEO_API_URL`

Mock service mirroring Vimeo API endpoints. See `vimeo-api/vimeo-api_postman_collection.json`*` for the runnable request collection.

### Endpoints

#### Endpoints

- `GET {{baseUrl}}/health` — health
- `GET {{baseUrl}}/me` — me
- `GET {{baseUrl}}/me/videos?page=1&per_page=25` — my videos
- `GET {{baseUrl}}/videos/901000103` — video by id
- `GET {{baseUrl}}/videos/999999999` — video not found
- `GET {{baseUrl}}/users/12000002` — user by id
- `GET {{baseUrl}}/users/12000004/videos?page=1&per_page=25` — user videos

---

## 100. Webflow API

**Service**: `webflow-api` · **Port**: 8100 · **Env**: `WEBFLOW_API_URL`

Mock service mirroring Webflow API endpoints. See `webflow-api/webflow-api_postman_collection.json`*` for the runnable request collection.

### Endpoints

#### Endpoints

- `GET {{baseUrl}}/health` — health
- `GET {{baseUrl}}/v2/sites` — list sites
- `GET {{baseUrl}}/v2/sites/650a1f0000000000000001a1` — get site
- `GET {{baseUrl}}/v2/sites/650a1f0000000000000001a1/collections` — list collections
- `GET {{baseUrl}}/v2/collections/660b2a0000000000000002b1/items?limit=100&offset=0` — list items
- `POST {{baseUrl}}/v2/collections/660b2a0000000000000002b1/items` — create item

---

## 101. Activecampaign API

**Service**: `activecampaign-api` · **Port**: 8101 · **Env**: `ACTIVECAMPAIGN_API_URL`

Mock service mirroring Activecampaign API endpoints. See `activecampaign-api/activecampaign-api_postman_collection.json`*` for the runnable request collection.

### Endpoints

#### Endpoints

- `GET {{baseUrl}}/health` — health
- `GET {{baseUrl}}/api/3/contacts?limit=20&offset=0` — list contacts
- `GET {{baseUrl}}/api/3/contacts?email=olivia.bennett@example.com` — filter contacts by email
- `GET {{baseUrl}}/api/3/contacts/4` — get contact
- `POST {{baseUrl}}/api/3/contacts` — create contact
- `GET {{baseUrl}}/api/3/lists` — list lists
- `GET {{baseUrl}}/api/3/campaigns` — list campaigns
- `GET {{baseUrl}}/api/3/deals` — list deals

---

