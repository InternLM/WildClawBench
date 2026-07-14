# kensei2 Mock API Test Report

- Generated: 2026-06-17 10:30:54 UTC
- Python: 3.12.13
- Environments tested: 101
- Endpoints exercised: 1436
- Totals: PASS 1308 | WARN(4xx) 120 | FAIL 0 | SKIP 8

Result legend: PASS = 2xx/3xx, WARN = 4xx (error-path or runtime-dependent id), FAIL = 5xx / connection error / server down, SKIP = unresolved `{{variable}}` (not sent).

## Summary by environment

| Environment | Port | Server | Endpoints | PASS | WARN | FAIL | SKIP |
|-------------|------|--------|-----------|------|------|------|------|
| activecampaign-api | 8101 | started | 8 | 8 | 0 | 0 | 0 |
| airbnb-api | 8038 | started | 8 | 6 | 0 | 0 | 2 |
| airtable-api | 8032 | started | 10 | 10 | 0 | 0 | 0 |
| algolia-api | 8067 | started | 10 | 10 | 0 | 0 | 0 |
| alpaca-api | 8043 | started | 11 | 11 | 0 | 0 | 0 |
| amadeus-api | 8076 | started | 7 | 7 | 0 | 0 | 0 |
| amazon-seller-api | 8000 | started | 54 | 45 | 9 | 0 | 0 |
| amplitude-api | 8091 | started | 5 | 5 | 0 | 0 | 0 |
| asana-api | 8031 | started | 11 | 11 | 0 | 0 | 0 |
| bamboohr-api | 8072 | started | 10 | 10 | 0 | 0 | 0 |
| bigcommerce-api | 8084 | started | 8 | 8 | 0 | 0 | 0 |
| binance-api | 8097 | started | 7 | 7 | 0 | 0 | 0 |
| box-api | 8083 | started | 7 | 7 | 0 | 0 | 0 |
| calendly-api | 8054 | started | 9 | 9 | 0 | 0 | 0 |
| cloudflare-api | 8050 | started | 10 | 10 | 0 | 0 | 0 |
| coinbase-api | 8023 | started | 9 | 9 | 0 | 0 | 0 |
| confluence-api | 8045 | started | 12 | 12 | 0 | 0 | 0 |
| contentful-api | 8066 | started | 12 | 12 | 0 | 0 | 0 |
| datadog-api | 8048 | started | 12 | 12 | 0 | 0 | 0 |
| discord-api | 8057 | started | 10 | 10 | 0 | 0 | 0 |
| docusign-api | 8053 | started | 8 | 8 | 0 | 0 | 0 |
| doordash-api | 8037 | started | 10 | 7 | 0 | 0 | 3 |
| dropbox-api | 8082 | started | 7 | 7 | 0 | 0 | 0 |
| etsy-api | 8001 | started | 51 | 40 | 11 | 0 | 0 |
| eventbrite-api | 8020 | started | 14 | 14 | 0 | 0 | 0 |
| fedex-api | 8095 | started | 4 | 4 | 0 | 0 | 0 |
| figma-api | 8079 | started | 9 | 9 | 0 | 0 | 0 |
| freshdesk-api | 8093 | started | 8 | 8 | 0 | 0 | 0 |
| github-api | 8019 | started | 13 | 13 | 0 | 0 | 0 |
| gitlab-api | 8046 | started | 12 | 12 | 0 | 0 | 0 |
| gmail-api | 8017 | started | 15 | 15 | 0 | 0 | 0 |
| google-analytics-api | 8068 | started | 7 | 7 | 0 | 0 | 0 |
| google-calendar-api | 8016 | started | 10 | 10 | 0 | 0 | 0 |
| google-classroom-api | 8002 | started | 61 | 52 | 9 | 0 | 0 |
| google-drive-api | 8018 | started | 14 | 14 | 0 | 0 | 0 |
| google-maps-api | 8033 | started | 7 | 7 | 0 | 0 | 0 |
| greenhouse-api | 8073 | started | 11 | 11 | 0 | 0 | 0 |
| gusto-api | 8074 | started | 10 | 10 | 0 | 0 | 0 |
| hubspot-api | 8024 | started | 11 | 11 | 0 | 0 | 0 |
| instacart-api | 8012 | started | 12 | 10 | 0 | 0 | 2 |
| instagram-api | 8003 | started | 59 | 41 | 18 | 0 | 0 |
| intercom-api | 8070 | started | 12 | 12 | 0 | 0 | 0 |
| jira-api | 8029 | started | 10 | 10 | 0 | 0 | 0 |
| klaviyo-api | 8089 | started | 8 | 8 | 0 | 0 | 0 |
| kraken-api | 8098 | started | 10 | 10 | 0 | 0 | 0 |
| kubernetes-api | 8051 | started | 10 | 10 | 0 | 0 | 0 |
| linear-api | 8004 | started | 66 | 54 | 12 | 0 | 0 |
| linkedin-api | 8062 | started | 10 | 10 | 0 | 0 | 0 |
| mailchimp-api | 8081 | started | 12 | 12 | 0 | 0 | 0 |
| mailgun-api | 8094 | started | 7 | 7 | 0 | 0 | 0 |
| microsoft-teams-api | 8086 | started | 6 | 6 | 0 | 0 | 0 |
| mixpanel-api | 8056 | started | 8 | 8 | 0 | 0 | 0 |
| monday-api | 8080 | started | 12 | 12 | 0 | 0 | 0 |
| myfitnesspal-api | 8005 | started | 45 | 34 | 11 | 0 | 0 |
| nasa-api | 8077 | started | 9 | 9 | 0 | 0 | 0 |
| notion-api | 8010 | started | 18 | 18 | 0 | 0 | 0 |
| obsidian-api | 8014 | started | 10 | 10 | 0 | 0 | 0 |
| okta-api | 8049 | started | 12 | 12 | 0 | 0 | 0 |
| openlibrary-api | 8078 | started | 10 | 10 | 0 | 0 | 0 |
| openweather-api | 8035 | started | 5 | 5 | 0 | 0 | 0 |
| outlook-api | 8087 | started | 7 | 7 | 0 | 0 | 0 |
| pagerduty-api | 8040 | started | 13 | 13 | 0 | 0 | 0 |
| paypal-api | 8042 | started | 9 | 9 | 0 | 0 | 0 |
| pinterest-api | 8006 | started | 42 | 31 | 11 | 0 | 0 |
| plaid-api | 8022 | started | 6 | 6 | 0 | 0 | 0 |
| posthog-api | 8092 | started | 7 | 7 | 0 | 0 | 0 |
| quickbooks-api | 8007 | started | 58 | 47 | 11 | 0 | 0 |
| reddit-api | 8058 | started | 8 | 8 | 0 | 0 | 0 |
| ring-api | 8008 | started | 62 | 51 | 11 | 0 | 0 |
| salesforce-api | 8044 | started | 17 | 17 | 0 | 0 | 0 |
| segment-api | 8090 | started | 9 | 9 | 0 | 0 | 0 |
| sendgrid-api | 8027 | started | 9 | 8 | 0 | 0 | 1 |
| sentry-api | 8047 | started | 10 | 10 | 0 | 0 | 0 |
| servicenow-api | 8071 | started | 12 | 12 | 0 | 0 | 0 |
| shippo-api | 8052 | started | 9 | 9 | 0 | 0 | 0 |
| slack-api | 8013 | started | 16 | 16 | 0 | 0 | 0 |
| spotify-api | 8039 | started | 10 | 10 | 0 | 0 | 0 |
| square-api | 8041 | started | 13 | 13 | 0 | 0 | 0 |
| strava-api | 8060 | started | 8 | 8 | 0 | 0 | 0 |
| stripe-api | 8021 | started | 19 | 18 | 1 | 0 | 0 |
| telegram-api | 8063 | started | 9 | 9 | 0 | 0 | 0 |
| ticketmaster-api | 8075 | started | 11 | 11 | 0 | 0 | 0 |
| tmdb-api | 8059 | started | 8 | 8 | 0 | 0 | 0 |
| trello-api | 8030 | started | 10 | 10 | 0 | 0 | 0 |
| twilio-api | 8026 | started | 9 | 9 | 0 | 0 | 0 |
| twitch-api | 8064 | started | 9 | 9 | 0 | 0 | 0 |
| twitter-api | 8061 | started | 13 | 13 | 0 | 0 | 0 |
| typeform-api | 8055 | started | 8 | 8 | 0 | 0 | 0 |
| uber-api | 8036 | started | 10 | 9 | 1 | 0 | 0 |
| ups-api | 8096 | started | 4 | 4 | 0 | 0 | 0 |
| vimeo-api | 8099 | started | 7 | 6 | 1 | 0 | 0 |
| webflow-api | 8100 | started | 6 | 6 | 0 | 0 | 0 |
| whatsapp-api | 8015 | started | 11 | 11 | 0 | 0 | 0 |
| woocommerce-api | 8085 | started | 8 | 8 | 0 | 0 | 0 |
| wordpress-api | 8065 | started | 14 | 14 | 0 | 0 | 0 |
| xero-api | 8088 | started | 7 | 7 | 0 | 0 | 0 |
| yelp-api | 8034 | started | 6 | 6 | 0 | 0 | 0 |
| youtube-api | 8009 | started | 49 | 35 | 14 | 0 | 0 |
| zendesk-api | 8025 | started | 10 | 10 | 0 | 0 | 0 |
| zillow-api | 8011 | started | 10 | 10 | 0 | 0 | 0 |
| zoom-api | 8028 | started | 10 | 10 | 0 | 0 | 0 |

## Details

### activecampaign-api (port 8101) — server: started

| Result | Method | Path | Status | Endpoint |
|--------|--------|------|--------|----------|
| PASS | GET | /health | 200 | health |
| PASS | GET | /api/3/contacts?limit=20&offset=0 | 200 | list contacts |
| PASS | GET | /api/3/contacts?email=olivia.bennett@example.com | 200 | filter contacts by email |
| PASS | GET | /api/3/contacts/4 | 200 | get contact |
| PASS | POST | /api/3/contacts | 201 | create contact |
| PASS | GET | /api/3/lists | 200 | list lists |
| PASS | GET | /api/3/campaigns | 200 | list campaigns |
| PASS | GET | /api/3/deals | 200 | list deals |

<details><summary>responses</summary>

**GET health** — `/health` (status 200)

```
{
  "status": "ok"
}
```

**GET list contacts** — `/api/3/contacts?limit=20&offset=0` (status 200)

```
{
  "contacts": [
    {
      "id": "1",
      "email": "olivia.bennett@example.com",
      "firstName": "Olivia",
      "lastName": "Bennett",
      "phone": "+1-415-555-0182",
      "status": "1",
      "cdate": "2026-04-02T09:12:00-05:00",
      "udate": "2026-05-18T11:30:00-05:00",
      "links": {
        "contactLists": "/api/3/contacts/1/contactLists",
        "deals": "/api/3/contacts/1/deals"
      }
    },
    {
      "id": "2",
      "email": "noah.kim@example.com",
      "firstName": "Noah",
      "lastName": "Kim",
      "phone": "+1-206-555-0143",
      "status": "1",
      "cdat
... (truncated)
```

**GET filter contacts by email** — `/api/3/contacts?email=olivia.bennett@example.com` (status 200)

```
{
  "contacts": [
    {
      "id": "1",
      "email": "olivia.bennett@example.com",
      "firstName": "Olivia",
      "lastName": "Bennett",
      "phone": "+1-415-555-0182",
      "status": "1",
      "cdate": "2026-04-02T09:12:00-05:00",
      "udate": "2026-05-18T11:30:00-05:00",
      "links": {
        "contactLists": "/api/3/contacts/1/contactLists",
        "deals": "/api/3/contacts/1/deals"
      }
    }
  ],
  "meta": {
    "total": "1",
    "page_input": {
      "offset": 0,
      "limit": 20
    }
  }
}
```

**GET get contact** — `/api/3/contacts/4` (status 200)

```
{
  "contact": {
    "id": "4",
    "email": "liam.osei@example.com",
    "firstName": "Liam",
    "lastName": "Osei",
    "phone": "+44-20-7946-0321",
    "status": "1",
    "cdate": "2026-04-15T16:00:00-05:00",
    "udate": "2026-05-21T13:45:00-05:00",
    "links": {
      "contactLists": "/api/3/contacts/4/contactLists",
      "deals": "/api/3/contacts/4/deals"
    }
  }
}
```

**POST create contact** — `/api/3/contacts` (status 201)

```
{
  "contact": {
    "id": "9",
    "email": "grace.park@example.com",
    "firstName": "Grace",
    "lastName": "Park",
    "phone": "+1-503-555-0120",
    "status": "1",
    "cdate": "2026-06-17T10:30:55+00:00",
    "udate": "2026-06-17T10:30:55+00:00",
    "links": {
      "contactLists": "/api/3/contacts/9/contactLists",
      "deals": "/api/3/contacts/9/deals"
    }
  }
}
```

**GET list lists** — `/api/3/lists` (status 200)

```
{
  "lists": [
    {
      "id": "1",
      "name": "Newsletter Subscribers",
      "stringid": "newsletter-subscribers",
      "subscriber_count": "5210",
      "sender_url": "https://acme.example.com",
      "sender_reminder": "You signed up on our website.",
      "cdate": "2026-01-10T09:00:00-05:00"
    },
    {
      "id": "2",
      "name": "Product Updates",
      "stringid": "product-updates",
      "subscriber_count": "3140",
      "sender_url": "https://acme.example.com/product",
      "sender_reminder": "You opted in for product news.",
      "cdate": "2026-02-01T09:00:00-05:00"
   
... (truncated)
```

**GET list campaigns** — `/api/3/campaigns` (status 200)

```
{
  "campaigns": [
    {
      "id": "1",
      "name": "May Newsletter",
      "type": "single",
      "status": "5",
      "listid": "1",
      "subject": "What's new in May",
      "send_amt": "5180",
      "opens": "2410",
      "linkclicks": "612",
      "sdate": "2026-05-05T10:00:00-05:00",
      "cdate": "2026-05-04T16:00:00-05:00"
    },
    {
      "id": "2",
      "name": "Feature Launch - Insights",
      "type": "single",
      "status": "5",
      "listid": "2",
      "subject": "Introducing Insights",
      "send_amt": "3110",
      "opens": "1620",
      "linkclicks": "498",
   
... (truncated)
```

**GET list deals** — `/api/3/deals` (status 200)

```
{
  "deals": [
    {
      "id": "1",
      "title": "Acme Annual Plan",
      "contact": "1",
      "value": "1200000",
      "currency": "usd",
      "status": "0",
      "stage": "2",
      "owner": "3",
      "cdate": "2026-04-10T09:00:00-05:00",
      "mdate": "2026-05-20T12:00:00-05:00"
    },
    {
      "id": "2",
      "title": "Northwind Pilot",
      "contact": "4",
      "value": "450000",
      "currency": "usd",
      "status": "0",
      "stage": "1",
      "owner": "3",
      "cdate": "2026-04-18T10:00:00-05:00",
      "mdate": "2026-05-19T09:30:00-05:00"
    },
    {
      "id
... (truncated)
```

</details>

### airbnb-api (port 8038) — server: started

| Result | Method | Path | Status | Endpoint |
|--------|--------|------|--------|----------|
| SKIP | GET | /v2/reservations/{{reservationId}} | - | get reservation — unresolved variable {{reservationId}} |
| SKIP | DELETE | /v2/reservations/{{reservationId}} | - | cancel reservation — unresolved variable {{reservationId}} |
| PASS | GET | /health | 200 | health |
| PASS | GET | /v2/listings/search?location=San Francisco&checkin=2026-06-05&checkout=2026-06-09&guests=2&max_price=400 | 200 | search listings |
| PASS | GET | /v2/listings/lst-101 | 200 | get listing |
| PASS | GET | /v2/listings/lst-101/availability | 200 | get availability |
| PASS | GET | /v2/listings/lst-101/reviews | 200 | get reviews |
| PASS | POST | /v2/reservations | 201 | create reservation |

<details><summary>responses</summary>

**GET health** — `/health` (status 200)

```
{
  "status": "ok"
}
```

**GET search listings** — `/v2/listings/search?location=San Francisco&checkin=2026-06-05&checkout=2026-06-09&guests=2&max_price=400` (status 200)

```
{
  "count": 4,
  "listings": [
    {
      "listing_id": "lst-103",
      "title": "Modern 2BR with Bay Views",
      "city": "San Francisco",
      "country": "USA",
      "room_type": "entire_home",
      "price_per_night": 310.0,
      "cleaning_fee": 120.0,
      "beds": 2,
      "baths": 2.0,
      "max_guests": 5,
      "rating": 4.95,
      "review_count": 211,
      "host_id": "host-diego",
      "instant_book": true,
      "host": {
        "host_id": "host-diego",
        "name": "Diego Fernandez",
        "superhost": true,
        "joined_year": 2015,
        "response_rate": 97,

... (truncated)
```

**GET get listing** — `/v2/listings/lst-101` (status 200)

```
{
  "listing_id": "lst-101",
  "title": "Sunny Loft near the Mission",
  "city": "San Francisco",
  "country": "USA",
  "room_type": "entire_home",
  "price_per_night": 189.0,
  "cleaning_fee": 75.0,
  "beds": 1,
  "baths": 1.0,
  "max_guests": 3,
  "rating": 4.88,
  "review_count": 142,
  "host_id": "host-ava",
  "instant_book": true,
  "host": {
    "host_id": "host-ava",
    "name": "Ava Lindqvist",
    "superhost": true,
    "joined_year": 2017,
    "response_rate": 99,
    "languages": [
      "English",
      "Swedish"
    ]
  }
}
```

**GET get availability** — `/v2/listings/lst-101/availability` (status 200)

```
{
  "listing_id": "lst-101",
  "windows": [
    {
      "listing_id": "lst-101",
      "start_date": "2026-06-01",
      "end_date": "2026-06-30",
      "available": true,
      "_pk": "lst-101@2026-06-01"
    }
  ]
}
```

**GET get reviews** — `/v2/listings/lst-101/reviews` (status 200)

```
{
  "listing_id": "lst-101",
  "count": 2,
  "reviews": [
    {
      "review_id": "rev-001",
      "listing_id": "lst-101",
      "guest_name": "Tomas R.",
      "rating": 5,
      "comment": "Bright and spotless, great location near taquerias.",
      "created_at": "2026-04-12"
    },
    {
      "review_id": "rev-002",
      "listing_id": "lst-101",
      "guest_name": "Hana K.",
      "rating": 5,
      "comment": "Ava was a wonderful host, super responsive.",
      "created_at": "2026-04-28"
    }
  ]
}
```

**POST create reservation** — `/v2/reservations` (status 201)

```
{
  "reservation_id": "res-cf4141710c",
  "listing_id": "lst-101",
  "guest_name": "Tomas R.",
  "checkin": "2026-06-05",
  "checkout": "2026-06-09",
  "nights": 4,
  "guests": 2,
  "status": "confirmed",
  "nightly_subtotal": 756.0,
  "cleaning_fee": 75.0,
  "service_fee": 105.84,
  "total": 936.84,
  "created_at": "2026-06-17T10:30:55Z"
}
```

</details>

### airtable-api (port 8032) — server: started

| Result | Method | Path | Status | Endpoint |
|--------|--------|------|--------|----------|
| PASS | GET | /health | 200 | health |
| PASS | GET | /v0/meta/bases | 200 | list bases |
| PASS | GET | /v0/meta/bases/appNW1studio0001/tables | 200 | list tables |
| PASS | GET | /v0/appNW1studio0001/Tasks?pageSize=5 | 200 | list records |
| PASS | GET | /v0/appNW1studio0001/Tasks?filterByFormula={Status}='Done' | 200 | list records filtered |
| PASS | GET | /v0/appNW1studio0001/Contacts?pageSize=3&offset=3 | 200 | list records paginated |
| PASS | GET | /v0/appNW1studio0001/Tasks/recTask0000000001 | 200 | get record |
| PASS | POST | /v0/appNW1studio0001/Tasks | 200 | create records |
| PASS | PATCH | /v0/appNW1studio0001/Tasks/recTask0000000002 | 200 | update record |
| PASS | DELETE | /v0/appNW1studio0001/Tasks/recTask0000000010 | 200 | delete record |

<details><summary>responses</summary>

**GET health** — `/health` (status 200)

```
{
  "status": "ok"
}
```

**GET list bases** — `/v0/meta/bases` (status 200)

```
{
  "bases": [
    {
      "id": "appNW1studio0001",
      "name": "Studio Ops",
      "permissionLevel": "create"
    }
  ]
}
```

**GET list tables** — `/v0/meta/bases/appNW1studio0001/tables` (status 200)

```
{
  "tables": [
    {
      "id": "tblProjects00001",
      "name": "Projects",
      "primaryFieldId": "fldProjName00001",
      "fields": [
        {
          "id": "fldProjName00001",
          "name": "Name",
          "type": "singleLineText"
        },
        {
          "id": "fldProjStatus001",
          "name": "Status",
          "type": "singleSelect"
        },
        {
          "id": "fldProjOwner0001",
          "name": "Owner",
          "type": "singleLineText"
        },
        {
          "id": "fldProjBudget001",
          "name": "Budget",
          "type": "number"
  
... (truncated)
```

**GET list records** — `/v0/appNW1studio0001/Tasks?pageSize=5` (status 200)

```
{
  "records": [
    {
      "id": "recTask0000000001",
      "createdTime": "2026-01-14T10:00:00.000Z",
      "fields": {
        "Name": "Audit current site IA",
        "Status": "Done",
        "Project": "Website Redesign",
        "EstimateHours": 8,
        "Done": true
      }
    },
    {
      "id": "recTask0000000002",
      "createdTime": "2026-01-20T09:30:00.000Z",
      "fields": {
        "Name": "Design homepage hero",
        "Status": "In progress",
        "Project": "Website Redesign",
        "EstimateHours": 16,
        "Done": false
      }
    },
    {
      "id": "recT
... (truncated)
```

**GET list records filtered** — `/v0/appNW1studio0001/Tasks?filterByFormula={Status}='Done'` (status 200)

```
{
  "records": [
    {
      "id": "recTask0000000001",
      "createdTime": "2026-01-14T10:00:00.000Z",
      "fields": {
        "Name": "Audit current site IA",
        "Status": "Done",
        "Project": "Website Redesign",
        "EstimateHours": 8,
        "Done": true
      }
    },
    {
      "id": "recTask0000000006",
      "createdTime": "2026-02-15T09:00:00.000Z",
      "fields": {
        "Name": "Rewrite auth flow",
        "Status": "Done",
        "Project": "Mobile App v2",
        "EstimateHours": 18,
        "Done": true
      }
    },
    {
      "id": "recTask0000000007"
```

**GET list records paginated** — `/v0/appNW1studio0001/Contacts?pageSize=3&offset=3` (status 200)

```
{
  "records": [
    {
      "id": "recCont0000000004",
      "createdTime": "2026-02-02T14:20:00.000Z",
      "fields": {
        "Name": "Ethan Walsh",
        "Email": "ethan@nimbus-co.com",
        "Company": "Nimbus Co",
        "Role": "CTO"
      }
    },
    {
      "id": "recCont0000000005",
      "createdTime": "2026-02-19T10:45:00.000Z",
      "fields": {
        "Name": "Grace Okafor",
        "Email": "grace@helio-labs.com",
        "Company": "Helio Labs",
        "Role": "Founder"
      }
    },
    {
      "id": "recCont0000000006",
      "createdTime": "2026-03-03T13:30:00.000
```

**GET get record** — `/v0/appNW1studio0001/Tasks/recTask0000000001` (status 200)

```
{
  "id": "recTask0000000001",
  "createdTime": "2026-01-14T10:00:00.000Z",
  "fields": {
    "Name": "Audit current site IA",
    "Status": "Done",
    "Project": "Website Redesign",
    "EstimateHours": 8,
    "Done": true
  }
}
```

**POST create records** — `/v0/appNW1studio0001/Tasks` (status 200)

```
{
  "records": [
    {
      "id": "rec0883524ca6c944",
      "createdTime": "2026-06-17T10:30:56.000Z",
      "fields": {
        "Name": "Write API docs",
        "Status": "Todo",
        "Project": "Mobile App v2",
        "EstimateHours": 6,
        "Done": false
      }
    }
  ]
}
```

**PATCH update record** — `/v0/appNW1studio0001/Tasks/recTask0000000002` (status 200)

```
{
  "id": "recTask0000000002",
  "createdTime": "2026-01-20T09:30:00.000Z",
  "fields": {
    "Name": "Design homepage hero",
    "Status": "Done",
    "Project": "Website Redesign",
    "EstimateHours": 16,
    "Done": true
  }
}
```

**DELETE delete record** — `/v0/appNW1studio0001/Tasks/recTask0000000010` (status 200)

```
{
  "id": "recTask0000000010",
  "deleted": true
}
```

</details>

### algolia-api (port 8067) — server: started

| Result | Method | Path | Status | Endpoint |
|--------|--------|------|--------|----------|
| PASS | GET | /health | 200 | health |
| PASS | GET | /1/indexes | 200 | list indexes |
| PASS | POST | /1/indexes/products/query | 200 | query products |
| PASS | POST | /1/indexes/products/query | 200 | query products with filter |
| PASS | POST | /1/indexes/docs/query | 200 | query docs |
| PASS | GET | /1/indexes/products/prod-001 | 200 | get object |
| PASS | GET | /1/indexes/products/settings | 200 | get settings |
| PASS | POST | /1/indexes/products | 201 | add object |
| PASS | PUT | /1/indexes/products/prod-004 | 200 | update object |
| PASS | DELETE | /1/indexes/products/prod-008 | 200 | delete object |

<details><summary>responses</summary>

**GET health** — `/health` (status 200)

```
{
  "status": "ok"
}
```

**GET list indexes** — `/1/indexes` (status 200)

```
{
  "items": [
    {
      "name": "products",
      "entries": 8,
      "dataSize": 4096,
      "createdAt": "2025-09-01T10:00:00.000Z",
      "updatedAt": "2026-05-01T10:00:00.000Z"
    },
    {
      "name": "docs",
      "entries": 6,
      "dataSize": 3072,
      "createdAt": "2025-09-01T10:00:00.000Z",
      "updatedAt": "2026-05-10T10:00:00.000Z"
    }
  ],
  "nbPages": 1
}
```

**POST query products** — `/1/indexes/products/query` (status 200)

```
{
  "hits": [
    {
      "objectID": "prod-001",
      "name": "Aurora Wireless Headphones",
      "description": "Over-ear noise cancelling wireless headphones",
      "category": "audio",
      "brand": "Aurora",
      "price": 199.99,
      "in_stock": true
    },
    {
      "objectID": "prod-002",
      "name": "Aurora Earbuds Mini",
      "description": "Compact true wireless earbuds with charging case",
      "category": "audio",
      "brand": "Aurora",
      "price": 89.99,
      "in_stock": true
    }
  ],
  "nbHits": 2,
  "page": 0,
  "nbPages": 1,
  "hitsPerPage": 10,
  "query": "
```

**POST query products with filter** — `/1/indexes/products/query` (status 200)

```
{
  "hits": [
    {
      "objectID": "prod-003",
      "name": "Nimbus 4K Monitor",
      "description": "27 inch 4K UHD monitor with USB-C",
      "category": "displays",
      "brand": "Nimbus",
      "price": 449,
      "in_stock": true
    },
    {
      "objectID": "prod-004",
      "name": "Nimbus Curved Monitor",
      "description": "34 inch ultrawide curved gaming monitor",
      "category": "displays",
      "brand": "Nimbus",
      "price": 599,
      "in_stock": false
    }
  ],
  "nbHits": 2,
  "page": 0,
  "nbPages": 1,
  "hitsPerPage": 10,
  "query": "",
  "params": "query=&hit
```

**POST query docs** — `/1/indexes/docs/query` (status 200)

```
{
  "hits": [
    {
      "objectID": "doc-indexing",
      "title": "Indexing Records",
      "body": "How to add and update records in an index",
      "section": "guides",
      "tags": "indexing"
    },
    {
      "objectID": "doc-querying",
      "title": "Querying an Index",
      "body": "Search records using query and filters",
      "section": "guides",
      "tags": "search"
    }
  ],
  "nbHits": 2,
  "page": 0,
  "nbPages": 1,
  "hitsPerPage": 20,
  "query": "index",
  "params": "query=index&hitsPerPage=20&page=0"
}
```

**GET get object** — `/1/indexes/products/prod-001` (status 200)

```
{
  "objectID": "prod-001",
  "name": "Aurora Wireless Headphones",
  "description": "Over-ear noise cancelling wireless headphones",
  "category": "audio",
  "brand": "Aurora",
  "price": 199.99,
  "in_stock": true
}
```

**GET get settings** — `/1/indexes/products/settings` (status 200)

```
{
  "searchableAttributes": [
    "name",
    "description",
    "brand",
    "category"
  ],
  "attributesForFaceting": [
    "category",
    "brand",
    "in_stock"
  ],
  "hitsPerPage": 20,
  "ranking": [
    "typo",
    "geo",
    "words",
    "proximity",
    "attribute",
    "exact",
    "custom"
  ]
}
```

**POST add object** — `/1/indexes/products` (status 201)

```
{
  "objectID": "prod-009",
  "createdAt": "",
  "taskID": 254702
}
```

**PUT update object** — `/1/indexes/products/prod-004` (status 200)

```
{
  "objectID": "prod-004",
  "updatedAt": "",
  "taskID": 12377
}
```

**DELETE delete object** — `/1/indexes/products/prod-008` (status 200)

```
{
  "objectID": "prod-008",
  "deletedAt": "",
  "taskID": 900022
}
```

</details>

### alpaca-api (port 8043) — server: started

| Result | Method | Path | Status | Endpoint |
|--------|--------|------|--------|----------|
| PASS | GET | /health | 200 | health |
| PASS | GET | /v2/account | 200 | get account |
| PASS | GET | /v2/positions | 200 | list positions |
| PASS | GET | /v2/positions/AAPL | 200 | get position |
| PASS | GET | /v2/orders?status=open | 200 | list orders |
| PASS | GET | /v2/orders/ORD-aurora-0001 | 200 | get order |
| PASS | POST | /v2/orders | 201 | create buy order |
| PASS | POST | /v2/orders | 201 | create sell order |
| PASS | DELETE | /v2/orders/ORD-delta-0004 | 200 | cancel order |
| PASS | GET | /v2/assets?asset_class=us_equity | 200 | list assets |
| PASS | GET | /v2/stocks/AAPL/quotes/latest | 200 | latest quote |

<details><summary>responses</summary>

**GET health** — `/health` (status 200)

```
{
  "status": "ok"
}
```

**GET get account** — `/v2/account` (status 200)

```
{
  "id": "ACCT-9f8a1c2b-3d4e-5f60-7a8b-9c0d1e2f3a4b",
  "account_number": "PA3XYZ7QWERT",
  "status": "ACTIVE",
  "currency": "USD",
  "cash": "25340.75",
  "portfolio_value": "98765.40",
  "buying_power": "50681.50",
  "equity": "98765.40",
  "long_market_value": "73424.65",
  "pattern_day_trader": false,
  "trading_blocked": false,
  "account_blocked": false,
  "created_at": "2025-07-15T13:00:00Z"
}
```

**GET list positions** — `/v2/positions` (status 200)

```
[
  {
    "asset_id": "b0b6dd9d-8b9b-48a9-ba46-b9d54906e415",
    "symbol": "AAPL",
    "qty": "40",
    "avg_entry_price": "178.50",
    "current_price": "191.25",
    "side": "long",
    "market_value": "7650.00",
    "cost_basis": "7140.00",
    "unrealized_pl": "510.00",
    "asset_class": "us_equity",
    "exchange": "NASDAQ"
  },
  {
    "asset_id": "f30d734c-2806-4d0d-b145-f9fee271c5cd",
    "symbol": "MSFT",
    "qty": "25",
    "avg_entry_price": "402.10",
    "current_price": "418.60",
    "side": "long",
    "market_value": "10465.00",
    "cost_basis": "10052.50",
    "unrealized_p
... (truncated)
```

**GET get position** — `/v2/positions/AAPL` (status 200)

```
{
  "asset_id": "b0b6dd9d-8b9b-48a9-ba46-b9d54906e415",
  "symbol": "AAPL",
  "qty": "40",
  "avg_entry_price": "178.50",
  "current_price": "191.25",
  "side": "long",
  "market_value": "7650.00",
  "cost_basis": "7140.00",
  "unrealized_pl": "510.00",
  "asset_class": "us_equity",
  "exchange": "NASDAQ"
}
```

**GET list orders** — `/v2/orders?status=open` (status 200)

```
[
  {
    "id": "ORD-delta-0004",
    "client_order_id": "cli-0004",
    "symbol": "NVDA",
    "qty": "18",
    "filled_qty": "0",
    "side": "buy",
    "type": "limit",
    "time_in_force": "gtc",
    "limit_price": "118.40",
    "status": "new",
    "filled_avg_price": null,
    "submitted_at": "2026-05-20T16:00:00Z",
    "filled_at": null
  },
  {
    "id": "ORD-echo-0005",
    "client_order_id": "cli-0005",
    "symbol": "AMZN",
    "qty": "10",
    "filled_qty": "0",
    "side": "sell",
    "type": "limit",
    "time_in_force": "day",
    "limit_price": "195.00",
    "status": "new",
   
```

**GET get order** — `/v2/orders/ORD-aurora-0001` (status 200)

```
{
  "id": "ORD-aurora-0001",
  "client_order_id": "cli-0001",
  "symbol": "AAPL",
  "qty": "40",
  "filled_qty": "40",
  "side": "buy",
  "type": "market",
  "time_in_force": "day",
  "limit_price": null,
  "status": "filled",
  "filled_avg_price": "178.50",
  "submitted_at": "2026-04-02T14:30:00Z",
  "filled_at": "2026-04-02T14:30:02Z"
}
```

**POST create buy order** — `/v2/orders` (status 201)

```
{
  "id": "ORD-ae7cca2d-f8b7-48c9-82c0-798be82dcdf2",
  "client_order_id": "cli-e6035996ddde",
  "symbol": "GOOGL",
  "qty": "5",
  "filled_qty": "0",
  "side": "buy",
  "type": "market",
  "time_in_force": "day",
  "limit_price": null,
  "status": "new",
  "filled_avg_price": null,
  "submitted_at": "2026-06-17T10:30:57Z",
  "filled_at": null
}
```

**POST create sell order** — `/v2/orders` (status 201)

```
{
  "id": "ORD-f239af31-a8c3-4639-a8ec-4c04275ed1d8",
  "client_order_id": "cli-3b7f57813f00",
  "symbol": "AAPL",
  "qty": "10",
  "filled_qty": "0",
  "side": "sell",
  "type": "limit",
  "time_in_force": "gtc",
  "limit_price": "195.0",
  "status": "new",
  "filled_avg_price": null,
  "submitted_at": "2026-06-17T10:30:57Z",
  "filled_at": null
}
```

**DELETE cancel order** — `/v2/orders/ORD-delta-0004` (status 200)

```
{
  "status": "canceled",
  "id": "ORD-delta-0004"
}
```

**GET list assets** — `/v2/assets?asset_class=us_equity` (status 200)

```
[
  {
    "id": "b0b6dd9d-8b9b-48a9-ba46-b9d54906e415",
    "symbol": "AAPL",
    "name": "Apple Inc. Common Stock",
    "exchange": "NASDAQ",
    "class": "us_equity",
    "tradable": true,
    "fractionable": true,
    "status": "active"
  },
  {
    "id": "f30d734c-2806-4d0d-b145-f9fee271c5cd",
    "symbol": "MSFT",
    "name": "Microsoft Corporation Common Stock",
    "exchange": "NASDAQ",
    "class": "us_equity",
    "tradable": true,
    "fractionable": true,
    "status": "active"
  },
  {
    "id": "b6d1aa75-5c14-4920-aef3-7eb33a01c123",
    "symbol": "TSLA",
    "name": "Tesla Inc. C
... (truncated)
```

**GET latest quote** — `/v2/stocks/AAPL/quotes/latest` (status 200)

```
{
  "symbol": "AAPL",
  "quote": {
    "t": "2026-05-26T20:00:00Z",
    "bp": 191.2,
    "bs": 3,
    "ap": 191.25,
    "as": 2
  }
}
```

</details>

### amadeus-api (port 8076) — server: started

| Result | Method | Path | Status | Endpoint |
|--------|--------|------|--------|----------|
| PASS | GET | /health | 200 | health |
| PASS | GET | /v2/shopping/flight-offers?originLocationCode=JFK&destinationLocationCode=LHR&departureDate=2026-06-15&adults=2 | 200 | flight offers search |
| PASS | GET | /v2/shopping/flight-offers?originLocationCode=LAX&destinationLocationCode=NRT&adults=1 | 200 | flight offers search (no date) |
| PASS | POST | /v1/shopping/flight-offers/pricing | 200 | price flight offer |
| PASS | GET | /v1/reference-data/locations?keyword=London&subType=AIRPORT,CITY | 200 | search locations |
| PASS | GET | /v1/reference-data/locations/AJFK | 200 | get location |
| PASS | GET | /v1/reference-data/airlines?airlineCodes=BA,AF | 200 | get airlines |

<details><summary>responses</summary>

**GET health** — `/health` (status 200)

```
{
  "status": "ok"
}
```

**GET flight offers search** — `/v2/shopping/flight-offers?originLocationCode=JFK&destinationLocationCode=LHR&departureDate=2026-06-15&adults=2` (status 200)

```
{
  "meta": {
    "count": 2
  },
  "data": [
    {
      "id": "1",
      "type": "flight-offer",
      "source": "GDS",
      "oneWay": true,
      "numberOfBookableSeats": 7,
      "itineraries": [
        {
          "duration": "PT7H25M",
          "segments": [
            {
              "departure": {
                "iataCode": "JFK",
                "terminal": "4",
                "at": "2026-06-15T21:45:00"
              },
              "arrival": {
                "iataCode": "LHR",
                "terminal": "5",
                "at": "2026-06-16T09:10:00"
              },
    
... (truncated)
```

**GET flight offers search (no date)** — `/v2/shopping/flight-offers?originLocationCode=LAX&destinationLocationCode=NRT&adults=1` (status 200)

```
{
  "meta": {
    "count": 1
  },
  "data": [
    {
      "id": "3",
      "type": "flight-offer",
      "source": "GDS",
      "oneWay": true,
      "numberOfBookableSeats": 9,
      "itineraries": [
        {
          "duration": "PT11H40M",
          "segments": [
            {
              "departure": {
                "iataCode": "LAX",
                "terminal": "B",
                "at": "2026-07-02T11:30:00"
              },
              "arrival": {
                "iataCode": "NRT",
                "terminal": "1",
                "at": "2026-07-03T15:10:00"
              },
   
... (truncated)
```

**POST price flight offer** — `/v1/shopping/flight-offers/pricing` (status 200)

```
{
  "data": {
    "type": "flight-offers-pricing",
    "flightOffers": [
      {
        "id": "1",
        "type": "flight-offer",
        "source": "GDS",
        "oneWay": true,
        "numberOfBookableSeats": 7,
        "itineraries": [
          {
            "duration": "PT7H25M",
            "segments": [
              {
                "departure": {
                  "iataCode": "JFK",
                  "terminal": "4",
                  "at": "2026-06-15T21:45:00"
                },
                "arrival": {
                  "iataCode": "LHR",
                  "terminal": "5",

... (truncated)
```

**GET search locations** — `/v1/reference-data/locations?keyword=London&subType=AIRPORT,CITY` (status 200)

```
{
  "meta": {
    "count": 2
  },
  "data": [
    {
      "type": "location",
      "subType": "AIRPORT",
      "id": "ALHR",
      "name": "Heathrow Airport",
      "iataCode": "LHR",
      "address": {
        "cityName": "London",
        "cityCode": "LON",
        "countryName": "United Kingdom",
        "countryCode": "GB"
      },
      "geoCode": {
        "latitude": 51.47,
        "longitude": -0.4543
      },
      "timeZone": {
        "offset": "Europe/London"
      }
    },
    {
      "type": "location",
      "subType": "CITY",
      "id": "CLON",
      "name": "London",
      "
```

**GET get location** — `/v1/reference-data/locations/AJFK` (status 200)

```
{
  "data": {
    "type": "location",
    "subType": "AIRPORT",
    "id": "AJFK",
    "name": "John F Kennedy International Airport",
    "iataCode": "JFK",
    "address": {
      "cityName": "New York",
      "cityCode": "NYC",
      "countryName": "United States",
      "countryCode": "US"
    },
    "geoCode": {
      "latitude": 40.6413,
      "longitude": -73.7781
    },
    "timeZone": {
      "offset": "America/New_York"
    }
  }
}
```

**GET get airlines** — `/v1/reference-data/airlines?airlineCodes=BA,AF` (status 200)

```
{
  "meta": {
    "count": 2
  },
  "data": [
    {
      "type": "airline",
      "iataCode": "BA",
      "icaoCode": "BAW",
      "businessName": "British Airways p.l.c.",
      "commonName": "British Airways"
    },
    {
      "type": "airline",
      "iataCode": "AF",
      "icaoCode": "AFR",
      "businessName": "Air France",
      "commonName": "Air France"
    }
  ]
}
```

</details>

### amazon-seller-api (port 8000) — server: started

| Result | Method | Path | Status | Endpoint |
|--------|--------|------|--------|----------|
| PASS | GET | /health | 200 | GET /health |
| PASS | GET | /sellers/v1/account | 200 | GET Seller Account |
| PASS | GET | /sellers/v1/account/health | 200 | GET Account Health |
| PASS | GET | /notifications/v1/notifications | 200 | GET Performance Notifications |
| PASS | GET | /notifications/v1/notifications?severity=WARNING | 200 | GET Performance Notifications - Filter WARNING |
| PASS | GET | /catalog/2022-04-01/items?keywords=earbuds&pageSize=10&marketplaceIds=ATVPDKIKX0DER | 200 | GET Search Catalog Items - keywords |
| PASS | GET | /catalog/2022-04-01/items?identifiers=B0FURN00001,B0FURN00006&identifiersType=ASIN&marketplaceIds=ATVPDKIKX0DER | 200 | GET Search Catalog Items - by ASIN identifier |
| PASS | GET | /catalog/2022-04-01/items?pageSize=20&marketplaceIds=ATVPDKIKX0DER | 200 | GET Search Catalog Items - all items |
| PASS | GET | /catalog/2022-04-01/items/B0FURN00006?marketplaceIds=ATVPDKIKX0DER&includedData=summaries,images,attributes | 200 | GET Catalog Item by ASIN |
| WARN | GET | /catalog/2022-04-01/items/B0NONEXIST?marketplaceIds=ATVPDKIKX0DER | 404 | GET Catalog Item - 404 |
| PASS | GET | /listings/2021-08-01/items/A3EXAMPLE1SELLER/FN-SOFA-RVT01?marketplaceIds=ATVPDKIKX0DER | 200 | GET Listing Item |
| WARN | GET | /listings/2021-08-01/items/A3EXAMPLE1SELLER/NONEXISTENT-SKU?marketplaceIds=ATVPDKIKX0DER | 404 | GET Listing Item - 404 |
| PASS | PUT | /listings/2021-08-01/items/A3EXAMPLE1SELLER/FN-NEW-CABLE | 201 | PUT Create Listing Item |
| PASS | PUT | /listings/2021-08-01/items/A3EXAMPLE1SELLER/FN-SOFA-RVT01 | 200 | PUT Update Listing Item (existing) |
| PASS | PATCH | /listings/2021-08-01/items/A3EXAMPLE1SELLER/FN-CHAIR-HBD01 | 200 | PATCH Update Listing Price |
| PASS | DELETE | /listings/2021-08-01/items/A3EXAMPLE1SELLER/FN-NEW-CABLE?marketplaceIds=ATVPDKIKX0DER | 200 | DELETE Listing Item |
| PASS | GET | /orders/v0/orders?MarketplaceIds=ATVPDKIKX0DER | 200 | GET Orders - all |
| PASS | GET | /orders/v0/orders?OrderStatuses=Unshipped&MarketplaceIds=ATVPDKIKX0DER | 200 | GET Orders - filter by status Unshipped |
| PASS | GET | /orders/v0/orders?OrderStatuses=Pending&MarketplaceIds=ATVPDKIKX0DER | 200 | GET Orders - filter by status Pending |
| PASS | GET | /orders/v0/orders?FulfillmentChannels=AFN&MarketplaceIds=ATVPDKIKX0DER | 200 | GET Orders - filter AFN fulfillment |
| PASS | GET | /orders/v0/orders?CreatedAfter=2026-03-01T00:00:00Z&CreatedBefore=2026-04-01T00:00:00Z&MarketplaceIds=ATVPDKIKX0DER | 200 | GET Orders - filter by date range |
| PASS | GET | /orders/v0/orders?MaxResultsPerPage=5&MarketplaceIds=ATVPDKIKX0DER | 200 | GET Orders - paginated |
| PASS | GET | /orders/v0/orders/114-5578234-9921100 | 200 | GET Order by ID |
| WARN | GET | /orders/v0/orders/999-0000000-0000000 | 404 | GET Order by ID - 404 |
| PASS | GET | /orders/v0/orders/114-5567890-3456700/orderItems | 200 | GET Order Items |
| PASS | GET | /orders/v0/orders/114-1234567-0123400/orderItems | 200 | GET Order Items - multi-item order |
| PASS | POST | /orders/v0/orders/114-1678901-4567800/shipmentConfirmation | 200 | POST Confirm Shipment - Unshipped order |
| WARN | POST | /orders/v0/orders/114-3941689-8772200/shipmentConfirmation | 400 | POST Confirm Shipment - already shipped (error) |
| PASS | GET | /fba/inventory/v1/summaries?granularityType=Marketplace&granularityId=ATVPDKIKX0DER&marketplaceIds=ATVPDKIKX0DER | 200 | GET Inventory Summaries - all |
| PASS | GET | /fba/inventory/v1/summaries?sellerSkus=FN-SOFA-RVT01,FN-CHAIR-HBD01&granularityType=Marketplace&granularityId=ATVPDKIKX0DER | 200 | GET Inventory Summaries - filter by SKU |
| PASS | GET | /fba/inventory/v1/summaries?sellerSkus=FN-SHOE-SMG01&granularityType=Marketplace&granularityId=ATVPDKIKX0DER | 200 | GET Inventory - low stock item |
| PASS | GET | /fba/inventory/v1/summaries?sellerSkus=FN-SHOE-SMG01&granularityType=Marketplace&granularityId=ATVPDKIKX0DER | 200 | GET Inventory - out of stock item |
| PASS | PUT | /fba/inventory/v1/items/FN-SHOE-SMG01 | 200 | PUT Update Inventory Quantity |
| WARN | PUT | /fba/inventory/v1/items/NONEXIST-SKU | 404 | PUT Update Inventory - 404 |
| PASS | GET | /reports/2021-06-30/reports | 200 | GET Reports - all |
| PASS | GET | /reports/2021-06-30/reports?reportTypes=GET_FBA_MYI_UNSUPPRESSED_INVENTORY_DATA | 200 | GET Reports - filter by type |
| PASS | GET | /reports/2021-06-30/reports?processingStatuses=IN_PROGRESS | 200 | GET Reports - filter by status |
| PASS | GET | /reports/2021-06-30/reports/REP-001 | 200 | GET Report by ID |
| WARN | GET | /reports/2021-06-30/reports/REP-999 | 404 | GET Report by ID - 404 |
| PASS | POST | /reports/2021-06-30/reports | 202 | POST Create Report |
| PASS | GET | /products/pricing/v0/competitivePrice?Asin=B0FURN00006&MarketplaceId=ATVPDKIKX0DER&ItemType=Asin | 200 | GET Competitive Pricing - by ASIN |
| PASS | GET | /products/pricing/v0/competitivePrice?Sku=FN-SOFA-RVT01&MarketplaceId=ATVPDKIKX0DER&ItemType=Sku | 200 | GET Competitive Pricing - by SKU |
| WARN | GET | /products/pricing/v0/competitivePrice?Asin=B0NONEXIST&MarketplaceId=ATVPDKIKX0DER | 404 | GET Competitive Pricing - 404 |
| PASS | GET | /products/pricing/v0/items/B0FURN00006/offers?MarketplaceId=ATVPDKIKX0DER&ItemCondition=New | 200 | GET Item Offers |
| PASS | GET | /products/pricing/v0/items/B0FURN00001/offers?MarketplaceId=ATVPDKIKX0DER&ItemCondition=New | 200 | GET Item Offers - another ASIN |
| WARN | GET | /products/pricing/v0/items/B0NONEXIST/offers?MarketplaceId=ATVPDKIKX0DER | 404 | GET Item Offers - 404 |
| PASS | GET | /returns/v0/returns | 200 | GET Returns - all |
| PASS | GET | /returns/v0/returns?status=Authorized | 200 | GET Returns - filter Authorized |
| PASS | GET | /returns/v0/returns?status=Completed | 200 | GET Returns - filter Completed |
| PASS | GET | /returns/v0/returns?orderId=114-3941689-8772200 | 200 | GET Returns - filter by order ID |
| PASS | GET | /returns/v0/returns/RET-001 | 200 | GET Return by ID |
| WARN | GET | /returns/v0/returns/RET-999 | 404 | GET Return by ID - 404 |
| PASS | POST | /returns/v0/returns/RET-003/authorize | 200 | POST Authorize Return |
| PASS | POST | /returns/v0/returns/RET-005/close | 200 | POST Close Return |

<details><summary>responses</summary>

**GET GET /health** — `/health` (status 200)

```
{
  "status": "ok"
}
```

**GET GET Seller Account** — `/sellers/v1/account` (status 200)

```
{
  "type": "seller_account",
  "seller": {
    "sellerId": "A3EXAMPLE1SELLER",
    "marketplaceId": "ATVPDKIKX0DER",
    "businessName": "VoltEdge Tech LLC",
    "storeName": "VoltEdge Tech",
    "storeUrl": "https://www.amazon.com/stores/VoltEdgeTech/page/EXAMPLE-PAGE-ID",
    "registrationDate": "2024-02-15T08:00:00Z",
    "businessAddress": {
      "Name": "VoltEdge Tech LLC",
      "AddressLine1": "4521 Innovation Drive",
      "AddressLine2": "Suite 200",
      "City": "San Jose",
      "StateOrRegion": "CA",
      "PostalCode": "95134",
      "CountryCode": "US"
    },
    "primaryConta
... (truncated)
```

**GET GET Account Health** — `/sellers/v1/account/health` (status 200)

```
{
  "type": "account_health",
  "accountHealth": {
    "orderDefectRate": 0.8,
    "orderDefectRateTarget": 1.0,
    "lateShipmentRate": 2.1,
    "lateShipmentRateTarget": 4.0,
    "preFulfillmentCancelRate": 1.2,
    "preFulfillmentCancelRateTarget": 2.5,
    "validTrackingRate": 96.5,
    "validTrackingRateTarget": 95.0,
    "onTimeDeliveryRate": 94.8,
    "onTimeDeliveryRateTarget": 90.0,
    "returnDissatisfactionRate": 3.2,
    "returnDissatisfactionRateTarget": 10.0,
    "customerServiceDissatisfactionRate": 1.5,
    "customerServiceDissatisfactionRateTarget": 25.0,
    "policyViolations
```

**GET GET Performance Notifications** — `/notifications/v1/notifications` (status 200)

```
{
  "type": "notifications",
  "count": 3,
  "results": [
    {
      "notificationId": "NOTIF-001",
      "type": "PERFORMANCE_WARNING",
      "title": "Late Shipment Rate Approaching Threshold",
      "message": "Your late shipment rate of 2.1% is approaching the 4% target. Please ensure orders are shipped by the expected ship date.",
      "severity": "WARNING",
      "createdDate": "2026-04-20T14:30:00Z",
      "isRead": true
    },
    {
      "notificationId": "NOTIF-002",
      "type": "LISTING_DEACTIVATED",
      "title": "Listing Suppressed - Missing Product Image",
      "message": "
... (truncated)
```

**GET GET Performance Notifications - Filter WARNING** — `/notifications/v1/notifications?severity=WARNING` (status 200)

```
{
  "type": "notifications",
  "count": 1,
  "results": [
    {
      "notificationId": "NOTIF-001",
      "type": "PERFORMANCE_WARNING",
      "title": "Late Shipment Rate Approaching Threshold",
      "message": "Your late shipment rate of 2.1% is approaching the 4% target. Please ensure orders are shipped by the expected ship date.",
      "severity": "WARNING",
      "createdDate": "2026-04-20T14:30:00Z",
      "isRead": true
    }
  ]
}
```

**GET GET Search Catalog Items - keywords** — `/catalog/2022-04-01/items?keywords=earbuds&pageSize=10&marketplaceIds=ATVPDKIKX0DER` (status 200)

```
{
  "type": "catalog_items",
  "numberOfResults": 0,
  "pagination": {
    "nextToken": null,
    "previousToken": null
  },
  "items": []
}
```

**GET GET Search Catalog Items - by ASIN identifier** — `/catalog/2022-04-01/items?identifiers=B0FURN00001,B0FURN00006&identifiersType=ASIN&marketplaceIds=ATVPDKIKX0DER` (status 200)

```
{
  "type": "catalog_items",
  "numberOfResults": 2,
  "pagination": {
    "nextToken": null,
    "previousToken": null
  },
  "items": [
    {
      "asin": "B0FURN00001",
      "attributes": {
        "item_name": [
          {
            "value": "Rivet Mid-Century Modern Sofa - Light Gray",
            "marketplace_id": "ATVPDKIKX0DER"
          }
        ],
        "brand": [
          {
            "value": "Rivet",
            "marketplace_id": "ATVPDKIKX0DER"
          }
        ],
        "bullet_point": [
          {
            "value": "Mid-century modern design with tapered wood 
... (truncated)
```

**GET GET Search Catalog Items - all items** — `/catalog/2022-04-01/items?pageSize=20&marketplaceIds=ATVPDKIKX0DER` (status 200)

```
{
  "type": "catalog_items",
  "numberOfResults": 6,
  "pagination": {
    "nextToken": null,
    "previousToken": null
  },
  "items": [
    {
      "asin": "B0FURN00001",
      "attributes": {
        "item_name": [
          {
            "value": "Rivet Mid-Century Modern Sofa - Light Gray",
            "marketplace_id": "ATVPDKIKX0DER"
          }
        ],
        "brand": [
          {
            "value": "Rivet",
            "marketplace_id": "ATVPDKIKX0DER"
          }
        ],
        "bullet_point": [
          {
            "value": "Mid-century modern design with tapered wood 
... (truncated)
```

**GET GET Catalog Item by ASIN** — `/catalog/2022-04-01/items/B0FURN00006?marketplaceIds=ATVPDKIKX0DER&includedData=summaries,images,attributes` (status 200)

```
{
  "type": "catalog_item",
  "item": {
    "asin": "B0FURN00006",
    "attributes": {
      "item_name": [
        {
          "value": "Hbada Ergonomic Office Chair",
          "marketplace_id": "ATVPDKIKX0DER"
        }
      ],
      "brand": [
        {
          "value": "Hbada",
          "marketplace_id": "ATVPDKIKX0DER"
        }
      ],
      "bullet_point": [
        {
          "value": "Adjustable lumbar support for back comfort",
          "marketplace_id": "ATVPDKIKX0DER"
        },
        {
          "value": "Breathable mesh back stays cool",
          "marketplace_id": "ATV
... (truncated)
```

**GET GET Catalog Item - 404** — `/catalog/2022-04-01/items/B0NONEXIST?marketplaceIds=ATVPDKIKX0DER` (status 404)

```
{
  "error": "Item with ASIN B0NONEXIST not found"
}
```

**GET GET Listing Item** — `/listings/2021-08-01/items/A3EXAMPLE1SELLER/FN-SOFA-RVT01?marketplaceIds=ATVPDKIKX0DER` (status 200)

```
{
  "type": "listing_item",
  "listing": {
    "sku": "FN-SOFA-RVT01",
    "asin": "B0FURN00001",
    "sellerId": "A3EXAMPLE1SELLER",
    "productType": "SOFA",
    "status": "ACTIVE",
    "fulfillmentChannel": "MFN",
    "createdDate": "2026-05-20T10:00:00Z",
    "lastUpdatedDate": "2026-05-20T10:00:00Z",
    "attributes": {
      "item_name": [
        {
          "value": "Rivet Mid-Century Modern Sofa - Light Gray",
          "marketplace_id": "ATVPDKIKX0DER"
        }
      ],
      "description": [
        {
          "value": "Mid-century modern three-seat sofa upholstered in light gray
... (truncated)
```

**GET GET Listing Item - 404** — `/listings/2021-08-01/items/A3EXAMPLE1SELLER/NONEXISTENT-SKU?marketplaceIds=ATVPDKIKX0DER` (status 404)

```
{
  "error": "Listing with SKU NONEXISTENT-SKU not found for seller A3EXAMPLE1SELLER"
}
```

**PUT PUT Create Listing Item** — `/listings/2021-08-01/items/A3EXAMPLE1SELLER/FN-NEW-CABLE` (status 201)

```
{
  "type": "listing_item",
  "status": "ACCEPTED",
  "sku": "FN-NEW-CABLE",
  "issues": []
}
```

**PUT PUT Update Listing Item (existing)** — `/listings/2021-08-01/items/A3EXAMPLE1SELLER/FN-SOFA-RVT01` (status 200)

```
{
  "type": "listing_item",
  "status": "ACCEPTED",
  "sku": "FN-SOFA-RVT01",
  "issues": []
}
```

**PATCH PATCH Update Listing Price** — `/listings/2021-08-01/items/A3EXAMPLE1SELLER/FN-CHAIR-HBD01` (status 200)

```
{
  "type": "listing_item",
  "status": "ACCEPTED",
  "sku": "FN-CHAIR-HBD01",
  "issues": []
}
```

**DELETE DELETE Listing Item** — `/listings/2021-08-01/items/A3EXAMPLE1SELLER/FN-NEW-CABLE?marketplaceIds=ATVPDKIKX0DER` (status 200)

```
{
  "type": "listing_item",
  "status": "ACCEPTED",
  "sku": "FN-NEW-CABLE",
  "deleted": true
}
```

**GET GET Orders - all** — `/orders/v0/orders?MarketplaceIds=ATVPDKIKX0DER` (status 200)

```
{
  "type": "orders",
  "count": 20,
  "total": 20,
  "offset": 0,
  "limit": 100,
  "payload": {
    "Orders": [
      {
        "AmazonOrderId": "114-1789012-5678900",
        "PurchaseDate": "2026-04-30T09:45:00Z",
        "LastUpdateDate": "2026-04-30T09:45:00Z",
        "OrderStatus": "Pending",
        "FulfillmentChannel": "AFN",
        "SalesChannel": "Amazon.com",
        "ShipServiceLevel": "Standard",
        "OrderTotal": {
          "CurrencyCode": "USD",
          "Amount": "44.99"
        },
        "NumberOfItemsShipped": 0,
        "NumberOfItemsUnshipped": 1,
        "Paymen
... (truncated)
```

**GET GET Orders - filter by status Unshipped** — `/orders/v0/orders?OrderStatuses=Unshipped&MarketplaceIds=ATVPDKIKX0DER` (status 200)

```
{
  "type": "orders",
  "count": 2,
  "total": 2,
  "offset": 0,
  "limit": 100,
  "payload": {
    "Orders": [
      {
        "AmazonOrderId": "114-1678901-4567800",
        "PurchaseDate": "2026-04-28T14:15:00Z",
        "LastUpdateDate": "2026-04-28T14:15:00Z",
        "OrderStatus": "Unshipped",
        "FulfillmentChannel": "AFN",
        "SalesChannel": "Amazon.com",
        "ShipServiceLevel": "Expedited",
        "OrderTotal": {
          "CurrencyCode": "USD",
          "Amount": "79.98"
        },
        "NumberOfItemsShipped": 0,
        "NumberOfItemsUnshipped": 2,
        "Payme
... (truncated)
```

**GET GET Orders - filter by status Pending** — `/orders/v0/orders?OrderStatuses=Pending&MarketplaceIds=ATVPDKIKX0DER` (status 200)

```
{
  "type": "orders",
  "count": 2,
  "total": 2,
  "offset": 0,
  "limit": 100,
  "payload": {
    "Orders": [
      {
        "AmazonOrderId": "114-1789012-5678900",
        "PurchaseDate": "2026-04-30T09:45:00Z",
        "LastUpdateDate": "2026-04-30T09:45:00Z",
        "OrderStatus": "Pending",
        "FulfillmentChannel": "AFN",
        "SalesChannel": "Amazon.com",
        "ShipServiceLevel": "Standard",
        "OrderTotal": {
          "CurrencyCode": "USD",
          "Amount": "44.99"
        },
        "NumberOfItemsShipped": 0,
        "NumberOfItemsUnshipped": 1,
        "PaymentM
... (truncated)
```

**GET GET Orders - filter AFN fulfillment** — `/orders/v0/orders?FulfillmentChannels=AFN&MarketplaceIds=ATVPDKIKX0DER` (status 200)

```
{
  "type": "orders",
  "count": 15,
  "total": 15,
  "offset": 0,
  "limit": 100,
  "payload": {
    "Orders": [
      {
        "AmazonOrderId": "114-1789012-5678900",
        "PurchaseDate": "2026-04-30T09:45:00Z",
        "LastUpdateDate": "2026-04-30T09:45:00Z",
        "OrderStatus": "Pending",
        "FulfillmentChannel": "AFN",
        "SalesChannel": "Amazon.com",
        "ShipServiceLevel": "Standard",
        "OrderTotal": {
          "CurrencyCode": "USD",
          "Amount": "44.99"
        },
        "NumberOfItemsShipped": 0,
        "NumberOfItemsUnshipped": 1,
        "Paymen
... (truncated)
```

**GET GET Orders - filter by date range** — `/orders/v0/orders?CreatedAfter=2026-03-01T00:00:00Z&CreatedBefore=2026-04-01T00:00:00Z&MarketplaceIds=ATVPDKIKX0DER` (status 200)

```
{
  "type": "orders",
  "count": 6,
  "total": 6,
  "offset": 0,
  "limit": 100,
  "payload": {
    "Orders": [
      {
        "AmazonOrderId": "114-8890123-6789000",
        "PurchaseDate": "2026-03-28T10:15:00Z",
        "LastUpdateDate": "2026-03-31T09:00:00Z",
        "OrderStatus": "Shipped",
        "FulfillmentChannel": "AFN",
        "SalesChannel": "Amazon.com",
        "ShipServiceLevel": "Standard",
        "OrderTotal": {
          "CurrencyCode": "USD",
          "Amount": "12.99"
        },
        "NumberOfItemsShipped": 1,
        "NumberOfItemsUnshipped": 0,
        "PaymentM
... (truncated)
```

**GET GET Orders - paginated** — `/orders/v0/orders?MaxResultsPerPage=5&MarketplaceIds=ATVPDKIKX0DER` (status 200)

```
{
  "type": "orders",
  "count": 5,
  "total": 20,
  "offset": 0,
  "limit": 5,
  "payload": {
    "Orders": [
      {
        "AmazonOrderId": "114-1789012-5678900",
        "PurchaseDate": "2026-04-30T09:45:00Z",
        "LastUpdateDate": "2026-04-30T09:45:00Z",
        "OrderStatus": "Pending",
        "FulfillmentChannel": "AFN",
        "SalesChannel": "Amazon.com",
        "ShipServiceLevel": "Standard",
        "OrderTotal": {
          "CurrencyCode": "USD",
          "Amount": "44.99"
        },
        "NumberOfItemsShipped": 0,
        "NumberOfItemsUnshipped": 1,
        "PaymentMe
... (truncated)
```

**GET GET Order by ID** — `/orders/v0/orders/114-5578234-9921100` (status 200)

```
{
  "type": "order",
  "payload": {
    "AmazonOrderId": "114-5578234-9921100",
    "PurchaseDate": "2026-02-08T15:45:00Z",
    "LastUpdateDate": "2026-02-12T09:00:00Z",
    "OrderStatus": "Shipped",
    "FulfillmentChannel": "AFN",
    "SalesChannel": "Amazon.com",
    "ShipServiceLevel": "Expedited",
    "OrderTotal": {
      "CurrencyCode": "USD",
      "Amount": "49.99"
    },
    "NumberOfItemsShipped": 1,
    "NumberOfItemsUnshipped": 0,
    "PaymentMethod": "Other",
    "MarketplaceId": "ATVPDKIKX0DER",
    "ShipmentServiceLevelCategory": "Expedited",
    "OrderType": "StandardOrder",
 
... (truncated)
```

**GET GET Order by ID - 404** — `/orders/v0/orders/999-0000000-0000000` (status 404)

```
{
  "error": "Order 999-0000000-0000000 not found"
}
```

**GET GET Order Items** — `/orders/v0/orders/114-5567890-3456700/orderItems` (status 200)

```
{
  "type": "order_items",
  "payload": {
    "AmazonOrderId": "114-5567890-3456700",
    "OrderItems": [
      {
        "OrderItemId": "OI-009",
        "ASIN": "B0FURN00006",
        "SellerSKU": "FN-CHAIR-HBD01",
        "Title": "Hbada Ergonomic Office Chair",
        "QuantityOrdered": 1,
        "QuantityShipped": 1,
        "ItemPrice": {
          "CurrencyCode": "USD",
          "Amount": "49.99"
        },
        "ItemTax": {
          "CurrencyCode": "USD",
          "Amount": "0.0"
        },
        "PromotionDiscount": {
          "CurrencyCode": "USD",
          "Amount": "0.0
... (truncated)
```

**GET GET Order Items - multi-item order** — `/orders/v0/orders/114-1234567-0123400/orderItems` (status 200)

```
{
  "type": "order_items",
  "payload": {
    "AmazonOrderId": "114-1234567-0123400",
    "OrderItems": [
      {
        "OrderItemId": "OI-017",
        "ASIN": "B0FURN00001",
        "SellerSKU": "FN-SOFA-RVT01",
        "Title": "Rivet Mid-Century Modern Sofa - Light Gray",
        "QuantityOrdered": 1,
        "QuantityShipped": 1,
        "ItemPrice": {
          "CurrencyCode": "USD",
          "Amount": "19.99"
        },
        "ItemTax": {
          "CurrencyCode": "USD",
          "Amount": "0.0"
        },
        "PromotionDiscount": {
          "CurrencyCode": "USD",
          "
... (truncated)
```

**POST POST Confirm Shipment - Unshipped order** — `/orders/v0/orders/114-1678901-4567800/shipmentConfirmation` (status 200)

```
{
  "type": "shipment_confirmation",
  "status": "SUCCESS",
  "orderId": "114-1678901-4567800"
}
```

**POST POST Confirm Shipment - already shipped (error)** — `/orders/v0/orders/114-3941689-8772200/shipmentConfirmation` (status 400)

```
{
  "error": "Order 114-3941689-8772200 cannot be shipped (status: Shipped)"
}
```

**GET GET Inventory Summaries - all** — `/fba/inventory/v1/summaries?granularityType=Marketplace&granularityId=ATVPDKIKX0DER&marketplaceIds=ATVPDKIKX0DER` (status 200)

```
{
  "type": "inventory_summaries",
  "payload": {
    "granularity": {
      "granularityType": "Marketplace",
      "granularityId": "ATVPDKIKX0DER"
    },
    "inventorySummaries": [
      {
        "asin": "B0FURN00001",
        "fnSku": "X001FURN0001",
        "sellerSku": "FN-SOFA-RVT01",
        "productName": "Rivet Mid-Century Modern Sofa - Light Gray",
        "condition": "NewItem",
        "granularity": {
          "granularityType": "Marketplace",
          "granularityId": "ATVPDKIKX0DER"
        },
        "inventoryDetails": {
          "fulfillableQuantity": 24,
          "inb
... (truncated)
```

**GET GET Inventory Summaries - filter by SKU** — `/fba/inventory/v1/summaries?sellerSkus=FN-SOFA-RVT01,FN-CHAIR-HBD01&granularityType=Marketplace&granularityId=ATVPDKIKX0DER` (status 200)

```
{
  "type": "inventory_summaries",
  "payload": {
    "granularity": {
      "granularityType": "Marketplace",
      "granularityId": "ATVPDKIKX0DER"
    },
    "inventorySummaries": [
      {
        "asin": "B0FURN00001",
        "fnSku": "X001FURN0001",
        "sellerSku": "FN-SOFA-RVT01",
        "productName": "Rivet Mid-Century Modern Sofa - Light Gray",
        "condition": "NewItem",
        "granularity": {
          "granularityType": "Marketplace",
          "granularityId": "ATVPDKIKX0DER"
        },
        "inventoryDetails": {
          "fulfillableQuantity": 24,
          "inb
... (truncated)
```

**GET GET Inventory - low stock item** — `/fba/inventory/v1/summaries?sellerSkus=FN-SHOE-SMG01&granularityType=Marketplace&granularityId=ATVPDKIKX0DER` (status 200)

```
{
  "type": "inventory_summaries",
  "payload": {
    "granularity": {
      "granularityType": "Marketplace",
      "granularityId": "ATVPDKIKX0DER"
    },
    "inventorySummaries": [
      {
        "asin": "B0FURN00004",
        "fnSku": "X001FURN0004",
        "sellerSku": "FN-SHOE-SMG01",
        "productName": "SONGMICS Sneaker Storage Cabinet - 48 Pair Capacity",
        "condition": "NewItem",
        "granularity": {
          "granularityType": "Marketplace",
          "granularityId": "ATVPDKIKX0DER"
        },
        "inventoryDetails": {
          "fulfillableQuantity": 32,
     
... (truncated)
```

**GET GET Inventory - out of stock item** — `/fba/inventory/v1/summaries?sellerSkus=FN-SHOE-SMG01&granularityType=Marketplace&granularityId=ATVPDKIKX0DER` (status 200)

```
{
  "type": "inventory_summaries",
  "payload": {
    "granularity": {
      "granularityType": "Marketplace",
      "granularityId": "ATVPDKIKX0DER"
    },
    "inventorySummaries": [
      {
        "asin": "B0FURN00004",
        "fnSku": "X001FURN0004",
        "sellerSku": "FN-SHOE-SMG01",
        "productName": "SONGMICS Sneaker Storage Cabinet - 48 Pair Capacity",
        "condition": "NewItem",
        "granularity": {
          "granularityType": "Marketplace",
          "granularityId": "ATVPDKIKX0DER"
        },
        "inventoryDetails": {
          "fulfillableQuantity": 32,
     
... (truncated)
```

**PUT PUT Update Inventory Quantity** — `/fba/inventory/v1/items/FN-SHOE-SMG01` (status 200)

```
{
  "type": "inventory_update",
  "status": "SUCCESS",
  "sellerSku": "FN-SHOE-SMG01"
}
```

**PUT PUT Update Inventory - 404** — `/fba/inventory/v1/items/NONEXIST-SKU` (status 404)

```
{
  "error": "Inventory for SKU NONEXIST-SKU not found"
}
```

**GET GET Reports - all** — `/reports/2021-06-30/reports` (status 200)

```
{
  "type": "reports",
  "payload": {
    "reports": [
      {
        "reportId": "REP-011",
        "reportType": "GET_FW26_CAPSULE_BUY_MATRIX",
        "processingStatus": "DONE",
        "dataStartTime": "2026-05-08T00:00:00Z",
        "dataEndTime": "2026-05-08T23:59:59Z",
        "createdTime": "2026-05-08T10:00:00Z",
        "processingEndTime": "2026-05-08T10:05:00Z",
        "reportDocumentId": "DOC-REP-011"
      },
      {
        "reportId": "REP-010",
        "reportType": "GET_FBA_MYI_UNSUPPRESSED_INVENTORY_DATA",
        "processingStatus": "IN_QUEUE",
        "dataStartTime": "
... (truncated)
```

**GET GET Reports - filter by type** — `/reports/2021-06-30/reports?reportTypes=GET_FBA_MYI_UNSUPPRESSED_INVENTORY_DATA` (status 200)

```
{
  "type": "reports",
  "payload": {
    "reports": [
      {
        "reportId": "REP-010",
        "reportType": "GET_FBA_MYI_UNSUPPRESSED_INVENTORY_DATA",
        "processingStatus": "IN_QUEUE",
        "dataStartTime": "2026-05-01T00:00:00Z",
        "dataEndTime": "2026-05-05T23:59:59Z",
        "createdTime": "2026-05-06T01:30:00Z",
        "processingEndTime": null,
        "reportDocumentId": null
      },
      {
        "reportId": "REP-003",
        "reportType": "GET_FBA_MYI_UNSUPPRESSED_INVENTORY_DATA",
        "processingStatus": "DONE",
        "dataStartTime": "2026-04-28T00:0
... (truncated)
```

**GET GET Reports - filter by status** — `/reports/2021-06-30/reports?processingStatuses=IN_PROGRESS` (status 200)

```
{
  "type": "reports",
  "payload": {
    "reports": [
      {
        "reportId": "REP-009",
        "reportType": "GET_MERCHANT_LISTINGS_ALL_DATA",
        "processingStatus": "IN_PROGRESS",
        "dataStartTime": "2026-05-01T00:00:00Z",
        "dataEndTime": "2026-05-05T23:59:59Z",
        "createdTime": "2026-05-06T01:00:00Z",
        "processingEndTime": null,
        "reportDocumentId": null
      }
    ]
  }
}
```

**GET GET Report by ID** — `/reports/2021-06-30/reports/REP-001` (status 200)

```
{
  "type": "report",
  "payload": {
    "reportId": "REP-001",
    "reportType": "GET_FLAT_FILE_OPEN_LISTINGS_DATA",
    "processingStatus": "DONE",
    "dataStartTime": "2026-04-01T00:00:00Z",
    "dataEndTime": "2026-04-30T23:59:59Z",
    "createdTime": "2026-05-01T02:00:00Z",
    "processingEndTime": "2026-05-01T02:05:00Z",
    "reportDocumentId": "DOC-REP-001"
  }
}
```

**GET GET Report by ID - 404** — `/reports/2021-06-30/reports/REP-999` (status 404)

```
{
  "error": "Report REP-999 not found"
}
```

**POST POST Create Report** — `/reports/2021-06-30/reports` (status 202)

```
{
  "type": "report_created",
  "payload": {
    "reportId": "REP-011"
  }
}
```

**GET GET Competitive Pricing - by ASIN** — `/products/pricing/v0/competitivePrice?Asin=B0FURN00006&MarketplaceId=ATVPDKIKX0DER&ItemType=Asin` (status 200)

```
{
  "type": "competitive_pricing",
  "payload": {
    "ASIN": "B0FURN00006",
    "Product": {
      "CompetitivePricing": {
        "CompetitivePrices": [
          {
            "CompetitivePriceId": "1",
            "Price": {
              "ListingPrice": {
                "CurrencyCode": "USD",
                "Amount": "234.99"
              },
              "LandedPrice": {
                "CurrencyCode": "USD",
                "Amount": "249.99"
              },
              "Shipping": {
                "CurrencyCode": "USD",
                "Amount": "0.0"
              }
           
... (truncated)
```

**GET GET Competitive Pricing - by SKU** — `/products/pricing/v0/competitivePrice?Sku=FN-SOFA-RVT01&MarketplaceId=ATVPDKIKX0DER&ItemType=Sku` (status 200)

```
{
  "type": "competitive_pricing",
  "payload": {
    "ASIN": "B0FURN00001",
    "Product": {
      "CompetitivePricing": {
        "CompetitivePrices": [
          {
            "CompetitivePriceId": "1",
            "Price": {
              "ListingPrice": {
                "CurrencyCode": "USD",
                "Amount": "869.99"
              },
              "LandedPrice": {
                "CurrencyCode": "USD",
                "Amount": "899.99"
              },
              "Shipping": {
                "CurrencyCode": "USD",
                "Amount": "49.99"
              }
         
... (truncated)
```

**GET GET Competitive Pricing - 404** — `/products/pricing/v0/competitivePrice?Asin=B0NONEXIST&MarketplaceId=ATVPDKIKX0DER` (status 404)

```
{
  "error": "Pricing not found for B0NONEXIST"
}
```

**GET GET Item Offers** — `/products/pricing/v0/items/B0FURN00006/offers?MarketplaceId=ATVPDKIKX0DER&ItemCondition=New` (status 200)

```
{
  "type": "item_offers",
  "payload": {
    "ASIN": "B0FURN00006",
    "status": "Success",
    "ItemCondition": "New",
    "Summary": {
      "LowestPrices": [
        {
          "condition": "New",
          "fulfillmentChannel": "Amazon",
          "LandedPrice": {
            "CurrencyCode": "USD",
            "Amount": "234.99"
          },
          "ListingPrice": {
            "CurrencyCode": "USD",
            "Amount": "234.99"
          },
          "Shipping": {
            "CurrencyCode": "USD",
            "Amount": "0.0"
          }
        }
      ],
      "BuyBoxPrices": [

... (truncated)
```

**GET GET Item Offers - another ASIN** — `/products/pricing/v0/items/B0FURN00001/offers?MarketplaceId=ATVPDKIKX0DER&ItemCondition=New` (status 200)

```
{
  "type": "item_offers",
  "payload": {
    "ASIN": "B0FURN00001",
    "status": "Success",
    "ItemCondition": "New",
    "Summary": {
      "LowestPrices": [
        {
          "condition": "New",
          "fulfillmentChannel": "Amazon",
          "LandedPrice": {
            "CurrencyCode": "USD",
            "Amount": "869.99"
          },
          "ListingPrice": {
            "CurrencyCode": "USD",
            "Amount": "869.99"
          },
          "Shipping": {
            "CurrencyCode": "USD",
            "Amount": "49.99"
          }
        }
      ],
      "BuyBoxPrices": 
... (truncated)
```

**GET GET Item Offers - 404** — `/products/pricing/v0/items/B0NONEXIST/offers?MarketplaceId=ATVPDKIKX0DER` (status 404)

```
{
  "error": "Offers not found for ASIN B0NONEXIST"
}
```

**GET GET Returns - all** — `/returns/v0/returns` (status 200)

```
{
  "type": "returns",
  "count": 5,
  "total": 5,
  "offset": 0,
  "limit": 100,
  "results": [
    {
      "returnId": "RET-005",
      "AmazonOrderId": "114-8890123-6789000",
      "sellerSKU": "FN-BED-ZNS01",
      "asin": "B0FURN00003",
      "returnDate": "2026-04-10T16:00:00Z",
      "returnReason": "DEFECTIVE",
      "returnStatus": "Authorized",
      "returnQuantity": 1,
      "resolution": "PENDING",
      "refundAmount": 12.99,
      "refundCurrency": "USD",
      "buyerComments": "Screen protector has tiny bubbles that won't go away even with the alignment frame."
    },
    {
   
... (truncated)
```

**GET GET Returns - filter Authorized** — `/returns/v0/returns?status=Authorized` (status 200)

```
{
  "type": "returns",
  "count": 2,
  "total": 2,
  "offset": 0,
  "limit": 100,
  "results": [
    {
      "returnId": "RET-005",
      "AmazonOrderId": "114-8890123-6789000",
      "sellerSKU": "FN-BED-ZNS01",
      "asin": "B0FURN00003",
      "returnDate": "2026-04-10T16:00:00Z",
      "returnReason": "DEFECTIVE",
      "returnStatus": "Authorized",
      "returnQuantity": 1,
      "resolution": "PENDING",
      "refundAmount": 12.99,
      "refundCurrency": "USD",
      "buyerComments": "Screen protector has tiny bubbles that won't go away even with the alignment frame."
    },
    {
   
... (truncated)
```

**GET GET Returns - filter Completed** — `/returns/v0/returns?status=Completed` (status 200)

```
{
  "type": "returns",
  "count": 3,
  "total": 3,
  "offset": 0,
  "limit": 100,
  "results": [
    {
      "returnId": "RET-004",
      "AmazonOrderId": "114-9981234-5567800",
      "sellerSKU": "FN-SOFA-RVT01",
      "asin": "B0FURN00001",
      "returnDate": "2026-03-05T11:00:00Z",
      "returnReason": "NO_LONGER_NEEDED",
      "returnStatus": "Completed",
      "returnQuantity": 1,
      "resolution": "REFUND",
      "refundAmount": 34.99,
      "refundCurrency": "USD",
      "buyerComments": "Changed my mind. Got a different brand."
    },
    {
      "returnId": "RET-002",
      "Amazo
... (truncated)
```

**GET GET Returns - filter by order ID** — `/returns/v0/returns?orderId=114-3941689-8772200` (status 200)

```
{
  "type": "returns",
  "count": 1,
  "total": 1,
  "offset": 0,
  "limit": 100,
  "results": [
    {
      "returnId": "RET-001",
      "AmazonOrderId": "114-3941689-8772200",
      "sellerSKU": "FN-SOFA-RVT01",
      "asin": "B0FURN00001",
      "returnDate": "2026-02-18T10:00:00Z",
      "returnReason": "DEFECTIVE",
      "returnStatus": "Completed",
      "returnQuantity": 1,
      "resolution": "REFUND",
      "refundAmount": 19.99,
      "refundCurrency": "USD",
      "buyerComments": "Case cracked on first drop. Not what I expected from military grade protection."
    }
  ]
}
```

**GET GET Return by ID** — `/returns/v0/returns/RET-001` (status 200)

```
{
  "type": "return",
  "return": {
    "returnId": "RET-001",
    "AmazonOrderId": "114-3941689-8772200",
    "sellerSKU": "FN-SOFA-RVT01",
    "asin": "B0FURN00001",
    "returnDate": "2026-02-18T10:00:00Z",
    "returnReason": "DEFECTIVE",
    "returnStatus": "Completed",
    "returnQuantity": 1,
    "resolution": "REFUND",
    "refundAmount": 19.99,
    "refundCurrency": "USD",
    "buyerComments": "Case cracked on first drop. Not what I expected from military grade protection."
  }
}
```

**GET GET Return by ID - 404** — `/returns/v0/returns/RET-999` (status 404)

```
{
  "error": "Return RET-999 not found"
}
```

**POST POST Authorize Return** — `/returns/v0/returns/RET-003/authorize` (status 200)

```
{
  "type": "return_authorization",
  "status": "SUCCESS",
  "returnId": "RET-003"
}
```

**POST POST Close Return** — `/returns/v0/returns/RET-005/close` (status 200)

```
{
  "type": "return_close",
  "status": "SUCCESS",
  "returnId": "RET-005"
}
```

</details>

### amplitude-api (port 8091) — server: started

| Result | Method | Path | Status | Endpoint |
|--------|--------|------|--------|----------|
| PASS | GET | /health | 200 | health |
| PASS | POST | /2/httpapi | 200 | httpapi upload |
| PASS | GET | /api/2/events/segmentation?e=purchase&start=2026-05-02&end=2026-05-06 | 200 | segmentation |
| PASS | GET | /api/2/events/segmentation | 200 | segmentation all |
| PASS | GET | /api/2/useractivity?user=user_2001 | 200 | user activity |

<details><summary>responses</summary>

**GET health** — `/health` (status 200)

```
{
  "status": "ok"
}
```

**POST httpapi upload** — `/2/httpapi` (status 200)

```
{
  "code": 200,
  "events_ingested": 1,
  "server_upload_time": "2026-06-17T10:30:59Z"
}
```

**GET segmentation** — `/api/2/events/segmentation?e=purchase&start=2026-05-02&end=2026-05-06` (status 200)

```
{
  "data": {
    "series": [
      [
        3,
        5,
        8,
        6,
        9
      ]
    ],
    "seriesLabels": [
      "purchase"
    ],
    "xValues": [
      "2026-05-02",
      "2026-05-03",
      "2026-05-04",
      "2026-05-05",
      "2026-05-06"
    ]
  }
}
```

**GET segmentation all** — `/api/2/events/segmentation` (status 200)

```
{
  "data": {
    "series": [
      [
        3,
        5,
        8,
        6,
        9
      ],
      [
        120,
        134,
        128,
        141,
        150
      ]
    ],
    "seriesLabels": [
      "purchase",
      "session_start"
    ],
    "xValues": [
      "2026-05-02",
      "2026-05-03",
      "2026-05-04",
      "2026-05-05",
      "2026-05-06"
    ]
  }
}
```

**GET user activity** — `/api/2/useractivity?user=user_2001` (status 200)

```
{
  "userData": {
    "user_id": "user_2001",
    "device_id": "dev_aa01",
    "country": "United States",
    "platform": "web",
    "version": "4.2.0",
    "first_seen": "2026-04-20T08:00:00Z",
    "last_seen": "2026-05-05T09:45:51Z"
  },
  "events": [
    {
      "event_id": "ev_900001",
      "user_id": "user_2001",
      "device_id": "dev_aa01",
      "event_type": "session_start",
      "event_time": "2026-05-02T08:00:00Z",
      "event_properties": {
        "platform": "web"
      }
    },
    {
      "event_id": "ev_900002",
      "user_id": "user_2001",
      "device_id": "dev_aa01",
... (truncated)
```

</details>

### asana-api (port 8031) — server: started

| Result | Method | Path | Status | Endpoint |
|--------|--------|------|--------|----------|
| PASS | GET | /health | 200 | health |
| PASS | GET | /api/1.0/workspaces | 200 | list workspaces |
| PASS | GET | /api/1.0/users?workspace=1201990000000001 | 200 | list users |
| PASS | GET | /api/1.0/projects?workspace=1201990000000001 | 200 | list projects |
| PASS | GET | /api/1.0/projects/1203000000002001 | 200 | get project |
| PASS | GET | /api/1.0/projects/1203000000002001/sections | 200 | list project sections |
| PASS | GET | /api/1.0/projects/1203000000002001/tasks | 200 | list project tasks |
| PASS | GET | /api/1.0/tasks?project=1203000000002002&completed=false | 200 | list tasks |
| PASS | GET | /api/1.0/tasks/1205000000004001 | 200 | get task |
| PASS | POST | /api/1.0/tasks | 201 | create task |
| PASS | PUT | /api/1.0/tasks/1205000000004002 | 200 | complete task |

<details><summary>responses</summary>

**GET health** — `/health` (status 200)

```
{
  "status": "ok"
}
```

**GET list workspaces** — `/api/1.0/workspaces` (status 200)

```
{
  "data": [
    {
      "gid": "1201990000000001",
      "resource_type": "workspace",
      "name": "Northwind Studio"
    }
  ]
}
```

**GET list users** — `/api/1.0/users?workspace=1201990000000001` (status 200)

```
{
  "data": [
    {
      "gid": "1202000000001001",
      "resource_type": "user",
      "name": "Priya Raman",
      "email": "priya.raman@northwind-studio.com"
    },
    {
      "gid": "1202000000001002",
      "resource_type": "user",
      "name": "Daniel Cho",
      "email": "daniel.cho@northwind-studio.com"
    },
    {
      "gid": "1202000000001003",
      "resource_type": "user",
      "name": "Sofia Marquez",
      "email": "sofia.marquez@northwind-studio.com"
    },
    {
      "gid": "1202000000001004",
      "resource_type": "user",
      "name": "Liam OConnor",
      "email": "
```

**GET list projects** — `/api/1.0/projects?workspace=1201990000000001` (status 200)

```
{
  "data": [
    {
      "gid": "1203000000002001",
      "resource_type": "project",
      "name": "Website Redesign",
      "owner": {
        "gid": "1202000000001001",
        "resource_type": "user",
        "name": "Priya Raman"
      },
      "color": "dark-blue",
      "archived": false,
      "notes": "Q2 marketing site rebuild",
      "created_at": "2026-01-12T09:00:00.000Z"
    },
    {
      "gid": "1203000000002002",
      "resource_type": "project",
      "name": "Mobile App v2",
      "owner": {
        "gid": "1202000000001002",
        "resource_type": "user",
        "name":
... (truncated)
```

**GET get project** — `/api/1.0/projects/1203000000002001` (status 200)

```
{
  "data": {
    "gid": "1203000000002001",
    "resource_type": "project",
    "name": "Website Redesign",
    "owner": {
      "gid": "1202000000001001",
      "resource_type": "user",
      "name": "Priya Raman"
    },
    "color": "dark-blue",
    "archived": false,
    "notes": "Q2 marketing site rebuild",
    "created_at": "2026-01-12T09:00:00.000Z"
  }
}
```

**GET list project sections** — `/api/1.0/projects/1203000000002001/sections` (status 200)

```
{
  "data": [
    {
      "gid": "1204000000003001",
      "resource_type": "section",
      "name": "To Do",
      "project": {
        "gid": "1203000000002001",
        "resource_type": "project",
        "name": "Website Redesign"
      },
      "created_at": "2026-01-12T09:05:00.000Z"
    },
    {
      "gid": "1204000000003002",
      "resource_type": "section",
      "name": "In Progress",
      "project": {
        "gid": "1203000000002001",
        "resource_type": "project",
        "name": "Website Redesign"
      },
      "created_at": "2026-01-12T09:05:00.000Z"
    },
    {
      
... (truncated)
```

**GET list project tasks** — `/api/1.0/projects/1203000000002001/tasks` (status 200)

```
{
  "data": [
    {
      "gid": "1205000000004001",
      "resource_type": "task",
      "name": "Audit current site IA",
      "completed": true,
      "due_on": "2026-02-01",
      "notes": "Document existing page hierarchy",
      "created_at": "2026-01-13T10:00:00.000Z",
      "modified_at": "2026-02-01T16:00:00.000Z",
      "assignee": {
        "gid": "1202000000001001",
        "resource_type": "user",
        "name": "Priya Raman"
      },
      "memberships": [
        {
          "project": {
            "gid": "1203000000002001",
            "resource_type": "project",
            
... (truncated)
```

**GET list tasks** — `/api/1.0/tasks?project=1203000000002002&completed=false` (status 200)

```
{
  "data": [
    {
      "gid": "1205000000004005",
      "resource_type": "task",
      "name": "Set up offline cache layer",
      "completed": false,
      "due_on": "2026-06-15",
      "notes": "IndexedDB sync strategy",
      "created_at": "2026-02-10T15:00:00.000Z",
      "modified_at": "2026-05-24T17:30:00.000Z",
      "assignee": {
        "gid": "1202000000001002",
        "resource_type": "user",
        "name": "Daniel Cho"
      },
      "memberships": [
        {
          "project": {
            "gid": "1203000000002002",
            "resource_type": "project",
            "nam
... (truncated)
```

**GET get task** — `/api/1.0/tasks/1205000000004001` (status 200)

```
{
  "data": {
    "gid": "1205000000004001",
    "resource_type": "task",
    "name": "Audit current site IA",
    "completed": true,
    "due_on": "2026-02-01",
    "notes": "Document existing page hierarchy",
    "created_at": "2026-01-13T10:00:00.000Z",
    "modified_at": "2026-02-01T16:00:00.000Z",
    "assignee": {
      "gid": "1202000000001001",
      "resource_type": "user",
      "name": "Priya Raman"
    },
    "memberships": [
      {
        "project": {
          "gid": "1203000000002001",
          "resource_type": "project",
          "name": "Website Redesign"
        },
      
```

**POST create task** — `/api/1.0/tasks` (status 201)

```
{
  "data": {
    "gid": "2563539399383111",
    "resource_type": "task",
    "name": "Write release notes",
    "completed": false,
    "due_on": "2026-07-10",
    "notes": "Summarize v2 changes",
    "created_at": "2026-06-17T10:31:00.000Z",
    "modified_at": "2026-06-17T10:31:00.000Z",
    "assignee": {
      "gid": "1202000000001002",
      "resource_type": "user",
      "name": "Daniel Cho"
    },
    "memberships": [
      {
        "project": {
          "gid": "1203000000002002",
          "resource_type": "project",
          "name": "Mobile App v2"
        },
        "section": {
  
```

**PUT complete task** — `/api/1.0/tasks/1205000000004002` (status 200)

```
{
  "data": {
    "gid": "1205000000004002",
    "resource_type": "task",
    "name": "Design new homepage hero",
    "completed": false,
    "due_on": "2026-06-10",
    "notes": "Three variants for A/B test",
    "created_at": "2026-01-20T09:30:00.000Z",
    "modified_at": "2026-05-22T12:00:00.000Z",
    "assignee": {
      "gid": "1202000000001004",
      "resource_type": "user",
      "name": "Liam OConnor"
    },
    "memberships": [
      {
        "project": {
          "gid": "1203000000002001",
          "resource_type": "project",
          "name": "Website Redesign"
        },
      
```

</details>

### bamboohr-api (port 8072) — server: started

| Result | Method | Path | Status | Endpoint |
|--------|--------|------|--------|----------|
| PASS | GET | /health | 200 | health |
| PASS | GET | /api/gateway.php/orbitlabs/v1/company | 200 | get company |
| PASS | GET | /api/gateway.php/orbitlabs/v1/employees/directory | 200 | employees directory |
| PASS | GET | /api/gateway.php/orbitlabs/v1/employees/emp-102 | 200 | get employee |
| PASS | POST | /api/gateway.php/orbitlabs/v1/employees | 201 | create employee |
| PASS | GET | /api/gateway.php/orbitlabs/v1/time_off/requests?status=requested | 200 | list time off requests |
| PASS | POST | /api/gateway.php/orbitlabs/v1/time_off/requests | 201 | create time off request |
| PASS | PUT | /api/gateway.php/orbitlabs/v1/time_off/requests/tor-5003/status | 200 | approve time off request |
| PASS | GET | /api/gateway.php/orbitlabs/v1/time_off/whos_out | 200 | whos out |
| PASS | GET | /api/gateway.php/orbitlabs/v1/reports/1 | 200 | get report |

<details><summary>responses</summary>

**GET health** — `/health` (status 200)

```
{
  "status": "ok"
}
```

**GET get company** — `/api/gateway.php/orbitlabs/v1/company` (status 200)

```
{
  "subdomain": "orbitlabs",
  "name": "Orbit Labs Inc.",
  "employeeCount": 12,
  "industry": "Software",
  "headquarters": "San Francisco, CA",
  "fiscalYearStart": "01-01",
  "timeOffPolicies": [
    "Vacation",
    "Sick",
    "Personal",
    "Holiday"
  ]
}
```

**GET employees directory** — `/api/gateway.php/orbitlabs/v1/employees/directory` (status 200)

```
{
  "employees": [
    {
      "id": "emp-101",
      "firstName": "Amelia",
      "lastName": "Ortega",
      "workEmail": "amelia.ortega@orbit-labs.com",
      "department": "Engineering",
      "jobTitle": "VP of Engineering",
      "location": "San Francisco",
      "hireDate": "2019-03-04",
      "status": "Active",
      "supervisorId": null
    },
    {
      "id": "emp-102",
      "firstName": "Jonas",
      "lastName": "Pereira",
      "workEmail": "jonas.pereira@orbit-labs.com",
      "department": "Engineering",
      "jobTitle": "Staff Software Engineer",
      "location": "San Fra
... (truncated)
```

**GET get employee** — `/api/gateway.php/orbitlabs/v1/employees/emp-102` (status 200)

```
{
  "id": "emp-102",
  "firstName": "Jonas",
  "lastName": "Pereira",
  "workEmail": "jonas.pereira@orbit-labs.com",
  "department": "Engineering",
  "jobTitle": "Staff Software Engineer",
  "location": "San Francisco",
  "hireDate": "2020-06-15",
  "status": "Active",
  "supervisorId": "emp-101"
}
```

**POST create employee** — `/api/gateway.php/orbitlabs/v1/employees` (status 201)

```
{
  "id": "emp-fdaeeef9",
  "firstName": "Aisha",
  "lastName": "Khan",
  "workEmail": "aisha.khan@orbit-labs.com",
  "department": "Engineering",
  "jobTitle": "Software Engineer",
  "location": "Remote",
  "hireDate": "2026-06-17",
  "status": "Active",
  "supervisorId": "emp-102"
}
```

**GET list time off requests** — `/api/gateway.php/orbitlabs/v1/time_off/requests?status=requested` (status 200)

```
[
  {
    "id": "tor-5003",
    "employeeId": "emp-104",
    "type": "Vacation",
    "status": "requested",
    "start": "2026-07-01",
    "end": "2026-07-10",
    "amount": 8,
    "unit": "days",
    "notes": "Summer holiday",
    "created": "2026-05-22"
  },
  {
    "id": "tor-5006",
    "employeeId": "emp-108",
    "type": "Vacation",
    "status": "requested",
    "start": "2026-08-04",
    "end": "2026-08-15",
    "amount": 10,
    "unit": "days",
    "notes": "Annual leave",
    "created": "2026-05-25"
  },
  {
    "id": "tor-5008",
    "employeeId": "emp-112",
    "type": "Personal",
  
```

**POST create time off request** — `/api/gateway.php/orbitlabs/v1/time_off/requests` (status 201)

```
{
  "id": "tor-9fc07abe",
  "employeeId": "emp-104",
  "type": "Vacation",
  "status": "requested",
  "start": "2026-07-20",
  "end": "2026-07-24",
  "amount": 5,
  "unit": "days",
  "notes": "Conference travel",
  "created": "2026-06-17"
}
```

**PUT approve time off request** — `/api/gateway.php/orbitlabs/v1/time_off/requests/tor-5003/status` (status 200)

```
{
  "id": "tor-5003",
  "employeeId": "emp-104",
  "type": "Vacation",
  "status": "approved",
  "start": "2026-07-01",
  "end": "2026-07-10",
  "amount": 8,
  "unit": "days",
  "notes": "Summer holiday",
  "created": "2026-05-22"
}
```

**GET whos out** — `/api/gateway.php/orbitlabs/v1/time_off/whos_out` (status 200)

```
[
  {
    "id": "who-9001",
    "employeeId": "emp-102",
    "name": "Jonas Pereira",
    "type": "Vacation",
    "start": "2026-06-08",
    "end": "2026-06-12"
  },
  {
    "id": "who-9002",
    "employeeId": "emp-107",
    "name": "Yuki Tanaka",
    "type": "Vacation",
    "start": "2026-05-28",
    "end": "2026-05-30"
  },
  {
    "id": "who-9003",
    "employeeId": "emp-105",
    "name": "Noor Aziz",
    "type": "Sick",
    "start": "2026-05-26",
    "end": "2026-05-26"
  },
  {
    "id": "who-9004",
    "employeeId": "emp-103",
    "name": "Helena Park",
    "type": "Vacation",
    "start
```

**GET get report** — `/api/gateway.php/orbitlabs/v1/reports/1` (status 200)

```
{
  "title": "Headcount by Department",
  "fields": [
    {
      "id": "department",
      "name": "Department"
    },
    {
      "id": "headcount",
      "name": "Headcount"
    }
  ],
  "employees": [
    {
      "department": "Engineering",
      "headcount": 4
    },
    {
      "department": "Executive",
      "headcount": 1
    },
    {
      "department": "Marketing",
      "headcount": 2
    },
    {
      "department": "People",
      "headcount": 2
    },
    {
      "department": "Sales",
      "headcount": 2
    }
  ]
}
```

</details>

### bigcommerce-api (port 8084) — server: started

| Result | Method | Path | Status | Endpoint |
|--------|--------|------|--------|----------|
| PASS | GET | /health | 200 | health |
| PASS | GET | /v3/catalog/products?limit=5&page=1 | 200 | list products |
| PASS | GET | /v3/catalog/products?name=wireless | 200 | filter products by name |
| PASS | GET | /v3/catalog/products/101 | 200 | get product |
| PASS | GET | /v2/orders?customer_id=1001 | 200 | list orders |
| PASS | GET | /v2/orders/2001 | 200 | get order |
| PASS | POST | /v2/orders | 200 | create order |
| PASS | GET | /v3/customers?email=olivia | 200 | list customers |

<details><summary>responses</summary>

**GET health** — `/health` (status 200)

```
{
  "status": "ok"
}
```

**GET list products** — `/v3/catalog/products?limit=5&page=1` (status 200)

```
{
  "data": [
    {
      "id": 101,
      "name": "Aurora Wireless Headphones",
      "sku": "AUR-WH-001",
      "type": "physical",
      "price": 149.99,
      "sale_price": 129.99,
      "cost_price": 72.5,
      "weight": 0.45,
      "inventory_level": 120,
      "inventory_tracking": "product",
      "is_visible": true,
      "brand_id": 11,
      "categories": [
        21,
        24
      ],
      "description": "Over-ear wireless headphones with ANC",
      "date_created": "2026-01-12T08:00:00Z"
    },
    {
      "id": 102,
      "name": "Nimbus Bluetooth Speaker",
      "sku": "NIM
... (truncated)
```

**GET filter products by name** — `/v3/catalog/products?name=wireless` (status 200)

```
{
  "data": [
    {
      "id": 101,
      "name": "Aurora Wireless Headphones",
      "sku": "AUR-WH-001",
      "type": "physical",
      "price": 149.99,
      "sale_price": 129.99,
      "cost_price": 72.5,
      "weight": 0.45,
      "inventory_level": 120,
      "inventory_tracking": "product",
      "is_visible": true,
      "brand_id": 11,
      "categories": [
        21,
        24
      ],
      "description": "Over-ear wireless headphones with ANC",
      "date_created": "2026-01-12T08:00:00Z"
    }
  ],
  "meta": {
    "pagination": {
      "total": 1,
      "count": 1,
      "per
```

**GET get product** — `/v3/catalog/products/101` (status 200)

```
{
  "data": {
    "id": 101,
    "name": "Aurora Wireless Headphones",
    "sku": "AUR-WH-001",
    "type": "physical",
    "price": 149.99,
    "sale_price": 129.99,
    "cost_price": 72.5,
    "weight": 0.45,
    "inventory_level": 120,
    "inventory_tracking": "product",
    "is_visible": true,
    "brand_id": 11,
    "categories": [
      21,
      24
    ],
    "description": "Over-ear wireless headphones with ANC",
    "date_created": "2026-01-12T08:00:00Z"
  },
  "meta": {}
}
```

**GET list orders** — `/v2/orders?customer_id=1001` (status 200)

```
[
  {
    "id": 2001,
    "customer_id": 1001,
    "status_id": 2,
    "status": "Shipped",
    "total_inc_tax": "159.98",
    "subtotal_inc_tax": "149.99",
    "currency_code": "USD",
    "payment_method": "Credit Card",
    "items_total": 1,
    "date_created": "2026-04-02T10:05:00Z",
    "billing_address": {
      "first_name": "Olivia",
      "last_name": "Bennett",
      "email": "olivia.bennett@example.com"
    }
  },
  {
    "id": 2006,
    "customer_id": 1001,
    "status_id": 2,
    "status": "Shipped",
    "total_inc_tax": "79.99",
    "subtotal_inc_tax": "69.99",
    "currency_code"
... (truncated)
```

**GET get order** — `/v2/orders/2001` (status 200)

```
{
  "id": 2001,
  "customer_id": 1001,
  "status_id": 2,
  "status": "Shipped",
  "total_inc_tax": "159.98",
  "subtotal_inc_tax": "149.99",
  "currency_code": "USD",
  "payment_method": "Credit Card",
  "items_total": 1,
  "date_created": "2026-04-02T10:05:00Z",
  "billing_address": {
    "first_name": "Olivia",
    "last_name": "Bennett",
    "email": "olivia.bennett@example.com"
  }
}
```

**POST create order** — `/v2/orders` (status 200)

```
{
  "id": 2007,
  "customer_id": 1002,
  "status_id": 1,
  "status": "Pending",
  "total_inc_tax": "239.00",
  "subtotal_inc_tax": "239.00",
  "currency_code": "USD",
  "payment_method": "Credit Card",
  "items_total": 2,
  "date_created": "2026-05-28T00:00:00Z",
  "billing_address": {
    "first_name": "Marcus",
    "last_name": "Lee",
    "email": "marcus.lee@example.com"
  }
}
```

**GET list customers** — `/v3/customers?email=olivia` (status 200)

```
{
  "data": [
    {
      "id": 1001,
      "first_name": "Olivia",
      "last_name": "Bennett",
      "email": "olivia.bennett@example.com",
      "company": "Bennett Studio",
      "phone": "+1-415-555-0110",
      "customer_group_id": 2,
      "date_created": "2026-01-05T10:00:00Z"
    }
  ],
  "meta": {
    "pagination": {
      "total": 1,
      "count": 1,
      "per_page": 50,
      "current_page": 1,
      "total_pages": 1
    }
  }
}
```

</details>

### binance-api (port 8097) — server: started

| Result | Method | Path | Status | Endpoint |
|--------|--------|------|--------|----------|
| PASS | GET | /health | 200 | health |
| PASS | GET | /api/v3/ticker/price | 200 | ticker price all |
| PASS | GET | /api/v3/ticker/price?symbol=BTCUSDT | 200 | ticker price symbol |
| PASS | GET | /api/v3/ticker/24hr?symbol=ETHUSDT | 200 | ticker 24hr |
| PASS | GET | /api/v3/depth?symbol=BTCUSDT&limit=5 | 200 | depth |
| PASS | GET | /api/v3/klines?symbol=BTCUSDT&interval=1h | 200 | klines |
| PASS | GET | /api/v3/account | 200 | account |

<details><summary>responses</summary>

**GET health** — `/health` (status 200)

```
{
  "status": "ok"
}
```

**GET ticker price all** — `/api/v3/ticker/price` (status 200)

```
[
  {
    "symbol": "BTCUSDT",
    "price": "67250.45000000"
  },
  {
    "symbol": "ETHUSDT",
    "price": "3520.18000000"
  },
  {
    "symbol": "BNBUSDT",
    "price": "592.74000000"
  },
  {
    "symbol": "SOLUSDT",
    "price": "168.92000000"
  },
  {
    "symbol": "XRPUSDT",
    "price": "0.52340000"
  },
  {
    "symbol": "ADAUSDT",
    "price": "0.46120000"
  },
  {
    "symbol": "DOGEUSDT",
    "price": "0.15820000"
  },
  {
    "symbol": "MATICUSDT",
    "price": "0.72450000"
  },
  {
    "symbol": "DOTUSDT",
    "price": "7.21400000"
  },
  {
    "symbol": "LTCUSDT",
    "price": "8
```

**GET ticker price symbol** — `/api/v3/ticker/price?symbol=BTCUSDT` (status 200)

```
{
  "symbol": "BTCUSDT",
  "price": "67250.45000000"
}
```

**GET ticker 24hr** — `/api/v3/ticker/24hr?symbol=ETHUSDT` (status 200)

```
{
  "symbol": "ETHUSDT",
  "priceChange": "-45.32000000",
  "priceChangePercent": "-1.271",
  "lastPrice": "3520.18000000",
  "highPrice": "3601.40000000",
  "lowPrice": "3480.05000000",
  "volume": "92344.11800000"
}
```

**GET depth** — `/api/v3/depth?symbol=BTCUSDT&limit=5` (status 200)

```
{
  "lastUpdateId": 1027024,
  "bids": [
    [
      "67250.00000000",
      "0.51200000"
    ],
    [
      "67249.50000000",
      "1.23000000"
    ],
    [
      "67248.10000000",
      "0.87500000"
    ],
    [
      "67247.00000000",
      "2.14000000"
    ],
    [
      "67245.20000000",
      "0.33000000"
    ]
  ],
  "asks": [
    [
      "67251.00000000",
      "0.64000000"
    ],
    [
      "67252.40000000",
      "1.08000000"
    ],
    [
      "67253.90000000",
      "0.42000000"
    ],
    [
      "67255.00000000",
      "1.77000000"
    ],
    [
      "67256.80000000",
      "0.
```

**GET klines** — `/api/v3/klines?symbol=BTCUSDT&interval=1h` (status 200)

```
[
  [
    1779004800000,
    "66100.00000000",
    "66480.00000000",
    "66020.50000000",
    "66410.20000000",
    "812.44100000",
    1779008399999,
    "53954369.29820000",
    0,
    "0",
    "0",
    "0"
  ],
  [
    1779008400000,
    "66410.20000000",
    "66900.00000000",
    "66380.00000000",
    "66850.75000000",
    "945.11800000",
    1779011999999,
    "63181847.13850001",
    0,
    "0",
    "0",
    "0"
  ],
  [
    1779012000000,
    "66850.75000000",
    "67200.00000000",
    "66800.10000000",
    "67120.40000000",
    "1023.66700000",
    1779015599999,
    "68708938.5068000
... (truncated)
```

**GET account** — `/api/v3/account` (status 200)

```
{
  "makerCommission": 10,
  "takerCommission": 10,
  "buyerCommission": 0,
  "sellerCommission": 0,
  "canTrade": true,
  "canWithdraw": true,
  "canDeposit": true,
  "accountType": "SPOT",
  "balances": [
    {
      "asset": "BTC",
      "free": "0.45821000",
      "locked": "0.01000000"
    },
    {
      "asset": "ETH",
      "free": "3.20140000",
      "locked": "0.50000000"
    },
    {
      "asset": "BNB",
      "free": "12.40000000",
      "locked": "0.00000000"
    },
    {
      "asset": "SOL",
      "free": "85.00000000",
      "locked": "5.00000000"
    },
    {
      "asset": "U
... (truncated)
```

</details>

### box-api (port 8083) — server: started

| Result | Method | Path | Status | Endpoint |
|--------|--------|------|--------|----------|
| PASS | GET | /health | 200 | health |
| PASS | GET | /2.0/users/me | 200 | current user |
| PASS | GET | /2.0/folders/0 | 200 | get root folder |
| PASS | GET | /2.0/folders/0/items?limit=10&offset=0 | 200 | get folder items |
| PASS | GET | /2.0/folders/160001/items | 200 | get marketing folder items |
| PASS | GET | /2.0/files/500001 | 200 | get file |
| PASS | GET | /2.0/search?query=campaign&type=file | 200 | search |

<details><summary>responses</summary>

**GET health** — `/health` (status 200)

```
{
  "status": "ok"
}
```

**GET current user** — `/2.0/users/me` (status 200)

```
{
  "type": "user",
  "id": "11446498",
  "name": "Aaron Levie",
  "login": "aaron@example.com",
  "role": "admin",
  "status": "active",
  "language": "en",
  "timezone": "America/Los_Angeles",
  "space_amount": 10995116277760,
  "space_used": 2147483648,
  "max_upload_size": 5368709120,
  "job_title": "CEO",
  "phone": "+1-650-555-0100",
  "created_at": "2025-09-01T10:00:00-07:00"
}
```

**GET get root folder** — `/2.0/folders/0` (status 200)

```
{
  "type": "folder",
  "id": "0",
  "name": "All Files",
  "description": "Root folder",
  "size": 0,
  "created_at": "2025-09-01T10:00:00-07:00",
  "modified_at": "2026-05-20T14:00:00-07:00",
  "item_count": 3,
  "parent": null,
  "owned_by": {
    "type": "user",
    "id": "11446498",
    "name": "Aaron Levie",
    "login": "aaron@example.com"
  }
}
```

**GET get folder items** — `/2.0/folders/0/items?limit=10&offset=0` (status 200)

```
{
  "total_count": 3,
  "entries": [
    {
      "type": "folder",
      "id": "160001",
      "name": "Marketing",
      "description": "Marketing collateral and assets",
      "size": 7086592,
      "created_at": "2025-10-01T09:00:00-07:00",
      "modified_at": "2026-05-18T16:20:00-07:00",
      "item_count": 3,
      "parent": {
        "type": "folder",
        "id": "0",
        "name": "All Files"
      },
      "owned_by": {
        "type": "user",
        "id": "11446498",
        "name": "Aaron Levie",
        "login": "aaron@example.com"
      }
    },
    {
      "type": "folder",

... (truncated)
```

**GET get marketing folder items** — `/2.0/folders/160001/items` (status 200)

```
{
  "total_count": 4,
  "entries": [
    {
      "type": "folder",
      "id": "160004",
      "name": "Campaigns",
      "description": "Active campaign folder",
      "size": 72704,
      "created_at": "2026-02-10T11:00:00-08:00",
      "modified_at": "2026-05-10T12:00:00-08:00",
      "item_count": 1,
      "parent": {
        "type": "folder",
        "id": "160001",
        "name": "Marketing"
      },
      "owned_by": {
        "type": "user",
        "id": "22893011",
        "name": "Priya Nair",
        "login": "priya@example.com"
      }
    },
    {
      "type": "file",
      "id
... (truncated)
```

**GET get file** — `/2.0/files/500001` (status 200)

```
{
  "type": "file",
  "id": "500001",
  "name": "brand-guidelines.pdf",
  "description": "Brand guidelines v3",
  "size": 1843200,
  "extension": "pdf",
  "sha1": "a1b2c3d4e5f60718293a4b5c6d7e8f9012345601",
  "created_at": "2026-03-01T10:00:00-08:00",
  "modified_at": "2026-05-12T09:00:00-07:00",
  "parent": {
    "type": "folder",
    "id": "160001",
    "name": "Marketing"
  },
  "owned_by": {
    "type": "user",
    "id": "11446498",
    "name": "Aaron Levie",
    "login": "aaron@example.com"
  }
}
```

**GET search** — `/2.0/search?query=campaign&type=file` (status 200)

```
{
  "total_count": 1,
  "entries": [
    {
      "type": "file",
      "id": "500003",
      "name": "q2-campaign-plan.docx",
      "description": "Q2 campaign plan",
      "size": 72704,
      "extension": "docx",
      "sha1": "a1b2c3d4e5f60718293a4b5c6d7e8f9012345603",
      "created_at": "2026-04-15T09:20:00-07:00",
      "modified_at": "2026-05-10T12:00:00-07:00",
      "parent": {
        "type": "folder",
        "id": "160004",
        "name": "Campaigns"
      },
      "owned_by": {
        "type": "user",
        "id": "22893011",
        "name": "Priya Nair",
        "login": "priya
```

</details>

### calendly-api (port 8054) — server: started

| Result | Method | Path | Status | Endpoint |
|--------|--------|------|--------|----------|
| PASS | GET | /health | 200 | health |
| PASS | GET | /users/me | 200 | get me |
| PASS | GET | /event_types?user=user-amelia-ortega | 200 | list event types |
| PASS | GET | /event_types/et-discovery-30 | 200 | get event type |
| PASS | GET | /scheduled_events?user=user-amelia-ortega&status=active | 200 | list scheduled events |
| PASS | GET | /scheduled_events/sev-1001 | 200 | get scheduled event |
| PASS | GET | /scheduled_events/sev-1001/invitees | 200 | list invitees |
| PASS | POST | /scheduled_events | 201 | book event |
| PASS | POST | /scheduled_events/sev-1002/cancellation | 200 | cancel event |

<details><summary>responses</summary>

**GET health** — `/health` (status 200)

```
{
  "status": "ok"
}
```

**GET get me** — `/users/me` (status 200)

```
{
  "resource": {
    "uri": "https://api.calendly.com/users/user-amelia-ortega",
    "name": "Amelia Ortega",
    "slug": "amelia-ortega",
    "email": "amelia.ortega@orbit-labs.com",
    "scheduling_url": "https://calendly.com/amelia-ortega",
    "timezone": "America/Los_Angeles",
    "current_organization": "https://api.calendly.com/organizations/org-orbit-labs",
    "created_at": "2025-09-01T10:00:00.000000Z",
    "updated_at": "2026-05-20T14:00:00.000000Z"
  }
}
```

**GET list event types** — `/event_types?user=user-amelia-ortega` (status 200)

```
{
  "collection": [
    {
      "uri": "https://api.calendly.com/event_types/et-intro-15",
      "name": "Intro Call",
      "slug": "intro-call",
      "duration": 15,
      "kind": "solo",
      "color": "#0069ff",
      "active": true,
      "description_plain": "Quick 15-minute introduction call",
      "scheduling_url": "https://calendly.com/amelia-ortega/intro-call",
      "profile": {
        "owner": "https://api.calendly.com/users/user-amelia-ortega"
      },
      "created_at": "2025-09-02T10:00:00.000000Z"
    },
    {
      "uri": "https://api.calendly.com/event_types/et-discovery-
... (truncated)
```

**GET get event type** — `/event_types/et-discovery-30` (status 200)

```
{
  "resource": {
    "uri": "https://api.calendly.com/event_types/et-discovery-30",
    "name": "Discovery Session",
    "slug": "discovery-session",
    "duration": 30,
    "kind": "solo",
    "color": "#1aa763",
    "active": true,
    "description_plain": "30-minute product discovery session",
    "scheduling_url": "https://calendly.com/amelia-ortega/discovery-session",
    "profile": {
      "owner": "https://api.calendly.com/users/user-amelia-ortega"
    },
    "created_at": "2025-09-02T10:05:00.000000Z"
  }
}
```

**GET list scheduled events** — `/scheduled_events?user=user-amelia-ortega&status=active` (status 200)

```
{
  "collection": [
    {
      "uri": "https://api.calendly.com/scheduled_events/sev-1001",
      "name": "Intro Call",
      "status": "active",
      "start_time": "2026-05-28T17:00:00.000000Z",
      "end_time": "2026-05-28T17:15:00.000000Z",
      "event_type": "https://api.calendly.com/event_types/et-intro-15",
      "location": {
        "type": "zoom",
        "location": "https://zoom.us/j/8801234567"
      },
      "event_memberships": [
        {
          "user": "https://api.calendly.com/users/user-amelia-ortega"
        }
      ],
      "cancellation": null,
      "created_at": "
... (truncated)
```

**GET get scheduled event** — `/scheduled_events/sev-1001` (status 200)

```
{
  "resource": {
    "uri": "https://api.calendly.com/scheduled_events/sev-1001",
    "name": "Intro Call",
    "status": "active",
    "start_time": "2026-05-28T17:00:00.000000Z",
    "end_time": "2026-05-28T17:15:00.000000Z",
    "event_type": "https://api.calendly.com/event_types/et-intro-15",
    "location": {
      "type": "zoom",
      "location": "https://zoom.us/j/8801234567"
    },
    "event_memberships": [
      {
        "user": "https://api.calendly.com/users/user-amelia-ortega"
      }
    ],
    "cancellation": null,
    "created_at": "2026-05-25T09:00:00.000000Z"
  }
}
```

**GET list invitees** — `/scheduled_events/sev-1001/invitees` (status 200)

```
{
  "collection": [
    {
      "uri": "https://api.calendly.com/scheduled_events/sev-1001/invitees/inv-5001",
      "name": "Maria Chen",
      "email": "maria.chen@acme-corp.com",
      "status": "active",
      "timezone": "America/New_York",
      "event": "https://api.calendly.com/scheduled_events/sev-1001",
      "questions_and_answers": [
        {
          "question": "What would you like to discuss?",
          "answer": "Pricing and onboarding"
        }
      ],
      "created_at": "2026-05-25T09:00:00.000000Z"
    }
  ],
  "pagination": {
    "count": 1,
    "next_page": null
  }

```

**POST book event** — `/scheduled_events` (status 201)

```
{
  "resource": {
    "uri": "https://api.calendly.com/scheduled_events/sev-4ca4b37be1af",
    "name": "Intro Call",
    "status": "active",
    "start_time": "2026-06-03T17:00:00.000000Z",
    "end_time": "2026-06-03T17:15:00.000000Z",
    "event_type": "https://api.calendly.com/event_types/et-intro-15",
    "location": {
      "type": "zoom",
      "location": "https://zoom.us/j/8801234999"
    },
    "event_memberships": [
      {
        "user": "https://api.calendly.com/users/user-amelia-ortega"
      }
    ],
    "cancellation": null,
    "created_at": "2026-06-17T10:31:02.000000Z"
  }
}
```

**POST cancel event** — `/scheduled_events/sev-1002/cancellation` (status 200)

```
{
  "resource": {
    "canceled_by": "Amelia Ortega",
    "reason": "Host out of office",
    "canceler_type": "host"
  }
}
```

</details>

### cloudflare-api (port 8050) — server: started

| Result | Method | Path | Status | Endpoint |
|--------|--------|------|--------|----------|
| PASS | GET | /health | 200 | health |
| PASS | GET | /client/v4/zones | 200 | list zones |
| PASS | GET | /client/v4/zones/zone1aaaa1111bbbb2222cccc3333dddd | 200 | get zone |
| PASS | GET | /client/v4/zones/zone1aaaa1111bbbb2222cccc3333dddd/dns_records | 200 | list dns records |
| PASS | GET | /client/v4/zones/zone1aaaa1111bbbb2222cccc3333dddd/dns_records?type=A | 200 | list dns records by type |
| PASS | GET | /client/v4/zones/zone1aaaa1111bbbb2222cccc3333dddd/dns_records/rec0001aaaa | 200 | get dns record |
| PASS | POST | /client/v4/zones/zone1aaaa1111bbbb2222cccc3333dddd/dns_records | 200 | create dns record |
| PASS | PUT | /client/v4/zones/zone1aaaa1111bbbb2222cccc3333dddd/dns_records/rec0001aaaa | 200 | update dns record |
| PASS | DELETE | /client/v4/zones/zone1aaaa1111bbbb2222cccc3333dddd/dns_records/rec0005eeee | 200 | delete dns record |
| PASS | GET | /client/v4/zones/zone1aaaa1111bbbb2222cccc3333dddd/firewall/rules | 200 | list firewall rules |

<details><summary>responses</summary>

**GET health** — `/health` (status 200)

```
{
  "status": "ok"
}
```

**GET list zones** — `/client/v4/zones` (status 200)

```
{
  "success": true,
  "errors": [],
  "messages": [],
  "result": [
    {
      "id": "zone1aaaa1111bbbb2222cccc3333dddd",
      "name": "orbit-labs.com",
      "status": "active",
      "paused": false,
      "type": "full",
      "development_mode": 0,
      "plan": {
        "name": "Pro"
      },
      "created_on": "2024-01-10T10:00:00.000Z",
      "modified_on": "2026-05-26T09:00:00.000Z"
    },
    {
      "id": "zone2eeee4444ffff5555gggg6666hhhh",
      "name": "orbit-cdn.net",
      "status": "active",
      "paused": false,
      "type": "full",
      "development_mode": 0,
      "p
```

**GET get zone** — `/client/v4/zones/zone1aaaa1111bbbb2222cccc3333dddd` (status 200)

```
{
  "success": true,
  "errors": [],
  "messages": [],
  "result": {
    "id": "zone1aaaa1111bbbb2222cccc3333dddd",
    "name": "orbit-labs.com",
    "status": "active",
    "paused": false,
    "type": "full",
    "development_mode": 0,
    "plan": {
      "name": "Pro"
    },
    "created_on": "2024-01-10T10:00:00.000Z",
    "modified_on": "2026-05-26T09:00:00.000Z"
  }
}
```

**GET list dns records** — `/client/v4/zones/zone1aaaa1111bbbb2222cccc3333dddd/dns_records` (status 200)

```
{
  "success": true,
  "errors": [],
  "messages": [],
  "result": [
    {
      "id": "rec0001aaaa",
      "zone_id": "zone1aaaa1111bbbb2222cccc3333dddd",
      "type": "A",
      "name": "orbit-labs.com",
      "content": "203.0.113.10",
      "ttl": 1,
      "proxied": true,
      "priority": 0,
      "created_on": "2024-01-10T10:00:00.000Z",
      "modified_on": "2026-05-20T10:00:00.000Z"
    },
    {
      "id": "rec0002bbbb",
      "zone_id": "zone1aaaa1111bbbb2222cccc3333dddd",
      "type": "A",
      "name": "www.orbit-labs.com",
      "content": "203.0.113.10",
      "ttl": 1,
      
... (truncated)
```

**GET list dns records by type** — `/client/v4/zones/zone1aaaa1111bbbb2222cccc3333dddd/dns_records?type=A` (status 200)

```
{
  "success": true,
  "errors": [],
  "messages": [],
  "result": [
    {
      "id": "rec0001aaaa",
      "zone_id": "zone1aaaa1111bbbb2222cccc3333dddd",
      "type": "A",
      "name": "orbit-labs.com",
      "content": "203.0.113.10",
      "ttl": 1,
      "proxied": true,
      "priority": 0,
      "created_on": "2024-01-10T10:00:00.000Z",
      "modified_on": "2026-05-20T10:00:00.000Z"
    },
    {
      "id": "rec0002bbbb",
      "zone_id": "zone1aaaa1111bbbb2222cccc3333dddd",
      "type": "A",
      "name": "www.orbit-labs.com",
      "content": "203.0.113.10",
      "ttl": 1,
      
```

**GET get dns record** — `/client/v4/zones/zone1aaaa1111bbbb2222cccc3333dddd/dns_records/rec0001aaaa` (status 200)

```
{
  "success": true,
  "errors": [],
  "messages": [],
  "result": {
    "id": "rec0001aaaa",
    "zone_id": "zone1aaaa1111bbbb2222cccc3333dddd",
    "type": "A",
    "name": "orbit-labs.com",
    "content": "203.0.113.10",
    "ttl": 1,
    "proxied": true,
    "priority": 0,
    "created_on": "2024-01-10T10:00:00.000Z",
    "modified_on": "2026-05-20T10:00:00.000Z"
  }
}
```

**POST create dns record** — `/client/v4/zones/zone1aaaa1111bbbb2222cccc3333dddd/dns_records` (status 200)

```
{
  "success": true,
  "errors": [],
  "messages": [],
  "result": {
    "id": "ceff9c32855244088cf3d7dd7c4e0788325c99d6",
    "zone_id": "zone1aaaa1111bbbb2222cccc3333dddd",
    "type": "A",
    "name": "docs.orbit-labs.com",
    "content": "203.0.113.55",
    "ttl": 3600,
    "proxied": true,
    "priority": 0,
    "created_on": "2026-06-17T10:31:03.000000Z",
    "modified_on": "2026-06-17T10:31:03.000000Z"
  }
}
```

**PUT update dns record** — `/client/v4/zones/zone1aaaa1111bbbb2222cccc3333dddd/dns_records/rec0001aaaa` (status 200)

```
{
  "success": true,
  "errors": [],
  "messages": [],
  "result": {
    "id": "rec0001aaaa",
    "zone_id": "zone1aaaa1111bbbb2222cccc3333dddd",
    "type": "A",
    "name": "orbit-labs.com",
    "content": "203.0.113.10",
    "ttl": 1,
    "proxied": true,
    "priority": 0,
    "created_on": "2024-01-10T10:00:00.000Z",
    "modified_on": "2026-05-20T10:00:00.000Z"
  }
}
```

**DELETE delete dns record** — `/client/v4/zones/zone1aaaa1111bbbb2222cccc3333dddd/dns_records/rec0005eeee` (status 200)

```
{
  "success": true,
  "errors": [],
  "messages": [],
  "result": {
    "id": "rec0005eeee"
  }
}
```

**GET list firewall rules** — `/client/v4/zones/zone1aaaa1111bbbb2222cccc3333dddd/firewall/rules` (status 200)

```
{
  "success": true,
  "errors": [],
  "messages": [],
  "result": [
    {
      "id": "fw0001aaaa",
      "description": "Block known bad bots",
      "action": "block",
      "filter": {
        "expression": "(cf.client.bot and not cf.verified_bot_category eq \"\")"
      },
      "paused": false,
      "priority": 1,
      "created_on": "2024-04-01T10:00:00.000Z"
    },
    {
      "id": "fw0002bbbb",
      "description": "Challenge high threat score",
      "action": "challenge",
      "filter": {
        "expression": "(cf.threat_score gt 30)"
      },
      "paused": false,
      "prior
... (truncated)
```

</details>

### coinbase-api (port 8023) — server: started

| Result | Method | Path | Status | Endpoint |
|--------|--------|------|--------|----------|
| PASS | GET | /health | 200 | health |
| PASS | GET | /v2/user | 200 | get user |
| PASS | GET | /v2/accounts | 200 | list accounts |
| PASS | GET | /v2/accounts/acct-btc-001 | 200 | get account |
| PASS | GET | /v2/prices/BTC-USD/spot | 200 | get spot price BTC-USD |
| PASS | GET | /v2/prices/ETH-USD/spot | 200 | get spot price ETH-USD |
| PASS | POST | /v2/accounts/acct-btc-001/buys | 201 | create buy |
| PASS | POST | /v2/accounts/acct-eth-002/sells | 201 | create sell |
| PASS | GET | /v2/accounts/acct-btc-001/transactions | 200 | list transactions |

<details><summary>responses</summary>

**GET health** — `/health` (status 200)

```
{
  "status": "ok"
}
```

**GET get user** — `/v2/user` (status 200)

```
{
  "data": {
    "id": "user-orbit-001",
    "name": "Amelia Ortega",
    "username": "amelia.ortega",
    "profile_location": "Portland, OR",
    "email": "amelia.ortega@orbit-labs.com",
    "country": {
      "code": "US",
      "name": "United States"
    },
    "native_currency": "USD",
    "created_at": "2025-01-10T09:00:00Z"
  }
}
```

**GET list accounts** — `/v2/accounts` (status 200)

```
{
  "data": [
    {
      "id": "acct-btc-001",
      "name": "BTC Wallet",
      "primary": true,
      "type": "wallet",
      "currency": {
        "code": "BTC",
        "name": "Bitcoin"
      },
      "balance": {
        "amount": "0.45120000",
        "currency": "BTC"
      },
      "native_balance": {
        "amount": "29328.00",
        "currency": "USD"
      },
      "created_at": "2025-01-10T09:00:00Z",
      "updated_at": "2026-05-20T12:00:00Z"
    },
    {
      "id": "acct-eth-002",
      "name": "ETH Wallet",
      "primary": false,
      "type": "wallet",
      "currency": 
... (truncated)
```

**GET get account** — `/v2/accounts/acct-btc-001` (status 200)

```
{
  "data": {
    "id": "acct-btc-001",
    "name": "BTC Wallet",
    "primary": true,
    "type": "wallet",
    "currency": {
      "code": "BTC",
      "name": "Bitcoin"
    },
    "balance": {
      "amount": "0.45120000",
      "currency": "BTC"
    },
    "native_balance": {
      "amount": "29328.00",
      "currency": "USD"
    },
    "created_at": "2025-01-10T09:00:00Z",
    "updated_at": "2026-05-20T12:00:00Z"
  }
}
```

**GET get spot price BTC-USD** — `/v2/prices/BTC-USD/spot` (status 200)

```
{
  "data": {
    "base": "BTC",
    "currency": "USD",
    "amount": "65000.00"
  }
}
```

**GET get spot price ETH-USD** — `/v2/prices/ETH-USD/spot` (status 200)

```
{
  "data": {
    "base": "ETH",
    "currency": "USD",
    "amount": "3100.00"
  }
}
```

**POST create buy** — `/v2/accounts/acct-btc-001/buys` (status 201)

```
{
  "data": {
    "id": "c8bd1e5b-ee26-4b31-a2bd-56f2a47377e8",
    "status": "completed",
    "resource": "buy",
    "amount": {
      "amount": "0.05000000",
      "currency": "BTC"
    },
    "total": {
      "amount": "3250.00",
      "currency": "USD"
    },
    "unit_price": {
      "amount": "65000.00",
      "currency": "USD"
    },
    "account_id": "acct-btc-001",
    "transaction_id": "8f187553-beb1-4548-b69d-ed5940f435ca",
    "created_at": "2026-06-17T10:31:04Z"
  }
}
```

**POST create sell** — `/v2/accounts/acct-eth-002/sells` (status 201)

```
{
  "data": {
    "id": "ecdeca27-4d63-48f9-9d06-ca9f796b9544",
    "status": "completed",
    "resource": "sell",
    "amount": {
      "amount": "0.50000000",
      "currency": "ETH"
    },
    "total": {
      "amount": "1550.00",
      "currency": "USD"
    },
    "unit_price": {
      "amount": "3100.00",
      "currency": "USD"
    },
    "account_id": "acct-eth-002",
    "transaction_id": "dbcf8620-4221-44b7-8b51-fb8e60658bc1",
    "created_at": "2026-06-17T10:31:04Z"
  }
}
```

**GET list transactions** — `/v2/accounts/acct-btc-001/transactions` (status 200)

```
{
  "data": [
    {
      "id": "txn-btc-003",
      "account_id": "acct-btc-001",
      "type": "sell",
      "status": "completed",
      "amount": {
        "amount": "-0.05000000",
        "currency": "BTC"
      },
      "native_amount": {
        "amount": "-3250.00",
        "currency": "USD"
      },
      "description": "Sold 0.05 BTC",
      "created_at": "2026-04-10T09:15:00Z",
      "updated_at": "2026-04-10T09:15:00Z"
    },
    {
      "id": "txn-btc-002",
      "account_id": "acct-btc-001",
      "type": "buy",
      "status": "completed",
      "amount": {
        "amount": "0.
... (truncated)
```

</details>

### confluence-api (port 8045) — server: started

| Result | Method | Path | Status | Endpoint |
|--------|--------|------|--------|----------|
| PASS | GET | /health | 200 | health |
| PASS | GET | /wiki/rest/api/space | 200 | list spaces |
| PASS | GET | /wiki/rest/api/space/ENG | 200 | get space |
| PASS | GET | /wiki/rest/api/content?type=page&spaceKey=ENG | 200 | list content |
| PASS | POST | /wiki/rest/api/content | 201 | create content |
| PASS | GET | /wiki/rest/api/content/100103 | 200 | get content |
| PASS | PUT | /wiki/rest/api/content/100103 | 200 | update content |
| PASS | GET | /wiki/rest/api/content/100101/child/page | 200 | list child pages |
| PASS | GET | /wiki/rest/api/content/100103/label | 200 | list labels |
| PASS | GET | /wiki/rest/api/content/100103/child/comment | 200 | list comments |
| PASS | GET | /wiki/rest/api/content/search?cql=space=ENG | 200 | search by space |
| PASS | GET | /wiki/rest/api/content/search?cql=title~"Runbook" | 200 | search by title |

<details><summary>responses</summary>

**GET health** — `/health` (status 200)

```
{
  "status": "ok"
}
```

**GET list spaces** — `/wiki/rest/api/space` (status 200)

```
{
  "results": [
    {
      "id": 98001,
      "key": "ENG",
      "name": "Engineering",
      "type": "global",
      "status": "current",
      "description": {
        "plain": {
          "value": "Engineering team space for design docs and runbooks",
          "representation": "plain"
        }
      }
    },
    {
      "id": 98002,
      "key": "PROD",
      "name": "Product",
      "type": "global",
      "status": "current",
      "description": {
        "plain": {
          "value": "Product specs roadmaps and release notes",
          "representation": "plain"
        }
      }

```

**GET get space** — `/wiki/rest/api/space/ENG` (status 200)

```
{
  "id": 98001,
  "key": "ENG",
  "name": "Engineering",
  "type": "global",
  "status": "current",
  "description": {
    "plain": {
      "value": "Engineering team space for design docs and runbooks",
      "representation": "plain"
    }
  }
}
```

**GET list content** — `/wiki/rest/api/content?type=page&spaceKey=ENG` (status 200)

```
{
  "results": [
    {
      "id": "100101",
      "type": "page",
      "status": "current",
      "title": "Engineering Home",
      "space": {
        "key": "ENG"
      },
      "version": {
        "number": 3
      },
      "history": {
        "createdBy": {
          "username": "amelia"
        },
        "createdDate": "2025-09-02T10:00:00Z"
      },
      "_links": {
        "webui": "/spaces/ENG/pages/100101"
      },
      "body": {
        "storage": {
          "value": "Welcome to the Engineering space. Start here for runbooks and design docs.",
          "representation": "sto
... (truncated)
```

**POST create content** — `/wiki/rest/api/content` (status 201)

```
{
  "id": "3709502",
  "type": "page",
  "status": "current",
  "title": "Incident Postmortem Template",
  "space": {
    "key": "ENG"
  },
  "version": {
    "number": 1
  },
  "history": {
    "createdBy": {
      "username": "apiuser"
    },
    "createdDate": "2026-06-17T10:31:04.000Z"
  },
  "_links": {
    "webui": "/spaces/ENG/pages/3709502"
  },
  "ancestors": [
    {
      "id": "100102",
      "type": "page"
    }
  ],
  "body": {
    "storage": {
      "value": "Template for writing incident postmortems.",
      "representation": "storage"
    }
  }
}
```

**GET get content** — `/wiki/rest/api/content/100103` (status 200)

```
{
  "id": "100103",
  "type": "page",
  "status": "current",
  "title": "Auth Service Runbook",
  "space": {
    "key": "ENG"
  },
  "version": {
    "number": 8
  },
  "history": {
    "createdBy": {
      "username": "helena"
    },
    "createdDate": "2025-09-12T09:30:00Z"
  },
  "_links": {
    "webui": "/spaces/ENG/pages/100103"
  },
  "ancestors": [
    {
      "id": "100102",
      "type": "page"
    }
  ],
  "body": {
    "storage": {
      "value": "On-call steps for the authentication service including failover.",
      "representation": "storage"
    }
  }
}
```

**PUT update content** — `/wiki/rest/api/content/100103` (status 200)

```
{
  "id": "100103",
  "type": "page",
  "status": "current",
  "title": "Auth Service Runbook",
  "space": {
    "key": "ENG"
  },
  "version": {
    "number": 9
  },
  "history": {
    "createdBy": {
      "username": "helena"
    },
    "createdDate": "2025-09-12T09:30:00Z"
  },
  "_links": {
    "webui": "/spaces/ENG/pages/100103"
  },
  "ancestors": [
    {
      "id": "100102",
      "type": "page"
    }
  ],
  "body": {
    "storage": {
      "value": "Updated on-call steps including token rotation.",
      "representation": "storage"
    }
  }
}
```

**GET list child pages** — `/wiki/rest/api/content/100101/child/page` (status 200)

```
{
  "results": [
    {
      "id": "100102",
      "type": "page",
      "status": "current",
      "title": "Service Runbooks",
      "space": {
        "key": "ENG"
      },
      "version": {
        "number": 5
      },
      "history": {
        "createdBy": {
          "username": "jonas"
        },
        "createdDate": "2025-09-10T11:00:00Z"
      },
      "_links": {
        "webui": "/spaces/ENG/pages/100102"
      },
      "ancestors": [
        {
          "id": "100101",
          "type": "page"
        }
      ]
    },
    {
      "id": "100105",
      "type": "page",
      "sta
... (truncated)
```

**GET list labels** — `/wiki/rest/api/content/100103/label` (status 200)

```
{
  "results": [
    {
      "id": "300001",
      "name": "runbook",
      "prefix": "global",
      "label": "runbook"
    },
    {
      "id": "300002",
      "name": "oncall",
      "prefix": "global",
      "label": "oncall"
    }
  ],
  "size": 2
}
```

**GET list comments** — `/wiki/rest/api/content/100103/child/comment` (status 200)

```
{
  "results": [
    {
      "id": "200001",
      "type": "comment",
      "container": {
        "id": "100103",
        "type": "page"
      },
      "history": {
        "createdBy": {
          "username": "jonas"
        },
        "createdDate": "2025-09-13T08:00:00Z"
      },
      "body": {
        "storage": {
          "value": "Should we add a section on token rotation cadence?",
          "representation": "storage"
        }
      }
    },
    {
      "id": "200002",
      "type": "comment",
      "container": {
        "id": "100103",
        "type": "page"
      },
      "histo
```

**GET search by space** — `/wiki/rest/api/content/search?cql=space=ENG` (status 200)

```
{
  "results": [
    {
      "content": {
        "id": "100101",
        "type": "page",
        "status": "current",
        "title": "Engineering Home",
        "space": {
          "key": "ENG"
        },
        "version": {
          "number": 3
        },
        "history": {
          "createdBy": {
            "username": "amelia"
          },
          "createdDate": "2025-09-02T10:00:00Z"
        },
        "_links": {
          "webui": "/spaces/ENG/pages/100101"
        }
      },
      "title": "Engineering Home"
    },
    {
      "content": {
        "id": "100102",
        "ty
... (truncated)
```

**GET search by title** — `/wiki/rest/api/content/search?cql=title~"Runbook"` (status 200)

```
{
  "results": [
    {
      "content": {
        "id": "100102",
        "type": "page",
        "status": "current",
        "title": "Service Runbooks",
        "space": {
          "key": "ENG"
        },
        "version": {
          "number": 5
        },
        "history": {
          "createdBy": {
            "username": "jonas"
          },
          "createdDate": "2025-09-10T11:00:00Z"
        },
        "_links": {
          "webui": "/spaces/ENG/pages/100102"
        },
        "ancestors": [
          {
            "id": "100101",
            "type": "page"
          }
        
... (truncated)
```

</details>

### contentful-api (port 8066) — server: started

| Result | Method | Path | Status | Endpoint |
|--------|--------|------|--------|----------|
| PASS | GET | /health | 200 | health |
| PASS | GET | /spaces/space-orbit-cms | 200 | get space |
| PASS | GET | /spaces/space-orbit-cms/environments/master/content_types | 200 | list content types |
| PASS | GET | /spaces/space-orbit-cms/environments/master/content_types/blogPost | 200 | get content type |
| PASS | GET | /spaces/space-orbit-cms/environments/master/entries?content_type=blogPost&limit=10 | 200 | list entries |
| PASS | GET | /spaces/space-orbit-cms/environments/master/entries?content_type=blogPost&fields.slug=getting-started | 200 | list entries by field |
| PASS | GET | /spaces/space-orbit-cms/environments/master/entries/post-getting-started | 200 | get entry |
| PASS | POST | /spaces/space-orbit-cms/environments/master/entries | 201 | create entry |
| PASS | PUT | /spaces/space-orbit-cms/environments/master/entries/post-draft-webhooks | 200 | update entry |
| PASS | DELETE | /spaces/space-orbit-cms/environments/master/entries/post-content-modeling | 200 | delete entry |
| PASS | GET | /spaces/space-orbit-cms/environments/master/assets | 200 | list assets |
| PASS | GET | /spaces/space-orbit-cms/environments/master/assets/asset-hero-1 | 200 | get asset |

<details><summary>responses</summary>

**GET health** — `/health` (status 200)

```
{
  "status": "ok"
}
```

**GET get space** — `/spaces/space-orbit-cms` (status 200)

```
{
  "id": "space-orbit-cms",
  "name": "Orbit Labs CMS",
  "default_environment": "master",
  "locales": [
    "en-US"
  ],
  "created_at": "2025-09-01T09:00:00.000Z",
  "organization": "org-orbit-labs"
}
```

**GET list content types** — `/spaces/space-orbit-cms/environments/master/content_types` (status 200)

```
{
  "sys": {
    "type": "Array"
  },
  "total": 3,
  "skip": 0,
  "limit": 3,
  "items": [
    {
      "sys": {
        "id": "blogPost",
        "type": "ContentType"
      },
      "name": "Blog Post",
      "displayField": "title",
      "description": "A single article or blog entry",
      "fields": [
        {
          "id": "title",
          "name": "Title",
          "type": "Symbol",
          "required": true
        },
        {
          "id": "slug",
          "name": "Slug",
          "type": "Symbol",
          "required": true
        },
        {
          "id": "body",
   
... (truncated)
```

**GET get content type** — `/spaces/space-orbit-cms/environments/master/content_types/blogPost` (status 200)

```
{
  "sys": {
    "id": "blogPost",
    "type": "ContentType"
  },
  "name": "Blog Post",
  "displayField": "title",
  "description": "A single article or blog entry",
  "fields": [
    {
      "id": "title",
      "name": "Title",
      "type": "Symbol",
      "required": true
    },
    {
      "id": "slug",
      "name": "Slug",
      "type": "Symbol",
      "required": true
    },
    {
      "id": "body",
      "name": "Body",
      "type": "Text",
      "required": false
    },
    {
      "id": "author",
      "name": "Author",
      "type": "Link",
      "linkType": "Entry",
      "requ
```

**GET list entries** — `/spaces/space-orbit-cms/environments/master/entries?content_type=blogPost&limit=10` (status 200)

```
{
  "sys": {
    "type": "Array"
  },
  "total": 3,
  "skip": 0,
  "limit": 10,
  "items": [
    {
      "sys": {
        "id": "post-getting-started",
        "type": "Entry",
        "createdAt": "2025-09-10T08:00:00.000Z",
        "updatedAt": "2025-09-12T14:00:00.000Z",
        "publishedVersion": 5,
        "contentType": {
          "sys": {
            "type": "Link",
            "linkType": "ContentType",
            "id": "blogPost"
          }
        }
      },
      "fields": {
        "title": "Getting Started with Headless CMS",
        "slug": "getting-started",
        "body": 
... (truncated)
```

**GET list entries by field** — `/spaces/space-orbit-cms/environments/master/entries?content_type=blogPost&fields.slug=getting-started` (status 200)

```
{
  "sys": {
    "type": "Array"
  },
  "total": 1,
  "skip": 0,
  "limit": 100,
  "items": [
    {
      "sys": {
        "id": "post-getting-started",
        "type": "Entry",
        "createdAt": "2025-09-10T08:00:00.000Z",
        "updatedAt": "2025-09-12T14:00:00.000Z",
        "publishedVersion": 5,
        "contentType": {
          "sys": {
            "type": "Link",
            "linkType": "ContentType",
            "id": "blogPost"
          }
        }
      },
      "fields": {
        "title": "Getting Started with Headless CMS",
        "slug": "getting-started",
        "body":
```

**GET get entry** — `/spaces/space-orbit-cms/environments/master/entries/post-getting-started` (status 200)

```
{
  "sys": {
    "id": "post-getting-started",
    "type": "Entry",
    "createdAt": "2025-09-10T08:00:00.000Z",
    "updatedAt": "2025-09-12T14:00:00.000Z",
    "publishedVersion": 5,
    "contentType": {
      "sys": {
        "type": "Link",
        "linkType": "ContentType",
        "id": "blogPost"
      }
    }
  },
  "fields": {
    "title": "Getting Started with Headless CMS",
    "slug": "getting-started",
    "body": "Headless CMS decouples content from presentation.",
    "author": {
      "sys": {
        "type": "Link",
        "linkType": "Entry",
        "id": "author-mara"
    
```

**POST create entry** — `/spaces/space-orbit-cms/environments/master/entries` (status 201)

```
{
  "sys": {
    "id": "1ad186b9a61644eb",
    "type": "Entry",
    "createdAt": "2026-06-17T10:31:05.000Z",
    "updatedAt": "2026-06-17T10:31:05.000Z",
    "publishedVersion": 0,
    "contentType": {
      "sys": {
        "type": "Link",
        "linkType": "ContentType",
        "id": "blogPost"
      }
    }
  },
  "fields": {
    "title": "Scaling Content Delivery",
    "slug": "scaling-content-delivery",
    "body": "Tips for a fast CDN-backed delivery.",
    "published": false
  }
}
```

**PUT update entry** — `/spaces/space-orbit-cms/environments/master/entries/post-draft-webhooks` (status 200)

```
{
  "sys": {
    "id": "post-draft-webhooks",
    "type": "Entry",
    "createdAt": "2025-11-05T08:00:00.000Z",
    "updatedAt": "2026-06-17T10:31:05.000Z",
    "publishedVersion": 0,
    "contentType": {
      "sys": {
        "type": "Link",
        "linkType": "ContentType",
        "id": "blogPost"
      }
    }
  },
  "fields": {
    "title": "Using Webhooks Effectively",
    "slug": "using-webhooks",
    "body": "Draft post about webhook patterns.",
    "author": {
      "sys": {
        "type": "Link",
        "linkType": "Entry",
        "id": "author-mara"
      }
    },
    "publishe
```

**DELETE delete entry** — `/spaces/space-orbit-cms/environments/master/entries/post-content-modeling` (status 200)

```
{
  "id": "post-content-modeling",
  "deleted": true
}
```

**GET list assets** — `/spaces/space-orbit-cms/environments/master/assets` (status 200)

```
{
  "sys": {
    "type": "Array"
  },
  "total": 4,
  "skip": 0,
  "limit": 4,
  "items": [
    {
      "sys": {
        "id": "asset-hero-1",
        "type": "Asset",
        "createdAt": "2025-09-09T08:00:00.000Z",
        "updatedAt": "2025-09-09T08:00:00.000Z",
        "publishedVersion": 2
      },
      "fields": {
        "title": "Headless diagram",
        "description": "Diagram of headless architecture",
        "file": {
          "url": "https://assets.example.com/headless-diagram.png",
          "fileName": "headless-diagram.png",
          "contentType": "image/png",
          "
... (truncated)
```

**GET get asset** — `/spaces/space-orbit-cms/environments/master/assets/asset-hero-1` (status 200)

```
{
  "sys": {
    "id": "asset-hero-1",
    "type": "Asset",
    "createdAt": "2025-09-09T08:00:00.000Z",
    "updatedAt": "2025-09-09T08:00:00.000Z",
    "publishedVersion": 2
  },
  "fields": {
    "title": "Headless diagram",
    "description": "Diagram of headless architecture",
    "file": {
      "url": "https://assets.example.com/headless-diagram.png",
      "fileName": "headless-diagram.png",
      "contentType": "image/png",
      "details": {
        "size": 184320
      }
    }
  }
}
```

</details>

### datadog-api (port 8048) — server: started

| Result | Method | Path | Status | Endpoint |
|--------|--------|------|--------|----------|
| PASS | GET | /health | 200 | health |
| PASS | GET | /api/v1/query?from=1748160000&to=1748250600&query=avg:trace.http.request.duration{service:auth-service} | 200 | query metric series |
| PASS | GET | /api/v1/monitor | 200 | list monitors |
| PASS | GET | /api/v1/monitor?overall_state=Alert | 200 | list monitors alerting |
| PASS | GET | /api/v1/monitor/1001 | 200 | get monitor |
| PASS | POST | /api/v1/monitor | 201 | create monitor |
| PASS | PUT | /api/v1/monitor/1001 | 200 | update monitor (mute via state) |
| PASS | GET | /api/v1/dashboard | 200 | list dashboards |
| PASS | GET | /api/v1/dashboard/abc-123-def | 200 | get dashboard |
| PASS | GET | /api/v1/events | 200 | list events |
| PASS | POST | /api/v1/events | 201 | create event |
| PASS | GET | /api/v1/hosts | 200 | list hosts |

<details><summary>responses</summary>

**GET health** — `/health` (status 200)

```
{
  "status": "ok"
}
```

**GET query metric series** — `/api/v1/query?from=1748160000&to=1748250600&query=avg:trace.http.request.duration{service:auth-service}` (status 200)

```
{
  "status": "ok",
  "query": "avg:trace.http.request.duration{service:auth-service}",
  "from_date": 1748160000000,
  "to_date": 1748250600000,
  "series": [
    {
      "metric": "trace.http.request.duration",
      "scope": "service:auth-service",
      "unit": "second",
      "interval": 4530,
      "length": 21,
      "pointlist": [
        [
          1748160000000,
          0.42
        ],
        [
          1748164530000,
          0.4789
        ],
        [
          1748169060000,
          0.5313
        ],
        [
          1748173590000,
          0.5715
        ],
        [
... (truncated)
```

**GET list monitors** — `/api/v1/monitor` (status 200)

```
[
  {
    "id": 1001,
    "name": "High API p95 latency",
    "type": "metric alert",
    "query": "avg(last_5m):avg:trace.http.request.duration{service:auth-service} > 0.6",
    "message": "Auth API latency is high",
    "overall_state": "Alert",
    "priority": 1,
    "tags": [
      "service:auth-service",
      "team:platform"
    ],
    "created": "2025-11-01T10:00:00+00:00",
    "modified": "2026-05-26T09:00:00+00:00"
  },
  {
    "id": 1002,
    "name": "Error rate above threshold",
    "type": "metric alert",
    "query": "sum(last_5m):sum:trace.http.request.errors{service:web-frontend
... (truncated)
```

**GET list monitors alerting** — `/api/v1/monitor?overall_state=Alert` (status 200)

```
[
  {
    "id": 1001,
    "name": "High API p95 latency",
    "type": "metric alert",
    "query": "avg(last_5m):avg:trace.http.request.duration{service:auth-service} > 0.6",
    "message": "Auth API latency is high",
    "overall_state": "Alert",
    "priority": 1,
    "tags": [
      "service:auth-service",
      "team:platform"
    ],
    "created": "2025-11-01T10:00:00+00:00",
    "modified": "2026-05-26T09:00:00+00:00"
  }
]
```

**GET get monitor** — `/api/v1/monitor/1001` (status 200)

```
{
  "id": 1001,
  "name": "High API p95 latency",
  "type": "metric alert",
  "query": "avg(last_5m):avg:trace.http.request.duration{service:auth-service} > 0.6",
  "message": "Auth API latency is high",
  "overall_state": "Alert",
  "priority": 1,
  "tags": [
    "service:auth-service",
    "team:platform"
  ],
  "created": "2025-11-01T10:00:00+00:00",
  "modified": "2026-05-26T09:00:00+00:00"
}
```

**POST create monitor** — `/api/v1/monitor` (status 201)

```
{
  "id": 1006,
  "name": "5xx rate alert",
  "type": "metric alert",
  "query": "sum(last_5m):sum:trace.http.request.errors{service:auth-service}.as_count() > 25",
  "message": "Auth 5xx elevated",
  "overall_state": "OK",
  "priority": 2,
  "tags": [
    "service:auth-service"
  ],
  "created": "2026-06-17T10:31:05+00:00",
  "modified": "2026-06-17T10:31:05+00:00"
}
```

**PUT update monitor (mute via state)** — `/api/v1/monitor/1001` (status 200)

```
{
  "id": 1001,
  "name": "High API p95 latency",
  "type": "metric alert",
  "query": "avg(last_5m):avg:trace.http.request.duration{service:auth-service} > 0.6",
  "message": "Auth API latency is high",
  "overall_state": "Alert",
  "priority": 1,
  "tags": [
    "service:auth-service",
    "team:platform"
  ],
  "created": "2025-11-01T10:00:00+00:00",
  "modified": "2026-05-26T09:00:00+00:00"
}
```

**GET list dashboards** — `/api/v1/dashboard` (status 200)

```
{
  "dashboards": [
    {
      "id": "abc-123-def",
      "title": "Platform Overview",
      "description": "Top-level platform health and SLOs",
      "layout_type": "ordered",
      "author": "amelia-ortega",
      "widget_count": 12,
      "is_read_only": false,
      "created": "2025-11-01T10:00:00+00:00",
      "modified": "2026-05-26T09:00:00+00:00"
    },
    {
      "id": "ghi-456-jkl",
      "title": "Auth Service Deep Dive",
      "description": "Latency and error breakdown for auth-service",
      "layout_type": "ordered",
      "author": "helena-park",
      "widget_count": 8,
  
... (truncated)
```

**GET get dashboard** — `/api/v1/dashboard/abc-123-def` (status 200)

```
{
  "id": "abc-123-def",
  "title": "Platform Overview",
  "description": "Top-level platform health and SLOs",
  "layout_type": "ordered",
  "author": "amelia-ortega",
  "widget_count": 12,
  "is_read_only": false,
  "created": "2025-11-01T10:00:00+00:00",
  "modified": "2026-05-26T09:00:00+00:00"
}
```

**GET list events** — `/api/v1/events` (status 200)

```
{
  "events": [
    {
      "id": 500002,
      "title": "Monitor alert: High API p95 latency",
      "text": "Monitor triggered: avg latency exceeded 0.6s.",
      "alert_type": "error",
      "priority": "normal",
      "host": "web-01",
      "tags": [
        "service:auth-service",
        "monitor:1001"
      ],
      "date_happened": 1748250600
    },
    {
      "id": 500001,
      "title": "Deployment auth-service 2.0.3",
      "text": "Deployed auth-service version 2.0.3 to production.",
      "alert_type": "info",
      "priority": "normal",
      "host": "web-01",
      "tags": [
 
... (truncated)
```

**POST create event** — `/api/v1/events` (status 201)

```
{
  "status": "ok",
  "event": {
    "id": 500005,
    "title": "Manual rollback auth-service",
    "text": "Rolled back to 2.0.2 after latency spike.",
    "alert_type": "warning",
    "priority": "normal",
    "host": "web-01",
    "tags": [
      "service:auth-service",
      "event:rollback"
    ],
    "date_happened": 1781692265
  }
}
```

**GET list hosts** — `/api/v1/hosts` (status 200)

```
{
  "host_list": [
    {
      "name": "web-01",
      "up": true,
      "apps": [
        "nginx",
        "auth-service"
      ],
      "sources": "agent",
      "cpu_pct": 72.4,
      "mem_pct": 61.0,
      "last_reported": 1748250600
    },
    {
      "name": "web-02",
      "up": true,
      "apps": [
        "nginx",
        "web-frontend"
      ],
      "sources": "agent",
      "cpu_pct": 48.1,
      "mem_pct": 55.3,
      "last_reported": 1748250600
    },
    {
      "name": "db-01",
      "up": true,
      "apps": [
        "postgres"
      ],
      "sources": "agent",
      "cpu_p
```

</details>

### discord-api (port 8057) — server: started

| Result | Method | Path | Status | Endpoint |
|--------|--------|------|--------|----------|
| PASS | GET | /health | 200 | health |
| PASS | GET | /api/v10/users/@me | 200 | get me |
| PASS | GET | /api/v10/users/@me/guilds | 200 | my guilds |
| PASS | GET | /api/v10/guilds/900100200300400001 | 200 | get guild |
| PASS | GET | /api/v10/guilds/900100200300400001/channels | 200 | guild channels |
| PASS | GET | /api/v10/guilds/900100200300400001/members?limit=10 | 200 | guild members |
| PASS | GET | /api/v10/guilds/900100200300400001/roles | 200 | guild roles |
| PASS | GET | /api/v10/channels/800100200300400001 | 200 | get channel |
| PASS | GET | /api/v10/channels/800100200300400001/messages?limit=10 | 200 | channel messages |
| PASS | POST | /api/v10/channels/800100200300400001/messages | 201 | create message |

<details><summary>responses</summary>

**GET health** — `/health` (status 200)

```
{
  "status": "ok"
}
```

**GET get me** — `/api/v10/users/@me` (status 200)

```
{
  "id": "300100200300400001",
  "username": "orbitbot",
  "discriminator": "0",
  "global_name": "Orbit Bot",
  "avatar": "a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6",
  "bot": true,
  "verified": true,
  "email": "bot@orbit-labs.example.com",
  "flags": 0
}
```

**GET my guilds** — `/api/v10/users/@me/guilds` (status 200)

```
[
  {
    "id": "900100200300400001",
    "name": "Orbit Labs Community",
    "icon": "f1e2d3c4b5a6f7e8d9c0b1a2f3e4d5c6",
    "owner": false,
    "permissions": "104324673"
  },
  {
    "id": "900100200300400002",
    "name": "Indie Game Devs",
    "icon": "a9b8c7d6e5f4a3b2c1d0e9f8a7b6c5d4",
    "owner": false,
    "permissions": "104324673"
  }
]
```

**GET get guild** — `/api/v10/guilds/900100200300400001` (status 200)

```
{
  "id": "900100200300400001",
  "name": "Orbit Labs Community",
  "owner_id": "500100200300400001",
  "approximate_member_count": 5,
  "description": "Hangout for Orbit Labs makers and users",
  "icon": "f1e2d3c4b5a6f7e8d9c0b1a2f3e4d5c6",
  "region": "us-east"
}
```

**GET guild channels** — `/api/v10/guilds/900100200300400001/channels` (status 200)

```
[
  {
    "id": "800100200300400001",
    "guild_id": "900100200300400001",
    "name": "general",
    "type": 0,
    "position": 0,
    "topic": "General chatter and announcements",
    "nsfw": false
  },
  {
    "id": "800100200300400002",
    "guild_id": "900100200300400001",
    "name": "support",
    "type": 0,
    "position": 1,
    "topic": "Ask for help with Orbit Labs products",
    "nsfw": false
  },
  {
    "id": "800100200300400003",
    "guild_id": "900100200300400001",
    "name": "off-topic",
    "type": 0,
    "position": 2,
    "topic": "Anything goes (within reason)",
    "ns
... (truncated)
```

**GET guild members** — `/api/v10/guilds/900100200300400001/members?limit=10` (status 200)

```
[
  {
    "guild_id": "900100200300400001",
    "user": {
      "id": "500100200300400001",
      "username": "amelia",
      "global_name": "Amelia O",
      "bot": false
    },
    "nick": "Amelia",
    "joined_at": "2024-11-02T10:00:00Z",
    "roles": [
      "700100200300400001",
      "700100200300400002"
    ]
  },
  {
    "guild_id": "900100200300400001",
    "user": {
      "id": "500100200300400002",
      "username": "jonas",
      "global_name": "Jonas P",
      "bot": false
    },
    "nick": null,
    "joined_at": "2024-11-05T12:30:00Z",
    "roles": [
      "700100200300400002"
 
... (truncated)
```

**GET guild roles** — `/api/v10/guilds/900100200300400001/roles` (status 200)

```
[
  {
    "id": "700100200300400001",
    "guild_id": "900100200300400001",
    "name": "Admin",
    "color": 15158332,
    "position": 4,
    "hoist": true,
    "mentionable": true,
    "permissions": "8"
  },
  {
    "id": "700100200300400002",
    "guild_id": "900100200300400001",
    "name": "Moderator",
    "color": 3447003,
    "position": 3,
    "hoist": true,
    "mentionable": true,
    "permissions": "268435456"
  },
  {
    "id": "700100200300400004",
    "guild_id": "900100200300400001",
    "name": "Bots",
    "color": 9807270,
    "position": 2,
    "hoist": false,
    "mentionab
... (truncated)
```

**GET get channel** — `/api/v10/channels/800100200300400001` (status 200)

```
{
  "id": "800100200300400001",
  "guild_id": "900100200300400001",
  "name": "general",
  "type": 0,
  "position": 0,
  "topic": "General chatter and announcements",
  "nsfw": false
}
```

**GET channel messages** — `/api/v10/channels/800100200300400001/messages?limit=10` (status 200)

```
[
  {
    "id": "1001000200030004003",
    "channel_id": "800100200300400001",
    "author": {
      "id": "300100200300400001",
      "username": "orbitbot"
    },
    "content": "Release v2.18.0 is now live in production.",
    "timestamp": "2025-05-01T12:00:00Z",
    "pinned": false,
    "edited_timestamp": null
  },
  {
    "id": "1001000200030004002",
    "channel_id": "800100200300400001",
    "author": {
      "id": "500100200300400002",
      "username": "jonas"
    },
    "content": "Glad to be here. The new dashboard looks great.",
    "timestamp": "2025-05-01T09:05:00Z",
    "pinned
... (truncated)
```

**POST create message** — `/api/v10/channels/800100200300400001/messages` (status 201)

```
{
  "id": "1516752040442068993",
  "channel_id": "800100200300400001",
  "author": {
    "id": "500100200300400001",
    "username": "amelia"
  },
  "content": "Posting from the mock API.",
  "timestamp": "2026-06-17T10:31:06.000000+00:00",
  "pinned": false,
  "edited_timestamp": null
}
```

</details>

### docusign-api (port 8053) — server: started

| Result | Method | Path | Status | Endpoint |
|--------|--------|------|--------|----------|
| PASS | GET | /health | 200 | health |
| PASS | GET | /restapi/v2.1/accounts/acct-orbit-labs/envelopes?status=sent | 200 | list envelopes |
| PASS | POST | /restapi/v2.1/accounts/acct-orbit-labs/envelopes | 201 | create envelope |
| PASS | GET | /restapi/v2.1/accounts/acct-orbit-labs/envelopes/env-2001 | 200 | get envelope |
| PASS | PUT | /restapi/v2.1/accounts/acct-orbit-labs/envelopes/env-2001 | 200 | void envelope |
| PASS | GET | /restapi/v2.1/accounts/acct-orbit-labs/envelopes/env-2003/recipients | 200 | list recipients |
| PASS | GET | /restapi/v2.1/accounts/acct-orbit-labs/envelopes/env-2001/documents | 200 | list documents |
| PASS | GET | /restapi/v2.1/accounts/acct-orbit-labs/templates | 200 | list templates |

<details><summary>responses</summary>

**GET health** — `/health` (status 200)

```
{
  "status": "ok"
}
```

**GET list envelopes** — `/restapi/v2.1/accounts/acct-orbit-labs/envelopes?status=sent` (status 200)

```
{
  "resultSetSize": "1",
  "totalSetSize": "1",
  "envelopes": [
    {
      "envelopeId": "env-2001",
      "status": "sent",
      "emailSubject": "Please sign: Master Services Agreement",
      "sender": {
        "userName": "Amelia Ortega",
        "email": "amelia.ortega@orbit-labs.com"
      },
      "createdDateTime": "2026-05-20T10:00:00Z",
      "sentDateTime": "2026-05-20T10:05:00Z",
      "completedDateTime": null,
      "templateId": "tmpl-msa"
    }
  ]
}
```

**POST create envelope** — `/restapi/v2.1/accounts/acct-orbit-labs/envelopes` (status 201)

```
{
  "envelopeId": "4a837f77-47c9-4d0f-89eb-bb84d1072c70",
  "status": "sent",
  "statusDateTime": "2026-06-17T10:31:06.0000000Z",
  "uri": "/envelopes/4a837f77-47c9-4d0f-89eb-bb84d1072c70"
}
```

**GET get envelope** — `/restapi/v2.1/accounts/acct-orbit-labs/envelopes/env-2001` (status 200)

```
{
  "envelopeId": "env-2001",
  "status": "sent",
  "emailSubject": "Please sign: Master Services Agreement",
  "sender": {
    "userName": "Amelia Ortega",
    "email": "amelia.ortega@orbit-labs.com"
  },
  "createdDateTime": "2026-05-20T10:00:00Z",
  "sentDateTime": "2026-05-20T10:05:00Z",
  "completedDateTime": null,
  "templateId": "tmpl-msa"
}
```

**PUT void envelope** — `/restapi/v2.1/accounts/acct-orbit-labs/envelopes/env-2001` (status 200)

```
{
  "envelopeId": "env-2001",
  "status": "voided",
  "statusDateTime": "2026-06-17T10:31:06.0000000Z"
}
```

**GET list recipients** — `/restapi/v2.1/accounts/acct-orbit-labs/envelopes/env-2003/recipients` (status 200)

```
{
  "signers": [
    {
      "recipientId": "rcp-5",
      "name": "Lena Voss",
      "email": "lena.voss@vendorco.com",
      "recipientType": "signer",
      "status": "completed",
      "routingOrder": 1,
      "signedDateTime": "2026-05-18T16:40:00Z"
    },
    {
      "recipientId": "rcp-6",
      "name": "Helena Park",
      "email": "helena.park@orbit-labs.com",
      "recipientType": "signer",
      "status": "completed",
      "routingOrder": 2,
      "signedDateTime": "2026-05-18T16:45:00Z"
    }
  ],
  "recipientCount": "2"
}
```

**GET list documents** — `/restapi/v2.1/accounts/acct-orbit-labs/envelopes/env-2001/documents` (status 200)

```
{
  "envelopeId": "env-2001",
  "envelopeDocuments": [
    {
      "documentId": "doc-1",
      "name": "Master Services Agreement.pdf",
      "type": "content",
      "pages": 12,
      "order": 1
    },
    {
      "documentId": "doc-2",
      "name": "Exhibit A - Pricing.pdf",
      "type": "content",
      "pages": 2,
      "order": 2
    }
  ]
}
```

**GET list templates** — `/restapi/v2.1/accounts/acct-orbit-labs/templates` (status 200)

```
{
  "resultSetSize": "3",
  "envelopeTemplates": [
    {
      "templateId": "tmpl-msa",
      "name": "Master Services Agreement",
      "description": "Standard MSA for new enterprise customers",
      "shared": "true",
      "owner": {
        "userName": "Amelia Ortega"
      },
      "created": "2026-01-10T09:00:00Z"
    },
    {
      "templateId": "tmpl-nda",
      "name": "Mutual NDA",
      "description": "Two-way confidentiality agreement",
      "shared": "true",
      "owner": {
        "userName": "Jonas Pereira"
      },
      "created": "2026-01-12T10:30:00Z"
    },
    {
      
... (truncated)
```

</details>

### doordash-api (port 8037) — server: started

| Result | Method | Path | Status | Endpoint |
|--------|--------|------|--------|----------|
| SKIP | POST | /v1/carts/{{cartId}}/items | - | add cart item — unresolved variable {{cartId}} |
| SKIP | GET | /v1/carts/{{cartId}} | - | get cart — unresolved variable {{cartId}} |
| SKIP | POST | /v1/carts/{{cartId}}/checkout | - | checkout — unresolved variable {{cartId}} |
| PASS | GET | /health | 200 | health |
| PASS | GET | /v1/stores?latitude=37.7842&longitude=-122.4078 | 200 | list stores |
| PASS | GET | /v1/stores?cuisine=Japanese | 200 | list stores by cuisine |
| PASS | GET | /v1/stores/store-sakura | 200 | get store |
| PASS | GET | /v1/stores/store-sakura/menu | 200 | get menu |
| PASS | POST | /v1/carts | 201 | create cart |
| PASS | GET | /v1/orders/order-90aa12 | 200 | get order |

<details><summary>responses</summary>

**GET health** — `/health` (status 200)

```
{
  "status": "ok"
}
```

**GET list stores** — `/v1/stores?latitude=37.7842&longitude=-122.4078` (status 200)

```
{
  "count": 5,
  "stores": [
    {
      "store_id": "store-sakura",
      "name": "Sakura Ramen House",
      "cuisine": "Japanese",
      "rating": 4.7,
      "review_count": 1284,
      "price_range": "$$",
      "delivery_fee": 2.99,
      "eta_minutes": 28,
      "latitude": 37.7842,
      "longitude": -122.4078,
      "address": "512 Geary St San Francisco",
      "is_open": true
    },
    {
      "store_id": "store-tacolibre",
      "name": "Taco Libre",
      "cuisine": "Mexican",
      "rating": 4.6,
      "review_count": 2031,
      "price_range": "$",
      "delivery_fee": 1.99,
 
... (truncated)
```

**GET list stores by cuisine** — `/v1/stores?cuisine=Japanese` (status 200)

```
{
  "count": 1,
  "stores": [
    {
      "store_id": "store-sakura",
      "name": "Sakura Ramen House",
      "cuisine": "Japanese",
      "rating": 4.7,
      "review_count": 1284,
      "price_range": "$$",
      "delivery_fee": 2.99,
      "eta_minutes": 28,
      "latitude": 37.7842,
      "longitude": -122.4078,
      "address": "512 Geary St San Francisco",
      "is_open": true
    }
  ]
}
```

**GET get store** — `/v1/stores/store-sakura` (status 200)

```
{
  "store_id": "store-sakura",
  "name": "Sakura Ramen House",
  "cuisine": "Japanese",
  "rating": 4.7,
  "review_count": 1284,
  "price_range": "$$",
  "delivery_fee": 2.99,
  "eta_minutes": 28,
  "latitude": 37.7842,
  "longitude": -122.4078,
  "address": "512 Geary St San Francisco",
  "is_open": true
}
```

**GET get menu** — `/v1/stores/store-sakura/menu` (status 200)

```
{
  "store_id": "store-sakura",
  "categories": [
    {
      "name": "Ramen",
      "items": [
        {
          "item_id": "item-sak-001",
          "store_id": "store-sakura",
          "name": "Tonkotsu Ramen",
          "description": "Rich pork-bone broth with chashu and soft egg",
          "category": "Ramen",
          "price": 15.5,
          "calories": 720,
          "popular": true,
          "available": true
        },
        {
          "item_id": "item-sak-002",
          "store_id": "store-sakura",
          "name": "Spicy Miso Ramen",
          "description": "Miso broth 
... (truncated)
```

**POST create cart** — `/v1/carts` (status 201)

```
{
  "cart_id": "cart-b5df454b",
  "store_id": "store-sakura",
  "items": [],
  "created_at": "2026-06-17T10:31:07Z",
  "subtotal": 0.0,
  "delivery_fee": 2.99,
  "service_fee": 0.0,
  "estimated_total": 2.99
}
```

**GET get order** — `/v1/orders/order-90aa12` (status 200)

```
{
  "order_id": "order-90aa12",
  "store_id": "store-sakura",
  "customer_name": "Priya Nair",
  "status": "delivered",
  "subtotal": 38.5,
  "delivery_fee": 2.99,
  "service_fee": 3.85,
  "tip": 6.0,
  "total": 51.34,
  "placed_at": "2026-05-22T19:14:00Z",
  "dasher_name": "Carlos M.",
  "items": [
    {
      "order_id": "order-90aa12",
      "item_id": "item-sak-001",
      "quantity": 2,
      "unit_price": 15.5,
      "line_total": 31.0
    },
    {
      "order_id": "order-90aa12",
      "item_id": "item-sak-003",
      "quantity": 1,
      "unit_price": 7.5,
      "line_total": 7.5
    
```

</details>

### dropbox-api (port 8082) — server: started

| Result | Method | Path | Status | Endpoint |
|--------|--------|------|--------|----------|
| PASS | GET | /health | 200 | health |
| PASS | POST | /2/users/get_current_account | 200 | get current account |
| PASS | POST | /2/files/list_folder | 200 | list folder root |
| PASS | POST | /2/files/list_folder | 200 | list folder documents |
| PASS | POST | /2/files/get_metadata | 200 | get metadata |
| PASS | POST | /2/files/search_v2 | 200 | search v2 |
| PASS | POST | /2/sharing/list_shared_links | 200 | list shared links |

<details><summary>responses</summary>

**GET health** — `/health` (status 200)

```
{
  "status": "ok"
}
```

**POST get current account** — `/2/users/get_current_account` (status 200)

```
{
  "account_id": "dbid:AAH4f99T0taONIb-OurWxbNQ6ywGRopQngc",
  "name": {
    "given_name": "Maya",
    "surname": "Robinson",
    "display_name": "Maya Robinson",
    "familiar_name": "Maya",
    "abbreviated_name": "MR"
  },
  "email": "maya.robinson@example.com",
  "email_verified": true,
  "country": "US",
  "locale": "en",
  "account_type": {
    ".tag": "business"
  },
  "is_paired": false,
  "disabled": false
}
```

**POST list folder root** — `/2/files/list_folder` (status 200)

```
{
  "entries": [
    {
      ".tag": "folder",
      "id": "id:a4ayc_80000000000000000000001",
      "name": "Documents",
      "path_lower": "/documents",
      "path_display": "/Documents"
    },
    {
      ".tag": "folder",
      "id": "id:a4ayc_80000000000000000000002",
      "name": "Photos",
      "path_lower": "/photos",
      "path_display": "/Photos"
    },
    {
      ".tag": "folder",
      "id": "id:a4ayc_80000000000000000000003",
      "name": "Projects",
      "path_lower": "/projects",
      "path_display": "/Projects"
    }
  ],
  "cursor": "AAH4f99T0taONIb-mock-cursor",
  "ha
```

**POST list folder documents** — `/2/files/list_folder` (status 200)

```
{
  "entries": [
    {
      ".tag": "file",
      "id": "id:a4ayc_80000000000000000000004",
      "name": "Q2-Report.pdf",
      "path_lower": "/documents/q2-report.pdf",
      "path_display": "/Documents/Q2-Report.pdf",
      "size": 284517,
      "client_modified": "2026-05-10T14:32:00Z",
      "server_modified": "2026-05-10T14:32:00Z",
      "rev": "0123456789abcdef01000001",
      "is_downloadable": true
    },
    {
      ".tag": "file",
      "id": "id:a4ayc_80000000000000000000005",
      "name": "Budget-2026.xlsx",
      "path_lower": "/documents/budget-2026.xlsx",
      "path_display
... (truncated)
```

**POST get metadata** — `/2/files/get_metadata` (status 200)

```
{
  ".tag": "file",
  "id": "id:a4ayc_80000000000000000000004",
  "name": "Q2-Report.pdf",
  "path_lower": "/documents/q2-report.pdf",
  "path_display": "/Documents/Q2-Report.pdf",
  "size": 284517,
  "client_modified": "2026-05-10T14:32:00Z",
  "server_modified": "2026-05-10T14:32:00Z",
  "rev": "0123456789abcdef01000001",
  "is_downloadable": true
}
```

**POST search v2** — `/2/files/search_v2` (status 200)

```
{
  "matches": [
    {
      "match_type": {
        ".tag": "filename"
      },
      "metadata": {
        ".tag": "metadata",
        "metadata": {
          ".tag": "file",
          "id": "id:a4ayc_80000000000000000000004",
          "name": "Q2-Report.pdf",
          "path_lower": "/documents/q2-report.pdf",
          "path_display": "/Documents/Q2-Report.pdf",
          "size": 284517,
          "client_modified": "2026-05-10T14:32:00Z",
          "server_modified": "2026-05-10T14:32:00Z",
          "rev": "0123456789abcdef01000001",
          "is_downloadable": true
        }
      }
 
```

**POST list shared links** — `/2/sharing/list_shared_links` (status 200)

```
{
  "links": [
    {
      ".tag": "file",
      "id": "sl_0001",
      "url": "https://www.dropbox.com/s/abc123def456/Q2-Report.pdf?dl=0",
      "name": "Q2-Report.pdf",
      "path_lower": "/documents/q2-report.pdf",
      "link_permissions": {
        "resolved_visibility": {
          ".tag": "public"
        },
        "can_revoke": true
      }
    },
    {
      ".tag": "file",
      "id": "sl_0002",
      "url": "https://www.dropbox.com/s/ghi789jkl012/Budget-2026.xlsx?dl=0",
      "name": "Budget-2026.xlsx",
      "path_lower": "/documents/budget-2026.xlsx",
      "link_permissions": {
... (truncated)
```

</details>

### etsy-api (port 8001) — server: started

| Result | Method | Path | Status | Endpoint |
|--------|--------|------|--------|----------|
| PASS | GET | /health | 200 | GET /health |
| PASS | GET | /v3/application/shops/29457183 | 200 | GET Shop |
| WARN | GET | /v3/application/shops/99999 | 404 | GET Shop - 404 |
| PASS | PUT | /v3/application/shops/29457183 | 200 | PUT Update Shop |
| PASS | GET | /v3/application/shops/29457183/sections | 200 | GET List Shop Sections |
| PASS | GET | /v3/application/shops/29457183/sections/40001 | 200 | GET Single Shop Section |
| WARN | GET | /v3/application/shops/29457183/sections/99999 | 404 | GET Shop Section - 404 |
| PASS | GET | /v3/application/shops/29457183/listings | 200 | GET List Listings (default - active) |
| PASS | GET | /v3/application/shops/29457183/listings?state=draft | 200 | GET List Listings - draft state |
| PASS | GET | /v3/application/shops/29457183/listings?q=mug | 200 | GET List Listings - search query |
| PASS | GET | /v3/application/shops/29457183/listings?section_id=40002 | 200 | GET List Listings - by section |
| PASS | GET | /v3/application/shops/29457183/listings?limit=5&offset=5&sort_on=price&sort_order=asc | 200 | GET List Listings - pagination |
| PASS | GET | /v3/application/listings/1001 | 200 | GET Single Listing |
| WARN | GET | /v3/application/listings/99999 | 404 | GET Single Listing - 404 |
| PASS | POST | /v3/application/shops/29457183/listings | 201 | POST Create Listing |
| WARN | POST | /v3/application/shops/29457183/listings | 422 | POST Create Listing - missing required field |
| PASS | PUT | /v3/application/listings/1001 | 200 | PUT Update Listing - price and quantity |
| PASS | PUT | /v3/application/listings/1020 | 200 | PUT Update Listing - activate draft |
| PASS | DELETE | /v3/application/listings/1017 | 200 | DELETE Listing |
| WARN | DELETE | /v3/application/listings/99999 | 404 | DELETE Listing - 404 |
| PASS | GET | /v3/application/listings/1001/images | 200 | GET List Listing Images |
| PASS | GET | /v3/application/listings/1001/images/90001 | 200 | GET Single Listing Image |
| WARN | GET | /v3/application/listings/1001/images/99999 | 404 | GET Listing Image - 404 |
| PASS | DELETE | /v3/application/listings/1001/images/90003 | 200 | DELETE Listing Image |
| PASS | GET | /v3/application/shops/29457183/receipts | 200 | GET List Receipts (all) |
| PASS | GET | /v3/application/shops/29457183/receipts?status=paid | 200 | GET List Receipts - paid only |
| PASS | GET | /v3/application/shops/29457183/receipts?was_shipped=false | 200 | GET List Receipts - not shipped |
| PASS | GET | /v3/application/shops/29457183/receipts?min_created=2025-03-01&max_created=2025-04-01 | 200 | GET List Receipts - date range |
| PASS | GET | /v3/application/shops/29457183/receipts?limit=5&offset=5&sort_order=asc | 200 | GET List Receipts - pagination |
| PASS | GET | /v3/application/shops/29457183/receipts/2003 | 200 | GET Single Receipt (with transactions) |
| PASS | GET | /v3/application/shops/29457183/receipts/2008 | 200 | GET Single Receipt - gift order |
| PASS | GET | /v3/application/shops/29457183/receipts/2010 | 200 | GET Single Receipt - cancelled |
| WARN | GET | /v3/application/shops/29457183/receipts/99999 | 404 | GET Single Receipt - 404 |
| PASS | PUT | /v3/application/shops/29457183/receipts/2007 | 200 | PUT Update Receipt - mark shipped |
| PASS | PUT | /v3/application/shops/29457183/receipts/2008 | 200 | PUT Update Receipt - add tracking to paid order |
| PASS | GET | /v3/application/shops/29457183/receipts/2003/transactions | 200 | GET List Receipt Transactions |
| WARN | GET | /v3/application/shops/29457183/receipts/99999/transactions | 404 | GET List Receipt Transactions - 404 |
| PASS | GET | /v3/application/shops/29457183/transactions/3001 | 200 | GET Single Transaction |
| WARN | GET | /v3/application/shops/29457183/transactions/99999 | 404 | GET Single Transaction - 404 |
| PASS | GET | /v3/application/shops/29457183/reviews | 200 | GET List Shop Reviews |
| PASS | GET | /v3/application/shops/29457183/reviews?min_rating=5 | 200 | GET List Shop Reviews - min rating filter |
| PASS | GET | /v3/application/shops/29457183/reviews?listing_id=1001 | 200 | GET List Shop Reviews - by listing |
| PASS | GET | /v3/application/shops/29457183/reviews?limit=3&offset=3 | 200 | GET List Shop Reviews - pagination |
| PASS | GET | /v3/application/listings/1001/reviews | 200 | GET List Listing Reviews |
| PASS | GET | /v3/application/listings/1011/reviews | 200 | GET List Listing Reviews - low ratings |
| PASS | GET | /v3/application/shops/29457183/shipping-profiles | 200 | GET List Shipping Profiles |
| PASS | GET | /v3/application/shops/29457183/shipping-profiles/50001 | 200 | GET Single Shipping Profile |
| WARN | GET | /v3/application/shops/29457183/shipping-profiles/99999 | 404 | GET Shipping Profile - 404 |
| PASS | GET | /v3/application/shops/29457183/return-policies | 200 | GET List Return Policies |
| PASS | GET | /v3/application/shops/29457183/return-policies/60001 | 200 | GET Single Return Policy |
| WARN | GET | /v3/application/shops/29457183/return-policies/99999 | 404 | GET Return Policy - 404 |

<details><summary>responses</summary>

**GET GET /health** — `/health` (status 200)

```
{
  "status": "ok"
}
```

**GET GET Shop** — `/v3/application/shops/29457183` (status 200)

```
{
  "type": "shop",
  "shop": {
    "shop_id": 29457183,
    "shop_name": "WalshWoodcraft",
    "user_id": 81726354,
    "title": "Hand-Carved Woodwork & Artisan Crafts \u2022 Pacific Northwest",
    "announcement": "Welcome to Walsh Woodcraft! Every piece is hand-carved in my Tacoma, WA workshop using locally-sourced Pacific Northwest woods. I also sell woven baskets, beaded jewelry, and handmade instruments at the Steilacoom Artisan Market. Please allow 1-3 weeks for made-to-order items. Custom wildlife carvings and fly boxes available\u2014just message me!",
    "currency_code": "USD",
    
... (truncated)
```

**GET GET Shop - 404** — `/v3/application/shops/99999` (status 404)

```
{
  "error": "Shop 99999 not found"
}
```

**PUT PUT Update Shop** — `/v3/application/shops/29457183` (status 200)

```
{
  "type": "shop",
  "shop": {
    "shop_id": 29457183,
    "shop_name": "WalshWoodcraft",
    "user_id": 81726354,
    "title": "Hand-Carved Woodwork & Artisan Crafts \u2022 Pacific Northwest",
    "announcement": "Welcome to Walsh Woodcraft! Every piece is hand-carved in my Tacoma, WA workshop using locally-sourced Pacific Northwest woods. I also sell woven baskets, beaded jewelry, and handmade instruments at the Steilacoom Artisan Market. Please allow 1-3 weeks for made-to-order items. Custom wildlife carvings and fly boxes available\u2014just message me!",
    "currency_code": "USD",
    
... (truncated)
```

**GET GET List Shop Sections** — `/v3/application/shops/29457183/sections` (status 200)

```
{
  "type": "shop_sections",
  "count": 6,
  "results": [
    {
      "shop_section_id": 40001,
      "shop_id": 29457183,
      "title": "Kitchenware & Fly Boxes",
      "rank": 1,
      "active_listing_count": 4
    },
    {
      "shop_section_id": 40002,
      "shop_id": 29457183,
      "title": "Home Decor & Sculptures",
      "rank": 2,
      "active_listing_count": 5
    },
    {
      "shop_section_id": 40003,
      "shop_id": 29457183,
      "title": "Accessories & Jewelry",
      "rank": 3,
      "active_listing_count": 5
    },
    {
      "shop_section_id": 40004,
      "shop_id": 
... (truncated)
```

**GET GET Single Shop Section** — `/v3/application/shops/29457183/sections/40001` (status 200)

```
{
  "type": "shop_section",
  "shop_section": {
    "shop_section_id": 40001,
    "shop_id": 29457183,
    "title": "Kitchenware & Fly Boxes",
    "rank": 1,
    "active_listing_count": 4
  }
}
```

**GET GET Shop Section - 404** — `/v3/application/shops/29457183/sections/99999` (status 404)

```
{
  "error": "Shop section 99999 not found"
}
```

**GET GET List Listings (default - active)** — `/v3/application/shops/29457183/listings` (status 200)

```
{"type":"listings","count":19,"total":19,"offset":0,"limit":25,"results":[{"listing_id":1019,"shop_id":29457183,"title":"Cedar Fly Box - Steelhead Scene","description":"Hand-carved cedar fly box with a detailed steelhead trout scene on the lid. Interior fitted with dual-layer closed-cell foam holding 60+ flies. Approximately 8 x 5 x 2.5 inches. Brass hinges and latch. Companion piece to the Trout Scene box.","price":150.0,"currency_code":"USD","quantity":2,"taxonomy_id":6516,"tags":["fly box","steelhead carving","cedar box","fly fishing","fishing gift","carved fly box","handmade box"],"materia
... (truncated)
```

**GET GET List Listings - draft state** — `/v3/application/shops/29457183/listings?state=draft` (status 200)

```
{
  "type": "listings",
  "count": 1,
  "total": 1,
  "offset": 0,
  "limit": 25,
  "results": [
    {
      "listing_id": 1020,
      "shop_id": 29457183,
      "title": "Beginner Woodcarving Workshop Kit",
      "description": "Starter kit for beginner woodcarvers. Includes two basswood blanks, a basic carving knife, a gouge, sandpaper, and a printed guide with three projects. NOT YET AVAILABLE - assembling kits for summer workshops at the Tacoma Community Craft Center.",
      "price": 40.0,
      "currency_code": "USD",
      "quantity": 0,
      "taxonomy_id": 6516,
      "tags": [
      
... (truncated)
```

**GET GET List Listings - search query** — `/v3/application/shops/29457183/listings?q=mug` (status 200)

```
{
  "type": "listings",
  "count": 0,
  "total": 0,
  "offset": 0,
  "limit": 25,
  "results": []
}
```

**GET GET List Listings - by section** — `/v3/application/shops/29457183/listings?section_id=40002` (status 200)

```
{
  "type": "listings",
  "count": 5,
  "total": 5,
  "offset": 0,
  "limit": 25,
  "results": [
    {
      "listing_id": 1014,
      "shop_id": 29457183,
      "title": "Hand-Carved Great Blue Heron - Driftwood Base",
      "description": "Life-sized great blue heron sculpture hand-carved from western red cedar and mounted on a natural Puget Sound driftwood base. Detailed feather work and painted accents. Approximately 36 inches tall. A signature Walsh Woodcraft piece.",
      "price": 550.0,
      "currency_code": "USD",
      "quantity": 1,
      "taxonomy_id": 6516,
      "tags": [
      
... (truncated)
```

**GET GET List Listings - pagination** — `/v3/application/shops/29457183/listings?limit=5&offset=5&sort_on=price&sort_order=asc` (status 200)

```
{
  "type": "listings",
  "count": 5,
  "total": 19,
  "offset": 5,
  "limit": 5,
  "results": [
    {
      "listing_id": 1007,
      "shop_id": 29457183,
      "title": "Traditional Beaded Necklace - Multi-color",
      "description": "Handcrafted multi-color beaded necklace using traditional stringing techniques. Features a vibrant mix of glass and wood beads in earthy and bright tones. Adjustable length approximately 18-22 inches. Finished with a handmade clasp.",
      "price": 55.0,
      "currency_code": "USD",
      "quantity": 6,
      "taxonomy_id": 6516,
      "tags": [
        "bea
... (truncated)
```

**GET GET Single Listing** — `/v3/application/listings/1001` (status 200)

```
{
  "type": "listing",
  "listing": {
    "listing_id": 1001,
    "shop_id": 29457183,
    "title": "Hand-Carved Mortar & Pestle Set - Red Cedar",
    "description": "Solid red cedar mortar and pestle set hand-carved in my Tacoma workshop. The mortar stands approximately 7 inches tall with a 5-inch opening. Pestle is shaped for a comfortable grip. Finished with food-safe mineral oil. Each set shows unique grain patterns.",
    "price": 180.0,
    "currency_code": "USD",
    "quantity": 3,
    "taxonomy_id": 6516,
    "tags": [
      "mortar and pestle",
      "wood mortar",
      "hand carved"
... (truncated)
```

**GET GET Single Listing - 404** — `/v3/application/listings/99999` (status 404)

```
{
  "error": "Listing 99999 not found"
}
```

**POST POST Create Listing** — `/v3/application/shops/29457183/listings` (status 201)

```
{
  "type": "listing",
  "listing": {
    "listing_id": 1021,
    "shop_id": 29457183,
    "title": "Ceramic Candle Holder - Crescent Moon",
    "description": "Hand-thrown crescent moon shaped candle holder in matte black glaze. Holds a standard taper candle. 5 inches tall.",
    "price": 30.0,
    "currency_code": "USD",
    "quantity": 8,
    "taxonomy_id": 2078,
    "tags": [
      "candle holder",
      "ceramic",
      "moon",
      "handmade",
      "black ceramic"
    ],
    "materials": [
      "stoneware clay",
      "matte black glaze"
    ],
    "who_made": "i_did",
    "when_made"
... (truncated)
```

**POST POST Create Listing - missing required field** — `/v3/application/shops/29457183/listings` (status 422)

```
{
  "detail": [
    {
      "type": "missing",
      "loc": [
        "body",
        "description"
      ],
      "msg": "Field required",
      "input": {
        "title": "Incomplete Listing",
        "price": 10.0
      }
    },
    {
      "type": "missing",
      "loc": [
        "body",
        "quantity"
      ],
      "msg": "Field required",
      "input": {
        "title": "Incomplete Listing",
        "price": 10.0
      }
    },
    {
      "type": "missing",
      "loc": [
        "body",
        "who_made"
      ],
      "msg": "Field required",
      "input": {
        "title"
... (truncated)
```

**PUT PUT Update Listing - price and quantity** — `/v3/application/listings/1001` (status 200)

```
{
  "type": "listing",
  "listing": {
    "listing_id": 1001,
    "shop_id": 29457183,
    "title": "Hand-Carved Mortar & Pestle Set - Red Cedar",
    "description": "Solid red cedar mortar and pestle set hand-carved in my Tacoma workshop. The mortar stands approximately 7 inches tall with a 5-inch opening. Pestle is shaped for a comfortable grip. Finished with food-safe mineral oil. Each set shows unique grain patterns.",
    "price": 180.0,
    "currency_code": "USD",
    "quantity": 3,
    "taxonomy_id": 6516,
    "tags": [
      "mortar and pestle",
      "wood mortar",
      "hand carved"
... (truncated)
```

**PUT PUT Update Listing - activate draft** — `/v3/application/listings/1020` (status 200)

```
{
  "type": "listing",
  "listing": {
    "listing_id": 1020,
    "shop_id": 29457183,
    "title": "Beginner Woodcarving Workshop Kit",
    "description": "Starter kit for beginner woodcarvers. Includes two basswood blanks, a basic carving knife, a gouge, sandpaper, and a printed guide with three projects. NOT YET AVAILABLE - assembling kits for summer workshops at the Tacoma Community Craft Center.",
    "price": 40.0,
    "currency_code": "USD",
    "quantity": 0,
    "taxonomy_id": 6516,
    "tags": [
      "woodcarving kit",
      "beginner carving",
      "workshop kit",
      "carving t
... (truncated)
```

**DELETE DELETE Listing** — `/v3/application/listings/1017` (status 200)

```
{
  "type": "listing",
  "deleted": true,
  "listing_id": 1017
}
```

**DELETE DELETE Listing - 404** — `/v3/application/listings/99999` (status 404)

```
{
  "error": "Listing 99999 not found"
}
```

**GET GET List Listing Images** — `/v3/application/listings/1001/images` (status 200)

```
{
  "type": "listing_images",
  "count": 3,
  "results": [
    {
      "listing_image_id": 90001,
      "listing_id": 1001,
      "shop_id": 29457183,
      "rank": 1,
      "url_75x75": "https://i.etsystatic.com/example/il_75x75.90001.jpg",
      "url_170x135": "https://i.etsystatic.com/example/il_170x135.90001.jpg",
      "url_570xN": "https://i.etsystatic.com/example/il_570xN.90001.jpg",
      "url_fullxfull": "https://i.etsystatic.com/example/il_fullxfull.90001.jpg",
      "alt_text": "Hand-carved red cedar mortar and pestle set on rustic wood table",
      "created_timestamp": "2024-01-15
... (truncated)
```

**GET GET Single Listing Image** — `/v3/application/listings/1001/images/90001` (status 200)

```
{
  "type": "listing_image",
  "listing_image": {
    "listing_image_id": 90001,
    "listing_id": 1001,
    "shop_id": 29457183,
    "rank": 1,
    "url_75x75": "https://i.etsystatic.com/example/il_75x75.90001.jpg",
    "url_170x135": "https://i.etsystatic.com/example/il_170x135.90001.jpg",
    "url_570xN": "https://i.etsystatic.com/example/il_570xN.90001.jpg",
    "url_fullxfull": "https://i.etsystatic.com/example/il_fullxfull.90001.jpg",
    "alt_text": "Hand-carved red cedar mortar and pestle set on rustic wood table",
    "created_timestamp": "2024-01-15T09:35:00"
  }
}
```

**GET GET Listing Image - 404** — `/v3/application/listings/1001/images/99999` (status 404)

```
{
  "error": "Image 99999 not found for listing 1001"
}
```

**DELETE DELETE Listing Image** — `/v3/application/listings/1001/images/90003` (status 200)

```
{
  "type": "listing_image",
  "deleted": true,
  "listing_image_id": 90003
}
```

**GET GET List Receipts (all)** — `/v3/application/shops/29457183/receipts` (status 200)

```
{
  "type": "receipts",
  "count": 15,
  "total": 15,
  "offset": 0,
  "limit": 25,
  "results": [
    {
      "receipt_id": 2014,
      "shop_id": 29457183,
      "buyer_user_id": 55013,
      "buyer_email": "chris.doyle55@gmail.com",
      "name": "Chris Doyle",
      "address_first_line": "1100 Summit Blvd",
      "address_city": "Atlanta",
      "address_state": "GA",
      "address_zip": "30301",
      "address_country": "US",
      "status": "open",
      "payment_method": "cc",
      "grandtotal": 85.0,
      "subtotal": 85.0,
      "total_shipping_cost": 0.0,
      "total_tax_cost": 0.
... (truncated)
```

**GET GET List Receipts - paid only** — `/v3/application/shops/29457183/receipts?status=paid` (status 200)

```
{
  "type": "receipts",
  "count": 3,
  "total": 3,
  "offset": 0,
  "limit": 25,
  "results": [
    {
      "receipt_id": 2011,
      "shop_id": 29457183,
      "buyer_user_id": 55001,
      "buyer_email": "marissa.chen@email.com",
      "name": "Marissa Chen",
      "address_first_line": "742 Evergreen Terrace",
      "address_city": "San Francisco",
      "address_state": "CA",
      "address_zip": "94102",
      "address_country": "US",
      "status": "paid",
      "payment_method": "cc",
      "grandtotal": 291.99,
      "subtotal": 280.0,
      "total_shipping_cost": 11.99,
      "total
... (truncated)
```

**GET GET List Receipts - not shipped** — `/v3/application/shops/29457183/receipts?was_shipped=false` (status 200)

```
{
  "type": "receipts",
  "count": 5,
  "total": 5,
  "offset": 0,
  "limit": 25,
  "results": [
    {
      "receipt_id": 2014,
      "shop_id": 29457183,
      "buyer_user_id": 55013,
      "buyer_email": "chris.doyle55@gmail.com",
      "name": "Chris Doyle",
      "address_first_line": "1100 Summit Blvd",
      "address_city": "Atlanta",
      "address_state": "GA",
      "address_zip": "30301",
      "address_country": "US",
      "status": "open",
      "payment_method": "cc",
      "grandtotal": 85.0,
      "subtotal": 85.0,
      "total_shipping_cost": 0.0,
      "total_tax_cost": 0.0,
... (truncated)
```

**GET GET List Receipts - date range** — `/v3/application/shops/29457183/receipts?min_created=2025-03-01&max_created=2025-04-01` (status 200)

```
{
  "type": "receipts",
  "count": 5,
  "total": 5,
  "offset": 0,
  "limit": 25,
  "results": [
    {
      "receipt_id": 2007,
      "shop_id": 29457183,
      "buyer_user_id": 55007,
      "buyer_email": "priya.patel.design@gmail.com",
      "name": "Priya Patel",
      "address_first_line": "2105 Willow Way",
      "address_city": "Nashville",
      "address_state": "TN",
      "address_zip": "37201",
      "address_country": "US",
      "status": "paid",
      "payment_method": "cc",
      "grandtotal": 41.99,
      "subtotal": 35.0,
      "total_shipping_cost": 5.99,
      "total_tax_cos
... (truncated)
```

**GET GET List Receipts - pagination** — `/v3/application/shops/29457183/receipts?limit=5&offset=5&sort_order=asc` (status 200)

```
{
  "type": "receipts",
  "count": 5,
  "total": 15,
  "offset": 5,
  "limit": 5,
  "results": [
    {
      "receipt_id": 2015,
      "shop_id": 29457183,
      "buyer_user_id": 55014,
      "buyer_email": "hannah.nguyen.art@email.com",
      "name": "Hannah Nguyen",
      "address_first_line": "345 Linden Street",
      "address_city": "Philadelphia",
      "address_state": "PA",
      "address_zip": "19101",
      "address_country": "US",
      "status": "return_requested",
      "payment_method": "cc",
      "grandtotal": 90.0,
      "subtotal": 90.0,
      "total_shipping_cost": 0.0,
    
... (truncated)
```

**GET GET Single Receipt (with transactions)** — `/v3/application/shops/29457183/receipts/2003` (status 200)

```
{
  "type": "receipt",
  "receipt": {
    "receipt_id": 2003,
    "shop_id": 29457183,
    "buyer_user_id": 55003,
    "buyer_email": "katie.yamamoto@outlook.com",
    "name": "Katie Yamamoto",
    "address_first_line": "89 Pine Street",
    "address_city": "Seattle",
    "address_state": "WA",
    "address_zip": "98101",
    "address_country": "US",
    "status": "completed",
    "payment_method": "cc",
    "grandtotal": 95.99,
    "subtotal": 90.0,
    "total_shipping_cost": 5.99,
    "total_tax_cost": 0.0,
    "discount_amt": 0.0,
    "gift_message": "Happy Housewarming! Love Katie",
    "i
... (truncated)
```

**GET GET Single Receipt - gift order** — `/v3/application/shops/29457183/receipts/2008` (status 200)

```
{
  "type": "receipt",
  "receipt": {
    "receipt_id": 2008,
    "shop_id": 29457183,
    "buyer_user_id": 55008,
    "buyer_email": "marcus.wellington@email.com",
    "name": "Marcus Wellington",
    "address_first_line": "445 Spruce Street Apt 12",
    "address_city": "Brooklyn",
    "address_state": "NY",
    "address_zip": "11201",
    "address_country": "US",
    "status": "paid",
    "payment_method": "paypal",
    "grandtotal": 580.99,
    "subtotal": 550.0,
    "total_shipping_cost": 24.99,
    "total_tax_cost": 6.0,
    "discount_amt": 0.0,
    "gift_message": "Congratulations on you
... (truncated)
```

**GET GET Single Receipt - cancelled** — `/v3/application/shops/29457183/receipts/2010` (status 200)

```
{
  "type": "receipt",
  "receipt": {
    "receipt_id": 2010,
    "shop_id": 29457183,
    "buyer_user_id": 55010,
    "buyer_email": "danielle.martinez99@gmail.com",
    "name": "Danielle Martinez",
    "address_first_line": "1234 Elm Street",
    "address_city": "Phoenix",
    "address_state": "AZ",
    "address_zip": "85001",
    "address_country": "US",
    "status": "cancelled",
    "payment_method": "cc",
    "grandtotal": 45.0,
    "subtotal": 45.0,
    "total_shipping_cost": 0.0,
    "total_tax_cost": 0.0,
    "discount_amt": 0.0,
    "gift_message": null,
    "is_gift": false,
    "sh
... (truncated)
```

**GET GET Single Receipt - 404** — `/v3/application/shops/29457183/receipts/99999` (status 404)

```
{
  "error": "Receipt 99999 not found"
}
```

**PUT PUT Update Receipt - mark shipped** — `/v3/application/shops/29457183/receipts/2007` (status 200)

```
{
  "type": "receipt",
  "receipt": {
    "receipt_id": 2007,
    "shop_id": 29457183,
    "buyer_user_id": 55007,
    "buyer_email": "priya.patel.design@gmail.com",
    "name": "Priya Patel",
    "address_first_line": "2105 Willow Way",
    "address_city": "Nashville",
    "address_state": "TN",
    "address_zip": "37201",
    "address_country": "US",
    "status": "paid",
    "payment_method": "cc",
    "grandtotal": 41.99,
    "subtotal": 35.0,
    "total_shipping_cost": 5.99,
    "total_tax_cost": 1.0,
    "discount_amt": 0.0,
    "gift_message": null,
    "is_gift": false,
    "shipping_c
... (truncated)
```

**PUT PUT Update Receipt - add tracking to paid order** — `/v3/application/shops/29457183/receipts/2008` (status 200)

```
{
  "type": "receipt",
  "receipt": {
    "receipt_id": 2008,
    "shop_id": 29457183,
    "buyer_user_id": 55008,
    "buyer_email": "marcus.wellington@email.com",
    "name": "Marcus Wellington",
    "address_first_line": "445 Spruce Street Apt 12",
    "address_city": "Brooklyn",
    "address_state": "NY",
    "address_zip": "11201",
    "address_country": "US",
    "status": "paid",
    "payment_method": "paypal",
    "grandtotal": 580.99,
    "subtotal": 550.0,
    "total_shipping_cost": 24.99,
    "total_tax_cost": 6.0,
    "discount_amt": 0.0,
    "gift_message": "Congratulations on you
... (truncated)
```

**GET GET List Receipt Transactions** — `/v3/application/shops/29457183/receipts/2003/transactions` (status 200)

```
{
  "type": "transactions",
  "count": 1,
  "results": [
    {
      "transaction_id": 3003,
      "receipt_id": 2003,
      "listing_id": 1002,
      "shop_id": 29457183,
      "buyer_user_id": 55003,
      "title": "Traditional Pattern Rolling Pin - Carved Beechwood",
      "quantity": 2,
      "price": 45.0,
      "shipping_cost": 5.99,
      "is_digital": false,
      "variations": "",
      "created_timestamp": "2025-02-02T18:30:00"
    }
  ]
}
```

**GET GET List Receipt Transactions - 404** — `/v3/application/shops/29457183/receipts/99999/transactions` (status 404)

```
{
  "error": "Receipt 99999 not found"
}
```

**GET GET Single Transaction** — `/v3/application/shops/29457183/transactions/3001` (status 200)

```
{
  "type": "transaction",
  "transaction": {
    "transaction_id": 3001,
    "receipt_id": 2001,
    "listing_id": 1001,
    "shop_id": 29457183,
    "buyer_user_id": 55001,
    "title": "Hand-Carved Mortar & Pestle Set - Red Cedar",
    "quantity": 1,
    "price": 180.0,
    "shipping_cost": 11.99,
    "is_digital": false,
    "variations": "",
    "created_timestamp": "2025-01-08T14:22:00"
  }
}
```

**GET GET Single Transaction - 404** — `/v3/application/shops/29457183/transactions/99999` (status 404)

```
{
  "error": "Transaction 99999 not found"
}
```

**GET GET List Shop Reviews** — `/v3/application/shops/29457183/reviews` (status 200)

```
{
  "type": "reviews",
  "count": 12,
  "total": 12,
  "offset": 0,
  "limit": 25,
  "results": [
    {
      "review_id": 7009,
      "shop_id": 29457183,
      "listing_id": 1005,
      "buyer_user_id": 55009,
      "rating": 5,
      "review": "Perfect market basket! Sturdy enough to haul produce from the farmers market and attractive enough to use as home decor. The weave is tight and even. Already planning to buy more as gifts for friends.",
      "language": "en",
      "image_url": "https://i.etsystatic.com/example/review_7009.jpg",
      "created_timestamp": "2025-04-20T16:00:00",
    
... (truncated)
```

**GET GET List Shop Reviews - min rating filter** — `/v3/application/shops/29457183/reviews?min_rating=5` (status 200)

```
{
  "type": "reviews",
  "count": 9,
  "total": 9,
  "offset": 0,
  "limit": 25,
  "results": [
    {
      "review_id": 7009,
      "shop_id": 29457183,
      "listing_id": 1005,
      "buyer_user_id": 55009,
      "rating": 5,
      "review": "Perfect market basket! Sturdy enough to haul produce from the farmers market and attractive enough to use as home decor. The weave is tight and even. Already planning to buy more as gifts for friends.",
      "language": "en",
      "image_url": "https://i.etsystatic.com/example/review_7009.jpg",
      "created_timestamp": "2025-04-20T16:00:00",
      
... (truncated)
```

**GET GET List Shop Reviews - by listing** — `/v3/application/shops/29457183/reviews?listing_id=1001` (status 200)

```
{
  "type": "reviews",
  "count": 1,
  "total": 1,
  "offset": 0,
  "limit": 25,
  "results": [
    {
      "review_id": 7001,
      "shop_id": 29457183,
      "listing_id": 1001,
      "buyer_user_id": 55001,
      "rating": 5,
      "review": "Absolutely stunning mortar and pestle set! The red cedar has such a rich color and the carving work is exquisite. It's heavy and sturdy - clearly built to last. The grain pattern on mine is beautiful. Will definitely be ordering more pieces from this shop!",
      "language": "en",
      "image_url": null,
      "created_timestamp": "2025-01-20T08:30:0
```

**GET GET List Shop Reviews - pagination** — `/v3/application/shops/29457183/reviews?limit=3&offset=3` (status 200)

```
{
  "type": "reviews",
  "count": 3,
  "total": 12,
  "offset": 3,
  "limit": 3,
  "results": [
    {
      "review_id": 7010,
      "shop_id": 29457183,
      "listing_id": 1013,
      "buyer_user_id": 55014,
      "rating": 2,
      "review": "The bangles arrived with one noticeably bent out of shape. I reached out to the seller who was responsive and offered a replacement but I'm disappointed with the original packaging - they were just tossed in a padded envelope. The designs are beautiful though so I'm hopeful the replacement set will arrive safely.",
      "language": "en",
      "image_
... (truncated)
```

**GET GET List Listing Reviews** — `/v3/application/listings/1001/reviews` (status 200)

```
{
  "type": "reviews",
  "count": 1,
  "total": 1,
  "offset": 0,
  "limit": 25,
  "results": [
    {
      "review_id": 7001,
      "shop_id": 29457183,
      "listing_id": 1001,
      "buyer_user_id": 55001,
      "rating": 5,
      "review": "Absolutely stunning mortar and pestle set! The red cedar has such a rich color and the carving work is exquisite. It's heavy and sturdy - clearly built to last. The grain pattern on mine is beautiful. Will definitely be ordering more pieces from this shop!",
      "language": "en",
      "image_url": null,
      "created_timestamp": "2025-01-20T08:30:0
```

**GET GET List Listing Reviews - low ratings** — `/v3/application/listings/1011/reviews` (status 200)

```
{
  "type": "reviews",
  "count": 1,
  "total": 1,
  "offset": 0,
  "limit": 25,
  "results": [
    {
      "review_id": 7012,
      "shop_id": 29457183,
      "listing_id": 1011,
      "buyer_user_id": 55002,
      "rating": 5,
      "review": "As a PNW native I'm picky about salmon art and this wall mount delivers! The form is dynamic - it really captures a salmon mid-leap. The painted details on the scales catch the light beautifully. Looks perfect above our mantel.",
      "language": "en",
      "image_url": null,
      "created_timestamp": "2025-04-10T07:45:00",
      "updated_timestamp"
```

**GET GET List Shipping Profiles** — `/v3/application/shops/29457183/shipping-profiles` (status 200)

```
{
  "type": "shipping_profiles",
  "count": 3,
  "results": [
    {
      "shipping_profile_id": 50001,
      "shop_id": 29457183,
      "title": "Standard Shipping - Small Items",
      "origin_country": "US",
      "origin_postal_code": "98402",
      "processing_min": 5,
      "processing_max": 10,
      "min_delivery_days": 3,
      "max_delivery_days": 5,
      "cost": 5.99,
      "secondary_cost": 3.99
    },
    {
      "shipping_profile_id": 50002,
      "shop_id": 29457183,
      "title": "Standard Shipping - Large/Heavy Items",
      "origin_country": "US",
      "origin_postal_code"
... (truncated)
```

**GET GET Single Shipping Profile** — `/v3/application/shops/29457183/shipping-profiles/50001` (status 200)

```
{
  "type": "shipping_profile",
  "shipping_profile": {
    "shipping_profile_id": 50001,
    "shop_id": 29457183,
    "title": "Standard Shipping - Small Items",
    "origin_country": "US",
    "origin_postal_code": "98402",
    "processing_min": 5,
    "processing_max": 10,
    "min_delivery_days": 3,
    "max_delivery_days": 5,
    "cost": 5.99,
    "secondary_cost": 3.99
  }
}
```

**GET GET Shipping Profile - 404** — `/v3/application/shops/29457183/shipping-profiles/99999` (status 404)

```
{
  "error": "Shipping profile 99999 not found"
}
```

**GET GET List Return Policies** — `/v3/application/shops/29457183/return-policies` (status 200)

```
{
  "type": "return_policies",
  "count": 1,
  "results": [
    {
      "return_policy_id": 60001,
      "shop_id": 29457183,
      "accepts_returns": true,
      "accepts_exchanges": true,
      "return_deadline": 30
    }
  ]
}
```

**GET GET Single Return Policy** — `/v3/application/shops/29457183/return-policies/60001` (status 200)

```
{
  "type": "return_policy",
  "return_policy": {
    "return_policy_id": 60001,
    "shop_id": 29457183,
    "accepts_returns": true,
    "accepts_exchanges": true,
    "return_deadline": 30
  }
}
```

**GET GET Return Policy - 404** — `/v3/application/shops/29457183/return-policies/99999` (status 404)

```
{
  "error": "Return policy 99999 not found"
}
```

</details>

### eventbrite-api (port 8020) — server: started

| Result | Method | Path | Status | Endpoint |
|--------|--------|------|--------|----------|
| PASS | GET | /health | 200 | health |
| PASS | GET | /v3/users/me/organizations | 200 | my organizations |
| PASS | GET | /v3/organizations/org-cascade/events?status=live | 200 | org events |
| PASS | GET | /v3/events/search?q=postgres | 200 | search events |
| PASS | GET | /v3/events/evt-7000001 | 200 | get event |
| PASS | POST | /v3/events | 201 | create draft event |
| PASS | POST | /v3/events/evt-7000003/publish | 200 | publish event |
| PASS | POST | /v3/events/evt-7000004/cancel | 200 | cancel event |
| PASS | GET | /v3/venues | 200 | list venues |
| PASS | GET | /v3/events/evt-7000001/ticket_classes | 200 | ticket classes |
| PASS | POST | /v3/events/evt-7000003/ticket_classes | 201 | create ticket class |
| PASS | GET | /v3/events/evt-7000001/attendees | 200 | list attendees |
| PASS | POST | /v3/events/evt-7000004/attendees | 201 | register attendee |
| PASS | POST | /v3/attendees/att-001/check_in | 200 | check in |

<details><summary>responses</summary>

**GET health** — `/health` (status 200)

```
{
  "status": "ok"
}
```

**GET my organizations** — `/v3/users/me/organizations` (status 200)

```
{
  "organizations": [
    {
      "id": "org-cascade",
      "name": "Cascade Eng Meetups",
      "description": "Bay Area engineering and SRE meetups",
      "vertical": "Tech",
      "image_url": "https://img.example.com/org-cascade.png"
    },
    {
      "id": "org-sf-runners",
      "name": "SF Bay Runners",
      "description": "Group runs around SF Bay Area parks",
      "vertical": "Sports",
      "image_url": "https://img.example.com/org-sfrun.png"
    }
  ],
  "pagination": {
    "object_count": 2
  }
}
```

**GET org events** — `/v3/organizations/org-cascade/events?status=live` (status 200)

```
{
  "events": [
    {
      "id": "evt-7000001",
      "organization_id": "org-cascade",
      "name": {
        "text": "Production Postgres at scale",
        "html": "<p>Production Postgres at scale</p>"
      },
      "summary": "Practitioner talks on running Postgres at scale.",
      "status": "live",
      "start_utc": "2026-06-04T01:30:00Z",
      "end_utc": "2026-06-04T04:00:00Z",
      "timezone": "America/Los_Angeles",
      "venue_id": "venue-soma",
      "capacity": 120,
      "is_free": false,
      "online_event": false,
      "url": "https://eventbrite.example.com/e/pg-scale",

... (truncated)
```

**GET search events** — `/v3/events/search?q=postgres` (status 200)

```
{
  "events": [
    {
      "id": "evt-7000001",
      "organization_id": "org-cascade",
      "name": {
        "text": "Production Postgres at scale",
        "html": "<p>Production Postgres at scale</p>"
      },
      "summary": "Practitioner talks on running Postgres at scale.",
      "status": "live",
      "start_utc": "2026-06-04T01:30:00Z",
      "end_utc": "2026-06-04T04:00:00Z",
      "timezone": "America/Los_Angeles",
      "venue_id": "venue-soma",
      "capacity": 120,
      "is_free": false,
      "online_event": false,
      "url": "https://eventbrite.example.com/e/pg-scale",

... (truncated)
```

**GET get event** — `/v3/events/evt-7000001` (status 200)

```
{
  "id": "evt-7000001",
  "organization_id": "org-cascade",
  "name": {
    "text": "Production Postgres at scale",
    "html": "<p>Production Postgres at scale</p>"
  },
  "summary": "Practitioner talks on running Postgres at scale.",
  "status": "live",
  "start_utc": "2026-06-04T01:30:00Z",
  "end_utc": "2026-06-04T04:00:00Z",
  "timezone": "America/Los_Angeles",
  "venue_id": "venue-soma",
  "capacity": 120,
  "is_free": false,
  "online_event": false,
  "url": "https://eventbrite.example.com/e/pg-scale",
  "created": "2026-04-01T10:00:00Z",
  "start": {
    "timezone": "America/Los_Angel
... (truncated)
```

**POST create draft event** — `/v3/events` (status 201)

```
{
  "id": "evt-55d33028",
  "organization_id": "org-cascade",
  "name": {
    "text": "Service-mesh deep dive",
    "html": "<p>Service-mesh deep dive</p>"
  },
  "summary": "Half-day service mesh deep dive",
  "status": "draft",
  "start_utc": "2026-08-15T17:00:00Z",
  "end_utc": "2026-08-15T21:00:00Z",
  "timezone": "America/Los_Angeles",
  "venue_id": "venue-soma",
  "capacity": 60,
  "is_free": false,
  "online_event": false,
  "url": "",
  "created": "2026-06-17T10:31:09Z",
  "start": {
    "timezone": "America/Los_Angeles",
    "utc": "2026-08-15T17:00:00Z"
  },
  "end": {
    "timezone"
... (truncated)
```

**POST publish event** — `/v3/events/evt-7000003/publish` (status 200)

```
{
  "id": "evt-7000003",
  "organization_id": "org-cascade",
  "name": {
    "text": "Bay Area auth + identity meetup",
    "html": "<p>Bay Area auth + identity meetup</p>"
  },
  "summary": "Lightning talks + networking on auth/identity.",
  "status": "draft",
  "start_utc": "2026-07-09T01:00:00Z",
  "end_utc": "2026-07-09T04:00:00Z",
  "timezone": "America/Los_Angeles",
  "venue_id": "venue-soma",
  "capacity": 80,
  "is_free": true,
  "online_event": false,
  "url": "https://eventbrite.example.com/e/auth-meetup",
  "created": "2026-05-20T10:00:00Z",
  "start": {
    "timezone": "America/Los
... (truncated)
```

**POST cancel event** — `/v3/events/evt-7000004/cancel` (status 200)

```
{
  "id": "evt-7000004",
  "organization_id": "org-sf-runners",
  "name": {
    "text": "Saturday Presidio loop run",
    "html": "<p>Saturday Presidio loop run</p>"
  },
  "summary": "5 mile group run with optional coffee after.",
  "status": "live",
  "start_utc": "2026-05-31T15:00:00Z",
  "end_utc": "2026-05-31T17:00:00Z",
  "timezone": "America/Los_Angeles",
  "venue_id": "venue-presidio",
  "capacity": 30,
  "is_free": true,
  "online_event": false,
  "url": "https://eventbrite.example.com/e/presidio-run",
  "created": "2026-05-10T10:00:00Z",
  "start": {
    "timezone": "America/Los_Ange
... (truncated)
```

**GET list venues** — `/v3/venues` (status 200)

```
{
  "venues": [
    {
      "id": "venue-soma",
      "name": "GitHub Loft",
      "address1": "532 Folsom St",
      "city": "San Francisco",
      "region": "CA",
      "postal_code": "94105",
      "country": "US",
      "latitude": 37.7853,
      "longitude": -122.397
    },
    {
      "id": "venue-mission",
      "name": "Mission Bay Conference Center",
      "address1": "1675 Owens St",
      "city": "San Francisco",
      "region": "CA",
      "postal_code": "94158",
      "country": "US",
      "latitude": 37.7679,
      "longitude": -122.3925
    },
    {
      "id": "venue-presidio"
```

**GET ticket classes** — `/v3/events/evt-7000001/ticket_classes` (status 200)

```
{
  "ticket_classes": [
    {
      "id": "tc-001",
      "event_id": "evt-7000001",
      "name": "Standard",
      "quantity_total": 120,
      "quantity_sold": 86,
      "cost": 2500,
      "fee": 250,
      "free": false,
      "sales_start": "2026-04-01T10:00:00Z",
      "sales_end": "2026-06-04T01:00:00Z"
    },
    {
      "id": "tc-002",
      "event_id": "evt-7000001",
      "name": "Student",
      "quantity_total": 30,
      "quantity_sold": 18,
      "cost": 1000,
      "fee": 100,
      "free": false,
      "sales_start": "2026-04-01T10:00:00Z",
      "sales_end": "2026-06-04T01:0
```

**POST create ticket class** — `/v3/events/evt-7000003/ticket_classes` (status 201)

```
{
  "id": "tc-4e3bf71b",
  "event_id": "evt-7000003",
  "name": "Early bird",
  "quantity_total": 30,
  "quantity_sold": 0,
  "cost": 1500,
  "fee": 150,
  "free": false,
  "sales_start": "2026-06-17T10:31:09Z",
  "sales_end": "2026-06-17T10:31:09Z"
}
```

**GET list attendees** — `/v3/events/evt-7000001/attendees` (status 200)

```
{
  "attendees": [
    {
      "id": "att-001",
      "event_id": "evt-7000001",
      "ticket_class_id": "tc-001",
      "name": "Amelia Ortega",
      "email": "amelia@orbit-labs.com",
      "status": "attending",
      "checked_in": false,
      "created": "2026-04-05T10:00:00Z"
    },
    {
      "id": "att-002",
      "event_id": "evt-7000001",
      "ticket_class_id": "tc-001",
      "name": "Jonas Pereira",
      "email": "jonas@orbit-labs.com",
      "status": "attending",
      "checked_in": false,
      "created": "2026-04-06T10:00:00Z"
    },
    {
      "id": "att-003",
      "even
... (truncated)
```

**POST register attendee** — `/v3/events/evt-7000004/attendees` (status 201)

```
{
  "id": "att-4d3db85a",
  "event_id": "evt-7000004",
  "ticket_class_id": "tc-005",
  "name": "Helena Park",
  "email": "helena@orbit-labs.com",
  "status": "attending",
  "checked_in": false,
  "created": "2026-06-17T10:31:09Z"
}
```

**POST check in** — `/v3/attendees/att-001/check_in` (status 200)

```
{
  "id": "att-001",
  "event_id": "evt-7000001",
  "ticket_class_id": "tc-001",
  "name": "Amelia Ortega",
  "email": "amelia@orbit-labs.com",
  "status": "attending",
  "checked_in": false,
  "created": "2026-04-05T10:00:00Z"
}
```

</details>

### fedex-api (port 8095) — server: started

| Result | Method | Path | Status | Endpoint |
|--------|--------|------|--------|----------|
| PASS | GET | /health | 200 | health |
| PASS | POST | /rate/v1/rates/quotes | 200 | rate quote |
| PASS | POST | /ship/v1/shipments | 200 | create shipment |
| PASS | POST | /track/v1/trackingnumbers | 200 | track |

<details><summary>responses</summary>

**GET health** — `/health` (status 200)

```
{
  "status": "ok"
}
```

**POST rate quote** — `/rate/v1/rates/quotes` (status 200)

```
{
  "output": {
    "rateReplyDetails": [
      {
        "serviceType": "FEDEX_GROUND",
        "serviceName": "FedEx Ground",
        "packagingType": "YOUR_PACKAGING",
        "commit": {
          "dateDetail": {
            "dayCxsFormat": "2026-05-29"
          },
          "transitDays": 4
        },
        "ratedShipmentDetails": [
          {
            "rateType": "ACCOUNT",
            "totalNetCharge": 18.45,
            "currency": "USD"
          }
        ]
      },
      {
        "serviceType": "FEDEX_2_DAY",
        "serviceName": "FedEx 2Day",
        "packagingType": "YOU
... (truncated)
```

**POST create shipment** — `/ship/v1/shipments` (status 200)

```
{
  "output": {
    "transactionShipments": [
      {
        "serviceType": "FEDEX_GROUND",
        "serviceName": "FedEx Ground",
        "shipDatestamp": "2026-06-17",
        "masterTrackingNumber": "794612035895",
        "pieceResponses": [
          {
            "trackingNumber": "794612035895",
            "netChargeAmount": 18.45,
            "currency": "USD",
            "packageDocuments": [
              {
                "contentType": "LABEL",
                "docType": "PDF",
                "url": "https://fedex.example/labels/794612035895.pdf"
              }
            ]
 
```

**POST track** — `/track/v1/trackingnumbers` (status 200)

```
{
  "output": {
    "completeTrackResults": [
      {
        "trackingNumber": "794612035840",
        "trackResults": [
          {
            "trackingNumberInfo": {
              "trackingNumber": "794612035840",
              "carrierCode": "FDXG"
            },
            "latestStatusDetail": {
              "code": "DL",
              "description": "Delivered",
              "scanLocation": {
                "city": "New York, NY"
              }
            },
            "serviceDetail": {
              "description": "FedEx Ground"
            },
            "dateAndTimes": [
   
```

</details>

### figma-api (port 8079) — server: started

| Result | Method | Path | Status | Endpoint |
|--------|--------|------|--------|----------|
| PASS | GET | /health | 200 | health |
| PASS | GET | /v1/me | 200 | get me |
| PASS | GET | /v1/teams/team-501/projects | 200 | team projects |
| PASS | GET | /v1/projects/proj-201/files | 200 | project files |
| PASS | GET | /v1/files/FK001abcdefg | 200 | get file |
| PASS | GET | /v1/files/FK001abcdefg/nodes?ids=5:10,5:20 | 200 | get file nodes |
| PASS | GET | /v1/files/FK001abcdefg/comments | 200 | get comments |
| PASS | POST | /v1/files/FK001abcdefg/comments | 201 | create comment |
| PASS | GET | /v1/files/FK004vwxyz12/components | 200 | get components |

<details><summary>responses</summary>

**GET health** — `/health` (status 200)

```
{
  "status": "ok"
}
```

**GET get me** — `/v1/me` (status 200)

```
{
  "id": "user-1001",
  "handle": "Priya Nair",
  "email": "priya@orbit-labs.example.com",
  "img_url": "https://figma-avatars.example.com/user-1001.png"
}
```

**GET team projects** — `/v1/teams/team-501/projects` (status 200)

```
{
  "name": "Orbit Labs Design",
  "projects": [
    {
      "id": "proj-201",
      "name": "Mobile App"
    },
    {
      "id": "proj-202",
      "name": "Marketing Website"
    },
    {
      "id": "proj-203",
      "name": "Design System"
    }
  ]
}
```

**GET project files** — `/v1/projects/proj-201/files` (status 200)

```
{
  "name": "Mobile App",
  "files": [
    {
      "key": "FK001abcdefg",
      "name": "Onboarding Flow",
      "thumbnail_url": "https://figma-thumbs.example.com/FK001.png",
      "last_modified": "2026-05-22T14:30:00Z"
    },
    {
      "key": "FK002hijklmn",
      "name": "Checkout Redesign",
      "thumbnail_url": "https://figma-thumbs.example.com/FK002.png",
      "last_modified": "2026-05-24T09:12:00Z"
    }
  ]
}
```

**GET get file** — `/v1/files/FK001abcdefg` (status 200)

```
{
  "name": "Onboarding Flow",
  "role": "owner",
  "lastModified": "2026-05-22T14:30:00Z",
  "editorType": "figma",
  "thumbnailUrl": "https://figma-thumbs.example.com/FK001.png",
  "version": "4920183",
  "document": {
    "id": "0:0",
    "name": "Document",
    "type": "DOCUMENT",
    "children": [
      {
        "id": "1:2",
        "name": "Page 1",
        "type": "CANVAS",
        "backgroundColor": {
          "r": 0.96,
          "g": 0.96,
          "b": 0.96,
          "a": 1
        },
        "children": [
          {
            "id": "5:10",
            "name": "Welcome Screen
... (truncated)
```

**GET get file nodes** — `/v1/files/FK001abcdefg/nodes?ids=5:10,5:20` (status 200)

```
{
  "name": "Onboarding Flow",
  "lastModified": "2026-05-22T14:30:00Z",
  "version": "4920183",
  "nodes": {
    "5:10": {
      "document": {
        "id": "5:10",
        "name": "Welcome Screen",
        "type": "FRAME",
        "absoluteBoundingBox": {
          "x": 0,
          "y": 0,
          "width": 375,
          "height": 812
        },
        "children": [
          {
            "id": "5:11",
            "name": "Headline",
            "type": "TEXT",
            "characters": "Welcome to Orbit"
          },
          {
            "id": "5:12",
            "name": "Nav / Bott
... (truncated)
```

**GET get comments** — `/v1/files/FK001abcdefg/comments` (status 200)

```
{
  "comments": [
    {
      "id": "cmt-9001",
      "file_key": "FK001abcdefg",
      "message": "Can we increase the tap target on this button?",
      "client_meta": {
        "node_id": "5:12"
      },
      "user": {
        "id": "user-1001",
        "handle": "Priya Nair",
        "img_url": "https://figma-avatars.example.com/user-1001.png"
      },
      "resolved_at": null,
      "created_at": "2026-05-22T15:01:00Z"
    },
    {
      "id": "cmt-9002",
      "file_key": "FK001abcdefg",
      "message": "Agreed; bumping to 48px height.",
      "client_meta": {
        "node_id": "5:12
... (truncated)
```

**POST create comment** — `/v1/files/FK001abcdefg/comments` (status 201)

```
{
  "id": "cmt-321fc5c4",
  "file_key": "FK001abcdefg",
  "message": "Let's align the spacing here.",
  "client_meta": {
    "node_id": "5:11"
  },
  "user": {
    "id": "user-1003",
    "handle": "Mara Lindqvist",
    "img_url": "https://figma-avatars.example.com/user-1003.png"
  },
  "resolved_at": null,
  "created_at": "2026-06-17T10:31:10Z"
}
```

**GET get components** — `/v1/files/FK004vwxyz12/components` (status 200)

```
{
  "meta": {
    "components": [
      {
        "key": "comp-btn-primary",
        "file_key": "FK004vwxyz12",
        "node_id": "10:21",
        "name": "Button / Primary",
        "description": "Primary call to action button"
      },
      {
        "key": "comp-btn-secondary",
        "file_key": "FK004vwxyz12",
        "node_id": "10:22",
        "name": "Button / Secondary",
        "description": "Secondary action button"
      },
      {
        "key": "comp-input-text",
        "file_key": "FK004vwxyz12",
        "node_id": "10:30",
        "name": "Input / Text",
        "descrip
```

</details>

### freshdesk-api (port 8093) — server: started

| Result | Method | Path | Status | Endpoint |
|--------|--------|------|--------|----------|
| PASS | GET | /health | 200 | health |
| PASS | GET | /api/v2/tickets | 200 | list tickets |
| PASS | GET | /api/v2/tickets?status=2&priority=2 | 200 | list tickets filtered |
| PASS | GET | /api/v2/tickets/70001 | 200 | get ticket |
| PASS | POST | /api/v2/tickets | 201 | create ticket |
| PASS | PUT | /api/v2/tickets/70001 | 200 | update ticket |
| PASS | GET | /api/v2/contacts | 200 | list contacts |
| PASS | GET | /api/v2/agents | 200 | list agents |

<details><summary>responses</summary>

**GET health** — `/health` (status 200)

```
{
  "status": "ok"
}
```

**GET list tickets** — `/api/v2/tickets` (status 200)

```
[
  {
    "id": 70001,
    "subject": "Cannot log in to dashboard",
    "description": "User reports a 403 error after password reset.",
    "status": 2,
    "priority": 2,
    "requester_id": 90001,
    "responder_id": 80001,
    "type": "Incident",
    "tags": [
      "login",
      "auth"
    ],
    "created_at": "2026-05-02T09:12:00Z",
    "updated_at": "2026-05-02T10:01:00Z"
  },
  {
    "id": 70002,
    "subject": "Invoice charged twice",
    "description": "Customer was billed twice for the May subscription.",
    "status": 3,
    "priority": 3,
    "requester_id": 90002,
    "responder
... (truncated)
```

**GET list tickets filtered** — `/api/v2/tickets?status=2&priority=2` (status 200)

```
[
  {
    "id": 70001,
    "subject": "Cannot log in to dashboard",
    "description": "User reports a 403 error after password reset.",
    "status": 2,
    "priority": 2,
    "requester_id": 90001,
    "responder_id": 80001,
    "type": "Incident",
    "tags": [
      "login",
      "auth"
    ],
    "created_at": "2026-05-02T09:12:00Z",
    "updated_at": "2026-05-02T10:01:00Z"
  }
]
```

**GET get ticket** — `/api/v2/tickets/70001` (status 200)

```
{
  "id": 70001,
  "subject": "Cannot log in to dashboard",
  "description": "User reports a 403 error after password reset.",
  "status": 2,
  "priority": 2,
  "requester_id": 90001,
  "responder_id": 80001,
  "type": "Incident",
  "tags": [
    "login",
    "auth"
  ],
  "created_at": "2026-05-02T09:12:00Z",
  "updated_at": "2026-05-02T10:01:00Z"
}
```

**POST create ticket** — `/api/v2/tickets` (status 201)

```
{
  "id": 70009,
  "subject": "Billing question",
  "description": "Please clarify my last invoice.",
  "status": 2,
  "priority": 2,
  "requester_id": 90001,
  "responder_id": null,
  "type": "Question",
  "tags": [
    "billing"
  ],
  "created_at": "2026-06-17T10:31:10Z",
  "updated_at": "2026-06-17T10:31:10Z"
}
```

**PUT update ticket** — `/api/v2/tickets/70001` (status 200)

```
{
  "id": 70001,
  "subject": "Cannot log in to dashboard",
  "description": "User reports a 403 error after password reset.",
  "status": 2,
  "priority": 2,
  "requester_id": 90001,
  "responder_id": 80001,
  "type": "Incident",
  "tags": [
    "login",
    "auth"
  ],
  "created_at": "2026-05-02T09:12:00Z",
  "updated_at": "2026-05-02T10:01:00Z"
}
```

**GET list contacts** — `/api/v2/contacts` (status 200)

```
[
  {
    "id": 90001,
    "name": "Avery Collins",
    "email": "avery@acme.example",
    "phone": "+1-202-555-0101",
    "company_id": 60001,
    "active": true,
    "created_at": "2026-04-10T09:00:00Z"
  },
  {
    "id": 90002,
    "name": "Bianca Ruiz",
    "email": "bianca@globex.example",
    "phone": "+1-202-555-0102",
    "company_id": 60002,
    "active": true,
    "created_at": "2026-04-12T09:00:00Z"
  },
  {
    "id": 90003,
    "name": "Caleb Nguyen",
    "email": "caleb@initech.example",
    "phone": "+1-202-555-0103",
    "company_id": 60003,
    "active": true,
    "created_at":
... (truncated)
```

**GET list agents** — `/api/v2/agents` (status 200)

```
[
  {
    "id": 80001,
    "available": true,
    "ticket_scope": 1,
    "occasional": false,
    "created_at": "2026-03-01T09:00:00Z",
    "contact": {
      "name": "Priya Sharma",
      "email": "priya@support.example"
    }
  },
  {
    "id": 80002,
    "available": true,
    "ticket_scope": 1,
    "occasional": false,
    "created_at": "2026-03-02T09:00:00Z",
    "contact": {
      "name": "Marcus Lee",
      "email": "marcus@support.example"
    }
  },
  {
    "id": 80003,
    "available": false,
    "ticket_scope": 2,
    "occasional": true,
    "created_at": "2026-03-03T09:00:00Z",
   
... (truncated)
```

</details>

### github-api (port 8019) — server: started

| Result | Method | Path | Status | Endpoint |
|--------|--------|------|--------|----------|
| PASS | GET | /health | 200 | health |
| PASS | GET | /user | 200 | authenticated user |
| PASS | GET | /orgs/orbit-labs/repos | 200 | org repos |
| PASS | GET | /repos/orbit-labs/auth-api | 200 | repo |
| PASS | GET | /repos/orbit-labs/auth-api/issues?state=open&labels=bug | 200 | open issues with bug label |
| PASS | GET | /repos/orbit-labs/auth-api/issues/142 | 200 | get issue |
| PASS | POST | /repos/orbit-labs/auth-api/issues | 201 | create issue |
| PASS | PATCH | /repos/orbit-labs/docs/issues/7 | 200 | close issue |
| PASS | GET | /repos/orbit-labs/auth-api/pulls?state=open | 200 | list open pulls |
| PASS | GET | /repos/orbit-labs/auth-api/pulls/144 | 200 | get pull |
| PASS | PUT | /repos/orbit-labs/auth-api/pulls/144/merge | 200 | merge pull |
| PASS | GET | /repos/orbit-labs/auth-api/issues/142/comments | 200 | list issue comments |
| PASS | POST | /repos/orbit-labs/auth-api/issues/142/comments | 201 | post issue comment |

<details><summary>responses</summary>

**GET health** — `/health` (status 200)

```
{
  "status": "ok"
}
```

**GET authenticated user** — `/user` (status 200)

```
{
  "login": "amelia-ortega",
  "id": 4001001,
  "name": "Amelia Ortega",
  "email": "amelia@orbit-labs.com",
  "avatar_url": "https://avatars.example.com/amelia.png",
  "type": "User",
  "site_admin": false,
  "company": "Orbit Labs",
  "public_repos": 12,
  "followers": 142,
  "following": 86
}
```

**GET org repos** — `/orgs/orbit-labs/repos` (status 200)

```
[
  {
    "id": 2100001,
    "name": "auth-api",
    "full_name": "orbit-labs/auth-api",
    "owner": {
      "login": "orbit-labs"
    },
    "private": true,
    "description": "Authentication service for Orbit Labs",
    "default_branch": "main",
    "language": "Go",
    "stargazers_count": 42,
    "forks_count": 8,
    "open_issues_count": 7,
    "created_at": "2024-04-12T10:00:00Z",
    "updated_at": "2026-05-22T11:00:00Z"
  },
  {
    "id": 2100002,
    "name": "billing-api",
    "full_name": "orbit-labs/billing-api",
    "owner": {
      "login": "orbit-labs"
    },
    "private": true
... (truncated)
```

**GET repo** — `/repos/orbit-labs/auth-api` (status 200)

```
{
  "id": 2100001,
  "name": "auth-api",
  "full_name": "orbit-labs/auth-api",
  "owner": {
    "login": "orbit-labs"
  },
  "private": true,
  "description": "Authentication service for Orbit Labs",
  "default_branch": "main",
  "language": "Go",
  "stargazers_count": 42,
  "forks_count": 8,
  "open_issues_count": 7,
  "created_at": "2024-04-12T10:00:00Z",
  "updated_at": "2026-05-22T11:00:00Z"
}
```

**GET open issues with bug label** — `/repos/orbit-labs/auth-api/issues?state=open&labels=bug` (status 200)

```
[
  {
    "id": 3000001,
    "number": 142,
    "title": "Refresh-token rotation under load",
    "body": "During load tests we see refresh-token issuance latency spike beyond 600ms p95. Suspected lock contention in session-store write path.",
    "state": "open",
    "user": {
      "login": "helena-park"
    },
    "assignee": {
      "login": "jonas-pereira"
    },
    "labels": [
      {
        "name": "bug"
      },
      {
        "name": "perf"
      }
    ],
    "milestone": {
      "title": "v2.0"
    },
    "created_at": "2026-05-22T11:00:00Z",
    "updated_at": "2026-05-26T09:00:00
```

**GET get issue** — `/repos/orbit-labs/auth-api/issues/142` (status 200)

```
{
  "id": 3000001,
  "number": 142,
  "title": "Refresh-token rotation under load",
  "body": "During load tests we see refresh-token issuance latency spike beyond 600ms p95. Suspected lock contention in session-store write path.",
  "state": "open",
  "user": {
    "login": "helena-park"
  },
  "assignee": {
    "login": "jonas-pereira"
  },
  "labels": [
    {
      "name": "bug"
    },
    {
      "name": "perf"
    }
  ],
  "milestone": {
    "title": "v2.0"
  },
  "created_at": "2026-05-22T11:00:00Z",
  "updated_at": "2026-05-26T09:00:00Z",
  "closed_at": null,
  "pull_request": null
}
```

**POST create issue** — `/repos/orbit-labs/auth-api/issues` (status 201)

```
{
  "id": 3000041,
  "number": 145,
  "title": "Cookie issuer feature flag gating",
  "body": "Confirm cookie issuer is gated behind auth_v2_rollout.",
  "state": "open",
  "user": {
    "login": "amelia-ortega"
  },
  "assignee": {
    "login": "amelia-ortega"
  },
  "labels": [
    {
      "name": "enhancement"
    }
  ],
  "milestone": null,
  "created_at": "2026-06-17T10:31:11Z",
  "updated_at": "2026-06-17T10:31:11Z",
  "closed_at": null,
  "pull_request": null
}
```

**PATCH close issue** — `/repos/orbit-labs/docs/issues/7` (status 200)

```
{
  "id": 3000040,
  "number": 7,
  "title": "Document feature flag rollout playbook",
  "body": "Closing the loop on the rollout playbook discussion.",
  "state": "closed",
  "user": {
    "login": "amelia-ortega"
  },
  "assignee": {
    "login": "amelia-ortega"
  },
  "labels": [
    {
      "name": "documentation"
    }
  ],
  "milestone": null,
  "created_at": "2026-04-15T10:00:00Z",
  "updated_at": "2026-05-10T14:00:00Z",
  "closed_at": "2026-05-10T14:00:00Z",
  "pull_request": null
}
```

**GET list open pulls** — `/repos/orbit-labs/auth-api/pulls?state=open` (status 200)

```
[
  {
    "id": 3000003,
    "number": 144,
    "title": "PR: introduce dual-write shim",
    "body": "Adds the dual-write shim behind the auth_v2_rollout flag.",
    "state": "open",
    "user": {
      "login": "amelia-ortega"
    },
    "assignee": {
      "login": "jonas-pereira"
    },
    "labels": [
      {
        "name": "enhancement"
      }
    ],
    "milestone": {
      "title": "v2.0"
    },
    "created_at": "2026-05-18T11:00:00Z",
    "updated_at": "2026-05-25T14:00:00Z",
    "closed_at": null,
    "pull_request": {
      "url": "/repos/auth-api/pulls/144"
    },
    "repo": "a
... (truncated)
```

**GET get pull** — `/repos/orbit-labs/auth-api/pulls/144` (status 200)

```
{
  "id": 3000003,
  "number": 144,
  "title": "PR: introduce dual-write shim",
  "body": "Adds the dual-write shim behind the auth_v2_rollout flag.",
  "state": "open",
  "user": {
    "login": "amelia-ortega"
  },
  "assignee": {
    "login": "jonas-pereira"
  },
  "labels": [
    {
      "name": "enhancement"
    }
  ],
  "milestone": {
    "title": "v2.0"
  },
  "created_at": "2026-05-18T11:00:00Z",
  "updated_at": "2026-05-25T14:00:00Z",
  "closed_at": null,
  "pull_request": {
    "url": "/repos/auth-api/pulls/144"
  },
  "repo": "auth-api",
  "head_branch": "feature/dual-write-shim",
  
... (truncated)
```

**PUT merge pull** — `/repos/orbit-labs/auth-api/pulls/144/merge` (status 200)

```
{
  "merged": true,
  "sha": "deadbeefcafe123"
}
```

**GET list issue comments** — `/repos/orbit-labs/auth-api/issues/142/comments` (status 200)

```
[
  {
    "id": 4000001,
    "issue_number": 142,
    "repo": "auth-api",
    "user": "jonas-pereira",
    "body": "Suspecting we need a write batch \u2014 every refresh kicks a SET. Let me try an N=8 batch on the dual-writer.",
    "created_at": "2026-05-22T14:00:00Z"
  },
  {
    "id": 4000002,
    "issue_number": 142,
    "repo": "auth-api",
    "user": "amelia-ortega",
    "body": "Agree. Once the batch lands let's re-run the load test from baseline.",
    "created_at": "2026-05-26T09:00:00Z"
  }
]
```

**POST post issue comment** — `/repos/orbit-labs/auth-api/issues/142/comments` (status 201)

```
{
  "id": 4000006,
  "issue_number": 142,
  "repo": "auth-api",
  "user": "amelia-ortega",
  "body": "Re-running the load test on N=8 batch now.",
  "created_at": "2026-06-17T10:31:11Z"
}
```

</details>

### gitlab-api (port 8046) — server: started

| Result | Method | Path | Status | Endpoint |
|--------|--------|------|--------|----------|
| PASS | GET | /health | 200 | health |
| PASS | GET | /api/v4/user | 200 | get current user |
| PASS | GET | /api/v4/projects | 200 | list projects |
| PASS | GET | /api/v4/projects/101 | 200 | get project |
| PASS | GET | /api/v4/projects/101/issues?state=opened | 200 | list issues |
| PASS | GET | /api/v4/projects/101/issues/1 | 200 | get issue |
| PASS | POST | /api/v4/projects/101/issues | 201 | create issue |
| PASS | PUT | /api/v4/projects/101/issues/2 | 200 | update issue (close) |
| PASS | GET | /api/v4/projects/101/merge_requests?state=opened | 200 | list merge requests |
| PASS | POST | /api/v4/projects/101/merge_requests | 201 | create merge request |
| PASS | PUT | /api/v4/projects/101/merge_requests/1/merge | 200 | merge merge request |
| PASS | GET | /api/v4/projects/101/pipelines | 200 | list pipelines |

<details><summary>responses</summary>

**GET health** — `/health` (status 200)

```
{
  "status": "ok"
}
```

**GET get current user** — `/api/v4/user` (status 200)

```
{
  "id": 201,
  "username": "amelia-ortega",
  "name": "Amelia Ortega",
  "email": "amelia.ortega@orbit-labs.com",
  "state": "active",
  "is_admin": true,
  "bio": "Platform engineering lead at Orbit Labs",
  "web_url": "https://gitlab.example.com/amelia-ortega",
  "avatar_url": "https://avatars.example.com/amelia.png",
  "created_at": "2024-01-10T10:00:00.000Z"
}
```

**GET list projects** — `/api/v4/projects` (status 200)

```
[
  {
    "id": 101,
    "name": "auth-service",
    "path": "auth-service",
    "path_with_namespace": "orbit-labs/auth-service",
    "namespace": "orbit-labs",
    "description": "Authentication and session service",
    "visibility": "private",
    "default_branch": "main",
    "star_count": 42,
    "forks_count": 8,
    "open_issues_count": 2,
    "created_at": "2024-04-12T10:00:00.000Z",
    "last_activity_at": "2026-05-26T09:00:00.000Z"
  },
  {
    "id": 102,
    "name": "billing-service",
    "path": "billing-service",
    "path_with_namespace": "orbit-labs/billing-service",
    "names
... (truncated)
```

**GET get project** — `/api/v4/projects/101` (status 200)

```
{
  "id": 101,
  "name": "auth-service",
  "path": "auth-service",
  "path_with_namespace": "orbit-labs/auth-service",
  "namespace": "orbit-labs",
  "description": "Authentication and session service",
  "visibility": "private",
  "default_branch": "main",
  "star_count": 42,
  "forks_count": 8,
  "open_issues_count": 2,
  "created_at": "2024-04-12T10:00:00.000Z",
  "last_activity_at": "2026-05-26T09:00:00.000Z"
}
```

**GET list issues** — `/api/v4/projects/101/issues?state=opened` (status 200)

```
[
  {
    "id": 5001,
    "iid": 1,
    "project_id": 101,
    "title": "Refresh-token rotation latency spike",
    "description": "Refresh-token issuance p95 latency spikes past 600ms during load tests; suspected lock contention.",
    "state": "opened",
    "author": "helena-park",
    "assignee": "jonas-pereira",
    "labels": [
      "bug",
      "perf"
    ],
    "created_at": "2026-05-22T11:00:00.000Z",
    "updated_at": "2026-05-26T09:00:00.000Z",
    "closed_at": null
  },
  {
    "id": 5002,
    "iid": 2,
    "project_id": 101,
    "title": "Add queue-depth metric for dual-writer",
  
... (truncated)
```

**GET get issue** — `/api/v4/projects/101/issues/1` (status 200)

```
{
  "id": 5001,
  "iid": 1,
  "project_id": 101,
  "title": "Refresh-token rotation latency spike",
  "description": "Refresh-token issuance p95 latency spikes past 600ms during load tests; suspected lock contention.",
  "state": "opened",
  "author": "helena-park",
  "assignee": "jonas-pereira",
  "labels": [
    "bug",
    "perf"
  ],
  "created_at": "2026-05-22T11:00:00.000Z",
  "updated_at": "2026-05-26T09:00:00.000Z",
  "closed_at": null
}
```

**POST create issue** — `/api/v4/projects/101/issues` (status 201)

```
{
  "id": 5022,
  "iid": 4,
  "project_id": 101,
  "title": "Add rate limiting to token endpoint",
  "description": "Protect /token from brute force.",
  "state": "opened",
  "author": "amelia-ortega",
  "assignee": "helena-park",
  "labels": [
    "security"
  ],
  "created_at": "2026-06-17T10:31:12.000Z",
  "updated_at": "2026-06-17T10:31:12.000Z",
  "closed_at": null
}
```

**PUT update issue (close)** — `/api/v4/projects/101/issues/2` (status 200)

```
{
  "id": 5002,
  "iid": 2,
  "project_id": 101,
  "title": "Add queue-depth metric for dual-writer",
  "description": "Need a gauge for the dual-writer queue depth so we can alert when it grows.",
  "state": "opened",
  "author": "amelia-ortega",
  "assignee": "helena-park",
  "labels": [
    "enhancement"
  ],
  "created_at": "2026-05-20T10:00:00.000Z",
  "updated_at": "2026-05-23T16:00:00.000Z",
  "closed_at": null
}
```

**GET list merge requests** — `/api/v4/projects/101/merge_requests?state=opened` (status 200)

```
[
  {
    "id": 6001,
    "iid": 1,
    "project_id": 101,
    "title": "Introduce dual-write shim",
    "description": "Adds the dual-write shim behind the auth_v2_rollout flag.",
    "state": "opened",
    "source_branch": "feature/dual-write-shim",
    "target_branch": "main",
    "author": "amelia-ortega",
    "assignee": "jonas-pereira",
    "merge_status": "can_be_merged",
    "draft": false,
    "created_at": "2026-05-18T11:00:00.000Z",
    "updated_at": "2026-05-25T14:00:00.000Z",
    "merged_at": null
  }
]
```

**POST create merge request** — `/api/v4/projects/101/merge_requests` (status 201)

```
{
  "id": 6021,
  "iid": 3,
  "project_id": 101,
  "title": "Add token rate limiter",
  "description": "",
  "state": "opened",
  "source_branch": "feature/token-rate-limit",
  "target_branch": "main",
  "author": "amelia-ortega",
  "assignee": "",
  "merge_status": "can_be_merged",
  "draft": false,
  "created_at": "2026-06-17T10:31:12.000Z",
  "updated_at": "2026-06-17T10:31:12.000Z",
  "merged_at": null
}
```

**PUT merge merge request** — `/api/v4/projects/101/merge_requests/1/merge` (status 200)

```
{
  "id": 6001,
  "iid": 1,
  "project_id": 101,
  "title": "Introduce dual-write shim",
  "description": "Adds the dual-write shim behind the auth_v2_rollout flag.",
  "state": "opened",
  "source_branch": "feature/dual-write-shim",
  "target_branch": "main",
  "author": "amelia-ortega",
  "assignee": "jonas-pereira",
  "merge_status": "can_be_merged",
  "draft": false,
  "created_at": "2026-05-18T11:00:00.000Z",
  "updated_at": "2026-05-25T14:00:00.000Z",
  "merged_at": null
}
```

**GET list pipelines** — `/api/v4/projects/101/pipelines` (status 200)

```
[
  {
    "id": 9002,
    "project_id": 101,
    "ref": "feature/dual-write-shim",
    "sha": "b2c3d4e5f6a1",
    "status": "running",
    "source": "merge_request_event",
    "duration": 0,
    "created_at": "2026-05-26T09:05:00.000Z",
    "updated_at": "2026-05-26T09:05:00.000Z"
  },
  {
    "id": 9001,
    "project_id": 101,
    "ref": "main",
    "sha": "a1b2c3d4e5f6",
    "status": "success",
    "source": "push",
    "duration": 412,
    "created_at": "2026-05-26T08:30:00.000Z",
    "updated_at": "2026-05-26T08:37:00.000Z"
  },
  {
    "id": 9003,
    "project_id": 101,
    "ref": "featu
... (truncated)
```

</details>

### gmail-api (port 8017) — server: started

| Result | Method | Path | Status | Endpoint |
|--------|--------|------|--------|----------|
| PASS | GET | /health | 200 | health |
| PASS | GET | /gmail/v1/users/me/profile | 200 | profile |
| PASS | GET | /gmail/v1/users/me/labels | 200 | labels |
| PASS | POST | /gmail/v1/users/me/labels | 201 | create label |
| PASS | GET | /gmail/v1/users/me/messages?labelIds=INBOX | 200 | list inbox |
| PASS | GET | /gmail/v1/users/me/messages?q=is:unread%20from:jonas | 200 | search unread from jonas |
| PASS | GET | /gmail/v1/users/me/messages/msg-100 | 200 | get message |
| PASS | POST | /gmail/v1/users/me/messages/send | 201 | send message |
| PASS | POST | /gmail/v1/users/me/messages/msg-101/modify | 200 | mark message read |
| PASS | POST | /gmail/v1/users/me/messages/msg-105/modify | 200 | star message |
| PASS | POST | /gmail/v1/users/me/messages/msg-104/trash | 200 | trash spam |
| PASS | GET | /gmail/v1/users/me/threads?q=label:Orbit%20Labs | 200 | list threads |
| PASS | GET | /gmail/v1/users/me/threads/thr-100 | 200 | get thread |
| PASS | POST | /gmail/v1/users/me/drafts | 201 | create draft |
| PASS | POST | /gmail/v1/users/me/drafts/draft-001/send | 200 | send draft |

<details><summary>responses</summary>

**GET health** — `/health` (status 200)

```
{
  "status": "ok"
}
```

**GET profile** — `/gmail/v1/users/me/profile` (status 200)

```
{
  "emailAddress": "amelia@orbit-labs.com",
  "messagesTotal": 6,
  "threadsTotal": 5,
  "historyId": "104221"
}
```

**GET labels** — `/gmail/v1/users/me/labels` (status 200)

```
{
  "labels": [
    {
      "id": "INBOX",
      "name": "INBOX",
      "type": "system"
    },
    {
      "id": "SENT",
      "name": "SENT",
      "type": "system"
    },
    {
      "id": "DRAFTS",
      "name": "DRAFT",
      "type": "system"
    },
    {
      "id": "TRASH",
      "name": "TRASH",
      "type": "system"
    },
    {
      "id": "SPAM",
      "name": "SPAM",
      "type": "system"
    },
    {
      "id": "Label_orbit",
      "name": "Orbit Labs",
      "type": "user"
    },
    {
      "id": "Label_followup",
      "name": "Follow up",
      "type": "user"
    },
    {
 
```

**POST create label** — `/gmail/v1/users/me/labels` (status 201)

```
{
  "id": "Label_ac4abcbe",
  "name": "Customer escalations",
  "type": "user",
  "messages_total": 0,
  "messagesTotal": 0,
  "messages_unread": 0,
  "messagesUnread": 0,
  "threads_total": 0,
  "threadsTotal": 0,
  "threads_unread": 0,
  "threadsUnread": 0
}
```

**GET list inbox** — `/gmail/v1/users/me/messages?labelIds=INBOX` (status 200)

```
{
  "messages": [
    {
      "id": "msg-105",
      "threadId": "thr-105"
    },
    {
      "id": "msg-103",
      "threadId": "thr-103"
    },
    {
      "id": "msg-100",
      "threadId": "thr-100"
    },
    {
      "id": "msg-101",
      "threadId": "thr-101"
    }
  ],
  "resultSizeEstimate": 4
}
```

**GET search unread from jonas** — `/gmail/v1/users/me/messages?q=is:unread%20from:jonas` (status 200)

```
{
  "messages": [],
  "resultSizeEstimate": 0
}
```

**GET get message** — `/gmail/v1/users/me/messages/msg-100` (status 200)

```
{
  "id": "msg-100",
  "threadId": "thr-100",
  "labelIds": [
    "INBOX",
    "Label_orbit"
  ],
  "snippet": "Hi Amelia \u2014 sharing the draft cutover plan for Friday...",
  "internalDate": "1748016000000",
  "sizeEstimate": 5400,
  "payload": {
    "headers": [
      {
        "name": "From",
        "value": "jonas@orbit-labs.com"
      },
      {
        "name": "To",
        "value": "amelia@orbit-labs.com"
      },
      {
        "name": "Cc",
        "value": ""
      },
      {
        "name": "Subject",
        "value": "Auth v2 cutover plan \u2014 draft"
      },
      {
        
... (truncated)
```

**POST send message** — `/gmail/v1/users/me/messages/send` (status 201)

```
{
  "id": "msg-ef32666144",
  "threadId": "thr-101",
  "labelIds": [
    "SENT"
  ],
  "snippet": "Helena \u2014 let's correlate the spike with shim warmup. Pulling timing now.",
  "internalDate": "1781672472589",
  "sizeEstimate": 95,
  "payload": {
    "headers": [
      {
        "name": "From",
        "value": "amelia@orbit-labs.com"
      },
      {
        "name": "To",
        "value": "helena@orbit-labs.com"
      },
      {
        "name": "Cc",
        "value": ""
      },
      {
        "name": "Subject",
        "value": "Re: Latency spike alert"
      },
      {
        "name": 
```

**POST mark message read** — `/gmail/v1/users/me/messages/msg-101/modify` (status 200)

```
{
  "id": "msg-101",
  "threadId": "thr-101",
  "labelIds": [
    "INBOX",
    "Label_orbit",
    "Label_followup"
  ],
  "snippet": "FYI alertmanager fired at 10:42 UTC for auth.refresh p95 > 600ms...",
  "internalDate": "1748005200000",
  "sizeEstimate": 3200,
  "payload": {
    "headers": [
      {
        "name": "From",
        "value": "helena@orbit-labs.com"
      },
      {
        "name": "To",
        "value": "amelia@orbit-labs.com"
      },
      {
        "name": "Cc",
        "value": "jonas@orbit-labs.com"
      },
      {
        "name": "Subject",
        "value": "Latency spi
... (truncated)
```

**POST star message** — `/gmail/v1/users/me/messages/msg-105/modify` (status 200)

```
{
  "id": "msg-105",
  "threadId": "thr-105",
  "labelIds": [
    "INBOX",
    "Label_followup"
  ],
  "snippet": "Quick reminder about the open house...",
  "internalDate": "1748191500000",
  "sizeEstimate": 1900,
  "payload": {
    "headers": [
      {
        "name": "From",
        "value": "sarah.whitfield@cascaderealty.com"
      },
      {
        "name": "To",
        "value": "amelia@orbit-labs.com"
      },
      {
        "name": "Cc",
        "value": ""
      },
      {
        "name": "Subject",
        "value": "Open house this Saturday \u2014 412 Maple Grove"
      },
      {
 
... (truncated)
```

**POST trash spam** — `/gmail/v1/users/me/messages/msg-104/trash` (status 200)

```
{
  "id": "msg-104",
  "threadId": "thr-104",
  "labelIds": [
    "SPAM"
  ],
  "snippet": "We came across your profile...",
  "internalDate": "1748145600000",
  "sizeEstimate": 2200,
  "payload": {
    "headers": [
      {
        "name": "From",
        "value": "careers-spam@example-recruit.com"
      },
      {
        "name": "To",
        "value": "amelia@orbit-labs.com"
      },
      {
        "name": "Cc",
        "value": ""
      },
      {
        "name": "Subject",
        "value": "Exclusive opportunity for senior engineers"
      },
      {
        "name": "Date",
        "value
... (truncated)
```

**GET list threads** — `/gmail/v1/users/me/threads?q=label:Orbit%20Labs` (status 200)

```
{
  "threads": [],
  "resultSizeEstimate": 0
}
```

**GET get thread** — `/gmail/v1/users/me/threads/thr-100` (status 200)

```
{
  "id": "thr-100",
  "historyId": "104221",
  "messages": [
    {
      "id": "msg-100",
      "threadId": "thr-100",
      "labelIds": [
        "INBOX",
        "Label_orbit"
      ],
      "snippet": "Hi Amelia \u2014 sharing the draft cutover plan for Friday...",
      "internalDate": "1748016000000",
      "sizeEstimate": 5400,
      "payload": {
        "headers": [
          {
            "name": "From",
            "value": "jonas@orbit-labs.com"
          },
          {
            "name": "To",
            "value": "amelia@orbit-labs.com"
          },
          {
            "name"
... (truncated)
```

**POST create draft** — `/gmail/v1/users/me/drafts` (status 201)

```
{
  "id": "draft-fe1999f6d9",
  "thread_id": "",
  "to_addr": "jonas@orbit-labs.com",
  "cc_addr": "",
  "subject": "Cutover dry-run notes",
  "body": "Few quick notes from the dry-run...",
  "updated_at": "2026-06-17T10:31:12Z"
}
```

**POST send draft** — `/gmail/v1/users/me/drafts/draft-001/send` (status 200)

```
{
  "id": "msg-570382e1a4",
  "threadId": "thr-101",
  "labelIds": [
    "SENT"
  ],
  "snippet": "Helena \u2014 adding @jonas. Let's correlate the spike with the shim warmup. Can you pull the timing of the dual-writer flush?\n\n\u2014 Amelia",
  "internalDate": "1781672472598",
  "sizeEstimate": 169,
  "payload": {
    "headers": [
      {
        "name": "From",
        "value": "amelia@orbit-labs.com"
      },
      {
        "name": "To",
        "value": "helena@orbit-labs.com"
      },
      {
        "name": "Cc",
        "value": "jonas@orbit-labs.com"
      },
      {
        "name": 
... (truncated)
```

</details>

### google-analytics-api (port 8068) — server: started

| Result | Method | Path | Status | Endpoint |
|--------|--------|------|--------|----------|
| PASS | GET | /health | 200 | health |
| PASS | GET | /v1beta/properties/412233445 | 200 | get property |
| PASS | GET | /v1beta/properties/412233445/metadata | 200 | get metadata |
| PASS | POST | /v1beta/properties/412233445:runReport | 200 | run report by country |
| PASS | POST | /v1beta/properties/412233445:runReport | 200 | run report by date and device |
| PASS | POST | /v1beta/properties/412233445:runRealtimeReport | 200 | run realtime report |
| PASS | POST | /v1beta/properties/412233445:batchRunReports | 200 | batch run reports |

<details><summary>responses</summary>

**GET health** — `/health` (status 200)

```
{
  "status": "ok"
}
```

**GET get property** — `/v1beta/properties/412233445` (status 200)

```
{
  "property_id": "412233445",
  "name": "Orbit Labs Website",
  "currency_code": "USD",
  "time_zone": "America/New_York",
  "create_time": "2025-01-15T10:00:00.000Z",
  "industry_category": "TECHNOLOGY"
}
```

**GET get metadata** — `/v1beta/properties/412233445/metadata` (status 200)

```
{
  "name": "properties/412233445/metadata",
  "dimensions": [
    {
      "apiName": "date",
      "uiName": "date",
      "category": "General"
    },
    {
      "apiName": "country",
      "uiName": "country",
      "category": "General"
    },
    {
      "apiName": "pagePath",
      "uiName": "pagePath",
      "category": "Page / Screen"
    },
    {
      "apiName": "deviceCategory",
      "uiName": "deviceCategory",
      "category": "General"
    }
  ],
  "metrics": [
    {
      "apiName": "sessions",
      "uiName": "sessions",
      "type": "TYPE_INTEGER"
    },
    {
      "apiNam
... (truncated)
```

**POST run report by country** — `/v1beta/properties/412233445:runReport` (status 200)

```
{
  "dimensionHeaders": [
    {
      "name": "country"
    }
  ],
  "metricHeaders": [
    {
      "name": "sessions",
      "type": "TYPE_INTEGER"
    },
    {
      "name": "activeUsers",
      "type": "TYPE_INTEGER"
    }
  ],
  "rows": [
    {
      "dimensionValues": [
        {
          "value": "United States"
        }
      ],
      "metricValues": [
        {
          "value": "688"
        },
        {
          "value": "571"
        }
      ]
    },
    {
      "dimensionValues": [
        {
          "value": "United Kingdom"
        }
      ],
      "metricValues": [
        
... (truncated)
```

**POST run report by date and device** — `/v1beta/properties/412233445:runReport` (status 200)

```
{
  "dimensionHeaders": [
    {
      "name": "date"
    },
    {
      "name": "deviceCategory"
    }
  ],
  "metricHeaders": [
    {
      "name": "screenPageViews",
      "type": "TYPE_INTEGER"
    },
    {
      "name": "eventCount",
      "type": "TYPE_INTEGER"
    }
  ],
  "rows": [
    {
      "dimensionValues": [
        {
          "value": "20260520"
        },
        {
          "value": "desktop"
        }
      ],
      "metricValues": [
        {
          "value": "435"
        },
        {
          "value": "1580"
        }
      ]
    },
    {
      "dimensionValues": [
    
... (truncated)
```

**POST run realtime report** — `/v1beta/properties/412233445:runRealtimeReport` (status 200)

```
{
  "dimensionHeaders": [
    {
      "name": "country"
    }
  ],
  "metricHeaders": [
    {
      "name": "activeUsers",
      "type": "TYPE_INTEGER"
    }
  ],
  "rows": [
    {
      "dimensionValues": [
        {
          "value": "United States"
        }
      ],
      "metricValues": [
        {
          "value": "29"
        }
      ]
    },
    {
      "dimensionValues": [
        {
          "value": "United Kingdom"
        }
      ],
      "metricValues": [
        {
          "value": "7"
        }
      ]
    },
    {
      "dimensionValues": [
        {
          "value": "Ge
```

**POST batch run reports** — `/v1beta/properties/412233445:batchRunReports` (status 200)

```
{
  "kind": "analyticsData#batchRunReports",
  "reports": [
    {
      "dimensionHeaders": [
        {
          "name": "country"
        }
      ],
      "metricHeaders": [
        {
          "name": "sessions",
          "type": "TYPE_INTEGER"
        }
      ],
      "rows": [
        {
          "dimensionValues": [
            {
              "value": "United States"
            }
          ],
          "metricValues": [
            {
              "value": "688"
            }
          ]
        },
        {
          "dimensionValues": [
            {
              "value": "United K
... (truncated)
```

</details>

### google-calendar-api (port 8016) — server: started

| Result | Method | Path | Status | Endpoint |
|--------|--------|------|--------|----------|
| PASS | GET | /health | 200 | health |
| PASS | GET | /calendar/v3/users/me/calendarList | 200 | list calendars |
| PASS | GET | /calendar/v3/calendars/primary | 200 | get primary calendar |
| PASS | GET | /calendar/v3/calendars/primary/events?timeMin=2026-05-26T00:00:00Z&timeMax=2026-05-31T23:59:59Z&orderBy=startTime | 200 | list events this week |
| PASS | GET | /calendar/v3/calendars/primary/events?q=auth | 200 | search events |
| PASS | GET | /calendar/v3/calendars/primary/events/evt-003 | 200 | get event |
| PASS | POST | /calendar/v3/calendars/primary/events | 201 | create event |
| PASS | PATCH | /calendar/v3/calendars/primary/events/evt-003 | 200 | patch event |
| PASS | DELETE | /calendar/v3/calendars/amelia.personal@gmail.com/events/evt-006 | 200 | delete event |
| PASS | POST | /calendar/v3/freeBusy | 200 | freeBusy |

<details><summary>responses</summary>

**GET health** — `/health` (status 200)

```
{
  "status": "ok"
}
```

**GET list calendars** — `/calendar/v3/users/me/calendarList` (status 200)

```
{
  "kind": "calendar#calendarList",
  "items": [
    {
      "id": "amelia@orbit-labs.com",
      "summary": "Amelia Ortega",
      "description": "Primary calendar",
      "time_zone": "America/Los_Angeles",
      "access_role": "owner",
      "primary": true,
      "color_id": "1"
    },
    {
      "id": "orbit-labs.com_eng@group.calendar.google.com",
      "summary": "Engineering",
      "description": "Team-wide engineering events",
      "time_zone": "America/Los_Angeles",
      "access_role": "writer",
      "primary": false,
      "color_id": "2"
    },
    {
      "id": "orbit-labs.c
... (truncated)
```

**GET get primary calendar** — `/calendar/v3/calendars/primary` (status 200)

```
{
  "id": "amelia@orbit-labs.com",
  "summary": "Amelia Ortega",
  "description": "Primary calendar",
  "time_zone": "America/Los_Angeles",
  "access_role": "owner",
  "primary": true,
  "color_id": "1"
}
```

**GET list events this week** — `/calendar/v3/calendars/primary/events?timeMin=2026-05-26T00:00:00Z&timeMax=2026-05-31T23:59:59Z&orderBy=startTime` (status 200)

```
{
  "kind": "calendar#events",
  "items": [
    {
      "id": "evt-001",
      "calendar_id": "amelia@orbit-labs.com",
      "summary": "Weekly 1:1 with Jonas",
      "description": "Direct report sync",
      "location": "",
      "start": {
        "dateTime": "2026-05-26T15:00:00-07:00",
        "timeZone": "America/Los_Angeles"
      },
      "end": {
        "dateTime": "2026-05-26T15:30:00-07:00",
        "timeZone": "America/Los_Angeles"
      },
      "all_day": false,
      "status": "confirmed",
      "creator": "amelia@orbit-labs.com",
      "organizer": "amelia@orbit-labs.com",
   
... (truncated)
```

**GET search events** — `/calendar/v3/calendars/primary/events?q=auth` (status 200)

```
{
  "kind": "calendar#events",
  "items": [
    {
      "id": "evt-003",
      "calendar_id": "amelia@orbit-labs.com",
      "summary": "Auth v2 cutover dry-run",
      "description": "Rehearsal for next week's cutover",
      "location": "Zoom: https://zoom.example.com/j/12345",
      "start": {
        "dateTime": "2026-05-28T17:00:00-07:00",
        "timeZone": "America/Los_Angeles"
      },
      "end": {
        "dateTime": "2026-05-28T19:00:00-07:00",
        "timeZone": "America/Los_Angeles"
      },
      "all_day": false,
      "status": "tentative",
      "creator": "amelia@orbit-lab
... (truncated)
```

**GET get event** — `/calendar/v3/calendars/primary/events/evt-003` (status 200)

```
{
  "id": "evt-003",
  "calendar_id": "amelia@orbit-labs.com",
  "summary": "Auth v2 cutover dry-run",
  "description": "Rehearsal for next week's cutover",
  "location": "Zoom: https://zoom.example.com/j/12345",
  "start": {
    "dateTime": "2026-05-28T17:00:00-07:00",
    "timeZone": "America/Los_Angeles"
  },
  "end": {
    "dateTime": "2026-05-28T19:00:00-07:00",
    "timeZone": "America/Los_Angeles"
  },
  "all_day": false,
  "status": "tentative",
  "creator": "amelia@orbit-labs.com",
  "organizer": "amelia@orbit-labs.com",
  "recurrence": [],
  "visibility": "private",
  "attendees": [

... (truncated)
```

**POST create event** — `/calendar/v3/calendars/primary/events` (status 201)

```
{
  "id": "evt-7848c443ef",
  "calendar_id": "amelia@orbit-labs.com",
  "summary": "RFC review: billing gRPC",
  "description": "",
  "location": "Zoom",
  "start": {
    "dateTime": "2026-05-30T15:00:00-07:00",
    "timeZone": "America/Los_Angeles"
  },
  "end": {
    "dateTime": "2026-05-30T16:00:00-07:00",
    "timeZone": "America/Los_Angeles"
  },
  "all_day": false,
  "status": "confirmed",
  "creator": "amelia@orbit-labs.com",
  "organizer": "amelia@orbit-labs.com",
  "recurrence": [],
  "visibility": "default",
  "attendees": []
}
```

**PATCH patch event** — `/calendar/v3/calendars/primary/events/evt-003` (status 200)

```
{
  "id": "evt-003",
  "calendar_id": "amelia@orbit-labs.com",
  "summary": "Auth v2 cutover dry-run",
  "description": "Rehearsal for next week's cutover",
  "location": "Zoom: https://zoom.example.com/j/12345",
  "start": {
    "dateTime": "2026-05-28T17:00:00-07:00",
    "timeZone": "America/Los_Angeles"
  },
  "end": {
    "dateTime": "2026-05-28T19:00:00-07:00",
    "timeZone": "America/Los_Angeles"
  },
  "all_day": false,
  "status": "tentative",
  "creator": "amelia@orbit-labs.com",
  "organizer": "amelia@orbit-labs.com",
  "recurrence": [],
  "visibility": "private",
  "attendees": [

... (truncated)
```

**DELETE delete event** — `/calendar/v3/calendars/amelia.personal@gmail.com/events/evt-006` (status 200)

```
{
  "deleted": true,
  "id": "evt-006"
}
```

**POST freeBusy** — `/calendar/v3/freeBusy` (status 200)

```
{
  "kind": "calendar#freeBusy",
  "timeMin": "2026-05-26T00:00:00Z",
  "timeMax": "2026-05-31T00:00:00Z",
  "calendars": {
    "amelia@orbit-labs.com": {
      "busy": [
        {
          "start": "2026-05-26T15:00:00-07:00",
          "end": "2026-05-26T15:30:00-07:00"
        },
        {
          "start": "2026-05-26T16:00:00-07:00",
          "end": "2026-05-26T17:00:00-07:00"
        },
        {
          "start": "2026-05-27T09:00:00-07:00",
          "end": "2026-05-27T11:30:00-07:00"
        }
      ]
    },
    "orbit-labs.com_eng@group.calendar.google.com": {
      "busy": []
  
```

</details>

### google-classroom-api (port 8002) — server: started

| Result | Method | Path | Status | Endpoint |
|--------|--------|------|--------|----------|
| PASS | GET | /health | 200 | Health Check |
| PASS | GET | /v1/courses | 200 | List All Courses |
| PASS | GET | /v1/courses?courseStates=ACTIVE | 200 | List Active Courses |
| PASS | GET | /v1/courses/course_005 | 200 | Get Course (Intertidal Lab) |
| PASS | GET | /v1/courses?courseStates=ARCHIVED | 200 | List Archived Courses |
| PASS | GET | /v1/courses/course_001 | 200 | Get Course (Valid) |
| WARN | GET | /v1/courses/course_999 | 404 | Get Course (404) |
| PASS | POST | /v1/courses | 201 | Create Course |
| PASS | PATCH | /v1/courses/course_001 | 200 | Update Course |
| PASS | POST | /v1/courses/course_004:archive | 200 | Archive Course |
| PASS | GET | /v1/courses/course_001/courseWork | 200 | List CourseWork |
| PASS | GET | /v1/courses/course_005/courseWork | 200 | List CourseWork (Intertidal Lab) |
| PASS | GET | /v1/courses/course_001/courseWork?topicId=topic_104 | 200 | List CourseWork by Topic |
| PASS | GET | /v1/courses/course_001/courseWork?orderBy=dueDate desc | 200 | List CourseWork ordered by dueDate |
| PASS | GET | /v1/courses/course_001/courseWork/cw_101 | 200 | Get CourseWork (Valid) |
| WARN | GET | /v1/courses/course_001/courseWork/cw_999 | 404 | Get CourseWork (404) |
| PASS | POST | /v1/courses/course_001/courseWork | 201 | Create CourseWork (Assignment) |
| PASS | POST | /v1/courses/course_002/courseWork | 201 | Create CourseWork (Question) |
| PASS | PATCH | /v1/courses/course_001/courseWork/cw_109 | 200 | Update CourseWork (Due Date) |
| PASS | DELETE | /v1/courses/course_001/courseWork/cw_103 | 200 | Delete CourseWork |
| WARN | DELETE | /v1/courses/course_001/courseWork/cw_999 | 404 | Delete CourseWork (404) |
| PASS | GET | /v1/courses/course_001/topics | 200 | List Topics |
| PASS | GET | /v1/courses/course_005/topics | 200 | List Topics (Intertidal Lab) |
| PASS | GET | /v1/courses/course_001/topics/topic_101 | 200 | Get Topic (Valid) |
| WARN | GET | /v1/courses/course_001/topics/topic_999 | 404 | Get Topic (404) |
| PASS | POST | /v1/courses/course_001/topics | 201 | Create Topic |
| PASS | PATCH | /v1/courses/course_001/topics/topic_101 | 200 | Update Topic |
| PASS | DELETE | /v1/courses/course_001/topics/topic_107 | 200 | Delete Topic |
| PASS | GET | /v1/courses/course_001/courseWork/cw_101/studentSubmissions | 200 | List Submissions |
| PASS | GET | /v1/courses/course_005/courseWork/cw_501/studentSubmissions | 200 | List Submissions (Intertidal Lab - Kelp Upload) |
| PASS | GET | /v1/courses/course_001/courseWork/cw_108/studentSubmissions?states=TURNED_IN | 200 | List Submissions (TURNED_IN filter) |
| PASS | GET | /v1/courses/course_001/courseWork/cw_101/studentSubmissions?states=RETURNED | 200 | List Submissions (RETURNED filter) |
| PASS | GET | /v1/courses/course_001/courseWork/cw_101/studentSubmissions?late=true | 200 | List Submissions (Late filter) |
| PASS | GET | /v1/courses/course_001/courseWork/cw_101/studentSubmissions/sub_001 | 200 | Get Submission (Valid) |
| WARN | GET | /v1/courses/course_001/courseWork/cw_101/studentSubmissions/sub_999 | 404 | Get Submission (404) |
| PASS | PATCH | /v1/courses/course_001/courseWork/cw_108/studentSubmissions/sub_024 | 200 | Grade Submission |
| PASS | POST | /v1/courses/course_001/courseWork/cw_108/studentSubmissions/sub_024:return | 200 | Return Submission |
| PASS | POST | /v1/courses/course_001/courseWork/cw_108/studentSubmissions/sub_025:reclaim | 200 | Reclaim Submission |
| PASS | GET | /v1/courses/course_001/students | 200 | List Students |
| PASS | GET | /v1/courses/course_005/students | 200 | List Students (Intertidal Lab) |
| PASS | GET | /v1/courses/course_002/students?pageSize=10&pageToken=10 | 200 | List Students (Page 2) |
| PASS | GET | /v1/courses/course_001/students/student_001 | 200 | Get Student (Valid) |
| WARN | GET | /v1/courses/course_001/students/student_999 | 404 | Get Student (404) |
| PASS | POST | /v1/courses/course_001/students | 201 | Invite Student |
| PASS | DELETE | /v1/courses/course_001/students/student_048 | 200 | Remove Student |
| PASS | GET | /v1/courses/course_001/teachers | 200 | List Teachers |
| PASS | GET | /v1/courses/course_001/teachers/teacher_001 | 200 | Get Teacher (Valid) |
| WARN | GET | /v1/courses/course_001/teachers/teacher_999 | 404 | Get Teacher (404) |
| PASS | GET | /v1/courses/course_002/teachers | 200 | List Teachers (course_002 - multiple) |
| PASS | GET | /v1/courses/course_001/announcements | 200 | List Announcements |
| PASS | GET | /v1/courses/course_001/announcements/ann_001 | 200 | Get Announcement (Valid) |
| WARN | GET | /v1/courses/course_001/announcements/ann_999 | 404 | Get Announcement (404) |
| PASS | POST | /v1/courses/course_001/announcements | 201 | Create Announcement |
| PASS | PATCH | /v1/courses/course_001/announcements/ann_002 | 200 | Update Announcement |
| PASS | DELETE | /v1/courses/course_001/announcements/ann_004 | 200 | Delete Announcement |
| PASS | GET | /v1/courses/course_001/courseWorkMaterials | 200 | List Materials |
| PASS | GET | /v1/courses/course_001/courseWorkMaterials/mat_001 | 200 | Get Material (Valid) |
| WARN | GET | /v1/courses/course_001/courseWorkMaterials/mat_999 | 404 | Get Material (404) |
| PASS | POST | /v1/courses/course_001/courseWorkMaterials | 201 | Create Material |
| PASS | POST | /v1/courses/course_005/courseWorkMaterials | 201 | Create Material (Intertidal Lab - Evidence Plates) |
| PASS | GET | /v1/courses/course_002/courseWorkMaterials | 200 | List Materials (course_002) |

<details><summary>responses</summary>

**GET Health Check** — `/health` (status 200)

```
{
  "status": "ok"
}
```

**GET List All Courses** — `/v1/courses` (status 200)

```
{
  "courses": [
    {
      "id": "course_001",
      "name": "AP Computer Science A",
      "section": "Period 2",
      "descriptionHeading": "Welcome to AP CS A",
      "description": "Rigorous college-level course covering Java programming fundamentals including object-oriented design data structures and algorithms. Prepares students for the AP Computer Science A exam.",
      "room": "Room 214",
      "ownerId": "teacher_001",
      "courseState": "ACTIVE",
      "creationTime": "2025-01-06T08:00:00Z",
      "updateTime": "2025-04-25T14:30:00Z",
      "enrollmentCode": "apcsa25",
      "
... (truncated)
```

**GET List Active Courses** — `/v1/courses?courseStates=ACTIVE` (status 200)

```
{
  "courses": [
    {
      "id": "course_001",
      "name": "AP Computer Science A",
      "section": "Period 2",
      "descriptionHeading": "Welcome to AP CS A",
      "description": "Rigorous college-level course covering Java programming fundamentals including object-oriented design data structures and algorithms. Prepares students for the AP Computer Science A exam.",
      "room": "Room 214",
      "ownerId": "teacher_001",
      "courseState": "ACTIVE",
      "creationTime": "2025-01-06T08:00:00Z",
      "updateTime": "2025-04-25T14:30:00Z",
      "enrollmentCode": "apcsa25",
      "
... (truncated)
```

**GET Get Course (Intertidal Lab)** — `/v1/courses/course_005` (status 200)

```
{
  "course": {
    "id": "course_005",
    "name": "Casco Bay Intertidal 2025",
    "section": "Spring 2025",
    "descriptionHeading": "Lab fieldwork coordination",
    "description": "Shared workspace for Crawford Lab intertidal research team \u2014 survey data protocols and materials.",
    "room": "Marine Sciences 204",
    "ownerId": "teacher_003",
    "courseState": "ACTIVE",
    "creationTime": "2025-01-15T09:00:00Z",
    "updateTime": "2025-05-12T14:30:00Z",
    "enrollmentCode": "cbint25",
    "alternateLink": "https://classroom.google.com/c/course_005",
    "guardiansEnabled": false
```

**GET List Archived Courses** — `/v1/courses?courseStates=ARCHIVED` (status 200)

```
{
  "courses": [
    {
      "id": "course_004",
      "name": "Intro to Python (Fall 2024)",
      "section": "Period 3",
      "descriptionHeading": "Welcome to Python",
      "description": "Introduction to programming using Python. Covers variables loops functions and basic data structures. No prior coding experience required.",
      "room": "Room 214",
      "ownerId": "teacher_001",
      "courseState": "ARCHIVED",
      "creationTime": "2024-08-19T08:00:00Z",
      "updateTime": "2024-12-20T15:00:00Z",
      "enrollmentCode": "python24",
      "alternateLink": "https://classroom.google
... (truncated)
```

**GET Get Course (Valid)** — `/v1/courses/course_001` (status 200)

```
{
  "course": {
    "id": "course_001",
    "name": "AP Computer Science A",
    "section": "Period 2",
    "descriptionHeading": "Welcome to AP CS A",
    "description": "Rigorous college-level course covering Java programming fundamentals including object-oriented design data structures and algorithms. Prepares students for the AP Computer Science A exam.",
    "room": "Room 214",
    "ownerId": "teacher_001",
    "courseState": "ACTIVE",
    "creationTime": "2025-01-06T08:00:00Z",
    "updateTime": "2025-04-25T14:30:00Z",
    "enrollmentCode": "apcsa25",
    "alternateLink": "https://classr
... (truncated)
```

**GET Get Course (404)** — `/v1/courses/course_999` (status 404)

```
{
  "error": "Course course_999 not found"
}
```

**POST Create Course** — `/v1/courses` (status 201)

```
{
  "course": {
    "id": "course_005",
    "name": "Data Structures (Spring 2025)",
    "section": "Period 7",
    "descriptionHeading": null,
    "description": "Advanced data structures using Java",
    "room": "Room 214",
    "ownerId": null,
    "courseState": "ACTIVE",
    "creationTime": "2026-06-17T10:31:14Z",
    "updateTime": "2026-06-17T10:31:14Z",
    "enrollmentCode": "code5",
    "alternateLink": "https://classroom.google.com/c/course_005",
    "guardiansEnabled": false,
    "calendarId": "calendar_005"
  }
}
```

**PATCH Update Course** — `/v1/courses/course_001` (status 200)

```
{
  "course": {
    "id": "course_001",
    "name": "AP Computer Science A",
    "section": "Period 2",
    "descriptionHeading": "Welcome to AP CS A",
    "description": "Rigorous college-level course covering Java programming fundamentals including object-oriented design data structures and algorithms. Prepares students for the AP Computer Science A exam.",
    "room": "Room 214",
    "ownerId": "teacher_001",
    "courseState": "ACTIVE",
    "creationTime": "2025-01-06T08:00:00Z",
    "updateTime": "2025-04-25T14:30:00Z",
    "enrollmentCode": "apcsa25",
    "alternateLink": "https://classr
... (truncated)
```

**POST Archive Course** — `/v1/courses/course_004:archive` (status 200)

```
{
  "course": {
    "id": "course_004",
    "name": "Intro to Python (Fall 2024)",
    "section": "Period 3",
    "descriptionHeading": "Welcome to Python",
    "description": "Introduction to programming using Python. Covers variables loops functions and basic data structures. No prior coding experience required.",
    "room": "Room 214",
    "ownerId": "teacher_001",
    "courseState": "ARCHIVED",
    "creationTime": "2024-08-19T08:00:00Z",
    "updateTime": "2024-12-20T15:00:00Z",
    "enrollmentCode": "python24",
    "alternateLink": "https://classroom.google.com/c/course_004",
    "guardi
```

**GET List CourseWork** — `/v1/courses/course_001/courseWork` (status 200)

```
{
  "courseWork": [
    {
      "courseId": "course_001",
      "id": "cw_101",
      "title": "Variables and Data Types Lab",
      "description": "Write a Java program that demonstrates the use of int double boolean and String variables. Include type casting examples.",
      "state": "PUBLISHED",
      "maxPoints": 25.0,
      "workType": "ASSIGNMENT",
      "topicId": "topic_101",
      "creationTime": "2025-01-13T09:00:00Z",
      "updateTime": "2025-01-13T09:00:00Z",
      "alternateLink": "https://classroom.google.com/c/course_001/a/cw_101",
      "dueDate": {
        "year": 2025,
    
... (truncated)
```

**GET List CourseWork (Intertidal Lab)** — `/v1/courses/course_005/courseWork` (status 200)

```
{
  "courseWork": [
    {
      "courseId": "course_005",
      "id": "cw_501",
      "title": "Day 3 Kelp Macro Shots - Upload",
      "description": "Upload all macro lens photographs from Day 3 (May 14) kelp transects. Include RAW + JPEG. Label by transect letter.",
      "state": "PUBLISHED",
      "maxPoints": 10.0,
      "workType": "ASSIGNMENT",
      "topicId": "topic_501",
      "creationTime": "2025-05-14T18:00:00Z",
      "updateTime": "2025-05-14T18:00:00Z",
      "alternateLink": "https://classroom.google.com/c/course_005/a/cw_501",
      "dueDate": {
        "year": 2025,
       
```

**GET List CourseWork by Topic** — `/v1/courses/course_001/courseWork?topicId=topic_104` (status 200)

```
{
  "courseWork": [
    {
      "courseId": "course_001",
      "id": "cw_105",
      "title": "While Loop Patterns",
      "description": "Create programs that use while loops to generate number patterns: pyramid triangle and diamond shapes in the console.",
      "state": "PUBLISHED",
      "maxPoints": 50.0,
      "workType": "ASSIGNMENT",
      "topicId": "topic_104",
      "creationTime": "2025-02-26T09:00:00Z",
      "updateTime": "2025-02-26T09:00:00Z",
      "alternateLink": "https://classroom.google.com/c/course_001/a/cw_105",
      "dueDate": {
        "year": 2025,
        "month": 
... (truncated)
```

**GET List CourseWork ordered by dueDate** — `/v1/courses/course_001/courseWork?orderBy=dueDate desc` (status 200)

```
{
  "courseWork": [
    {
      "courseId": "course_001",
      "id": "cw_109",
      "title": "AP Practice: FRQ Set 1",
      "description": "Complete Free Response Questions 1-3 from the 2023 AP CS A exam practice set. Show all work.",
      "state": "PUBLISHED",
      "maxPoints": 100.0,
      "workType": "ASSIGNMENT",
      "topicId": "topic_107",
      "creationTime": "2025-04-21T09:00:00Z",
      "updateTime": "2025-04-21T09:00:00Z",
      "alternateLink": "https://classroom.google.com/c/course_001/a/cw_109",
      "dueDate": {
        "year": 2025,
        "month": 5,
        "day": 2
 
... (truncated)
```

**GET Get CourseWork (Valid)** — `/v1/courses/course_001/courseWork/cw_101` (status 200)

```
{
  "courseWork": {
    "courseId": "course_001",
    "id": "cw_101",
    "title": "Variables and Data Types Lab",
    "description": "Write a Java program that demonstrates the use of int double boolean and String variables. Include type casting examples.",
    "state": "PUBLISHED",
    "maxPoints": 25.0,
    "workType": "ASSIGNMENT",
    "topicId": "topic_101",
    "creationTime": "2025-01-13T09:00:00Z",
    "updateTime": "2025-01-13T09:00:00Z",
    "alternateLink": "https://classroom.google.com/c/course_001/a/cw_101",
    "dueDate": {
      "year": 2025,
      "month": 1,
      "day": 20
  
```

**GET Get CourseWork (404)** — `/v1/courses/course_001/courseWork/cw_999` (status 404)

```
{
  "error": "CourseWork cw_999 not found in course course_001"
}
```

**POST Create CourseWork (Assignment)** — `/v1/courses/course_001/courseWork` (status 201)

```
{
  "courseWork": {
    "courseId": "course_001",
    "id": "cw_400",
    "title": "Recursion Challenge",
    "description": "Implement recursive solutions for factorial, fibonacci, and tower of hanoi.",
    "state": null,
    "maxPoints": 75.0,
    "workType": "ASSIGNMENT",
    "topicId": "topic_107",
    "creationTime": "2026-06-17T10:31:14Z",
    "updateTime": "2026-06-17T10:31:14Z",
    "dueDate": {
      "year": 2025,
      "month": 5,
      "day": 9
    },
    "dueTime": {
      "hours": 23,
      "minutes": 59
    },
    "alternateLink": "https://classroom.google.com/c/course_001/a/cw_4
```

**POST Create CourseWork (Question)** — `/v1/courses/course_002/courseWork` (status 201)

```
{
  "courseWork": {
    "courseId": "course_002",
    "id": "cw_401",
    "title": "CSS Box Model Quiz",
    "description": "What is the difference between content-box and border-box?",
    "state": null,
    "maxPoints": 10.0,
    "workType": "SHORT_ANSWER_QUESTION",
    "topicId": "topic_202",
    "creationTime": "2026-06-17T10:31:14Z",
    "updateTime": "2026-06-17T10:31:14Z",
    "dueDate": null,
    "dueTime": null,
    "alternateLink": "https://classroom.google.com/c/course_002/a/cw_401"
  }
}
```

**PATCH Update CourseWork (Due Date)** — `/v1/courses/course_001/courseWork/cw_109` (status 200)

```
{
  "courseWork": {
    "courseId": "course_001",
    "id": "cw_109",
    "title": "AP Practice: FRQ Set 1",
    "description": "Complete Free Response Questions 1-3 from the 2023 AP CS A exam practice set. Show all work.",
    "state": "PUBLISHED",
    "maxPoints": 100.0,
    "workType": "ASSIGNMENT",
    "topicId": "topic_107",
    "creationTime": "2025-04-21T09:00:00Z",
    "updateTime": "2025-04-21T09:00:00Z",
    "alternateLink": "https://classroom.google.com/c/course_001/a/cw_109",
    "dueDate": {
      "year": 2025,
      "month": 5,
      "day": 2
    },
    "dueTime": {
      "hours"
```

**DELETE Delete CourseWork** — `/v1/courses/course_001/courseWork/cw_103` (status 200)

```
{
  "deleted": true
}
```

**DELETE Delete CourseWork (404)** — `/v1/courses/course_001/courseWork/cw_999` (status 404)

```
{
  "error": "CourseWork cw_999 not found in course course_001"
}
```

**GET List Topics** — `/v1/courses/course_001/topics` (status 200)

```
{
  "topic": [
    {
      "courseId": "course_001",
      "topicId": "topic_101",
      "name": "Unit 1: Primitive Types",
      "updateTime": "2025-01-10T08:00:00Z"
    },
    {
      "courseId": "course_001",
      "topicId": "topic_102",
      "name": "Unit 2: Using Objects",
      "updateTime": "2025-01-27T08:00:00Z"
    },
    {
      "courseId": "course_001",
      "topicId": "topic_103",
      "name": "Unit 3: Boolean Expressions and if Statements",
      "updateTime": "2025-02-10T08:00:00Z"
    },
    {
      "courseId": "course_001",
      "topicId": "topic_104",
      "name": "Unit 
... (truncated)
```

**GET List Topics (Intertidal Lab)** — `/v1/courses/course_005/topics` (status 200)

```
{
  "topic": [
    {
      "courseId": "course_005",
      "topicId": "topic_501",
      "name": "Protocols & Methods",
      "updateTime": "2025-01-20T09:00:00Z"
    },
    {
      "courseId": "course_005",
      "topicId": "topic_502",
      "name": "Mackworth 2024",
      "updateTime": "2025-04-10T14:00:00Z"
    }
  ]
}
```

**GET Get Topic (Valid)** — `/v1/courses/course_001/topics/topic_101` (status 200)

```
{
  "topic": {
    "courseId": "course_001",
    "topicId": "topic_101",
    "name": "Unit 1: Primitive Types",
    "updateTime": "2025-01-10T08:00:00Z"
  }
}
```

**GET Get Topic (404)** — `/v1/courses/course_001/topics/topic_999` (status 404)

```
{
  "error": "Topic topic_999 not found in course course_001"
}
```

**POST Create Topic** — `/v1/courses/course_001/topics` (status 201)

```
{
  "topic": {
    "courseId": "course_001",
    "topicId": "topic_400",
    "name": "Unit 8: 2D Arrays",
    "updateTime": "2026-06-17T10:31:14Z"
  }
}
```

**PATCH Update Topic** — `/v1/courses/course_001/topics/topic_101` (status 200)

```
{
  "topic": {
    "courseId": "course_001",
    "topicId": "topic_101",
    "name": "Unit 1: Primitive Types",
    "updateTime": "2025-01-10T08:00:00Z"
  }
}
```

**DELETE Delete Topic** — `/v1/courses/course_001/topics/topic_107` (status 200)

```
{
  "deleted": true
}
```

**GET List Submissions** — `/v1/courses/course_001/courseWork/cw_101/studentSubmissions` (status 200)

```
{
  "studentSubmissions": [
    {
      "courseId": "course_001",
      "courseWorkId": "cw_101",
      "id": "sub_001",
      "userId": "student_001",
      "state": "RETURNED",
      "late": false,
      "creationTime": "2025-01-14T10:00:00Z",
      "updateTime": "2025-01-22T14:00:00Z",
      "alternateLink": "https://classroom.google.com/c/course_001/a/cw_101/submissions/sub_001",
      "assignedGrade": 23.0,
      "draftGrade": 23.0
    },
    {
      "courseId": "course_001",
      "courseWorkId": "cw_101",
      "id": "sub_002",
      "userId": "student_002",
      "state": "RETURNED",
 
... (truncated)
```

**GET List Submissions (Intertidal Lab - Kelp Upload)** — `/v1/courses/course_005/courseWork/cw_501/studentSubmissions` (status 200)

```
{
  "studentSubmissions": [
    {
      "courseId": "course_005",
      "courseWorkId": "cw_501",
      "id": "sub_074",
      "userId": "student_086",
      "state": "TURNED_IN",
      "late": false,
      "creationTime": "2025-05-15T14:22:00Z",
      "updateTime": "2025-05-15T14:22:00Z",
      "alternateLink": "https://classroom.google.com/c/course_005/a/cw_501/submissions/sub_074",
      "assignedGrade": null,
      "draftGrade": null
    }
  ]
}
```

**GET List Submissions (TURNED_IN filter)** — `/v1/courses/course_001/courseWork/cw_108/studentSubmissions?states=TURNED_IN` (status 200)

```
{
  "studentSubmissions": [
    {
      "courseId": "course_001",
      "courseWorkId": "cw_108",
      "id": "sub_024",
      "userId": "student_001",
      "state": "TURNED_IN",
      "late": false,
      "creationTime": "2025-04-15T10:00:00Z",
      "updateTime": "2025-04-15T10:00:00Z",
      "alternateLink": "https://classroom.google.com/c/course_001/a/cw_108/submissions/sub_024",
      "assignedGrade": null,
      "draftGrade": null
    },
    {
      "courseId": "course_001",
      "courseWorkId": "cw_108",
      "id": "sub_025",
      "userId": "student_002",
      "state": "TURNED_IN",
... (truncated)
```

**GET List Submissions (RETURNED filter)** — `/v1/courses/course_001/courseWork/cw_101/studentSubmissions?states=RETURNED` (status 200)

```
{
  "studentSubmissions": [
    {
      "courseId": "course_001",
      "courseWorkId": "cw_101",
      "id": "sub_001",
      "userId": "student_001",
      "state": "RETURNED",
      "late": false,
      "creationTime": "2025-01-14T10:00:00Z",
      "updateTime": "2025-01-22T14:00:00Z",
      "alternateLink": "https://classroom.google.com/c/course_001/a/cw_101/submissions/sub_001",
      "assignedGrade": 23.0,
      "draftGrade": 23.0
    },
    {
      "courseId": "course_001",
      "courseWorkId": "cw_101",
      "id": "sub_002",
      "userId": "student_002",
      "state": "RETURNED",
 
... (truncated)
```

**GET List Submissions (Late filter)** — `/v1/courses/course_001/courseWork/cw_101/studentSubmissions?late=true` (status 200)

```
{
  "studentSubmissions": [
    {
      "courseId": "course_001",
      "courseWorkId": "cw_101",
      "id": "sub_004",
      "userId": "student_004",
      "state": "RETURNED",
      "late": true,
      "creationTime": "2025-01-21T11:00:00Z",
      "updateTime": "2025-01-23T09:00:00Z",
      "alternateLink": "https://classroom.google.com/c/course_001/a/cw_101/submissions/sub_004",
      "assignedGrade": 18.0,
      "draftGrade": 18.0
    }
  ]
}
```

**GET Get Submission (Valid)** — `/v1/courses/course_001/courseWork/cw_101/studentSubmissions/sub_001` (status 200)

```
{
  "studentSubmission": {
    "courseId": "course_001",
    "courseWorkId": "cw_101",
    "id": "sub_001",
    "userId": "student_001",
    "state": "RETURNED",
    "late": false,
    "creationTime": "2025-01-14T10:00:00Z",
    "updateTime": "2025-01-22T14:00:00Z",
    "alternateLink": "https://classroom.google.com/c/course_001/a/cw_101/submissions/sub_001",
    "assignedGrade": 23.0,
    "draftGrade": 23.0
  }
}
```

**GET Get Submission (404)** — `/v1/courses/course_001/courseWork/cw_101/studentSubmissions/sub_999` (status 404)

```
{
  "error": "Submission sub_999 not found"
}
```

**PATCH Grade Submission** — `/v1/courses/course_001/courseWork/cw_108/studentSubmissions/sub_024` (status 200)

```
{
  "studentSubmission": {
    "courseId": "course_001",
    "courseWorkId": "cw_108",
    "id": "sub_024",
    "userId": "student_001",
    "state": "TURNED_IN",
    "late": false,
    "creationTime": "2025-04-15T10:00:00Z",
    "updateTime": "2025-04-15T10:00:00Z",
    "alternateLink": "https://classroom.google.com/c/course_001/a/cw_108/submissions/sub_024",
    "assignedGrade": null,
    "draftGrade": null
  }
}
```

**POST Return Submission** — `/v1/courses/course_001/courseWork/cw_108/studentSubmissions/sub_024:return` (status 200)

```
{
  "studentSubmission": {
    "courseId": "course_001",
    "courseWorkId": "cw_108",
    "id": "sub_024",
    "userId": "student_001",
    "state": "TURNED_IN",
    "late": false,
    "creationTime": "2025-04-15T10:00:00Z",
    "updateTime": "2025-04-15T10:00:00Z",
    "alternateLink": "https://classroom.google.com/c/course_001/a/cw_108/submissions/sub_024",
    "assignedGrade": null,
    "draftGrade": null
  }
}
```

**POST Reclaim Submission** — `/v1/courses/course_001/courseWork/cw_108/studentSubmissions/sub_025:reclaim` (status 200)

```
{
  "studentSubmission": {
    "courseId": "course_001",
    "courseWorkId": "cw_108",
    "id": "sub_025",
    "userId": "student_002",
    "state": "TURNED_IN",
    "late": false,
    "creationTime": "2025-04-16T08:00:00Z",
    "updateTime": "2025-04-16T08:00:00Z",
    "alternateLink": "https://classroom.google.com/c/course_001/a/cw_108/submissions/sub_025",
    "assignedGrade": null,
    "draftGrade": null
  }
}
```

**GET List Students** — `/v1/courses/course_001/students` (status 200)

```
{
  "students": [
    {
      "courseId": "course_001",
      "userId": "student_001",
      "profile": {
        "id": "student_001",
        "name": {
          "fullName": "Ethan Nakamura"
        },
        "emailAddress": "enakamura@westlake.edu",
        "photoUrl": "https://lh3.googleusercontent.com/a/student001"
      }
    },
    {
      "courseId": "course_001",
      "userId": "student_002",
      "profile": {
        "id": "student_002",
        "name": {
          "fullName": "Sofia Patel"
        },
        "emailAddress": "spatel@westlake.edu",
        "photoUrl": "https://lh3.g
... (truncated)
```

**GET List Students (Intertidal Lab)** — `/v1/courses/course_005/students` (status 200)

```
{
  "students": [
    {
      "courseId": "course_005",
      "userId": "student_086",
      "profile": {
        "id": "student_086",
        "name": {
          "fullName": "Marcus Chen"
        },
        "emailAddress": "mchen@cascobay-marine.edu",
        "photoUrl": "https://lh3.googleusercontent.com/a/student086"
      }
    },
    {
      "courseId": "course_005",
      "userId": "student_087",
      "profile": {
        "id": "student_087",
        "name": {
          "fullName": "Priya Ramanathan"
        },
        "emailAddress": "pramanathan@cascobay-marine.edu",
        "photoUrl
... (truncated)
```

**GET List Students (Page 2)** — `/v1/courses/course_002/students?pageSize=10&pageToken=10` (status 200)

```
{
  "students": [
    {
      "courseId": "course_002",
      "userId": "student_050",
      "profile": {
        "id": "student_050",
        "name": {
          "fullName": "Rachel Green"
        },
        "emailAddress": "rgreen@westlake.edu",
        "photoUrl": "https://lh3.googleusercontent.com/a/student050"
      }
    },
    {
      "courseId": "course_002",
      "userId": "student_051",
      "profile": {
        "id": "student_051",
        "name": {
          "fullName": "David Park"
        },
        "emailAddress": "dpark@westlake.edu",
        "photoUrl": "https://lh3.googleus
... (truncated)
```

**GET Get Student (Valid)** — `/v1/courses/course_001/students/student_001` (status 200)

```
{
  "student": {
    "courseId": "course_001",
    "userId": "student_001",
    "profile": {
      "id": "student_001",
      "name": {
        "fullName": "Ethan Nakamura"
      },
      "emailAddress": "enakamura@westlake.edu",
      "photoUrl": "https://lh3.googleusercontent.com/a/student001"
    }
  }
}
```

**GET Get Student (404)** — `/v1/courses/course_001/students/student_999` (status 404)

```
{
  "error": "Student student_999 not found in course course_001"
}
```

**POST Invite Student** — `/v1/courses/course_001/students` (status 201)

```
{
  "student": {
    "courseId": "course_001",
    "userId": "student_new_92",
    "profile": {
      "id": "student_new_92",
      "name": {
        "fullName": "New Student"
      },
      "emailAddress": "newstudent@westlake.edu",
      "photoUrl": "https://lh3.googleusercontent.com/a/student_new_92"
    }
  }
}
```

**DELETE Remove Student** — `/v1/courses/course_001/students/student_048` (status 200)

```
{
  "deleted": true
}
```

**GET List Teachers** — `/v1/courses/course_001/teachers` (status 200)

```
{
  "teachers": [
    {
      "courseId": "course_001",
      "userId": "teacher_001",
      "profile": {
        "id": "teacher_001",
        "name": {
          "fullName": "Rachel Torres"
        },
        "emailAddress": "rtorres@westlake.edu",
        "photoUrl": "https://lh3.googleusercontent.com/a/teacher001"
      }
    }
  ]
}
```

**GET Get Teacher (Valid)** — `/v1/courses/course_001/teachers/teacher_001` (status 200)

```
{
  "teacher": {
    "courseId": "course_001",
    "userId": "teacher_001",
    "profile": {
      "id": "teacher_001",
      "name": {
        "fullName": "Rachel Torres"
      },
      "emailAddress": "rtorres@westlake.edu",
      "photoUrl": "https://lh3.googleusercontent.com/a/teacher001"
    }
  }
}
```

**GET Get Teacher (404)** — `/v1/courses/course_001/teachers/teacher_999` (status 404)

```
{
  "error": "Teacher teacher_999 not found in course course_001"
}
```

**GET List Teachers (course_002 - multiple)** — `/v1/courses/course_002/teachers` (status 200)

```
{
  "teachers": [
    {
      "courseId": "course_002",
      "userId": "teacher_001",
      "profile": {
        "id": "teacher_001",
        "name": {
          "fullName": "Rachel Torres"
        },
        "emailAddress": "rtorres@westlake.edu",
        "photoUrl": "https://lh3.googleusercontent.com/a/teacher001"
      }
    },
    {
      "courseId": "course_002",
      "userId": "teacher_002",
      "profile": {
        "id": "teacher_002",
        "name": {
          "fullName": "Marcus Chen"
        },
        "emailAddress": "mchen@westlake.edu",
        "photoUrl": "https://lh3.googl
```

**GET List Announcements** — `/v1/courses/course_001/announcements` (status 200)

```
{
  "announcements": [
    {
      "courseId": "course_001",
      "id": "ann_004",
      "text": "No class Thursday due to PSAT testing day. Use the time to work on your BankAccount project.",
      "state": "PUBLISHED",
      "creationTime": "2025-03-17T08:00:00Z",
      "updateTime": "2025-03-17T08:00:00Z",
      "creatorUserId": "teacher_001",
      "alternateLink": "https://classroom.google.com/c/course_001/p/ann_004"
    },
    {
      "courseId": "course_001",
      "id": "ann_003",
      "text": "AP Exam registration deadline is next Monday March 3. Sign up in the counseling office if 
... (truncated)
```

**GET Get Announcement (Valid)** — `/v1/courses/course_001/announcements/ann_001` (status 200)

```
{
  "announcement": {
    "courseId": "course_001",
    "id": "ann_001",
    "text": "Welcome to AP Computer Science A! Please review the syllabus linked in Materials and complete the intro survey by Friday.",
    "state": "PUBLISHED",
    "creationTime": "2025-01-06T09:00:00Z",
    "updateTime": "2025-01-06T09:00:00Z",
    "creatorUserId": "teacher_001",
    "alternateLink": "https://classroom.google.com/c/course_001/p/ann_001"
  }
}
```

**GET Get Announcement (404)** — `/v1/courses/course_001/announcements/ann_999` (status 404)

```
{
  "error": "Announcement ann_999 not found in course course_001"
}
```

**POST Create Announcement** — `/v1/courses/course_001/announcements` (status 201)

```
{
  "announcement": {
    "courseId": "course_001",
    "id": "ann_020",
    "text": "Extra credit opportunity: attend the CS guest speaker event this Thursday at 3pm in the auditorium.",
    "state": null,
    "creationTime": "2026-06-17T10:31:14Z",
    "updateTime": "2026-06-17T10:31:14Z",
    "creatorUserId": "teacher_001",
    "alternateLink": "https://classroom.google.com/c/course_001/p/ann_020"
  }
}
```

**PATCH Update Announcement** — `/v1/courses/course_001/announcements/ann_002` (status 200)

```
{
  "announcement": {
    "courseId": "course_001",
    "id": "ann_002",
    "text": "Reminder: Unit 2 test on Friday. Review String methods and Scanner input. Office hours Tuesday and Thursday after school.",
    "state": "PUBLISHED",
    "creationTime": "2025-02-03T08:00:00Z",
    "updateTime": "2025-02-03T08:00:00Z",
    "creatorUserId": "teacher_001",
    "alternateLink": "https://classroom.google.com/c/course_001/p/ann_002"
  }
}
```

**DELETE Delete Announcement** — `/v1/courses/course_001/announcements/ann_004` (status 200)

```
{
  "deleted": true
}
```

**GET List Materials** — `/v1/courses/course_001/courseWorkMaterials` (status 200)

```
{
  "courseWorkMaterial": [
    {
      "courseId": "course_001",
      "id": "mat_001",
      "title": "AP CS A Syllabus",
      "description": "Course syllabus with schedule grading policy and required materials.",
      "state": "PUBLISHED",
      "creationTime": "2025-01-06T08:30:00Z",
      "updateTime": "2025-01-06T08:30:00Z",
      "creatorUserId": "teacher_001",
      "topicId": "topic_101",
      "alternateLink": "https://classroom.google.com/c/course_001/m/mat_001",
      "materials": [
        {
          "link": {
            "url": "https://docs.google.com/document/d/apcs-syllabus
... (truncated)
```

**GET Get Material (Valid)** — `/v1/courses/course_001/courseWorkMaterials/mat_001` (status 200)

```
{
  "courseWorkMaterial": {
    "courseId": "course_001",
    "id": "mat_001",
    "title": "AP CS A Syllabus",
    "description": "Course syllabus with schedule grading policy and required materials.",
    "state": "PUBLISHED",
    "creationTime": "2025-01-06T08:30:00Z",
    "updateTime": "2025-01-06T08:30:00Z",
    "creatorUserId": "teacher_001",
    "topicId": "topic_101",
    "alternateLink": "https://classroom.google.com/c/course_001/m/mat_001",
    "materials": [
      {
        "link": {
          "url": "https://docs.google.com/document/d/apcs-syllabus-2025",
          "title": "AP CS 
```

**GET Get Material (404)** — `/v1/courses/course_001/courseWorkMaterials/mat_999` (status 404)

```
{
  "error": "Material mat_999 not found in course course_001"
}
```

**POST Create Material** — `/v1/courses/course_001/courseWorkMaterials` (status 201)

```
{
  "courseWorkMaterial": {
    "courseId": "course_001",
    "id": "mat_010",
    "title": "ArrayList Tutorial Video",
    "description": "Comprehensive video tutorial on Java ArrayList operations",
    "state": "PUBLISHED",
    "creationTime": "2026-06-17T10:31:14Z",
    "updateTime": "2026-06-17T10:31:14Z",
    "creatorUserId": "teacher_001",
    "topicId": "topic_107",
    "alternateLink": "https://classroom.google.com/c/course_001/m/mat_010",
    "materials": [
      {
        "link": {
          "url": "https://www.youtube.com/watch?v=example",
          "title": "ArrayList Tutorial"
   
```

**POST Create Material (Intertidal Lab - Evidence Plates)** — `/v1/courses/course_005/courseWorkMaterials` (status 201)

```
{
  "courseWorkMaterial": {
    "courseId": "course_005",
    "id": "mat_011",
    "title": "Survey Evidence Plates - May 2025",
    "description": "Photographic evidence plates from Mackworth Island intertidal survey",
    "state": "PUBLISHED",
    "creationTime": "2026-06-17T10:31:14Z",
    "updateTime": "2026-06-17T10:31:14Z",
    "creatorUserId": "teacher_001",
    "topicId": "topic_501",
    "alternateLink": "https://classroom.google.com/c/course_005/m/mat_011",
    "materials": [
      {
        "link": {
          "url": "https://drive.google.com/file/d/evidence_plates_may2025",
       
```

**GET List Materials (course_002)** — `/v1/courses/course_002/courseWorkMaterials` (status 200)

```
{
  "courseWorkMaterial": [
    {
      "courseId": "course_002",
      "id": "mat_004",
      "title": "VS Code Setup Guide",
      "description": "Step-by-step instructions for installing VS Code and recommended extensions for web development.",
      "state": "PUBLISHED",
      "creationTime": "2025-01-06T11:30:00Z",
      "updateTime": "2025-01-06T11:30:00Z",
      "creatorUserId": "teacher_001",
      "topicId": "topic_201",
      "alternateLink": "https://classroom.google.com/c/course_002/m/mat_004",
      "materials": [
        {
          "link": {
            "url": "https://docs.goog
... (truncated)
```

</details>

### google-drive-api (port 8018) — server: started

| Result | Method | Path | Status | Endpoint |
|--------|--------|------|--------|----------|
| PASS | GET | /health | 200 | health |
| PASS | GET | /drive/v3/about | 200 | about |
| PASS | GET | /drive/v3/files?q='folder-eng' in parents and trashed = false | 200 | list files in Engineering |
| PASS | GET | /drive/v3/files?q=mimeType = 'application/pdf' and trashed = false | 200 | search PDFs |
| PASS | GET | /drive/v3/files?q=starred = true | 200 | search starred |
| PASS | GET | /drive/v3/files/file-rfc-auth | 200 | get file |
| PASS | POST | /drive/v3/files | 201 | create folder |
| PASS | PATCH | /drive/v3/files/file-trace | 200 | rename file |
| PASS | PATCH | /drive/v3/files/file-budget | 200 | star file |
| PASS | POST | /drive/v3/files/file-personal/trash | 200 | trash file |
| PASS | DELETE | /drive/v3/files/file-trashed | 200 | delete file |
| PASS | GET | /drive/v3/files/file-rfc-auth/permissions | 200 | list permissions |
| PASS | POST | /drive/v3/files/file-rfc-auth/permissions | 201 | share with writer |
| PASS | DELETE | /drive/v3/files/file-budget/permissions/perm-008 | 200 | remove permission |

<details><summary>responses</summary>

**GET health** — `/health` (status 200)

```
{
  "status": "ok"
}
```

**GET about** — `/drive/v3/about` (status 200)

```
{
  "user": {
    "displayName": "Amelia Ortega",
    "emailAddress": "amelia@orbit-labs.com",
    "permissionId": "perm-amelia"
  },
  "storageQuota": {
    "limit": "16106127360",
    "usage": "4823520102",
    "usageInDrive": "4500000000",
    "usageInDriveTrash": "12000000"
  },
  "maxUploadSize": "5368709120"
}
```

**GET list files in Engineering** — `/drive/v3/files?q='folder-eng' in parents and trashed = false` (status 200)

```
{
  "kind": "drive#fileList",
  "files": [
    {
      "kind": "drive#file",
      "id": "folder-docs",
      "name": "Docs",
      "mimeType": "application/vnd.google-apps.folder",
      "parents": [
        "folder-eng"
      ],
      "size": "0",
      "createdTime": "2025-09-05T10:00:00Z",
      "modifiedTime": "2026-05-22T09:00:00Z",
      "owners": [
        {
          "emailAddress": "amelia@orbit-labs.com"
        }
      ],
      "starred": false,
      "trashed": false,
      "webViewLink": "https://drive.google.com/drive/folders/folder-docs"
    },
    {
      "kind": "drive#file",
... (truncated)
```

**GET search PDFs** — `/drive/v3/files?q=mimeType = 'application/pdf' and trashed = false` (status 200)

```
{
  "kind": "drive#fileList",
  "files": [
    {
      "kind": "drive#file",
      "id": "file-arch",
      "name": "architecture.pdf",
      "mimeType": "application/pdf",
      "parents": [
        "folder-eng"
      ],
      "size": "983040",
      "createdTime": "2026-02-20T15:00:00Z",
      "modifiedTime": "2026-05-08T08:45:00Z",
      "owners": [
        {
          "emailAddress": "amelia@orbit-labs.com"
        }
      ],
      "starred": false,
      "trashed": false,
      "webViewLink": "https://drive.google.com/file/d/file-arch/view"
    },
    {
      "kind": "drive#file",
      "
... (truncated)
```

**GET search starred** — `/drive/v3/files?q=starred = true` (status 200)

```
{
  "kind": "drive#fileList",
  "files": [
    {
      "kind": "drive#file",
      "id": "file-rfc-auth",
      "name": "RFC: Auth v2.gdoc",
      "mimeType": "application/vnd.google-apps.document",
      "parents": [
        "folder-rfcs"
      ],
      "size": "0",
      "createdTime": "2025-10-05T11:00:00Z",
      "modifiedTime": "2026-05-22T09:00:00Z",
      "owners": [
        {
          "emailAddress": "amelia@orbit-labs.com"
        }
      ],
      "starred": true,
      "trashed": false,
      "webViewLink": "https://docs.google.com/document/d/file-rfc-auth"
    },
    {
      "kind"
... (truncated)
```

**GET get file** — `/drive/v3/files/file-rfc-auth` (status 200)

```
{
  "kind": "drive#file",
  "id": "file-rfc-auth",
  "name": "RFC: Auth v2.gdoc",
  "mimeType": "application/vnd.google-apps.document",
  "parents": [
    "folder-rfcs"
  ],
  "size": "0",
  "createdTime": "2025-10-05T11:00:00Z",
  "modifiedTime": "2026-05-22T09:00:00Z",
  "owners": [
    {
      "emailAddress": "amelia@orbit-labs.com"
    }
  ],
  "starred": true,
  "trashed": false,
  "webViewLink": "https://docs.google.com/document/d/file-rfc-auth"
}
```

**POST create folder** — `/drive/v3/files` (status 201)

```
{
  "kind": "drive#file",
  "id": "file-d83717a72e",
  "name": "Postmortems",
  "mimeType": "application/vnd.google-apps.folder",
  "parents": [
    "folder-eng"
  ],
  "size": "0",
  "createdTime": "2026-06-17T10:31:14Z",
  "modifiedTime": "2026-06-17T10:31:14Z",
  "owners": [
    {
      "emailAddress": "amelia@orbit-labs.com"
    }
  ],
  "starred": false,
  "trashed": false,
  "webViewLink": null
}
```

**PATCH rename file** — `/drive/v3/files/file-trace` (status 200)

```
{
  "kind": "drive#file",
  "id": "file-trace",
  "name": "Trace export 2026-05-20.json",
  "mimeType": "application/json",
  "parents": [
    "folder-eng"
  ],
  "size": "1024000",
  "createdTime": "2026-05-20T15:00:00Z",
  "modifiedTime": "2026-05-20T15:00:00Z",
  "owners": [
    {
      "emailAddress": "helena@orbit-labs.com"
    }
  ],
  "starred": false,
  "trashed": false,
  "webViewLink": "https://drive.google.com/file/d/file-trace"
}
```

**PATCH star file** — `/drive/v3/files/file-budget` (status 200)

```
{
  "kind": "drive#file",
  "id": "file-budget",
  "name": "2026 Eng budget.xlsx",
  "mimeType": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
  "parents": [
    "folder-eng"
  ],
  "size": "184320",
  "createdTime": "2025-12-01T09:00:00Z",
  "modifiedTime": "2026-04-30T15:00:00Z",
  "owners": [
    {
      "emailAddress": "amelia@orbit-labs.com"
    }
  ],
  "starred": false,
  "trashed": false,
  "webViewLink": "https://drive.google.com/file/d/file-budget"
}
```

**POST trash file** — `/drive/v3/files/file-personal/trash` (status 200)

```
{
  "kind": "drive#file",
  "id": "file-personal",
  "name": "tax_returns_2025.pdf",
  "mimeType": "application/pdf",
  "parents": [
    "folder-root"
  ],
  "size": "512000",
  "createdTime": "2026-02-14T12:00:00Z",
  "modifiedTime": "2026-02-14T12:00:00Z",
  "owners": [
    {
      "emailAddress": "amelia@orbit-labs.com"
    }
  ],
  "starred": false,
  "trashed": false,
  "webViewLink": "https://drive.google.com/file/d/file-personal"
}
```

**DELETE delete file** — `/drive/v3/files/file-trashed` (status 200)

```
{
  "deleted": true,
  "id": "file-trashed"
}
```

**GET list permissions** — `/drive/v3/files/file-rfc-auth/permissions` (status 200)

```
{
  "kind": "drive#permissionList",
  "permissions": [
    {
      "id": "perm-004",
      "file_id": "file-rfc-auth",
      "type": "user",
      "role": "owner",
      "email": "amelia@orbit-labs.com",
      "display_name": "Amelia Ortega"
    },
    {
      "id": "perm-005",
      "file_id": "file-rfc-auth",
      "type": "user",
      "role": "commenter",
      "email": "jonas@orbit-labs.com",
      "display_name": "Jonas Pereira"
    }
  ]
}
```

**POST share with writer** — `/drive/v3/files/file-rfc-auth/permissions` (status 201)

```
{
  "id": "perm-2d3424",
  "file_id": "file-rfc-auth",
  "type": "user",
  "role": "writer",
  "email": "helena@orbit-labs.com",
  "display_name": "helena@orbit-labs.com"
}
```

**DELETE remove permission** — `/drive/v3/files/file-budget/permissions/perm-008` (status 200)

```
{
  "deleted": true,
  "id": "perm-008"
}
```

</details>

### google-maps-api (port 8033) — server: started

| Result | Method | Path | Status | Endpoint |
|--------|--------|------|--------|----------|
| PASS | GET | /health | 200 | health |
| PASS | GET | /maps/api/place/textsearch/json?query=coffee | 200 | text search |
| PASS | GET | /maps/api/place/details/json?place_id=ChIJplace0000001 | 200 | place details |
| PASS | GET | /maps/api/place/nearbysearch/json?location=37.7825,-122.4061&radius=3000&type=cafe | 200 | nearby search |
| PASS | GET | /maps/api/geocode/json?address=union square | 200 | geocode |
| PASS | GET | /maps/api/directions/json?origin=union square&destination=fishermans wharf&mode=driving | 200 | directions |
| PASS | GET | /maps/api/distancematrix/json?origins=san francisco|oakland&destinations=berkeley|palo alto&mode=driving | 200 | distance matrix |

<details><summary>responses</summary>

**GET health** — `/health` (status 200)

```
{
  "status": "ok"
}
```

**GET text search** — `/maps/api/place/textsearch/json?query=coffee` (status 200)

```
{
  "status": "OK",
  "results": [
    {
      "place_id": "ChIJplace0000001",
      "name": "Blue Bottle Coffee",
      "formatted_address": "66 Mint St San Francisco CA 94103",
      "geometry": {
        "location": {
          "lat": 37.7825,
          "lng": -122.4061
        }
      },
      "rating": 4.4,
      "user_ratings_total": 1820,
      "types": [
        "cafe",
        "food",
        "point_of_interest"
      ],
      "business_status": "OPERATIONAL",
      "price_level": 2
    },
    {
      "place_id": "ChIJplace0000008",
      "name": "Philz Coffee",
      "formatted_addre
... (truncated)
```

**GET place details** — `/maps/api/place/details/json?place_id=ChIJplace0000001` (status 200)

```
{
  "status": "OK",
  "result": {
    "place_id": "ChIJplace0000001",
    "name": "Blue Bottle Coffee",
    "formatted_address": "66 Mint St San Francisco CA 94103",
    "geometry": {
      "location": {
        "lat": 37.7825,
        "lng": -122.4061
      }
    },
    "rating": 4.4,
    "user_ratings_total": 1820,
    "types": [
      "cafe",
      "food",
      "point_of_interest"
    ],
    "business_status": "OPERATIONAL",
    "price_level": 2
  }
}
```

**GET nearby search** — `/maps/api/place/nearbysearch/json?location=37.7825,-122.4061&radius=3000&type=cafe` (status 200)

```
{
  "status": "OK",
  "results": [
    {
      "place_id": "ChIJplace0000001",
      "name": "Blue Bottle Coffee",
      "formatted_address": "66 Mint St San Francisco CA 94103",
      "geometry": {
        "location": {
          "lat": 37.7825,
          "lng": -122.4061
        }
      },
      "rating": 4.4,
      "user_ratings_total": 1820,
      "types": [
        "cafe",
        "food",
        "point_of_interest"
      ],
      "business_status": "OPERATIONAL",
      "price_level": 2,
      "distance_meters": 0
    }
  ]
}
```

**GET geocode** — `/maps/api/geocode/json?address=union square` (status 200)

```
{
  "status": "OK",
  "results": [
    {
      "formatted_address": "Union Square, San Francisco, CA 94108, USA",
      "geometry": {
        "location": {
          "lat": 37.788,
          "lng": -122.4075
        },
        "location_type": "ROOFTOP"
      },
      "place_id": "ChIJgeo0000000002"
    }
  ]
}
```

**GET directions** — `/maps/api/directions/json?origin=union square&destination=fishermans wharf&mode=driving` (status 200)

```
{
  "status": "OK",
  "routes": [
    {
      "summary": "Union Square, San Francisco, CA 94108, USA to Fisherman's Wharf, San Francisco, CA 94133, USA",
      "legs": [
        {
          "start_address": "Union Square, San Francisco, CA 94108, USA",
          "end_address": "Fisherman's Wharf, San Francisco, CA 94133, USA",
          "start_location": {
            "lat": 37.788,
            "lng": -122.4075
          },
          "end_location": {
            "lat": 37.808,
            "lng": -122.4177
          },
          "distance": {
            "text": "3.1 km",
            "value": 
```

**GET distance matrix** — `/maps/api/distancematrix/json?origins=san francisco|oakland&destinations=berkeley|palo alto&mode=driving` (status 200)

```
{
  "status": "OK",
  "origin_addresses": [
    "San Francisco, CA, USA",
    "Oakland, CA, USA"
  ],
  "destination_addresses": [
    "Berkeley, CA, USA",
    "Palo Alto, CA, USA"
  ],
  "rows": [
    {
      "elements": [
        {
          "status": "OK",
          "distance": {
            "text": "21.8 km",
            "value": 21781
          },
          "duration": {
            "text": "27 min",
            "value": 1625
          }
        },
        {
          "status": "OK",
          "distance": {
            "text": "57.6 km",
            "value": 57610
          },
          "
```

</details>

### greenhouse-api (port 8073) — server: started

| Result | Method | Path | Status | Endpoint |
|--------|--------|------|--------|----------|
| PASS | GET | /health | 200 | health |
| PASS | GET | /v1/candidates | 200 | list candidates |
| PASS | GET | /v1/candidates/cand-7001 | 200 | get candidate |
| PASS | POST | /v1/candidates | 201 | create candidate |
| PASS | GET | /v1/jobs?status=open | 200 | list jobs open |
| PASS | GET | /v1/jobs/job-3001 | 200 | get job |
| PASS | GET | /v1/applications?job_id=job-3001 | 200 | list applications |
| PASS | GET | /v1/applications/app-4001 | 200 | get application |
| PASS | POST | /v1/applications/app-4001/advance | 200 | advance application |
| PASS | POST | /v1/applications/app-4007/reject | 200 | reject application |
| PASS | GET | /v1/scorecards?application_id=app-4002 | 200 | list scorecards |

<details><summary>responses</summary>

**GET health** — `/health` (status 200)

```
{
  "status": "ok"
}
```

**GET list candidates** — `/v1/candidates` (status 200)

```
[
  {
    "id": "cand-7001",
    "first_name": "Maya",
    "last_name": "Robinson",
    "email": "maya.robinson@example.com",
    "phone": "+1-415-555-0101",
    "company": "Northwind",
    "title": "Backend Engineer",
    "source": "LinkedIn",
    "created_at": "2026-04-02T10:00:00Z"
  },
  {
    "id": "cand-7002",
    "first_name": "Liam",
    "last_name": "Chen",
    "email": "liam.chen@example.com",
    "phone": "+1-415-555-0102",
    "company": "Acme Corp",
    "title": "Frontend Engineer",
    "source": "Referral",
    "created_at": "2026-04-05T11:30:00Z"
  },
  {
    "id": "cand-7003",

... (truncated)
```

**GET get candidate** — `/v1/candidates/cand-7001` (status 200)

```
{
  "id": "cand-7001",
  "first_name": "Maya",
  "last_name": "Robinson",
  "email": "maya.robinson@example.com",
  "phone": "+1-415-555-0101",
  "company": "Northwind",
  "title": "Backend Engineer",
  "source": "LinkedIn",
  "created_at": "2026-04-02T10:00:00Z"
}
```

**POST create candidate** — `/v1/candidates` (status 201)

```
{
  "id": "cand-dc470677",
  "first_name": "Priya",
  "last_name": "Sharma",
  "email": "priya.sharma@example.com",
  "phone": "",
  "company": "Vandelay",
  "title": "Backend Engineer",
  "source": "Referral",
  "created_at": "2026-06-17T10:31:16Z"
}
```

**GET list jobs open** — `/v1/jobs?status=open` (status 200)

```
[
  {
    "id": "job-3001",
    "title": "Senior Backend Engineer",
    "status": "open",
    "department": "Engineering",
    "location": "San Francisco",
    "opened_at": "2026-03-01T00:00:00Z",
    "closed_at": null
  },
  {
    "id": "job-3002",
    "title": "Frontend Engineer",
    "status": "open",
    "department": "Engineering",
    "location": "Remote",
    "opened_at": "2026-03-10T00:00:00Z",
    "closed_at": null
  },
  {
    "id": "job-3003",
    "title": "Product Designer",
    "status": "open",
    "department": "Design",
    "location": "New York",
    "opened_at": "2026-03-15T0
... (truncated)
```

**GET get job** — `/v1/jobs/job-3001` (status 200)

```
{
  "id": "job-3001",
  "title": "Senior Backend Engineer",
  "status": "open",
  "department": "Engineering",
  "location": "San Francisco",
  "opened_at": "2026-03-01T00:00:00Z",
  "closed_at": null
}
```

**GET list applications** — `/v1/applications?job_id=job-3001` (status 200)

```
[
  {
    "id": "app-4001",
    "candidate_id": "cand-7001",
    "job_id": "job-3001",
    "status": "active",
    "current_stage": "Application Review",
    "applied_at": "2026-04-02T10:05:00Z",
    "last_activity_at": "2026-04-03T09:00:00Z"
  },
  {
    "id": "app-4002",
    "candidate_id": "cand-7005",
    "job_id": "job-3001",
    "status": "active",
    "current_stage": "Interview",
    "applied_at": "2026-04-15T08:25:00Z",
    "last_activity_at": "2026-04-20T11:00:00Z"
  }
]
```

**GET get application** — `/v1/applications/app-4001` (status 200)

```
{
  "id": "app-4001",
  "candidate_id": "cand-7001",
  "job_id": "job-3001",
  "status": "active",
  "current_stage": "Application Review",
  "applied_at": "2026-04-02T10:05:00Z",
  "last_activity_at": "2026-04-03T09:00:00Z"
}
```

**POST advance application** — `/v1/applications/app-4001/advance` (status 200)

```
{
  "id": "app-4001",
  "candidate_id": "cand-7001",
  "job_id": "job-3001",
  "status": "active",
  "current_stage": "Interview",
  "applied_at": "2026-04-02T10:05:00Z",
  "last_activity_at": "2026-06-17T10:31:16Z"
}
```

**POST reject application** — `/v1/applications/app-4007/reject` (status 200)

```
{
  "id": "app-4007",
  "candidate_id": "cand-7006",
  "job_id": "job-3005",
  "status": "rejected",
  "current_stage": "Application Review",
  "applied_at": "2026-04-18T16:05:00Z",
  "last_activity_at": "2026-06-17T10:31:16Z",
  "rejection_reason": "Position filled internally"
}
```

**GET list scorecards** — `/v1/scorecards?application_id=app-4002` (status 200)

```
[
  {
    "id": "sc-6001",
    "application_id": "app-4002",
    "candidate_id": "cand-7005",
    "interviewer": "Amelia Ortega",
    "stage": "Interview",
    "overall_recommendation": "strong_yes",
    "rating": 5,
    "submitted_at": "2026-04-20T11:30:00Z",
    "notes": "Excellent system design depth."
  },
  {
    "id": "sc-6006",
    "application_id": "app-4002",
    "candidate_id": "cand-7005",
    "interviewer": "Helena Park",
    "stage": "Interview",
    "overall_recommendation": "yes",
    "rating": 4,
    "submitted_at": "2026-04-19T13:00:00Z",
    "notes": "Strong coding; clarify s
```

</details>

### gusto-api (port 8074) — server: started

| Result | Method | Path | Status | Endpoint |
|--------|--------|------|--------|----------|
| PASS | GET | /health | 200 | health |
| PASS | GET | /v1/companies/comp-001 | 200 | get company |
| PASS | GET | /v1/companies/comp-001/employees | 200 | list company employees |
| PASS | GET | /v1/employees/gemp-202 | 200 | get employee |
| PASS | GET | /v1/companies/comp-001/payrolls | 200 | list company payrolls |
| PASS | GET | /v1/companies/comp-001/payrolls?processed=false | 200 | list unprocessed payrolls |
| PASS | GET | /v1/payrolls/pay-401 | 200 | get payroll |
| PASS | POST | /v1/companies/comp-001/payrolls | 201 | create payroll |
| PASS | PUT | /v1/payrolls/pay-404/submit | 200 | submit payroll |
| PASS | GET | /v1/companies/comp-001/contractors | 200 | list company contractors |

<details><summary>responses</summary>

**GET health** — `/health` (status 200)

```
{
  "status": "ok"
}
```

**GET get company** — `/v1/companies/comp-001` (status 200)

```
{
  "id": "comp-001",
  "name": "Orbit Labs Inc.",
  "ein": "84-1234567",
  "entity_type": "C-Corporation",
  "company_status": "Approved",
  "primary_address": "500 Market St, San Francisco, CA 94105",
  "pay_schedule": "Semimonthly",
  "currency": "USD"
}
```

**GET list company employees** — `/v1/companies/comp-001/employees` (status 200)

```
[
  {
    "id": "gemp-201",
    "company_id": "comp-001",
    "first_name": "Amelia",
    "last_name": "Ortega",
    "email": "amelia.ortega@orbit-labs.com",
    "department": "Engineering",
    "job_title": "VP of Engineering",
    "rate": 210000.0,
    "payment_unit": "Year",
    "flsa_status": "Exempt",
    "start_date": "2019-03-04",
    "terminated": false,
    "compensation": {
      "id": "gcomp-301",
      "employee_id": "gemp-201",
      "job_title": "VP of Engineering",
      "rate": 210000.0,
      "payment_unit": "Year",
      "flsa_status": "Exempt",
      "effective_date": "2024-
... (truncated)
```

**GET get employee** — `/v1/employees/gemp-202` (status 200)

```
{
  "id": "gemp-202",
  "company_id": "comp-001",
  "first_name": "Jonas",
  "last_name": "Pereira",
  "email": "jonas.pereira@orbit-labs.com",
  "department": "Engineering",
  "job_title": "Staff Software Engineer",
  "rate": 185000.0,
  "payment_unit": "Year",
  "flsa_status": "Exempt",
  "start_date": "2020-06-15",
  "terminated": false,
  "compensation": {
    "id": "gcomp-302",
    "employee_id": "gemp-202",
    "job_title": "Staff Software Engineer",
    "rate": 185000.0,
    "payment_unit": "Year",
    "flsa_status": "Exempt",
    "effective_date": "2024-01-01"
  }
}
```

**GET list company payrolls** — `/v1/companies/comp-001/payrolls` (status 200)

```
[
  {
    "id": "pay-401",
    "company_id": "comp-001",
    "pay_period_start": "2026-04-01",
    "pay_period_end": "2026-04-15",
    "check_date": "2026-04-20",
    "processed": true,
    "gross_pay": 48750.0,
    "net_pay": 35420.5,
    "employee_count": 8
  },
  {
    "id": "pay-402",
    "company_id": "comp-001",
    "pay_period_start": "2026-04-16",
    "pay_period_end": "2026-04-30",
    "check_date": "2026-05-05",
    "processed": true,
    "gross_pay": 48975.25,
    "net_pay": 35610.1,
    "employee_count": 8
  },
  {
    "id": "pay-403",
    "company_id": "comp-001",
    "pay_period_
... (truncated)
```

**GET list unprocessed payrolls** — `/v1/companies/comp-001/payrolls?processed=false` (status 200)

```
[
  {
    "id": "pay-404",
    "company_id": "comp-001",
    "pay_period_start": "2026-05-16",
    "pay_period_end": "2026-05-31",
    "check_date": "2026-06-05",
    "processed": false,
    "gross_pay": 0.0,
    "net_pay": 0.0,
    "employee_count": 8
  }
]
```

**GET get payroll** — `/v1/payrolls/pay-401` (status 200)

```
{
  "id": "pay-401",
  "company_id": "comp-001",
  "pay_period_start": "2026-04-01",
  "pay_period_end": "2026-04-15",
  "check_date": "2026-04-20",
  "processed": true,
  "gross_pay": 48750.0,
  "net_pay": 35420.5,
  "employee_count": 8
}
```

**POST create payroll** — `/v1/companies/comp-001/payrolls` (status 201)

```
{
  "id": "pay-5efc9485",
  "company_id": "comp-001",
  "pay_period_start": "2026-06-01",
  "pay_period_end": "2026-06-15",
  "check_date": "2026-06-20",
  "processed": false,
  "gross_pay": 0.0,
  "net_pay": 0.0,
  "employee_count": 8
}
```

**PUT submit payroll** — `/v1/payrolls/pay-404/submit` (status 200)

```
{
  "id": "pay-404",
  "company_id": "comp-001",
  "pay_period_start": "2026-05-16",
  "pay_period_end": "2026-05-31",
  "check_date": "2026-06-05",
  "processed": true,
  "gross_pay": 44691.78,
  "net_pay": 32446.23,
  "employee_count": 8
}
```

**GET list company contractors** — `/v1/companies/comp-001/contractors` (status 200)

```
[
  {
    "id": "gcon-501",
    "company_id": "comp-001",
    "first_name": "Sam",
    "last_name": "Whitaker",
    "business_name": "",
    "type": "Individual",
    "email": "sam.whitaker@example.com",
    "hourly_rate": 85.0,
    "wage_type": "Hourly",
    "start_date": "2025-02-01"
  },
  {
    "id": "gcon-502",
    "company_id": "comp-001",
    "first_name": "",
    "last_name": "",
    "business_name": "Brightline Design LLC",
    "type": "Business",
    "email": "billing@brightlinedesign.com",
    "hourly_rate": 0.0,
    "wage_type": "Fixed",
    "start_date": "2025-06-15"
  },
  {
    
... (truncated)
```

</details>

### hubspot-api (port 8024) — server: started

| Result | Method | Path | Status | Endpoint |
|--------|--------|------|--------|----------|
| PASS | GET | /health | 200 | health |
| PASS | GET | /crm/v3/objects/contacts?limit=5 | 200 | list contacts |
| PASS | GET | /crm/v3/objects/contacts/201 | 200 | get contact |
| PASS | POST | /crm/v3/objects/contacts | 201 | create contact |
| PASS | PATCH | /crm/v3/objects/contacts/204 | 200 | update contact |
| PASS | GET | /crm/v3/objects/companies | 200 | list companies |
| PASS | GET | /crm/v3/objects/deals?limit=10 | 200 | list deals |
| PASS | GET | /crm/v3/objects/deals/402 | 200 | get deal |
| PASS | POST | /crm/v3/objects/deals | 201 | create deal |
| PASS | PATCH | /crm/v3/objects/deals/403 | 200 | move deal to new stage |
| PASS | GET | /crm/v3/pipelines/deals | 200 | list deal pipelines |

<details><summary>responses</summary>

**GET health** — `/health` (status 200)

```
{
  "status": "ok"
}
```

**GET list contacts** — `/crm/v3/objects/contacts?limit=5` (status 200)

```
{
  "results": [
    {
      "id": "201",
      "properties": {
        "firstname": "Maya",
        "lastname": "Fernandez",
        "email": "maya.fernandez@aurorabistro.com",
        "phone": "+14155551201",
        "jobtitle": "Owner",
        "company": "Aurora Bistro LLC",
        "lifecyclestage": "customer",
        "createdate": "2025-11-02T10:00:00Z",
        "lastmodifieddate": "2026-05-20T12:00:00Z"
      },
      "createdAt": "2025-11-02T10:00:00Z",
      "updatedAt": "2026-05-20T12:00:00Z",
      "archived": false
    },
    {
      "id": "202",
      "properties": {
        "fir
... (truncated)
```

**GET get contact** — `/crm/v3/objects/contacts/201` (status 200)

```
{
  "id": "201",
  "properties": {
    "firstname": "Maya",
    "lastname": "Fernandez",
    "email": "maya.fernandez@aurorabistro.com",
    "phone": "+14155551201",
    "jobtitle": "Owner",
    "company": "Aurora Bistro LLC",
    "lifecyclestage": "customer",
    "createdate": "2025-11-02T10:00:00Z",
    "lastmodifieddate": "2026-05-20T12:00:00Z"
  },
  "createdAt": "2025-11-02T10:00:00Z",
  "updatedAt": "2026-05-20T12:00:00Z",
  "archived": false
}
```

**POST create contact** — `/crm/v3/objects/contacts` (status 201)

```
{
  "id": "40810812984",
  "properties": {
    "firstname": "Lena",
    "lastname": "Vargas",
    "email": "lena.vargas@example.com",
    "phone": "",
    "jobtitle": "COO",
    "company": "",
    "lifecyclestage": "lead",
    "createdate": "2026-06-17T10:31:17.000Z",
    "lastmodifieddate": "2026-06-17T10:31:17.000Z"
  },
  "createdAt": "2026-06-17T10:31:17.000Z",
  "updatedAt": "2026-06-17T10:31:17.000Z",
  "archived": false
}
```

**PATCH update contact** — `/crm/v3/objects/contacts/204` (status 200)

```
{
  "id": "204",
  "properties": {
    "firstname": "Tomas",
    "lastname": "Reyes",
    "email": "tomas.reyes@pelagicfreight.com",
    "phone": "+14155551204",
    "jobtitle": "Chief Financial Officer",
    "company": "Pelagic Freight Co",
    "lifecyclestage": "opportunity",
    "createdate": "2026-02-20T16:00:00Z",
    "lastmodifieddate": "2026-06-17T10:31:17.000Z"
  },
  "createdAt": "2026-02-20T16:00:00Z",
  "updatedAt": "2026-06-17T10:31:17.000Z",
  "archived": false
}
```

**GET list companies** — `/crm/v3/objects/companies` (status 200)

```
{
  "results": [
    {
      "id": "301",
      "properties": {
        "name": "Helix Robotics Inc",
        "domain": "helixrobotics.io",
        "industry": "Robotics",
        "city": "Austin",
        "state": "TX",
        "numberofemployees": "240",
        "annualrevenue": "42000000",
        "createdate": "2025-09-15T09:30:00Z"
      },
      "createdAt": "2025-09-15T09:30:00Z",
      "updatedAt": "2025-09-15T09:30:00Z",
      "archived": false
    },
    {
      "id": "302",
      "properties": {
        "name": "Lumen Design Studio",
        "domain": "lumendesign.co",
        "indu
... (truncated)
```

**GET list deals** — `/crm/v3/objects/deals?limit=10` (status 200)

```
{
  "results": [
    {
      "id": "401",
      "properties": {
        "dealname": "Helix Enterprise Renewal",
        "pipeline": "default",
        "dealstage": "closedwon",
        "amount": "358800",
        "closedate": "2026-04-30T00:00:00Z",
        "dealtype": "existingbusiness",
        "createdate": "2026-02-01T10:00:00Z",
        "lastmodifieddate": "2026-04-30T12:00:00Z"
      },
      "createdAt": "2026-02-01T10:00:00Z",
      "updatedAt": "2026-04-30T12:00:00Z",
      "archived": false
    },
    {
      "id": "402",
      "properties": {
        "dealname": "Lumen Pro Upgrade",
... (truncated)
```

**GET get deal** — `/crm/v3/objects/deals/402` (status 200)

```
{
  "id": "402",
  "properties": {
    "dealname": "Lumen Pro Upgrade",
    "pipeline": "default",
    "dealstage": "decisionmakerboughtin",
    "amount": "11760",
    "closedate": "2026-06-15T00:00:00Z",
    "dealtype": "existingbusiness",
    "createdate": "2026-03-10T14:00:00Z",
    "lastmodifieddate": "2026-05-22T11:00:00Z"
  },
  "createdAt": "2026-03-10T14:00:00Z",
  "updatedAt": "2026-05-22T11:00:00Z",
  "archived": false
}
```

**POST create deal** — `/crm/v3/objects/deals` (status 201)

```
{
  "id": "100045844660",
  "properties": {
    "dealname": "Driftwood Renewal",
    "pipeline": "default",
    "dealstage": "qualifiedtobuy",
    "amount": "20000",
    "closedate": "",
    "dealtype": "",
    "createdate": "2026-06-17T10:31:17.000Z",
    "lastmodifieddate": "2026-06-17T10:31:17.000Z"
  },
  "createdAt": "2026-06-17T10:31:17.000Z",
  "updatedAt": "2026-06-17T10:31:17.000Z",
  "archived": false
}
```

**PATCH move deal to new stage** — `/crm/v3/objects/deals/403` (status 200)

```
{
  "id": "403",
  "properties": {
    "dealname": "Pelagic Logistics Pilot",
    "pipeline": "default",
    "dealstage": "presentationscheduled",
    "amount": "45000",
    "closedate": "2026-07-01T00:00:00Z",
    "dealtype": "newbusiness",
    "createdate": "2026-02-25T16:00:00Z",
    "lastmodifieddate": "2026-06-17T10:31:17.000Z"
  },
  "createdAt": "2026-02-25T16:00:00Z",
  "updatedAt": "2026-06-17T10:31:17.000Z",
  "archived": false
}
```

**GET list deal pipelines** — `/crm/v3/pipelines/deals` (status 200)

```
{
  "results": [
    {
      "id": "default",
      "label": "Sales Pipeline",
      "displayOrder": 0,
      "stages": [
        {
          "id": "appointmentscheduled",
          "label": "Appointment Scheduled",
          "displayOrder": 0,
          "metadata": {
            "isClosed": "false",
            "probability": "0.2"
          }
        },
        {
          "id": "qualifiedtobuy",
          "label": "Qualified To Buy",
          "displayOrder": 1,
          "metadata": {
            "isClosed": "false",
            "probability": "0.4"
          }
        },
        {
       
... (truncated)
```

</details>

### instacart-api (port 8012) — server: started

| Result | Method | Path | Status | Endpoint |
|--------|--------|------|--------|----------|
| SKIP | POST | /v1/carts/{{cart_id}}/items | - | add to cart — unresolved variable {{cart_id}} |
| SKIP | POST | /v1/carts/{{cart_id}}/checkout | - | checkout — unresolved variable {{cart_id}} |
| PASS | GET | /health | 200 | health |
| PASS | GET | /v1/users/me | 200 | get me |
| PASS | GET | /v1/retailers?zip=94110 | 200 | list retailers by zip |
| PASS | GET | /v1/retailers/ret-safeway | 200 | get retailer |
| PASS | GET | /v1/products?retailer_id=ret-safeway&q=milk | 200 | search products |
| PASS | GET | /v1/products/prod-safe-002 | 200 | get product |
| PASS | POST | /v1/carts | 201 | create cart |
| PASS | GET | /v1/orders?user_id=user-emily | 200 | list orders |
| PASS | GET | /v1/orders/order-001 | 200 | get order |
| PASS | POST | /v1/orders/order-003/cancel | 200 | cancel order |

<details><summary>responses</summary>

**GET health** — `/health` (status 200)

```
{
  "status": "ok"
}
```

**GET get me** — `/v1/users/me` (status 200)

```
{
  "user_id": "user-emily",
  "name": "Emily Carson",
  "email": "emily.carson@example.com",
  "default_zip": "94110",
  "membership": "instacart_plus",
  "default_address": {
    "line1": "245 Folsom St",
    "line2": "Apt 3",
    "city": "San Francisco",
    "state": "CA",
    "zip": "94110"
  },
  "default_payment_method_id": "pm-visa-1234"
}
```

**GET list retailers by zip** — `/v1/retailers?zip=94110` (status 200)

```
[
  {
    "retailer_id": "ret-safeway",
    "name": "Safeway",
    "logo_url": "https://logos.example.com/safeway.png",
    "delivers_to_zips": [
      "94103",
      "94110",
      "94114"
    ],
    "min_basket": 10.0,
    "delivery_fee": 3.99,
    "service_fee_pct": 5.0,
    "eta_minutes": 75
  },
  {
    "retailer_id": "ret-wholefoods",
    "name": "Whole Foods Market",
    "logo_url": "https://logos.example.com/wholefoods.png",
    "delivers_to_zips": [
      "94103",
      "94110",
      "94117"
    ],
    "min_basket": 10.0,
    "delivery_fee": 4.99,
    "service_fee_pct": 5.0,
    "eta
... (truncated)
```

**GET get retailer** — `/v1/retailers/ret-safeway` (status 200)

```
{
  "retailer_id": "ret-safeway",
  "name": "Safeway",
  "logo_url": "https://logos.example.com/safeway.png",
  "delivers_to_zips": [
    "94103",
    "94110",
    "94114"
  ],
  "min_basket": 10.0,
  "delivery_fee": 3.99,
  "service_fee_pct": 5.0,
  "eta_minutes": 75
}
```

**GET search products** — `/v1/products?retailer_id=ret-safeway&q=milk` (status 200)

```
{
  "total": 1,
  "count": 1,
  "offset": 0,
  "limit": 25,
  "results": [
    {
      "product_id": "prod-safe-002",
      "retailer_id": "ret-safeway",
      "name": "Whole Milk Gallon",
      "brand": "Lucerne",
      "category": "Dairy",
      "unit_size": "1 gal",
      "price": 4.79,
      "in_stock": true,
      "sale_price": null,
      "image_url": ""
    }
  ]
}
```

**GET get product** — `/v1/products/prod-safe-002` (status 200)

```
{
  "product_id": "prod-safe-002",
  "retailer_id": "ret-safeway",
  "name": "Whole Milk Gallon",
  "brand": "Lucerne",
  "category": "Dairy",
  "unit_size": "1 gal",
  "price": 4.79,
  "in_stock": true,
  "sale_price": null,
  "image_url": ""
}
```

**POST create cart** — `/v1/carts` (status 201)

```
{
  "cart_id": "cart-dd37210f",
  "user_id": "user-emily",
  "retailer_id": "ret-safeway",
  "items": [],
  "created_at": "2026-06-17T10:31:17Z",
  "subtotal": 0.0,
  "service_fee": 0.0,
  "delivery_fee": 3.99,
  "min_basket": 10.0,
  "meets_minimum": false,
  "estimated_total": 3.99
}
```

**GET list orders** — `/v1/orders?user_id=user-emily` (status 200)

```
{
  "count": 3,
  "results": [
    {
      "order_id": "order-003",
      "user_id": "user-emily",
      "retailer_id": "ret-traderjoes",
      "status": "SHOPPING",
      "subtotal": 29.96,
      "delivery_fee": 5.99,
      "service_fee": 1.5,
      "tip": 5.0,
      "total": 42.45,
      "placed_at": "2026-05-26T08:45:00Z",
      "delivery_window_start": "2026-05-26T10:30:00Z",
      "delivery_window_end": "2026-05-26T11:30:00Z",
      "shopper_id": "shopper-derek"
    },
    {
      "order_id": "order-002",
      "user_id": "user-emily",
      "retailer_id": "ret-wholefoods",
      "status"
... (truncated)
```

**GET get order** — `/v1/orders/order-001` (status 200)

```
{
  "order_id": "order-001",
  "user_id": "user-emily",
  "retailer_id": "ret-safeway",
  "status": "DELIVERED",
  "subtotal": 42.18,
  "delivery_fee": 3.99,
  "service_fee": 2.11,
  "tip": 8.0,
  "total": 56.28,
  "placed_at": "2026-05-12T10:15:00Z",
  "delivery_window_start": "2026-05-12T12:00:00Z",
  "delivery_window_end": "2026-05-12T13:00:00Z",
  "shopper_id": "shopper-mark",
  "items": [
    {
      "order_id": "order-001",
      "product_id": "prod-safe-001",
      "quantity": 2,
      "unit_price": 2.49,
      "line_total": 4.98,
      "replacement_for": null
    },
    {
      "order_
... (truncated)
```

**POST cancel order** — `/v1/orders/order-003/cancel` (status 200)

```
{
  "order_id": "order-003",
  "user_id": "user-emily",
  "retailer_id": "ret-traderjoes",
  "status": "SHOPPING",
  "subtotal": 29.96,
  "delivery_fee": 5.99,
  "service_fee": 1.5,
  "tip": 5.0,
  "total": 42.45,
  "placed_at": "2026-05-26T08:45:00Z",
  "delivery_window_start": "2026-05-26T10:30:00Z",
  "delivery_window_end": "2026-05-26T11:30:00Z",
  "shopper_id": "shopper-derek"
}
```

</details>

### instagram-api (port 8003) — server: started

| Result | Method | Path | Status | Endpoint |
|--------|--------|------|--------|----------|
| PASS | GET | /health | 200 | GET /health |
| PASS | GET | /17841400123456789 | 200 | GET User Profile |
| PASS | GET | /17841400123456789?fields=id,username,name,followers_count,media_count | 200 | GET User Profile - with fields |
| WARN | GET | /99999999 | 404 | GET User Profile - 404 |
| PASS | GET | /17841400123456789/media | 200 | GET User Media (list) |
| PASS | GET | /17841400123456789/media?limit=5 | 200 | GET User Media - with limit |
| PASS | GET | /17841400123456789/media?media_type=VIDEO | 200 | GET User Media - filter by type VIDEO |
| PASS | GET | /17841400123456789/media?media_type=CAROUSEL_ALBUM | 200 | GET User Media - filter by type CAROUSEL_ALBUM |
| PASS | GET | /17841400123456789/media?fields=id,caption,media_type,like_count,timestamp | 200 | GET User Media - with fields |
| PASS | GET | /media/17900001002 | 200 | GET Single Media |
| WARN | GET | /media/99999999 | 404 | GET Single Media - 404 |
| PASS | DELETE | /media/17900001028 | 200 | DELETE Media |
| WARN | DELETE | /media/99999999 | 404 | DELETE Media - 404 |
| PASS | GET | /media/17900001005/children | 200 | GET Carousel Children |
| WARN | GET | /media/17900001001/children | 404 | GET Carousel Children - non-carousel 404 |
| WARN | GET | /media/99999999/children | 404 | GET Carousel Children - media 404 |
| PASS | GET | /media/17900001002/comments | 200 | GET Media Comments |
| PASS | GET | /media/17900001002/comments?limit=3 | 200 | GET Media Comments - with limit |
| WARN | GET | /media/99999999/comments | 404 | GET Media Comments - media 404 |
| PASS | GET | /comment/17800001001 | 200 | GET Single Comment |
| WARN | GET | /comment/99999999 | 404 | GET Single Comment - 404 |
| PASS | GET | /comment/17800001001/replies | 200 | GET Comment Replies |
| PASS | POST | /media/17900001002/comments | 201 | POST Create Comment Reply |
| PASS | POST | /media/17900001001/comments | 201 | POST Create Comment (top-level) |
| PASS | DELETE | /media/17900001002/comments/17800001006 | 200 | DELETE Comment |
| WARN | DELETE | /media/17900001002/comments/99999999 | 404 | DELETE Comment - 404 |
| PASS | PUT | /media/17900001002/comments/17800001003/hide | 200 | PUT Hide Comment |
| PASS | PUT | /media/17900001002/comments/17800001003/hide | 200 | PUT Unhide Comment |
| PASS | POST | /media/17900001002/comments | 201 | POST Create Comment Reply (Bakery Variant) |
| PASS | POST | /media/17900001001/comments | 201 | POST Create Comment (top-level) (Bakery Variant) |
| PASS | GET | /17841400123456789/stories | 200 | GET User Stories |
| WARN | GET | /99999999/stories | 404 | GET User Stories - 404 |
| PASS | GET | /stories/17950001001 | 200 | GET Single Story |
| WARN | GET | /stories/99999999 | 404 | GET Single Story - 404 |
| PASS | GET | /17841400123456789/insights | 200 | GET User Insights (all metrics) |
| PASS | GET | /17841400123456789/insights?metric=impressions,reach | 200 | GET User Insights - specific metrics |
| WARN | GET | /99999999/insights | 404 | GET User Insights - 404 |
| PASS | GET | /media/17900001002/insights | 200 | GET Media Insights |
| PASS | GET | /media/17900001002/insights?metric=impressions,reach,saved | 200 | GET Media Insights - specific metrics |
| WARN | GET | /media/99999999/insights | 404 | GET Media Insights - media 404 |
| PASS | GET | /ig_hashtag_search?q=coffee | 200 | GET Search Hashtags |
| PASS | GET | /ig_hashtag_search?q=latteart | 200 | GET Search Hashtags - specific |
| PASS | GET | /hashtag/17840001001 | 200 | GET Hashtag by ID |
| WARN | GET | /hashtag/99999999 | 404 | GET Hashtag - 404 |
| PASS | GET | /hashtag/17840001001/recent_media?user_id=17841400123456789 | 200 | GET Hashtag Recent Media |
| WARN | GET | /hashtag/99999999/recent_media?user_id=17841400123456789 | 404 | GET Hashtag Recent Media - 404 |
| PASS | GET | /ig_hashtag_search?q=pastry | 200 | GET Search Hashtags (Bakery Variant) |
| PASS | GET | /ig_hashtag_search?q=croissantlove | 200 | GET Search Hashtags - specific (Bakery Variant) |
| PASS | GET | /17841400123456789/tags | 200 | GET User Mentions (tags) |
| PASS | GET | /17841400123456789/tags?limit=3 | 200 | GET User Mentions - with limit |
| WARN | GET | /99999999/tags | 404 | GET User Mentions - 404 |
| PASS | POST | /17841400123456789/media | 201 | POST Create Media Container (IMAGE) |
| PASS | POST | /17841400123456789/media | 201 | POST Create Media Container (VIDEO) |
| PASS | POST | /17841400123456789/media_publish | 201 | POST Publish Media Container |
| WARN | POST | /17841400123456789/media_publish | 400 | POST Publish - container 404 |
| WARN | GET | /container/17920001001 | 404 | GET Container Status |
| WARN | GET | /container/99999999 | 404 | GET Container Status - 404 |
| PASS | POST | /17841400123456789/media | 201 | POST Create Media Container (IMAGE) (Bakery Variant) |
| PASS | POST | /17841400123456789/media | 201 | POST Create Media Container (VIDEO) (Bakery Variant) |

<details><summary>responses</summary>

**GET GET /health** — `/health` (status 200)

```
{
  "status": "ok"
}
```

**GET GET User Profile** — `/17841400123456789` (status 200)

```
{
  "id": "17841400123456789",
  "username": "brewedawakening_",
  "name": "Brewed Awakening \u2615",
  "biography": "Specialty coffee roasters & cafe \ud83c\udf3f Portland, OR\nSingle-origin beans \u2022 Latte art \u2022 Brewing tutorials\nOnline shop \u2b07\ufe0f Fresh roasts shipped weekly",
  "website": "https://brewedawakening.co",
  "followers_count": 28500,
  "follows_count": 890,
  "media_count": 33,
  "profile_picture_url": "https://instagram.mock/profiles/brewedawakening_/avatar_hd.jpg",
  "ig_id": 5214783690,
  "account_type": "BUSINESS",
  "category": "Coffee Shop"
}
```

**GET GET User Profile - with fields** — `/17841400123456789?fields=id,username,name,followers_count,media_count` (status 200)

```
{
  "id": "17841400123456789",
  "username": "brewedawakening_",
  "name": "Brewed Awakening \u2615",
  "followers_count": 28500,
  "media_count": 33
}
```

**GET GET User Profile - 404** — `/99999999` (status 404)

```
{
  "error": {
    "message": "User 99999999 not found",
    "type": "IGApiException",
    "code": 100
  }
}
```

**GET GET User Media (list)** — `/17841400123456789/media` (status 200)

```
{
  "data": [
    {
      "id": "17900001002",
      "user_id": "17841400123456789",
      "caption": "Maria's rosetta game is on another level today.\\n\\nEight months of practice and it shows.\\n\\n#latteart #coffee #baristalife",
      "media_type": "IMAGE",
      "media_url": "https://instagram.mock/media/17900001002.jpg",
      "permalink": "https://instagram.mock/p/BB2cD3eF4g/",
      "thumbnail_url": null,
      "timestamp": "2026-05-02T12:30:00",
      "like_count": 2450,
      "comments_count": 112,
      "is_comment_enabled": true
    },
    {
      "id": "17900001001",
      "user_i
... (truncated)
```

**GET GET User Media - with limit** — `/17841400123456789/media?limit=5` (status 200)

```
{
  "data": [
    {
      "id": "17900001002",
      "user_id": "17841400123456789",
      "caption": "Maria's rosetta game is on another level today.\\n\\nEight months of practice and it shows.\\n\\n#latteart #coffee #baristalife",
      "media_type": "IMAGE",
      "media_url": "https://instagram.mock/media/17900001002.jpg",
      "permalink": "https://instagram.mock/p/BB2cD3eF4g/",
      "thumbnail_url": null,
      "timestamp": "2026-05-02T12:30:00",
      "like_count": 2450,
      "comments_count": 112,
      "is_comment_enabled": true
    },
    {
      "id": "17900001001",
      "user_i
... (truncated)
```

**GET GET User Media - filter by type VIDEO** — `/17841400123456789/media?media_type=VIDEO` (status 200)

```
{
  "data": [
    {
      "id": "17900001035",
      "user_id": "17841400123456789",
      "caption": "Dance fitness energy!\\n\\nOur community fitness class brought the energy today. Group workouts hit different!\\n\\n#teamfitness #schoolsports",
      "media_type": "VIDEO",
      "media_url": "https://instagram.mock/media/17900001035.mp4",
      "permalink": "https://instagram.mock/p/JI5kL6mN7o/",
      "thumbnail_url": "https://instagram.mock/media/17900001035_thumb.jpg",
      "timestamp": "2026-02-16T18:00:00",
      "like_count": 3380,
      "comments_count": 138,
      "is_comment_enabl
... (truncated)
```

**GET GET User Media - filter by type CAROUSEL_ALBUM** — `/17841400123456789/media?media_type=CAROUSEL_ALBUM` (status 200)

```
{
  "data": [
    {
      "id": "17900001005",
      "user_id": "17841400123456789",
      "caption": "Cafe through the seasons \u2014 a four-photo carousel.\\n\\nSwipe to see autumn, winter, spring, and summer golden hour.\\n\\n#cafe #coffee #seasons",
      "media_type": "CAROUSEL_ALBUM",
      "media_url": "https://instagram.mock/media/17900001005.jpg",
      "permalink": "https://instagram.mock/p/CC3dE4fG5h/",
      "thumbnail_url": null,
      "timestamp": "2026-04-25T18:30:00",
      "like_count": 1670,
      "comments_count": 84,
      "is_comment_enabled": true
    }
  ],
  "paging": {
```

**GET GET User Media - with fields** — `/17841400123456789/media?fields=id,caption,media_type,like_count,timestamp` (status 200)

```
{
  "data": [
    {
      "id": "17900001002",
      "caption": "Maria's rosetta game is on another level today.\\n\\nEight months of practice and it shows.\\n\\n#latteart #coffee #baristalife",
      "media_type": "IMAGE",
      "timestamp": "2026-05-02T12:30:00",
      "like_count": 2450
    },
    {
      "id": "17900001001",
      "caption": "Morning pour-over ritual at the bar.\\n\\nNothing beats the bloom on a fresh Ethiopian Sidamo.\\n\\n#coffee #specialtycoffee #pourover",
      "media_type": "IMAGE",
      "timestamp": "2026-05-01T06:30:00",
      "like_count": 1280
    },
    {
     
... (truncated)
```

**GET GET Single Media** — `/media/17900001002` (status 200)

```
{
  "id": "17900001002",
  "user_id": "17841400123456789",
  "caption": "Maria's rosetta game is on another level today.\\n\\nEight months of practice and it shows.\\n\\n#latteart #coffee #baristalife",
  "media_type": "IMAGE",
  "media_url": "https://instagram.mock/media/17900001002.jpg",
  "permalink": "https://instagram.mock/p/BB2cD3eF4g/",
  "thumbnail_url": null,
  "timestamp": "2026-05-02T12:30:00",
  "like_count": 2450,
  "comments_count": 112,
  "is_comment_enabled": true
}
```

**GET GET Single Media - 404** — `/media/99999999` (status 404)

```
{
  "error": {
    "message": "Media 99999999 not found",
    "type": "IGApiException",
    "code": 100
  }
}
```

**DELETE DELETE Media** — `/media/17900001028` (status 200)

```
{
  "success": true
}
```

**DELETE DELETE Media - 404** — `/media/99999999` (status 404)

```
{
  "error": {
    "message": "Media 99999999 not found",
    "type": "IGApiException",
    "code": 100
  }
}
```

**GET GET Carousel Children** — `/media/17900001005/children` (status 200)

```
{
  "data": [
    {
      "id": "17860001001",
      "media_id": "17900001005",
      "media_type": "IMAGE",
      "media_url": "https://instagram.mock/media/17900001005_1.jpg",
      "timestamp": "2026-04-25T18:30:00"
    },
    {
      "id": "17860001002",
      "media_id": "17900001005",
      "media_type": "IMAGE",
      "media_url": "https://instagram.mock/media/17900001005_2.jpg",
      "timestamp": "2026-04-25T18:30:00"
    },
    {
      "id": "17860001003",
      "media_id": "17900001005",
      "media_type": "IMAGE",
      "media_url": "https://instagram.mock/media/17900001005_3.jpg"
... (truncated)
```

**GET GET Carousel Children - non-carousel 404** — `/media/17900001001/children` (status 404)

```
{
  "error": {
    "message": "Media 17900001001 is not a carousel album",
    "type": "IGApiException",
    "code": 100
  }
}
```

**GET GET Carousel Children - media 404** — `/media/99999999/children` (status 404)

```
{
  "error": {
    "message": "Media 99999999 not found",
    "type": "IGApiException",
    "code": 100
  }
}
```

**GET GET Media Comments** — `/media/17900001002/comments` (status 200)

```
{
  "data": [
    {
      "id": "17800001007",
      "media_id": "17900001002",
      "user_id": "17841400999005",
      "username": "maria_pours",
      "text": "Ahh thank you for posting this!! Still can\\u2019t believe I nailed it \\ud83e\\udd29",
      "timestamp": "2026-05-02T16:00:00",
      "like_count": 23,
      "hidden": false,
      "parent_id": null
    },
    {
      "id": "17800001078",
      "media_id": "17900001002",
      "user_id": "89210017",
      "username": "soulfoodstories",
      "text": "This post made me emotional honestly. Coffee brings people together.",
      "time
... (truncated)
```

**GET GET Media Comments - with limit** — `/media/17900001002/comments?limit=3` (status 200)

```
{
  "data": [
    {
      "id": "17800001007",
      "media_id": "17900001002",
      "user_id": "17841400999005",
      "username": "maria_pours",
      "text": "Ahh thank you for posting this!! Still can\\u2019t believe I nailed it \\ud83e\\udd29",
      "timestamp": "2026-05-02T16:00:00",
      "like_count": 23,
      "hidden": false,
      "parent_id": null
    },
    {
      "id": "17800001078",
      "media_id": "17900001002",
      "user_id": "89210017",
      "username": "soulfoodstories",
      "text": "This post made me emotional honestly. Coffee brings people together.",
      "time
... (truncated)
```

**GET GET Media Comments - media 404** — `/media/99999999/comments` (status 404)

```
{
  "error": {
    "message": "Media 99999999 not found",
    "type": "IGApiException",
    "code": 100
  }
}
```

**GET GET Single Comment** — `/comment/17800001001` (status 200)

```
{
  "id": "17800001001",
  "media_id": "17900001002",
  "user_id": "17841400999001",
  "username": "latteart_lover",
  "text": "OMG this is STUNNING! How long did it take to learn this? \\ud83d\\ude0d",
  "timestamp": "2026-05-02T12:45:00",
  "like_count": 12,
  "hidden": false,
  "parent_id": null
}
```

**GET GET Single Comment - 404** — `/comment/99999999` (status 404)

```
{
  "error": {
    "message": "Comment 99999999 not found",
    "type": "IGApiException",
    "code": 100
  }
}
```

**GET GET Comment Replies** — `/comment/17800001001/replies` (status 200)

```
{
  "data": [
    {
      "id": "17800001002",
      "media_id": "17900001002",
      "user_id": "17841400123456789",
      "username": "brewedawakening_",
      "text": "@latteart_lover Thank you! Maria has been practicing for about 8 months. Come to our workshop Saturday!",
      "timestamp": "2026-05-02T13:00:00",
      "like_count": 8,
      "hidden": false,
      "parent_id": "17800001001"
    }
  ],
  "paging": {}
}
```

**POST POST Create Comment Reply** — `/media/17900001002/comments` (status 201)

```
{
  "id": "17800001051",
  "media_id": "17900001002",
  "user_id": "17841400123456789",
  "username": "brewedawakening_",
  "text": "Thanks for the love! Come visit us this weekend!",
  "timestamp": "2026-06-17T10:31:18+0000",
  "like_count": 0,
  "hidden": false,
  "parent_id": "17800001003"
}
```

**POST POST Create Comment (top-level)** — `/media/17900001001/comments` (status 201)

```
{
  "id": "17800001052",
  "media_id": "17900001001",
  "user_id": "17841400123456789",
  "username": "brewedawakening_",
  "text": "Thanks for the support everyone! New batch dropping next week.",
  "timestamp": "2026-06-17T10:31:18+0000",
  "like_count": 0,
  "hidden": false,
  "parent_id": null
}
```

**DELETE DELETE Comment** — `/media/17900001002/comments/17800001006` (status 200)

```
{
  "success": true
}
```

**DELETE DELETE Comment - 404** — `/media/17900001002/comments/99999999` (status 404)

```
{
  "error": {
    "message": "Comment 99999999 not found",
    "type": "IGApiException",
    "code": 100
  }
}
```

**PUT PUT Hide Comment** — `/media/17900001002/comments/17800001003/hide` (status 200)

```
{
  "success": true
}
```

**PUT PUT Unhide Comment** — `/media/17900001002/comments/17800001003/hide` (status 200)

```
{
  "success": true
}
```

**POST POST Create Comment Reply (Bakery Variant)** — `/media/17900001002/comments` (status 201)

```
{
  "id": "17800001053",
  "media_id": "17900001002",
  "user_id": "17841400123456789",
  "username": "brewedawakening_",
  "text": "Thanks for the support! Fresh croissants coming out at sunrise tomorrow.",
  "timestamp": "2026-06-17T10:31:18+0000",
  "like_count": 0,
  "hidden": false,
  "parent_id": "17800001003"
}
```

**POST POST Create Comment (top-level) (Bakery Variant)** — `/media/17900001001/comments` (status 201)

```
{
  "id": "17800001054",
  "media_id": "17900001001",
  "user_id": "17841400123456789",
  "username": "brewedawakening_",
  "text": "Thanks everyone Mother\u2019s Day pastry boxes open again Friday morning.",
  "timestamp": "2026-06-17T10:31:18+0000",
  "like_count": 0,
  "hidden": false,
  "parent_id": null
}
```

**GET GET User Stories** — `/17841400123456789/stories` (status 200)

```
{
  "data": [
    {
      "id": "17950001011",
      "user_id": "17841400123456789",
      "media_type": "IMAGE",
      "media_url": "https://instagram.mock/stories/17950001011.jpg",
      "timestamp": "2026-06-07T18:00:00",
      "expiring_at": "2026-06-08T18:00:00",
      "caption": "Summer Conditioning Camp starts TOMORROW! Get ready for an epic summer of training! #summercamp #conditioning",
      "link": null,
      "poll_question": null,
      "poll_options": null
    },
    {
      "id": "17950001010",
      "user_id": "17841400123456789",
      "media_type": "IMAGE",
      "media_url":
... (truncated)
```

**GET GET User Stories - 404** — `/99999999/stories` (status 404)

```
{
  "error": {
    "message": "User 99999999 not found",
    "type": "IGApiException",
    "code": 100
  }
}
```

**GET GET Single Story** — `/stories/17950001001` (status 200)

```
{
  "id": "17950001001",
  "user_id": "17841400123456789",
  "media_type": "IMAGE",
  "media_url": "https://instagram.mock/stories/17950001001.jpg",
  "timestamp": "2026-05-04T08:00:00",
  "expiring_at": "2026-05-05T08:00:00",
  "caption": "Friday roast day! Costa Rica Tarrazu drops at 10am \u2615 #coffee #freshroast",
  "link": "https://brewedawakening.co/shop",
  "poll_question": null,
  "poll_options": null
}
```

**GET GET Single Story - 404** — `/stories/99999999` (status 404)

```
{
  "error": {
    "message": "Story 99999999 not found",
    "type": "IGApiException",
    "code": 100
  }
}
```

**GET GET User Insights (all metrics)** — `/17841400123456789/insights` (status 200)

```
{
  "data": [
    {
      "name": "impressions",
      "period": "day",
      "values": [
        {
          "value": 217100,
          "end_time": "2026-06-17T10:31:18+0000"
        }
      ],
      "title": "Impressions",
      "description": "Total number of times your posts have been seen"
    },
    {
      "name": "reach",
      "period": "day",
      "values": [
        {
          "value": 176000,
          "end_time": "2026-06-17T10:31:18+0000"
        }
      ],
      "title": "Reach",
      "description": "Total number of unique accounts that have seen your posts"
    },
    {
    
... (truncated)
```

**GET GET User Insights - specific metrics** — `/17841400123456789/insights?metric=impressions,reach` (status 200)

```
{
  "data": [
    {
      "name": "impressions",
      "period": "day",
      "values": [
        {
          "value": 217100,
          "end_time": "2026-06-17T10:31:18+0000"
        }
      ],
      "title": "Impressions",
      "description": "Total number of times your posts have been seen"
    },
    {
      "name": "reach",
      "period": "day",
      "values": [
        {
          "value": 176000,
          "end_time": "2026-06-17T10:31:18+0000"
        }
      ],
      "title": "Reach",
      "description": "Total number of unique accounts that have seen your posts"
    }
  ]
}
```

**GET GET User Insights - 404** — `/99999999/insights` (status 404)

```
{
  "error": {
    "message": "User 99999999 not found",
    "type": "IGApiException",
    "code": 100
  }
}
```

**GET GET Media Insights** — `/media/17900001002/insights` (status 200)

```
{
  "data": [
    {
      "name": "impressions",
      "period": "lifetime",
      "values": [
        {
          "value": 32400
        }
      ],
      "title": "Impressions"
    },
    {
      "name": "reach",
      "period": "lifetime",
      "values": [
        {
          "value": 26800
        }
      ],
      "title": "Reach"
    },
    {
      "name": "engagement",
      "period": "lifetime",
      "values": [
        {
          "value": 2666
        }
      ],
      "title": "Engagement"
    },
    {
      "name": "saved",
      "period": "lifetime",
      "values": [
        {
   
... (truncated)
```

**GET GET Media Insights - specific metrics** — `/media/17900001002/insights?metric=impressions,reach,saved` (status 200)

```
{
  "data": [
    {
      "name": "impressions",
      "period": "lifetime",
      "values": [
        {
          "value": 32400
        }
      ],
      "title": "Impressions"
    },
    {
      "name": "reach",
      "period": "lifetime",
      "values": [
        {
          "value": 26800
        }
      ],
      "title": "Reach"
    },
    {
      "name": "saved",
      "period": "lifetime",
      "values": [
        {
          "value": 210
        }
      ],
      "title": "Saves"
    }
  ]
}
```

**GET GET Media Insights - media 404** — `/media/99999999/insights` (status 404)

```
{
  "error": {
    "message": "Media 99999999 not found",
    "type": "IGApiException",
    "code": 100
  }
}
```

**GET GET Search Hashtags** — `/ig_hashtag_search?q=coffee` (status 200)

```
{
  "data": [
    {
      "id": "17840001001",
      "name": "coffee",
      "media_count": 182000000
    },
    {
      "id": "17840001003",
      "name": "specialtycoffee",
      "media_count": 8900000
    }
  ]
}
```

**GET GET Search Hashtags - specific** — `/ig_hashtag_search?q=latteart` (status 200)

```
{
  "data": [
    {
      "id": "17840001002",
      "name": "latteart",
      "media_count": 12400000
    }
  ]
}
```

**GET GET Hashtag by ID** — `/hashtag/17840001001` (status 200)

```
{
  "id": "17840001001",
  "name": "coffee",
  "media_count": 182000000
}
```

**GET GET Hashtag - 404** — `/hashtag/99999999` (status 404)

```
{
  "error": {
    "message": "Hashtag 99999999 not found",
    "type": "IGApiException",
    "code": 100
  }
}
```

**GET GET Hashtag Recent Media** — `/hashtag/17840001001/recent_media?user_id=17841400123456789` (status 200)

```
{
  "data": [
    {
      "id": "17900001002",
      "user_id": "17841400123456789",
      "caption": "Maria's rosetta game is on another level today.\\n\\nEight months of practice and it shows.\\n\\n#latteart #coffee #baristalife",
      "media_type": "IMAGE",
      "media_url": "https://instagram.mock/media/17900001002.jpg",
      "permalink": "https://instagram.mock/p/BB2cD3eF4g/",
      "thumbnail_url": null,
      "timestamp": "2026-05-02T12:30:00",
      "like_count": 2450,
      "comments_count": 113,
      "is_comment_enabled": true
    },
    {
      "id": "17900001001",
      "user_i
... (truncated)
```

**GET GET Hashtag Recent Media - 404** — `/hashtag/99999999/recent_media?user_id=17841400123456789` (status 404)

```
{
  "error": {
    "message": "Hashtag 99999999 not found",
    "type": "IGApiException",
    "code": 100
  }
}
```

**GET GET Search Hashtags (Bakery Variant)** — `/ig_hashtag_search?q=pastry` (status 200)

```
{
  "data": []
}
```

**GET GET Search Hashtags - specific (Bakery Variant)** — `/ig_hashtag_search?q=croissantlove` (status 200)

```
{
  "data": []
}
```

**GET GET User Mentions (tags)** — `/17841400123456789/tags` (status 200)

```
{
  "data": [
    {
      "id": "17870002001",
      "media_id": "17900200001",
      "mentioned_by_user_id": "17841400999140",
      "mentioned_by_username": "connect_app_official",
      "media_url": "https://instagram.mock/media/mention_beta_001.jpg",
      "timestamp": "2026-05-15T08:00:00",
      "caption": "Connect Beta feedback is officially open. Tag us with #ConnectBeta to report onboarding bugs and UI issues across iOS and Android."
    },
    {
      "id": "17870002002",
      "media_id": "17900200002",
      "mentioned_by_user_id": "17841400999141",
      "mentioned_by_username": "
... (truncated)
```

**GET GET User Mentions - with limit** — `/17841400123456789/tags?limit=3` (status 200)

```
{
  "data": [
    {
      "id": "17870002001",
      "media_id": "17900200001",
      "mentioned_by_user_id": "17841400999140",
      "mentioned_by_username": "connect_app_official",
      "media_url": "https://instagram.mock/media/mention_beta_001.jpg",
      "timestamp": "2026-05-15T08:00:00",
      "caption": "Connect Beta feedback is officially open. Tag us with #ConnectBeta to report onboarding bugs and UI issues across iOS and Android."
    },
    {
      "id": "17870002002",
      "media_id": "17900200002",
      "mentioned_by_user_id": "17841400999141",
      "mentioned_by_username": "
... (truncated)
```

**GET GET User Mentions - 404** — `/99999999/tags` (status 404)

```
{
  "error": {
    "message": "User 99999999 not found",
    "type": "IGApiException",
    "code": 100
  }
}
```

**POST POST Create Media Container (IMAGE)** — `/17841400123456789/media` (status 201)

```
{
  "id": "17920001001"
}
```

**POST POST Create Media Container (VIDEO)** — `/17841400123456789/media` (status 201)

```
{
  "id": "17920001002"
}
```

**POST POST Publish Media Container** — `/17841400123456789/media_publish` (status 201)

```
{
  "id": "17900001029"
}
```

**POST POST Publish - container 404** — `/17841400123456789/media_publish` (status 400)

```
{
  "error": {
    "message": "Container 99999999 not found",
    "type": "IGApiException",
    "code": 100
  }
}
```

**GET GET Container Status** — `/container/17920001001` (status 404)

```
{
  "error": {
    "message": "Container 17920001001 not found",
    "type": "IGApiException",
    "code": 100
  }
}
```

**GET GET Container Status - 404** — `/container/99999999` (status 404)

```
{
  "error": {
    "message": "Container 99999999 not found",
    "type": "IGApiException",
    "code": 100
  }
}
```

**POST POST Create Media Container (IMAGE) (Bakery Variant)** — `/17841400123456789/media` (status 201)

```
{
  "id": "17920001003"
}
```

**POST POST Create Media Container (VIDEO) (Bakery Variant)** — `/17841400123456789/media` (status 201)

```
{
  "id": "17920001004"
}
```

</details>

### intercom-api (port 8070) — server: started

| Result | Method | Path | Status | Endpoint |
|--------|--------|------|--------|----------|
| PASS | GET | /health | 200 | health |
| PASS | GET | /contacts?role=user | 200 | list contacts |
| PASS | GET | /contacts/contact-mara | 200 | get contact |
| PASS | POST | /contacts | 201 | create contact |
| PASS | GET | /conversations?state=open | 200 | list conversations |
| PASS | GET | /conversations/conv-1001 | 200 | get conversation |
| PASS | POST | /conversations | 201 | create conversation |
| PASS | POST | /conversations/conv-1001/reply | 200 | reply to conversation |
| PASS | POST | /conversations/conv-1003/parts | 200 | assign conversation |
| PASS | POST | /conversations/conv-1001/parts | 200 | close conversation |
| PASS | GET | /companies | 200 | list companies |
| PASS | GET | /companies/company-brightpath | 200 | get company |

<details><summary>responses</summary>

**GET health** — `/health` (status 200)

```
{
  "status": "ok"
}
```

**GET list contacts** — `/contacts?role=user` (status 200)

```
{
  "type": "list",
  "data": [
    {
      "id": "contact-mara",
      "role": "user",
      "name": "Mara Lindgren",
      "email": "mara@brightpath.io",
      "phone": "+1-202-555-0101",
      "company_id": "company-brightpath",
      "created_at": "2025-09-02T08:00:00.000Z",
      "last_seen_at": "2026-05-25T14:00:00.000Z"
    },
    {
      "id": "contact-tomas",
      "role": "user",
      "name": "Tomas Vega",
      "email": "tomas@brightpath.io",
      "phone": "+1-202-555-0102",
      "company_id": "company-brightpath",
      "created_at": "2025-09-05T09:00:00.000Z",
      "last_seen_
... (truncated)
```

**GET get contact** — `/contacts/contact-mara` (status 200)

```
{
  "type": "contact",
  "id": "contact-mara",
  "role": "user",
  "name": "Mara Lindgren",
  "email": "mara@brightpath.io",
  "phone": "+1-202-555-0101",
  "company_id": "company-brightpath",
  "created_at": "2025-09-02T08:00:00.000Z",
  "last_seen_at": "2026-05-25T14:00:00.000Z"
}
```

**POST create contact** — `/contacts` (status 201)

```
{
  "type": "contact",
  "id": "contact-32365b909b9c",
  "role": "lead",
  "name": "Priya Nair",
  "email": "priya@delta-io.com",
  "phone": null,
  "company_id": null,
  "created_at": "2026-06-17T10:31:18.000Z",
  "last_seen_at": null
}
```

**GET list conversations** — `/conversations?state=open` (status 200)

```
{
  "type": "conversation.list",
  "conversations": [
    {
      "type": "conversation",
      "id": "conv-1001",
      "state": "open",
      "open": true,
      "title": "Cannot export reports to CSV",
      "created_at": "2026-05-20T09:00:00.000Z",
      "updated_at": "2026-05-25T14:00:00.000Z",
      "contact_id": "contact-mara",
      "admin_assignee_id": "admin-jonas"
    },
    {
      "type": "conversation",
      "id": "conv-1003",
      "state": "open",
      "open": true,
      "title": "Request for SSO setup",
      "created_at": "2026-05-22T13:00:00.000Z",
      "updated_at": "20
```

**GET get conversation** — `/conversations/conv-1001` (status 200)

```
{
  "type": "conversation",
  "id": "conv-1001",
  "state": "open",
  "open": true,
  "title": "Cannot export reports to CSV",
  "created_at": "2026-05-20T09:00:00.000Z",
  "updated_at": "2026-05-25T14:00:00.000Z",
  "contact_id": "contact-mara",
  "admin_assignee_id": "admin-jonas",
  "conversation_parts": {
    "type": "conversation_part.list",
    "total_count": 3,
    "conversation_parts": [
      {
        "id": "part-1",
        "conversation_id": "conv-1001",
        "part_type": "comment",
        "author_type": "user",
        "author_id": "contact-mara",
        "body": "The CSV expo
... (truncated)
```

**POST create conversation** — `/conversations` (status 201)

```
{
  "type": "conversation",
  "id": "conv-163286c16f10",
  "state": "open",
  "open": true,
  "title": "Inviting teammates",
  "created_at": "2026-06-17T10:31:18.000Z",
  "updated_at": "2026-06-17T10:31:18.000Z",
  "contact_id": "contact-hannah",
  "admin_assignee_id": null,
  "conversation_parts": {
    "type": "conversation_part.list",
    "total_count": 1,
    "conversation_parts": [
      {
        "id": "part-79aaefdc3f3f",
        "conversation_id": "conv-163286c16f10",
        "part_type": "comment",
        "author_type": "user",
        "author_id": "contact-hannah",
        "body": "
```

**POST reply to conversation** — `/conversations/conv-1001/reply` (status 200)

```
{
  "type": "conversation",
  "id": "conv-1001",
  "state": "open",
  "open": true,
  "title": "Cannot export reports to CSV",
  "created_at": "2026-05-20T09:00:00.000Z",
  "updated_at": "2026-06-17T10:31:18.000Z",
  "contact_id": "contact-mara",
  "admin_assignee_id": "admin-jonas",
  "conversation_parts": {
    "type": "conversation_part.list",
    "total_count": 4,
    "conversation_parts": [
      {
        "id": "part-1",
        "conversation_id": "conv-1001",
        "part_type": "comment",
        "author_type": "user",
        "author_id": "contact-mara",
        "body": "The CSV expo
... (truncated)
```

**POST assign conversation** — `/conversations/conv-1003/parts` (status 200)

```
{
  "type": "conversation",
  "id": "conv-1003",
  "state": "open",
  "open": true,
  "title": "Request for SSO setup",
  "created_at": "2026-05-22T13:00:00.000Z",
  "updated_at": "2026-06-17T10:31:18.000Z",
  "contact_id": "contact-grace",
  "admin_assignee_id": "admin-helena",
  "conversation_parts": {
    "type": "conversation_part.list",
    "total_count": 2,
    "conversation_parts": [
      {
        "id": "part-7",
        "conversation_id": "conv-1003",
        "part_type": "comment",
        "author_type": "user",
        "author_id": "contact-grace",
        "body": "We need SAML SSO
... (truncated)
```

**POST close conversation** — `/conversations/conv-1001/parts` (status 200)

```
{
  "type": "conversation",
  "id": "conv-1001",
  "state": "closed",
  "open": false,
  "title": "Cannot export reports to CSV",
  "created_at": "2026-05-20T09:00:00.000Z",
  "updated_at": "2026-06-17T10:31:18.000Z",
  "contact_id": "contact-mara",
  "admin_assignee_id": "admin-jonas",
  "conversation_parts": {
    "type": "conversation_part.list",
    "total_count": 5,
    "conversation_parts": [
      {
        "id": "part-1",
        "conversation_id": "conv-1001",
        "part_type": "comment",
        "author_type": "user",
        "author_id": "contact-mara",
        "body": "The CSV e
... (truncated)
```

**GET list companies** — `/companies` (status 200)

```
{
  "type": "list",
  "data": [
    {
      "id": "company-brightpath",
      "company_id": "BP-001",
      "name": "Brightpath",
      "plan": "Pro",
      "monthly_spend": 499.0,
      "user_count": 2,
      "industry": "Software",
      "created_at": "2025-09-01T08:00:00.000Z"
    },
    {
      "id": "company-nimbus",
      "company_id": "NB-002",
      "name": "Nimbus Co",
      "plan": "Growth",
      "monthly_spend": 199.0,
      "user_count": 2,
      "industry": "Marketing",
      "created_at": "2025-09-20T08:00:00.000Z"
    },
    {
      "id": "company-helio",
      "company_id": "H
... (truncated)
```

**GET get company** — `/companies/company-brightpath` (status 200)

```
{
  "type": "company",
  "id": "company-brightpath",
  "company_id": "BP-001",
  "name": "Brightpath",
  "plan": "Pro",
  "monthly_spend": 499.0,
  "user_count": 2,
  "industry": "Software",
  "created_at": "2025-09-01T08:00:00.000Z"
}
```

</details>

### jira-api (port 8029) — server: started

| Result | Method | Path | Status | Endpoint |
|--------|--------|------|--------|----------|
| PASS | GET | /health | 200 | health |
| PASS | GET | /rest/api/3/project | 200 | list projects |
| PASS | POST | /rest/api/3/issue | 201 | create issue |
| PASS | GET | /rest/api/3/issue/ENG-102 | 200 | get issue |
| PASS | PUT | /rest/api/3/issue/ENG-102 | 204 | update issue |
| PASS | GET | /rest/api/3/issue/ENG-104/transitions | 200 | get transitions |
| PASS | POST | /rest/api/3/issue/ENG-104/transitions | 204 | transition issue |
| PASS | GET | /rest/api/3/search?jql=project %3D ENG AND status %3D "In Progress" | 200 | search jql |
| PASS | GET | /rest/agile/1.0/board | 200 | list boards |
| PASS | GET | /rest/agile/1.0/board/1/sprint?state=active | 200 | list sprints |

<details><summary>responses</summary>

**GET health** — `/health` (status 200)

```
{
  "status": "ok"
}
```

**GET list projects** — `/rest/api/3/project` (status 200)

```
[
  {
    "id": "10001",
    "key": "ENG",
    "name": "Engineering",
    "projectTypeKey": "software",
    "lead": {
      "accountId": "user-amelia",
      "displayName": "Amelia Ortega",
      "emailAddress": "amelia.ortega@orbit-labs.com",
      "active": true
    },
    "description": "Core engineering delivery project"
  },
  {
    "id": "10002",
    "key": "OPS",
    "name": "Operations",
    "projectTypeKey": "software",
    "lead": {
      "accountId": "user-helena",
      "displayName": "Helena Park",
      "emailAddress": "helena.park@orbit-labs.com",
      "active": true
    },
   
```

**POST create issue** — `/rest/api/3/issue` (status 201)

```
{
  "id": "20011",
  "key": "ENG-108",
  "self": "/rest/api/3/issue/20011"
}
```

**GET get issue** — `/rest/api/3/issue/ENG-102` (status 200)

```
{
  "id": "20002",
  "key": "ENG-102",
  "fields": {
    "summary": "Refresh-token latency spike under load",
    "description": "p95 issuance latency exceeds 600ms.",
    "issuetype": {
      "name": "Bug"
    },
    "project": {
      "key": "ENG"
    },
    "status": {
      "name": "In Progress",
      "statusCategory": {
        "id": 4,
        "key": "indeterminate",
        "name": "In Progress"
      }
    },
    "priority": {
      "name": "Highest"
    },
    "assignee": {
      "accountId": "user-jonas",
      "displayName": "Jonas Pereira",
      "emailAddress": "jonas.pereira@orb
... (truncated)
```

**PUT update issue** — `/rest/api/3/issue/ENG-102` (status 204)

_(empty)_

**GET get transitions** — `/rest/api/3/issue/ENG-104/transitions` (status 200)

```
{
  "transitions": [
    {
      "id": "11",
      "name": "To In Progress",
      "to": {
        "name": "In Progress"
      }
    }
  ]
}
```

**POST transition issue** — `/rest/api/3/issue/ENG-104/transitions` (status 204)

_(empty)_

**GET search jql** — `/rest/api/3/search?jql=project %3D ENG AND status %3D "In Progress"` (status 200)

```
{
  "expand": "schema,names",
  "startAt": 0,
  "maxResults": 50,
  "total": 3,
  "issues": [
    {
      "id": "20002",
      "key": "ENG-102",
      "fields": {
        "summary": "Refresh-token latency spike under load",
        "description": "p95 issuance latency exceeds 600ms.",
        "issuetype": {
          "name": "Bug"
        },
        "project": {
          "key": "ENG"
        },
        "status": {
          "name": "In Progress",
          "statusCategory": {
            "id": 4,
            "key": "indeterminate",
            "name": "In Progress"
          }
        },
    
... (truncated)
```

**GET list boards** — `/rest/agile/1.0/board` (status 200)

```
{
  "maxResults": 50,
  "startAt": 0,
  "total": 2,
  "values": [
    {
      "id": 1,
      "name": "ENG Scrum Board",
      "type": "scrum",
      "location": {
        "projectKey": "ENG"
      }
    },
    {
      "id": 2,
      "name": "OPS Kanban Board",
      "type": "kanban",
      "location": {
        "projectKey": "OPS"
      }
    }
  ]
}
```

**GET list sprints** — `/rest/agile/1.0/board/1/sprint?state=active` (status 200)

```
{
  "maxResults": 50,
  "startAt": 0,
  "total": 1,
  "values": [
    {
      "id": 102,
      "name": "ENG Sprint 22",
      "state": "active",
      "originBoardId": 1,
      "startDate": "2026-05-19T09:00:00Z",
      "endDate": "2026-06-02T09:00:00Z",
      "goal": "Ship dual-write shim"
    }
  ]
}
```

</details>

### klaviyo-api (port 8089) — server: started

| Result | Method | Path | Status | Endpoint |
|--------|--------|------|--------|----------|
| PASS | GET | /health | 200 | health |
| PASS | GET | /api/profiles | 200 | list profiles |
| PASS | GET | /api/profiles?email=jane.doe@example.com | 200 | filter profiles by email |
| PASS | GET | /api/profiles/01HZPROF000000000000000001 | 200 | get profile |
| PASS | POST | /api/profiles | 201 | create profile |
| PASS | GET | /api/lists | 200 | list lists |
| PASS | GET | /api/campaigns | 200 | list campaigns |
| PASS | GET | /api/campaigns?status=Sent&channel=email | 200 | list sent email campaigns |

<details><summary>responses</summary>

**GET health** — `/health` (status 200)

```
{
  "status": "ok"
}
```

**GET list profiles** — `/api/profiles` (status 200)

```
{
  "data": [
    {
      "type": "profile",
      "id": "01HZPROF000000000000000001",
      "attributes": {
        "email": "jane.doe@example.com",
        "phone_number": "+14155550101",
        "first_name": "Jane",
        "last_name": "Doe",
        "organization": "Contoso",
        "title": "Marketing Lead",
        "location": {
          "city": "San Francisco",
          "region": "California",
          "country": "United States"
        },
        "created": "2026-03-01T09:00:00Z",
        "updated": "2026-05-10T12:00:00Z"
      }
    },
    {
      "type": "profile",
      "id": 
... (truncated)
```

**GET filter profiles by email** — `/api/profiles?email=jane.doe@example.com` (status 200)

```
{
  "data": [
    {
      "type": "profile",
      "id": "01HZPROF000000000000000001",
      "attributes": {
        "email": "jane.doe@example.com",
        "phone_number": "+14155550101",
        "first_name": "Jane",
        "last_name": "Doe",
        "organization": "Contoso",
        "title": "Marketing Lead",
        "location": {
          "city": "San Francisco",
          "region": "California",
          "country": "United States"
        },
        "created": "2026-03-01T09:00:00Z",
        "updated": "2026-05-10T12:00:00Z"
      }
    }
  ]
}
```

**GET get profile** — `/api/profiles/01HZPROF000000000000000001` (status 200)

```
{
  "data": {
    "type": "profile",
    "id": "01HZPROF000000000000000001",
    "attributes": {
      "email": "jane.doe@example.com",
      "phone_number": "+14155550101",
      "first_name": "Jane",
      "last_name": "Doe",
      "organization": "Contoso",
      "title": "Marketing Lead",
      "location": {
        "city": "San Francisco",
        "region": "California",
        "country": "United States"
      },
      "created": "2026-03-01T09:00:00Z",
      "updated": "2026-05-10T12:00:00Z"
    }
  }
}
```

**POST create profile** — `/api/profiles` (status 201)

```
{
  "data": {
    "type": "profile",
    "id": "01HZPROFABLS6EAW5FAL0ZU7YB",
    "attributes": {
      "email": "new.lead@example.com",
      "phone_number": "",
      "first_name": "New",
      "last_name": "Lead",
      "organization": "Contoso",
      "title": "",
      "location": {
        "city": "Seattle",
        "region": "Washington",
        "country": "United States"
      },
      "created": "2026-06-17T10:31:20Z",
      "updated": "2026-06-17T10:31:20Z"
    }
  }
}
```

**GET list lists** — `/api/lists` (status 200)

```
{
  "data": [
    {
      "type": "list",
      "id": "01HZLIST000000000000000001",
      "attributes": {
        "name": "Newsletter Subscribers",
        "profile_count": 4820,
        "created": "2026-01-10T09:00:00Z",
        "updated": "2026-05-26T08:00:00Z"
      }
    },
    {
      "type": "list",
      "id": "01HZLIST000000000000000002",
      "attributes": {
        "name": "VIP Customers",
        "profile_count": 312,
        "created": "2026-01-15T10:00:00Z",
        "updated": "2026-05-25T12:30:00Z"
      }
    },
    {
      "type": "list",
      "id": "01HZLIST00000000000000000
... (truncated)
```

**GET list campaigns** — `/api/campaigns` (status 200)

```
{
  "data": [
    {
      "type": "campaign",
      "id": "01HZCAMP000000000000000001",
      "attributes": {
        "name": "May Newsletter",
        "status": "Sent",
        "channel": "email",
        "subject": "Whats New in May",
        "from_email": "hello@contoso.com",
        "from_label": "Contoso",
        "send_time": "2026-05-05T15:00:00Z",
        "created": "2026-05-01T09:00:00Z",
        "updated": "2026-05-05T15:05:00Z"
      },
      "relationships": {
        "list": {
          "data": {
            "type": "list",
            "id": "01HZLIST000000000000000001"
          
... (truncated)
```

**GET list sent email campaigns** — `/api/campaigns?status=Sent&channel=email` (status 200)

```
{
  "data": [
    {
      "type": "campaign",
      "id": "01HZCAMP000000000000000001",
      "attributes": {
        "name": "May Newsletter",
        "status": "Sent",
        "channel": "email",
        "subject": "Whats New in May",
        "from_email": "hello@contoso.com",
        "from_label": "Contoso",
        "send_time": "2026-05-05T15:00:00Z",
        "created": "2026-05-01T09:00:00Z",
        "updated": "2026-05-05T15:05:00Z"
      },
      "relationships": {
        "list": {
          "data": {
            "type": "list",
            "id": "01HZLIST000000000000000001"
          
... (truncated)
```

</details>

### kraken-api (port 8098) — server: started

| Result | Method | Path | Status | Endpoint |
|--------|--------|------|--------|----------|
| PASS | GET | /health | 200 | health |
| PASS | GET | /0/public/Ticker?pair=XBTUSD | 200 | ticker single |
| PASS | GET | /0/public/Ticker?pair=XBTUSD,ETHUSD | 200 | ticker multi |
| PASS | GET | /0/public/Ticker | 200 | ticker all |
| PASS | GET | /0/public/OHLC?pair=XBTUSD&interval=60 | 200 | ohlc |
| PASS | GET | /0/public/AssetPairs | 200 | asset pairs all |
| PASS | GET | /0/public/AssetPairs?pair=ETHUSD | 200 | asset pairs filter |
| PASS | GET | /0/public/Assets | 200 | assets all |
| PASS | GET | /0/public/Assets?asset=XBT,ETH | 200 | assets filter |
| PASS | POST | /0/private/Balance | 200 | balance |

<details><summary>responses</summary>

**GET health** — `/health` (status 200)

```
{
  "status": "ok"
}
```

**GET ticker single** — `/0/public/Ticker?pair=XBTUSD` (status 200)

```
{
  "error": [],
  "result": {
    "XXBTZUSD": {
      "a": [
        "67250.10",
        "1",
        "1.000"
      ],
      "b": [
        "67248.90",
        "1",
        "1.000"
      ],
      "c": [
        "67249.50",
        "0.10000000"
      ],
      "v": [
        "1842.55231000",
        "1842.55231000"
      ],
      "h": [
        "68120.00",
        "68120.00"
      ],
      "l": [
        "66310.40",
        "66310.40"
      ],
      "o": "66980.20"
    }
  }
}
```

**GET ticker multi** — `/0/public/Ticker?pair=XBTUSD,ETHUSD` (status 200)

```
{
  "error": [],
  "result": {
    "XXBTZUSD": {
      "a": [
        "67250.10",
        "1",
        "1.000"
      ],
      "b": [
        "67248.90",
        "1",
        "1.000"
      ],
      "c": [
        "67249.50",
        "0.10000000"
      ],
      "v": [
        "1842.55231000",
        "1842.55231000"
      ],
      "h": [
        "68120.00",
        "68120.00"
      ],
      "l": [
        "66310.40",
        "66310.40"
      ],
      "o": "66980.20"
    },
    "XETHZUSD": {
      "a": [
        "3712.45",
        "1",
        "1.000"
      ],
      "b": [
        "3711.80",
    
```

**GET ticker all** — `/0/public/Ticker` (status 200)

```
{
  "error": [],
  "result": {
    "XXBTZUSD": {
      "a": [
        "67250.10",
        "1",
        "1.000"
      ],
      "b": [
        "67248.90",
        "1",
        "1.000"
      ],
      "c": [
        "67249.50",
        "0.10000000"
      ],
      "v": [
        "1842.55231000",
        "1842.55231000"
      ],
      "h": [
        "68120.00",
        "68120.00"
      ],
      "l": [
        "66310.40",
        "66310.40"
      ],
      "o": "66980.20"
    },
    "XETHZUSD": {
      "a": [
        "3712.45",
        "1",
        "1.000"
      ],
      "b": [
        "3711.80",
    
... (truncated)
```

**GET ohlc** — `/0/public/OHLC?pair=XBTUSD&interval=60` (status 200)

```
{
  "error": [],
  "result": {
    "XXBTZUSD": [
      [
        1747008000,
        "66980.20",
        "67340.10",
        "66810.00",
        "67120.40",
        "67050.80",
        "142.41201000",
        3120
      ],
      [
        1747011600,
        "67120.40",
        "67510.60",
        "67010.20",
        "67388.90",
        "67280.10",
        "98.55120000",
        2410
      ],
      [
        1747015200,
        "67388.90",
        "67620.00",
        "67210.40",
        "67249.50",
        "67410.20",
        "110.20114000",
        2685
      ]
    ],
    "last": 1747015200
 
```

**GET asset pairs all** — `/0/public/AssetPairs` (status 200)

```
{
  "error": [],
  "result": {
    "XXBTZUSD": {
      "altname": "XBTUSD",
      "wsname": "XBT/USD",
      "aclass_base": "currency",
      "base": "XXBT",
      "aclass_quote": "currency",
      "quote": "ZUSD",
      "pair_decimals": 1,
      "lot_decimals": 8,
      "ordermin": "0.0001",
      "status": "online"
    },
    "XETHZUSD": {
      "altname": "ETHUSD",
      "wsname": "ETH/USD",
      "aclass_base": "currency",
      "base": "XETH",
      "aclass_quote": "currency",
      "quote": "ZUSD",
      "pair_decimals": 2,
      "lot_decimals": 8,
      "ordermin": "0.01",
      "status
... (truncated)
```

**GET asset pairs filter** — `/0/public/AssetPairs?pair=ETHUSD` (status 200)

```
{
  "error": [],
  "result": {
    "XETHZUSD": {
      "altname": "ETHUSD",
      "wsname": "ETH/USD",
      "aclass_base": "currency",
      "base": "XETH",
      "aclass_quote": "currency",
      "quote": "ZUSD",
      "pair_decimals": 2,
      "lot_decimals": 8,
      "ordermin": "0.01",
      "status": "online"
    }
  }
}
```

**GET assets all** — `/0/public/Assets` (status 200)

```
{
  "error": [],
  "result": {
    "XXBT": {
      "aclass": "currency",
      "altname": "XBT",
      "decimals": 10,
      "display_decimals": 5
    },
    "XETH": {
      "aclass": "currency",
      "altname": "ETH",
      "decimals": 10,
      "display_decimals": 5
    },
    "ZUSD": {
      "aclass": "currency",
      "altname": "USD",
      "decimals": 4,
      "display_decimals": 2
    },
    "ZEUR": {
      "aclass": "currency",
      "altname": "EUR",
      "decimals": 4,
      "display_decimals": 2
    },
    "XXRP": {
      "aclass": "currency",
      "altname": "XRP",
      "decima
... (truncated)
```

**GET assets filter** — `/0/public/Assets?asset=XBT,ETH` (status 200)

```
{
  "error": [],
  "result": {
    "XXBT": {
      "aclass": "currency",
      "altname": "XBT",
      "decimals": 10,
      "display_decimals": 5
    },
    "XETH": {
      "aclass": "currency",
      "altname": "ETH",
      "decimals": 10,
      "display_decimals": 5
    }
  }
}
```

**POST balance** — `/0/private/Balance` (status 200)

```
{
  "error": [],
  "result": {
    "ZUSD": "15420.5230",
    "XXBT": "0.84210000",
    "XETH": "4.21100000",
    "SOL": "32.50000000",
    "ADA": "1200.00000000",
    "USDT": "2500.00000000"
  }
}
```

</details>

### kubernetes-api (port 8051) — server: started

| Result | Method | Path | Status | Endpoint |
|--------|--------|------|--------|----------|
| PASS | GET | /health | 200 | health |
| PASS | GET | /api/v1/namespaces | 200 | list namespaces |
| PASS | GET | /api/v1/namespaces/prod/pods | 200 | list pods |
| PASS | GET | /api/v1/namespaces/prod/pods/api-gateway-5d8f7c | 200 | get pod |
| PASS | DELETE | /api/v1/namespaces/prod/pods/billing-worker-9af21 | 200 | delete pod |
| PASS | GET | /apis/apps/v1/namespaces/prod/deployments | 200 | list deployments |
| PASS | GET | /apis/apps/v1/namespaces/prod/deployments/api-gateway | 200 | get deployment |
| PASS | PATCH | /apis/apps/v1/namespaces/prod/deployments/api-gateway/scale | 200 | scale deployment |
| PASS | GET | /api/v1/namespaces/prod/services | 200 | list services |
| PASS | GET | /api/v1/nodes | 200 | list nodes |

<details><summary>responses</summary>

**GET health** — `/health` (status 200)

```
{
  "status": "ok"
}
```

**GET list namespaces** — `/api/v1/namespaces` (status 200)

```
{
  "kind": "NamespaceList",
  "apiVersion": "v1",
  "items": [
    {
      "kind": "Namespace",
      "apiVersion": "v1",
      "metadata": {
        "name": "default",
        "labels": {
          "kubernetes.io/metadata.name": "default"
        },
        "creationTimestamp": "2025-08-01T09:00:00Z"
      },
      "status": {
        "phase": "Active"
      }
    },
    {
      "kind": "Namespace",
      "apiVersion": "v1",
      "metadata": {
        "name": "kube-system",
        "labels": {
          "kubernetes.io/metadata.name": "kube-system"
        },
        "creationTimestamp": "20
... (truncated)
```

**GET list pods** — `/api/v1/namespaces/prod/pods` (status 200)

```
{
  "kind": "PodList",
  "apiVersion": "v1",
  "items": [
    {
      "kind": "Pod",
      "apiVersion": "v1",
      "metadata": {
        "name": "api-gateway-5d8f7c",
        "namespace": "prod",
        "creationTimestamp": "2026-05-20T12:00:00Z"
      },
      "spec": {
        "nodeName": "node-worker-1",
        "containers": [
          {
            "name": "gateway",
            "image": "orbit-labs/api-gateway:2.4.1"
          }
        ]
      },
      "status": {
        "phase": "Running",
        "podIP": "10.244.1.21",
        "containerStatuses": [
          {
            "name
... (truncated)
```

**GET get pod** — `/api/v1/namespaces/prod/pods/api-gateway-5d8f7c` (status 200)

```
{
  "kind": "Pod",
  "apiVersion": "v1",
  "metadata": {
    "name": "api-gateway-5d8f7c",
    "namespace": "prod",
    "creationTimestamp": "2026-05-20T12:00:00Z"
  },
  "spec": {
    "nodeName": "node-worker-1",
    "containers": [
      {
        "name": "gateway",
        "image": "orbit-labs/api-gateway:2.4.1"
      }
    ]
  },
  "status": {
    "phase": "Running",
    "podIP": "10.244.1.21",
    "containerStatuses": [
      {
        "name": "gateway",
        "ready": true,
        "restartCount": 0,
        "state": "Running"
      }
    ]
  }
}
```

**DELETE delete pod** — `/api/v1/namespaces/prod/pods/billing-worker-9af21` (status 200)

```
{
  "kind": "Pod",
  "apiVersion": "v1",
  "metadata": {
    "name": "billing-worker-9af21",
    "namespace": "prod",
    "creationTimestamp": "2026-05-27T08:15:00Z"
  },
  "spec": {
    "nodeName": null,
    "containers": [
      {
        "name": "worker",
        "image": "orbit-labs/billing-worker:1.8.0"
      }
    ]
  },
  "status": {
    "phase": "Terminating",
    "podIP": null,
    "containerStatuses": [
      {
        "name": "worker",
        "ready": false,
        "restartCount": 0,
        "state": "Pending"
      }
    ]
  }
}
```

**GET list deployments** — `/apis/apps/v1/namespaces/prod/deployments` (status 200)

```
{
  "kind": "DeploymentList",
  "apiVersion": "v1",
  "items": [
    {
      "kind": "Deployment",
      "apiVersion": "apps/v1",
      "metadata": {
        "name": "api-gateway",
        "namespace": "prod",
        "creationTimestamp": "2026-05-01T10:00:00Z"
      },
      "spec": {
        "replicas": 2,
        "strategy": {
          "type": "RollingUpdate"
        },
        "template": {
          "spec": {
            "containers": [
              {
                "name": "api-gateway",
                "image": "orbit-labs/api-gateway:2.4.1"
              }
            ]
          }

... (truncated)
```

**GET get deployment** — `/apis/apps/v1/namespaces/prod/deployments/api-gateway` (status 200)

```
{
  "kind": "Deployment",
  "apiVersion": "apps/v1",
  "metadata": {
    "name": "api-gateway",
    "namespace": "prod",
    "creationTimestamp": "2026-05-01T10:00:00Z"
  },
  "spec": {
    "replicas": 2,
    "strategy": {
      "type": "RollingUpdate"
    },
    "template": {
      "spec": {
        "containers": [
          {
            "name": "api-gateway",
            "image": "orbit-labs/api-gateway:2.4.1"
          }
        ]
      }
    }
  },
  "status": {
    "replicas": 2,
    "availableReplicas": 2,
    "readyReplicas": 2,
    "updatedReplicas": 2
  }
}
```

**PATCH scale deployment** — `/apis/apps/v1/namespaces/prod/deployments/api-gateway/scale` (status 200)

```
{
  "kind": "Scale",
  "apiVersion": "autoscaling/v1",
  "metadata": {
    "name": "api-gateway",
    "namespace": "prod"
  },
  "spec": {
    "replicas": 4
  },
  "status": {
    "replicas": 4
  }
}
```

**GET list services** — `/api/v1/namespaces/prod/services` (status 200)

```
{
  "kind": "ServiceList",
  "apiVersion": "v1",
  "items": [
    {
      "kind": "Service",
      "apiVersion": "v1",
      "metadata": {
        "name": "api-gateway",
        "namespace": "prod",
        "creationTimestamp": "2026-05-01T10:05:00Z"
      },
      "spec": {
        "type": "LoadBalancer",
        "clusterIP": "10.96.12.40",
        "selector": {
          "app": "api-gateway"
        },
        "ports": [
          {
            "port": 80,
            "targetPort": 8080,
            "protocol": "TCP"
          }
        ]
      },
      "status": {
        "loadBalancer": {

... (truncated)
```

**GET list nodes** — `/api/v1/nodes` (status 200)

```
{
  "kind": "NodeList",
  "apiVersion": "v1",
  "items": [
    {
      "kind": "Node",
      "apiVersion": "v1",
      "metadata": {
        "name": "node-control-1",
        "labels": {
          "node-role.kubernetes.io/control-plane": ""
        },
        "creationTimestamp": "2025-08-01T08:55:00Z"
      },
      "status": {
        "capacity": {
          "cpu": "4",
          "memory": "16Gi"
        },
        "nodeInfo": {
          "kubeletVersion": "v1.29.4",
          "osImage": "Ubuntu 22.04.4 LTS"
        },
        "addresses": [
          {
            "type": "InternalIP",
    
... (truncated)
```

</details>

### linear-api (port 8004) — server: started

| Result | Method | Path | Status | Endpoint |
|--------|--------|------|--------|----------|
| PASS | GET | /health | 200 | GET /health |
| PASS | GET | /v1/teams | 200 | GET List Teams |
| PASS | GET | /v1/teams/team-backend | 200 | GET Team by ID |
| WARN | GET | /v1/teams/nonexistent-team-99999 | 404 | GET Team - 404 |
| PASS | GET | /v1/teams/team-backend/members | 200 | GET Team Members |
| PASS | GET | /v1/teams/team-frontend/issues | 200 | GET Team Issues |
| PASS | GET | /v1/teams/team-backend/projects | 200 | GET Team Projects |
| PASS | GET | /v1/teams/team-backend/cycles | 200 | GET Team Cycles |
| PASS | GET | /v1/teams/team-backend/workflow-states | 200 | GET Team Workflow States |
| PASS | GET | /v1/teams/team-frontend/labels | 200 | GET Team Labels |
| PASS | GET | /v1/users | 200 | GET List Users |
| PASS | GET | /v1/users/user-01 | 200 | GET User by ID |
| WARN | GET | /v1/users/nonexistent-user-99999 | 404 | GET User - 404 |
| PASS | GET | /v1/users/user-01/issues | 200 | GET User Assigned Issues |
| PASS | GET | /v1/workflow-states | 200 | GET List Workflow States |
| PASS | GET | /v1/workflow-states?teamId=team-frontend | 200 | GET Workflow States by Team |
| PASS | GET | /v1/workflow-states/state-bkd-inprogress | 200 | GET Workflow State by ID |
| WARN | GET | /v1/workflow-states/nonexistent-state-99999 | 404 | GET Workflow State - 404 |
| PASS | GET | /v1/labels | 200 | GET List Labels |
| PASS | GET | /v1/labels?teamId=team-platform | 200 | GET Labels by Team |
| PASS | GET | /v1/labels/label-bug | 200 | GET Label by ID |
| WARN | GET | /v1/labels/nonexistent-label-99999 | 404 | GET Label - 404 |
| PASS | POST | /v1/labels | 201 | POST Create Label |
| PASS | GET | /v1/projects | 200 | GET List Projects |
| PASS | GET | /v1/projects/proj-api-v2 | 200 | GET Project by ID |
| WARN | GET | /v1/projects/nonexistent-project-99999 | 404 | GET Project - 404 |
| PASS | GET | /v1/projects/proj-api-v2/issues | 200 | GET Project Issues |
| PASS | POST | /v1/projects | 201 | POST Create Project |
| PASS | PUT | /v1/projects/proj-dashboard | 200 | PUT Update Project |
| PASS | GET | /v1/cycles | 200 | GET List Cycles |
| PASS | GET | /v1/cycles?teamId=team-backend | 200 | GET Cycles by Team |
| PASS | GET | /v1/cycles?status=current | 200 | GET Current Cycles |
| PASS | GET | /v1/cycles?status=past | 200 | GET Past Cycles |
| PASS | GET | /v1/cycles/cycle-bkd-2 | 200 | GET Cycle by ID |
| WARN | GET | /v1/cycles/nonexistent-cycle-99999 | 404 | GET Cycle - 404 |
| PASS | GET | /v1/cycles/cycle-bkd-2/issues | 200 | GET Cycle Issues |
| PASS | POST | /v1/cycles | 201 | POST Create Cycle |
| PASS | GET | /v1/issues | 200 | GET List Issues (unfiltered) |
| PASS | GET | /v1/issues?stateId=state-bkd-inprogress | 200 | GET Issues by State |
| PASS | GET | /v1/issues?assigneeId=user-01 | 200 | GET Issues by Assignee |
| PASS | GET | /v1/issues?projectId=proj-api-v2 | 200 | GET Issues by Project |
| PASS | GET | /v1/issues?priority=1 | 200 | GET Issues by Priority |
| PASS | GET | /v1/issues?labelId=label-bug | 200 | GET Issues by Label |
| PASS | GET | /v1/issues?teamId=team-platform | 200 | GET Issues by Team |
| PASS | GET | /v1/issues?stateId=state-bkd-inprogress&assigneeId=user-01 | 200 | GET Issues - Combined Filters (State + Assignee) |
| PASS | GET | /v1/issues?projectId=proj-perf&priority=2 | 200 | GET Issues - Combined Filters (Project + Priority) |
| PASS | GET | /v1/issues?limit=5&offset=0 | 200 | GET Issues with Pagination |
| PASS | GET | /v1/issues/issue-01 | 200 | GET Issue by ID |
| WARN | GET | /v1/issues/nonexistent-issue-99999 | 404 | GET Issue - 404 |
| PASS | GET | /v1/issues/search?q=rate+limiting | 200 | GET Search Issues - keyword |
| PASS | GET | /v1/issues/search?q=MER-5 | 200 | GET Search Issues - identifier |
| PASS | POST | /v1/issues | 201 | POST Create Issue |
| PASS | PUT | /v1/issues/issue-09 | 200 | PUT Update Issue - State Change |
| PASS | PUT | /v1/issues/issue-15 | 200 | PUT Update Issue - Priority and Estimate |
| PASS | PUT | /v1/issues/issue-07 | 200 | PUT Update Issue - Labels |
| PASS | DELETE | /v1/issues/issue-26 | 200 | DELETE Issue |
| WARN | DELETE | /v1/issues/nonexistent-issue-99999 | 404 | DELETE Issue - 404 |
| PASS | GET | /v1/issues/issue-01/comments | 200 | GET List Comments for Issue |
| WARN | GET | /v1/issues/nonexistent-issue-99999/comments | 404 | GET Comments - Issue 404 |
| PASS | GET | /v1/comments/comment-01 | 200 | GET Comment by ID |
| WARN | GET | /v1/comments/nonexistent-comment-99999 | 404 | GET Comment - 404 |
| PASS | POST | /v1/comments | 201 | POST Create Comment |
| WARN | POST | /v1/comments | 400 | POST Create Comment - Issue 404 |
| PASS | PUT | /v1/comments/comment-01 | 200 | PUT Update Comment |
| PASS | DELETE | /v1/comments/comment-25 | 200 | DELETE Comment |
| WARN | DELETE | /v1/comments/nonexistent-comment-99999 | 404 | DELETE Comment - 404 |

<details><summary>responses</summary>

**GET GET /health** — `/health` (status 200)

```
{
  "status": "ok"
}
```

**GET GET List Teams** — `/v1/teams` (status 200)

```
{
  "type": "teams",
  "count": 4,
  "total": 4,
  "offset": 0,
  "limit": 50,
  "results": [
    {
      "id": "team-ux",
      "name": "Patient Portal UX",
      "key": "PORT",
      "description": "UX team building and reviewing the Cumberland patient portal redesign",
      "color": "#5E6AD2",
      "createdAt": "2026-01-15T09:00:00",
      "updatedAt": "2026-05-01T10:00:00"
    },
    {
      "id": "team-backend",
      "name": "Backend Engineering",
      "key": "BKD",
      "description": "Backend services team owning API gateway, auth, and core data services",
      "color": "#26B5CE",
... (truncated)
```

**GET GET Team by ID** — `/v1/teams/team-backend` (status 200)

```
{
  "type": "team",
  "team": {
    "id": "team-backend",
    "name": "Backend Engineering",
    "key": "BKD",
    "description": "Backend services team owning API gateway, auth, and core data services",
    "color": "#26B5CE",
    "createdAt": "2026-01-15T09:00:00",
    "updatedAt": "2026-05-10T10:00:00"
  }
}
```

**GET GET Team - 404** — `/v1/teams/nonexistent-team-99999` (status 404)

```
{
  "error": "Team nonexistent-team-99999 not found"
}
```

**GET GET Team Members** — `/v1/teams/team-backend/members` (status 200)

```
{
  "type": "users",
  "count": 3,
  "results": [
    {
      "id": "user-01",
      "name": "alex.rivera",
      "displayName": "Alex Rivera",
      "email": "alex.rivera@meridianlabs.io",
      "avatarUrl": "https://avatars.example.com/alex.png",
      "active": true,
      "admin": false,
      "teamId": "team-backend",
      "createdAt": "2026-01-20T09:00:00",
      "updatedAt": "2026-05-10T10:00:00"
    },
    {
      "id": "user-02",
      "name": "jordan.kim",
      "displayName": "Jordan Kim",
      "email": "jordan.kim@meridianlabs.io",
      "avatarUrl": "https://avatars.example.com/
... (truncated)
```

**GET GET Team Issues** — `/v1/teams/team-frontend/issues` (status 200)

```
{
  "type": "issues",
  "count": 0,
  "total": 0,
  "offset": 0,
  "limit": 50,
  "results": []
}
```

**GET GET Team Projects** — `/v1/teams/team-backend/projects` (status 200)

```
{
  "type": "projects",
  "count": 2,
  "results": [
    {
      "id": "proj-api-v2",
      "name": "API v2 Migration",
      "description": "Migrate public REST endpoints from v1 to v2 with consistent error envelopes, rate-limit headers, and uniform pagination",
      "state": "started",
      "leadId": "user-01",
      "teamIds": [
        "team-backend"
      ],
      "startDate": "2026-02-01",
      "targetDate": "2026-06-30",
      "createdAt": "2026-01-20T09:00:00",
      "updatedAt": "2026-05-10T10:00:00"
    },
    {
      "id": "proj-dashboard",
      "name": "Customer Dashboard",
   
... (truncated)
```

**GET GET Team Cycles** — `/v1/teams/team-backend/cycles` (status 200)

```
{
  "type": "cycles",
  "count": 2,
  "results": [
    {
      "id": "cycle-bkd-1",
      "name": "Backend Sprint 1",
      "number": 1,
      "teamId": "team-backend",
      "startsAt": "2026-04-06",
      "endsAt": "2026-04-19",
      "completedAt": "2026-04-19T17:00:00",
      "createdAt": "2026-03-29T09:00:00",
      "updatedAt": "2026-04-19T17:00:00"
    },
    {
      "id": "cycle-bkd-2",
      "name": "Backend Sprint 2",
      "number": 2,
      "teamId": "team-backend",
      "startsAt": "2026-04-20",
      "endsAt": "2026-05-03",
      "completedAt": null,
      "createdAt": "2026-04-
```

**GET GET Team Workflow States** — `/v1/teams/team-backend/workflow-states` (status 200)

```
{
  "type": "workflow_states",
  "count": 6,
  "results": [
    {
      "id": "state-bkd-backlog",
      "name": "Backlog",
      "type": "backlog",
      "color": "#bec2c8",
      "position": 0,
      "teamId": "team-backend",
      "description": "Issues that are not yet prioritized"
    },
    {
      "id": "state-bkd-todo",
      "name": "Todo",
      "type": "unstarted",
      "color": "#e2e2e2",
      "position": 1,
      "teamId": "team-backend",
      "description": "Issues ready to be picked up"
    },
    {
      "id": "state-bkd-inprogress",
      "name": "In Progress",
      "type"
... (truncated)
```

**GET GET Team Labels** — `/v1/teams/team-frontend/labels` (status 200)

```
{
  "type": "labels",
  "count": 9,
  "results": [
    {
      "id": "label-bug",
      "name": "Bug",
      "color": "#eb5757",
      "description": "Something isn't working correctly",
      "teamId": null,
      "createdAt": "2026-01-15T09:00:00",
      "updatedAt": "2026-01-15T09:00:00"
    },
    {
      "id": "label-critical",
      "name": "Critical",
      "color": "#eb5757",
      "description": "Critical severity",
      "teamId": null,
      "createdAt": "2026-01-15T09:00:00",
      "updatedAt": "2026-01-15T09:00:00"
    },
    {
      "id": "label-high",
      "name": "High",
     
... (truncated)
```

**GET GET List Users** — `/v1/users` (status 200)

```
{
  "type": "users",
  "count": 8,
  "total": 8,
  "offset": 0,
  "limit": 50,
  "results": [
    {
      "id": "user-david",
      "name": "david.nelson",
      "displayName": "David Nelson",
      "email": "david.nelson@cumberlandregional.org",
      "avatarUrl": "https://avatars.example.com/david.png",
      "active": true,
      "admin": false,
      "teamId": "team-ux",
      "createdAt": "2026-01-20T09:00:00",
      "updatedAt": "2026-05-10T10:00:00"
    },
    {
      "id": "user-patty",
      "name": "patty.oglesby",
      "displayName": "Patty Oglesby",
      "email": "patty.oglesby@c
... (truncated)
```

**GET GET User by ID** — `/v1/users/user-01` (status 200)

```
{
  "type": "user",
  "user": {
    "id": "user-01",
    "name": "alex.rivera",
    "displayName": "Alex Rivera",
    "email": "alex.rivera@meridianlabs.io",
    "avatarUrl": "https://avatars.example.com/alex.png",
    "active": true,
    "admin": false,
    "teamId": "team-backend",
    "createdAt": "2026-01-20T09:00:00",
    "updatedAt": "2026-05-10T10:00:00"
  }
}
```

**GET GET User - 404** — `/v1/users/nonexistent-user-99999` (status 404)

```
{
  "error": "User nonexistent-user-99999 not found"
}
```

**GET GET User Assigned Issues** — `/v1/users/user-01/issues` (status 200)

```
{
  "type": "issues",
  "count": 2,
  "total": 2,
  "offset": 0,
  "limit": 50,
  "results": [
    {
      "id": "issue-01",
      "identifier": "BKD-1",
      "number": 1,
      "title": "Add rate limiting to public API endpoints",
      "description": "Implement per-user rate limiting on /v1/* using a token-bucket algorithm in Redis. Need X-RateLimit-Limit, X-RateLimit-Remaining, X-RateLimit-Reset headers on all responses. Initial benchmarks suggest 10ms p99 overhead per request, which is within budget.",
      "priority": 2,
      "estimate": 5,
      "stateId": "state-bkd-inprogress",
    
... (truncated)
```

**GET GET List Workflow States** — `/v1/workflow-states` (status 200)

```
{
  "type": "workflow_states",
  "count": 12,
  "total": 12,
  "offset": 0,
  "limit": 50,
  "results": [
    {
      "id": "state-bkd-backlog",
      "name": "Backlog",
      "type": "backlog",
      "color": "#bec2c8",
      "position": 0,
      "teamId": "team-backend",
      "description": "Issues that are not yet prioritized"
    },
    {
      "id": "state-bkd-todo",
      "name": "Todo",
      "type": "unstarted",
      "color": "#e2e2e2",
      "position": 1,
      "teamId": "team-backend",
      "description": "Issues ready to be picked up"
    },
    {
      "id": "state-bkd-inprogre
... (truncated)
```

**GET GET Workflow States by Team** — `/v1/workflow-states?teamId=team-frontend` (status 200)

```
{
  "type": "workflow_states",
  "count": 0,
  "total": 0,
  "offset": 0,
  "limit": 50,
  "results": []
}
```

**GET GET Workflow State by ID** — `/v1/workflow-states/state-bkd-inprogress` (status 200)

```
{
  "type": "workflow_state",
  "workflowState": {
    "id": "state-bkd-inprogress",
    "name": "In Progress",
    "type": "started",
    "color": "#f2c94c",
    "position": 2,
    "teamId": "team-backend",
    "description": "Issues actively being worked on"
  }
}
```

**GET GET Workflow State - 404** — `/v1/workflow-states/nonexistent-state-99999` (status 404)

```
{
  "error": "Workflow state nonexistent-state-99999 not found"
}
```

**GET GET List Labels** — `/v1/labels` (status 200)

```
{
  "type": "labels",
  "count": 15,
  "total": 15,
  "offset": 0,
  "limit": 50,
  "results": [
    {
      "id": "label-bug",
      "name": "Bug",
      "color": "#eb5757",
      "description": "Something isn't working correctly",
      "teamId": null,
      "createdAt": "2026-01-15T09:00:00",
      "updatedAt": "2026-01-15T09:00:00"
    },
    {
      "id": "label-critical",
      "name": "Critical",
      "color": "#eb5757",
      "description": "Critical severity",
      "teamId": null,
      "createdAt": "2026-01-15T09:00:00",
      "updatedAt": "2026-01-15T09:00:00"
    },
    {
      "
... (truncated)
```

**GET GET Labels by Team** — `/v1/labels?teamId=team-platform` (status 200)

```
{
  "type": "labels",
  "count": 8,
  "total": 8,
  "offset": 0,
  "limit": 50,
  "results": [
    {
      "id": "label-bug",
      "name": "Bug",
      "color": "#eb5757",
      "description": "Something isn't working correctly",
      "teamId": null,
      "createdAt": "2026-01-15T09:00:00",
      "updatedAt": "2026-01-15T09:00:00"
    },
    {
      "id": "label-critical",
      "name": "Critical",
      "color": "#eb5757",
      "description": "Critical severity",
      "teamId": null,
      "createdAt": "2026-01-15T09:00:00",
      "updatedAt": "2026-01-15T09:00:00"
    },
    {
      "id
... (truncated)
```

**GET GET Label by ID** — `/v1/labels/label-bug` (status 200)

```
{
  "type": "label",
  "label": {
    "id": "label-bug",
    "name": "Bug",
    "color": "#eb5757",
    "description": "Something isn't working correctly",
    "teamId": null,
    "createdAt": "2026-01-15T09:00:00",
    "updatedAt": "2026-01-15T09:00:00"
  }
}
```

**GET GET Label - 404** — `/v1/labels/nonexistent-label-99999` (status 404)

```
{
  "error": "Label nonexistent-label-99999 not found"
}
```

**POST POST Create Label** — `/v1/labels` (status 201)

```
{
  "type": "label",
  "label": {
    "id": "label-c27eb46f",
    "name": "needs-review",
    "color": "#F2C94C",
    "description": "Issues requiring additional review",
    "teamId": "team-backend",
    "createdAt": "2026-06-17T10:31:21",
    "updatedAt": "2026-06-17T10:31:21"
  }
}
```

**GET GET List Projects** — `/v1/projects` (status 200)

```
{
  "type": "projects",
  "count": 3,
  "total": 3,
  "offset": 0,
  "limit": 50,
  "results": [
    {
      "id": "PROJ-PORTAL",
      "name": "Patient Portal UX Redesign",
      "description": "Cross-functional redesign of the Cumberland patient portal covering medications, dashboard, dark mode, and form validation flows. Charge nurse David Nelson signs off in this tracker before go-live.",
      "state": "started",
      "leadId": "user-patty",
      "teamIds": [
        "team-ux"
      ],
      "startDate": "2026-02-01",
      "targetDate": "2026-05-30",
      "createdAt": "2026-01-25T10:0
... (truncated)
```

**GET GET Project by ID** — `/v1/projects/proj-api-v2` (status 200)

```
{
  "type": "project",
  "project": {
    "id": "proj-api-v2",
    "name": "API v2 Migration",
    "description": "Migrate public REST endpoints from v1 to v2 with consistent error envelopes, rate-limit headers, and uniform pagination",
    "state": "started",
    "leadId": "user-01",
    "teamIds": [
      "team-backend"
    ],
    "startDate": "2026-02-01",
    "targetDate": "2026-06-30",
    "createdAt": "2026-01-20T09:00:00",
    "updatedAt": "2026-05-10T10:00:00"
  }
}
```

**GET GET Project - 404** — `/v1/projects/nonexistent-project-99999` (status 404)

```
{
  "error": "Project nonexistent-project-99999 not found"
}
```

**GET GET Project Issues** — `/v1/projects/proj-api-v2/issues` (status 200)

```
{
  "type": "issues",
  "count": 3,
  "total": 3,
  "offset": 0,
  "limit": 50,
  "results": [
    {
      "id": "issue-01",
      "identifier": "BKD-1",
      "number": 1,
      "title": "Add rate limiting to public API endpoints",
      "description": "Implement per-user rate limiting on /v1/* using a token-bucket algorithm in Redis. Need X-RateLimit-Limit, X-RateLimit-Remaining, X-RateLimit-Reset headers on all responses. Initial benchmarks suggest 10ms p99 overhead per request, which is within budget.",
      "priority": 2,
      "estimate": 5,
      "stateId": "state-bkd-inprogress",
    
... (truncated)
```

**POST POST Create Project** — `/v1/projects` (status 201)

```
{
  "type": "project",
  "project": {
    "id": "proj-b7317d7b",
    "name": "Mobile App MVP",
    "description": "Build first version of the mobile companion app",
    "state": "planned",
    "leadId": "user-06",
    "teamIds": [
      "team-frontend",
      "team-backend"
    ],
    "startDate": "2025-06-01",
    "targetDate": "2025-09-30",
    "createdAt": "2026-06-17T10:31:21",
    "updatedAt": "2026-06-17T10:31:21"
  }
}
```

**PUT PUT Update Project** — `/v1/projects/proj-dashboard` (status 200)

```
{
  "type": "project",
  "project": {
    "id": "proj-dashboard",
    "name": "Customer Dashboard",
    "description": "New customer-facing dashboard for usage analytics and billing",
    "state": "started",
    "leadId": "user-06",
    "teamIds": [
      "team-frontend",
      "team-backend"
    ],
    "startDate": "2026-03-01",
    "targetDate": "2026-07-15",
    "createdAt": "2026-02-15T09:00:00",
    "updatedAt": "2026-05-10T10:00:00"
  }
}
```

**GET GET List Cycles** — `/v1/cycles` (status 200)

```
{
  "type": "cycles",
  "count": 8,
  "total": 8,
  "offset": 0,
  "limit": 50,
  "results": [
    {
      "id": "cycle-port-1",
      "name": "Sprint 1",
      "number": 1,
      "teamId": "team-ux",
      "startsAt": "2026-03-09",
      "endsAt": "2026-03-22",
      "completedAt": "2026-03-22T17:00:00",
      "createdAt": "2026-02-28T09:00:00",
      "updatedAt": "2026-03-22T17:00:00"
    },
    {
      "id": "cycle-port-2",
      "name": "Sprint 2",
      "number": 2,
      "teamId": "team-ux",
      "startsAt": "2026-03-23",
      "endsAt": "2026-04-05",
      "completedAt": "2026-04-05T17
... (truncated)
```

**GET GET Cycles by Team** — `/v1/cycles?teamId=team-backend` (status 200)

```
{
  "type": "cycles",
  "count": 2,
  "total": 2,
  "offset": 0,
  "limit": 50,
  "results": [
    {
      "id": "cycle-bkd-1",
      "name": "Backend Sprint 1",
      "number": 1,
      "teamId": "team-backend",
      "startsAt": "2026-04-06",
      "endsAt": "2026-04-19",
      "completedAt": "2026-04-19T17:00:00",
      "createdAt": "2026-03-29T09:00:00",
      "updatedAt": "2026-04-19T17:00:00"
    },
    {
      "id": "cycle-bkd-2",
      "name": "Backend Sprint 2",
      "number": 2,
      "teamId": "team-backend",
      "startsAt": "2026-04-20",
      "endsAt": "2026-05-03",
      "comp
```

**GET GET Current Cycles** — `/v1/cycles?status=current` (status 200)

```
{
  "type": "cycles",
  "count": 0,
  "total": 0,
  "offset": 0,
  "limit": 50,
  "results": []
}
```

**GET GET Past Cycles** — `/v1/cycles?status=past` (status 200)

```
{
  "type": "cycles",
  "count": 5,
  "total": 5,
  "offset": 0,
  "limit": 50,
  "results": [
    {
      "id": "cycle-port-1",
      "name": "Sprint 1",
      "number": 1,
      "teamId": "team-ux",
      "startsAt": "2026-03-09",
      "endsAt": "2026-03-22",
      "completedAt": "2026-03-22T17:00:00",
      "createdAt": "2026-02-28T09:00:00",
      "updatedAt": "2026-03-22T17:00:00"
    },
    {
      "id": "cycle-port-2",
      "name": "Sprint 2",
      "number": 2,
      "teamId": "team-ux",
      "startsAt": "2026-03-23",
      "endsAt": "2026-04-05",
      "completedAt": "2026-04-05T17
... (truncated)
```

**GET GET Cycle by ID** — `/v1/cycles/cycle-bkd-2` (status 200)

```
{
  "type": "cycle",
  "cycle": {
    "id": "cycle-bkd-2",
    "name": "Backend Sprint 2",
    "number": 2,
    "teamId": "team-backend",
    "startsAt": "2026-04-20",
    "endsAt": "2026-05-03",
    "completedAt": null,
    "createdAt": "2026-04-13T09:00:00",
    "updatedAt": "2026-05-10T10:00:00"
  }
}
```

**GET GET Cycle - 404** — `/v1/cycles/nonexistent-cycle-99999` (status 404)

```
{
  "error": "Cycle nonexistent-cycle-99999 not found"
}
```

**GET GET Cycle Issues** — `/v1/cycles/cycle-bkd-2/issues` (status 200)

```
{
  "type": "issues",
  "count": 5,
  "total": 5,
  "offset": 0,
  "limit": 50,
  "results": [
    {
      "id": "issue-01",
      "identifier": "BKD-1",
      "number": 1,
      "title": "Add rate limiting to public API endpoints",
      "description": "Implement per-user rate limiting on /v1/* using a token-bucket algorithm in Redis. Need X-RateLimit-Limit, X-RateLimit-Remaining, X-RateLimit-Reset headers on all responses. Initial benchmarks suggest 10ms p99 overhead per request, which is within budget.",
      "priority": 2,
      "estimate": 5,
      "stateId": "state-bkd-inprogress",
    
... (truncated)
```

**POST POST Create Cycle** — `/v1/cycles` (status 201)

```
{
  "type": "cycle",
  "cycle": {
    "id": "cycle-ce53f6a5",
    "name": "Sprint 25",
    "number": 3,
    "teamId": "team-backend",
    "startsAt": "2025-05-19",
    "endsAt": "2025-06-01",
    "completedAt": null,
    "createdAt": "2026-06-17T10:31:21",
    "updatedAt": "2026-06-17T10:31:21"
  }
}
```

**GET GET List Issues (unfiltered)** — `/v1/issues` (status 200)

```
{
  "type": "issues",
  "count": 13,
  "total": 13,
  "offset": 0,
  "limit": 50,
  "results": [
    {
      "id": "BUG-201",
      "identifier": "PORT-201",
      "number": 201,
      "title": "Stats cards overlap on tablet viewport below 768px",
      "description": "Dashboard stats cards overlap each other on tablet viewports under 768px. Reported by Patty during the Apr review walkthrough.",
      "priority": 2,
      "estimate": 3,
      "stateId": "state-port-done",
      "assigneeId": "user-tyler",
      "teamId": "team-ux",
      "projectId": "PROJ-PORTAL",
      "cycleId": "cycle-port
... (truncated)
```

**GET GET Issues by State** — `/v1/issues?stateId=state-bkd-inprogress` (status 200)

```
{
  "type": "issues",
  "count": 1,
  "total": 1,
  "offset": 0,
  "limit": 50,
  "results": [
    {
      "id": "issue-01",
      "identifier": "BKD-1",
      "number": 1,
      "title": "Add rate limiting to public API endpoints",
      "description": "Implement per-user rate limiting on /v1/* using a token-bucket algorithm in Redis. Need X-RateLimit-Limit, X-RateLimit-Remaining, X-RateLimit-Reset headers on all responses. Initial benchmarks suggest 10ms p99 overhead per request, which is within budget.",
      "priority": 2,
      "estimate": 5,
      "stateId": "state-bkd-inprogress",
    
... (truncated)
```

**GET GET Issues by Assignee** — `/v1/issues?assigneeId=user-01` (status 200)

```
{
  "type": "issues",
  "count": 2,
  "total": 2,
  "offset": 0,
  "limit": 50,
  "results": [
    {
      "id": "issue-01",
      "identifier": "BKD-1",
      "number": 1,
      "title": "Add rate limiting to public API endpoints",
      "description": "Implement per-user rate limiting on /v1/* using a token-bucket algorithm in Redis. Need X-RateLimit-Limit, X-RateLimit-Remaining, X-RateLimit-Reset headers on all responses. Initial benchmarks suggest 10ms p99 overhead per request, which is within budget.",
      "priority": 2,
      "estimate": 5,
      "stateId": "state-bkd-inprogress",
    
... (truncated)
```

**GET GET Issues by Project** — `/v1/issues?projectId=proj-api-v2` (status 200)

```
{
  "type": "issues",
  "count": 3,
  "total": 3,
  "offset": 0,
  "limit": 50,
  "results": [
    {
      "id": "issue-01",
      "identifier": "BKD-1",
      "number": 1,
      "title": "Add rate limiting to public API endpoints",
      "description": "Implement per-user rate limiting on /v1/* using a token-bucket algorithm in Redis. Need X-RateLimit-Limit, X-RateLimit-Remaining, X-RateLimit-Reset headers on all responses. Initial benchmarks suggest 10ms p99 overhead per request, which is within budget.",
      "priority": 2,
      "estimate": 5,
      "stateId": "state-bkd-inprogress",
    
... (truncated)
```

**GET GET Issues by Priority** — `/v1/issues?priority=1` (status 200)

```
{
  "type": "issues",
  "count": 1,
  "total": 1,
  "offset": 0,
  "limit": 50,
  "results": [
    {
      "id": "BUG-209",
      "identifier": "PORT-209",
      "number": 209,
      "title": "Dark mode Recent Activity timestamps invisible white text on light gray",
      "description": "Dark mode renders Recent Activity timestamps as white text on a near-white card. Completely unreadable in low-light ER lighting.",
      "priority": 1,
      "estimate": 5,
      "stateId": "state-port-inprogress",
      "assigneeId": "user-tyler",
      "teamId": "team-ux",
      "projectId": "PROJ-PORTAL",
 
... (truncated)
```

**GET GET Issues by Label** — `/v1/issues?labelId=label-bug` (status 200)

```
{
  "type": "issues",
  "count": 10,
  "total": 10,
  "offset": 0,
  "limit": 50,
  "results": [
    {
      "id": "BUG-201",
      "identifier": "PORT-201",
      "number": 201,
      "title": "Stats cards overlap on tablet viewport below 768px",
      "description": "Dashboard stats cards overlap each other on tablet viewports under 768px. Reported by Patty during the Apr review walkthrough.",
      "priority": 2,
      "estimate": 3,
      "stateId": "state-port-done",
      "assigneeId": "user-tyler",
      "teamId": "team-ux",
      "projectId": "PROJ-PORTAL",
      "cycleId": "cycle-port
... (truncated)
```

**GET GET Issues by Team** — `/v1/issues?teamId=team-platform` (status 200)

```
{
  "type": "issues",
  "count": 0,
  "total": 0,
  "offset": 0,
  "limit": 50,
  "results": []
}
```

**GET GET Issues - Combined Filters (State + Assignee)** — `/v1/issues?stateId=state-bkd-inprogress&assigneeId=user-01` (status 200)

```
{
  "type": "issues",
  "count": 1,
  "total": 1,
  "offset": 0,
  "limit": 50,
  "results": [
    {
      "id": "issue-01",
      "identifier": "BKD-1",
      "number": 1,
      "title": "Add rate limiting to public API endpoints",
      "description": "Implement per-user rate limiting on /v1/* using a token-bucket algorithm in Redis. Need X-RateLimit-Limit, X-RateLimit-Remaining, X-RateLimit-Reset headers on all responses. Initial benchmarks suggest 10ms p99 overhead per request, which is within budget.",
      "priority": 2,
      "estimate": 5,
      "stateId": "state-bkd-inprogress",
    
... (truncated)
```

**GET GET Issues - Combined Filters (Project + Priority)** — `/v1/issues?projectId=proj-perf&priority=2` (status 200)

```
{
  "type": "issues",
  "count": 0,
  "total": 0,
  "offset": 0,
  "limit": 50,
  "results": []
}
```

**GET GET Issues with Pagination** — `/v1/issues?limit=5&offset=0` (status 200)

```
{
  "type": "issues",
  "count": 5,
  "total": 13,
  "offset": 0,
  "limit": 5,
  "results": [
    {
      "id": "BUG-201",
      "identifier": "PORT-201",
      "number": 201,
      "title": "Stats cards overlap on tablet viewport below 768px",
      "description": "Dashboard stats cards overlap each other on tablet viewports under 768px. Reported by Patty during the Apr review walkthrough.",
      "priority": 2,
      "estimate": 3,
      "stateId": "state-port-done",
      "assigneeId": "user-tyler",
      "teamId": "team-ux",
      "projectId": "PROJ-PORTAL",
      "cycleId": "cycle-port-4
... (truncated)
```

**GET GET Issue by ID** — `/v1/issues/issue-01` (status 200)

```
{
  "type": "issue",
  "issue": {
    "id": "issue-01",
    "identifier": "BKD-1",
    "number": 1,
    "title": "Add rate limiting to public API endpoints",
    "description": "Implement per-user rate limiting on /v1/* using a token-bucket algorithm in Redis. Need X-RateLimit-Limit, X-RateLimit-Remaining, X-RateLimit-Reset headers on all responses. Initial benchmarks suggest 10ms p99 overhead per request, which is within budget.",
    "priority": 2,
    "estimate": 5,
    "stateId": "state-bkd-inprogress",
    "assigneeId": "user-01",
    "teamId": "team-backend",
    "projectId": "proj-api-v
... (truncated)
```

**GET GET Issue - 404** — `/v1/issues/nonexistent-issue-99999` (status 404)

```
{
  "error": "Issue nonexistent-issue-99999 not found"
}
```

**GET GET Search Issues - keyword** — `/v1/issues/search?q=rate+limiting` (status 200)

```
{
  "type": "issues",
  "count": 1,
  "total": 1,
  "offset": 0,
  "limit": 50,
  "results": [
    {
      "id": "issue-01",
      "identifier": "BKD-1",
      "number": 1,
      "title": "Add rate limiting to public API endpoints",
      "description": "Implement per-user rate limiting on /v1/* using a token-bucket algorithm in Redis. Need X-RateLimit-Limit, X-RateLimit-Remaining, X-RateLimit-Reset headers on all responses. Initial benchmarks suggest 10ms p99 overhead per request, which is within budget.",
      "priority": 2,
      "estimate": 5,
      "stateId": "state-bkd-inprogress",
    
... (truncated)
```

**GET GET Search Issues - identifier** — `/v1/issues/search?q=MER-5` (status 200)

```
{
  "type": "issues",
  "count": 0,
  "total": 0,
  "offset": 0,
  "limit": 50,
  "results": []
}
```

**POST POST Create Issue** — `/v1/issues` (status 201)

```
{
  "type": "issue",
  "issue": {
    "id": "issue-60240762",
    "identifier": "MER-213",
    "number": 213,
    "title": "Add rate limit headers to API responses",
    "description": "Include X-RateLimit-Limit, X-RateLimit-Remaining, and X-RateLimit-Reset headers in all API responses",
    "priority": 3,
    "estimate": 2,
    "stateId": "state-bkd-todo",
    "assigneeId": "user-02",
    "teamId": "team-backend",
    "projectId": "proj-api-v2",
    "cycleId": "cycle-bkd-2",
    "labelIds": [
      "label-feature",
      "label-api"
    ],
    "dueDate": "2025-05-10",
    "sortOrder": 213.0,

... (truncated)
```

**PUT PUT Update Issue - State Change** — `/v1/issues/issue-09` (status 200)

```
{
  "type": "issue",
  "issue": {
    "id": "issue-09",
    "identifier": "BKD-9",
    "number": 9,
    "title": "Investigate intermittent 504 on bulk export endpoint",
    "description": "Bulk export occasionally times out at 30s under high load. Need to add streaming responses and tune connection keep-alive on the upstream proxy.",
    "priority": 2,
    "estimate": 8,
    "stateId": "state-bkd-todo",
    "assigneeId": "user-01",
    "teamId": "team-backend",
    "projectId": "proj-api-v2",
    "cycleId": "cycle-bkd-2",
    "labelIds": [
      "label-bug",
      "label-performance"
    ],
  
... (truncated)
```

**PUT PUT Update Issue - Priority and Estimate** — `/v1/issues/issue-15` (status 200)

```
{
  "type": "issue",
  "issue": {
    "id": "issue-15",
    "identifier": "BKD-15",
    "number": 15,
    "title": "Add OpenAPI 3.1 schema export for v2 endpoints",
    "description": "Generate complete OpenAPI 3.1 schema from the FastAPI app and publish it to the docs site.",
    "priority": 4,
    "estimate": 3,
    "stateId": "state-bkd-todo",
    "assigneeId": "user-02",
    "teamId": "team-backend",
    "projectId": "proj-api-v2",
    "cycleId": "cycle-bkd-2",
    "labelIds": [
      "label-feature",
      "label-api"
    ],
    "dueDate": null,
    "sortOrder": 4.0,
    "branchName": nul
... (truncated)
```

**PUT PUT Update Issue - Labels** — `/v1/issues/issue-07` (status 200)

```
{
  "type": "issue",
  "issue": {
    "id": "issue-07",
    "identifier": "BKD-7",
    "number": 7,
    "title": "Cache invalidation cascade on user profile updates",
    "description": "Profile edits should invalidate downstream cached views in the dashboard service. Today the dashboard can show stale display names for up to 30 minutes after a profile update.",
    "priority": 3,
    "estimate": 3,
    "stateId": "state-bkd-todo",
    "assigneeId": "user-02",
    "teamId": "team-backend",
    "projectId": "proj-dashboard",
    "cycleId": "cycle-bkd-2",
    "labelIds": [
      "label-feature",
... (truncated)
```

**DELETE DELETE Issue** — `/v1/issues/issue-26` (status 200)

```
{
  "type": "issue",
  "deleted": true,
  "issueId": "issue-26"
}
```

**DELETE DELETE Issue - 404** — `/v1/issues/nonexistent-issue-99999` (status 404)

```
{
  "error": "Issue nonexistent-issue-99999 not found"
}
```

**GET GET List Comments for Issue** — `/v1/issues/issue-01/comments` (status 200)

```
{
  "type": "comments",
  "count": 1,
  "total": 1,
  "offset": 0,
  "limit": 50,
  "results": [
    {
      "id": "comment-01",
      "body": "Started prototyping the token-bucket implementation. Initial benchmarks suggest 10ms p99 overhead per request, which is within budget.",
      "issueId": "issue-01",
      "userId": "user-01",
      "createdAt": "2026-04-22T10:00:00",
      "updatedAt": "2026-04-22T10:00:00"
    }
  ]
}
```

**GET GET Comments - Issue 404** — `/v1/issues/nonexistent-issue-99999/comments` (status 404)

```
{
  "error": "Issue nonexistent-issue-99999 not found"
}
```

**GET GET Comment by ID** — `/v1/comments/comment-01` (status 200)

```
{
  "type": "comment",
  "comment": {
    "id": "comment-01",
    "body": "Started prototyping the token-bucket implementation. Initial benchmarks suggest 10ms p99 overhead per request, which is within budget.",
    "issueId": "issue-01",
    "userId": "user-01",
    "createdAt": "2026-04-22T10:00:00",
    "updatedAt": "2026-04-22T10:00:00"
  }
}
```

**GET GET Comment - 404** — `/v1/comments/nonexistent-comment-99999` (status 404)

```
{
  "error": "Comment nonexistent-comment-99999 not found"
}
```

**POST POST Create Comment** — `/v1/comments` (status 201)

```
{
  "type": "comment",
  "comment": {
    "id": "comment-14",
    "body": "Looks good! Just one nit - can we add a retry mechanism for the rate limit check in case Redis is temporarily unavailable?",
    "issueId": "issue-01",
    "userId": "user-01",
    "createdAt": "2026-06-17T10:31:21",
    "updatedAt": "2026-06-17T10:31:21"
  }
}
```

**POST POST Create Comment - Issue 404** — `/v1/comments` (status 400)

```
{
  "error": "Issue nonexistent-issue-99999 not found"
}
```

**PUT PUT Update Comment** — `/v1/comments/comment-01` (status 200)

```
{
  "type": "comment",
  "comment": {
    "id": "comment-01",
    "body": "Started prototyping the token-bucket implementation. Initial benchmarks suggest 10ms p99 overhead per request, which is within budget.",
    "issueId": "issue-01",
    "userId": "user-01",
    "createdAt": "2026-04-22T10:00:00",
    "updatedAt": "2026-04-22T10:00:00"
  }
}
```

**DELETE DELETE Comment** — `/v1/comments/comment-25` (status 200)

```
{
  "type": "comment",
  "deleted": true,
  "commentId": "comment-25"
}
```

**DELETE DELETE Comment - 404** — `/v1/comments/nonexistent-comment-99999` (status 404)

```
{
  "error": "Comment nonexistent-comment-99999 not found"
}
```

</details>

### linkedin-api (port 8062) — server: started

| Result | Method | Path | Status | Endpoint |
|--------|--------|------|--------|----------|
| PASS | GET | /health | 200 | health |
| PASS | GET | /v2/me | 200 | get me |
| PASS | GET | /v2/connections?count=10 | 200 | list connections |
| PASS | GET | /v2/posts | 200 | list posts |
| PASS | GET | /v2/posts?author_id=urn:li:person:amelia-ortega | 200 | list posts by author |
| PASS | GET | /v2/posts/6003 | 200 | get post |
| PASS | POST | /v2/posts | 201 | create post |
| PASS | GET | /v2/organizations/5001 | 200 | get organization |
| PASS | GET | /v2/jobs?keywords=backend&location=Remote | 200 | search jobs |
| PASS | GET | /v2/jobs/7001 | 200 | get job |

<details><summary>responses</summary>

**GET health** — `/health` (status 200)

```
{
  "status": "ok"
}
```

**GET get me** — `/v2/me` (status 200)

```
{
  "id": "urn:li:person:amelia-ortega",
  "localizedFirstName": "Amelia",
  "localizedLastName": "Ortega",
  "headline": "VP Engineering at Orbit Labs | Distributed Systems",
  "vanityName": "amelia-ortega",
  "location": "Seattle, Washington, United States",
  "industry": "Software Development",
  "summary": "Engineering leader focused on developer platforms and reliability. Previously infra lead at two high-growth startups.",
  "profilePicture": "https://media.example.com/amelia.png",
  "publicProfileUrl": "https://www.linkedin.com/in/amelia-ortega",
  "numConnections": 842,
  "currentOrgan
```

**GET list connections** — `/v2/connections?count=10` (status 200)

```
{
  "elements": [
    {
      "id": "urn:li:person:jonas-pereira",
      "firstName": "Jonas",
      "lastName": "Pereira",
      "headline": "Senior Infrastructure Engineer at Orbit Labs",
      "location": "Lisbon Portugal",
      "industry": "Software Development",
      "connectedAt": "2024-02-11T10:00:00.000Z",
      "organizationId": "5001"
    },
    {
      "id": "urn:li:person:helena-park",
      "firstName": "Helena",
      "lastName": "Park",
      "headline": "Staff Frontend Engineer | Accessibility",
      "location": "Austin Texas",
      "industry": "Software Development",
     
... (truncated)
```

**GET list posts** — `/v2/posts` (status 200)

```
{
  "elements": [
    {
      "id": "6006",
      "author_id": "urn:li:person:amelia-ortega",
      "commentary": "Reliability tip: gate every rollout on p95 latency, not averages. Averages hide the pain your users feel.",
      "visibility": "PUBLIC",
      "created_at": "2026-05-25T08:15:00.000Z",
      "socialDetail": {
        "likeCount": 512,
        "commentCount": 71,
        "shareCount": 94
      }
    },
    {
      "id": "6005",
      "author_id": "urn:li:person:noor-aziz",
      "commentary": "New migration guide is up: moving to the Orbit plugin API without downtime. Took us a we
... (truncated)
```

**GET list posts by author** — `/v2/posts?author_id=urn:li:person:amelia-ortega` (status 200)

```
{
  "elements": [
    {
      "id": "6006",
      "author_id": "urn:li:person:amelia-ortega",
      "commentary": "Reliability tip: gate every rollout on p95 latency, not averages. Averages hide the pain your users feel.",
      "visibility": "PUBLIC",
      "created_at": "2026-05-25T08:15:00.000Z",
      "socialDetail": {
        "likeCount": 512,
        "commentCount": 71,
        "shareCount": 94
      }
    },
    {
      "id": "6002",
      "author_id": "urn:li:person:amelia-ortega",
      "commentary": "Hiring two senior backend engineers for the platform team. Remote-friendly across EU
... (truncated)
```

**GET get post** — `/v2/posts/6003` (status 200)

```
{
  "id": "6003",
  "author_id": "urn:li:organization:orbit-labs",
  "commentary": "Orbit CLI 2.0 is live. Faster cold starts and a new plugin system. Read the launch post on our blog.",
  "visibility": "PUBLIC",
  "created_at": "2026-05-21T17:00:00.000Z",
  "socialDetail": {
    "likeCount": 904,
    "commentCount": 112,
    "shareCount": 210
  }
}
```

**POST create post** — `/v2/posts` (status 201)

```
{
  "id": "1121718325",
  "author_id": "urn:li:person:amelia-ortega",
  "commentary": "Thrilled to share our team shipped the new plugin API today.",
  "visibility": "PUBLIC",
  "created_at": "2026-06-17T10:31:22.000Z",
  "socialDetail": {
    "likeCount": 0,
    "commentCount": 0,
    "shareCount": 0
  }
}
```

**GET get organization** — `/v2/organizations/5001` (status 200)

```
{
  "id": "5001",
  "name": "Orbit Labs",
  "vanityName": "orbit-labs",
  "industry": "Software Development",
  "website": "https://orbit-labs.com",
  "location": "Remote",
  "staffCountRange": "51-200",
  "followerCount": 48210,
  "description": "Developer tooling for the modern stack. Makers of the Orbit CLI and platform."
}
```

**GET search jobs** — `/v2/jobs?keywords=backend&location=Remote` (status 200)

```
{
  "elements": [
    {
      "id": "7001",
      "title": "Senior Backend Engineer",
      "organizationId": "5001",
      "location": "Remote",
      "workplaceType": "REMOTE",
      "employmentType": "FULL_TIME",
      "seniority": "Senior",
      "keywords": [
        "backend",
        "python",
        "distributed-systems"
      ],
      "postedAt": "2026-05-15T09:00:00.000Z",
      "applicants": 64,
      "description": "Build and scale the Orbit platform services in Python and Go."
    }
  ],
  "paging": {
    "start": 0,
    "count": 50,
    "total": 1
  }
}
```

**GET get job** — `/v2/jobs/7001` (status 200)

```
{
  "id": "7001",
  "title": "Senior Backend Engineer",
  "organizationId": "5001",
  "location": "Remote",
  "workplaceType": "REMOTE",
  "employmentType": "FULL_TIME",
  "seniority": "Senior",
  "keywords": [
    "backend",
    "python",
    "distributed-systems"
  ],
  "postedAt": "2026-05-15T09:00:00.000Z",
  "applicants": 64,
  "description": "Build and scale the Orbit platform services in Python and Go."
}
```

</details>

### mailchimp-api (port 8081) — server: started

| Result | Method | Path | Status | Endpoint |
|--------|--------|------|--------|----------|
| PASS | GET | /health | 200 | health |
| PASS | GET | /3.0/lists | 200 | list lists |
| PASS | GET | /3.0/lists/list-newsletter | 200 | get list |
| PASS | GET | /3.0/lists/list-newsletter/members?status=subscribed | 200 | list members |
| PASS | POST | /3.0/lists/list-newsletter/members | 201 | create member |
| PASS | GET | /3.0/lists/list-newsletter/members/mara@brightpath.io | 200 | get member |
| PASS | PATCH | /3.0/lists/list-newsletter/members/tomas@brightpath.io | 200 | update member |
| PASS | GET | /3.0/campaigns?status=sent | 200 | list campaigns |
| PASS | POST | /3.0/campaigns | 201 | create campaign |
| PASS | GET | /3.0/campaigns/camp-sep-news | 200 | get campaign |
| PASS | POST | /3.0/campaigns/camp-nov-draft/actions/send | 200 | send campaign |
| PASS | GET | /3.0/reports/camp-oct-news | 200 | get report |

<details><summary>responses</summary>

**GET health** — `/health` (status 200)

```
{
  "status": "ok"
}
```

**GET list lists** — `/3.0/lists` (status 200)

```
{
  "lists": [
    {
      "id": "list-newsletter",
      "name": "Orbit Monthly Newsletter",
      "company": "Orbit Labs",
      "from_name": "Orbit Labs",
      "from_email": "news@orbit-labs.com",
      "subject": "Orbit Monthly",
      "member_count": 5,
      "unsubscribe_count": 1,
      "date_created": "2025-09-01T10:00:00.000Z"
    },
    {
      "id": "list-product",
      "name": "Product Updates",
      "company": "Orbit Labs",
      "from_name": "Orbit Product",
      "from_email": "product@orbit-labs.com",
      "subject": "Product Updates",
      "member_count": 4,
      "unsubs
```

**GET get list** — `/3.0/lists/list-newsletter` (status 200)

```
{
  "id": "list-newsletter",
  "name": "Orbit Monthly Newsletter",
  "company": "Orbit Labs",
  "from_name": "Orbit Labs",
  "from_email": "news@orbit-labs.com",
  "subject": "Orbit Monthly",
  "member_count": 5,
  "unsubscribe_count": 1,
  "date_created": "2025-09-01T10:00:00.000Z"
}
```

**GET list members** — `/3.0/lists/list-newsletter/members?status=subscribed` (status 200)

```
{
  "members": [
    {
      "id": "0d05c30f3ef9742e1a0144755a9299b4",
      "list_id": "list-newsletter",
      "email_address": "mara@brightpath.io",
      "full_name": "Mara Lindgren",
      "status": "subscribed",
      "timestamp_signup": "2025-09-02T08:00:00.000Z",
      "member_rating": 4
    },
    {
      "id": "e680f3f5e04d7a7de7e1d2aa788f12b6",
      "list_id": "list-newsletter",
      "email_address": "tomas@brightpath.io",
      "full_name": "Tomas Vega",
      "status": "subscribed",
      "timestamp_signup": "2025-09-05T09:00:00.000Z",
      "member_rating": 3
    },
    {
     
... (truncated)
```

**POST create member** — `/3.0/lists/list-newsletter/members` (status 201)

```
{
  "id": "9e55e80ea942b2727c9d6d0c625ca636",
  "list_id": "list-newsletter",
  "email_address": "newuser@example.com",
  "full_name": "New User",
  "status": "subscribed",
  "timestamp_signup": "2026-06-17T10:31:22+00:00",
  "member_rating": 0
}
```

**GET get member** — `/3.0/lists/list-newsletter/members/mara@brightpath.io` (status 200)

```
{
  "id": "0d05c30f3ef9742e1a0144755a9299b4",
  "list_id": "list-newsletter",
  "email_address": "mara@brightpath.io",
  "full_name": "Mara Lindgren",
  "status": "subscribed",
  "timestamp_signup": "2025-09-02T08:00:00.000Z",
  "member_rating": 4
}
```

**PATCH update member** — `/3.0/lists/list-newsletter/members/tomas@brightpath.io` (status 200)

```
{
  "id": "e680f3f5e04d7a7de7e1d2aa788f12b6",
  "list_id": "list-newsletter",
  "email_address": "tomas@brightpath.io",
  "full_name": "Tomas Vega",
  "status": "unsubscribed",
  "timestamp_signup": "2025-09-05T09:00:00.000Z",
  "member_rating": 3
}
```

**GET list campaigns** — `/3.0/campaigns?status=sent` (status 200)

```
{
  "campaigns": [
    {
      "id": "camp-sep-news",
      "list_id": "list-newsletter",
      "type": "regular",
      "status": "sent",
      "emails_sent": 5,
      "send_time": "2025-09-28T15:00:00.000Z",
      "create_time": "2025-09-25T10:00:00.000Z",
      "recipients": {
        "list_id": "list-newsletter"
      },
      "settings": {
        "subject_line": "September Highlights",
        "from_name": "Orbit Labs",
        "reply_to": "news@orbit-labs.com",
        "title": "September Newsletter"
      }
    },
    {
      "id": "camp-oct-news",
      "list_id": "list-newsletter",
 
... (truncated)
```

**POST create campaign** — `/3.0/campaigns` (status 201)

```
{
  "id": "camp-66e49ca108",
  "list_id": "list-product",
  "type": "regular",
  "status": "save",
  "emails_sent": 0,
  "send_time": null,
  "create_time": "2026-06-17T10:31:22+00:00",
  "recipients": {
    "list_id": "list-product"
  },
  "settings": {
    "subject_line": "December Update",
    "from_name": "Orbit Product",
    "reply_to": "product@orbit-labs.com",
    "title": "December Update"
  }
}
```

**GET get campaign** — `/3.0/campaigns/camp-sep-news` (status 200)

```
{
  "id": "camp-sep-news",
  "list_id": "list-newsletter",
  "type": "regular",
  "status": "sent",
  "emails_sent": 5,
  "send_time": "2025-09-28T15:00:00.000Z",
  "create_time": "2025-09-25T10:00:00.000Z",
  "recipients": {
    "list_id": "list-newsletter"
  },
  "settings": {
    "subject_line": "September Highlights",
    "from_name": "Orbit Labs",
    "reply_to": "news@orbit-labs.com",
    "title": "September Newsletter"
  }
}
```

**POST send campaign** — `/3.0/campaigns/camp-nov-draft/actions/send` (status 200)

```
{
  "id": "camp-nov-draft",
  "status": "sent",
  "emails_sent": 6
}
```

**GET get report** — `/3.0/reports/camp-oct-news` (status 200)

```
{
  "id": "camp-oct-news",
  "emails_sent": 5,
  "opens": {
    "opens_total": 22,
    "unique_opens": 5,
    "open_rate": 1.0
  },
  "clicks": {
    "clicks_total": 9,
    "unique_clicks": 4,
    "click_rate": 0.8
  },
  "unsubscribed": 1,
  "bounces": {
    "hard_bounces": 0
  }
}
```

</details>

### mailgun-api (port 8094) — server: started

| Result | Method | Path | Status | Endpoint |
|--------|--------|------|--------|----------|
| PASS | GET | /health | 200 | health |
| PASS | POST | /v3/sandbox.mailgun.org/messages | 200 | send message |
| PASS | GET | /v3/sandbox.mailgun.org/events | 200 | events |
| PASS | GET | /v3/sandbox.mailgun.org/events?event=delivered | 200 | events by type |
| PASS | GET | /v3/sandbox.mailgun.org/stats/total | 200 | stats total |
| PASS | GET | /v3/lists/newsletter@sandbox.mailgun.org/members | 200 | list members |
| PASS | GET | /v3/lists/newsletter@sandbox.mailgun.org/members?subscribed=true | 200 | list members subscribed |

<details><summary>responses</summary>

**GET health** — `/health` (status 200)

```
{
  "status": "ok"
}
```

**POST send message** — `/v3/sandbox.mailgun.org/messages` (status 200)

```
{
  "id": "<20260617103123.766CE13CD801@sandbox.mailgun.org>",
  "message": "Queued. Thank you."
}
```

**GET events** — `/v3/sandbox.mailgun.org/events` (status 200)

```
{
  "items": [
    {
      "id": "ev_0012",
      "event": "accepted",
      "timestamp": "2026-05-24T17:56:11Z",
      "recipient": "grace@example.com",
      "message": {
        "headers": {
          "message-id": "20260524175611.7.A7B8C9D0E1F2@sandbox.mailgun.org"
        }
      }
    },
    {
      "id": "ev_0011",
      "event": "delivered",
      "timestamp": "2026-05-20T11:39:06Z",
      "recipient": "frank@example.com",
      "message": {
        "headers": {
          "message-id": "20260520113900.6.F6A7B8C9D0E1@sandbox.mailgun.org"
        }
      }
    },
    {
      "id": "ev_00
... (truncated)
```

**GET events by type** — `/v3/sandbox.mailgun.org/events?event=delivered` (status 200)

```
{
  "items": [
    {
      "id": "ev_0011",
      "event": "delivered",
      "timestamp": "2026-05-20T11:39:06Z",
      "recipient": "frank@example.com",
      "message": {
        "headers": {
          "message-id": "20260520113900.6.F6A7B8C9D0E1@sandbox.mailgun.org"
        }
      }
    },
    {
      "id": "ev_0009",
      "event": "delivered",
      "timestamp": "2026-05-15T10:47:39Z",
      "recipient": "erin@example.com",
      "message": {
        "headers": {
          "message-id": "20260515104733.5.E5F6A7B8C9D0@sandbox.mailgun.org"
        }
      }
    },
    {
      "id": "ev_00
... (truncated)
```

**GET stats total** — `/v3/sandbox.mailgun.org/stats/total` (status 200)

```
{
  "start": "2026-05-01T09:30:12Z",
  "end": "2026-05-24T17:56:11Z",
  "resolution": "month",
  "stats": [
    {
      "time": "2026-06-17T10:31:23Z",
      "accepted": {
        "total": 4
      }
    },
    {
      "time": "2026-06-17T10:31:23Z",
      "delivered": {
        "total": 5
      }
    },
    {
      "time": "2026-06-17T10:31:23Z",
      "failed": {
        "total": 1
      }
    },
    {
      "time": "2026-06-17T10:31:23Z",
      "opened": {
        "total": 1
      }
    },
    {
      "time": "2026-06-17T10:31:23Z",
      "clicked": {
        "total": 1
      }
    }
  ]
}
```

**GET list members** — `/v3/lists/newsletter@sandbox.mailgun.org/members` (status 200)

```
{
  "items": [
    {
      "address": "alice@example.com",
      "name": "Alice Adams",
      "subscribed": true,
      "vars": "{\"plan\":\"pro\"}"
    },
    {
      "address": "bob@example.com",
      "name": "Bob Brown",
      "subscribed": true,
      "vars": "{\"plan\":\"free\"}"
    },
    {
      "address": "carol@example.com",
      "name": "Carol Clark",
      "subscribed": false,
      "vars": "{\"plan\":\"free\"}"
    },
    {
      "address": "dave@example.com",
      "name": "Dave Davis",
      "subscribed": true,
      "vars": "{\"plan\":\"enterprise\"}"
    }
  ],
  "total_coun
```

**GET list members subscribed** — `/v3/lists/newsletter@sandbox.mailgun.org/members?subscribed=true` (status 200)

```
{
  "items": [
    {
      "address": "alice@example.com",
      "name": "Alice Adams",
      "subscribed": true,
      "vars": "{\"plan\":\"pro\"}"
    },
    {
      "address": "bob@example.com",
      "name": "Bob Brown",
      "subscribed": true,
      "vars": "{\"plan\":\"free\"}"
    },
    {
      "address": "dave@example.com",
      "name": "Dave Davis",
      "subscribed": true,
      "vars": "{\"plan\":\"enterprise\"}"
    }
  ],
  "total_count": 3
}
```

</details>

### microsoft-teams-api (port 8086) — server: started

| Result | Method | Path | Status | Endpoint |
|--------|--------|------|--------|----------|
| PASS | GET | /health | 200 | health |
| PASS | GET | /v1.0/me/joinedTeams | 200 | joined teams |
| PASS | GET | /v1.0/teams/19:team-eng0001@thread.tacv2 | 200 | get team |
| PASS | GET | /v1.0/teams/19:team-eng0001@thread.tacv2/channels | 200 | list channels |
| PASS | GET | /v1.0/teams/19:team-eng0001@thread.tacv2/channels/19:chan-eng-gen01@thread.tacv2/messages | 200 | list channel messages |
| PASS | POST | /v1.0/teams/19:team-eng0001@thread.tacv2/channels/19:chan-eng-gen01@thread.tacv2/messages | 201 | send channel message |

<details><summary>responses</summary>

**GET health** — `/health` (status 200)

```
{
  "status": "ok"
}
```

**GET joined teams** — `/v1.0/me/joinedTeams` (status 200)

```
{
  "value": [
    {
      "id": "19:team-eng0001@thread.tacv2",
      "displayName": "Engineering",
      "description": "Core engineering team for platform and infra",
      "visibility": "private",
      "isArchived": false,
      "webUrl": "https://teams.microsoft.com/l/team/19%3Ateam-eng0001"
    },
    {
      "id": "19:team-allco005@thread.tacv2",
      "displayName": "All Company",
      "description": "Company-wide announcements and town halls",
      "visibility": "public",
      "isArchived": false,
      "webUrl": "https://teams.microsoft.com/l/team/19%3Ateam-allco005"
    }
  ]
}
```

**GET get team** — `/v1.0/teams/19:team-eng0001@thread.tacv2` (status 200)

```
{
  "id": "19:team-eng0001@thread.tacv2",
  "displayName": "Engineering",
  "description": "Core engineering team for platform and infra",
  "visibility": "private",
  "isArchived": false,
  "webUrl": "https://teams.microsoft.com/l/team/19%3Ateam-eng0001"
}
```

**GET list channels** — `/v1.0/teams/19:team-eng0001@thread.tacv2/channels` (status 200)

```
{
  "value": [
    {
      "id": "19:chan-eng-gen01@thread.tacv2",
      "displayName": "General",
      "description": "Default channel for the Engineering team",
      "membershipType": "standard",
      "webUrl": "https://teams.microsoft.com/l/channel/19%3Achan-eng-gen01",
      "createdDateTime": "2026-01-12T09:00:00Z"
    },
    {
      "id": "19:chan-eng-plat02@thread.tacv2",
      "displayName": "Platform",
      "description": "Platform services discussion",
      "membershipType": "standard",
      "webUrl": "https://teams.microsoft.com/l/channel/19%3Achan-eng-plat02",
      "createdD
... (truncated)
```

**GET list channel messages** — `/v1.0/teams/19:team-eng0001@thread.tacv2/channels/19:chan-eng-gen01@thread.tacv2/messages` (status 200)

```
{
  "value": [
    {
      "id": "1747900000002",
      "messageType": "message",
      "createdDateTime": "2026-05-11T13:45:00Z",
      "importance": "high",
      "channelIdentity": {
        "teamId": "19:team-eng0001@thread.tacv2",
        "channelId": "19:chan-eng-gen01@thread.tacv2"
      },
      "from": {
        "user": {
          "id": "user-002",
          "displayName": "Priya Nair"
        }
      },
      "body": {
        "contentType": "html",
        "content": "Reminder: sprint planning at 2pm today."
      }
    },
    {
      "id": "1747900000001",
      "messageType": "me
... (truncated)
```

**POST send channel message** — `/v1.0/teams/19:team-eng0001@thread.tacv2/channels/19:chan-eng-gen01@thread.tacv2/messages` (status 201)

```
{
  "id": "1781692284050fc7d",
  "messageType": "message",
  "createdDateTime": "2026-06-17T10:31:24Z",
  "importance": "high",
  "channelIdentity": {
    "teamId": "19:team-eng0001@thread.tacv2",
    "channelId": "19:chan-eng-gen01@thread.tacv2"
  },
  "from": {
    "user": {
      "id": "user-001",
      "displayName": "Alex Carter"
    }
  },
  "body": {
    "contentType": "html",
    "content": "Deploy window confirmed for 3pm."
  }
}
```

</details>

### mixpanel-api (port 8056) — server: started

| Result | Method | Path | Status | Endpoint |
|--------|--------|------|--------|----------|
| PASS | GET | /health | 200 | health |
| PASS | POST | /track | 200 | track event |
| PASS | GET | /api/2.0/events?event=App Open,Checkout&from_date=2025-05-01&to_date=2025-05-04 | 200 | events counts |
| PASS | GET | /api/2.0/funnels/list | 200 | funnels list |
| PASS | GET | /api/2.0/funnels?funnel_id=7461001 | 200 | funnel |
| PASS | GET | /api/2.0/segmentation?event=App Open&from_date=2025-05-01&to_date=2025-05-04&on=country | 200 | segmentation |
| PASS | GET | /api/2.0/engage?where=plan==paid | 200 | engage profiles |
| PASS | GET | /api/2.0/engage?distinct_id=user-aria | 200 | engage one profile |

<details><summary>responses</summary>

**GET health** — `/health` (status 200)

```
{
  "status": "ok"
}
```

**POST track event** — `/track` (status 200)

```
{
  "status": 1,
  "event_id": "evt-add5a575"
}
```

**GET events counts** — `/api/2.0/events?event=App Open,Checkout&from_date=2025-05-01&to_date=2025-05-04` (status 200)

```
{
  "data": {
    "series": [
      "2025-05-01",
      "2025-05-02",
      "2025-05-03",
      "2025-05-04"
    ],
    "values": {
      "App Open": {
        "2025-05-01": 1,
        "2025-05-02": 2,
        "2025-05-03": 1,
        "2025-05-04": 1
      },
      "Checkout": {
        "2025-05-01": 1,
        "2025-05-02": 0,
        "2025-05-03": 1,
        "2025-05-04": 0
      }
    }
  },
  "legend_size": 2
}
```

**GET funnels list** — `/api/2.0/funnels/list` (status 200)

```
[
  {
    "funnel_id": 7461001,
    "name": "Purchase Funnel"
  },
  {
    "funnel_id": 7461002,
    "name": "Activation Funnel"
  }
]
```

**GET funnel** — `/api/2.0/funnels?funnel_id=7461001` (status 200)

```
{
  "funnel_id": 7461001,
  "name": "Purchase Funnel",
  "steps": [
    {
      "step_label": "App Open",
      "event": "App Open",
      "count": 1200,
      "step_conv_ratio": 1.0,
      "overall_conv_ratio": 1.0
    },
    {
      "step_label": "Product Viewed",
      "event": "Product Viewed",
      "count": 860,
      "step_conv_ratio": 0.7167,
      "overall_conv_ratio": 0.7167
    },
    {
      "step_label": "Add to Cart",
      "event": "Add to Cart",
      "count": 430,
      "step_conv_ratio": 0.5,
      "overall_conv_ratio": 0.3583
    },
    {
      "step_label": "Checkout",
    
```

**GET segmentation** — `/api/2.0/segmentation?event=App Open&from_date=2025-05-01&to_date=2025-05-04&on=country` (status 200)

```
{
  "data": {
    "series": [
      "2025-05-01",
      "2025-05-02",
      "2025-05-03",
      "2025-05-04"
    ],
    "values": {
      "US": {
        "2025-05-01": 1,
        "2025-05-02": 0,
        "2025-05-03": 1,
        "2025-05-04": 1
      },
      "DE": {
        "2025-05-01": 0,
        "2025-05-02": 1,
        "2025-05-03": 0,
        "2025-05-04": 0
      },
      "GB": {
        "2025-05-01": 0,
        "2025-05-02": 1,
        "2025-05-03": 0,
        "2025-05-04": 0
      }
    }
  }
}
```

**GET engage profiles** — `/api/2.0/engage?where=plan==paid` (status 200)

```
{
  "results": [
    {
      "distinct_id": "user-aria",
      "properties": {
        "$name": "Aria Mensah",
        "$email": "aria.mensah@example.com",
        "country": "US",
        "plan": "paid",
        "total_events": 6,
        "$last_seen": "2025-05-03T18:02:00Z"
      }
    },
    {
      "distinct_id": "user-bode",
      "properties": {
        "$name": "Bode Larsen",
        "$email": "bode.larsen@example.com",
        "country": "DE",
        "plan": "paid",
        "total_events": 5,
        "$last_seen": "2025-05-03T09:10:00Z"
      }
    }
  ],
  "page": 0,
  "page_size": 5
```

**GET engage one profile** — `/api/2.0/engage?distinct_id=user-aria` (status 200)

```
{
  "results": [
    {
      "distinct_id": "user-aria",
      "properties": {
        "$name": "Aria Mensah",
        "$email": "aria.mensah@example.com",
        "country": "US",
        "plan": "paid",
        "total_events": 6,
        "$last_seen": "2025-05-03T18:02:00Z"
      }
    }
  ],
  "page": 0,
  "page_size": 50,
  "total": 1
}
```

</details>

### monday-api (port 8080) — server: started

| Result | Method | Path | Status | Endpoint |
|--------|--------|------|--------|----------|
| PASS | GET | /health | 200 | health |
| PASS | GET | /v2/workspaces | 200 | list workspaces |
| PASS | GET | /v2/boards?workspace_id=ws-1 | 200 | list boards |
| PASS | GET | /v2/boards/board-101 | 200 | get board |
| PASS | GET | /v2/boards/board-101/items | 200 | board items |
| PASS | GET | /v2/items?board_id=board-101&group_id=grp-todo | 200 | list items |
| PASS | GET | /v2/items/item-1001 | 200 | get item |
| PASS | POST | /v2/items | 201 | create item |
| PASS | PUT | /v2/items/item-1002 | 200 | update item (change status) |
| PASS | PUT | /v2/items/item-1002 | 200 | update item (move group) |
| PASS | DELETE | /v2/items/item-1004 | 200 | delete item |
| PASS | GET | /v2/users | 200 | list users |

<details><summary>responses</summary>

**GET health** — `/health` (status 200)

```
{
  "status": "ok"
}
```

**GET list workspaces** — `/v2/workspaces` (status 200)

```
{
  "workspaces": [
    {
      "id": "ws-1",
      "name": "Engineering",
      "kind": "open",
      "description": "Engineering delivery and sprint planning"
    },
    {
      "id": "ws-2",
      "name": "Marketing",
      "kind": "open",
      "description": "Campaigns and content calendar"
    }
  ]
}
```

**GET list boards** — `/v2/boards?workspace_id=ws-1` (status 200)

```
{
  "boards": [
    {
      "id": "board-101",
      "name": "Sprint Backlog",
      "description": "Current sprint work items",
      "state": "active",
      "board_kind": "public",
      "workspace_id": "ws-1"
    },
    {
      "id": "board-102",
      "name": "Bug Tracker",
      "description": "Reported defects and triage",
      "state": "active",
      "board_kind": "public",
      "workspace_id": "ws-1"
    }
  ]
}
```

**GET get board** — `/v2/boards/board-101` (status 200)

```
{
  "id": "board-101",
  "name": "Sprint Backlog",
  "description": "Current sprint work items",
  "state": "active",
  "board_kind": "public",
  "workspace_id": "ws-1",
  "groups": [
    {
      "id": "grp-todo",
      "title": "To Do",
      "color": "#fdab3d",
      "position": 1
    },
    {
      "id": "grp-doing",
      "title": "In Progress",
      "color": "#0086c0",
      "position": 2
    },
    {
      "id": "grp-done",
      "title": "Done",
      "color": "#00c875",
      "position": 3
    }
  ],
  "columns": [
    {
      "id": "status",
      "title": "Status",
      "type": "st
... (truncated)
```

**GET board items** — `/v2/boards/board-101/items` (status 200)

```
{
  "items": [
    {
      "id": "item-1001",
      "name": "Implement OAuth token refresh",
      "board_id": "board-101",
      "group": {
        "id": "grp-doing"
      },
      "created_at": "2026-05-18T09:00:00Z",
      "column_values": [
        {
          "id": "status",
          "text": "In Progress",
          "value": null
        },
        {
          "id": "owner",
          "text": "Helena Park",
          "value": "usr-2"
        },
        {
          "id": "due",
          "text": "2026-05-30",
          "value": null
        },
        {
          "id": "notes",
          
... (truncated)
```

**GET list items** — `/v2/items?board_id=board-101&group_id=grp-todo` (status 200)

```
{
  "items": [
    {
      "id": "item-1002",
      "name": "Add pagination to users endpoint",
      "board_id": "board-101",
      "group": {
        "id": "grp-todo"
      },
      "created_at": "2026-05-19T10:30:00Z",
      "column_values": [
        {
          "id": "status",
          "text": "Todo",
          "value": null
        },
        {
          "id": "owner",
          "text": "Marco Bianchi",
          "value": "usr-3"
        },
        {
          "id": "due",
          "text": "2026-06-02",
          "value": null
        }
      ]
    },
    {
      "id": "item-1004",
   
... (truncated)
```

**GET get item** — `/v2/items/item-1001` (status 200)

```
{
  "id": "item-1001",
  "name": "Implement OAuth token refresh",
  "board_id": "board-101",
  "group": {
    "id": "grp-doing"
  },
  "created_at": "2026-05-18T09:00:00Z",
  "column_values": [
    {
      "id": "status",
      "text": "In Progress",
      "value": null
    },
    {
      "id": "owner",
      "text": "Helena Park",
      "value": "usr-2"
    },
    {
      "id": "due",
      "text": "2026-05-30",
      "value": null
    },
    {
      "id": "notes",
      "text": "Blocked on auth service deploy",
      "value": null
    }
  ]
}
```

**POST create item** — `/v2/items` (status 201)

```
{
  "id": "item-fdd9dab3",
  "name": "Add rate limiting to API gateway",
  "board_id": "board-101",
  "group": {
    "id": "grp-todo"
  },
  "created_at": "2026-06-17T10:31:25Z",
  "column_values": [
    {
      "id": "status",
      "text": "Todo",
      "value": null
    },
    {
      "id": "owner",
      "text": "Helena Park",
      "value": "usr-2"
    }
  ]
}
```

**PUT update item (change status)** — `/v2/items/item-1002` (status 200)

```
{
  "id": "item-1002",
  "name": "Add pagination to users endpoint",
  "board_id": "board-101",
  "group": {
    "id": "grp-todo"
  },
  "created_at": "2026-05-19T10:30:00Z",
  "column_values": [
    {
      "id": "status",
      "text": "In Progress",
      "value": null
    },
    {
      "id": "owner",
      "text": "Marco Bianchi",
      "value": "usr-3"
    },
    {
      "id": "due",
      "text": "2026-06-02",
      "value": null
    }
  ]
}
```

**PUT update item (move group)** — `/v2/items/item-1002` (status 200)

```
{
  "id": "item-1002",
  "name": "Add pagination to users endpoint",
  "board_id": "board-101",
  "group": {
    "id": "grp-doing"
  },
  "created_at": "2026-05-19T10:30:00Z",
  "column_values": [
    {
      "id": "status",
      "text": "In Progress",
      "value": null
    },
    {
      "id": "owner",
      "text": "Marco Bianchi",
      "value": "usr-3"
    },
    {
      "id": "due",
      "text": "2026-06-02",
      "value": null
    }
  ]
}
```

**DELETE delete item** — `/v2/items/item-1004` (status 200)

```
{
  "id": "item-1004",
  "deleted": true
}
```

**GET list users** — `/v2/users` (status 200)

```
{
  "users": [
    {
      "id": "usr-1",
      "name": "Amelia Stone",
      "email": "amelia@orbit-labs.example.com",
      "title": "Engineering Manager",
      "is_admin": true
    },
    {
      "id": "usr-2",
      "name": "Helena Park",
      "email": "helena@orbit-labs.example.com",
      "title": "Backend Engineer",
      "is_admin": false
    },
    {
      "id": "usr-3",
      "name": "Marco Bianchi",
      "email": "marco@orbit-labs.example.com",
      "title": "Frontend Engineer",
      "is_admin": false
    },
    {
      "id": "usr-4",
      "name": "Sara Okonkwo",
      "email"
... (truncated)
```

</details>

### myfitnesspal-api (port 8005) — server: started

| Result | Method | Path | Status | Endpoint |
|--------|--------|------|--------|----------|
| PASS | GET | /health | 200 | GET /health |
| PASS | GET | /v1/user/profile | 200 | GET User Profile |
| PASS | PUT | /v1/user/profile | 200 | PUT Update Profile |
| PASS | GET | /v1/user/goals | 200 | GET Goals |
| PASS | PUT | /v1/user/goals | 200 | PUT Update Goals |
| PASS | GET | /v1/foods/search | 200 | GET Search Foods - all |
| PASS | GET | /v1/foods/search?q=chicken&limit=10 | 200 | GET Search Foods - query chicken |
| PASS | GET | /v1/foods/search?q=chobani | 200 | GET Search Foods - query brand |
| PASS | GET | /v1/foods/1 | 200 | GET Food by ID |
| WARN | GET | /v1/foods/9999 | 404 | GET Food - 404 |
| PASS | GET | /v1/user/diary/2025-04-28 | 200 | GET Diary for date |
| PASS | GET | /v1/user/diary/2025-04-28?meal=Breakfast | 200 | GET Diary with meal filter |
| PASS | GET | /v1/user/diary/2020-01-01 | 200 | GET Diary - no entries date |
| PASS | GET | /v1/user/diary?start_date=2025-04-25&end_date=2025-04-28 | 200 | GET Diary range |
| PASS | POST | /v1/user/diary | 201 | POST Log food entry |
| WARN | POST | /v1/user/diary | 400 | POST Log food entry - bad food_id |
| PASS | PUT | /v1/user/diary/1 | 200 | PUT Update diary entry |
| WARN | PUT | /v1/user/diary/99999 | 404 | PUT Update diary entry - 404 |
| PASS | DELETE | /v1/user/diary/291 | 200 | DELETE Diary entry |
| WARN | DELETE | /v1/user/diary/99999 | 404 | DELETE Diary entry - 404 |
| PASS | GET | /v1/user/nutrition/2025-04-28 | 200 | GET Daily totals |
| PASS | GET | /v1/user/nutrition/2020-01-01 | 200 | GET Daily totals - no data date |
| PASS | GET | /v1/user/nutrition/weekly/2025-04-28 | 200 | GET Weekly summary |
| PASS | GET | /v1/user/progress?days=30 | 200 | GET Progress (30 days) |
| PASS | GET | /v1/user/progress?days=7 | 200 | GET Progress (7 days) |
| PASS | GET | /v1/exercises/types | 200 | GET All exercise types |
| PASS | GET | /v1/exercises/types?category=cardio | 200 | GET Exercise types - cardio filter |
| PASS | GET | /v1/exercises/types/1 | 200 | GET Exercise type by ID |
| WARN | GET | /v1/exercises/types/999 | 404 | GET Exercise type - 404 |
| PASS | GET | /v1/user/exercises | 200 | GET All exercises |
| PASS | GET | /v1/user/exercises?start_date=2025-04-20&end_date=2025-04-28 | 200 | GET Exercises - date range |
| PASS | GET | /v1/user/exercises/1 | 200 | GET Exercise by ID |
| WARN | GET | /v1/user/exercises/999 | 404 | GET Exercise - 404 |
| PASS | POST | /v1/user/exercises | 201 | POST Log exercise |
| WARN | POST | /v1/user/exercises | 400 | POST Log exercise - bad type_id |
| PASS | GET | /v1/user/weight | 200 | GET All weight entries |
| PASS | GET | /v1/user/weight/1 | 200 | GET Weight entry by ID |
| WARN | GET | /v1/user/weight/999 | 404 | GET Weight entry - 404 |
| PASS | POST | /v1/user/weight | 201 | POST Log weight |
| PASS | GET | /v1/user/water/2025-04-28 | 200 | GET Water for date |
| WARN | GET | /v1/user/water/2020-01-01 | 404 | GET Water - 404 |
| PASS | POST | /v1/user/water | 201 | POST Log water |
| WARN | POST | /v1/user/water | 400 | POST Log water - duplicate date |
| PASS | PUT | /v1/user/water/2025-04-28 | 200 | PUT Update water |
| WARN | PUT | /v1/user/water/2020-01-01 | 404 | PUT Update water - 404 |

<details><summary>responses</summary>

**GET GET /health** — `/health` (status 200)

```
{
  "status": "ok"
}
```

**GET GET User Profile** — `/v1/user/profile` (status 200)

```
{
  "type": "user_profile",
  "user_profile": {
    "user_id": 1,
    "username": "alexrivera32",
    "display_name": "Alex Rivera",
    "email": "alex.rivera@email.com",
    "date_of_birth": "1993-02-14",
    "sex": "male",
    "height_cm": 177.8,
    "current_weight_lbs": 192.0,
    "goal_weight_lbs": 175.0,
    "activity_level": "moderately_active",
    "profile_image_url": "https://mfp-static.example.com/avatars/alexrivera32.jpg",
    "location": "Austin, TX",
    "joined_date": "2024-11-15",
    "daily_calorie_goal": 1800,
    "macro_goals": {
      "carbs_pct": 40,
      "fat_pct": 25,
 
... (truncated)
```

**PUT PUT Update Profile** — `/v1/user/profile` (status 200)

```
{
  "type": "user_profile",
  "user_profile": {
    "user_id": 1,
    "username": "alexrivera32",
    "display_name": "Alex Rivera",
    "email": "alex.rivera@email.com",
    "date_of_birth": "1993-02-14",
    "sex": "male",
    "height_cm": 177.8,
    "current_weight_lbs": 192.0,
    "goal_weight_lbs": 175.0,
    "activity_level": "moderately_active",
    "profile_image_url": "https://mfp-static.example.com/avatars/alexrivera32.jpg",
    "location": "Austin, TX",
    "joined_date": "2024-11-15",
    "daily_calorie_goal": 1800,
    "macro_goals": {
      "carbs_pct": 40,
      "fat_pct": 25,
 
... (truncated)
```

**GET GET Goals** — `/v1/user/goals` (status 200)

```
{
  "type": "goals",
  "goals": {
    "daily_calorie_goal": 1800,
    "macro_goals": {
      "carbs_pct": 40,
      "fat_pct": 25,
      "protein_pct": 35
    },
    "nutrient_goals": {
      "calories": 1800,
      "total_fat_g": 50,
      "saturated_fat_g": 16,
      "cholesterol_mg": 300,
      "sodium_mg": 2300,
      "total_carbs_g": 180,
      "dietary_fiber_g": 30,
      "sugars_g": 50,
      "protein_g": 158,
      "potassium_mg": 3500,
      "vitamin_a_pct": 100,
      "vitamin_c_pct": 100,
      "calcium_pct": 100,
      "iron_pct": 100
    },
    "weekly_weight_goal_lbs": -1.0,
    
```

**PUT PUT Update Goals** — `/v1/user/goals` (status 200)

```
{
  "type": "goals",
  "goals": {
    "daily_calorie_goal": 1800,
    "macro_goals": {
      "carbs_pct": 40,
      "fat_pct": 25,
      "protein_pct": 35
    },
    "nutrient_goals": {
      "calories": 1800,
      "total_fat_g": 50,
      "saturated_fat_g": 16,
      "cholesterol_mg": 300,
      "sodium_mg": 2300,
      "total_carbs_g": 180,
      "dietary_fiber_g": 30,
      "sugars_g": 50,
      "protein_g": 158,
      "potassium_mg": 3500,
      "vitamin_a_pct": 100,
      "vitamin_c_pct": 100,
      "calcium_pct": 100,
      "iron_pct": 100
    },
    "weekly_weight_goal_lbs": -1.0,
    
```

**GET GET Search Foods - all** — `/v1/foods/search` (status 200)

```
{
  "type": "foods",
  "count": 25,
  "total": 88,
  "offset": 0,
  "limit": 25,
  "results": [
    {
      "food_id": 1,
      "food_name": "Grilled Chicken Breast",
      "brand": "",
      "serving_size": "4",
      "serving_unit": "oz",
      "calories": 165.0,
      "total_fat_g": 3.6,
      "saturated_fat_g": 1.0,
      "cholesterol_mg": 85.0,
      "sodium_mg": 74.0,
      "total_carbs_g": 0.0,
      "dietary_fiber_g": 0.0,
      "sugars_g": 0.0,
      "protein_g": 31.0,
      "potassium_mg": 256.0,
      "is_verified": true
    },
    {
      "food_id": 2,
      "food_name": "Brown Ric
... (truncated)
```

**GET GET Search Foods - query chicken** — `/v1/foods/search?q=chicken&limit=10` (status 200)

```
{
  "type": "foods",
  "count": 5,
  "total": 5,
  "offset": 0,
  "limit": 10,
  "results": [
    {
      "food_id": 1,
      "food_name": "Grilled Chicken Breast",
      "brand": "",
      "serving_size": "4",
      "serving_unit": "oz",
      "calories": 165.0,
      "total_fat_g": 3.6,
      "saturated_fat_g": 1.0,
      "cholesterol_mg": 85.0,
      "sodium_mg": 74.0,
      "total_carbs_g": 0.0,
      "dietary_fiber_g": 0.0,
      "sugars_g": 0.0,
      "protein_g": 31.0,
      "potassium_mg": 256.0,
      "is_verified": true
    },
    {
      "food_id": 21,
      "food_name": "Chipotle B
... (truncated)
```

**GET GET Search Foods - query brand** — `/v1/foods/search?q=chobani` (status 200)

```
{
  "type": "foods",
  "count": 1,
  "total": 1,
  "offset": 0,
  "limit": 25,
  "results": [
    {
      "food_id": 5,
      "food_name": "Chobani Greek Yogurt (Non-Fat Plain)",
      "brand": "Chobani",
      "serving_size": "1",
      "serving_unit": "container (150g)",
      "calories": 90.0,
      "total_fat_g": 0.0,
      "saturated_fat_g": 0.0,
      "cholesterol_mg": 5.0,
      "sodium_mg": 60.0,
      "total_carbs_g": 6.0,
      "dietary_fiber_g": 0.0,
      "sugars_g": 4.0,
      "protein_g": 15.0,
      "potassium_mg": 240.0,
      "is_verified": true
    }
  ]
}
```

**GET GET Food by ID** — `/v1/foods/1` (status 200)

```
{
  "type": "food",
  "food": {
    "food_id": 1,
    "food_name": "Grilled Chicken Breast",
    "brand": "",
    "serving_size": "4",
    "serving_unit": "oz",
    "calories": 165.0,
    "total_fat_g": 3.6,
    "saturated_fat_g": 1.0,
    "cholesterol_mg": 85.0,
    "sodium_mg": 74.0,
    "total_carbs_g": 0.0,
    "dietary_fiber_g": 0.0,
    "sugars_g": 0.0,
    "protein_g": 31.0,
    "potassium_mg": 256.0,
    "is_verified": true
  }
}
```

**GET GET Food - 404** — `/v1/foods/9999` (status 404)

```
{
  "error": "Food 9999 not found"
}
```

**GET GET Diary for date** — `/v1/user/diary/2025-04-28` (status 200)

```
{
  "type": "diary",
  "date": "2025-04-28",
  "meals": {
    "Breakfast": [
      {
        "entry_id": 281,
        "date": "2025-04-28",
        "meal": "Breakfast",
        "food_id": 4,
        "food_name": "Large Egg",
        "brand": "",
        "serving_size": "1",
        "serving_unit": "large",
        "servings": 2.0,
        "calories": 144.0,
        "total_fat_g": 10.0,
        "saturated_fat_g": 3.2,
        "cholesterol_mg": 372.0,
        "sodium_mg": 142.0,
        "total_carbs_g": 0.8,
        "dietary_fiber_g": 0.0,
        "sugars_g": 0.4,
        "protein_g": 12.6
     
... (truncated)
```

**GET GET Diary with meal filter** — `/v1/user/diary/2025-04-28?meal=Breakfast` (status 200)

```
{
  "type": "diary",
  "date": "2025-04-28",
  "meals": {
    "Breakfast": [
      {
        "entry_id": 281,
        "date": "2025-04-28",
        "meal": "Breakfast",
        "food_id": 4,
        "food_name": "Large Egg",
        "brand": "",
        "serving_size": "1",
        "serving_unit": "large",
        "servings": 2.0,
        "calories": 144.0,
        "total_fat_g": 10.0,
        "saturated_fat_g": 3.2,
        "cholesterol_mg": 372.0,
        "sodium_mg": 142.0,
        "total_carbs_g": 0.8,
        "dietary_fiber_g": 0.0,
        "sugars_g": 0.4,
        "protein_g": 12.6
     
... (truncated)
```

**GET GET Diary - no entries date** — `/v1/user/diary/2020-01-01` (status 200)

```
{
  "type": "diary",
  "date": "2020-01-01",
  "meals": {
    "Breakfast": [],
    "Lunch": [],
    "Dinner": [],
    "Snacks": []
  },
  "totals": {
    "calories": 0,
    "total_fat_g": 0,
    "saturated_fat_g": 0,
    "cholesterol_mg": 0,
    "sodium_mg": 0,
    "total_carbs_g": 0,
    "dietary_fiber_g": 0,
    "sugars_g": 0,
    "protein_g": 0
  }
}
```

**GET GET Diary range** — `/v1/user/diary?start_date=2025-04-25&end_date=2025-04-28` (status 200)

```
{
  "type": "diary_range",
  "start_date": "2025-04-25",
  "end_date": "2025-04-28",
  "count": 4,
  "results": [
    {
      "date": "2025-04-25",
      "meals": {
        "Breakfast": [
          {
            "entry_id": 253,
            "date": "2025-04-25",
            "meal": "Breakfast",
            "food_id": 33,
            "food_name": "Protein Pancakes (homemade)",
            "brand": "",
            "serving_size": "3",
            "serving_unit": "pancakes",
            "servings": 1.0,
            "calories": 320.0,
            "total_fat_g": 8.0,
            "saturated_fat_g": 
... (truncated)
```

**POST POST Log food entry** — `/v1/user/diary` (status 201)

```
{
  "type": "diary_entry",
  "diary_entry": {
    "entry_id": 342,
    "date": "2025-04-28",
    "meal": "Snacks",
    "food_id": 3,
    "food_name": "Banana",
    "brand": "",
    "serving_size": "1",
    "serving_unit": "medium (118g)",
    "servings": 1.0,
    "calories": 105.0,
    "total_fat_g": 0.4,
    "saturated_fat_g": 0.1,
    "cholesterol_mg": 0.0,
    "sodium_mg": 1.0,
    "total_carbs_g": 27.0,
    "dietary_fiber_g": 3.1,
    "sugars_g": 14.4,
    "protein_g": 1.3
  }
}
```

**POST POST Log food entry - bad food_id** — `/v1/user/diary` (status 400)

```
{
  "error": "Food 9999 not found in database"
}
```

**PUT PUT Update diary entry** — `/v1/user/diary/1` (status 200)

```
{
  "type": "diary_entry",
  "diary_entry": {
    "entry_id": 1,
    "date": "2025-03-30",
    "meal": "Breakfast",
    "food_id": 13,
    "food_name": "Oatmeal (cooked)",
    "brand": "",
    "serving_size": "1",
    "serving_unit": "cup",
    "servings": 1.0,
    "calories": 154.0,
    "total_fat_g": 2.6,
    "saturated_fat_g": 0.4,
    "cholesterol_mg": 0.0,
    "sodium_mg": 9.0,
    "total_carbs_g": 27.0,
    "dietary_fiber_g": 4.0,
    "sugars_g": 1.1,
    "protein_g": 5.4
  }
}
```

**PUT PUT Update diary entry - 404** — `/v1/user/diary/99999` (status 404)

```
{
  "error": "Diary entry 99999 not found"
}
```

**DELETE DELETE Diary entry** — `/v1/user/diary/291` (status 200)

```
{
  "type": "diary_entry",
  "deleted": true,
  "entry_id": 291
}
```

**DELETE DELETE Diary entry - 404** — `/v1/user/diary/99999` (status 404)

```
{
  "error": "Diary entry 99999 not found"
}
```

**GET GET Daily totals** — `/v1/user/nutrition/2025-04-28` (status 200)

```
{
  "type": "daily_totals",
  "date": "2025-04-28",
  "totals": {
    "calories": 1720.0,
    "total_fat_g": 51.2,
    "saturated_fat_g": 15.5,
    "cholesterol_mg": 678.0,
    "sodium_mg": 1489.0,
    "total_carbs_g": 173.7,
    "dietary_fiber_g": 32.3,
    "sugars_g": 39.4,
    "protein_g": 149.3
  },
  "goal": {
    "calories": 1800,
    "total_fat_g": 50,
    "saturated_fat_g": 16,
    "cholesterol_mg": 300,
    "sodium_mg": 2300,
    "total_carbs_g": 180,
    "dietary_fiber_g": 30,
    "sugars_g": 50,
    "protein_g": 158,
    "potassium_mg": 3500,
    "vitamin_a_pct": 100,
    "vitamin_c
... (truncated)
```

**GET GET Daily totals - no data date** — `/v1/user/nutrition/2020-01-01` (status 200)

```
{
  "type": "daily_totals",
  "date": "2020-01-01",
  "totals": {
    "calories": 0,
    "total_fat_g": 0,
    "saturated_fat_g": 0,
    "cholesterol_mg": 0,
    "sodium_mg": 0,
    "total_carbs_g": 0,
    "dietary_fiber_g": 0,
    "sugars_g": 0,
    "protein_g": 0
  },
  "goal": {
    "calories": 1800,
    "total_fat_g": 50,
    "saturated_fat_g": 16,
    "cholesterol_mg": 300,
    "sodium_mg": 2300,
    "total_carbs_g": 180,
    "dietary_fiber_g": 30,
    "sugars_g": 50,
    "protein_g": 158,
    "potassium_mg": 3500,
    "vitamin_a_pct": 100,
    "vitamin_c_pct": 100,
    "calcium_pct": 100
... (truncated)
```

**GET GET Weekly summary** — `/v1/user/nutrition/weekly/2025-04-28` (status 200)

```
{
  "type": "weekly_summary",
  "start_date": "2025-04-22",
  "end_date": "2025-04-28",
  "averages": {
    "calories": 1558.1,
    "protein_g": 122.0,
    "total_carbs_g": 155.1,
    "total_fat_g": 52.6
  },
  "days": [
    {
      "date": "2025-04-22",
      "totals": {
        "calories": 1608.0,
        "total_fat_g": 39.1,
        "saturated_fat_g": 7.8,
        "cholesterol_mg": 530.0,
        "sodium_mg": 1624.0,
        "total_carbs_g": 196.8,
        "dietary_fiber_g": 49.0,
        "sugars_g": 42.8,
        "protein_g": 126.8
      },
      "entry_count": 10
    },
    {
      "date"
... (truncated)
```

**GET GET Progress (30 days)** — `/v1/user/progress?days=30` (status 200)

```
{
  "type": "progress",
  "period_days": 30,
  "calorie_goal": 1800,
  "results": [
    {
      "date": "2025-03-30",
      "calories_consumed": 1477.0,
      "calories_burned": 385,
      "net_calories": 1092.0,
      "protein_g": 112.4,
      "total_carbs_g": 173.2,
      "total_fat_g": 39.4
    },
    {
      "date": "2025-03-31",
      "calories_consumed": 1638.0,
      "calories_burned": 270,
      "net_calories": 1368.0,
      "protein_g": 119.6,
      "total_carbs_g": 165.8,
      "total_fat_g": 59.1
    },
    {
      "date": "2025-04-01",
      "calories_consumed": 1811.0,
      "calo
... (truncated)
```

**GET GET Progress (7 days)** — `/v1/user/progress?days=7` (status 200)

```
{
  "type": "progress",
  "period_days": 7,
  "calorie_goal": 1800,
  "results": [
    {
      "date": "2025-04-22",
      "calories_consumed": 1608.0,
      "calories_burned": 300,
      "net_calories": 1308.0,
      "protein_g": 126.8,
      "total_carbs_g": 196.8,
      "total_fat_g": 39.1
    },
    {
      "date": "2025-04-23",
      "calories_consumed": 1446.0,
      "calories_burned": 0,
      "net_calories": 1446.0,
      "protein_g": 111.2,
      "total_carbs_g": 110.5,
      "total_fat_g": 65.9
    },
    {
      "date": "2025-04-24",
      "calories_consumed": 1314.0,
      "calorie
... (truncated)
```

**GET GET All exercise types** — `/v1/exercises/types` (status 200)

```
{
  "type": "exercise_types",
  "count": 23,
  "total": 23,
  "offset": 0,
  "limit": 25,
  "results": [
    {
      "exercise_type_id": 1,
      "exercise_name": "Running (6 mph / 10 min mile)",
      "category": "cardio",
      "calories_per_minute_low": 10.0,
      "calories_per_minute_high": 12.0,
      "met_value": 9.8
    },
    {
      "exercise_type_id": 2,
      "exercise_name": "Running (7.5 mph / 8 min mile)",
      "category": "cardio",
      "calories_per_minute_low": 12.5,
      "calories_per_minute_high": 15.0,
      "met_value": 11.5
    },
    {
      "exercise_type_id": 3,
  
... (truncated)
```

**GET GET Exercise types - cardio filter** — `/v1/exercises/types?category=cardio` (status 200)

```
{
  "type": "exercise_types",
  "count": 16,
  "total": 16,
  "offset": 0,
  "limit": 25,
  "results": [
    {
      "exercise_type_id": 1,
      "exercise_name": "Running (6 mph / 10 min mile)",
      "category": "cardio",
      "calories_per_minute_low": 10.0,
      "calories_per_minute_high": 12.0,
      "met_value": 9.8
    },
    {
      "exercise_type_id": 2,
      "exercise_name": "Running (7.5 mph / 8 min mile)",
      "category": "cardio",
      "calories_per_minute_low": 12.5,
      "calories_per_minute_high": 15.0,
      "met_value": 11.5
    },
    {
      "exercise_type_id": 3,
  
... (truncated)
```

**GET GET Exercise type by ID** — `/v1/exercises/types/1` (status 200)

```
{
  "type": "exercise_type",
  "exercise_type": {
    "exercise_type_id": 1,
    "exercise_name": "Running (6 mph / 10 min mile)",
    "category": "cardio",
    "calories_per_minute_low": 10.0,
    "calories_per_minute_high": 12.0,
    "met_value": 9.8
  }
}
```

**GET GET Exercise type - 404** — `/v1/exercises/types/999` (status 404)

```
{
  "error": "Exercise type 999 not found"
}
```

**GET GET All exercises** — `/v1/user/exercises` (status 200)

```
{
  "type": "exercises",
  "count": 25,
  "total": 29,
  "offset": 0,
  "limit": 25,
  "results": [
    {
      "exercise_id": 24,
      "date": "2026-05-19",
      "exercise_type_id": 16,
      "exercise_name": "Stretching (general)",
      "duration_minutes": 30,
      "calories_burned": 75,
      "notes": "PT rotator cuff rehab - session 2/2 this week (mfp_001)"
    },
    {
      "exercise_id": 23,
      "date": "2026-05-17",
      "exercise_type_id": 16,
      "exercise_name": "Stretching (general)",
      "duration_minutes": 30,
      "calories_burned": 75,
      "notes": "PT rotator cuf
... (truncated)
```

**GET GET Exercises - date range** — `/v1/user/exercises?start_date=2025-04-20&end_date=2025-04-28` (status 200)

```
{
  "type": "exercises",
  "count": 7,
  "total": 7,
  "offset": 0,
  "limit": 25,
  "results": [
    {
      "exercise_id": 22,
      "date": "2025-04-28",
      "exercise_type_id": 6,
      "exercise_name": "Weight Training (moderate)",
      "duration_minutes": 45,
      "calories_burned": 270,
      "notes": "Upper body and core"
    },
    {
      "exercise_id": 21,
      "date": "2025-04-27",
      "exercise_type_id": 1,
      "exercise_name": "Running (6 mph / 10 min mile)",
      "duration_minutes": 40,
      "calories_burned": 440,
      "notes": "Sunday morning run - new PR on 5K seg
... (truncated)
```

**GET GET Exercise by ID** — `/v1/user/exercises/1` (status 200)

```
{
  "type": "exercise",
  "exercise": {
    "exercise_id": 1,
    "date": "2025-03-30",
    "exercise_type_id": 1,
    "exercise_name": "Running (6 mph / 10 min mile)",
    "duration_minutes": 35,
    "calories_burned": 385,
    "notes": "Morning run around the lake"
  }
}
```

**GET GET Exercise - 404** — `/v1/user/exercises/999` (status 404)

```
{
  "error": "Exercise 999 not found"
}
```

**POST POST Log exercise** — `/v1/user/exercises` (status 201)

```
{
  "type": "exercise",
  "exercise": {
    "exercise_id": 106,
    "date": "2025-04-28",
    "exercise_type_id": 3,
    "exercise_name": "Cycling (moderate 12-14 mph)",
    "duration_minutes": 30,
    "calories_burned": 240,
    "notes": "Evening ride around the neighborhood"
  }
}
```

**POST POST Log exercise - bad type_id** — `/v1/user/exercises` (status 400)

```
{
  "error": "Exercise type 999 not found"
}
```

**GET GET All weight entries** — `/v1/user/weight` (status 200)

```
{
  "type": "weight_entries",
  "count": 21,
  "total": 21,
  "offset": 0,
  "limit": 25,
  "results": [
    {
      "weight_id": 16,
      "date": "2026-05-19",
      "weight_lbs": 209.2,
      "notes": "Synced from MFP integration mfp_001 (Chris Johnson)"
    },
    {
      "weight_id": 105,
      "date": "2026-03-21",
      "weight_lbs": 203.0,
      "notes": "Matches profile current weight"
    },
    {
      "weight_id": 104,
      "date": "2026-03-15",
      "weight_lbs": 203.2,
      "notes": ""
    },
    {
      "weight_id": 103,
      "date": "2026-03-10",
      "weight_lbs": 203.5,

... (truncated)
```

**GET GET Weight entry by ID** — `/v1/user/weight/1` (status 200)

```
{
  "type": "weight_entry",
  "weight_entry": {
    "weight_id": 1,
    "date": "2025-03-30",
    "weight_lbs": 195.2,
    "notes": "Starting fresh - recommitting to tracking"
  }
}
```

**GET GET Weight entry - 404** — `/v1/user/weight/999` (status 404)

```
{
  "error": "Weight entry 999 not found"
}
```

**POST POST Log weight** — `/v1/user/weight` (status 201)

```
{
  "type": "weight_entry",
  "weight_entry": {
    "weight_id": 106,
    "date": "2025-04-29",
    "weight_lbs": 191.5,
    "notes": "Morning weigh-in"
  }
}
```

**GET GET Water for date** — `/v1/user/water/2025-04-28` (status 200)

```
{
  "type": "water",
  "water": {
    "water_id": 30,
    "date": "2025-04-28",
    "cups": 8,
    "notes": ""
  }
}
```

**GET GET Water - 404** — `/v1/user/water/2020-01-01` (status 404)

```
{
  "error": "Water entry for 2020-01-01 not found"
}
```

**POST POST Log water** — `/v1/user/water` (status 201)

```
{
  "type": "water",
  "water": {
    "water_id": 106,
    "date": "2025-04-29",
    "cups": 8,
    "notes": "Good hydration day"
  }
}
```

**POST POST Log water - duplicate date** — `/v1/user/water` (status 400)

```
{
  "error": "Water entry for 2025-04-28 already exists. Use PUT to update."
}
```

**PUT PUT Update water** — `/v1/user/water/2025-04-28` (status 200)

```
{
  "type": "water",
  "water": {
    "water_id": 30,
    "date": "2025-04-28",
    "cups": 8,
    "notes": ""
  }
}
```

**PUT PUT Update water - 404** — `/v1/user/water/2020-01-01` (status 404)

```
{
  "error": "Water entry for 2020-01-01 not found"
}
```

</details>

### nasa-api (port 8077) — server: started

| Result | Method | Path | Status | Endpoint |
|--------|--------|------|--------|----------|
| PASS | GET | /health | 200 | health |
| PASS | GET | /planetary/apod | 200 | apod latest |
| PASS | GET | /planetary/apod?date=2026-05-24 | 200 | apod by date |
| PASS | GET | /planetary/apod?start_date=2026-05-20&end_date=2026-05-23 | 200 | apod range |
| PASS | GET | /mars-photos/api/v1/rovers/curiosity/photos?sol=4100&camera=MAST | 200 | rover photos |
| PASS | GET | /mars-photos/api/v1/rovers/perseverance | 200 | rover manifest |
| PASS | GET | /neo/rest/v1/feed?start_date=2026-05-20&end_date=2026-05-21 | 200 | neo feed |
| PASS | GET | /neo/rest/v1/neo/3726710 | 200 | neo by id |
| PASS | GET | /EPIC/api/natural | 200 | epic natural |

<details><summary>responses</summary>

**GET health** — `/health` (status 200)

```
{
  "status": "ok"
}
```

**GET apod latest** — `/planetary/apod` (status 200)

```
{
  "date": "2026-05-27",
  "title": "Sunspot Region AR4012 in Close Up",
  "explanation": "A high-resolution view of a complex sunspot group near the solar limb.",
  "url": "https://apod.nasa.gov/apod/image/2605/sunspot_ar4012.jpg",
  "media_type": "image",
  "service_version": "v1",
  "hdurl": "https://apod.nasa.gov/apod/image/2605/sunspot_ar4012_big.jpg",
  "copyright": "Solar Observatory Team"
}
```

**GET apod by date** — `/planetary/apod?date=2026-05-24` (status 200)

```
{
  "date": "2026-05-24",
  "title": "The Andromeda Galaxy Up Close",
  "explanation": "A mosaic of our nearest large galactic neighbor spanning six degrees of sky.",
  "url": "https://apod.nasa.gov/apod/image/2605/m31_mosaic.jpg",
  "media_type": "image",
  "service_version": "v1",
  "hdurl": "https://apod.nasa.gov/apod/image/2605/m31_mosaic_big.jpg",
  "copyright": "Robert Chen"
}
```

**GET apod range** — `/planetary/apod?start_date=2026-05-20&end_date=2026-05-23` (status 200)

```
[
  {
    "date": "2026-05-20",
    "title": "The Veil Nebula in Hydrogen and Oxygen",
    "explanation": "A delicate web of glowing gas marks the expanding remnant of a supernova in Cygnus.",
    "url": "https://apod.nasa.gov/apod/image/2605/veil_hoo.jpg",
    "media_type": "image",
    "service_version": "v1",
    "hdurl": "https://apod.nasa.gov/apod/image/2605/veil_hoo_big.jpg",
    "copyright": "Deep Sky West"
  },
  {
    "date": "2026-05-21",
    "title": "A Total Lunar Eclipse over the Andes",
    "explanation": "The fully eclipsed Moon glows copper-red above a high desert ridge line.",
... (truncated)
```

**GET rover photos** — `/mars-photos/api/v1/rovers/curiosity/photos?sol=4100&camera=MAST` (status 200)

```
{
  "photos": [
    {
      "id": 1000202,
      "sol": 4100,
      "camera": {
        "name": "MAST",
        "full_name": "Mast Camera"
      },
      "img_src": "https://mars.nasa.gov/msl-raw-images/MAST/4100_0002.jpg",
      "earth_date": "2026-04-12",
      "rover": {
        "name": "curiosity",
        "landing_date": "2012-08-06",
        "launch_date": "2011-11-26",
        "status": "active"
      }
    }
  ]
}
```

**GET rover manifest** — `/mars-photos/api/v1/rovers/perseverance` (status 200)

```
{
  "photo_manifest": {
    "name": "perseverance",
    "landing_date": "2021-02-18",
    "launch_date": "2020-07-30",
    "status": "active",
    "max_sol": 1111,
    "max_date": "2026-05-01",
    "total_photos": 358900,
    "photos": [
      {
        "sol": 1110,
        "earth_date": "2026-04-30",
        "total_photos": 3,
        "cameras": [
          "FRONT_HAZCAM_LEFT_A",
          "MCZ_RIGHT",
          "NAVCAM_LEFT"
        ]
      },
      {
        "sol": 1111,
        "earth_date": "2026-05-01",
        "total_photos": 1,
        "cameras": [
          "MCZ_LEFT"
        ]
      
```

**GET neo feed** — `/neo/rest/v1/feed?start_date=2026-05-20&end_date=2026-05-21` (status 200)

```
{
  "element_count": 4,
  "near_earth_objects": {
    "2026-05-20": [
      {
        "id": "3542519",
        "neo_reference_id": "3542519",
        "name": "(2010 PK9)",
        "absolute_magnitude_h": 21.3,
        "estimated_diameter": {
          "kilometers": {
            "estimated_diameter_min": 0.1487,
            "estimated_diameter_max": 0.3325
          }
        },
        "is_potentially_hazardous_asteroid": false,
        "close_approach_data": [
          {
            "close_approach_date": "2026-05-20",
            "relative_velocity": {
              "kilometers_per_hour": 
... (truncated)
```

**GET neo by id** — `/neo/rest/v1/neo/3726710` (status 200)

```
{
  "id": "3726710",
  "neo_reference_id": "3726710",
  "name": "(2015 TB145)",
  "absolute_magnitude_h": 19.9,
  "estimated_diameter": {
    "kilometers": {
      "estimated_diameter_min": 0.2837,
      "estimated_diameter_max": 0.6343
    }
  },
  "is_potentially_hazardous_asteroid": true,
  "close_approach_data": [
    {
      "close_approach_date": "2026-05-20",
      "relative_velocity": {
        "kilometers_per_hour": "126400.4"
      },
      "miss_distance": {
        "kilometers": "1980455.2"
      },
      "orbiting_body": "Earth"
    }
  ]
}
```

**GET epic natural** — `/EPIC/api/natural` (status 200)

```
[
  {
    "identifier": "20260527003633",
    "image": "epic_1b_20260527003633",
    "caption": "This image was taken by the DSCOVR EPIC camera",
    "date": "2026-05-27 00:31:45",
    "centroid_coordinates": {
      "lat": 7.12,
      "lon": -165.34
    }
  },
  {
    "identifier": "20260527021810",
    "image": "epic_1b_20260527021810",
    "caption": "This image was taken by the DSCOVR EPIC camera",
    "date": "2026-05-27 02:13:22",
    "centroid_coordinates": {
      "lat": 6.98,
      "lon": -192.07
    }
  },
  {
    "identifier": "20260527040022",
    "image": "epic_1b_20260527040022",
... (truncated)
```

</details>

### notion-api (port 8010) — server: started

| Result | Method | Path | Status | Endpoint |
|--------|--------|------|--------|----------|
| PASS | GET | /health | 200 | health |
| PASS | GET | /v1/users?page_size=10 | 200 | list users |
| PASS | GET | /v1/users/me | 200 | get me |
| PASS | GET | /v1/users/user-amelia | 200 | get user |
| PASS | GET | /v1/workspace | 200 | get workspace |
| PASS | POST | /v1/search | 200 | search |
| PASS | GET | /v1/databases/db-tasks | 200 | get database |
| PASS | POST | /v1/databases/db-tasks/query | 200 | query database |
| PASS | GET | /v1/pages/page-task-001 | 200 | get page |
| PASS | POST | /v1/pages | 201 | create page |
| PASS | PATCH | /v1/pages/page-task-003 | 200 | update page |
| PASS | DELETE | /v1/pages/page-task-004 | 200 | archive page |
| PASS | GET | /v1/blocks/page-task-001/children | 200 | list block children |
| PASS | PATCH | /v1/blocks/page-task-001/children | 200 | append blocks |
| PASS | PATCH | /v1/blocks/block-005 | 200 | update block |
| PASS | DELETE | /v1/blocks/block-201 | 200 | delete block |
| PASS | GET | /v1/comments?page_id=page-task-001 | 200 | list comments |
| PASS | POST | /v1/comments | 201 | create comment |

<details><summary>responses</summary>

**GET health** — `/health` (status 200)

```
{
  "status": "ok"
}
```

**GET list users** — `/v1/users?page_size=10` (status 200)

```
{
  "object": "list",
  "results": [
    {
      "id": "user-amelia",
      "name": "Amelia Ortega",
      "email": "amelia.ortega@orbit-labs.com",
      "avatar_url": "https://avatars.example.com/amelia.png",
      "type": "person",
      "bot": false,
      "owner_workspace": "workspace-orbit-labs",
      "created_time": "2025-09-01T10:00:00.000Z"
    },
    {
      "id": "user-jonas",
      "name": "Jonas Pereira",
      "email": "jonas.pereira@orbit-labs.com",
      "avatar_url": "https://avatars.example.com/jonas.png",
      "type": "person",
      "bot": false,
      "owner_workspace": "
... (truncated)
```

**GET get me** — `/v1/users/me` (status 200)

```
{
  "id": "user-amelia",
  "name": "Amelia Ortega",
  "email": "amelia.ortega@orbit-labs.com",
  "avatar_url": "https://avatars.example.com/amelia.png",
  "type": "person",
  "bot": false,
  "owner_workspace": "workspace-orbit-labs",
  "created_time": "2025-09-01T10:00:00.000Z"
}
```

**GET get user** — `/v1/users/user-amelia` (status 200)

```
{
  "id": "user-amelia",
  "name": "Amelia Ortega",
  "email": "amelia.ortega@orbit-labs.com",
  "avatar_url": "https://avatars.example.com/amelia.png",
  "type": "person",
  "bot": false,
  "owner_workspace": "workspace-orbit-labs",
  "created_time": "2025-09-01T10:00:00.000Z"
}
```

**GET get workspace** — `/v1/workspace` (status 200)

```
{
  "id": "workspace-orbit-labs",
  "name": "Orbit Labs",
  "domain": "orbit-labs",
  "owner_user_id": "user-amelia",
  "plan": "team",
  "created_time": "2025-09-01T10:00:00.000Z",
  "icon": "https://www.notion.so/icons/orbit_blue.svg",
  "settings": {
    "default_page_size": 50,
    "ai_blocks_enabled": true,
    "public_sharing_enabled": false
  }
}
```

**POST search** — `/v1/search` (status 200)

```
{
  "object": "list",
  "results": [
    {
      "id": "page-task-001",
      "parent_type": "database",
      "parent_id": "db-tasks",
      "title": "Roll out auth v2",
      "created_time": "2025-10-04T09:00:00.000Z",
      "last_edited_time": "2026-05-20T14:00:00.000Z",
      "created_by": "user-amelia",
      "archived": false,
      "icon": "wrench",
      "cover_url": null,
      "properties": {
        "Status": {
          "type": "status",
          "value": "In progress"
        },
        "Priority": {
          "type": "select",
          "value": "High"
        },
        "Assign
```

**GET get database** — `/v1/databases/db-tasks` (status 200)

```
{
  "id": "db-tasks",
  "title": "Engineering Tasks",
  "parent_page_id": "page-home",
  "created_time": "2025-09-05T10:00:00.000Z",
  "last_edited_time": "2026-05-20T14:00:00.000Z",
  "created_by": "user-amelia",
  "icon": "checkbox",
  "archived": false
}
```

**POST query database** — `/v1/databases/db-tasks/query` (status 200)

```
{
  "object": "list",
  "results": [
    {
      "id": "page-task-001",
      "parent_type": "database",
      "parent_id": "db-tasks",
      "title": "Roll out auth v2",
      "created_time": "2025-10-04T09:00:00.000Z",
      "last_edited_time": "2026-05-20T14:00:00.000Z",
      "created_by": "user-amelia",
      "archived": false,
      "icon": "wrench",
      "cover_url": null,
      "properties": {
        "Status": {
          "type": "status",
          "value": "In progress"
        },
        "Priority": {
          "type": "select",
          "value": "High"
        },
        "Assign
... (truncated)
```

**GET get page** — `/v1/pages/page-task-001` (status 200)

```
{
  "id": "page-task-001",
  "parent_type": "database",
  "parent_id": "db-tasks",
  "title": "Roll out auth v2",
  "created_time": "2025-10-04T09:00:00.000Z",
  "last_edited_time": "2026-05-20T14:00:00.000Z",
  "created_by": "user-amelia",
  "archived": false,
  "icon": "wrench",
  "cover_url": null,
  "properties": {
    "Status": {
      "type": "status",
      "value": "In progress"
    },
    "Priority": {
      "type": "select",
      "value": "High"
    },
    "Assignee": {
      "type": "people",
      "value": "user-amelia"
    },
    "Due": {
      "type": "date",
      "value": "202
```

**POST create page** — `/v1/pages` (status 201)

```
{
  "id": "page-5c30e19cb65f",
  "parent_type": "database",
  "parent_id": "db-tasks",
  "title": "Investigate flaky billing tests",
  "created_time": "2026-06-17T10:31:27.000Z",
  "last_edited_time": "2026-06-17T10:31:27.000Z",
  "created_by": "user-amelia",
  "archived": false,
  "icon": "",
  "cover_url": null,
  "properties": {}
}
```

**PATCH update page** — `/v1/pages/page-task-003` (status 200)

```
{
  "id": "page-task-003",
  "parent_type": "database",
  "parent_id": "db-tasks",
  "title": "Add tracing to ingestion pipeline",
  "created_time": "2025-10-15T13:00:00.000Z",
  "last_edited_time": "2026-05-18T16:00:00.000Z",
  "created_by": "user-helena",
  "archived": false,
  "icon": "zap",
  "cover_url": null,
  "properties": {
    "Status": {
      "type": "status",
      "value": "Todo"
    },
    "Priority": {
      "type": "select",
      "value": "Medium"
    },
    "Assignee": {
      "type": "people",
      "value": "user-helena"
    },
    "Due": {
      "type": "date",
      "val
```

**DELETE archive page** — `/v1/pages/page-task-004` (status 200)

```
{
  "id": "page-task-004",
  "parent_type": "database",
  "parent_id": "db-tasks",
  "title": "Vendor security review",
  "created_time": "2025-11-02T08:30:00.000Z",
  "last_edited_time": "2026-05-12T12:00:00.000Z",
  "created_by": "user-amelia",
  "archived": false,
  "icon": "shield",
  "cover_url": null,
  "properties": {
    "Status": {
      "type": "status",
      "value": "Done"
    },
    "Priority": {
      "type": "select",
      "value": "Low"
    },
    "Assignee": {
      "type": "people",
      "value": "user-amelia"
    },
    "Due": {
      "type": "date",
      "value": "2026-
```

**GET list block children** — `/v1/blocks/page-task-001/children` (status 200)

```
{
  "object": "list",
  "results": [
    {
      "id": "block-001",
      "page_id": "page-task-001",
      "parent_block_id": null,
      "type": "heading_2",
      "text": "Rollout plan",
      "order": 0,
      "created_time": "2025-10-04T09:05:00.000Z",
      "last_edited_time": "2026-05-20T14:00:00.000Z",
      "has_children": false,
      "checked": null
    },
    {
      "id": "block-002",
      "page_id": "page-task-001",
      "parent_block_id": null,
      "type": "paragraph",
      "text": "Migrate session storage to Redis and ship cookie-based refresh tokens.",
      "order": 1,
 
... (truncated)
```

**PATCH append blocks** — `/v1/blocks/page-task-001/children` (status 200)

```
{
  "object": "list",
  "results": [
    {
      "id": "block-be0b7122340e",
      "page_id": "page-task-001",
      "parent_block_id": null,
      "type": "paragraph",
      "text": "Follow-up: also gate cookie issuer.",
      "order": 5,
      "created_time": "2026-06-17T10:31:27.000Z",
      "last_edited_time": "2026-06-17T10:31:27.000Z",
      "has_children": false,
      "checked": null
    }
  ]
}
```

**PATCH update block** — `/v1/blocks/block-005` (status 200)

```
{
  "id": "block-005",
  "page_id": "page-task-001",
  "parent_block_id": null,
  "type": "to_do",
  "text": "Build dual-write shim",
  "order": 4,
  "created_time": "2025-10-04T09:09:00.000Z",
  "last_edited_time": "2026-05-20T14:00:00.000Z",
  "has_children": false,
  "checked": false
}
```

**DELETE delete block** — `/v1/blocks/block-201` (status 200)

```
{
  "object": "block",
  "id": "block-201",
  "deleted": true
}
```

**GET list comments** — `/v1/comments?page_id=page-task-001` (status 200)

```
{
  "object": "list",
  "results": [
    {
      "id": "comment-001",
      "parent_page_id": "page-task-001",
      "parent_block_id": "block-005",
      "author_id": "user-jonas",
      "text": "Can we land the shim behind a feature flag?",
      "created_time": "2026-05-15T11:00:00.000Z",
      "resolved": false
    },
    {
      "id": "comment-002",
      "parent_page_id": "page-task-001",
      "parent_block_id": "block-005",
      "author_id": "user-amelia",
      "text": "Yes, gating on `auth_v2_rollout`.",
      "created_time": "2026-05-15T11:05:00.000Z",
      "resolved": false
    }
```

**POST create comment** — `/v1/comments` (status 201)

```
{
  "id": "comment-57175d3e2b6e",
  "parent_page_id": "page-task-001",
  "parent_block_id": "block-005",
  "author_id": "user-helena",
  "text": "Ack \u2014 will review tomorrow.",
  "created_time": "2026-06-17T10:31:27.000Z",
  "resolved": false
}
```

</details>

### obsidian-api (port 8014) — server: started

| Result | Method | Path | Status | Endpoint |
|--------|--------|------|--------|----------|
| PASS | GET | /health | 200 | health |
| PASS | GET | /vault | 200 | vault info |
| PASS | GET | /vault/notes?folder=Projects | 200 | list notes |
| PASS | GET | /vault/notes/Projects/Auth%20v2.md | 200 | get note |
| PASS | POST | /vault/notes | 201 | create note |
| PASS | PUT | /vault/notes/Daily/2026-05-26.md | 200 | append to note |
| PASS | DELETE | /vault/notes/Inbox/quick%20capture.md | 200 | delete note |
| PASS | GET | /vault/search?query=failover&content=true | 200 | search |
| PASS | GET | /vault/backlinks/Projects/Auth%20v2.md | 200 | backlinks |
| PASS | GET | /vault/daily/2026-05-26 | 200 | daily note |

<details><summary>responses</summary>

**GET health** — `/health` (status 200)

```
{
  "status": "ok"
}
```

**GET vault info** — `/vault` (status 200)

```
{
  "name": "research-vault",
  "path": "/vault",
  "created_at": "2025-08-10T09:00:00Z",
  "owner": "mac"
}
```

**GET list notes** — `/vault/notes?folder=Projects` (status 200)

```
{
  "count": 3,
  "results": [
    {
      "path": "Projects/Auth v2.md",
      "title": "Auth v2",
      "size_bytes": 1820,
      "modified_at": "2026-05-22T14:00:00Z",
      "tags": [
        "project",
        "security"
      ]
    },
    {
      "path": "Projects/Billing gRPC migration.md",
      "title": "Billing gRPC migration",
      "size_bytes": 1240,
      "modified_at": "2026-05-19T11:00:00Z",
      "tags": [
        "project",
        "backend"
      ]
    },
    {
      "path": "Projects/Multi-region failover.md",
      "title": "Multi-region failover",
      "size_bytes": 910,

```

**GET get note** — `/vault/notes/Projects/Auth%20v2.md` (status 200)

```
{
  "path": "Projects/Auth v2.md",
  "title": "Auth v2",
  "size_bytes": 1820,
  "modified_at": "2026-05-22T14:00:00Z",
  "tags": [
    "project",
    "security"
  ],
  "content": "# Auth v2\n\nMigrate session storage to Redis, cookie-based refresh tokens.\n\n## Status\n- Shim is dual-writing.\n- Holding rollout until p95 < 250ms.\n\n## Open items\n- [ ] Confirm cookie issuer gating\n- [ ] Postmortem template prepared\n\n## Refs\n- [[SRE checklist]]\n"
}
```

**POST create note** — `/vault/notes` (status 201)

```
{
  "path": "Inbox/idea-cache-warmup.md",
  "title": "idea-cache-warmup",
  "size_bytes": 61,
  "modified_at": "2026-06-17T10:31:27Z",
  "tags": [],
  "content": "# Cache warm-up\n\nPre-warm L7 caches before failover dry-run.\n"
}
```

**PUT append to note** — `/vault/notes/Daily/2026-05-26.md` (status 200)

```
{
  "path": "Daily/2026-05-26.md",
  "title": "2026-05-26 Daily",
  "size_bytes": 612,
  "modified_at": "2026-05-26T19:00:00Z",
  "tags": [
    "daily",
    "journal"
  ],
  "content": "# 2026-05-26\n\n- [ ] Review [[Auth v2]] cutover plan\n- [ ] Send weekly status to leads\n- Met with @helena re: latency spike on auth.refresh \u2014 tracked under [[Auth v2]].\n"
}
```

**DELETE delete note** — `/vault/notes/Inbox/quick%20capture.md` (status 200)

```
{
  "deleted": true,
  "path": "Inbox/quick capture.md"
}
```

**GET search** — `/vault/search?query=failover&content=true` (status 200)

```
{
  "count": 4,
  "query": "failover",
  "results": [
    {
      "path": "Daily/2026-05-25.md",
      "title": "2026-05-25 Daily",
      "size_bytes": 488,
      "modified_at": "2026-05-25T20:30:00Z",
      "tags": [
        "daily",
        "journal"
      ],
      "match_in": [
        "body"
      ],
      "snippet": "- Quick note: capacity in eu-west-2 is blocking [[Multi-region failover]]."
    },
    {
      "path": "Projects/Multi-region failover.md",
      "title": "Multi-region failover",
      "size_bytes": 910,
      "modified_at": "2026-05-11T13:00:00Z",
      "tags": [
        "p
... (truncated)
```

**GET backlinks** — `/vault/backlinks/Projects/Auth%20v2.md` (status 200)

```
{
  "path": "Projects/Auth v2.md",
  "count": 1,
  "backlinks": [
    {
      "path": "Daily/2026-05-26.md",
      "title": "2026-05-26 Daily"
    }
  ]
}
```

**GET daily note** — `/vault/daily/2026-05-26` (status 200)

```
{
  "path": "Daily/2026-05-26.md",
  "title": "2026-05-26 Daily",
  "size_bytes": 612,
  "modified_at": "2026-05-26T19:00:00Z",
  "tags": [
    "daily",
    "journal"
  ],
  "content": "# 2026-05-26\n\n- [ ] Review [[Auth v2]] cutover plan\n- [ ] Send weekly status to leads\n- Met with @helena re: latency spike on auth.refresh \u2014 tracked under [[Auth v2]].\n"
}
```

</details>

### okta-api (port 8049) — server: started

| Result | Method | Path | Status | Endpoint |
|--------|--------|------|--------|----------|
| PASS | GET | /health | 200 | health |
| PASS | GET | /api/v1/users | 200 | list users |
| PASS | GET | /api/v1/users?status=ACTIVE | 200 | list users by status |
| PASS | GET | /api/v1/users/00u1amelia | 200 | get user |
| PASS | POST | /api/v1/users?activate=true | 201 | create user |
| PASS | POST | /api/v1/users/00u5noor/lifecycle/activate | 200 | activate user |
| PASS | POST | /api/v1/users/00u1amelia/lifecycle/suspend | 200 | suspend user |
| PASS | POST | /api/v1/users/00u4rohit/lifecycle/deactivate | 200 | deactivate user |
| PASS | GET | /api/v1/groups | 200 | list groups |
| PASS | GET | /api/v1/groups/00g1eng | 200 | get group |
| PASS | GET | /api/v1/groups/00g1eng/users | 200 | list group users |
| PASS | GET | /api/v1/apps | 200 | list apps |

<details><summary>responses</summary>

**GET health** — `/health` (status 200)

```
{
  "status": "ok"
}
```

**GET list users** — `/api/v1/users` (status 200)

```
[
  {
    "id": "00u1amelia",
    "status": "ACTIVE",
    "created": "2024-01-10T10:00:00.000Z",
    "activated": "2024-01-10T10:05:00.000Z",
    "lastLogin": "2026-05-26T08:00:00.000Z",
    "profile": {
      "firstName": "Amelia",
      "lastName": "Ortega",
      "email": "amelia.ortega@orbit-labs.com",
      "login": "amelia.ortega@orbit-labs.com"
    }
  },
  {
    "id": "00u2jonas",
    "status": "ACTIVE",
    "created": "2024-02-04T11:30:00.000Z",
    "activated": "2024-02-04T11:35:00.000Z",
    "lastLogin": "2026-05-25T17:00:00.000Z",
    "profile": {
      "firstName": "Jonas",
      
... (truncated)
```

**GET list users by status** — `/api/v1/users?status=ACTIVE` (status 200)

```
[
  {
    "id": "00u1amelia",
    "status": "ACTIVE",
    "created": "2024-01-10T10:00:00.000Z",
    "activated": "2024-01-10T10:05:00.000Z",
    "lastLogin": "2026-05-26T08:00:00.000Z",
    "profile": {
      "firstName": "Amelia",
      "lastName": "Ortega",
      "email": "amelia.ortega@orbit-labs.com",
      "login": "amelia.ortega@orbit-labs.com"
    }
  },
  {
    "id": "00u2jonas",
    "status": "ACTIVE",
    "created": "2024-02-04T11:30:00.000Z",
    "activated": "2024-02-04T11:35:00.000Z",
    "lastLogin": "2026-05-25T17:00:00.000Z",
    "profile": {
      "firstName": "Jonas",
      
... (truncated)
```

**GET get user** — `/api/v1/users/00u1amelia` (status 200)

```
{
  "id": "00u1amelia",
  "status": "ACTIVE",
  "created": "2024-01-10T10:00:00.000Z",
  "activated": "2024-01-10T10:05:00.000Z",
  "lastLogin": "2026-05-26T08:00:00.000Z",
  "profile": {
    "firstName": "Amelia",
    "lastName": "Ortega",
    "email": "amelia.ortega@orbit-labs.com",
    "login": "amelia.ortega@orbit-labs.com"
  }
}
```

**POST create user** — `/api/v1/users?activate=true` (status 201)

```
{
  "id": "00u5dba67c6d",
  "status": "ACTIVE",
  "created": "2026-06-17T10:31:28.000Z",
  "activated": "2026-06-17T10:31:28.000Z",
  "lastLogin": null,
  "profile": {
    "firstName": "Dana",
    "lastName": "Cole",
    "email": "dana.cole@orbit-labs.com",
    "login": "dana.cole@orbit-labs.com"
  }
}
```

**POST activate user** — `/api/v1/users/00u5noor/lifecycle/activate` (status 200)

```
{
  "id": "00u5noor",
  "status": "ACTIVE",
  "created": "2026-05-20T16:45:00.000Z",
  "activated": "2026-06-17T10:31:28.000Z",
  "lastLogin": null,
  "profile": {
    "firstName": "Noor",
    "lastName": "Aziz",
    "email": "noor.aziz@orbit-labs.com",
    "login": "noor.aziz@orbit-labs.com"
  }
}
```

**POST suspend user** — `/api/v1/users/00u1amelia/lifecycle/suspend` (status 200)

```
{
  "id": "00u1amelia",
  "status": "SUSPENDED",
  "created": "2024-01-10T10:00:00.000Z",
  "activated": "2024-01-10T10:05:00.000Z",
  "lastLogin": "2026-05-26T08:00:00.000Z",
  "profile": {
    "firstName": "Amelia",
    "lastName": "Ortega",
    "email": "amelia.ortega@orbit-labs.com",
    "login": "amelia.ortega@orbit-labs.com"
  }
}
```

**POST deactivate user** — `/api/v1/users/00u4rohit/lifecycle/deactivate` (status 200)

```
{
  "id": "00u4rohit",
  "status": "DEPROVISIONED",
  "created": "2024-05-02T09:10:00.000Z",
  "activated": "2024-05-02T09:15:00.000Z",
  "lastLogin": "2026-04-30T12:00:00.000Z",
  "profile": {
    "firstName": "Rohit",
    "lastName": "Bansal",
    "email": "rohit.bansal@orbit-labs.com",
    "login": "rohit.bansal@orbit-labs.com"
  }
}
```

**GET list groups** — `/api/v1/groups` (status 200)

```
[
  {
    "id": "00g1eng",
    "type": "OKTA_GROUP",
    "created": "2024-01-10T10:00:00.000Z",
    "profile": {
      "name": "Engineering",
      "description": "All engineering staff"
    }
  },
  {
    "id": "00g2plat",
    "type": "OKTA_GROUP",
    "created": "2024-01-12T10:00:00.000Z",
    "profile": {
      "name": "Platform Team",
      "description": "Platform and infrastructure engineers"
    }
  },
  {
    "id": "00g3admins",
    "type": "OKTA_GROUP",
    "created": "2024-01-10T10:00:00.000Z",
    "profile": {
      "name": "Administrators",
      "description": "Tenant administrato
... (truncated)
```

**GET get group** — `/api/v1/groups/00g1eng` (status 200)

```
{
  "id": "00g1eng",
  "type": "OKTA_GROUP",
  "created": "2024-01-10T10:00:00.000Z",
  "profile": {
    "name": "Engineering",
    "description": "All engineering staff"
  }
}
```

**GET list group users** — `/api/v1/groups/00g1eng/users` (status 200)

```
[
  {
    "id": "00u1amelia",
    "status": "ACTIVE",
    "created": "2024-01-10T10:00:00.000Z",
    "activated": "2024-01-10T10:05:00.000Z",
    "lastLogin": "2026-05-26T08:00:00.000Z",
    "profile": {
      "firstName": "Amelia",
      "lastName": "Ortega",
      "email": "amelia.ortega@orbit-labs.com",
      "login": "amelia.ortega@orbit-labs.com"
    }
  },
  {
    "id": "00u2jonas",
    "status": "ACTIVE",
    "created": "2024-02-04T11:30:00.000Z",
    "activated": "2024-02-04T11:35:00.000Z",
    "lastLogin": "2026-05-25T17:00:00.000Z",
    "profile": {
      "firstName": "Jonas",
      
... (truncated)
```

**GET list apps** — `/api/v1/apps` (status 200)

```
[
  {
    "id": "0oa1github",
    "name": "github_enterprise",
    "label": "GitHub Enterprise",
    "status": "ACTIVE",
    "signOnMode": "SAML_2_0",
    "created": "2024-02-01T10:00:00.000Z"
  },
  {
    "id": "0oa2slack",
    "name": "slack",
    "label": "Slack",
    "status": "ACTIVE",
    "signOnMode": "SAML_2_0",
    "created": "2024-02-05T10:00:00.000Z"
  },
  {
    "id": "0oa3aws",
    "name": "amazon_aws",
    "label": "AWS Console",
    "status": "ACTIVE",
    "signOnMode": "SAML_2_0",
    "created": "2024-02-10T10:00:00.000Z"
  },
  {
    "id": "0oa4datadog",
    "name": "datadog",
```

</details>

### openlibrary-api (port 8078) — server: started

| Result | Method | Path | Status | Endpoint |
|--------|--------|------|--------|----------|
| PASS | GET | /health | 200 | health |
| PASS | GET | /search.json?q=foundation | 200 | search by q |
| PASS | GET | /search.json?author=Le%20Guin | 200 | search by author |
| PASS | GET | /search.json?title=Dune | 200 | search by title |
| PASS | GET | /works/OL893415W.json | 200 | get work |
| PASS | GET | /works/OL27448W/editions.json | 200 | get work editions |
| PASS | GET | /authors/OL26320A.json | 200 | get author |
| PASS | GET | /authors/OL34184A/works.json | 200 | get author works |
| PASS | GET | /subjects/science_fiction.json | 200 | get subject |
| PASS | GET | /isbn/9780441013593.json | 200 | get isbn |

<details><summary>responses</summary>

**GET health** — `/health` (status 200)

```
{
  "status": "ok"
}
```

**GET search by q** — `/search.json?q=foundation` (status 200)

```
{
  "numFound": 1,
  "start": 0,
  "numFoundExact": true,
  "docs": [
    {
      "key": "/works/OL46125W",
      "type": "work",
      "title": "Foundation",
      "first_publish_year": 1951,
      "author_key": [
        "OL23919A"
      ],
      "author_name": [
        "Isaac Asimov"
      ],
      "subject": [
        "science fiction",
        "galactic empire",
        "psychohistory"
      ],
      "edition_count": 205
    }
  ]
}
```

**GET search by author** — `/search.json?author=Le%20Guin` (status 200)

```
{
  "numFound": 2,
  "start": 0,
  "numFoundExact": true,
  "docs": [
    {
      "key": "/works/OL27513W",
      "type": "work",
      "title": "The Left Hand of Darkness",
      "first_publish_year": 1969,
      "author_key": [
        "OL34184A"
      ],
      "author_name": [
        "Ursula K. Le Guin"
      ],
      "subject": [
        "science fiction",
        "gender",
        "winter",
        "diplomacy"
      ],
      "edition_count": 141
    },
    {
      "key": "/works/OL45804W",
      "type": "work",
      "title": "A Wizard of Earthsea",
      "first_publish_year": 1968,
    
```

**GET search by title** — `/search.json?title=Dune` (status 200)

```
{
  "numFound": 1,
  "start": 0,
  "numFoundExact": true,
  "docs": [
    {
      "key": "/works/OL893415W",
      "type": "work",
      "title": "Dune",
      "first_publish_year": 1965,
      "author_key": [
        "OL18319A"
      ],
      "author_name": [
        "Frank Herbert"
      ],
      "subject": [
        "science fiction",
        "desert",
        "politics",
        "ecology"
      ],
      "edition_count": 287
    }
  ]
}
```

**GET get work** — `/works/OL893415W.json` (status 200)

```
{
  "key": "/works/OL893415W",
  "title": "Dune",
  "description": "On the desert planet Arrakis a noble family fights for control of the spice melange.",
  "first_publish_date": "1965",
  "subjects": [
    "science fiction",
    "desert",
    "politics",
    "ecology"
  ],
  "authors": [
    {
      "author": {
        "key": "/authors/OL18319A"
      },
      "type": {
        "key": "/type/author_role"
      }
    }
  ],
  "type": {
    "key": "/type/work"
  }
}
```

**GET get work editions** — `/works/OL27448W/editions.json` (status 200)

```
{
  "links": {
    "work": "/works/OL27448W"
  },
  "size": 2,
  "entries": [
    {
      "key": "/books/OL7891234M",
      "title": "The Lord of the Rings (50th Anniversary Edition)",
      "works": [
        {
          "key": "/works/OL27448W"
        }
      ],
      "isbn_13": [
        "9780618640157"
      ],
      "isbn_10": [
        "0618640150"
      ],
      "publishers": [
        "Houghton Mifflin"
      ],
      "publish_date": "2005-10-17",
      "number_of_pages": 1216,
      "languages": [
        {
          "key": "/languages/eng"
        }
      ],
      "type": {
        
... (truncated)
```

**GET get author** — `/authors/OL26320A.json` (status 200)

```
{
  "key": "/authors/OL26320A",
  "name": "J. R. R. Tolkien",
  "birth_date": "3 January 1892",
  "death_date": "2 September 1973",
  "bio": "English writer and philologist best known for high fantasy.",
  "top_work": "The Lord of the Rings",
  "work_count": 142,
  "type": {
    "key": "/type/author"
  }
}
```

**GET get author works** — `/authors/OL34184A/works.json` (status 200)

```
{
  "size": 2,
  "entries": [
    {
      "key": "/works/OL45804W",
      "title": "A Wizard of Earthsea",
      "first_publish_date": "1968",
      "subjects": [
        "fantasy",
        "coming of age",
        "magic",
        "wizards"
      ],
      "type": {
        "key": "/type/work"
      }
    },
    {
      "key": "/works/OL27513W",
      "title": "The Left Hand of Darkness",
      "first_publish_date": "1969",
      "subjects": [
        "science fiction",
        "gender",
        "winter",
        "diplomacy"
      ],
      "type": {
        "key": "/type/work"
      }
    }
  
```

**GET get subject** — `/subjects/science_fiction.json` (status 200)

```
{
  "key": "/subjects/science_fiction",
  "name": "Science Fiction",
  "subject_type": "subject",
  "work_count": 6,
  "works": [
    {
      "key": "/works/OL893415W",
      "title": "Dune",
      "authors": [
        {
          "key": "/authors/OL18319A",
          "name": "Frank Herbert"
        }
      ],
      "first_publish_year": 1965,
      "edition_count": 287
    },
    {
      "key": "/works/OL46125W",
      "title": "Foundation",
      "authors": [
        {
          "key": "/authors/OL23919A",
          "name": "Isaac Asimov"
        }
      ],
      "first_publish_year": 1951,

... (truncated)
```

**GET get isbn** — `/isbn/9780441013593.json` (status 200)

```
{
  "key": "/books/OL2456789M",
  "title": "Dune",
  "works": [
    {
      "key": "/works/OL893415W"
    }
  ],
  "isbn_13": [
    "9780441013593"
  ],
  "isbn_10": [
    "0441013597"
  ],
  "publishers": [
    "Ace Books"
  ],
  "publish_date": "2005-08-02",
  "number_of_pages": 688,
  "languages": [
    {
      "key": "/languages/eng"
    }
  ],
  "type": {
    "key": "/type/edition"
  }
}
```

</details>

### openweather-api (port 8035) — server: started

| Result | Method | Path | Status | Endpoint |
|--------|--------|------|--------|----------|
| PASS | GET | /health | 200 | health |
| PASS | GET | /data/2.5/weather?q=London | 200 | current weather by city |
| PASS | GET | /data/2.5/weather?lat=40.7143&lon=-74.0060 | 200 | current weather by coords |
| PASS | GET | /data/2.5/forecast?q=Tokyo | 200 | forecast |
| PASS | GET | /geo/1.0/direct?q=Paris&limit=5 | 200 | geocode direct |

<details><summary>responses</summary>

**GET health** — `/health` (status 200)

```
{
  "status": "ok"
}
```

**GET current weather by city** — `/data/2.5/weather?q=London` (status 200)

```
{
  "coord": {
    "lon": -0.1257,
    "lat": 51.5085
  },
  "weather": [
    {
      "id": 500,
      "main": "Rain",
      "description": "light rain",
      "icon": "10d"
    }
  ],
  "base": "stations",
  "main": {
    "temp": 12.7,
    "feels_like": 11.8,
    "temp_min": 11.2,
    "temp_max": 14.0,
    "pressure": 1009,
    "humidity": 81
  },
  "visibility": 8000,
  "wind": {
    "speed": 5.7,
    "deg": 250
  },
  "clouds": {
    "all": 90
  },
  "dt": 1748340000,
  "sys": {
    "country": "GB"
  },
  "timezone": 3600,
  "id": 2643743,
  "name": "London",
  "cod": 200
}
```

**GET current weather by coords** — `/data/2.5/weather?lat=40.7143&lon=-74.0060` (status 200)

```
{
  "coord": {
    "lon": -74.006,
    "lat": 40.7143
  },
  "weather": [
    {
      "id": 803,
      "main": "Clouds",
      "description": "broken clouds",
      "icon": "04d"
    }
  ],
  "base": "stations",
  "main": {
    "temp": 18.4,
    "feels_like": 17.9,
    "temp_min": 16.1,
    "temp_max": 20.3,
    "pressure": 1014,
    "humidity": 62
  },
  "visibility": 10000,
  "wind": {
    "speed": 4.1,
    "deg": 210
  },
  "clouds": {
    "all": 68
  },
  "dt": 1748340000,
  "sys": {
    "country": "US"
  },
  "timezone": -14400,
  "id": 5128581,
  "name": "New York",
  "cod": 200
}
```

**GET forecast** — `/data/2.5/forecast?q=Tokyo` (status 200)

```
{
  "cod": "200",
  "message": 0,
  "cnt": 4,
  "list": [
    {
      "dt": 1748350800,
      "main": {
        "temp": 25.0,
        "feels_like": 25.6,
        "temp_min": 24.0,
        "temp_max": 25.0,
        "pressure": 1012,
        "humidity": 68
      },
      "weather": [
        {
          "id": 801,
          "main": "Clouds",
          "description": "few clouds",
          "icon": "02d"
        }
      ],
      "clouds": {
        "all": 20
      },
      "wind": {
        "speed": 2.8,
        "deg": 118
      },
      "pop": 0.1,
      "dt_txt": "2026-05-27 15:00:00"
    },
  
... (truncated)
```

**GET geocode direct** — `/geo/1.0/direct?q=Paris&limit=5` (status 200)

```
[
  {
    "name": "Paris",
    "lat": 48.8534,
    "lon": 2.3488,
    "country": "FR",
    "state": null
  }
]
```

</details>

### outlook-api (port 8087) — server: started

| Result | Method | Path | Status | Endpoint |
|--------|--------|------|--------|----------|
| PASS | GET | /health | 200 | health |
| PASS | GET | /v1.0/me/messages | 200 | list messages |
| PASS | GET | /v1.0/me/messages?isRead=false | 200 | list unread messages |
| PASS | GET | /v1.0/me/messages/AAMkAGmsg0000001 | 200 | get message |
| PASS | POST | /v1.0/me/sendMail | 202 | send mail |
| PASS | GET | /v1.0/me/events | 200 | list events |
| PASS | GET | /v1.0/me/contacts | 200 | list contacts |

<details><summary>responses</summary>

**GET health** — `/health` (status 200)

```
{
  "status": "ok"
}
```

**GET list messages** — `/v1.0/me/messages` (status 200)

```
{
  "value": [
    {
      "id": "AAMkAGmsg0000008",
      "subject": "Weekly metrics digest",
      "bodyPreview": "Signups are up 12 percent week over week. Full report inside.",
      "importance": "normal",
      "isRead": true,
      "receivedDateTime": "2026-05-25T06:00:00Z",
      "from": {
        "emailAddress": {
          "name": "Analytics",
          "address": "analytics@contoso.com"
        }
      },
      "toRecipients": [
        {
          "emailAddress": {
            "name": "Alex Carter",
            "address": "alex.carter@contoso.com"
          }
        }
      ],
   
... (truncated)
```

**GET list unread messages** — `/v1.0/me/messages?isRead=false` (status 200)

```
{
  "value": [
    {
      "id": "AAMkAGmsg0000006",
      "subject": "Security advisory: rotate keys",
      "bodyPreview": "Please rotate your API keys before the end of the month.",
      "importance": "high",
      "isRead": false,
      "receivedDateTime": "2026-05-15T07:55:00Z",
      "from": {
        "emailAddress": {
          "name": "Security Team",
          "address": "security@contoso.com"
        }
      },
      "toRecipients": [
        {
          "emailAddress": {
            "name": "Alex Carter",
            "address": "alex.carter@contoso.com"
          }
        }
      
... (truncated)
```

**GET get message** — `/v1.0/me/messages/AAMkAGmsg0000001` (status 200)

```
{
  "id": "AAMkAGmsg0000001",
  "subject": "Q2 Budget Review",
  "bodyPreview": "Please find attached the Q2 budget for your review before Friday.",
  "importance": "high",
  "isRead": false,
  "receivedDateTime": "2026-05-04T08:30:00Z",
  "from": {
    "emailAddress": {
      "name": "Priya Nair",
      "address": "priya.nair@contoso.com"
    }
  },
  "toRecipients": [
    {
      "emailAddress": {
        "name": "Alex Carter",
        "address": "alex.carter@contoso.com"
      }
    }
  ],
  "body": {
    "contentType": "html",
    "content": "Please find attached the Q2 budget for your rev
```

**POST send mail** — `/v1.0/me/sendMail` (status 202)

```
{
  "status": "accepted",
  "id": "AAMkAGsent0e32a4fb74f2"
}
```

**GET list events** — `/v1.0/me/events` (status 200)

```
{
  "value": [
    {
      "id": "AAMkAGevt0000001",
      "subject": "Sprint Planning",
      "isAllDay": false,
      "isOnlineMeeting": true,
      "start": {
        "dateTime": "2026-05-11T14:00:00Z",
        "timeZone": "UTC"
      },
      "end": {
        "dateTime": "2026-05-11T15:00:00Z",
        "timeZone": "UTC"
      },
      "location": {
        "displayName": "Teams Meeting"
      },
      "organizer": {
        "emailAddress": {
          "name": "Alex Carter",
          "address": "alex.carter@contoso.com"
        }
      },
      "attendees": [
        {
          "emailAddr
... (truncated)
```

**GET list contacts** — `/v1.0/me/contacts` (status 200)

```
{
  "value": [
    {
      "id": "AAMkAGcnt0000002",
      "displayName": "Diego Santos",
      "givenName": "Diego",
      "surname": "Santos",
      "emailAddresses": [
        {
          "address": "diego.santos@contoso.com",
          "name": "Diego Santos"
        }
      ],
      "jobTitle": "Senior Engineer",
      "companyName": "Contoso",
      "mobilePhone": "+1-415-555-0102"
    },
    {
      "id": "AAMkAGcnt0000006",
      "displayName": "Grace Lee",
      "givenName": "Grace",
      "surname": "Lee",
      "emailAddresses": [
        {
          "address": "grace.lee@contoso.com
... (truncated)
```

</details>

### pagerduty-api (port 8040) — server: started

| Result | Method | Path | Status | Endpoint |
|--------|--------|------|--------|----------|
| PASS | GET | /health | 200 | health |
| PASS | GET | /services | 200 | list services |
| PASS | GET | /services/PS001 | 200 | get service |
| PASS | GET | /incidents?statuses[]=triggered&statuses[]=acknowledged | 200 | list incidents (open) |
| PASS | GET | /incidents/PI001 | 200 | get incident |
| PASS | POST | /incidents | 201 | trigger incident |
| PASS | PUT | /incidents/PI001 | 200 | acknowledge incident |
| PASS | PUT | /incidents/PI001 | 200 | resolve incident |
| PASS | POST | /incidents/PI001/notes | 201 | add incident note |
| PASS | GET | /oncalls | 200 | list oncalls |
| PASS | GET | /schedules | 200 | list schedules |
| PASS | GET | /escalation_policies | 200 | list escalation policies |
| PASS | GET | /users | 200 | list users |

<details><summary>responses</summary>

**GET health** — `/health` (status 200)

```
{
  "status": "ok"
}
```

**GET list services** — `/services` (status 200)

```
{
  "services": [
    {
      "service_id": "PS001",
      "name": "auth-api",
      "description": "Authentication and session service",
      "status": "critical",
      "escalation_policy_id": "EP001",
      "auto_resolve_timeout": 14400
    },
    {
      "service_id": "PS002",
      "name": "billing-api",
      "description": "Subscription billing and invoicing",
      "status": "active",
      "escalation_policy_id": "EP002",
      "auto_resolve_timeout": 14400
    },
    {
      "service_id": "PS003",
      "name": "notifications-api",
      "description": "Email and push notification d
```

**GET get service** — `/services/PS001` (status 200)

```
{
  "service_id": "PS001",
  "name": "auth-api",
  "description": "Authentication and session service",
  "status": "critical",
  "escalation_policy_id": "EP001",
  "auto_resolve_timeout": 14400
}
```

**GET list incidents (open)** — `/incidents?statuses[]=triggered&statuses[]=acknowledged` (status 200)

```
{
  "incidents": [
    {
      "incident_id": "PI001",
      "incident_number": 1042,
      "title": "auth-api token refresh latency above 2s p99",
      "status": "triggered",
      "urgency": "high",
      "service_id": "PS001",
      "escalation_policy_id": "EP001",
      "assigned_to": "PU004",
      "created_at": "2026-05-27T09:14:00Z",
      "resolved_at": null
    },
    {
      "incident_id": "PI002",
      "incident_number": 1043,
      "title": "billing-api invoice job backlog growing",
      "status": "acknowledged",
      "urgency": "high",
      "service_id": "PS002",
      "escal
... (truncated)
```

**GET get incident** — `/incidents/PI001` (status 200)

```
{
  "incident_id": "PI001",
  "incident_number": 1042,
  "title": "auth-api token refresh latency above 2s p99",
  "status": "triggered",
  "urgency": "high",
  "service_id": "PS001",
  "escalation_policy_id": "EP001",
  "assigned_to": "PU004",
  "created_at": "2026-05-27T09:14:00Z",
  "resolved_at": null
}
```

**POST trigger incident** — `/incidents` (status 201)

```
{
  "incident_id": "PI-878cfe5d27",
  "incident_number": 1044,
  "title": "auth-api refresh token endpoint timing out",
  "status": "triggered",
  "urgency": "high",
  "service_id": "PS001",
  "escalation_policy_id": "EP001",
  "assigned_to": "PU004",
  "created_at": "2026-06-17T10:31:30Z",
  "resolved_at": null
}
```

**PUT acknowledge incident** — `/incidents/PI001` (status 200)

```
{
  "incident_id": "PI001",
  "incident_number": 1042,
  "title": "auth-api token refresh latency above 2s p99",
  "status": "triggered",
  "urgency": "high",
  "service_id": "PS001",
  "escalation_policy_id": "EP001",
  "assigned_to": "PU004",
  "created_at": "2026-05-27T09:14:00Z",
  "resolved_at": null
}
```

**PUT resolve incident** — `/incidents/PI001` (status 200)

```
{
  "incident_id": "PI001",
  "incident_number": 1042,
  "title": "auth-api token refresh latency above 2s p99",
  "status": "triggered",
  "urgency": "high",
  "service_id": "PS001",
  "escalation_policy_id": "EP001",
  "assigned_to": "PU004",
  "created_at": "2026-05-27T09:14:00Z",
  "resolved_at": null
}
```

**POST add incident note** — `/incidents/PI001/notes` (status 201)

```
{
  "note_id": "NOTE-55aaf5b09d",
  "incident_id": "PI001",
  "content": "Rolled back auth-api deploy, p99 recovering.",
  "user_id": "PU004",
  "created_at": "2026-06-17T10:31:30Z"
}
```

**GET list oncalls** — `/oncalls` (status 200)

```
{
  "oncalls": [
    {
      "schedule_id": "SCH001",
      "schedule_name": "Platform Primary",
      "escalation_policy_id": "EP001",
      "user": {
        "user_id": "PU004",
        "name": "Rohit Bansal"
      },
      "start": "2026-05-26T17:00:00Z",
      "end": "2026-06-02T17:00:00Z"
    },
    {
      "schedule_id": "SCH002",
      "schedule_name": "Platform Secondary",
      "escalation_policy_id": "EP001",
      "user": {
        "user_id": "PU003",
        "name": "Helena Park"
      },
      "start": "2026-05-26T17:00:00Z",
      "end": "2026-06-02T17:00:00Z"
    },
    {
      
... (truncated)
```

**GET list schedules** — `/schedules` (status 200)

```
{
  "schedules": [
    {
      "schedule_id": "SCH001",
      "name": "Platform Primary",
      "time_zone": "America/Los_Angeles",
      "escalation_policy_id": "EP001",
      "current_oncall_user_id": "PU004",
      "oncall_start": "2026-05-26T17:00:00Z",
      "oncall_end": "2026-06-02T17:00:00Z"
    },
    {
      "schedule_id": "SCH002",
      "name": "Platform Secondary",
      "time_zone": "Europe/Berlin",
      "escalation_policy_id": "EP001",
      "current_oncall_user_id": "PU003",
      "oncall_start": "2026-05-26T17:00:00Z",
      "oncall_end": "2026-06-02T17:00:00Z"
    },
    {
 
... (truncated)
```

**GET list escalation policies** — `/escalation_policies` (status 200)

```
{
  "escalation_policies": [
    {
      "escalation_policy_id": "EP001",
      "name": "Platform On-Call",
      "num_loops": 2,
      "tier1_user_id": "PU004",
      "tier2_user_id": "PU001"
    },
    {
      "escalation_policy_id": "EP002",
      "name": "Billing On-Call",
      "num_loops": 1,
      "tier1_user_id": "PU002",
      "tier2_user_id": "PU005"
    }
  ]
}
```

**GET list users** — `/users` (status 200)

```
{
  "users": [
    {
      "user_id": "PU001",
      "name": "Amelia Ortega",
      "email": "amelia.ortega@orbit-labs.com",
      "role": "admin",
      "time_zone": "America/Los_Angeles",
      "job_title": "SRE Lead"
    },
    {
      "user_id": "PU002",
      "name": "Jonas Pereira",
      "email": "jonas.pereira@orbit-labs.com",
      "role": "user",
      "time_zone": "America/Los_Angeles",
      "job_title": "Backend Engineer"
    },
    {
      "user_id": "PU003",
      "name": "Helena Park",
      "email": "helena.park@orbit-labs.com",
      "role": "user",
      "time_zone": "Europe
... (truncated)
```

</details>

### paypal-api (port 8042) — server: started

| Result | Method | Path | Status | Endpoint |
|--------|--------|------|--------|----------|
| PASS | GET | /health | 200 | health |
| PASS | POST | /v2/checkout/orders | 201 | create checkout order |
| PASS | GET | /v2/checkout/orders/ORDER-8AB54321CD987654E | 200 | get checkout order |
| PASS | POST | /v2/checkout/orders/ORDER-8AB54321CD987654E/capture | 201 | capture order |
| PASS | POST | /v2/payments/refunds | 201 | create refund |
| PASS | GET | /v2/payments/refunds/REF_1A234567BC890123 | 200 | get refund |
| PASS | GET | /v2/invoicing/invoices?status=PAID | 200 | list invoices |
| PASS | POST | /v2/invoicing/invoices | 201 | create invoice |
| PASS | POST | /v1/payments/payouts | 201 | create payout |

<details><summary>responses</summary>

**GET health** — `/health` (status 200)

```
{
  "status": "ok"
}
```

**POST create checkout order** — `/v2/checkout/orders` (status 201)

```
{
  "id": "ORDER-5F3EF534C7A24D0F9",
  "intent": "CAPTURE",
  "status": "CREATED",
  "purchase_units": [
    {
      "amount": {
        "currency_code": "USD",
        "value": "42.00"
      },
      "payee": {
        "email_address": "merchant@orbit-labs.com"
      },
      "description": "New order"
    }
  ],
  "create_time": "2026-06-17T10:31:31Z"
}
```

**GET get checkout order** — `/v2/checkout/orders/ORDER-8AB54321CD987654E` (status 200)

```
{
  "id": "ORDER-8AB54321CD987654E",
  "intent": "CAPTURE",
  "status": "APPROVED",
  "purchase_units": [
    {
      "amount": {
        "currency_code": "USD",
        "value": "19.00"
      },
      "payee": {
        "email_address": "merchant@orbit-labs.com"
      },
      "description": "Starter plan monthly"
    }
  ],
  "create_time": "2026-05-18T11:15:00Z"
}
```

**POST capture order** — `/v2/checkout/orders/ORDER-8AB54321CD987654E/capture` (status 201)

```
{
  "id": "ORDER-8AB54321CD987654E",
  "status": "COMPLETED",
  "purchase_units": [
    {
      "payments": {
        "captures": [
          {
            "id": "CAP_BFE54E6B3E0B41B7",
            "order_id": "ORDER-8AB54321CD987654E",
            "status": "COMPLETED",
            "amount": {
              "currency_code": "USD",
              "value": "19.00"
            },
            "final_capture": true,
            "create_time": "2026-06-17T10:31:31Z"
          }
        ]
      }
    }
  ]
}
```

**POST create refund** — `/v2/payments/refunds` (status 201)

```
{
  "id": "REF_C78E8BB05A1E4F9E",
  "capture_id": "CAP_3C679384HN8401234",
  "status": "COMPLETED",
  "amount": {
    "currency_code": "USD",
    "value": "5.00"
  },
  "note_to_payer": "Goodwill credit",
  "create_time": "2026-06-17T10:31:31Z"
}
```

**GET get refund** — `/v2/payments/refunds/REF_1A234567BC890123` (status 200)

```
{
  "id": "REF_1A234567BC890123",
  "capture_id": "CAP_3C679384HN8401234",
  "status": "COMPLETED",
  "amount": {
    "currency_code": "USD",
    "value": "10.00"
  },
  "note_to_payer": "Partial refund for late delivery",
  "create_time": "2026-05-12T10:00:00Z"
}
```

**GET list invoices** — `/v2/invoicing/invoices?status=PAID` (status 200)

```
{
  "total_items": 2,
  "total_pages": 1,
  "items": [
    {
      "id": "INV2-AB12-CD34-EF56-GH78",
      "detail": {
        "invoice_number": "INV-0001",
        "currency_code": "USD",
        "note": "Thank you for your business"
      },
      "status": "PAID",
      "primary_recipients": [
        {
          "billing_info": {
            "email_address": "harper.nguyen@example.com"
          }
        }
      ],
      "amount": {
        "currency_code": "USD",
        "value": "49.99"
      },
      "due_date": "2026-05-15"
    },
    {
      "id": "INV2-YZ56-AB78-CD90-EF12",
      "d
... (truncated)
```

**POST create invoice** — `/v2/invoicing/invoices` (status 201)

```
{
  "id": "INV2_C785361B5F1C4385",
  "detail": {
    "invoice_number": "INV-0006",
    "currency_code": "USD",
    "note": "Net 30"
  },
  "status": "DRAFT",
  "primary_recipients": [
    {
      "billing_info": {
        "email_address": "priya.kapoor@example.com"
      }
    }
  ],
  "amount": {
    "currency_code": "USD",
    "value": "60.00"
  },
  "due_date": "2026-06-30"
}
```

**POST create payout** — `/v1/payments/payouts` (status 201)

```
{
  "batch_header": {
    "payout_batch_id": "PAYOUT-38D5406F97B3",
    "batch_status": "PENDING",
    "sender_batch_header": {
      "sender_batch_id": "Payouts_2026_05_28",
      "email_subject": "You have a payout"
    },
    "amount": {
      "currency_code": "USD",
      "value": "100.00"
    }
  },
  "recipient_email": "partner@orbit-labs.com",
  "create_time": "2026-06-17T10:31:31Z"
}
```

</details>

### pinterest-api (port 8006) — server: started

| Result | Method | Path | Status | Endpoint |
|--------|--------|------|--------|----------|
| PASS | GET | /health | 200 | GET /health |
| PASS | GET | /v5/user_account | 200 | GET User Account |
| PASS | GET | /v5/user_account/analytics | 200 | GET User Analytics |
| PASS | GET | /v5/user_account/analytics?start_date=2026-04-01&end_date=2026-04-05 | 200 | GET User Analytics - Date Range |
| PASS | GET | /v5/boards | 200 | GET List Boards |
| PASS | GET | /v5/boards?privacy=PUBLIC | 200 | GET List Boards - Public Only |
| PASS | GET | /v5/boards?limit=3&offset=0 | 200 | GET List Boards - Paginated |
| PASS | GET | /v5/boards/board_1001 | 200 | GET Board |
| WARN | GET | /v5/boards/board_99999 | 404 | GET Board - 404 |
| PASS | POST | /v5/boards | 201 | POST Create Board |
| PASS | PATCH | /v5/boards/board_1001 | 200 | PATCH Update Board |
| PASS | DELETE | /v5/boards/board_1009 | 200 | DELETE Board |
| PASS | GET | /v5/boards/board_1001/pins | 200 | GET Board Pins |
| WARN | GET | /v5/boards/board_99999/pins | 404 | GET Board Pins - 404 |
| PASS | GET | /v5/boards/board_1002/sections | 200 | GET List Board Sections |
| WARN | GET | /v5/boards/board_99999/sections | 404 | GET List Board Sections - 404 |
| PASS | POST | /v5/boards/board_1002/sections | 201 | POST Create Board Section |
| PASS | GET | /v5/boards/board_1002/sections/section_2001/pins | 200 | GET Section Pins |
| WARN | GET | /v5/boards/board_99999/sections/section_2001/pins | 404 | GET Section Pins - 404 Board |
| WARN | GET | /v5/boards/board_1002/sections/section_99999/pins | 404 | GET Section Pins - 404 Section |
| PASS | GET | /v5/pins | 200 | GET List Pins |
| PASS | GET | /v5/pins?limit=5&offset=0 | 200 | GET List Pins - Paginated |
| PASS | GET | /v5/pins/pin_3001 | 200 | GET Pin |
| WARN | GET | /v5/pins/pin_99999 | 404 | GET Pin - 404 |
| PASS | POST | /v5/pins | 201 | POST Create Pin |
| PASS | PATCH | /v5/pins/pin_3001 | 200 | PATCH Update Pin |
| PASS | DELETE | /v5/pins/pin_3016 | 200 | DELETE Pin |
| WARN | DELETE | /v5/pins/pin_99999 | 404 | DELETE Pin - 404 |
| PASS | GET | /v5/pins/pin_3001/analytics | 200 | GET Pin Analytics |
| PASS | GET | /v5/pins/pin_3005/analytics?start_date=2026-04-01&end_date=2026-04-03 | 200 | GET Pin Analytics - Date Range |
| WARN | GET | /v5/pins/pin_99999/analytics | 404 | GET Pin Analytics - 404 |
| PASS | GET | /v5/search/pins?query=DIY | 200 | GET Search Pins - DIY |
| PASS | GET | /v5/search/pins?query=kitchen | 200 | GET Search Pins - Kitchen |
| PASS | GET | /v5/search/pins?query=xyznonexistent | 200 | GET Search Pins - No Results |
| PASS | GET | /v5/media/pin_3001 | 200 | GET Media Status - Existing Pin |
| WARN | GET | /v5/media/media_99999 | 404 | GET Media Status - 404 |
| PASS | GET | /v5/ad_accounts | 200 | GET List Ad Accounts |
| PASS | GET | /v5/ad_accounts/ad_acct_7001 | 200 | GET Ad Account |
| WARN | GET | /v5/ad_accounts/ad_acct_99999 | 404 | GET Ad Account - 404 |
| PASS | GET | /v5/ad_accounts/ad_acct_7001/campaigns | 200 | GET List Campaigns |
| PASS | GET | /v5/ad_accounts/ad_acct_7001/campaigns?status=ACTIVE | 200 | GET List Campaigns - Filter Active |
| WARN | GET | /v5/ad_accounts/ad_acct_99999/campaigns | 404 | GET List Campaigns - 404 Account |

<details><summary>responses</summary>

**GET GET /health** — `/health` (status 200)

```
{
  "status": "ok"
}
```

**GET GET User Account** — `/v5/user_account` (status 200)

```
{
  "type": "user_account",
  "user_account": {
    "account_type": "BUSINESS",
    "username": "cozynestinteriors",
    "profile_image": "https://i.pinimg.com/avatars/cozynestinteriors_1680000000_150.jpg",
    "website_url": "https://www.cozynestinteriors.com",
    "business_name": "CozyNest Interiors",
    "board_count": 9,
    "pin_count": 127,
    "follower_count": 12043,
    "following_count": 340,
    "monthly_views": 285000,
    "created_at": "2023-03-12T08:15:00"
  }
}
```

**GET GET User Analytics** — `/v5/user_account/analytics` (status 200)

```
{
  "type": "user_analytics",
  "count": 30,
  "results": [
    {
      "date": "2026-03-27",
      "impressions": 520,
      "saves": 38,
      "pin_clicks": 26,
      "outbound_clicks": 17,
      "profile_visits": 10,
      "follows": 1
    },
    {
      "date": "2026-03-28",
      "impressions": 580,
      "saves": 42,
      "pin_clicks": 30,
      "outbound_clicks": 20,
      "profile_visits": 12,
      "follows": 2
    },
    {
      "date": "2026-03-29",
      "impressions": 465,
      "saves": 33,
      "pin_clicks": 23,
      "outbound_clicks": 15,
      "profile_visits": 8,
      "fo
... (truncated)
```

**GET GET User Analytics - Date Range** — `/v5/user_account/analytics?start_date=2026-04-01&end_date=2026-04-05` (status 200)

```
{
  "type": "user_analytics",
  "count": 5,
  "results": [
    {
      "date": "2026-04-01",
      "impressions": 610,
      "saves": 45,
      "pin_clicks": 31,
      "outbound_clicks": 21,
      "profile_visits": 13,
      "follows": 1
    },
    {
      "date": "2026-04-02",
      "impressions": 660,
      "saves": 48,
      "pin_clicks": 34,
      "outbound_clicks": 23,
      "profile_visits": 15,
      "follows": 2
    },
    {
      "date": "2026-04-03",
      "impressions": 530,
      "saves": 38,
      "pin_clicks": 26,
      "outbound_clicks": 17,
      "profile_visits": 10,
      "fo
... (truncated)
```

**GET GET List Boards** — `/v5/boards` (status 200)

```
{
  "type": "boards",
  "count": 9,
  "total": 9,
  "offset": 0,
  "limit": 25,
  "results": [
    {
      "board_id": "board_1003",
      "name": "Spring Macaron Collection",
      "description": "Inspo and product shots for seasonal macarons. Flavors techniques and styling ideas",
      "privacy": "PUBLIC",
      "created_at": "2026-02-10T14:22:00",
      "updated_at": "2026-04-18T09:45:00",
      "pin_count": 15,
      "follower_count": 189,
      "collaborator_count": 0
    },
    {
      "board_id": "board_1009",
      "name": "Show Prep Private Notes",
      "description": "Private plann
... (truncated)
```

**GET GET List Boards - Public Only** — `/v5/boards?privacy=PUBLIC` (status 200)

```
{
  "type": "boards",
  "count": 8,
  "total": 8,
  "offset": 0,
  "limit": 25,
  "results": [
    {
      "board_id": "board_1003",
      "name": "Spring Macaron Collection",
      "description": "Inspo and product shots for seasonal macarons. Flavors techniques and styling ideas",
      "privacy": "PUBLIC",
      "created_at": "2026-02-10T14:22:00",
      "updated_at": "2026-04-18T09:45:00",
      "pin_count": 15,
      "follower_count": 189,
      "collaborator_count": 0
    },
    {
      "board_id": "board_1001",
      "name": "Orchid Show Mood",
      "description": "Greenhouse setups an
... (truncated)
```

**GET GET List Boards - Paginated** — `/v5/boards?limit=3&offset=0` (status 200)

```
{
  "type": "boards",
  "count": 3,
  "total": 9,
  "offset": 0,
  "limit": 3,
  "results": [
    {
      "board_id": "board_1003",
      "name": "Spring Macaron Collection",
      "description": "Inspo and product shots for seasonal macarons. Flavors techniques and styling ideas",
      "privacy": "PUBLIC",
      "created_at": "2026-02-10T14:22:00",
      "updated_at": "2026-04-18T09:45:00",
      "pin_count": 15,
      "follower_count": 189,
      "collaborator_count": 0
    },
    {
      "board_id": "board_1009",
      "name": "Show Prep Private Notes",
      "description": "Private planni
... (truncated)
```

**GET GET Board** — `/v5/boards/board_1001` (status 200)

```
{
  "type": "board",
  "board": {
    "board_id": "board_1001",
    "name": "Orchid Show Mood",
    "description": "Greenhouse setups and display ideas for orchid society shows and competitions",
    "privacy": "PUBLIC",
    "created_at": "2025-11-03T09:10:00",
    "updated_at": "2026-05-12T14:30:00",
    "pin_count": 18,
    "follower_count": 324,
    "collaborator_count": 0
  }
}
```

**GET GET Board - 404** — `/v5/boards/board_99999` (status 404)

```
{
  "error": "Board board_99999 not found"
}
```

**POST POST Create Board** — `/v5/boards` (status 201)

```
{
  "type": "board",
  "board": {
    "board_id": "board_1010",
    "name": "Outdoor Living Spaces",
    "description": "Patio and garden design ideas",
    "privacy": "PUBLIC",
    "created_at": "2026-06-17T10:31:31",
    "updated_at": "2026-06-17T10:31:31",
    "pin_count": 0,
    "follower_count": 0,
    "collaborator_count": 0
  }
}
```

**PATCH PATCH Update Board** — `/v5/boards/board_1001` (status 200)

```
{
  "type": "board",
  "board": {
    "board_id": "board_1001",
    "name": "Orchid Show Mood",
    "description": "Greenhouse setups and display ideas for orchid society shows and competitions",
    "privacy": "PUBLIC",
    "created_at": "2025-11-03T09:10:00",
    "updated_at": "2026-05-12T14:30:00",
    "pin_count": 18,
    "follower_count": 324,
    "collaborator_count": 0
  }
}
```

**DELETE DELETE Board** — `/v5/boards/board_1009` (status 200)

```
{
  "type": "board",
  "deleted": true,
  "board_id": "board_1009"
}
```

**GET GET Board Pins** — `/v5/boards/board_1001/pins` (status 200)

```
{
  "type": "pins",
  "count": 3,
  "total": 3,
  "offset": 0,
  "limit": 25,
  "results": [
    {
      "pin_id": "pin_3003",
      "board_id": "board_1001",
      "board_section_id": null,
      "title": "Greenhouse to Show Floor Transport Tips",
      "description": "How to safely transport orchids from greenhouse to show venue. Packing materials and temperature management. #orchidtransport #greenhouse",
      "link": "https://www.orchidweb.com/articles/transporting-orchids",
      "media_type": "image",
      "created_at": "2026-01-15T14:00:00",
      "updated_at": "2026-05-01T09:30:00",
 
... (truncated)
```

**GET GET Board Pins - 404** — `/v5/boards/board_99999/pins` (status 404)

```
{
  "error": "Board board_99999 not found"
}
```

**GET GET List Board Sections** — `/v5/boards/board_1002/sections` (status 200)

```
{
  "type": "board_sections",
  "count": 3,
  "results": [
    {
      "section_id": "section_2001",
      "board_id": "board_1002",
      "name": "Phalaenopsis",
      "pin_count": 7
    },
    {
      "section_id": "section_2002",
      "board_id": "board_1002",
      "name": "Cattleya",
      "pin_count": 6
    },
    {
      "section_id": "section_2003",
      "board_id": "board_1002",
      "name": "Paphiopedilum",
      "pin_count": 5
    }
  ]
}
```

**GET GET List Board Sections - 404** — `/v5/boards/board_99999/sections` (status 404)

```
{
  "error": "Board board_99999 not found"
}
```

**POST POST Create Board Section** — `/v5/boards/board_1002/sections` (status 201)

```
{
  "type": "board_section",
  "board_section": {
    "section_id": "section_2012",
    "board_id": "board_1002",
    "name": "Electrical Projects",
    "pin_count": 0
  }
}
```

**GET GET Section Pins** — `/v5/boards/board_1002/sections/section_2001/pins` (status 200)

```
{
  "type": "pins",
  "count": 2,
  "total": 2,
  "offset": 0,
  "limit": 25,
  "results": [
    {
      "pin_id": "pin_3007",
      "board_id": "board_1002",
      "board_section_id": "section_2001",
      "title": "Root Health Check Visual Guide",
      "description": "How to tell healthy orchid roots from dehydrated or rotted ones. Color and texture indicators. #orchidroots #orchidhealth",
      "link": "https://www.orchidbliss.com/orchid-root-health/",
      "media_type": "image",
      "created_at": "2024-01-15T09:20:00",
      "updated_at": "2026-04-10T12:00:00",
      "dominant_color": 
... (truncated)
```

**GET GET Section Pins - 404 Board** — `/v5/boards/board_99999/sections/section_2001/pins` (status 404)

```
{
  "error": "Board board_99999 not found"
}
```

**GET GET Section Pins - 404 Section** — `/v5/boards/board_1002/sections/section_99999/pins` (status 404)

```
{
  "error": "Section section_99999 not found in board board_1002"
}
```

**GET GET List Pins** — `/v5/pins` (status 200)

```
{
  "type": "pins",
  "count": 20,
  "total": 20,
  "offset": 0,
  "limit": 25,
  "results": [
    {
      "pin_id": "pin_3010",
      "board_id": "board_1003",
      "board_section_id": "section_2004",
      "title": "Spring Macaron Tower Display Ideas",
      "description": "Beautiful tiered tower displays for spring macaron collections. Color coordination and height arrangements. #macarontower #springdessert",
      "link": "https://www.pinterest.com/ideas/macaron-tower/",
      "media_type": "image",
      "created_at": "2026-03-15T14:30:00",
      "updated_at": "2026-04-08T11:00:00",
    
... (truncated)
```

**GET GET List Pins - Paginated** — `/v5/pins?limit=5&offset=0` (status 200)

```
{
  "type": "pins",
  "count": 5,
  "total": 20,
  "offset": 0,
  "limit": 5,
  "results": [
    {
      "pin_id": "pin_3010",
      "board_id": "board_1003",
      "board_section_id": "section_2004",
      "title": "Spring Macaron Tower Display Ideas",
      "description": "Beautiful tiered tower displays for spring macaron collections. Color coordination and height arrangements. #macarontower #springdessert",
      "link": "https://www.pinterest.com/ideas/macaron-tower/",
      "media_type": "image",
      "created_at": "2026-03-15T14:30:00",
      "updated_at": "2026-04-08T11:00:00",
      
... (truncated)
```

**GET GET Pin** — `/v5/pins/pin_3001` (status 200)

```
{
  "type": "pin",
  "pin": {
    "pin_id": "pin_3001",
    "board_id": "board_1001",
    "board_section_id": null,
    "title": "Paphiopedilum Show Display Setup",
    "description": "Elegant arrangement ideas for slipper orchids on competition tables. Moss bases and accent lighting. #orchidshow #paphiopedilum #orchiddisplay",
    "link": "https://www.aos.org/orchids/orchid-shows.aspx",
    "media_type": "image",
    "created_at": "2025-11-10T09:00:00",
    "updated_at": "2026-05-10T14:00:00",
    "dominant_color": "#4A6741",
    "alt_text": "Three Paphiopedilum orchids arranged on moss-cover
... (truncated)
```

**GET GET Pin - 404** — `/v5/pins/pin_99999` (status 404)

```
{
  "error": "Pin pin_99999 not found"
}
```

**POST POST Create Pin** — `/v5/pins` (status 201)

```
{
  "type": "pin",
  "pin": {
    "pin_id": "pin_3021",
    "board_id": "board_1001",
    "board_section_id": null,
    "title": "Boho Living Room Makeover",
    "description": "Transform your space with these boho-chic design tips #boho #livingroom",
    "link": "https://www.cozynestinteriors.com/blog/boho-makeover",
    "media_type": "image",
    "created_at": "2026-06-17T10:31:31",
    "updated_at": "2026-06-17T10:31:31",
    "dominant_color": null,
    "alt_text": "A boho-styled living room with macrame and plants",
    "is_promoted": false,
    "pin_metrics_impressions": 0,
    "pin_metri
```

**PATCH PATCH Update Pin** — `/v5/pins/pin_3001` (status 200)

```
{
  "type": "pin",
  "pin": {
    "pin_id": "pin_3001",
    "board_id": "board_1001",
    "board_section_id": null,
    "title": "Paphiopedilum Show Display Setup",
    "description": "Elegant arrangement ideas for slipper orchids on competition tables. Moss bases and accent lighting. #orchidshow #paphiopedilum #orchiddisplay",
    "link": "https://www.aos.org/orchids/orchid-shows.aspx",
    "media_type": "image",
    "created_at": "2025-11-10T09:00:00",
    "updated_at": "2026-05-10T14:00:00",
    "dominant_color": "#4A6741",
    "alt_text": "Three Paphiopedilum orchids arranged on moss-cover
... (truncated)
```

**DELETE DELETE Pin** — `/v5/pins/pin_3016` (status 200)

```
{
  "type": "pin",
  "deleted": true,
  "pin_id": "pin_3016"
}
```

**DELETE DELETE Pin - 404** — `/v5/pins/pin_99999` (status 404)

```
{
  "error": "Pin pin_99999 not found"
}
```

**GET GET Pin Analytics** — `/v5/pins/pin_3001/analytics` (status 200)

```
{
  "type": "pin_analytics",
  "count": 5,
  "pin_id": "pin_3001",
  "results": [
    {
      "pin_id": "pin_3001",
      "date": "2026-04-01",
      "impressions": 165,
      "saves": 14,
      "pin_clicks": 9,
      "outbound_clicks": 6
    },
    {
      "pin_id": "pin_3001",
      "date": "2026-04-02",
      "impressions": 148,
      "saves": 12,
      "pin_clicks": 8,
      "outbound_clicks": 5
    },
    {
      "pin_id": "pin_3001",
      "date": "2026-04-03",
      "impressions": 182,
      "saves": 16,
      "pin_clicks": 11,
      "outbound_clicks": 7
    },
    {
      "pin_id": "pi
```

**GET GET Pin Analytics - Date Range** — `/v5/pins/pin_3005/analytics?start_date=2026-04-01&end_date=2026-04-03` (status 200)

```
{
  "type": "pin_analytics",
  "count": 3,
  "pin_id": "pin_3005",
  "results": [
    {
      "pin_id": "pin_3005",
      "date": "2026-04-01",
      "impressions": 185,
      "saves": 16,
      "pin_clicks": 10,
      "outbound_clicks": 7
    },
    {
      "pin_id": "pin_3005",
      "date": "2026-04-02",
      "impressions": 198,
      "saves": 18,
      "pin_clicks": 12,
      "outbound_clicks": 8
    },
    {
      "pin_id": "pin_3005",
      "date": "2026-04-03",
      "impressions": 172,
      "saves": 14,
      "pin_clicks": 9,
      "outbound_clicks": 6
    }
  ]
}
```

**GET GET Pin Analytics - 404** — `/v5/pins/pin_99999/analytics` (status 404)

```
{
  "error": "Pin pin_99999 not found"
}
```

**GET GET Search Pins - DIY** — `/v5/search/pins?query=DIY` (status 200)

```
{
  "type": "pins",
  "count": 0,
  "total": 0,
  "offset": 0,
  "limit": 25,
  "results": []
}
```

**GET GET Search Pins - Kitchen** — `/v5/search/pins?query=kitchen` (status 200)

```
{
  "type": "pins",
  "count": 0,
  "total": 0,
  "offset": 0,
  "limit": 25,
  "results": []
}
```

**GET GET Search Pins - No Results** — `/v5/search/pins?query=xyznonexistent` (status 200)

```
{
  "type": "pins",
  "count": 0,
  "total": 0,
  "offset": 0,
  "limit": 25,
  "results": []
}
```

**GET GET Media Status - Existing Pin** — `/v5/media/pin_3001` (status 200)

```
{
  "type": "media_upload",
  "media_id": "pin_3001",
  "status": "succeeded",
  "media_type": "image"
}
```

**GET GET Media Status - 404** — `/v5/media/media_99999` (status 404)

```
{
  "error": "Media media_99999 not found"
}
```

**GET GET List Ad Accounts** — `/v5/ad_accounts` (status 200)

```
{
  "type": "ad_accounts",
  "count": 1,
  "total": 1,
  "offset": 0,
  "limit": 25,
  "results": [
    {
      "ad_account_id": "ad_acct_7001",
      "name": "Erin Russell Orchid Pins",
      "currency": "USD",
      "country": "US",
      "status": "ACTIVE",
      "created_at": "2026-02-15T09:00:00"
    }
  ]
}
```

**GET GET Ad Account** — `/v5/ad_accounts/ad_acct_7001` (status 200)

```
{
  "type": "ad_account",
  "ad_account": {
    "ad_account_id": "ad_acct_7001",
    "name": "Erin Russell Orchid Pins",
    "currency": "USD",
    "country": "US",
    "status": "ACTIVE",
    "created_at": "2026-02-15T09:00:00"
  }
}
```

**GET GET Ad Account - 404** — `/v5/ad_accounts/ad_acct_99999` (status 404)

```
{
  "error": "Ad account ad_acct_99999 not found"
}
```

**GET GET List Campaigns** — `/v5/ad_accounts/ad_acct_7001/campaigns` (status 200)

```
{
  "type": "campaigns",
  "count": 3,
  "total": 3,
  "offset": 0,
  "limit": 25,
  "results": [
    {
      "campaign_id": "camp_8001",
      "ad_account_id": "ad_acct_7001",
      "name": "Orchid Show Awareness June 2026",
      "status": "ACTIVE",
      "objective_type": "AWARENESS",
      "daily_spend_cap_micro": 2000000,
      "lifetime_spend_cap_micro": 60000000,
      "start_time": "2026-05-01T00:00:00",
      "end_time": "2026-06-14T23:59:59",
      "created_at": "2026-04-20T10:00:00",
      "updated_at": "2026-05-10T08:30:00"
    },
    {
      "campaign_id": "camp_8002",
      "ad_a
... (truncated)
```

**GET GET List Campaigns - Filter Active** — `/v5/ad_accounts/ad_acct_7001/campaigns?status=ACTIVE` (status 200)

```
{
  "type": "campaigns",
  "count": 2,
  "total": 2,
  "offset": 0,
  "limit": 25,
  "results": [
    {
      "campaign_id": "camp_8001",
      "ad_account_id": "ad_acct_7001",
      "name": "Orchid Show Awareness June 2026",
      "status": "ACTIVE",
      "objective_type": "AWARENESS",
      "daily_spend_cap_micro": 2000000,
      "lifetime_spend_cap_micro": 60000000,
      "start_time": "2026-05-01T00:00:00",
      "end_time": "2026-06-14T23:59:59",
      "created_at": "2026-04-20T10:00:00",
      "updated_at": "2026-05-10T08:30:00"
    },
    {
      "campaign_id": "camp_8002",
      "ad_a
... (truncated)
```

**GET GET List Campaigns - 404 Account** — `/v5/ad_accounts/ad_acct_99999/campaigns` (status 404)

```
{
  "error": "Ad account ad_acct_99999 not found"
}
```

</details>

### plaid-api (port 8022) — server: started

| Result | Method | Path | Status | Endpoint |
|--------|--------|------|--------|----------|
| PASS | GET | /health | 200 | health |
| PASS | POST | /accounts/get | 200 | accounts get |
| PASS | POST | /accounts/balance/get | 200 | accounts balance get |
| PASS | POST | /transactions/get | 200 | transactions get |
| PASS | POST | /institutions/get_by_id | 200 | institutions get by id |
| PASS | POST | /identity/get | 200 | identity get |

<details><summary>responses</summary>

**GET health** — `/health` (status 200)

```
{
  "status": "ok"
}
```

**POST accounts get** — `/accounts/get` (status 200)

```
{
  "accounts": [
    {
      "account_id": "acc_chk_001",
      "name": "Everyday Checking",
      "official_name": "Cascade Everyday Checking",
      "mask": "0123",
      "type": "depository",
      "subtype": "checking",
      "balances": {
        "available": 4218.55,
        "current": 4318.55,
        "limit": null,
        "iso_currency_code": "USD",
        "unofficial_currency_code": null
      }
    },
    {
      "account_id": "acc_sav_002",
      "name": "High-Yield Savings",
      "official_name": "Cascade High-Yield Savings",
      "mask": "4455",
      "type": "depository",
  
... (truncated)
```

**POST accounts balance get** — `/accounts/balance/get` (status 200)

```
{
  "accounts": [
    {
      "account_id": "acc_chk_001",
      "name": "Everyday Checking",
      "official_name": "Cascade Everyday Checking",
      "mask": "0123",
      "type": "depository",
      "subtype": "checking",
      "balances": {
        "available": 4218.55,
        "current": 4318.55,
        "limit": null,
        "iso_currency_code": "USD",
        "unofficial_currency_code": null
      }
    }
  ],
  "item": {
    "item_id": "item_orbit_8a1f2c",
    "institution_id": "ins_109512",
    "webhook": "https://example.com/plaid/webhook",
    "available_products": [
      "balance
```

**POST transactions get** — `/transactions/get` (status 200)

```
{
  "accounts": [
    {
      "account_id": "acc_chk_001",
      "name": "Everyday Checking",
      "official_name": "Cascade Everyday Checking",
      "mask": "0123",
      "type": "depository",
      "subtype": "checking",
      "balances": {
        "available": 4218.55,
        "current": 4318.55,
        "limit": null,
        "iso_currency_code": "USD",
        "unofficial_currency_code": null
      }
    },
    {
      "account_id": "acc_sav_002",
      "name": "High-Yield Savings",
      "official_name": "Cascade High-Yield Savings",
      "mask": "4455",
      "type": "depository",
  
... (truncated)
```

**POST institutions get by id** — `/institutions/get_by_id` (status 200)

```
{
  "institution": {
    "institution_id": "ins_109512",
    "name": "Cascade Federal Bank",
    "products": [
      "transactions",
      "auth",
      "balance",
      "identity"
    ],
    "country_codes": [
      "US"
    ],
    "url": "https://www.cascadefed.example.com",
    "primary_color": "#1a73a8",
    "routing_numbers": [
      "122105155"
    ]
  },
  "request_id": "3c0814f152ea423d"
}
```

**POST identity get** — `/identity/get` (status 200)

```
{
  "accounts": [
    {
      "account_id": "acc_chk_001",
      "name": "Everyday Checking",
      "official_name": "Cascade Everyday Checking",
      "mask": "0123",
      "type": "depository",
      "subtype": "checking",
      "balances": {
        "available": 4218.55,
        "current": 4318.55,
        "limit": null,
        "iso_currency_code": "USD",
        "unofficial_currency_code": null
      },
      "owners": [
        {
          "names": [
            "Amelia Ortega"
          ],
          "emails": [
            {
              "data": "amelia.ortega@orbit-labs.com",
        
... (truncated)
```

</details>

### posthog-api (port 8092) — server: started

| Result | Method | Path | Status | Endpoint |
|--------|--------|------|--------|----------|
| PASS | GET | /health | 200 | health |
| PASS | POST | /capture | 200 | capture |
| PASS | POST | /decide | 200 | decide |
| PASS | GET | /api/projects/1/events | 200 | events |
| PASS | GET | /api/projects/1/events?event=$pageview&distinct_id=user_3001 | 200 | events filtered |
| PASS | GET | /api/projects/1/feature_flags | 200 | feature flags |
| PASS | GET | /api/projects/1/persons | 200 | persons |

<details><summary>responses</summary>

**GET health** — `/health` (status 200)

```
{
  "status": "ok"
}
```

**POST capture** — `/capture` (status 200)

```
{
  "status": 1
}
```

**POST decide** — `/decide` (status 200)

```
{
  "featureFlags": {
    "new-onboarding": true,
    "beta-dashboard": true,
    "dark-mode": false,
    "fast-checkout": true
  },
  "distinctId": "user_3001"
}
```

**GET events** — `/api/projects/1/events` (status 200)

```
{
  "results": [
    {
      "id": "evt_30001",
      "project_id": 1,
      "distinct_id": "user_3001",
      "event": "$pageview",
      "timestamp": "2026-05-02T09:00:00Z",
      "properties": {
        "$current_url": "/dashboard"
      }
    },
    {
      "id": "evt_30002",
      "project_id": 1,
      "distinct_id": "user_3001",
      "event": "button_clicked",
      "timestamp": "2026-05-02T09:02:11Z",
      "properties": {
        "name": "export",
        "plan": "pro"
      }
    },
    {
      "id": "evt_30003",
      "project_id": 1,
      "distinct_id": "user_3002",
      "event"
... (truncated)
```

**GET events filtered** — `/api/projects/1/events?event=$pageview&distinct_id=user_3001` (status 200)

```
{
  "results": [
    {
      "id": "evt_30001",
      "project_id": 1,
      "distinct_id": "user_3001",
      "event": "$pageview",
      "timestamp": "2026-05-02T09:00:00Z",
      "properties": {
        "$current_url": "/dashboard"
      }
    }
  ],
  "count": 1
}
```

**GET feature flags** — `/api/projects/1/feature_flags` (status 200)

```
{
  "results": [
    {
      "id": "flag_4001",
      "key": "new-onboarding",
      "name": "New Onboarding Flow",
      "active": true,
      "rollout_percentage": 100
    },
    {
      "id": "flag_4002",
      "key": "beta-dashboard",
      "name": "Beta Dashboard",
      "active": true,
      "rollout_percentage": 50
    },
    {
      "id": "flag_4003",
      "key": "dark-mode",
      "name": "Dark Mode",
      "active": false,
      "rollout_percentage": 0
    },
    {
      "id": "flag_4004",
      "key": "fast-checkout",
      "name": "Fast Checkout",
      "active": true,
      "roll
```

**GET persons** — `/api/projects/1/persons` (status 200)

```
{
  "results": [
    {
      "id": "per_5001",
      "distinct_ids": [
        "user_3001"
      ],
      "name": "Jordan Reyes",
      "properties": {
        "email": "jordan@example.com",
        "name": "Jordan Reyes"
      },
      "created_at": "2026-04-21T09:00:00Z"
    },
    {
      "id": "per_5002",
      "distinct_ids": [
        "user_3002"
      ],
      "name": "Mira Patel",
      "properties": {
        "email": "mira@example.com",
        "name": "Mira Patel"
      },
      "created_at": "2026-04-23T09:00:00Z"
    },
    {
      "id": "per_5003",
      "distinct_ids": [
       
... (truncated)
```

</details>

### quickbooks-api (port 8007) — server: started

| Result | Method | Path | Status | Endpoint |
|--------|--------|------|--------|----------|
| PASS | GET | /health | 200 | GET /health |
| PASS | GET | /v3/company/4620816365272861350/companyinfo/1 | 200 | GET Company Info |
| PASS | GET | /v3/company/4620816365272861350/query?query=SELECT * FROM Customer | 200 | GET Query All Customers |
| PASS | GET | /v3/company/4620816365272861350/customer/1 | 200 | GET Customer by ID |
| WARN | GET | /v3/company/4620816365272861350/customer/999 | 404 | GET Customer 404 |
| PASS | POST | /v3/company/4620816365272861350/customer | 201 | POST Create Customer |
| PASS | POST | /v3/company/4620816365272861350/customer | 200 | POST Update Customer |
| PASS | GET | /v3/company/4620816365272861350/query?query=SELECT * FROM Vendor | 200 | GET Query All Vendors |
| PASS | GET | /v3/company/4620816365272861350/vendor/1 | 200 | GET Vendor by ID |
| WARN | GET | /v3/company/4620816365272861350/vendor/999 | 404 | GET Vendor 404 |
| PASS | POST | /v3/company/4620816365272861350/vendor | 201 | POST Create Vendor |
| PASS | POST | /v3/company/4620816365272861350/vendor | 200 | POST Update Vendor |
| PASS | GET | /v3/company/4620816365272861350/query?query=SELECT * FROM Item | 200 | GET Query All Items |
| PASS | GET | /v3/company/4620816365272861350/item/1 | 200 | GET Item by ID |
| WARN | GET | /v3/company/4620816365272861350/item/999 | 404 | GET Item 404 |
| PASS | POST | /v3/company/4620816365272861350/item | 201 | POST Create Item |
| PASS | POST | /v3/company/4620816365272861350/item | 200 | POST Update Item |
| PASS | GET | /v3/company/4620816365272861350/query?query=SELECT * FROM Account | 200 | GET Query All Accounts |
| PASS | GET | /v3/company/4620816365272861350/account/3 | 200 | GET Account by ID |
| WARN | GET | /v3/company/4620816365272861350/account/999 | 404 | GET Account 404 |
| PASS | GET | /v3/company/4620816365272861350/query?query=SELECT * FROM Invoice | 200 | GET Query All Invoices |
| PASS | GET | /v3/company/4620816365272861350/query?query=SELECT * FROM Invoice WHERE Balance > '0' | 200 | GET Query Unpaid Invoices |
| PASS | GET | /v3/company/4620816365272861350/query?query=SELECT * FROM Invoice WHERE Status = 'Paid' | 200 | GET Query Invoices by Customer |
| PASS | GET | /v3/company/4620816365272861350/invoice/1201 | 200 | GET Invoice by ID |
| WARN | GET | /v3/company/4620816365272861350/invoice/9999 | 404 | GET Invoice 404 |
| PASS | GET | /v3/company/4620816365272861350/invoice/1201/pdf | 200 | GET Invoice PDF |
| PASS | POST | /v3/company/4620816365272861350/invoice | 201 | POST Create Invoice |
| PASS | POST | /v3/company/4620816365272861350/invoice | 200 | POST Update Invoice |
| PASS | POST | /v3/company/4620816365272861350/invoice/5008?operation=void | 200 | POST Void Invoice |
| PASS | POST | /v3/company/4620816365272861350/invoice/1401?include=send | 200 | POST Send Invoice |
| PASS | GET | /v3/company/4620816365272861350/query?query=SELECT * FROM Bill | 200 | GET Query All Bills |
| PASS | GET | /v3/company/4620816365272861350/query?query=SELECT * FROM Bill WHERE Balance > '0' | 200 | GET Query Open Bills |
| PASS | GET | /v3/company/4620816365272861350/bill/3001 | 200 | GET Bill by ID |
| WARN | GET | /v3/company/4620816365272861350/bill/9999 | 404 | GET Bill 404 |
| PASS | POST | /v3/company/4620816365272861350/bill | 201 | POST Create Bill |
| PASS | POST | /v3/company/4620816365272861350/bill/3002?operation=pay | 200 | POST Pay Bill |
| PASS | GET | /v3/company/4620816365272861350/query?query=SELECT * FROM Payment | 200 | GET Query All Payments |
| PASS | GET | /v3/company/4620816365272861350/payment/4001 | 200 | GET Payment by ID |
| WARN | GET | /v3/company/4620816365272861350/payment/9999 | 404 | GET Payment 404 |
| PASS | POST | /v3/company/4620816365272861350/payment | 201 | POST Record Payment |
| PASS | GET | /v3/company/4620816365272861350/query?query=SELECT * FROM Estimate | 200 | GET Query All Estimates |
| PASS | GET | /v3/company/4620816365272861350/estimate/4001 | 200 | GET Estimate by ID |
| WARN | GET | /v3/company/4620816365272861350/estimate/9999 | 404 | GET Estimate 404 |
| PASS | POST | /v3/company/4620816365272861350/estimate | 201 | POST Create Estimate |
| PASS | POST | /v3/company/4620816365272861350/estimate/4004?operation=convert | 200 | POST Convert Estimate to Invoice |
| PASS | GET | /v3/company/4620816365272861350/query?query=SELECT * FROM Purchase | 200 | GET Query All Purchases |
| PASS | GET | /v3/company/4620816365272861350/purchase/5201 | 200 | GET Expense by ID |
| WARN | GET | /v3/company/4620816365272861350/purchase/9999 | 404 | GET Expense 404 |
| PASS | POST | /v3/company/4620816365272861350/purchase | 201 | POST Create Expense |
| PASS | GET | /v3/company/4620816365272861350/query?query=SELECT * FROM Customer WHERE Active = true | 200 | Query - Active Customers |
| PASS | GET | /v3/company/4620816365272861350/query?query=SELECT * FROM Invoice WHERE Status = 'Overdue' | 200 | Query - Overdue Invoices |
| WARN | GET | /v3/company/4620816365272861350/query?query=INVALID QUERY | 400 | Query - Invalid Query |
| WARN | GET | /v3/company/4620816365272861350/query?query=SELECT * FROM UnknownEntity | 400 | Query - Unknown Entity |
| PASS | GET | /v3/company/4620816365272861350/reports/ProfitAndLoss?start_date=2025-01-01&end_date=2025-04-30 | 200 | GET Profit & Loss |
| PASS | GET | /v3/company/4620816365272861350/reports/ProfitAndLoss | 200 | GET Profit & Loss (no date range) |
| PASS | GET | /v3/company/4620816365272861350/reports/BalanceSheet?start_date=2025-01-01&end_date=2025-04-30 | 200 | GET Balance Sheet |
| PASS | GET | /v3/company/4620816365272861350/reports/AgedReceivableDetail | 200 | GET AR Aging |
| PASS | GET | /v3/company/4620816365272861350/reports/AgedPayableDetail | 200 | GET AP Aging |

<details><summary>responses</summary>

**GET GET /health** — `/health` (status 200)

```
{
  "status": "ok"
}
```

**GET GET Company Info** — `/v3/company/4620816365272861350/companyinfo/1` (status 200)

```
{
  "CompanyInfo": {
    "CompanyName": "Cedar Ridge Martial Arts Academy",
    "LegalName": "Cedar Ridge Martial Arts Academy LLC",
    "CompanyAddr": {
      "Line1": "4827 SW Cedar Hills Blvd",
      "City": "Beaverton",
      "CountrySubDivisionCode": "OR",
      "PostalCode": "97005"
    },
    "Email": {
      "Address": "aaron.delgado@cedarridgemartialarts.com"
    },
    "PrimaryPhone": {
      "FreeFormNumber": "(503) 555-0147"
    },
    "FiscalYearStartMonth": "January",
    "Country": "US",
    "IndustryType": "Sports & Recreation",
    "NameValue": [
      {
        "Name": "Owner
... (truncated)
```

**GET GET Query All Customers** — `/v3/company/4620816365272861350/query?query=SELECT * FROM Customer` (status 200)

```
{
  "QueryResponse": {
    "Customer": [
      {
        "Id": "0",
        "DisplayName": "Multiple - See Batch Detail",
        "PrimaryEmailAddr": null,
        "Balance": 0,
        "Active": true,
        "Notes": "Aggregate: Batch billing placeholder for multi-member invoices"
      },
      {
        "Id": "1",
        "DisplayName": "Abrams, Derek",
        "PrimaryEmailAddr": {
          "Address": "derek.abrams@gmail.com"
        },
        "Balance": 0,
        "Active": true,
        "Notes": "Kendo - M/W/F"
      },
      {
        "Id": "2",
        "DisplayName": "Alvarez, Sofia
... (truncated)
```

**GET GET Customer by ID** — `/v3/company/4620816365272861350/customer/1` (status 200)

```
{
  "Customer": {
    "Id": "1",
    "DisplayName": "Abrams, Derek",
    "PrimaryEmailAddr": {
      "Address": "derek.abrams@gmail.com"
    },
    "Balance": 0,
    "Active": true,
    "Notes": "Kendo - M/W/F"
  }
}
```

**GET GET Customer 404** — `/v3/company/4620816365272861350/customer/999` (status 404)

```
{
  "error": "Customer 999 not found"
}
```

**POST POST Create Customer** — `/v3/company/4620816365272861350/customer` (status 201)

```
{
  "Customer": {
    "Id": "302",
    "DisplayName": "Test Customer LLC",
    "GivenName": "Test",
    "FamilyName": "Customer",
    "CompanyName": null,
    "PrimaryEmailAddr": {
      "Address": "test@example.com"
    },
    "PrimaryPhone": {
      "FreeFormNumber": "(704) 555-9999"
    },
    "BillAddr": null,
    "Balance": 0.0,
    "Active": true,
    "Job": false,
    "Notes": null,
    "MetaData": {
      "CreateTime": "2026-06-17T10:31:33-00:00",
      "LastUpdatedTime": "2026-06-17T10:31:33-00:00"
    },
    "SyncToken": "0"
  }
}
```

**POST POST Update Customer** — `/v3/company/4620816365272861350/customer` (status 200)

```
{
  "Customer": {
    "Id": "1",
    "DisplayName": "Mark Thompson (Updated)",
    "PrimaryEmailAddr": {
      "Address": "derek.abrams@gmail.com"
    },
    "Balance": 0,
    "Active": true,
    "Notes": "Kendo - M/W/F",
    "MetaData": {
      "CreateTime": "2026-06-17T10:31:33-00:00",
      "LastUpdatedTime": "2026-06-17T10:31:33-00:00"
    },
    "SyncToken": "1"
  }
}
```

**GET GET Query All Vendors** — `/v3/company/4620816365272861350/query?query=SELECT * FROM Vendor` (status 200)

```
{
  "QueryResponse": {
    "Vendor": [
      {
        "Id": "1",
        "DisplayName": "Westbrook Property Management",
        "PrimaryEmailAddr": {
          "Address": "leasing@westbrookpm.com"
        },
        "PrimaryPhone": {
          "FreeFormNumber": "(503) 555-0291"
        },
        "Balance": 0,
        "Active": true,
        "Notes": "Landlord - 4827 SW Cedar Hills Blvd. Lease renewed Jan 2026. Current rent $700/mo."
      },
      {
        "Id": "2",
        "DisplayName": "Pacific Northwest Insurance Group",
        "PrimaryEmailAddr": {
          "Address": "commercial@p
... (truncated)
```

**GET GET Vendor by ID** — `/v3/company/4620816365272861350/vendor/1` (status 200)

```
{
  "Vendor": {
    "Id": "1",
    "DisplayName": "Westbrook Property Management",
    "PrimaryEmailAddr": {
      "Address": "leasing@westbrookpm.com"
    },
    "PrimaryPhone": {
      "FreeFormNumber": "(503) 555-0291"
    },
    "Balance": 0,
    "Active": true,
    "Notes": "Landlord - 4827 SW Cedar Hills Blvd. Lease renewed Jan 2026. Current rent $700/mo."
  }
}
```

**GET GET Vendor 404** — `/v3/company/4620816365272861350/vendor/999` (status 404)

```
{
  "error": "Vendor 999 not found"
}
```

**POST POST Create Vendor** — `/v3/company/4620816365272861350/vendor` (status 201)

```
{
  "Vendor": {
    "Id": "405",
    "DisplayName": "New Vendor Inc",
    "CompanyName": "New Vendor Inc",
    "PrimaryEmailAddr": {
      "Address": "vendor@newvendor.com"
    },
    "PrimaryPhone": null,
    "BillAddr": null,
    "Balance": 0.0,
    "Active": true,
    "AcctNum": null,
    "Vendor1099": null,
    "MetaData": {
      "CreateTime": "2026-06-17T10:31:33-00:00",
      "LastUpdatedTime": "2026-06-17T10:31:33-00:00"
    },
    "SyncToken": "0"
  }
}
```

**POST POST Update Vendor** — `/v3/company/4620816365272861350/vendor` (status 200)

```
{
  "Vendor": {
    "Id": "2",
    "DisplayName": "SunPro Nursery (Updated)",
    "PrimaryEmailAddr": {
      "Address": "commercial@pnwig.com"
    },
    "PrimaryPhone": {
      "FreeFormNumber": "(503) 555-0188"
    },
    "Balance": 0,
    "Active": true,
    "Notes": "General liability + property. Policy #PNW-2026-04471. Annual $3,600 paid quarterly ($900/qtr).",
    "MetaData": {
      "CreateTime": "2026-06-17T10:31:33-00:00",
      "LastUpdatedTime": "2026-06-17T10:31:33-00:00"
    },
    "SyncToken": "1"
  }
}
```

**GET GET Query All Items** — `/v3/company/4620816365272861350/query?query=SELECT * FROM Item` (status 200)

```
{
  "QueryResponse": {
    "Item": [
      {
        "Id": "1",
        "Name": "Emergency Motel Stay",
        "Description": "Temporary motel reimbursement for tenant relocation support",
        "Type": "Service",
        "UnitPrice": 418.22,
        "IncomeAccountRef": {
          "value": "1",
          "name": "Reimbursement Grant Revenue"
        },
        "Active": true,
        "Taxable": false,
        "MetaData": {
          "CreateTime": "2026-06-17T10:31:33-00:00",
          "LastUpdatedTime": "2026-06-17T10:31:33-00:00"
        },
        "SyncToken": "0"
      },
      {
      
... (truncated)
```

**GET GET Item by ID** — `/v3/company/4620816365272861350/item/1` (status 200)

```
{
  "Item": {
    "Id": "1",
    "Name": "Emergency Motel Stay",
    "Description": "Temporary motel reimbursement for tenant relocation support",
    "Type": "Service",
    "UnitPrice": 418.22,
    "IncomeAccountRef": {
      "value": "1",
      "name": "Reimbursement Grant Revenue"
    },
    "Active": true,
    "Taxable": false,
    "MetaData": {
      "CreateTime": "2026-06-17T10:31:33-00:00",
      "LastUpdatedTime": "2026-06-17T10:31:33-00:00"
    },
    "SyncToken": "0"
  }
}
```

**GET GET Item 404** — `/v3/company/4620816365272861350/item/999` (status 404)

```
{
  "error": "Item 999 not found"
}
```

**POST POST Create Item** — `/v3/company/4620816365272861350/item` (status 201)

```
{
  "Item": {
    "Id": "10",
    "Name": "Snow Removal",
    "Description": "Snow removal and salting service",
    "Type": "Service",
    "UnitPrice": 150.0,
    "IncomeAccountRef": null,
    "Active": true,
    "Taxable": null,
    "MetaData": {
      "CreateTime": "2026-06-17T10:31:33-00:00",
      "LastUpdatedTime": "2026-06-17T10:31:33-00:00"
    },
    "SyncToken": "0"
  }
}
```

**POST POST Update Item** — `/v3/company/4620816365272861350/item` (status 200)

```
{
  "Item": {
    "Id": "1",
    "Name": "Emergency Motel Stay",
    "Description": "Temporary motel reimbursement for tenant relocation support",
    "Type": "Service",
    "UnitPrice": 80.0,
    "IncomeAccountRef": {
      "value": "1",
      "name": "Reimbursement Grant Revenue"
    },
    "Active": true,
    "Taxable": false,
    "MetaData": {
      "CreateTime": "2026-06-17T10:31:33-00:00",
      "LastUpdatedTime": "2026-06-17T10:31:33-00:00"
    },
    "SyncToken": "1"
  }
}
```

**GET GET Query All Accounts** — `/v3/company/4620816365272861350/query?query=SELECT * FROM Account` (status 200)

```
{
  "QueryResponse": {
    "Account": [
      {
        "Id": "1",
        "Name": "Operating Checking",
        "AccountType": "Bank",
        "AccountSubType": "Checking",
        "CurrentBalance": 5842.5,
        "Active": true,
        "Description": "Primary operating account - OnPoint Credit Union"
      },
      {
        "Id": "2",
        "Name": "Tournament Reserve",
        "AccountType": "Bank",
        "AccountSubType": "Savings",
        "CurrentBalance": 1450.0,
        "Active": true,
        "Description": "Set aside for tournament expenses and equipment replacement"
      },

... (truncated)
```

**GET GET Account by ID** — `/v3/company/4620816365272861350/account/3` (status 200)

```
{
  "Account": {
    "Id": "3",
    "Name": "Membership Income",
    "AccountType": "Income",
    "AccountSubType": "ServiceFeeIncome",
    "CurrentBalance": 0,
    "Active": true,
    "Description": "Monthly membership dues - $95/member"
  }
}
```

**GET GET Account 404** — `/v3/company/4620816365272861350/account/999` (status 404)

```
{
  "error": "Account 999 not found"
}
```

**GET GET Query All Invoices** — `/v3/company/4620816365272861350/query?query=SELECT * FROM Invoice` (status 200)

```
{
  "QueryResponse": {
    "Invoice": [
      {
        "Id": "5001",
        "DocNumber": "INV-2026-0301",
        "TxnDate": "2026-03-01",
        "DueDate": "2026-03-10",
        "CustomerRef": {
          "value": "1",
          "name": "Abrams, Derek"
        },
        "Line": [
          {
            "Amount": 95.0,
            "Description": "Monthly Membership - March 2026",
            "SalesItemLineDetail": {
              "ItemRef": {
                "name": "Membership Income"
              }
            }
          }
        ],
        "TotalAmt": 95.0,
        "Balance": 0,
   
... (truncated)
```

**GET GET Query Unpaid Invoices** — `/v3/company/4620816365272861350/query?query=SELECT * FROM Invoice WHERE Balance > '0'` (status 200)

```
{
  "QueryResponse": {
    "Invoice": [
      {
        "Id": "2003",
        "DocNumber": "INV-2026-0403",
        "TxnDate": "2026-04-01",
        "DueDate": "2026-04-10",
        "CustomerRef": {
          "value": "5",
          "name": "Callahan, Nate"
        },
        "Line": [
          {
            "Amount": 95.0,
            "Description": "Monthly Membership - April 2026",
            "SalesItemLineDetail": {
              "ItemRef": {
                "name": "Membership Income"
              }
            }
          }
        ],
        "TotalAmt": 95.0,
        "Balance": 95.0,
... (truncated)
```

**GET GET Query Invoices by Customer** — `/v3/company/4620816365272861350/query?query=SELECT * FROM Invoice WHERE Status = 'Paid'` (status 200)

```
{
  "QueryResponse": {
    "Invoice": [
      {
        "Id": "5001",
        "DocNumber": "INV-2026-0301",
        "TxnDate": "2026-03-01",
        "DueDate": "2026-03-10",
        "CustomerRef": {
          "value": "1",
          "name": "Abrams, Derek"
        },
        "Line": [
          {
            "Amount": 95.0,
            "Description": "Monthly Membership - March 2026",
            "SalesItemLineDetail": {
              "ItemRef": {
                "name": "Membership Income"
              }
            }
          }
        ],
        "TotalAmt": 95.0,
        "Balance": 0,
   
... (truncated)
```

**GET GET Invoice by ID** — `/v3/company/4620816365272861350/invoice/1201` (status 200)

```
{
  "Invoice": {
    "Id": "1201",
    "DocNumber": "ISC-2024-009",
    "TxnDate": "2024-04-10",
    "DueDate": "2024-04-20",
    "CustomerRef": {
      "value": "203",
      "name": "Marcus Webb"
    },
    "TotalAmt": 1800000.0,
    "Balance": 1800000.0,
    "Line": [
      {
        "Description": "Penetration Testing - TechVault Portal",
        "Amount": 600000.0
      },
      {
        "Description": "Infrastructure Security Audit",
        "Amount": 480000.0
      },
      {
        "Description": "API Vulnerability Assessment",
        "Amount": 360000.0
      },
      {
        "Desc
... (truncated)
```

**GET GET Invoice 404** — `/v3/company/4620816365272861350/invoice/9999` (status 404)

```
{
  "error": "Invoice 9999 not found"
}
```

**GET GET Invoice PDF** — `/v3/company/4620816365272861350/invoice/1201/pdf` (status 200)

```
{
  "url": "https://quickbooks.api.intuit.com/v3/company/4620816365272861350/invoice/1201/pdf"
}
```

**POST POST Create Invoice** — `/v3/company/4620816365272861350/invoice` (status 201)

```
{
  "Invoice": {
    "Id": "5009",
    "DocNumber": "5009",
    "TxnDate": "2025-05-01",
    "DueDate": "2025-05-31",
    "CustomerRef": {
      "value": "1",
      "name": "Mark Thompson"
    },
    "Line": [
      {
        "Amount": 150.0,
        "DetailType": "SalesItemLineDetail",
        "Description": "Test mowing service",
        "SalesItemLineDetail": {
          "ItemRef": {
            "value": "1",
            "name": "Weekly Lawn Mowing"
          },
          "UnitPrice": 75.0,
          "Qty": 2
        }
      },
      {
        "Amount": 150.0,
        "DetailType": "SubTota
... (truncated)
```

**POST POST Update Invoice** — `/v3/company/4620816365272861350/invoice` (status 200)

```
{
  "Invoice": {
    "Id": "1201",
    "DocNumber": "ISC-2024-009",
    "TxnDate": "2024-04-10",
    "DueDate": "2025-04-15",
    "CustomerRef": {
      "value": "203",
      "name": "Marcus Webb"
    },
    "TotalAmt": 1800000.0,
    "Balance": 1800000.0,
    "Line": [
      {
        "Description": "Penetration Testing - TechVault Portal",
        "Amount": 600000.0
      },
      {
        "Description": "Infrastructure Security Audit",
        "Amount": 480000.0
      },
      {
        "Description": "API Vulnerability Assessment",
        "Amount": 360000.0
      },
      {
        "Desc
... (truncated)
```

**POST POST Void Invoice** — `/v3/company/4620816365272861350/invoice/5008?operation=void` (status 200)

```
{
  "Invoice": {
    "Id": "5008",
    "DocNumber": "INV-2026-0307",
    "TxnDate": "2026-03-19",
    "DueDate": "2026-03-19",
    "CustomerRef": {
      "value": "64",
      "name": "Drop-in Sessions (Walk-ins)"
    },
    "Line": [
      {
        "Amount": 60.0,
        "Description": "Drop-in fees collected - second half March (3 sessions \u00d7 $20)",
        "SalesItemLineDetail": {
          "ItemRef": {
            "name": "Drop-in Fees"
          }
        }
      }
    ],
    "TotalAmt": 60.0,
    "Balance": 0.0,
    "Status": "Voided",
    "MetaData": {
      "CreateTime": "2026-06-
```

**POST POST Send Invoice** — `/v3/company/4620816365272861350/invoice/1401?include=send` (status 200)

```
{
  "Invoice": {
    "Id": "1401",
    "DocNumber": "BAR-1101",
    "TxnDate": "2025-04-18",
    "DueDate": "2025-04-18",
    "CustomerRef": {
      "value": "301",
      "name": "Bar Walk-In"
    },
    "Line": [
      {
        "Id": "1",
        "LineNum": 1,
        "Amount": 54.0,
        "DetailType": "SalesItemLineDetail",
        "Description": "Buffalo Trace pours",
        "SalesItemLineDetail": {
          "ItemRef": {
            "value": "401",
            "name": "Buffalo Trace"
          },
          "UnitPrice": 18.0,
          "Qty": 3
        }
      },
      {
        "Amoun
... (truncated)
```

**GET GET Query All Bills** — `/v3/company/4620816365272861350/query?query=SELECT * FROM Bill` (status 200)

```
{
  "QueryResponse": {
    "Bill": [
      {
        "Id": "3001",
        "DocNumber": "RENT-2026-03",
        "VendorRef": {
          "value": "1",
          "name": "Westbrook Property Management"
        },
        "TxnDate": "2026-03-01",
        "DueDate": "2026-03-05",
        "Line": [
          {
            "Amount": 700.0,
            "Description": "Monthly rent - March 2026. 4827 SW Cedar Hills Blvd.",
            "AccountBasedExpenseLineDetail": {
              "AccountRef": {
                "name": "Rent Expense",
                "value": "7"
              }
            }
    
... (truncated)
```

**GET GET Query Open Bills** — `/v3/company/4620816365272861350/query?query=SELECT * FROM Bill WHERE Balance > '0'` (status 200)

```
{
  "QueryResponse": {
    "Bill": [
      {
        "Id": "3016",
        "DocNumber": "BSC-2026-04",
        "VendorRef": {
          "value": "5",
          "name": "Bushido Supply Co."
        },
        "TxnDate": "2026-04-10",
        "DueDate": "2026-05-10",
        "Line": [
          {
            "Amount": 425.0,
            "Description": "Quarterly restock: shinai (12), bokken (6), mat cleaner (4 gal). PO#BSC-2290.",
            "AccountBasedExpenseLineDetail": {
              "AccountRef": {
                "name": "Supplies & Equipment",
                "value": "11"
            
... (truncated)
```

**GET GET Bill by ID** — `/v3/company/4620816365272861350/bill/3001` (status 200)

```
{
  "Bill": {
    "Id": "3001",
    "DocNumber": "RENT-2026-03",
    "VendorRef": {
      "value": "1",
      "name": "Westbrook Property Management"
    },
    "TxnDate": "2026-03-01",
    "DueDate": "2026-03-05",
    "Line": [
      {
        "Amount": 700.0,
        "Description": "Monthly rent - March 2026. 4827 SW Cedar Hills Blvd.",
        "AccountBasedExpenseLineDetail": {
          "AccountRef": {
            "name": "Rent Expense",
            "value": "7"
          }
        }
      }
    ],
    "TotalAmt": 700.0,
    "Balance": 0,
    "PrivateNote": "Paid on time."
  }
}
```

**GET GET Bill 404** — `/v3/company/4620816365272861350/bill/9999` (status 404)

```
{
  "error": "Bill 9999 not found"
}
```

**POST POST Create Bill** — `/v3/company/4620816365272861350/bill` (status 201)

```
{
  "Bill": {
    "Id": "3402",
    "VendorRef": {
      "value": "1",
      "name": "Charlotte Fuel Depot"
    },
    "TxnDate": "2025-05-01",
    "DueDate": "2025-05-31",
    "TotalAmt": 350.0,
    "Balance": 350.0,
    "Line": [
      {
        "Amount": 350.0,
        "DetailType": "AccountBasedExpenseLineDetail",
        "Description": "Diesel fuel - test",
        "AccountBasedExpenseLineDetail": {
          "AccountRef": {
            "value": "7",
            "name": "Fuel Expense"
          }
        }
      }
    ],
    "Status": "Open",
    "DocNumber": null,
    "MetaData": {
     
```

**POST POST Pay Bill** — `/v3/company/4620816365272861350/bill/3002?operation=pay` (status 200)

```
{
  "Bill": {
    "Id": "3002",
    "DocNumber": "PGE-2026-03",
    "VendorRef": {
      "value": "3",
      "name": "Portland General Electric"
    },
    "TxnDate": "2026-03-12",
    "DueDate": "2026-03-28",
    "Line": [
      {
        "Amount": 185.0,
        "Description": "Electric service Feb 10 - Mar 10. Acct #8827-4401-55.",
        "AccountBasedExpenseLineDetail": {
          "AccountRef": {
            "name": "Utilities",
            "value": "8"
          }
        }
      }
    ],
    "TotalAmt": 185.0,
    "Balance": 0.0,
    "Status": "Paid",
    "MetaData": {
      "CreateTim
```

**GET GET Query All Payments** — `/v3/company/4620816365272861350/query?query=SELECT * FROM Payment` (status 200)

```
{
  "QueryResponse": {
    "Payment": [
      {
        "Id": "4001",
        "TxnDate": "2026-03-03",
        "CustomerRef": {
          "value": "1",
          "name": "Abrams, Derek"
        },
        "TotalAmt": 95.0,
        "Line": [
          {
            "LinkedTxn": [
              {
                "TxnId": "5001",
                "TxnType": "Invoice"
              }
            ],
            "Amount": 95.0
          }
        ],
        "PrivateNote": "Check #1204"
      },
      {
        "Id": "4002",
        "TxnDate": "2026-03-04",
        "CustomerRef": {
          "value": 
... (truncated)
```

**GET GET Payment by ID** — `/v3/company/4620816365272861350/payment/4001` (status 200)

```
{
  "Payment": {
    "Id": "4001",
    "TxnDate": "2026-03-03",
    "CustomerRef": {
      "value": "1",
      "name": "Abrams, Derek"
    },
    "TotalAmt": 95.0,
    "Line": [
      {
        "LinkedTxn": [
          {
            "TxnId": "5001",
            "TxnType": "Invoice"
          }
        ],
        "Amount": 95.0
      }
    ],
    "PrivateNote": "Check #1204"
  }
}
```

**GET GET Payment 404** — `/v3/company/4620816365272861350/payment/9999` (status 404)

```
{
  "error": "Payment 9999 not found"
}
```

**POST POST Record Payment** — `/v3/company/4620816365272861350/payment` (status 201)

```
{
  "Payment": {
    "Id": "4020",
    "TxnDate": "2025-05-01",
    "CustomerRef": {
      "value": "4",
      "name": "Patricia Nguyen"
    },
    "TotalAmt": 150.0,
    "Line": [
      {
        "Amount": 150.0,
        "LinkedTxn": [
          {
            "TxnId": "1009",
            "TxnType": "Invoice"
          }
        ]
      }
    ],
    "MetaData": {
      "CreateTime": "2026-06-17T10:31:33-00:00",
      "LastUpdatedTime": "2026-06-17T10:31:33-00:00"
    },
    "SyncToken": "0"
  }
}
```

**GET GET Query All Estimates** — `/v3/company/4620816365272861350/query?query=SELECT * FROM Estimate` (status 200)

```
{
  "QueryResponse": {
    "Estimate": [
      {
        "Id": "4001",
        "DocNumber": "E-1001",
        "TxnDate": "2025-02-01",
        "ExpirationDate": "2025-03-03",
        "CustomerRef": {
          "value": "7",
          "name": "Amanda Foster"
        },
        "Line": [
          {
            "Id": "1",
            "LineNum": 1,
            "Amount": 4500.0,
            "DetailType": "SalesItemLineDetail",
            "Description": "Paver patio installation - approx 250 sq ft",
            "SalesItemLineDetail": {
              "ItemRef": {
                "value": "7",
     
... (truncated)
```

**GET GET Estimate by ID** — `/v3/company/4620816365272861350/estimate/4001` (status 200)

```
{
  "Estimate": {
    "Id": "4001",
    "DocNumber": "E-1001",
    "TxnDate": "2025-02-01",
    "ExpirationDate": "2025-03-03",
    "CustomerRef": {
      "value": "7",
      "name": "Amanda Foster"
    },
    "Line": [
      {
        "Id": "1",
        "LineNum": 1,
        "Amount": 4500.0,
        "DetailType": "SalesItemLineDetail",
        "Description": "Paver patio installation - approx 250 sq ft",
        "SalesItemLineDetail": {
          "ItemRef": {
            "value": "7",
            "name": "Hardscaping - Patio/Walkway"
          },
          "UnitPrice": 18.0,
          "Qty":
... (truncated)
```

**GET GET Estimate 404** — `/v3/company/4620816365272861350/estimate/9999` (status 404)

```
{
  "error": "Estimate 9999 not found"
}
```

**POST POST Create Estimate** — `/v3/company/4620816365272861350/estimate` (status 201)

```
{
  "Estimate": {
    "Id": "4008",
    "DocNumber": "E-4008",
    "TxnDate": "2025-05-01",
    "ExpirationDate": "2025-05-31",
    "CustomerRef": {
      "value": "18",
      "name": "Daniel Harris"
    },
    "Line": [
      {
        "Amount": 500.0,
        "DetailType": "SalesItemLineDetail",
        "Description": "Spring cleanup and mulching",
        "SalesItemLineDetail": {
          "ItemRef": {
            "value": "4",
            "name": "Spring Cleanup"
          },
          "UnitPrice": 250.0,
          "Qty": 2
        }
      }
    ],
    "TotalAmt": 500.0,
    "TxnStatus": "
```

**POST POST Convert Estimate to Invoice** — `/v3/company/4620816365272861350/estimate/4004?operation=convert` (status 200)

```
{
  "Invoice": {
    "Id": "5010",
    "DocNumber": "5010",
    "TxnDate": "2026-06-17",
    "DueDate": "2026-06-17",
    "CustomerRef": {
      "value": "25",
      "name": "Sandra Phillips"
    },
    "Line": [
      {
        "Id": "1",
        "LineNum": 1,
        "Amount": 950.0,
        "DetailType": "SalesItemLineDetail",
        "Description": "Full front yard landscape redesign with seasonal plantings",
        "SalesItemLineDetail": {
          "ItemRef": {
            "value": "10",
            "name": "Landscape Design Plan"
          },
          "UnitPrice": 450.0,
          "Qt
... (truncated)
```

**GET GET Query All Purchases** — `/v3/company/4620816365272861350/query?query=SELECT * FROM Purchase` (status 200)

```
{
  "QueryResponse": {
    "Purchase": [
      {
        "Id": "5201",
        "TxnDate": "2024-04-01",
        "TotalAmt": 6500.0,
        "Line": [
          {
            "Description": "Splice - Monthly sample subscription",
            "Amount": 6500.0
          }
        ],
        "MetaData": {
          "CreateTime": "2024-04-01T09:00:00"
        }
      },
      {
        "Id": "5202",
        "TxnDate": "2024-04-01",
        "TotalAmt": 42000.0,
        "Line": [
          {
            "Description": "Ableton - Live 12 Suite renewal",
            "Amount": 42000.0
          }
      
... (truncated)
```

**GET GET Expense by ID** — `/v3/company/4620816365272861350/purchase/5201` (status 200)

```
{
  "Purchase": {
    "Id": "5201",
    "TxnDate": "2024-04-01",
    "TotalAmt": 6500.0,
    "Line": [
      {
        "Description": "Splice - Monthly sample subscription",
        "Amount": 6500.0
      }
    ],
    "MetaData": {
      "CreateTime": "2024-04-01T09:00:00"
    }
  }
}
```

**GET GET Expense 404** — `/v3/company/4620816365272861350/purchase/9999` (status 404)

```
{
  "error": "Expense 9999 not found"
}
```

**POST POST Create Expense** — `/v3/company/4620816365272861350/purchase` (status 201)

```
{
  "Purchase": {
    "Id": "5208",
    "TxnDate": "2025-05-01",
    "AccountRef": {
      "value": "7",
      "name": "Fuel Expense"
    },
    "PaymentType": "Cash",
    "TotalAmt": 60.0,
    "Line": [
      {
        "Amount": 60.0,
        "DetailType": "AccountBasedExpenseLineDetail",
        "Description": "Gas for equipment",
        "AccountBasedExpenseLineDetail": {
          "AccountRef": {
            "value": "7",
            "name": "Fuel Expense"
          }
        }
      }
    ],
    "MetaData": {
      "CreateTime": "2026-06-17T10:31:33-00:00",
      "LastUpdatedTime": "2026-
```

**GET Query - Active Customers** — `/v3/company/4620816365272861350/query?query=SELECT * FROM Customer WHERE Active = true` (status 200)

```
{
  "QueryResponse": {
    "Customer": [
      {
        "Id": "0",
        "DisplayName": "Multiple - See Batch Detail",
        "PrimaryEmailAddr": null,
        "Balance": 0,
        "Active": true,
        "Notes": "Aggregate: Batch billing placeholder for multi-member invoices"
      },
      {
        "Id": "1",
        "DisplayName": "Mark Thompson (Updated)",
        "PrimaryEmailAddr": {
          "Address": "derek.abrams@gmail.com"
        },
        "Balance": 0,
        "Active": true,
        "Notes": "Kendo - M/W/F",
        "MetaData": {
          "CreateTime": "2026-06-17T10:31
... (truncated)
```

**GET Query - Overdue Invoices** — `/v3/company/4620816365272861350/query?query=SELECT * FROM Invoice WHERE Status = 'Overdue'` (status 200)

```
{
  "QueryResponse": {
    "Invoice": [
      {
        "Id": "2003",
        "DocNumber": "INV-2026-0403",
        "TxnDate": "2026-04-01",
        "DueDate": "2026-04-10",
        "CustomerRef": {
          "value": "5",
          "name": "Callahan, Nate"
        },
        "Line": [
          {
            "Amount": 95.0,
            "Description": "Monthly Membership - April 2026",
            "SalesItemLineDetail": {
              "ItemRef": {
                "name": "Membership Income"
              }
            }
          }
        ],
        "TotalAmt": 95.0,
        "Balance": 95.0,
... (truncated)
```

**GET Query - Invalid Query** — `/v3/company/4620816365272861350/query?query=INVALID QUERY` (status 400)

```
{
  "error": "Invalid query syntax: INVALID QUERY"
}
```

**GET Query - Unknown Entity** — `/v3/company/4620816365272861350/query?query=SELECT * FROM UnknownEntity` (status 400)

```
{
  "error": "Unknown entity: UnknownEntity"
}
```

**GET GET Profit & Loss** — `/v3/company/4620816365272861350/reports/ProfitAndLoss?start_date=2025-01-01&end_date=2025-04-30` (status 200)

```
{
  "Header": {
    "ReportName": "ProfitAndLoss",
    "StartPeriod": "2025-01-01",
    "EndPeriod": "2025-04-30",
    "Currency": "USD",
    "Option": [
      {
        "Name": "AccountingMethod",
        "Value": "Accrual"
      }
    ]
  },
  "Rows": {
    "Row": [
      {
        "group": "Income",
        "Summary": {
          "ColData": [
            {
              "value": "Total Income"
            },
            {
              "value": "134.00"
            }
          ]
        },
        "Rows": {
          "Row": [
            {
              "ColData": [
                {
      
```

**GET GET Profit & Loss (no date range)** — `/v3/company/4620816365272861350/reports/ProfitAndLoss` (status 200)

```
{
  "Header": {
    "ReportName": "ProfitAndLoss",
    "StartPeriod": "2025-01-01",
    "EndPeriod": "2025-12-31",
    "Currency": "USD",
    "Option": [
      {
        "Name": "AccountingMethod",
        "Value": "Accrual"
      }
    ]
  },
  "Rows": {
    "Row": [
      {
        "group": "Income",
        "Summary": {
          "ColData": [
            {
              "value": "Total Income"
            },
            {
              "value": "13429.00"
            }
          ]
        },
        "Rows": {
          "Row": [
            {
              "ColData": [
                {
    
... (truncated)
```

**GET GET Balance Sheet** — `/v3/company/4620816365272861350/reports/BalanceSheet?start_date=2025-01-01&end_date=2025-04-30` (status 200)

```
{
  "Header": {
    "ReportName": "BalanceSheet",
    "StartPeriod": "2025-01-01",
    "EndPeriod": "2025-04-30",
    "Currency": "USD"
  },
  "Rows": {
    "Row": [
      {
        "group": "Assets",
        "Summary": {
          "ColData": [
            {
              "value": "Total Assets"
            },
            {
              "value": "1864180.00"
            }
          ]
        },
        "Rows": {
          "Row": [
            {
              "ColData": [
                {
                  "value": "Business Checking"
                },
                {
                  "va
... (truncated)
```

**GET GET AR Aging** — `/v3/company/4620816365272861350/reports/AgedReceivableDetail` (status 200)

```
{
  "Header": {
    "ReportName": "AgedReceivableDetail",
    "ReportBasis": "Accrual",
    "Currency": "USD"
  },
  "Rows": {
    "Row": [
      {
        "ColData": [
          {
            "value": "Current"
          },
          {
            "value": "1450.00"
          }
        ],
        "Details": [
          {
            "CustomerRef": {
              "value": "25",
              "name": "Sandra Phillips"
            },
            "Balance": 1450.0,
            "DueDate": "2026-06-17"
          }
        ]
      },
      {
        "ColData": [
          {
            "value": "1-
... (truncated)
```

**GET GET AP Aging** — `/v3/company/4620816365272861350/reports/AgedPayableDetail` (status 200)

```
{
  "Header": {
    "ReportName": "AgedPayableDetail",
    "ReportBasis": "Accrual",
    "Currency": "USD"
  },
  "Rows": {
    "Row": [
      {
        "ColData": [
          {
            "value": "Current"
          },
          {
            "value": "0.00"
          }
        ],
        "Details": []
      },
      {
        "ColData": [
          {
            "value": "1-30"
          },
          {
            "value": "1298.50"
          }
        ],
        "Details": [
          {
            "VendorRef": {
              "value": "401",
              "name": "Marine Catch Seafood"
 
... (truncated)
```

</details>

### reddit-api (port 8058) — server: started

| Result | Method | Path | Status | Endpoint |
|--------|--------|------|--------|----------|
| PASS | GET | /health | 200 | health |
| PASS | GET | /r/programming/about | 200 | subreddit about |
| PASS | GET | /r/programming/hot?limit=10 | 200 | subreddit hot |
| PASS | GET | /r/homelab/new?limit=10 | 200 | subreddit new |
| PASS | GET | /comments/t3_p001 | 200 | post comments |
| PASS | POST | /api/submit | 200 | submit post |
| PASS | POST | /api/vote | 200 | vote up |
| PASS | GET | /user/devkat/about | 200 | user about |

<details><summary>responses</summary>

**GET health** — `/health` (status 200)

```
{
  "status": "ok"
}
```

**GET subreddit about** — `/r/programming/about` (status 200)

```
{
  "kind": "t5",
  "data": {
    "id": "t5_aaa001",
    "display_name": "programming",
    "title": "Programming",
    "public_description": "Computer programming news and discussion",
    "subscribers": 6800000,
    "created_utc": 1201234567.0,
    "over18": false
  }
}
```

**GET subreddit hot** — `/r/programming/hot?limit=10` (status 200)

```
{
  "kind": "Listing",
  "data": {
    "after": null,
    "before": null,
    "children": [
      {
        "kind": "t3",
        "data": {
          "id": "t3_p001",
          "subreddit": "programming",
          "title": "Why I switched from REST to gRPC for internal services",
          "author": "devkat",
          "url": "https://example.com/grpc-post",
          "selftext": "",
          "score": 1820,
          "ups": 1820,
          "num_comments": 3,
          "created_utc": 1716800000.0,
          "is_self": false,
          "_likes": null
        }
      },
      {
        "kind": 
... (truncated)
```

**GET subreddit new** — `/r/homelab/new?limit=10` (status 200)

```
{
  "kind": "Listing",
  "data": {
    "after": null,
    "before": null,
    "children": [
      {
        "kind": "t3",
        "data": {
          "id": "t3_p004",
          "subreddit": "homelab",
          "title": "PSA: label your cables before you regret it",
          "author": "cablechaos",
          "url": null,
          "selftext": "A cautionary tale about an unlabeled patch panel and a long debugging night.",
          "score": 990,
          "ups": 990,
          "num_comments": 1,
          "created_utc": 1716720000.0,
          "is_self": true,
          "_likes": null
        
... (truncated)
```

**GET post comments** — `/comments/t3_p001` (status 200)

```
[
  {
    "kind": "Listing",
    "data": {
      "after": null,
      "before": null,
      "children": [
        {
          "kind": "t3",
          "data": {
            "id": "t3_p001",
            "subreddit": "programming",
            "title": "Why I switched from REST to gRPC for internal services",
            "author": "devkat",
            "url": "https://example.com/grpc-post",
            "selftext": "",
            "score": 1820,
            "ups": 1820,
            "num_comments": 3,
            "created_utc": 1716800000.0,
            "is_self": false,
            "_likes": null
... (truncated)
```

**POST submit post** — `/api/submit` (status 200)

```
{
  "json": {
    "errors": [],
    "data": {
      "id": "t3_694a8a",
      "name": "t3_694a8a",
      "url": "https://example.com/csv-diff"
    }
  }
}
```

**POST vote up** — `/api/vote` (status 200)

```
{
  "name": "t3_p002",
  "score": 641,
  "likes": true
}
```

**GET user about** — `/user/devkat/about` (status 200)

```
{
  "kind": "t2",
  "data": {
    "name": "devkat",
    "id": "t2_u001",
    "link_karma": 18400,
    "comment_karma": 9200,
    "created_utc": 1401234567.0,
    "is_gold": true,
    "is_mod": false
  }
}
```

</details>

### ring-api (port 8008) — server: started

| Result | Method | Path | Status | Endpoint |
|--------|--------|------|--------|----------|
| PASS | GET | /health | 200 | Health Check |
| PASS | GET | /clients_api/ring_devices | 200 | List All Devices |
| PASS | GET | /clients_api/doorbots/987001 | 200 | Get Device - Doorbell Front |
| PASS | GET | /clients_api/doorbots/987003 | 200 | Get Device - Driveway Cam |
| PASS | GET | /clients_api/doorbots/987005 | 200 | Get Device - Side Gate |
| PASS | GET | /clients_api/doorbots/987006 | 200 | Get Device - Chime |
| WARN | GET | /clients_api/doorbots/999999 | 404 | Get Device - Not Found (404) |
| PASS | GET | /clients_api/doorbots/987001/health | 200 | Get Device Health - Doorbell |
| PASS | GET | /clients_api/doorbots/987003/health | 200 | Get Device Health - Driveway (weak WiFi) |
| PASS | GET | /clients_api/doorbots/987005/health | 200 | Get Device Health - Side Gate (low battery) |
| WARN | GET | /clients_api/doorbots/999999/health | 404 | Get Device Health - Not Found (404) |
| PASS | PUT | /clients_api/doorbots/987001/settings | 200 | Update Device Settings - Motion Sensitivity |
| PASS | PUT | /clients_api/doorbots/987004/settings | 200 | Update Device Settings - Toggle LED |
| WARN | PUT | /clients_api/doorbots/999999/settings | 404 | Update Device Settings - Not Found (404) |
| PASS | GET | /clients_api/locations/loc_martinez_001 | 200 | Get Location |
| WARN | GET | /clients_api/locations/loc_unknown_999 | 404 | Get Location - Not Found (404) |
| PASS | GET | /clients_api/locations/loc_martinez_001/devices | 200 | List Location Devices |
| PASS | GET | /clients_api/locations/loc_martinez_001/mode | 200 | Get Location Mode |
| PASS | PUT | /clients_api/locations/loc_martinez_001/mode | 200 | Set Location Mode - Away |
| PASS | PUT | /clients_api/locations/loc_martinez_001/mode | 200 | Set Location Mode - Home |
| WARN | PUT | /clients_api/locations/loc_martinez_001/mode | 400 | Set Location Mode - Invalid |
| PASS | GET | /clients_api/doorbots/987001/history | 200 | List Doorbell Events (all) |
| PASS | GET | /clients_api/doorbots/987001/history?kind=ding | 200 | List Doorbell Events - Dings only |
| PASS | GET | /clients_api/doorbots/987001/history?kind=motion | 200 | List Doorbell Events - Motion only |
| PASS | GET | /clients_api/doorbots/987001/history?kind=package_detected | 200 | List Doorbell Events - Package detected |
| PASS | GET | /clients_api/doorbots/987003/history | 200 | List Driveway Cam Events |
| PASS | GET | /clients_api/doorbots/987002/history | 200 | List Backyard Cam Events |
| PASS | GET | /clients_api/doorbots/987001/history?date_from=2025-04-28T00:00:00.000Z&date_to=2025-04-28T23:59:59.000Z | 200 | List Events - Today only |
| PASS | GET | /clients_api/doorbots/987001/history?date_from=2025-04-27T14:30:00.000Z | 200 | List Events - Last 24h |
| PASS | GET | /clients_api/doorbots/987001/history?limit=5&offset=0 | 200 | List Events - With pagination |
| PASS | GET | /clients_api/doorbots/987001/history?limit=5&offset=5 | 200 | List Events - Page 2 |
| PASS | GET | /clients_api/dings/7001 | 200 | Get Single Event |
| WARN | GET | /clients_api/dings/99999 | 404 | Get Single Event - Not Found (404) |
| PASS | GET | /clients_api/dings/7001/recording | 200 | Get Event Recording URL |
| WARN | GET | /clients_api/dings/99999/recording | 404 | Get Event Recording - Not Found (404) |
| PASS | GET | /clients_api/dings/active | 200 | List Active Dings |
| PASS | GET | /clients_api/doorbots/987001/recordings | 200 | List Recordings - Doorbell |
| PASS | GET | /clients_api/doorbots/987003/recordings | 200 | List Recordings - Driveway Cam |
| PASS | GET | /clients_api/doorbots/987001/recordings?date_from=2025-04-25T00:00:00.000Z&date_to=2025-04-26T23:59:59.000Z | 200 | List Recordings - Date Range |
| PASS | GET | /clients_api/locations/loc_martinez_001/users | 200 | List Shared Users |
| PASS | GET | /clients_api/locations/loc_martinez_001/users/100001 | 200 | Get Shared User - Carlos (owner) |
| PASS | GET | /clients_api/locations/loc_martinez_001/users/100003 | 200 | Get Shared User - Tom (guest) |
| WARN | GET | /clients_api/locations/loc_martinez_001/users/999999 | 404 | Get Shared User - Not Found (404) |
| PASS | GET | /clients_api/chimes/987006/settings | 200 | Get Chime Settings |
| WARN | GET | /clients_api/chimes/987001/settings | 404 | Get Chime Settings - Not a Chime (404) |
| PASS | PUT | /clients_api/chimes/987006/link | 200 | Link Chime to Doorbell |
| PASS | PUT | /clients_api/chimes/987006/unlink | 200 | Unlink Chime from Doorbell |
| PASS | GET | /clients_api/doorbots/987001/motion_zones | 200 | List Motion Zones - Doorbell |
| PASS | GET | /clients_api/doorbots/987003/motion_zones | 200 | List Motion Zones - Driveway |
| WARN | GET | /clients_api/doorbots/999999/motion_zones | 404 | List Motion Zones - Not Found (404) |
| PASS | GET | /clients_api/notifications | 200 | List All Notification Preferences |
| PASS | GET | /clients_api/notifications/987001 | 200 | Get Notification Pref - Doorbell |
| PASS | GET | /clients_api/notifications/987004 | 200 | Get Notification Pref - Living Room (alerts off) |
| WARN | GET | /clients_api/notifications/999999 | 404 | Get Notification Pref - Not Found (404) |
| PASS | PUT | /clients_api/notifications/987002 | 200 | Update Notification Pref - Toggle Motion Alerts Off |
| PASS | PUT | /clients_api/notifications/987004 | 200 | Update Notification Pref - Toggle Motion Alerts On |
| PASS | POST | /clients_api/doorbots/987003/siren_on | 200 | Activate Siren - Driveway |
| PASS | POST | /clients_api/doorbots/987003/siren_off | 200 | Deactivate Siren - Driveway |
| PASS | POST | /clients_api/doorbots/987002/siren_on | 200 | Activate Siren - No Siren (404) |
| PASS | PUT | /clients_api/doorbots/987003/floodlight_light_on | 200 | Turn Floodlight On |
| PASS | PUT | /clients_api/doorbots/987003/floodlight_light_on | 200 | Turn Floodlight Off |
| PASS | PUT | /clients_api/doorbots/987002/floodlight_light_on | 200 | Floodlight - No Floodlight (404) |

<details><summary>responses</summary>

**GET Health Check** — `/health` (status 200)

```
{
  "status": "ok"
}
```

**GET List All Devices** — `/clients_api/ring_devices` (status 200)

```
{
  "doorbots": [
    {
      "id": 987001,
      "description": "Front Door",
      "device_id": "doorbell_front",
      "address": "4821 Ridgeview Dr",
      "kind": "lpd_v2",
      "firmware_version": "3.22.8",
      "battery_life": 82,
      "external_connection": true,
      "latitude": 30.2241,
      "longitude": -97.8416,
      "location_id": "loc_martinez_001",
      "time_zone": "America/Chicago",
      "alerts": {
        "connection": "online"
      },
      "features": {
        "motions_enabled": true,
        "show_recordings": true,
        "advanced_motion_enabled": true,
     
... (truncated)
```

**GET Get Device - Doorbell Front** — `/clients_api/doorbots/987001` (status 200)

```
{
  "type": "device",
  "device_type": "doorbots",
  "device": {
    "id": 987001,
    "description": "Front Door",
    "device_id": "doorbell_front",
    "address": "4821 Ridgeview Dr",
    "kind": "lpd_v2",
    "firmware_version": "3.22.8",
    "battery_life": 82,
    "external_connection": true,
    "latitude": 30.2241,
    "longitude": -97.8416,
    "location_id": "loc_martinez_001",
    "time_zone": "America/Chicago",
    "alerts": {
      "connection": "online"
    },
    "features": {
      "motions_enabled": true,
      "show_recordings": true,
      "advanced_motion_enabled": true,
  
... (truncated)
```

**GET Get Device - Driveway Cam** — `/clients_api/doorbots/987003` (status 200)

```
{
  "type": "device",
  "device_type": "stickup_cams",
  "device": {
    "id": 987003,
    "description": "Driveway",
    "device_id": "cam_driveway",
    "address": "4821 Ridgeview Dr",
    "kind": "floodlight_v2",
    "firmware_version": "3.21.1",
    "battery_life": null,
    "external_connection": true,
    "latitude": 30.2241,
    "longitude": -97.8416,
    "location_id": "loc_martinez_001",
    "time_zone": "America/Chicago",
    "alerts": {
      "connection": "online"
    },
    "features": {
      "motions_enabled": true,
      "show_recordings": true,
      "advanced_motion_enabled":
... (truncated)
```

**GET Get Device - Side Gate** — `/clients_api/doorbots/987005` (status 200)

```
{
  "type": "device",
  "device_type": "stickup_cams",
  "device": {
    "id": 987005,
    "description": "Side Gate",
    "device_id": "cam_side_gate",
    "address": "4821 Ridgeview Dr",
    "kind": "spotlight_cam_v2",
    "firmware_version": "3.18.2",
    "battery_life": 23,
    "external_connection": false,
    "latitude": 30.2241,
    "longitude": -97.8416,
    "location_id": "loc_martinez_001",
    "time_zone": "America/Chicago",
    "alerts": {
      "connection": "online"
    },
    "features": {
      "motions_enabled": true,
      "show_recordings": true,
      "advanced_motion_enabl
... (truncated)
```

**GET Get Device - Chime** — `/clients_api/doorbots/987006` (status 200)

```
{
  "type": "device",
  "device_type": "chimes",
  "device": {
    "id": 987006,
    "description": "Hallway Chime",
    "device_id": "chime_hallway",
    "address": "4821 Ridgeview Dr",
    "kind": "chime_pro_v2",
    "firmware_version": "3.16.4",
    "latitude": 30.2241,
    "longitude": -97.8416,
    "location_id": "loc_martinez_001",
    "time_zone": "America/Chicago",
    "alerts": {
      "connection": "online"
    },
    "features": {
      "ringtones_enabled": true,
      "wifi_extender_enabled": true
    },
    "owned": true,
    "owner": {
      "id": 100001,
      "first_name": "Car
... (truncated)
```

**GET Get Device - Not Found (404)** — `/clients_api/doorbots/999999` (status 404)

```
{
  "error": "Device 999999 not found"
}
```

**GET Get Device Health - Doorbell** — `/clients_api/doorbots/987001/health` (status 200)

```
{
  "type": "device_health",
  "device_health": {
    "device_id": 987001,
    "firmware_version": "3.22.8",
    "battery_life": 82,
    "wifi_signal_strength": -45,
    "wifi_signal_category": "good",
    "alerts": {
      "connection": "online"
    },
    "external_connection": true
  }
}
```

**GET Get Device Health - Driveway (weak WiFi)** — `/clients_api/doorbots/987003/health` (status 200)

```
{
  "type": "device_health",
  "device_health": {
    "device_id": 987003,
    "firmware_version": "3.21.1",
    "battery_life": null,
    "wifi_signal_strength": -68,
    "wifi_signal_category": "poor",
    "alerts": {
      "connection": "online"
    },
    "external_connection": true
  }
}
```

**GET Get Device Health - Side Gate (low battery)** — `/clients_api/doorbots/987005/health` (status 200)

```
{
  "type": "device_health",
  "device_health": {
    "device_id": 987005,
    "firmware_version": "3.18.2",
    "battery_life": 23,
    "wifi_signal_strength": -55,
    "wifi_signal_category": "good",
    "alerts": {
      "connection": "online"
    },
    "external_connection": false
  }
}
```

**GET Get Device Health - Not Found (404)** — `/clients_api/doorbots/999999/health` (status 404)

```
{
  "error": "Device 999999 not found"
}
```

**PUT Update Device Settings - Motion Sensitivity** — `/clients_api/doorbots/987001/settings` (status 200)

```
{
  "type": "device",
  "device_type": "doorbots",
  "device": {
    "id": 987001,
    "description": "Front Door",
    "device_id": "doorbell_front",
    "address": "4821 Ridgeview Dr",
    "kind": "lpd_v2",
    "firmware_version": "3.22.8",
    "battery_life": 82,
    "external_connection": true,
    "latitude": 30.2241,
    "longitude": -97.8416,
    "location_id": "loc_martinez_001",
    "time_zone": "America/Chicago",
    "alerts": {
      "connection": "online"
    },
    "features": {
      "motions_enabled": true,
      "show_recordings": true,
      "advanced_motion_enabled": true,
  
... (truncated)
```

**PUT Update Device Settings - Toggle LED** — `/clients_api/doorbots/987004/settings` (status 200)

```
{
  "type": "device",
  "device_type": "stickup_cams",
  "device": {
    "id": 987004,
    "description": "Living Room",
    "device_id": "cam_living_room",
    "address": "4821 Ridgeview Dr",
    "kind": "stickup_cam_mini",
    "firmware_version": "3.19.8",
    "battery_life": null,
    "external_connection": true,
    "latitude": 30.2241,
    "longitude": -97.8416,
    "location_id": "loc_martinez_001",
    "time_zone": "America/Chicago",
    "alerts": {
      "connection": "online"
    },
    "features": {
      "motions_enabled": true,
      "show_recordings": true,
      "advanced_motion_
... (truncated)
```

**PUT Update Device Settings - Not Found (404)** — `/clients_api/doorbots/999999/settings` (status 404)

```
{
  "error": "Device 999999 not found"
}
```

**GET Get Location** — `/clients_api/locations/loc_martinez_001` (status 200)

```
{
  "type": "location",
  "location": {
    "location_id": "loc_martinez_001",
    "name": "Martinez Home",
    "address": {
      "street1": "4821 Ridgeview Dr",
      "street2": "",
      "city": "Austin",
      "state": "TX",
      "zip": "78749",
      "country": "US"
    },
    "latitude": 30.2241,
    "longitude": -97.8416,
    "time_zone": "America/Chicago",
    "mode": "home",
    "owner": {
      "id": 100001,
      "first_name": "Carlos",
      "last_name": "Martinez",
      "email": "carlos.martinez@email.com"
    },
    "subscription": {
      "plan": "protect_plus",
      "status"
```

**GET Get Location - Not Found (404)** — `/clients_api/locations/loc_unknown_999` (status 404)

```
{
  "error": "Location loc_unknown_999 not found"
}
```

**GET List Location Devices** — `/clients_api/locations/loc_martinez_001/devices` (status 200)

```
{
  "doorbots": [
    {
      "id": 987001,
      "description": "Front Door",
      "device_id": "doorbell_front",
      "address": "4821 Ridgeview Dr",
      "kind": "lpd_v2",
      "firmware_version": "3.22.8",
      "battery_life": 82,
      "external_connection": true,
      "latitude": 30.2241,
      "longitude": -97.8416,
      "location_id": "loc_martinez_001",
      "time_zone": "America/Chicago",
      "alerts": {
        "connection": "online"
      },
      "features": {
        "motions_enabled": true,
        "show_recordings": true,
        "advanced_motion_enabled": true,
     
... (truncated)
```

**GET Get Location Mode** — `/clients_api/locations/loc_martinez_001/mode` (status 200)

```
{
  "type": "mode",
  "mode": "home",
  "location_id": "loc_martinez_001"
}
```

**PUT Set Location Mode - Away** — `/clients_api/locations/loc_martinez_001/mode` (status 200)

```
{
  "type": "mode",
  "mode": "away",
  "location_id": "loc_martinez_001"
}
```

**PUT Set Location Mode - Home** — `/clients_api/locations/loc_martinez_001/mode` (status 200)

```
{
  "type": "mode",
  "mode": "home",
  "location_id": "loc_martinez_001"
}
```

**PUT Set Location Mode - Invalid** — `/clients_api/locations/loc_martinez_001/mode` (status 400)

```
{
  "error": "Invalid mode 'invalid_mode'. Must be one of: ['home', 'away', 'disarmed']"
}
```

**GET List Doorbell Events (all)** — `/clients_api/doorbots/987001/history` (status 200)

```
{
  "type": "events",
  "count": 1,
  "total": 1,
  "offset": 0,
  "limit": 20,
  "results": [
    {
      "id": 7001,
      "doorbot_id": 987001,
      "device_id": "doorbell_front",
      "kind": "ding",
      "created_at": "2026-04-13T19:00:00.000Z",
      "answered": true,
      "favorite": false,
      "recording": {
        "status": "ready"
      },
      "snapshot_url": "",
      "duration_seconds": 10,
      "cv_properties": "person"
    }
  ]
}
```

**GET List Doorbell Events - Dings only** — `/clients_api/doorbots/987001/history?kind=ding` (status 200)

```
{
  "type": "events",
  "count": 1,
  "total": 1,
  "offset": 0,
  "limit": 20,
  "results": [
    {
      "id": 7001,
      "doorbot_id": 987001,
      "device_id": "doorbell_front",
      "kind": "ding",
      "created_at": "2026-04-13T19:00:00.000Z",
      "answered": true,
      "favorite": false,
      "recording": {
        "status": "ready"
      },
      "snapshot_url": "",
      "duration_seconds": 10,
      "cv_properties": "person"
    }
  ]
}
```

**GET List Doorbell Events - Motion only** — `/clients_api/doorbots/987001/history?kind=motion` (status 200)

```
{
  "type": "events",
  "count": 0,
  "total": 0,
  "offset": 0,
  "limit": 20,
  "results": []
}
```

**GET List Doorbell Events - Package detected** — `/clients_api/doorbots/987001/history?kind=package_detected` (status 200)

```
{
  "type": "events",
  "count": 0,
  "total": 0,
  "offset": 0,
  "limit": 20,
  "results": []
}
```

**GET List Driveway Cam Events** — `/clients_api/doorbots/987003/history` (status 200)

```
{
  "type": "events",
  "count": 0,
  "total": 0,
  "offset": 0,
  "limit": 20,
  "results": []
}
```

**GET List Backyard Cam Events** — `/clients_api/doorbots/987002/history` (status 200)

```
{
  "type": "events",
  "count": 0,
  "total": 0,
  "offset": 0,
  "limit": 20,
  "results": []
}
```

**GET List Events - Today only** — `/clients_api/doorbots/987001/history?date_from=2025-04-28T00:00:00.000Z&date_to=2025-04-28T23:59:59.000Z` (status 200)

```
{
  "type": "events",
  "count": 0,
  "total": 0,
  "offset": 0,
  "limit": 20,
  "results": []
}
```

**GET List Events - Last 24h** — `/clients_api/doorbots/987001/history?date_from=2025-04-27T14:30:00.000Z` (status 200)

```
{
  "type": "events",
  "count": 1,
  "total": 1,
  "offset": 0,
  "limit": 20,
  "results": [
    {
      "id": 7001,
      "doorbot_id": 987001,
      "device_id": "doorbell_front",
      "kind": "ding",
      "created_at": "2026-04-13T19:00:00.000Z",
      "answered": true,
      "favorite": false,
      "recording": {
        "status": "ready"
      },
      "snapshot_url": "",
      "duration_seconds": 10,
      "cv_properties": "person"
    }
  ]
}
```

**GET List Events - With pagination** — `/clients_api/doorbots/987001/history?limit=5&offset=0` (status 200)

```
{
  "type": "events",
  "count": 1,
  "total": 1,
  "offset": 0,
  "limit": 5,
  "results": [
    {
      "id": 7001,
      "doorbot_id": 987001,
      "device_id": "doorbell_front",
      "kind": "ding",
      "created_at": "2026-04-13T19:00:00.000Z",
      "answered": true,
      "favorite": false,
      "recording": {
        "status": "ready"
      },
      "snapshot_url": "",
      "duration_seconds": 10,
      "cv_properties": "person"
    }
  ]
}
```

**GET List Events - Page 2** — `/clients_api/doorbots/987001/history?limit=5&offset=5` (status 200)

```
{
  "type": "events",
  "count": 0,
  "total": 1,
  "offset": 5,
  "limit": 5,
  "results": []
}
```

**GET Get Single Event** — `/clients_api/dings/7001` (status 200)

```
{
  "type": "event",
  "event": {
    "id": 7001,
    "doorbot_id": 987001,
    "device_id": "doorbell_front",
    "kind": "ding",
    "created_at": "2026-04-13T19:00:00.000Z",
    "answered": true,
    "favorite": false,
    "recording": {
      "status": "ready"
    },
    "snapshot_url": "",
    "duration_seconds": 10,
    "cv_properties": "person"
  }
}
```

**GET Get Single Event - Not Found (404)** — `/clients_api/dings/99999` (status 404)

```
{
  "error": "Event 99999 not found"
}
```

**GET Get Event Recording URL** — `/clients_api/dings/7001/recording` (status 200)

```
{
  "type": "recording",
  "event_id": 7001,
  "recording_url": "https://ring-recordings.s3.amazonaws.com/loc_martinez_001/doorbell_front/7001.mp4"
}
```

**GET Get Event Recording - Not Found (404)** — `/clients_api/dings/99999/recording` (status 404)

```
{
  "error": "Event 99999 not found"
}
```

**GET List Active Dings** — `/clients_api/dings/active` (status 200)

```
[
  {
    "id": 456789012345679,
    "id_str": "456789012345679",
    "state": "ringing",
    "protocol": "sip",
    "doorbot_id": 987007,
    "doorbot_description": "Garage",
    "device_kind": "stickup_cam_v3",
    "motion": true,
    "snapshot_url": "",
    "kind": "motion",
    "sip_server_ip": "192.168.1.1",
    "sip_server_port": 15063,
    "sip_server_tls": true,
    "sip_session_id": "r.ms.ghi456jkl789",
    "sip_from": "sip:ring007@ring.com",
    "sip_to": "sip:bennett001@ring.com",
    "sip_endpoints": [],
    "expires_in": 130,
    "now": 1744581660.0,
    "optimization_level": 3,
 
```

**GET List Recordings - Doorbell** — `/clients_api/doorbots/987001/recordings` (status 200)

```
{
  "type": "recordings",
  "count": 1,
  "results": [
    {
      "event_id": 7001,
      "doorbot_id": 987001,
      "device_id": "doorbell_front",
      "kind": "ding",
      "created_at": "2026-04-13T19:00:00.000Z",
      "duration_seconds": 10,
      "recording_url": "https://ring-recordings.s3.amazonaws.com/loc_martinez_001/doorbell_front/7001.mp4"
    }
  ]
}
```

**GET List Recordings - Driveway Cam** — `/clients_api/doorbots/987003/recordings` (status 200)

```
{
  "type": "recordings",
  "count": 0,
  "results": []
}
```

**GET List Recordings - Date Range** — `/clients_api/doorbots/987001/recordings?date_from=2025-04-25T00:00:00.000Z&date_to=2025-04-26T23:59:59.000Z` (status 200)

```
{
  "type": "recordings",
  "count": 0,
  "results": []
}
```

**GET List Shared Users** — `/clients_api/locations/loc_martinez_001/users` (status 200)

```
{
  "type": "shared_users",
  "count": 4,
  "results": [
    {
      "user_id": 100001,
      "first_name": "Carlos",
      "last_name": "Martinez",
      "email": "carlos.martinez@email.com",
      "role": "owner",
      "device_access": "all",
      "shared_at": "2022-06-20T14:30:00.000Z"
    },
    {
      "user_id": 100003,
      "first_name": "Tom",
      "last_name": "Reyes",
      "email": "tom.reyes@email.com",
      "role": "guest",
      "device_access": "doorbell_only",
      "shared_at": "2024-01-12T09:30:00.000Z"
    },
    {
      "user_id": 100004,
      "first_name": "Daniel",

... (truncated)
```

**GET Get Shared User - Carlos (owner)** — `/clients_api/locations/loc_martinez_001/users/100001` (status 200)

```
{
  "type": "shared_user",
  "shared_user": {
    "user_id": 100001,
    "first_name": "Carlos",
    "last_name": "Martinez",
    "email": "carlos.martinez@email.com",
    "role": "owner",
    "device_access": "all",
    "shared_at": "2022-06-20T14:30:00.000Z"
  }
}
```

**GET Get Shared User - Tom (guest)** — `/clients_api/locations/loc_martinez_001/users/100003` (status 200)

```
{
  "type": "shared_user",
  "shared_user": {
    "user_id": 100003,
    "first_name": "Tom",
    "last_name": "Reyes",
    "email": "tom.reyes@email.com",
    "role": "guest",
    "device_access": "doorbell_only",
    "shared_at": "2024-01-12T09:30:00.000Z"
  }
}
```

**GET Get Shared User - Not Found (404)** — `/clients_api/locations/loc_martinez_001/users/999999` (status 404)

```
{
  "error": "User 999999 not found"
}
```

**GET Get Chime Settings** — `/clients_api/chimes/987006/settings` (status 200)

```
{
  "type": "chime_settings",
  "settings": {
    "volume": 7,
    "ding_audio_id": "ring_default",
    "ding_audio_user_id": null,
    "motion_audio_id": null,
    "motion_audio_user_id": null,
    "linked_doorbots": [
      987001
    ]
  }
}
```

**GET Get Chime Settings - Not a Chime (404)** — `/clients_api/chimes/987001/settings` (status 404)

```
{
  "error": "Device 987001 is not a chime"
}
```

**PUT Link Chime to Doorbell** — `/clients_api/chimes/987006/link` (status 200)

```
{
  "type": "chime_settings",
  "settings": {
    "volume": 7,
    "ding_audio_id": "ring_default",
    "ding_audio_user_id": null,
    "motion_audio_id": null,
    "motion_audio_user_id": null,
    "linked_doorbots": [
      987001
    ]
  }
}
```

**PUT Unlink Chime from Doorbell** — `/clients_api/chimes/987006/unlink` (status 200)

```
{
  "type": "chime_settings",
  "settings": {
    "volume": 7,
    "ding_audio_id": "ring_default",
    "ding_audio_user_id": null,
    "motion_audio_id": null,
    "motion_audio_user_id": null,
    "linked_doorbots": []
  }
}
```

**GET List Motion Zones - Doorbell** — `/clients_api/doorbots/987001/motion_zones` (status 200)

```
{
  "type": "motion_zones",
  "count": 0,
  "results": []
}
```

**GET List Motion Zones - Driveway** — `/clients_api/doorbots/987003/motion_zones` (status 200)

```
{
  "type": "motion_zones",
  "count": 0,
  "results": []
}
```

**GET List Motion Zones - Not Found (404)** — `/clients_api/doorbots/999999/motion_zones` (status 404)

```
{
  "error": "Device 999999 not found"
}
```

**GET List All Notification Preferences** — `/clients_api/notifications` (status 200)

```
{
  "type": "notification_prefs",
  "count": 4,
  "results": [
    {
      "device_id": 987001,
      "channel": "push",
      "motion_alerts": true,
      "ding_alerts": true,
      "person_alerts": true,
      "package_alerts": true
    },
    {
      "device_id": 987002,
      "channel": "push",
      "motion_alerts": true,
      "ding_alerts": null,
      "person_alerts": null,
      "package_alerts": null
    },
    {
      "device_id": 987004,
      "channel": "push",
      "motion_alerts": false,
      "ding_alerts": null,
      "person_alerts": false,
      "package_alerts": false
    
```

**GET Get Notification Pref - Doorbell** — `/clients_api/notifications/987001` (status 200)

```
{
  "type": "notification_pref",
  "notification_pref": {
    "device_id": 987001,
    "channel": "push",
    "motion_alerts": true,
    "ding_alerts": true,
    "person_alerts": true,
    "package_alerts": true
  }
}
```

**GET Get Notification Pref - Living Room (alerts off)** — `/clients_api/notifications/987004` (status 200)

```
{
  "type": "notification_pref",
  "notification_pref": {
    "device_id": 987004,
    "channel": "push",
    "motion_alerts": false,
    "ding_alerts": null,
    "person_alerts": false,
    "package_alerts": false
  }
}
```

**GET Get Notification Pref - Not Found (404)** — `/clients_api/notifications/999999` (status 404)

```
{
  "error": "Notification preferences for device 999999 not found"
}
```

**PUT Update Notification Pref - Toggle Motion Alerts Off** — `/clients_api/notifications/987002` (status 200)

```
{
  "type": "notification_pref",
  "notification_pref": {
    "device_id": 987002,
    "channel": "push",
    "motion_alerts": false,
    "ding_alerts": null,
    "person_alerts": null,
    "package_alerts": null
  }
}
```

**PUT Update Notification Pref - Toggle Motion Alerts On** — `/clients_api/notifications/987004` (status 200)

```
{
  "type": "notification_pref",
  "notification_pref": {
    "device_id": 987004,
    "channel": "push",
    "motion_alerts": true,
    "ding_alerts": null,
    "person_alerts": false,
    "package_alerts": false
  }
}
```

**POST Activate Siren - Driveway** — `/clients_api/doorbots/987003/siren_on` (status 200)

```
{
  "type": "siren",
  "device_id": 987003,
  "siren_status": {
    "seconds_remaining": 15
  }
}
```

**POST Deactivate Siren - Driveway** — `/clients_api/doorbots/987003/siren_off` (status 200)

```
{
  "type": "siren",
  "device_id": 987003,
  "siren_status": {
    "seconds_remaining": 0
  }
}
```

**POST Activate Siren - No Siren (404)** — `/clients_api/doorbots/987002/siren_on` (status 200)

```
{
  "type": "siren",
  "device_id": 987002,
  "siren_status": {
    "seconds_remaining": 30
  }
}
```

**PUT Turn Floodlight On** — `/clients_api/doorbots/987003/floodlight_light_on` (status 200)

```
{
  "type": "floodlight",
  "device_id": 987003,
  "floodlight_status": {
    "on": true
  }
}
```

**PUT Turn Floodlight Off** — `/clients_api/doorbots/987003/floodlight_light_on` (status 200)

```
{
  "type": "floodlight",
  "device_id": 987003,
  "floodlight_status": {
    "on": false
  }
}
```

**PUT Floodlight - No Floodlight (404)** — `/clients_api/doorbots/987002/floodlight_light_on` (status 200)

```
{
  "type": "floodlight",
  "device_id": 987002,
  "floodlight_status": {
    "on": true
  }
}
```

</details>

### salesforce-api (port 8044) — server: started

| Result | Method | Path | Status | Endpoint |
|--------|--------|------|--------|----------|
| PASS | GET | /health | 200 | health |
| PASS | GET | /services/data/v59.0/sobjects/Account | 200 | list accounts |
| PASS | GET | /services/data/v59.0/sobjects/Account/001Ax000001AAAAAA1 | 200 | get account |
| PASS | POST | /services/data/v59.0/sobjects/Account | 201 | create account |
| PASS | PATCH | /services/data/v59.0/sobjects/Account/001Ax000001AAAAAA1 | 204 | update account |
| PASS | GET | /services/data/v59.0/sobjects/Contact | 200 | list contacts |
| PASS | GET | /services/data/v59.0/sobjects/Contact/003Ax000002BBBBBB2 | 200 | get contact |
| PASS | POST | /services/data/v59.0/sobjects/Contact | 201 | create contact |
| PASS | GET | /services/data/v59.0/sobjects/Lead | 200 | list leads |
| PASS | GET | /services/data/v59.0/sobjects/Lead/00QAx000001AAAAAA1 | 200 | get lead |
| PASS | POST | /services/data/v59.0/sobjects/Lead | 201 | create lead |
| PASS | PATCH | /services/data/v59.0/sobjects/Lead/00QAx000001AAAAAA1 | 204 | update lead |
| PASS | GET | /services/data/v59.0/sobjects/Opportunity | 200 | list opportunities |
| PASS | GET | /services/data/v59.0/sobjects/Opportunity/006Ax000001AAAAAA1 | 200 | get opportunity |
| PASS | POST | /services/data/v59.0/sobjects/Opportunity | 201 | create opportunity |
| PASS | GET | /services/data/v59.0/query?q=SELECT Id, Name, Industry FROM Account WHERE Industry = 'Technology' | 200 | soql query accounts |
| PASS | GET | /services/data/v59.0/query?q=SELECT Id, Name, Amount FROM Opportunity WHERE StageName = 'Closed Won' | 200 | soql query opportunities |

<details><summary>responses</summary>

**GET health** — `/health` (status 200)

```
{
  "status": "ok"
}
```

**GET list accounts** — `/services/data/v59.0/sobjects/Account` (status 200)

```
{
  "totalSize": 5,
  "done": true,
  "records": [
    {
      "Id": "001Ax000001AAAAAA1",
      "Name": "Northwind Traders",
      "Industry": "Retail",
      "AnnualRevenue": 5400000,
      "Phone": "+1-415-555-0190",
      "Website": "https://northwind.example.com",
      "BillingCity": "San Francisco",
      "BillingState": "CA",
      "NumberOfEmployees": 120,
      "attributes": {
        "type": "Account",
        "url": "/services/data/v59.0/sobjects/Account/001Ax000001AAAAAA1"
      }
    },
    {
      "Id": "001Ax000002BBBBBB2",
      "Name": "Initech Systems",
      "Industry": "Te
... (truncated)
```

**GET get account** — `/services/data/v59.0/sobjects/Account/001Ax000001AAAAAA1` (status 200)

```
{
  "Id": "001Ax000001AAAAAA1",
  "Name": "Northwind Traders",
  "Industry": "Retail",
  "AnnualRevenue": 5400000,
  "Phone": "+1-415-555-0190",
  "Website": "https://northwind.example.com",
  "BillingCity": "San Francisco",
  "BillingState": "CA",
  "NumberOfEmployees": 120,
  "attributes": {
    "type": "Account",
    "url": "/services/data/v59.0/sobjects/Account/001Ax000001AAAAAA1"
  }
}
```

**POST create account** — `/services/data/v59.0/sobjects/Account` (status 201)

```
{
  "id": "001D1F9A6C5652343F",
  "success": true,
  "errors": []
}
```

**PATCH update account** — `/services/data/v59.0/sobjects/Account/001Ax000001AAAAAA1` (status 204)

_(empty)_

**GET list contacts** — `/services/data/v59.0/sobjects/Contact` (status 200)

```
{
  "totalSize": 8,
  "done": true,
  "records": [
    {
      "Id": "003Ax000001AAAAAA1",
      "FirstName": "Harper",
      "LastName": "Nguyen",
      "Email": "harper.nguyen@northwind.example.com",
      "Phone": "+1-415-555-0191",
      "Title": "VP Operations",
      "AccountId": "001Ax000001AAAAAA1",
      "MailingCity": "San Francisco",
      "attributes": {
        "type": "Contact",
        "url": "/services/data/v59.0/sobjects/Contact/003Ax000001AAAAAA1"
      }
    },
    {
      "Id": "003Ax000002BBBBBB2",
      "FirstName": "Diego",
      "LastName": "Ramos",
      "Email": "dieg
... (truncated)
```

**GET get contact** — `/services/data/v59.0/sobjects/Contact/003Ax000002BBBBBB2` (status 200)

```
{
  "Id": "003Ax000002BBBBBB2",
  "FirstName": "Diego",
  "LastName": "Ramos",
  "Email": "diego.ramos@initech.example.com",
  "Phone": "+1-512-555-0143",
  "Title": "CTO",
  "AccountId": "001Ax000002BBBBBB2",
  "MailingCity": "Austin",
  "attributes": {
    "type": "Contact",
    "url": "/services/data/v59.0/sobjects/Contact/003Ax000002BBBBBB2"
  }
}
```

**POST create contact** — `/services/data/v59.0/sobjects/Contact` (status 201)

```
{
  "id": "003E225E73E1AC547D",
  "success": true,
  "errors": []
}
```

**GET list leads** — `/services/data/v59.0/sobjects/Lead` (status 200)

```
{
  "totalSize": 5,
  "done": true,
  "records": [
    {
      "Id": "00QAx000001AAAAAA1",
      "FirstName": "Sofia",
      "LastName": "Bauer",
      "Company": "Bauer Analytics",
      "Email": "sofia.bauer@bauer.example.com",
      "Phone": "+1-303-555-0201",
      "Status": "Open - Not Contacted",
      "LeadSource": "Web",
      "Industry": "Technology",
      "Rating": "Warm",
      "attributes": {
        "type": "Lead",
        "url": "/services/data/v59.0/sobjects/Lead/00QAx000001AAAAAA1"
      }
    },
    {
      "Id": "00QAx000002BBBBBB2",
      "FirstName": "Liam",
      "LastNam
... (truncated)
```

**GET get lead** — `/services/data/v59.0/sobjects/Lead/00QAx000001AAAAAA1` (status 200)

```
{
  "Id": "00QAx000001AAAAAA1",
  "FirstName": "Sofia",
  "LastName": "Bauer",
  "Company": "Bauer Analytics",
  "Email": "sofia.bauer@bauer.example.com",
  "Phone": "+1-303-555-0201",
  "Status": "Open - Not Contacted",
  "LeadSource": "Web",
  "Industry": "Technology",
  "Rating": "Warm",
  "attributes": {
    "type": "Lead",
    "url": "/services/data/v59.0/sobjects/Lead/00QAx000001AAAAAA1"
  }
}
```

**POST create lead** — `/services/data/v59.0/sobjects/Lead` (status 201)

```
{
  "id": "00QB264B1A41CCD491",
  "success": true,
  "errors": []
}
```

**PATCH update lead** — `/services/data/v59.0/sobjects/Lead/00QAx000001AAAAAA1` (status 204)

_(empty)_

**GET list opportunities** — `/services/data/v59.0/sobjects/Opportunity` (status 200)

```
{
  "totalSize": 6,
  "done": true,
  "records": [
    {
      "Id": "006Ax000001AAAAAA1",
      "Name": "Northwind POS Rollout",
      "AccountId": "001Ax000001AAAAAA1",
      "StageName": "Prospecting",
      "Amount": 120000,
      "Probability": 20,
      "CloseDate": "2026-07-15",
      "Type": "New Business",
      "attributes": {
        "type": "Opportunity",
        "url": "/services/data/v59.0/sobjects/Opportunity/006Ax000001AAAAAA1"
      }
    },
    {
      "Id": "006Ax000002BBBBBB2",
      "Name": "Initech Platform Upgrade",
      "AccountId": "001Ax000002BBBBBB2",
      "StageNa
... (truncated)
```

**GET get opportunity** — `/services/data/v59.0/sobjects/Opportunity/006Ax000001AAAAAA1` (status 200)

```
{
  "Id": "006Ax000001AAAAAA1",
  "Name": "Northwind POS Rollout",
  "AccountId": "001Ax000001AAAAAA1",
  "StageName": "Prospecting",
  "Amount": 120000,
  "Probability": 20,
  "CloseDate": "2026-07-15",
  "Type": "New Business",
  "attributes": {
    "type": "Opportunity",
    "url": "/services/data/v59.0/sobjects/Opportunity/006Ax000001AAAAAA1"
  }
}
```

**POST create opportunity** — `/services/data/v59.0/sobjects/Opportunity` (status 201)

```
{
  "id": "006640F024A70D549D",
  "success": true,
  "errors": []
}
```

**GET soql query accounts** — `/services/data/v59.0/query?q=SELECT Id, Name, Industry FROM Account WHERE Industry = 'Technology'` (status 200)

```
{
  "totalSize": 1,
  "done": true,
  "records": [
    {
      "attributes": {
        "type": "Account",
        "url": "/services/data/v59.0/sobjects/Account/001Ax000002BBBBBB2"
      },
      "Id": "001Ax000002BBBBBB2",
      "Name": "Initech Systems",
      "Industry": "Technology"
    }
  ]
}
```

**GET soql query opportunities** — `/services/data/v59.0/query?q=SELECT Id, Name, Amount FROM Opportunity WHERE StageName = 'Closed Won'` (status 200)

```
{
  "totalSize": 1,
  "done": true,
  "records": [
    {
      "attributes": {
        "type": "Opportunity",
        "url": "/services/data/v59.0/sobjects/Opportunity/006Ax000004DDDDDD4"
      },
      "Id": "006Ax000004DDDDDD4",
      "Name": "Soylent Telehealth Suite",
      "Amount": 210000
    }
  ]
}
```

</details>

### segment-api (port 8090) — server: started

| Result | Method | Path | Status | Endpoint |
|--------|--------|------|--------|----------|
| PASS | GET | /health | 200 | health |
| PASS | POST | /v1/track | 200 | track |
| PASS | POST | /v1/identify | 200 | identify |
| PASS | POST | /v1/page | 200 | page |
| PASS | POST | /v1/batch | 200 | batch |
| PASS | GET | /v1/events | 200 | events |
| PASS | GET | /v1/events?type=track&userId=user_1001 | 200 | events by type |
| PASS | GET | /v1/sources | 200 | sources |
| PASS | GET | /v1/destinations | 200 | destinations |

<details><summary>responses</summary>

**GET health** — `/health` (status 200)

```
{
  "status": "ok"
}
```

**POST track** — `/v1/track` (status 200)

```
{
  "success": true
}
```

**POST identify** — `/v1/identify` (status 200)

```
{
  "success": true
}
```

**POST page** — `/v1/page` (status 200)

```
{
  "success": true
}
```

**POST batch** — `/v1/batch` (status 200)

```
{
  "success": true,
  "ingested": 2
}
```

**GET events** — `/v1/events` (status 200)

```
{
  "events": [
    {
      "messageId": "msg_0a1b2c3d01",
      "type": "track",
      "userId": "user_1001",
      "event": "Order Completed",
      "timestamp": "2026-05-02T09:14:22Z",
      "properties": {
        "order_id": "ord_5501",
        "revenue": "129.99",
        "currency": "USD"
      }
    },
    {
      "messageId": "msg_0a1b2c3d02",
      "type": "track",
      "userId": "user_1002",
      "event": "Product Viewed",
      "timestamp": "2026-05-03T11:42:05Z",
      "properties": {
        "product_id": "sku_204",
        "category": "footwear"
      }
    },
    {
      "mes
... (truncated)
```

**GET events by type** — `/v1/events?type=track&userId=user_1001` (status 200)

```
{
  "events": [
    {
      "messageId": "msg_0a1b2c3d01",
      "type": "track",
      "userId": "user_1001",
      "event": "Order Completed",
      "timestamp": "2026-05-02T09:14:22Z",
      "properties": {
        "order_id": "ord_5501",
        "revenue": "129.99",
        "currency": "USD"
      }
    }
  ],
  "count": 1
}
```

**GET sources** — `/v1/sources` (status 200)

```
{
  "sources": [
    {
      "id": "src_web01",
      "name": "Marketing Website",
      "slug": "marketing-website",
      "enabled": true,
      "type": "javascript",
      "createdAt": "2026-04-12T09:00:00Z"
    },
    {
      "id": "src_ios01",
      "name": "iOS App",
      "slug": "ios-app",
      "enabled": true,
      "type": "ios",
      "createdAt": "2026-04-14T09:00:00Z"
    },
    {
      "id": "src_and01",
      "name": "Android App",
      "slug": "android-app",
      "enabled": true,
      "type": "android",
      "createdAt": "2026-04-16T09:00:00Z"
    },
    {
      "id": "src
... (truncated)
```

**GET destinations** — `/v1/destinations` (status 200)

```
{
  "destinations": [
    {
      "id": "dst_ga4001",
      "name": "Google Analytics 4",
      "slug": "google-analytics-4",
      "enabled": true,
      "sourceId": "src_web01",
      "createdAt": "2026-04-13T09:00:00Z"
    },
    {
      "id": "dst_ampl01",
      "name": "Amplitude",
      "slug": "amplitude",
      "enabled": true,
      "sourceId": "src_web01",
      "createdAt": "2026-04-13T10:00:00Z"
    },
    {
      "id": "dst_bq001",
      "name": "BigQuery Warehouse",
      "slug": "bigquery",
      "enabled": true,
      "sourceId": "src_srv01",
      "createdAt": "2026-04-19T09:0
... (truncated)
```

</details>

### sendgrid-api (port 8027) — server: started

| Result | Method | Path | Status | Endpoint |
|--------|--------|------|--------|----------|
| SKIP | POST | /v3/templates | - | create template — unresolved variable {{first_name}} |
| PASS | GET | /health | 200 | health |
| PASS | POST | /v3/mail/send | 202 | send mail |
| PASS | GET | /v3/templates?generations=dynamic | 200 | list templates |
| PASS | GET | /v3/templates/d-1a2b3c4d5e6f7081 | 200 | get template |
| PASS | GET | /v3/marketing/contacts | 200 | list marketing contacts |
| PASS | POST | /v3/marketing/contacts | 202 | upsert marketing contacts |
| PASS | GET | /v3/marketing/lists | 200 | list lists |
| PASS | GET | /v3/stats?start_date=2026-05-20&end_date=2026-05-26 | 200 | get stats |

<details><summary>responses</summary>

**GET health** — `/health` (status 200)

```
{
  "status": "ok"
}
```

**POST send mail** — `/v3/mail/send` (status 202)

```
{
  "accepted": 1,
  "message_ids": [
    "msg-f07ec2bb502d"
  ],
  "status": "queued"
}
```

**GET list templates** — `/v3/templates?generations=dynamic` (status 200)

```
{
  "result": [
    {
      "id": "d-1a2b3c4d5e6f7081",
      "name": "Welcome Email",
      "generation": "dynamic",
      "updated_at": "2026-05-10T10:00:00Z",
      "versions": [
        {
          "subject": "Welcome to Orbit Labs, {{first_name}}!",
          "html_content": "<h1>Welcome {{first_name}}</h1><p>Glad to have you.</p>",
          "active": 1
        }
      ]
    },
    {
      "id": "d-2b3c4d5e6f708192",
      "name": "Password Reset",
      "generation": "dynamic",
      "updated_at": "2026-05-12T11:30:00Z",
      "versions": [
        {
          "subject": "Reset your Orb
... (truncated)
```

**GET get template** — `/v3/templates/d-1a2b3c4d5e6f7081` (status 200)

```
{
  "id": "d-1a2b3c4d5e6f7081",
  "name": "Welcome Email",
  "generation": "dynamic",
  "updated_at": "2026-05-10T10:00:00Z",
  "versions": [
    {
      "subject": "Welcome to Orbit Labs, {{first_name}}!",
      "html_content": "<h1>Welcome {{first_name}}</h1><p>Glad to have you.</p>",
      "active": 1
    }
  ]
}
```

**GET list marketing contacts** — `/v3/marketing/contacts` (status 200)

```
{
  "result": [
    {
      "id": "contact-00a1",
      "email": "amelia.ortega@orbit-labs.com",
      "first_name": "Amelia",
      "last_name": "Ortega",
      "country": "US",
      "list_ids": [
        "list-7788aa11",
        "list-7788aa22"
      ],
      "created_at": "2025-09-02T10:00:00Z",
      "updated_at": "2026-05-20T10:00:00Z"
    },
    {
      "id": "contact-00a2",
      "email": "jonas.pereira@orbit-labs.com",
      "first_name": "Jonas",
      "last_name": "Pereira",
      "country": "PT",
      "list_ids": [
        "list-7788aa11",
        "list-7788aa22"
      ],
      "c
... (truncated)
```

**POST upsert marketing contacts** — `/v3/marketing/contacts` (status 202)

```
{
  "job_id": "job-8be20f8beb2c",
  "upserted": 1,
  "contact_ids": [
    "contact-cd2bba7b0c50"
  ]
}
```

**GET list lists** — `/v3/marketing/lists` (status 200)

```
{
  "result": [
    {
      "id": "list-7788aa11",
      "name": "Newsletter Subscribers",
      "contact_count": 4,
      "created_at": "2025-09-01T10:00:00Z"
    },
    {
      "id": "list-7788aa22",
      "name": "Active Customers",
      "contact_count": 3,
      "created_at": "2025-09-05T11:00:00Z"
    },
    {
      "id": "list-7788aa33",
      "name": "Trial Users",
      "contact_count": 2,
      "created_at": "2025-10-10T12:00:00Z"
    },
    {
      "id": "list-7788aa44",
      "name": "Beta Testers",
      "contact_count": 1,
      "created_at": "2026-01-15T09:00:00Z"
    }
  ]
}
```

**GET get stats** — `/v3/stats?start_date=2026-05-20&end_date=2026-05-26` (status 200)

```
[
  {
    "date": "2026-05-20",
    "stats": [
      {
        "metrics": {
          "requests": 520,
          "delivered": 512,
          "opens": 310,
          "unique_opens": 260,
          "clicks": 88,
          "unique_clicks": 71,
          "bounces": 8,
          "spam_reports": 1,
          "unsubscribes": 3
        }
      }
    ]
  },
  {
    "date": "2026-05-21",
    "stats": [
      {
        "metrics": {
          "requests": 610,
          "delivered": 601,
          "opens": 402,
          "unique_opens": 330,
          "clicks": 120,
          "unique_clicks": 95,
         
... (truncated)
```

</details>

### sentry-api (port 8047) — server: started

| Result | Method | Path | Status | Endpoint |
|--------|--------|------|--------|----------|
| PASS | GET | /health | 200 | health |
| PASS | GET | /api/0/organizations/orbit-labs/projects/ | 200 | list org projects |
| PASS | GET | /api/0/projects/orbit-labs/auth-service/issues/?status=unresolved | 200 | list project issues |
| PASS | GET | /api/0/projects/orbit-labs/web-frontend/issues/?level=error | 200 | list project issues by level |
| PASS | GET | /api/0/organizations/orbit-labs/issues/40001/ | 200 | get issue |
| PASS | PUT | /api/0/organizations/orbit-labs/issues/40001/ | 200 | resolve issue |
| PASS | PUT | /api/0/organizations/orbit-labs/issues/40002/ | 200 | ignore issue |
| PASS | GET | /api/0/organizations/orbit-labs/issues/40001/events/ | 200 | list issue events |
| PASS | GET | /api/0/organizations/orbit-labs/releases/ | 200 | list releases |
| PASS | GET | /api/0/organizations/orbit-labs/releases/?project=auth-service | 200 | list releases for project |

<details><summary>responses</summary>

**GET health** — `/health` (status 200)

```
{
  "status": "ok"
}
```

**GET list org projects** — `/api/0/organizations/orbit-labs/projects/` (status 200)

```
[
  {
    "id": "11",
    "slug": "auth-service",
    "name": "Auth Service",
    "platform": "go",
    "status": "active",
    "dateCreated": "2024-04-12T10:00:00.000Z"
  },
  {
    "id": "12",
    "slug": "web-frontend",
    "name": "Web Frontend",
    "platform": "javascript-react",
    "status": "active",
    "dateCreated": "2024-03-20T10:00:00.000Z"
  },
  {
    "id": "13",
    "slug": "billing-service",
    "name": "Billing Service",
    "platform": "java",
    "status": "active",
    "dateCreated": "2024-06-01T10:00:00.000Z"
  }
]
```

**GET list project issues** — `/api/0/projects/orbit-labs/auth-service/issues/?status=unresolved` (status 200)

```
[
  {
    "id": "40001",
    "shortId": "AUTH-1",
    "title": "DeadlineExceeded refreshing session token",
    "culprit": "session_store.write",
    "level": "error",
    "status": "unresolved",
    "count": 1842,
    "userCount": 612,
    "project": {
      "slug": "auth-service"
    },
    "firstSeen": "2026-05-22T11:00:00.000Z",
    "lastSeen": "2026-05-26T09:00:00.000Z"
  },
  {
    "id": "40002",
    "shortId": "AUTH-2",
    "title": "NilPointer in token validator",
    "culprit": "token.validate",
    "level": "error",
    "status": "unresolved",
    "count": 73,
    "userCount": 40,
  
```

**GET list project issues by level** — `/api/0/projects/orbit-labs/web-frontend/issues/?level=error` (status 200)

```
[
  {
    "id": "40010",
    "shortId": "WEB-1",
    "title": "TypeError reading property avatar of null",
    "culprit": "profile.avatarHook",
    "level": "error",
    "status": "unresolved",
    "count": 963,
    "userCount": 701,
    "project": {
      "slug": "web-frontend"
    },
    "firstSeen": "2026-05-25T08:00:00.000Z",
    "lastSeen": "2026-05-26T07:30:00.000Z"
  },
  {
    "id": "40011",
    "shortId": "WEB-2",
    "title": "Unhandled promise rejection in checkout",
    "culprit": "checkout.submit",
    "level": "error",
    "status": "resolved",
    "count": 310,
    "userCount": 
```

**GET get issue** — `/api/0/organizations/orbit-labs/issues/40001/` (status 200)

```
{
  "id": "40001",
  "shortId": "AUTH-1",
  "title": "DeadlineExceeded refreshing session token",
  "culprit": "session_store.write",
  "level": "error",
  "status": "unresolved",
  "count": 1842,
  "userCount": 612,
  "project": {
    "slug": "auth-service"
  },
  "firstSeen": "2026-05-22T11:00:00.000Z",
  "lastSeen": "2026-05-26T09:00:00.000Z"
}
```

**PUT resolve issue** — `/api/0/organizations/orbit-labs/issues/40001/` (status 200)

```
{
  "id": "40001",
  "shortId": "AUTH-1",
  "title": "DeadlineExceeded refreshing session token",
  "culprit": "session_store.write",
  "level": "error",
  "status": "unresolved",
  "count": 1842,
  "userCount": 612,
  "project": {
    "slug": "auth-service"
  },
  "firstSeen": "2026-05-22T11:00:00.000Z",
  "lastSeen": "2026-05-26T09:00:00.000Z"
}
```

**PUT ignore issue** — `/api/0/organizations/orbit-labs/issues/40002/` (status 200)

```
{
  "id": "40002",
  "shortId": "AUTH-2",
  "title": "NilPointer in token validator",
  "culprit": "token.validate",
  "level": "error",
  "status": "unresolved",
  "count": 73,
  "userCount": 40,
  "project": {
    "slug": "auth-service"
  },
  "firstSeen": "2026-05-24T08:00:00.000Z",
  "lastSeen": "2026-05-26T07:00:00.000Z"
}
```

**GET list issue events** — `/api/0/organizations/orbit-labs/issues/40001/events/` (status 200)

```
[
  {
    "id": "70001",
    "eventID": "a1b2c3d4e5f64718a1b2c3d4e5f64718",
    "message": "DeadlineExceeded refreshing session token",
    "platform": "go",
    "environment": "production",
    "release": "auth-service@2.0.3",
    "user": {
      "email": "user-1842@example.com"
    },
    "dateCreated": "2026-05-26T09:00:00.000Z"
  },
  {
    "id": "70002",
    "eventID": "b2c3d4e5f6471801b2c3d4e5f6471801",
    "message": "DeadlineExceeded refreshing session token",
    "platform": "go",
    "environment": "production",
    "release": "auth-service@2.0.3",
    "user": {
      "email": "user-
```

**GET list releases** — `/api/0/organizations/orbit-labs/releases/` (status 200)

```
[
  {
    "version": "web-frontend@5.4.1",
    "ref": "c3d4e5f",
    "status": "open",
    "newGroups": 1,
    "projects": [
      {
        "slug": "web-frontend"
      }
    ],
    "dateCreated": "2026-05-24T12:00:00.000Z",
    "dateReleased": "2026-05-24T15:00:00.000Z"
  },
  {
    "version": "auth-service@2.1.0-rc1",
    "ref": "b2c3d4e",
    "status": "open",
    "newGroups": 1,
    "projects": [
      {
        "slug": "auth-service"
      }
    ],
    "dateCreated": "2026-05-24T10:00:00.000Z",
    "dateReleased": null
  },
  {
    "version": "billing-service@3.1.0",
    "ref": "e5f6a1b"
... (truncated)
```

**GET list releases for project** — `/api/0/organizations/orbit-labs/releases/?project=auth-service` (status 200)

```
[
  {
    "version": "auth-service@2.1.0-rc1",
    "ref": "b2c3d4e",
    "status": "open",
    "newGroups": 1,
    "projects": [
      {
        "slug": "auth-service"
      }
    ],
    "dateCreated": "2026-05-24T10:00:00.000Z",
    "dateReleased": null
  },
  {
    "version": "auth-service@2.0.3",
    "ref": "a1b2c3d",
    "status": "open",
    "newGroups": 2,
    "projects": [
      {
        "slug": "auth-service"
      }
    ],
    "dateCreated": "2026-05-20T10:00:00.000Z",
    "dateReleased": "2026-05-21T09:00:00.000Z"
  }
]
```

</details>

### servicenow-api (port 8071) — server: started

| Result | Method | Path | Status | Endpoint |
|--------|--------|------|--------|----------|
| PASS | GET | /health | 200 | health |
| PASS | GET | /api/now/table/incident | 200 | list incidents |
| PASS | GET | /api/now/table/incident?sysparm_query=state=2^priority=1&sysparm_limit=5 | 200 | list incidents filtered |
| PASS | GET | /api/now/table/incident/inc-0001001 | 200 | get incident |
| PASS | POST | /api/now/table/incident | 201 | create incident |
| PASS | PATCH | /api/now/table/incident/inc-0001003 | 200 | update incident |
| PASS | GET | /api/now/table/change_request | 200 | list change requests |
| PASS | GET | /api/now/table/change_request/chg-0002001 | 200 | get change request |
| PASS | GET | /api/now/table/problem | 200 | list problems |
| PASS | GET | /api/now/table/problem/prb-0003001 | 200 | get problem |
| PASS | GET | /api/now/table/sys_user | 200 | list users |
| PASS | GET | /api/now/table/sys_user/usr-amelia | 200 | get user |

<details><summary>responses</summary>

**GET health** — `/health` (status 200)

```
{
  "status": "ok"
}
```

**GET list incidents** — `/api/now/table/incident` (status 200)

```
{
  "result": [
    {
      "sys_id": "inc-0001001",
      "number": "INC0001001",
      "short_description": "Email service intermittently unavailable",
      "description": "Users report Outlook disconnecting every few minutes since 9am.",
      "state": "2",
      "priority": "1",
      "impact": "1",
      "urgency": "1",
      "category": "software",
      "assigned_to": "usr-jonas",
      "opened_by": "usr-noor",
      "opened_at": "2026-05-20T09:12:00Z",
      "updated_at": "2026-05-20T10:40:00Z"
    },
    {
      "sys_id": "inc-0001002",
      "number": "INC0001002",
      "short_desc
... (truncated)
```

**GET list incidents filtered** — `/api/now/table/incident?sysparm_query=state=2^priority=1&sysparm_limit=5` (status 200)

```
{
  "result": [
    {
      "sys_id": "inc-0001001",
      "number": "INC0001001",
      "short_description": "Email service intermittently unavailable",
      "description": "Users report Outlook disconnecting every few minutes since 9am.",
      "state": "2",
      "priority": "1",
      "impact": "1",
      "urgency": "1",
      "category": "software",
      "assigned_to": "usr-jonas",
      "opened_by": "usr-noor",
      "opened_at": "2026-05-20T09:12:00Z",
      "updated_at": "2026-05-20T10:40:00Z"
    },
    {
      "sys_id": "inc-0001006",
      "number": "INC0001006",
      "short_desc
... (truncated)
```

**GET get incident** — `/api/now/table/incident/inc-0001001` (status 200)

```
{
  "result": {
    "sys_id": "inc-0001001",
    "number": "INC0001001",
    "short_description": "Email service intermittently unavailable",
    "description": "Users report Outlook disconnecting every few minutes since 9am.",
    "state": "2",
    "priority": "1",
    "impact": "1",
    "urgency": "1",
    "category": "software",
    "assigned_to": "usr-jonas",
    "opened_by": "usr-noor",
    "opened_at": "2026-05-20T09:12:00Z",
    "updated_at": "2026-05-20T10:40:00Z"
  }
}
```

**POST create incident** — `/api/now/table/incident` (status 201)

```
{
  "result": {
    "sys_id": "cae11ba842084720bbbfb23d4e6cec53",
    "number": "INC0001011",
    "short_description": "New monitor flickering",
    "description": "Desk monitor flickers intermittently.",
    "state": "1",
    "priority": "4",
    "impact": "3",
    "urgency": "3",
    "category": "hardware",
    "assigned_to": "usr-jonas",
    "opened_by": "usr-noor",
    "opened_at": "2026-06-17T10:31:37Z",
    "updated_at": "2026-06-17T10:31:37Z"
  }
}
```

**PATCH update incident** — `/api/now/table/incident/inc-0001003` (status 200)

```
{
  "result": {
    "sys_id": "inc-0001003",
    "number": "INC0001003",
    "short_description": "Laptop will not boot after BIOS update",
    "description": "Finance laptop shows black screen following overnight update.",
    "state": "2",
    "priority": "3",
    "impact": "3",
    "urgency": "3",
    "category": "hardware",
    "assigned_to": "usr-helena",
    "opened_by": "usr-noor",
    "opened_at": "2026-05-22T11:20:00Z",
    "updated_at": "2026-06-17T10:31:37Z"
  }
}
```

**GET list change requests** — `/api/now/table/change_request` (status 200)

```
{
  "result": [
    {
      "sys_id": "chg-0002001",
      "number": "CHG0002001",
      "short_description": "Upgrade core firewall firmware",
      "description": "Apply vendor security firmware to perimeter firewalls during window.",
      "state": "assess",
      "priority": "2",
      "risk": "high",
      "type": "normal",
      "assigned_to": "usr-helena",
      "requested_by": "usr-amelia",
      "start_date": "2026-06-01T22:00:00Z",
      "end_date": "2026-06-02T02:00:00Z"
    },
    {
      "sys_id": "chg-0002002",
      "number": "CHG0002002",
      "short_description": "Patch produ
... (truncated)
```

**GET get change request** — `/api/now/table/change_request/chg-0002001` (status 200)

```
{
  "result": {
    "sys_id": "chg-0002001",
    "number": "CHG0002001",
    "short_description": "Upgrade core firewall firmware",
    "description": "Apply vendor security firmware to perimeter firewalls during window.",
    "state": "assess",
    "priority": "2",
    "risk": "high",
    "type": "normal",
    "assigned_to": "usr-helena",
    "requested_by": "usr-amelia",
    "start_date": "2026-06-01T22:00:00Z",
    "end_date": "2026-06-02T02:00:00Z"
  }
}
```

**GET list problems** — `/api/now/table/problem` (status 200)

```
{
  "result": [
    {
      "sys_id": "prb-0003001",
      "number": "PRB0003001",
      "short_description": "Recurring email disconnects",
      "description": "Root cause analysis for repeated Outlook disconnection incidents.",
      "state": "2",
      "priority": "1",
      "assigned_to": "usr-priya",
      "opened_by": "usr-amelia",
      "opened_at": "2026-05-20T11:00:00Z",
      "related_incident": "inc-0001001"
    },
    {
      "sys_id": "prb-0003002",
      "number": "PRB0003002",
      "short_description": "VPN gateway instability after patches",
      "description": "Investigatin
... (truncated)
```

**GET get problem** — `/api/now/table/problem/prb-0003001` (status 200)

```
{
  "result": {
    "sys_id": "prb-0003001",
    "number": "PRB0003001",
    "short_description": "Recurring email disconnects",
    "description": "Root cause analysis for repeated Outlook disconnection incidents.",
    "state": "2",
    "priority": "1",
    "assigned_to": "usr-priya",
    "opened_by": "usr-amelia",
    "opened_at": "2026-05-20T11:00:00Z",
    "related_incident": "inc-0001001"
  }
}
```

**GET list users** — `/api/now/table/sys_user` (status 200)

```
{
  "result": [
    {
      "sys_id": "usr-amelia",
      "user_name": "amelia.ortega",
      "name": "Amelia Ortega",
      "email": "amelia.ortega@orbit-labs.com",
      "title": "IT Service Manager",
      "department": "IT Service Management",
      "active": true
    },
    {
      "sys_id": "usr-jonas",
      "user_name": "jonas.pereira",
      "name": "Jonas Pereira",
      "email": "jonas.pereira@orbit-labs.com",
      "title": "Senior Support Engineer",
      "department": "IT Support",
      "active": true
    },
    {
      "sys_id": "usr-helena",
      "user_name": "helena.park",
 
... (truncated)
```

**GET get user** — `/api/now/table/sys_user/usr-amelia` (status 200)

```
{
  "result": {
    "sys_id": "usr-amelia",
    "user_name": "amelia.ortega",
    "name": "Amelia Ortega",
    "email": "amelia.ortega@orbit-labs.com",
    "title": "IT Service Manager",
    "department": "IT Service Management",
    "active": true
  }
}
```

</details>

### shippo-api (port 8052) — server: started

| Result | Method | Path | Status | Endpoint |
|--------|--------|------|--------|----------|
| PASS | GET | /health | 200 | health |
| PASS | POST | /addresses | 201 | create address |
| PASS | GET | /addresses/addr-recv-01 | 200 | get address |
| PASS | POST | /shipments | 201 | create shipment |
| PASS | GET | /shipments/ship-1001 | 200 | get shipment |
| PASS | GET | /shipments/ship-1001/rates | 200 | list shipment rates |
| PASS | POST | /transactions | 201 | buy label |
| PASS | GET | /transactions/txn-9001 | 200 | get transaction |
| PASS | GET | /tracks/USPS/9400111202555842761023 | 200 | track shipment |

<details><summary>responses</summary>

**GET health** — `/health` (status 200)

```
{
  "status": "ok"
}
```

**POST create address** — `/addresses` (status 201)

```
{
  "object_id": "addr-1c5555a12f79",
  "name": "Noor Aziz",
  "company": "",
  "street1": "22 Greenway Dr",
  "street2": "",
  "city": "Seattle",
  "state": "WA",
  "zip": "98101",
  "country": "US",
  "phone": "",
  "email": "",
  "is_residential": true,
  "validated": true
}
```

**GET get address** — `/addresses/addr-recv-01` (status 200)

```
{
  "object_id": "addr-recv-01",
  "name": "Amelia Ortega",
  "company": "",
  "street1": "1842 Maple Grove Rd",
  "street2": "Apt 4B",
  "city": "Austin",
  "state": "TX",
  "zip": "78704",
  "country": "US",
  "phone": "5125550182",
  "email": "amelia.ortega@orbit-labs.com",
  "is_residential": true,
  "validated": true
}
```

**POST create shipment** — `/shipments` (status 201)

```
{
  "object_id": "ship-7bc009ef0f75",
  "status": "SUCCESS",
  "object_created": "2026-06-17T10:31:38Z",
  "address_from": {
    "object_id": "addr-sender-01",
    "name": "Orbit Labs Fulfillment",
    "company": "Orbit Labs",
    "street1": "500 Treat Ave",
    "street2": "Suite 200",
    "city": "San Francisco",
    "state": "CA",
    "zip": "94110",
    "country": "US",
    "phone": "4155550111",
    "email": "ship@orbit-labs.com",
    "is_residential": false,
    "validated": true
  },
  "address_to": {
    "object_id": "addr-recv-02",
    "name": "Jonas Pereira",
    "company": "Pereira S
... (truncated)
```

**GET get shipment** — `/shipments/ship-1001` (status 200)

```
{
  "object_id": "ship-1001",
  "status": "SUCCESS",
  "object_created": "2026-05-25T14:00:00Z",
  "address_from": {
    "object_id": "addr-sender-01",
    "name": "Orbit Labs Fulfillment",
    "company": "Orbit Labs",
    "street1": "500 Treat Ave",
    "street2": "Suite 200",
    "city": "San Francisco",
    "state": "CA",
    "zip": "94110",
    "country": "US",
    "phone": "4155550111",
    "email": "ship@orbit-labs.com",
    "is_residential": false,
    "validated": true
  },
  "address_to": {
    "object_id": "addr-recv-01",
    "name": "Amelia Ortega",
    "company": "",
    "street1":
... (truncated)
```

**GET list shipment rates** — `/shipments/ship-1001/rates` (status 200)

```
{
  "count": 4,
  "results": [
    {
      "object_id": "rate-usps-prio-01",
      "shipment": "ship-1001",
      "provider": "USPS",
      "servicelevel": {
        "token": "usps_priority",
        "name": "Priority Mail"
      },
      "amount": 8.45,
      "currency": "USD",
      "estimated_days": 2
    },
    {
      "object_id": "rate-usps-first-01",
      "shipment": "ship-1001",
      "provider": "USPS",
      "servicelevel": {
        "token": "usps_first",
        "name": "First Class Package"
      },
      "amount": 5.2,
      "currency": "USD",
      "estimated_days": 3
    },
  
... (truncated)
```

**POST buy label** — `/transactions` (status 201)

```
{
  "object_id": "txn-b551e8c78c56",
  "rate": "rate-ups-ground-01",
  "shipment": "ship-1001",
  "status": "SUCCESS",
  "tracking_number": "1Z999AA19219870361",
  "tracking_status": "PRE_TRANSIT",
  "carrier": "UPS",
  "label_url": "https://shippo-delivery.s3.amazonaws.com/labels/1Z999AA19219870361.pdf",
  "created_time": "2026-06-17T10:31:38Z"
}
```

**GET get transaction** — `/transactions/txn-9001` (status 200)

```
{
  "object_id": "txn-9001",
  "rate": "rate-usps-prio-01",
  "shipment": "ship-1001",
  "status": "SUCCESS",
  "tracking_number": "9400111202555842761023",
  "tracking_status": "DELIVERED",
  "carrier": "USPS",
  "label_url": "https://shippo-delivery.s3.amazonaws.com/labels/txn-9001.pdf",
  "created_time": "2026-05-25T14:05:00Z"
}
```

**GET track shipment** — `/tracks/USPS/9400111202555842761023` (status 200)

```
{
  "carrier": "USPS",
  "tracking_number": "9400111202555842761023",
  "tracking_status": {
    "status": "DELIVERED",
    "status_details": "Delivered front porch",
    "location": {
      "city": "Austin",
      "state": "TX"
    },
    "status_date": "2026-05-27T16:20:00Z"
  },
  "tracking_history": [
    {
      "status": "DELIVERED",
      "status_details": "Delivered front porch",
      "location": {
        "city": "Austin",
        "state": "TX"
      },
      "status_date": "2026-05-27T16:20:00Z"
    },
    {
      "status": "TRANSIT",
      "status_details": "Out for delivery",
    
... (truncated)
```

</details>

### slack-api (port 8013) — server: started

| Result | Method | Path | Status | Endpoint |
|--------|--------|------|--------|----------|
| PASS | GET | /health | 200 | health |
| PASS | GET | /api/auth.test | 200 | auth.test |
| PASS | GET | /api/team.info | 200 | team.info |
| PASS | GET | /api/users.list | 200 | users.list |
| PASS | GET | /api/users.info?user=U01AMELIA | 200 | users.info |
| PASS | POST | /api/users.setPresence | 200 | users.setPresence |
| PASS | GET | /api/conversations.list | 200 | conversations.list |
| PASS | GET | /api/conversations.info?channel=C01ENG | 200 | conversations.info |
| PASS | POST | /api/conversations.create | 200 | conversations.create |
| PASS | GET | /api/conversations.history?channel=C01ENG&limit=5 | 200 | conversations.history |
| PASS | GET | /api/conversations.replies?channel=C01ENG&ts=1748210000.000100 | 200 | conversations.replies |
| PASS | POST | /api/conversations.invite | 200 | conversations.invite |
| PASS | POST | /api/chat.postMessage | 200 | chat.postMessage |
| PASS | POST | /api/chat.update | 200 | chat.update |
| PASS | POST | /api/reactions.add | 200 | reactions.add |
| PASS | GET | /api/search.messages?query=cutover | 200 | search.messages |

<details><summary>responses</summary>

**GET health** — `/health` (status 200)

```
{
  "status": "ok"
}
```

**GET auth.test** — `/api/auth.test` (status 200)

```
{
  "ok": true,
  "url": "https://cascade-eng.slack.com/",
  "team": "Cascade Engineering",
  "user": "amelia",
  "team_id": "T01CASCADE",
  "user_id": "U01AMELIA"
}
```

**GET team.info** — `/api/team.info` (status 200)

```
{
  "ok": true,
  "team": {
    "id": "T01CASCADE",
    "name": "Cascade Engineering",
    "domain": "cascade-eng",
    "email_domain": "cascade-eng.com",
    "icon": {
      "image_132": "https://avatars.example.com/team-cascade.png"
    }
  }
}
```

**GET users.list** — `/api/users.list` (status 200)

```
{
  "ok": true,
  "members": [
    {
      "id": "U01AMELIA",
      "name": "amelia",
      "real_name": "Amelia Ortega",
      "email": "amelia@cascade-eng.com",
      "is_admin": true,
      "is_bot": false,
      "tz": "America/Los_Angeles",
      "status_text": "heads-down on auth v2",
      "presence": "active"
    },
    {
      "id": "U01JONAS",
      "name": "jonas",
      "real_name": "Jonas Pereira",
      "email": "jonas@cascade-eng.com",
      "is_admin": false,
      "is_bot": false,
      "tz": "America/Sao_Paulo",
      "status_text": "",
      "presence": "active"
    },
    {

... (truncated)
```

**GET users.info** — `/api/users.info?user=U01AMELIA` (status 200)

```
{
  "ok": true,
  "user": {
    "id": "U01AMELIA",
    "name": "amelia",
    "real_name": "Amelia Ortega",
    "email": "amelia@cascade-eng.com",
    "is_admin": true,
    "is_bot": false,
    "tz": "America/Los_Angeles",
    "status_text": "heads-down on auth v2",
    "presence": "active"
  }
}
```

**POST users.setPresence** — `/api/users.setPresence` (status 200)

```
{
  "ok": true,
  "presence": "active"
}
```

**GET conversations.list** — `/api/conversations.list` (status 200)

```
{
  "ok": true,
  "channels": [
    {
      "id": "C01GENERAL",
      "name": "general",
      "is_private": false,
      "is_archived": false,
      "topic": "Company-wide announcements",
      "purpose": "Default channel for all",
      "creator": "U01AMELIA",
      "created": 1700000000,
      "num_members": 5
    },
    {
      "id": "C01ENG",
      "name": "eng",
      "is_private": false,
      "is_archived": false,
      "topic": "All engineering discussion",
      "purpose": "Engineering team chat",
      "creator": "U01AMELIA",
      "created": 1700000100,
      "num_members": 5
    }
... (truncated)
```

**GET conversations.info** — `/api/conversations.info?channel=C01ENG` (status 200)

```
{
  "ok": true,
  "channel": {
    "id": "C01ENG",
    "name": "eng",
    "is_private": false,
    "is_archived": false,
    "topic": "All engineering discussion",
    "purpose": "Engineering team chat",
    "creator": "U01AMELIA",
    "created": 1700000100,
    "num_members": 5
  }
}
```

**POST conversations.create** — `/api/conversations.create` (status 200)

```
{
  "ok": true,
  "channel": {
    "id": "C01EA49867F",
    "name": "proj-billing-grpc",
    "is_private": false,
    "is_archived": false,
    "topic": "",
    "purpose": "",
    "creator": "U01AMELIA",
    "created": 1781692298,
    "num_members": 1
  }
}
```

**GET conversations.history** — `/api/conversations.history?channel=C01ENG&limit=5` (status 200)

```
{
  "ok": true,
  "messages": [
    {
      "ts": "1748210000.000100",
      "channel_id": "C01ENG",
      "user_id": "U01AMELIA",
      "text": "Kicking off auth v2 weekly. Status doc in #proj-auth-v2.",
      "thread_ts": null,
      "reply_count": 1,
      "reactions": []
    }
  ],
  "has_more": false
}
```

**GET conversations.replies** — `/api/conversations.replies?channel=C01ENG&ts=1748210000.000100` (status 200)

```
{
  "ok": true,
  "messages": [
    {
      "ts": "1748210000.000100",
      "channel_id": "C01ENG",
      "user_id": "U01AMELIA",
      "text": "Kicking off auth v2 weekly. Status doc in #proj-auth-v2.",
      "thread_ts": null,
      "reply_count": 1,
      "reactions": []
    },
    {
      "ts": "1748210100.000200",
      "channel_id": "C01ENG",
      "user_id": "U01JONAS",
      "text": "Will need a billing migration freeze for the cutover.",
      "thread_ts": "1748210000.000100",
      "reply_count": 0,
      "reactions": []
    }
  ]
}
```

**POST conversations.invite** — `/api/conversations.invite` (status 200)

```
{
  "ok": true,
  "results": [
    {
      "user": "U01ROHIT",
      "ok": true,
      "error": null
    }
  ],
  "channel": {
    "id": "C01AUTHV2",
    "name": "proj-auth-v2",
    "is_private": false,
    "is_archived": false,
    "topic": "Auth v2 rollout tracking",
    "purpose": "Project channel for auth migration",
    "creator": "U01AMELIA",
    "created": 1740000000,
    "num_members": 3
  }
}
```

**POST chat.postMessage** — `/api/chat.postMessage` (status 200)

```
{
  "ok": true,
  "channel": "C01AUTHV2",
  "ts": "1781692298.934109",
  "message": {
    "ts": "1781692298.934109",
    "channel_id": "C01AUTHV2",
    "user_id": "U01AMELIA",
    "text": "Cutover scheduled for Friday 8am PT.",
    "thread_ts": null,
    "reply_count": 0,
    "reactions": []
  }
}
```

**POST chat.update** — `/api/chat.update` (status 200)

```
{
  "ok": true,
  "channel": "C01ENG",
  "ts": "1748210000.000100",
  "text": "Updated agenda in the doc."
}
```

**POST reactions.add** — `/api/reactions.add` (status 200)

```
{
  "ok": true
}
```

**GET search.messages** — `/api/search.messages?query=cutover` (status 200)

```
{
  "ok": true,
  "messages": {
    "total": 1,
    "matches": [
      {
        "ts": "1748210100.000200",
        "channel_id": "C01ENG",
        "user_id": "U01JONAS",
        "text": "Will need a billing migration freeze for the cutover.",
        "thread_ts": "1748210000.000100",
        "reply_count": 0,
        "reactions": []
      }
    ]
  }
}
```

</details>

### spotify-api (port 8039) — server: started

| Result | Method | Path | Status | Endpoint |
|--------|--------|------|--------|----------|
| PASS | GET | /health | 200 | health |
| PASS | GET | /v1/me | 200 | get me |
| PASS | GET | /v1/me/playlists | 200 | my playlists |
| PASS | GET | /v1/playlists/37i9dQZF1DXcBWIGoYBM5M | 200 | get playlist |
| PASS | GET | /v1/playlists/37i9dQZF1DXcBWIGoYBM5M/tracks | 200 | playlist tracks |
| PASS | POST | /v1/users/user-leo/playlists | 201 | create playlist |
| PASS | POST | /v1/playlists/2v3iNvBX8Ay1Gt2uXtUKUg/tracks | 201 | add tracks |
| PASS | GET | /v1/search?q=neon&type=track,artist | 200 | search |
| PASS | GET | /v1/me/player | 200 | player state |
| PASS | PUT | /v1/me/player/play | 200 | play |

<details><summary>responses</summary>

**GET health** — `/health` (status 200)

```
{
  "status": "ok"
}
```

**GET get me** — `/v1/me` (status 200)

```
{
  "id": "user-leo",
  "display_name": "Leo Vasquez",
  "email": "leo.vasquez@example.com",
  "country": "US",
  "product": "premium",
  "followers": 312,
  "images": [
    {
      "url": "https://img.example.com/leo.png",
      "height": 300,
      "width": 300
    }
  ]
}
```

**GET my playlists** — `/v1/me/playlists` (status 200)

```
{
  "items": [
    {
      "id": "37i9dQZF1DXcBWIGoYBM5M",
      "name": "Today's Top Hits",
      "description": "The hottest tracks right now.",
      "owner": {
        "id": "user-leo"
      },
      "public": true,
      "collaborative": false,
      "uri": "spotify:playlist:37i9dQZF1DXcBWIGoYBM5M",
      "tracks": {
        "total": 3
      }
    },
    {
      "id": "2v3iNvBX8Ay1Gt2uXtUKUg",
      "name": "Indie Chill",
      "description": "Laid-back indie for focus and calm.",
      "owner": {
        "id": "user-leo"
      },
      "public": true,
      "collaborative": false,
      
... (truncated)
```

**GET get playlist** — `/v1/playlists/37i9dQZF1DXcBWIGoYBM5M` (status 200)

```
{
  "id": "37i9dQZF1DXcBWIGoYBM5M",
  "name": "Today's Top Hits",
  "description": "The hottest tracks right now.",
  "owner": {
    "id": "user-leo"
  },
  "public": true,
  "collaborative": false,
  "uri": "spotify:playlist:37i9dQZF1DXcBWIGoYBM5M",
  "tracks": {
    "total": 3,
    "items": [
      {
        "added_at": "2026-05-20T08:00:00Z",
        "track": {
          "id": "5fE6gF7hG8iH9jI0kJ1lK2",
          "name": "Caliente",
          "duration_ms": 198400,
          "popularity": 88,
          "explicit": true,
          "track_number": 1,
          "artist": {
            "id": "3r
... (truncated)
```

**GET playlist tracks** — `/v1/playlists/37i9dQZF1DXcBWIGoYBM5M/tracks` (status 200)

```
{
  "total": 3,
  "items": [
    {
      "added_at": "2026-05-20T08:00:00Z",
      "track": {
        "id": "5fE6gF7hG8iH9jI0kJ1lK2",
        "name": "Caliente",
        "duration_ms": 198400,
        "popularity": 88,
        "explicit": true,
        "track_number": 1,
        "artist": {
          "id": "3rT0fQ8sNuVbXc2Yd9Lm4p",
          "name": "Cassia Moreno"
        },
        "album": {
          "id": "1dE2fG3hI4jK5lM6nO7pQ8",
          "name": "Calor",
          "release_date": "2025-02-28"
        },
        "uri": "spotify:track:5fE6gF7hG8iH9jI0kJ1lK2"
      }
    },
    {
      "a
... (truncated)
```

**POST create playlist** — `/v1/users/user-leo/playlists` (status 201)

```
{
  "id": "7ywdP9TLsmUUMc7D6eNZmf",
  "name": "Road Trip 2026",
  "description": "Long drive mix",
  "owner": {
    "id": "user-leo"
  },
  "public": false,
  "collaborative": false,
  "uri": "spotify:playlist:7ywdP9TLsmUUMc7D6eNZmf",
  "tracks": {
    "total": 0,
    "items": []
  }
}
```

**POST add tracks** — `/v1/playlists/2v3iNvBX8Ay1Gt2uXtUKUg/tracks` (status 201)

```
{
  "playlist_id": "2v3iNvBX8Ay1Gt2uXtUKUg",
  "added": 1,
  "snapshot_id": "UMtHwPCz327Kn9P4KU1Bou"
}
```

**GET search** — `/v1/search?q=neon&type=track,artist` (status 200)

```
{
  "tracks": {
    "items": [
      {
        "id": "4eD5fE6gF7hG8iH9jI0kJ1",
        "name": "Neon Rails",
        "duration_ms": 243300,
        "popularity": 62,
        "explicit": false,
        "track_number": 2,
        "artist": {
          "id": "6mZ8tQ1nXpLkWv7Yd0fJ3a",
          "name": "The Midnight Trains"
        },
        "album": {
          "id": "7pQ8rS9tU0vW1xY2zA3bC4",
          "name": "Last Express",
          "release_date": "2023-05-19"
        },
        "uri": "spotify:track:4eD5fE6gF7hG8iH9jI0kJ1"
      }
    ],
    "total": 1
  },
  "artists": {
    "items": [],
 
```

**GET player state** — `/v1/me/player` (status 200)

```
{
  "is_playing": false,
  "device": {
    "id": "device-web-001",
    "name": "Web Player",
    "type": "Computer",
    "volume_percent": 65
  },
  "shuffle_state": false,
  "repeat_state": "off",
  "progress_ms": 0,
  "item": null
}
```

**PUT play** — `/v1/me/player/play` (status 200)

```
{
  "is_playing": true,
  "device": {
    "id": "device-web-001",
    "name": "Web Player",
    "type": "Computer",
    "volume_percent": 65
  },
  "shuffle_state": false,
  "repeat_state": "off",
  "progress_ms": 0,
  "item": {
    "id": "3dC4eD5fE6gF7hG8iH9jI0",
    "name": "Midnight Line",
    "duration_ms": 256800,
    "popularity": 69,
    "explicit": false,
    "track_number": 1,
    "artist": {
      "id": "6mZ8tQ1nXpLkWv7Yd0fJ3a",
      "name": "The Midnight Trains"
    },
    "album": {
      "id": "7pQ8rS9tU0vW1xY2zA3bC4",
      "name": "Last Express",
      "release_date": "2023-05-
```

</details>

### square-api (port 8041) — server: started

| Result | Method | Path | Status | Endpoint |
|--------|--------|------|--------|----------|
| PASS | GET | /health | 200 | health |
| PASS | GET | /v2/merchants/me | 200 | get merchant |
| PASS | GET | /v2/payments?limit=10 | 200 | list payments |
| PASS | GET | /v2/payments/PAY_AURORA01 | 200 | get payment |
| PASS | POST | /v2/payments | 201 | create payment |
| PASS | POST | /v2/refunds | 201 | create refund |
| PASS | GET | /v2/customers?limit=10 | 200 | list customers |
| PASS | GET | /v2/customers/CUST_MAYA03 | 200 | get customer |
| PASS | POST | /v2/customers | 201 | create customer |
| PASS | GET | /v2/catalog/list?types=ITEM | 200 | list catalog |
| PASS | POST | /v2/orders | 201 | create order |
| PASS | GET | /v2/orders/ORD_AURORA01 | 200 | get order |
| PASS | GET | /v2/inventory/VAR_BEANS_12 | 200 | get inventory |

<details><summary>responses</summary>

**GET health** — `/health` (status 200)

```
{
  "status": "ok"
}
```

**GET get merchant** — `/v2/merchants/me` (status 200)

```
{
  "merchant": {
    "id": "MERCH_RIVERSIDE",
    "business_name": "Riverside Coffee Co.",
    "country": "US",
    "language_code": "en-US",
    "currency": "USD",
    "status": "ACTIVE",
    "main_location_id": "LOC_MAIN",
    "created_at": "2025-08-01T00:00:00Z"
  }
}
```

**GET list payments** — `/v2/payments?limit=10` (status 200)

```
{
  "payments": [
    {
      "id": "PAY_AURORA01",
      "order_id": "ORD_AURORA01",
      "customer_id": "CUST_HARPER01",
      "amount_money": {
        "amount": 825,
        "currency": "USD"
      },
      "status": "COMPLETED",
      "source_type": "CARD",
      "location_id": "LOC_MAIN",
      "receipt_number": "RCP001",
      "created_at": "2026-05-20T08:15:00Z"
    },
    {
      "id": "PAY_BOREAL02",
      "order_id": "ORD_BOREAL02",
      "customer_id": "CUST_DIEGO02",
      "amount_money": {
        "amount": 500,
        "currency": "USD"
      },
      "status": "COMPLETED",
   
... (truncated)
```

**GET get payment** — `/v2/payments/PAY_AURORA01` (status 200)

```
{
  "payment": {
    "id": "PAY_AURORA01",
    "order_id": "ORD_AURORA01",
    "customer_id": "CUST_HARPER01",
    "amount_money": {
      "amount": 825,
      "currency": "USD"
    },
    "status": "COMPLETED",
    "source_type": "CARD",
    "location_id": "LOC_MAIN",
    "receipt_number": "RCP001",
    "created_at": "2026-05-20T08:15:00Z"
  }
}
```

**POST create payment** — `/v2/payments` (status 201)

```
{
  "payment": {
    "id": "PAY_1E79985203514E848E",
    "order_id": null,
    "customer_id": "CUST_HARPER01",
    "amount_money": {
      "amount": 750,
      "currency": "USD"
    },
    "status": "COMPLETED",
    "source_type": "CARD",
    "location_id": "LOC_MAIN",
    "receipt_number": "RCP008",
    "created_at": "2026-06-17T10:31:40Z"
  }
}
```

**POST create refund** — `/v2/refunds` (status 201)

```
{
  "refund": {
    "id": "REF_CB6E859154B84319B6",
    "payment_id": "PAY_AURORA01",
    "amount_money": {
      "amount": 825,
      "currency": "USD"
    },
    "status": "COMPLETED",
    "reason": "Damaged item",
    "created_at": "2026-06-17T10:31:40Z"
  }
}
```

**GET list customers** — `/v2/customers?limit=10` (status 200)

```
{
  "customers": [
    {
      "id": "CUST_HARPER01",
      "given_name": "Harper",
      "family_name": "Nguyen",
      "email_address": "harper.nguyen@example.com",
      "phone_number": "+14155550101",
      "company_name": "Riverside Cafe",
      "created_at": "2025-08-12T09:00:00Z"
    },
    {
      "id": "CUST_DIEGO02",
      "given_name": "Diego",
      "family_name": "Ramos",
      "email_address": "diego.ramos@example.com",
      "phone_number": "+14155550102",
      "company_name": null,
      "created_at": "2025-09-03T11:30:00Z"
    },
    {
      "id": "CUST_MAYA03",
      "given_
... (truncated)
```

**GET get customer** — `/v2/customers/CUST_MAYA03` (status 200)

```
{
  "customer": {
    "id": "CUST_MAYA03",
    "given_name": "Maya",
    "family_name": "Fischer",
    "email_address": "maya.fischer@example.com",
    "phone_number": "+14155550103",
    "company_name": "Fischer Bakery",
    "created_at": "2025-09-21T14:10:00Z"
  }
}
```

**POST create customer** — `/v2/customers` (status 201)

```
{
  "customer": {
    "id": "CUST_F416A98D3C854E8C93",
    "given_name": "Nina",
    "family_name": "Costa",
    "email_address": "nina.costa@example.com",
    "phone_number": null,
    "company_name": null,
    "created_at": "2026-06-17T10:31:40Z"
  }
}
```

**GET list catalog** — `/v2/catalog/list?types=ITEM` (status 200)

```
{
  "objects": [
    {
      "type": "ITEM",
      "id": "ITEM_LATTE",
      "item_data": {
        "name": "Caffe Latte",
        "description": "Espresso with steamed milk",
        "category": "Drinks",
        "variations": [
          {
            "type": "ITEM_VARIATION",
            "id": "VAR_LATTE_R",
            "item_variation_data": {
              "name": "Regular",
              "price_money": {
                "amount": 450,
                "currency": "USD"
              }
            }
          }
        ]
      }
    },
    {
      "type": "ITEM",
      "id": "ITEM_COLDBREW
... (truncated)
```

**POST create order** — `/v2/orders` (status 201)

```
{
  "order": {
    "id": "ORD_C13EDA1641BE42E495",
    "customer_id": "CUST_DIEGO02",
    "location_id": "LOC_MAIN",
    "line_items": [
      {
        "catalog_object_id": "VAR_LATTE_R",
        "quantity": "2"
      },
      {
        "catalog_object_id": "VAR_CROISSANT_R",
        "quantity": "1"
      }
    ],
    "total_money": {
      "amount": 1275,
      "currency": "USD"
    },
    "state": "OPEN",
    "created_at": "2026-06-17T10:31:40Z"
  }
}
```

**GET get order** — `/v2/orders/ORD_AURORA01` (status 200)

```
{
  "order": {
    "id": "ORD_AURORA01",
    "customer_id": "CUST_HARPER01",
    "location_id": "LOC_MAIN",
    "line_items": [
      {
        "catalog_object_id": "VAR_LATTE_R",
        "quantity": "1"
      },
      {
        "catalog_object_id": "VAR_CROISSANT_R",
        "quantity": "1"
      }
    ],
    "total_money": {
      "amount": 825,
      "currency": "USD"
    },
    "state": "COMPLETED",
    "created_at": "2026-05-20T08:14:00Z"
  }
}
```

**GET get inventory** — `/v2/inventory/VAR_BEANS_12` (status 200)

```
{
  "counts": [
    {
      "catalog_object_id": "VAR_BEANS_12",
      "location_id": "LOC_MAIN",
      "quantity": "82",
      "state": "IN_STOCK"
    }
  ]
}
```

</details>

### strava-api (port 8060) — server: started

| Result | Method | Path | Status | Endpoint |
|--------|--------|------|--------|----------|
| PASS | GET | /health | 200 | health |
| PASS | GET | /api/v3/athlete | 200 | get athlete |
| PASS | GET | /api/v3/athlete/activities?per_page=5 | 200 | list activities |
| PASS | GET | /api/v3/activities/9002 | 200 | get activity |
| PASS | PUT | /api/v3/activities/9002 | 200 | update activity |
| PASS | GET | /api/v3/activities/9002/kudos | 200 | activity kudos |
| PASS | GET | /api/v3/segments/3302 | 200 | get segment |
| PASS | GET | /api/v3/athletes/4410022/stats | 200 | athlete stats |

<details><summary>responses</summary>

**GET health** — `/health` (status 200)

```
{
  "status": "ok"
}
```

**GET get athlete** — `/api/v3/athlete` (status 200)

```
{
  "id": 4410022,
  "username": "nadia_runs",
  "firstname": "Nadia",
  "lastname": "Voss",
  "city": "Portland",
  "state": "OR",
  "country": "United States",
  "sex": "F",
  "premium": true,
  "weight": 61.0,
  "ftp": 198,
  "follower_count": 214,
  "friend_count": 187,
  "created_at": "2019-03-11T08:00:00Z"
}
```

**GET list activities** — `/api/v3/athlete/activities?per_page=5` (status 200)

```
[
  {
    "id": 9012,
    "name": "Track 400s",
    "type": "Run",
    "sport_type": "Run",
    "distance": 8000.0,
    "moving_time": 1740,
    "elapsed_time": 2400,
    "total_elevation_gain": 12.0,
    "average_speed": 4.6,
    "start_date": "2025-05-19T01:30:00Z",
    "kudos_count": 19,
    "segment_id": 3302
  },
  {
    "id": 9011,
    "name": "Gravel explorer",
    "type": "Ride",
    "sport_type": "Ride",
    "distance": 61300.0,
    "moving_time": 9000,
    "elapsed_time": 10200,
    "total_elevation_gain": 890.0,
    "average_speed": 6.81,
    "start_date": "2025-05-17T14:30:00Z",
  
... (truncated)
```

**GET get activity** — `/api/v3/activities/9002` (status 200)

```
{
  "id": 9002,
  "name": "Tempo Tuesday",
  "type": "Run",
  "sport_type": "Run",
  "distance": 11800.0,
  "moving_time": 3120,
  "elapsed_time": 3200,
  "total_elevation_gain": 88.0,
  "average_speed": 3.78,
  "start_date": "2025-05-03T13:05:00Z",
  "kudos_count": 21,
  "segment_id": 3302,
  "athlete": {
    "id": 4410022
  }
}
```

**PUT update activity** — `/api/v3/activities/9002` (status 200)

```
{
  "id": 9002,
  "name": "Tempo Tuesday",
  "type": "Run",
  "sport_type": "Run",
  "distance": 11800.0,
  "moving_time": 3120,
  "elapsed_time": 3200,
  "total_elevation_gain": 88.0,
  "average_speed": 3.78,
  "start_date": "2025-05-03T13:05:00Z",
  "kudos_count": 21,
  "segment_id": 3302,
  "athlete": {
    "id": 4410022
  }
}
```

**GET activity kudos** — `/api/v3/activities/9002/kudos` (status 200)

```
[
  {
    "firstname": "Marcus",
    "lastname": "Lindqvist"
  },
  {
    "firstname": "Priya",
    "lastname": "Anand"
  },
  {
    "firstname": "Tom",
    "lastname": "Becker"
  }
]
```

**GET get segment** — `/api/v3/segments/3302` (status 200)

```
{
  "id": 3302,
  "name": "Powell Butte Climb",
  "activity_type": "Run",
  "distance": 1800.0,
  "average_grade": 6.8,
  "maximum_grade": 11.2,
  "elevation_high": 188.0,
  "elevation_low": 66.0,
  "climb_category": 2,
  "city": "Portland",
  "state": "OR"
}
```

**GET athlete stats** — `/api/v3/athletes/4410022/stats` (status 200)

```
{
  "all_run_totals": {
    "count": 6,
    "distance": 53400.0,
    "moving_time": 15120,
    "elevation_gain": 640.0
  },
  "all_ride_totals": {
    "count": 4,
    "distance": 228100.0,
    "moving_time": 31440,
    "elevation_gain": 2900.0
  },
  "all_swim_totals": {
    "count": 2,
    "distance": 5400.0,
    "moving_time": 6000,
    "elevation_gain": 0.0
  }
}
```

</details>

### stripe-api (port 8021) — server: started

| Result | Method | Path | Status | Endpoint |
|--------|--------|------|--------|----------|
| PASS | GET | /health | 200 | health |
| PASS | GET | /v1/customers?limit=5 | 200 | list customers |
| PASS | GET | /v1/customers/cus_Nb1Aurora | 200 | get customer |
| PASS | POST | /v1/customers | 201 | create customer |
| PASS | GET | /v1/products | 200 | list products |
| PASS | GET | /v1/prices?product=prod_Pro | 200 | list prices |
| PASS | POST | /v1/payment_intents | 201 | create payment intent |
| WARN | GET | /v1/payment_intents/pi_example | 404 | get payment intent (404 expected - placeholder ID) |
| PASS | GET | /v1/charges?customer=cus_Nb1Aurora | 200 | list charges |
| PASS | GET | /v1/charges/ch_3Aurora01 | 200 | get charge |
| PASS | POST | /v1/charges | 201 | create charge |
| PASS | POST | /v1/refunds | 201 | create refund |
| PASS | GET | /v1/invoices?status=open | 200 | list invoices |
| PASS | GET | /v1/invoices/in_Aurora001 | 200 | get invoice |
| PASS | POST | /v1/invoices | 201 | create invoice |
| PASS | GET | /v1/subscriptions?status=active | 200 | list subscriptions |
| PASS | GET | /v1/subscriptions/sub_Aurora | 200 | get subscription |
| PASS | POST | /v1/subscriptions | 201 | create subscription |
| PASS | GET | /v1/balance | 200 | get balance |

<details><summary>responses</summary>

**GET health** — `/health` (status 200)

```
{
  "status": "ok"
}
```

**GET list customers** — `/v1/customers?limit=5` (status 200)

```
{
  "object": "list",
  "url": "/v1/customers",
  "has_more": false,
  "data": [
    {
      "id": "cus_Nb1Aurora",
      "name": "Aurora Bistro LLC",
      "email": "billing@aurorabistro.com",
      "description": "Monthly POS subscription",
      "currency": "usd",
      "delinquent": false,
      "balance": 0,
      "created": 1714579200,
      "phone": "+14155550101",
      "object": "customer"
    },
    {
      "id": "cus_Nb2Helix",
      "name": "Helix Robotics Inc",
      "email": "ap@helixrobotics.io",
      "description": "Enterprise plan",
      "currency": "usd",
      "delinquent"
... (truncated)
```

**GET get customer** — `/v1/customers/cus_Nb1Aurora` (status 200)

```
{
  "id": "cus_Nb1Aurora",
  "name": "Aurora Bistro LLC",
  "email": "billing@aurorabistro.com",
  "description": "Monthly POS subscription",
  "currency": "usd",
  "delinquent": false,
  "balance": 0,
  "created": 1714579200,
  "phone": "+14155550101",
  "object": "customer"
}
```

**POST create customer** — `/v1/customers` (status 201)

```
{
  "id": "cus_556f55903b324b1a",
  "object": "customer",
  "name": "Nimbus Coffee",
  "email": "billing@nimbus.coffee",
  "description": "New POS customer",
  "currency": "usd",
  "delinquent": false,
  "balance": 0,
  "phone": "",
  "created": 1781692301
}
```

**GET list products** — `/v1/products` (status 200)

```
{
  "object": "list",
  "url": "/v1/products",
  "has_more": false,
  "data": [
    {
      "id": "prod_Starter",
      "name": "Starter Plan",
      "description": "Up to 3 seats and basic reporting",
      "active": true,
      "created": 1700000000,
      "object": "product"
    },
    {
      "id": "prod_Pro",
      "name": "Pro Plan",
      "description": "Unlimited seats and advanced analytics",
      "active": true,
      "created": 1700000000,
      "object": "product"
    },
    {
      "id": "prod_Enterprise",
      "name": "Enterprise Plan",
      "description": "Dedicated support a
... (truncated)
```

**GET list prices** — `/v1/prices?product=prod_Pro` (status 200)

```
{
  "object": "list",
  "url": "/v1/prices",
  "has_more": false,
  "data": [
    {
      "id": "price_Pro_M",
      "product": "prod_Pro",
      "unit_amount": 4900,
      "currency": "usd",
      "recurring_interval": "month",
      "active": true,
      "nickname": "Pro Monthly",
      "object": "price",
      "recurring": {
        "interval": "month"
      },
      "type": "recurring"
    },
    {
      "id": "price_Pro_Y",
      "product": "prod_Pro",
      "unit_amount": 49000,
      "currency": "usd",
      "recurring_interval": "year",
      "active": true,
      "nickname": "Pro Annu
```

**POST create payment intent** — `/v1/payment_intents` (status 201)

```
{
  "id": "pi_05c366ff4d5f41ad",
  "object": "payment_intent",
  "amount": 4900,
  "currency": "usd",
  "customer": "cus_Nb3Lumen",
  "description": "Pro Monthly",
  "status": "succeeded",
  "latest_charge": "ch_b191294d06694c4a",
  "created": 1781692301
}
```

**GET get payment intent (404 expected - placeholder ID)** — `/v1/payment_intents/pi_example` (status 404)

```
{
  "error": "No such payment_intent: pi_example"
}
```

**GET list charges** — `/v1/charges?customer=cus_Nb1Aurora` (status 200)

```
{
  "object": "list",
  "url": "/v1/charges",
  "has_more": false,
  "data": [
    {
      "id": "ch_3Aurora01",
      "customer": "cus_Nb1Aurora",
      "amount": 1900,
      "currency": "usd",
      "status": "succeeded",
      "paid": true,
      "refunded": false,
      "amount_refunded": 0,
      "description": "Starter Monthly",
      "payment_intent": "pi_3Aurora01",
      "created": 1717286400,
      "object": "charge"
    },
    {
      "id": "ch_3Aurora02",
      "customer": "cus_Nb1Aurora",
      "amount": 9900,
      "currency": "usd",
      "status": "succeeded",
      "paid": tru
```

**GET get charge** — `/v1/charges/ch_3Aurora01` (status 200)

```
{
  "id": "ch_3Aurora01",
  "customer": "cus_Nb1Aurora",
  "amount": 1900,
  "currency": "usd",
  "status": "succeeded",
  "paid": true,
  "refunded": false,
  "amount_refunded": 0,
  "description": "Starter Monthly",
  "payment_intent": "pi_3Aurora01",
  "created": 1717286400,
  "object": "charge"
}
```

**POST create charge** — `/v1/charges` (status 201)

```
{
  "id": "ch_0d7ef83ad7e447a4",
  "object": "charge",
  "customer": "cus_Nb1Aurora",
  "amount": 9900,
  "currency": "usd",
  "status": "succeeded",
  "paid": true,
  "refunded": false,
  "amount_refunded": 0,
  "description": "POS Bundle",
  "payment_intent": null,
  "created": 1781692301
}
```

**POST create refund** — `/v1/refunds` (status 201)

```
{
  "id": "re_bc8e36056dab4e71",
  "object": "refund",
  "charge": "ch_3Aurora01",
  "amount": 1900,
  "currency": "usd",
  "reason": "requested_by_customer",
  "status": "succeeded",
  "created": 1781692301
}
```

**GET list invoices** — `/v1/invoices?status=open` (status 200)

```
{
  "object": "list",
  "url": "/v1/invoices",
  "has_more": false,
  "data": [
    {
      "id": "in_Pelagic001",
      "customer": "cus_Nb4Pelagic",
      "subscription": null,
      "amount_due": 12500,
      "amount_paid": 0,
      "currency": "usd",
      "status": "open",
      "number": "ORBIT-0004",
      "charge": null,
      "created": 1717545600,
      "due_date": 1720137600,
      "object": "invoice"
    },
    {
      "id": "in_Verdant001",
      "customer": "cus_Nb5Verdant",
      "subscription": "sub_Verdant",
      "amount_due": 4900,
      "amount_paid": 0,
      "currency": "
```

**GET get invoice** — `/v1/invoices/in_Aurora001` (status 200)

```
{
  "id": "in_Aurora001",
  "customer": "cus_Nb1Aurora",
  "subscription": "sub_Aurora",
  "amount_due": 1900,
  "amount_paid": 1900,
  "currency": "usd",
  "status": "paid",
  "number": "ORBIT-0001",
  "charge": "ch_3Aurora01",
  "created": 1717286400,
  "due_date": 1717286400,
  "object": "invoice"
}
```

**POST create invoice** — `/v1/invoices` (status 201)

```
{
  "id": "in_373a979289464718",
  "object": "invoice",
  "customer": "cus_Nb1Aurora",
  "subscription": null,
  "amount_due": 4900,
  "amount_paid": 0,
  "currency": "usd",
  "status": "draft",
  "number": "ORBIT-0008",
  "charge": null,
  "created": 1781692301,
  "due_date": null
}
```

**GET list subscriptions** — `/v1/subscriptions?status=active` (status 200)

```
{
  "object": "list",
  "url": "/v1/subscriptions",
  "has_more": false,
  "data": [
    {
      "id": "sub_Aurora",
      "customer": "cus_Nb1Aurora",
      "price": "price_Starter_M",
      "status": "active",
      "quantity": 1,
      "current_period_start": 1717286400,
      "current_period_end": 1719878400,
      "cancel_at_period_end": false,
      "created": 1714579200,
      "object": "subscription"
    },
    {
      "id": "sub_Helix",
      "customer": "cus_Nb2Helix",
      "price": "price_Ent_M",
      "status": "active",
      "quantity": 5,
      "current_period_start": 171737280
... (truncated)
```

**GET get subscription** — `/v1/subscriptions/sub_Aurora` (status 200)

```
{
  "id": "sub_Aurora",
  "customer": "cus_Nb1Aurora",
  "price": "price_Starter_M",
  "status": "active",
  "quantity": 1,
  "current_period_start": 1717286400,
  "current_period_end": 1719878400,
  "cancel_at_period_end": false,
  "created": 1714579200,
  "object": "subscription"
}
```

**POST create subscription** — `/v1/subscriptions` (status 201)

```
{
  "id": "sub_77d8989cb8314cb6",
  "object": "subscription",
  "customer": "cus_Nb1Aurora",
  "price": "price_Pro_M",
  "status": "active",
  "quantity": 1,
  "current_period_start": 1781692301,
  "current_period_end": 1784284301,
  "cancel_at_period_end": false,
  "created": 1781692301
}
```

**GET get balance** — `/v1/balance` (status 200)

```
{
  "object": "balance",
  "livemode": false,
  "available": [
    {
      "amount": 184200,
      "currency": "usd",
      "source_types": {
        "card": 184200
      }
    }
  ],
  "pending": [
    {
      "amount": 4900,
      "currency": "usd",
      "source_types": {
        "card": 4900
      }
    }
  ],
  "connect_reserved": [
    {
      "amount": 0,
      "currency": "usd"
    }
  ]
}
```

</details>

### telegram-api (port 8063) — server: started

| Result | Method | Path | Status | Endpoint |
|--------|--------|------|--------|----------|
| PASS | GET | /health | 200 | health |
| PASS | GET | /bot/getMe | 200 | getMe |
| PASS | GET | /bot/getUpdates?limit=10 | 200 | getUpdates |
| PASS | GET | /bot/getChat?chat_id=-200500 | 200 | getChat |
| PASS | GET | /bot/getChatMember?chat_id=-200500&user_id=9002 | 200 | getChatMember |
| PASS | POST | /bot/sendMessage | 200 | sendMessage |
| PASS | POST | /bot/sendPhoto | 200 | sendPhoto |
| PASS | POST | /bot/editMessageText | 200 | editMessageText |
| PASS | POST | /bot/deleteMessage | 200 | deleteMessage |

<details><summary>responses</summary>

**GET health** — `/health` (status 200)

```
{
  "status": "ok"
}
```

**GET getMe** — `/bot/getMe` (status 200)

```
{
  "ok": true,
  "result": {
    "id": 7654321098,
    "is_bot": true,
    "first_name": "Orbit Ops Bot",
    "username": "orbit_ops_bot",
    "can_join_groups": true,
    "can_read_all_group_messages": false,
    "supports_inline_queries": false
  }
}
```

**GET getUpdates** — `/bot/getUpdates?limit=10` (status 200)

```
{
  "ok": true,
  "result": [
    {
      "update_id": 100001,
      "message": {
        "message_id": 5001,
        "from": {
          "id": 9001,
          "is_bot": false,
          "first_name": "Amelia",
          "last_name": "Ortega",
          "username": "amelia_o"
        },
        "chat": {
          "id": -200500,
          "type": "group",
          "title": "Orbit Eng Standup",
          "description": "Daily standup and incident coordination for the platform team."
        },
        "date": 1748240000,
        "text": "Standup in 5. Drop blockers in the thread."
      }
    
... (truncated)
```

**GET getChat** — `/bot/getChat?chat_id=-200500` (status 200)

```
{
  "ok": true,
  "result": {
    "id": -200500,
    "type": "group",
    "title": "Orbit Eng Standup",
    "description": "Daily standup and incident coordination for the platform team.",
    "member_count": 6
  }
}
```

**GET getChatMember** — `/bot/getChatMember?chat_id=-200500&user_id=9002` (status 200)

```
{
  "ok": true,
  "result": {
    "user": {
      "id": 9002,
      "is_bot": false,
      "first_name": "Jonas",
      "last_name": "Pereira",
      "username": "jonas_p"
    },
    "status": "administrator"
  }
}
```

**POST sendMessage** — `/bot/sendMessage` (status 200)

```
{
  "ok": true,
  "result": {
    "message_id": 5010,
    "from": {
      "id": 7654321098,
      "is_bot": true,
      "first_name": "Orbit Ops Bot",
      "username": "orbit_ops_bot"
    },
    "chat": {
      "id": -200500,
      "type": "group",
      "title": "Orbit Eng Standup",
      "description": "Daily standup and incident coordination for the platform team."
    },
    "date": 1781692301,
    "text": "Standup starting now."
  }
}
```

**POST sendPhoto** — `/bot/sendPhoto` (status 200)

```
{
  "ok": true,
  "result": {
    "message_id": 5011,
    "from": {
      "id": 7654321098,
      "is_bot": true,
      "first_name": "Orbit Ops Bot",
      "username": "orbit_ops_bot"
    },
    "chat": {
      "id": -200501,
      "type": "supergroup",
      "title": "Orbit Deploys",
      "description": "Automated deploy and alerting notifications."
    },
    "date": 1781692301,
    "caption": "Latest deploy dashboard",
    "photo": [
      {
        "file_id": "AgACAgIAAxkBAAIB",
        "width": 1280,
        "height": 720
      }
    ]
  }
}
```

**POST editMessageText** — `/bot/editMessageText` (status 200)

```
{
  "ok": true,
  "result": {
    "message_id": 5006,
    "from": {
      "id": 7654321098,
      "is_bot": true,
      "first_name": "Orbit Ops Bot",
      "username": "orbit_ops_bot"
    },
    "chat": {
      "id": 1001,
      "type": "private",
      "username": "amelia_o",
      "first_name": "Amelia",
      "last_name": "Ortega"
    },
    "date": 1748242000,
    "text": "Your on-call shift starts tomorrow at 10:00 UTC.",
    "edit_date": 1781692301
  }
}
```

**POST deleteMessage** — `/bot/deleteMessage` (status 200)

```
{
  "ok": true,
  "result": true
}
```

</details>

### ticketmaster-api (port 8075) — server: started

| Result | Method | Path | Status | Endpoint |
|--------|--------|------|--------|----------|
| PASS | GET | /health | 200 | health |
| PASS | GET | /discovery/v2/events | 200 | search events |
| PASS | GET | /discovery/v2/events?keyword=Aria | 200 | search events by keyword |
| PASS | GET | /discovery/v2/events?city=New York&classificationName=Music | 200 | search events by city + classification |
| PASS | GET | /discovery/v2/events?startDateTime=2026-09-01T00:00:00Z | 200 | search events by startDateTime |
| PASS | GET | /discovery/v2/events/evt-1001 | 200 | get event |
| PASS | GET | /discovery/v2/venues?keyword=Arena | 200 | search venues |
| PASS | GET | /discovery/v2/venues/ven-001 | 200 | get venue |
| PASS | GET | /discovery/v2/attractions?keyword=Echoes | 200 | search attractions |
| PASS | GET | /discovery/v2/attractions/att-001 | 200 | get attraction |
| PASS | GET | /discovery/v2/classifications | 200 | list classifications |

<details><summary>responses</summary>

**GET health** — `/health` (status 200)

```
{
  "status": "ok"
}
```

**GET search events** — `/discovery/v2/events` (status 200)

```
{
  "_embedded": {
    "events": [
      {
        "id": "evt-1001",
        "name": "The Midnight Echoes Live",
        "dates": {
          "start": {
            "dateTime": "2026-07-12T20:00:00Z"
          },
          "status": {
            "code": "onsale"
          }
        },
        "classifications": [
          {
            "segment": {
              "name": "Music"
            },
            "genre": {
              "name": "Rock"
            },
            "subGenre": {
              "name": "Alternative Rock"
            }
          }
        ],
        "priceRanges": [
      
... (truncated)
```

**GET search events by keyword** — `/discovery/v2/events?keyword=Aria` (status 200)

```
{
  "_embedded": {
    "events": [
      {
        "id": "evt-1002",
        "name": "Aria Sloane World Tour",
        "dates": {
          "start": {
            "dateTime": "2026-08-03T19:30:00Z"
          },
          "status": {
            "code": "onsale"
          }
        },
        "classifications": [
          {
            "segment": {
              "name": "Music"
            },
            "genre": {
              "name": "Pop"
            },
            "subGenre": {
              "name": "Pop"
            }
          }
        ],
        "priceRanges": [
          {
          
... (truncated)
```

**GET search events by city + classification** — `/discovery/v2/events?city=New York&classificationName=Music` (status 200)

```
{
  "_embedded": {
    "events": [
      {
        "id": "evt-1001",
        "name": "The Midnight Echoes Live",
        "dates": {
          "start": {
            "dateTime": "2026-07-12T20:00:00Z"
          },
          "status": {
            "code": "onsale"
          }
        },
        "classifications": [
          {
            "segment": {
              "name": "Music"
            },
            "genre": {
              "name": "Rock"
            },
            "subGenre": {
              "name": "Alternative Rock"
            }
          }
        ],
        "priceRanges": [
      
... (truncated)
```

**GET search events by startDateTime** — `/discovery/v2/events?startDateTime=2026-09-01T00:00:00Z` (status 200)

```
{
  "_embedded": {
    "events": [
      {
        "id": "evt-1006",
        "name": "Starlight Musical Premiere",
        "dates": {
          "start": {
            "dateTime": "2026-09-10T19:00:00Z"
          },
          "status": {
            "code": "onsale"
          }
        },
        "classifications": [
          {
            "segment": {
              "name": "Arts & Theatre"
            },
            "genre": {
              "name": "Theatre"
            },
            "subGenre": {
              "name": "Musical"
            }
          }
        ],
        "priceRanges": [
 
... (truncated)
```

**GET get event** — `/discovery/v2/events/evt-1001` (status 200)

```
{
  "id": "evt-1001",
  "name": "The Midnight Echoes Live",
  "dates": {
    "start": {
      "dateTime": "2026-07-12T20:00:00Z"
    },
    "status": {
      "code": "onsale"
    }
  },
  "classifications": [
    {
      "segment": {
        "name": "Music"
      },
      "genre": {
        "name": "Rock"
      },
      "subGenre": {
        "name": "Alternative Rock"
      }
    }
  ],
  "priceRanges": [
    {
      "type": "standard",
      "currency": "USD",
      "min": 55.0,
      "max": 180.0
    }
  ],
  "_embedded": {
    "venues": [
      {
        "id": "ven-001",
        "name": "Ma
... (truncated)
```

**GET search venues** — `/discovery/v2/venues?keyword=Arena` (status 200)

```
{
  "_embedded": {
    "venues": [
      {
        "id": "ven-001",
        "name": "Madison Arc Arena",
        "city": {
          "name": "New York"
        },
        "state": {
          "stateCode": "NY"
        },
        "country": {
          "countryCode": "US"
        },
        "postalCode": "10001",
        "address": {
          "line1": "4 Pennsylvania Plaza"
        },
        "location": {
          "latitude": 40.7505,
          "longitude": -73.9934
        }
      }
    ]
  },
  "page": {
    "size": 1,
    "totalElements": 1,
    "totalPages": 1,
    "number": 0
  }
}
```

**GET get venue** — `/discovery/v2/venues/ven-001` (status 200)

```
{
  "id": "ven-001",
  "name": "Madison Arc Arena",
  "city": {
    "name": "New York"
  },
  "state": {
    "stateCode": "NY"
  },
  "country": {
    "countryCode": "US"
  },
  "postalCode": "10001",
  "address": {
    "line1": "4 Pennsylvania Plaza"
  },
  "location": {
    "latitude": 40.7505,
    "longitude": -73.9934
  }
}
```

**GET search attractions** — `/discovery/v2/attractions?keyword=Echoes` (status 200)

```
{
  "_embedded": {
    "attractions": [
      {
        "id": "att-001",
        "name": "The Midnight Echoes",
        "type": "band",
        "upcomingEvents": {
          "_total": 3
        },
        "classifications": [
          {
            "segment": {
              "name": "Music"
            },
            "genre": {
              "name": "Rock"
            }
          }
        ]
      }
    ]
  },
  "page": {
    "size": 1,
    "totalElements": 1,
    "totalPages": 1,
    "number": 0
  }
}
```

**GET get attraction** — `/discovery/v2/attractions/att-001` (status 200)

```
{
  "id": "att-001",
  "name": "The Midnight Echoes",
  "type": "band",
  "upcomingEvents": {
    "_total": 3
  },
  "classifications": [
    {
      "segment": {
        "name": "Music"
      },
      "genre": {
        "name": "Rock"
      }
    }
  ]
}
```

**GET list classifications** — `/discovery/v2/classifications` (status 200)

```
{
  "_embedded": {
    "classifications": [
      {
        "id": "cls-music-rock",
        "segment": {
          "name": "Music",
          "_embedded": {
            "genres": [
              {
                "name": "Rock",
                "_embedded": {
                  "subgenres": [
                    {
                      "name": "Alternative Rock"
                    }
                  ]
                }
              }
            ]
          }
        }
      },
      {
        "id": "cls-music-pop",
        "segment": {
          "name": "Music",
          "_embedded": {
   
... (truncated)
```

</details>

### tmdb-api (port 8059) — server: started

| Result | Method | Path | Status | Endpoint |
|--------|--------|------|--------|----------|
| PASS | GET | /health | 200 | health |
| PASS | GET | /3/search/movie?query=orbit | 200 | search movie |
| PASS | GET | /3/movie/popular | 200 | movie popular |
| PASS | GET | /3/movie/101 | 200 | get movie |
| PASS | GET | /3/movie/101/credits | 200 | movie credits |
| PASS | GET | /3/tv/201 | 200 | get tv |
| PASS | GET | /3/genre/movie/list | 200 | genre movie list |
| PASS | GET | /3/trending/all/week | 200 | trending all week |

<details><summary>responses</summary>

**GET health** — `/health` (status 200)

```
{
  "status": "ok"
}
```

**GET search movie** — `/3/search/movie?query=orbit` (status 200)

```
{
  "page": 1,
  "results": [
    {
      "id": 101,
      "title": "The Quiet Orbit",
      "original_title": "The Quiet Orbit",
      "overview": "A marooned engineer races to repair a failing station before its orbit decays.",
      "release_date": "2024-03-15",
      "vote_average": 7.8,
      "vote_count": 2140,
      "genre_ids": [
        878,
        53
      ],
      "popularity": 142.6,
      "original_language": "en",
      "media_type": "movie",
      "adult": false
    }
  ],
  "total_pages": 1,
  "total_results": 1
}
```

**GET movie popular** — `/3/movie/popular` (status 200)

```
{
  "page": 1,
  "results": [
    {
      "id": 101,
      "title": "The Quiet Orbit",
      "original_title": "The Quiet Orbit",
      "overview": "A marooned engineer races to repair a failing station before its orbit decays.",
      "release_date": "2024-03-15",
      "vote_average": 7.8,
      "vote_count": 2140,
      "genre_ids": [
        878,
        53
      ],
      "popularity": 142.6,
      "original_language": "en",
      "media_type": "movie",
      "adult": false
    },
    {
      "id": 110,
      "title": "The Cartographer",
      "original_title": "The Cartographer",
      "o
... (truncated)
```

**GET get movie** — `/3/movie/101` (status 200)

```
{
  "id": 101,
  "title": "The Quiet Orbit",
  "original_title": "The Quiet Orbit",
  "overview": "A marooned engineer races to repair a failing station before its orbit decays.",
  "release_date": "2024-03-15",
  "vote_average": 7.8,
  "vote_count": 2140,
  "genre_ids": [
    878,
    53
  ],
  "popularity": 142.6,
  "original_language": "en",
  "media_type": "movie",
  "adult": false,
  "genres": [
    {
      "id": 878,
      "name": "Science Fiction"
    },
    {
      "id": 53,
      "name": "Thriller"
    }
  ]
}
```

**GET movie credits** — `/3/movie/101/credits` (status 200)

```
{
  "id": 101,
  "cast": [
    {
      "id": 501,
      "name": "Mara Devlin",
      "known_for_department": "Acting",
      "popularity": 24.6,
      "character": "Commander Iris Vale",
      "order": 0
    },
    {
      "id": 502,
      "name": "Theo Almasi",
      "known_for_department": "Acting",
      "popularity": 19.3,
      "character": "Engineer Dak",
      "order": 1
    }
  ],
  "crew": [
    {
      "id": 504,
      "name": "Hugo B\u00e9langer",
      "known_for_department": "Directing",
      "popularity": 12.1,
      "job": "Director",
      "department": "Directing"
    },
    
```

**GET get tv** — `/3/tv/201` (status 200)

```
{
  "id": 201,
  "name": "Station Eleven Hours",
  "original_name": "Station Eleven Hours",
  "overview": "An anthology set across one shift on a deep-space relay station.",
  "first_air_date": "2023-09-01",
  "vote_average": 8.0,
  "vote_count": 1240,
  "genre_ids": [
    878,
    18
  ],
  "popularity": 95.2,
  "number_of_seasons": 2,
  "number_of_episodes": 16,
  "media_type": "tv",
  "genres": [
    {
      "id": 878,
      "name": "Science Fiction"
    },
    {
      "id": 18,
      "name": "Drama"
    }
  ]
}
```

**GET genre movie list** — `/3/genre/movie/list` (status 200)

```
{
  "genres": [
    {
      "id": 28,
      "name": "Action"
    },
    {
      "id": 12,
      "name": "Adventure"
    },
    {
      "id": 16,
      "name": "Animation"
    },
    {
      "id": 35,
      "name": "Comedy"
    },
    {
      "id": 18,
      "name": "Drama"
    },
    {
      "id": 27,
      "name": "Horror"
    },
    {
      "id": 878,
      "name": "Science Fiction"
    },
    {
      "id": 10749,
      "name": "Romance"
    },
    {
      "id": 53,
      "name": "Thriller"
    },
    {
      "id": 9648,
      "name": "Mystery"
    }
  ]
}
```

**GET trending all week** — `/3/trending/all/week` (status 200)

```
{
  "page": 1,
  "results": [
    {
      "id": 101,
      "title": "The Quiet Orbit",
      "original_title": "The Quiet Orbit",
      "overview": "A marooned engineer races to repair a failing station before its orbit decays.",
      "release_date": "2024-03-15",
      "vote_average": 7.8,
      "vote_count": 2140,
      "genre_ids": [
        878,
        53
      ],
      "popularity": 142.6,
      "original_language": "en",
      "media_type": "movie",
      "adult": false
    },
    {
      "id": 110,
      "title": "The Cartographer",
      "original_title": "The Cartographer",
      "o
... (truncated)
```

</details>

### trello-api (port 8030) — server: started

| Result | Method | Path | Status | Endpoint |
|--------|--------|------|--------|----------|
| PASS | GET | /health | 200 | health |
| PASS | GET | /1/members/me/boards | 200 | list my boards |
| PASS | GET | /1/boards/60b1000000000000000000b1 | 200 | get board |
| PASS | GET | /1/boards/60b1000000000000000000b1/lists | 200 | list board lists |
| PASS | GET | /1/lists/61c1000000000000000000c1/cards | 200 | list cards in list |
| PASS | POST | /1/cards?idList=61c1000000000000000000c1&name=Investigate%20webhook%20retries&desc=Add%20exponential%20backoff | 200 | create card |
| PASS | PUT | /1/cards/62d1000000000000000000d4?idList=61c1000000000000000000c2 | 200 | move card to Doing |
| PASS | DELETE | /1/cards/62d1000000000000000000da | 200 | delete card |
| PASS | GET | /1/cards/62d1000000000000000000d2/checklists | 200 | list card checklists |
| PASS | POST | /1/checklists?idCard=62d1000000000000000000d4&name=Spike%20tasks | 200 | create checklist |

<details><summary>responses</summary>

**GET health** — `/health` (status 200)

```
{
  "status": "ok"
}
```

**GET list my boards** — `/1/members/me/boards` (status 200)

```
[
  {
    "id": "60b1000000000000000000b1",
    "name": "Product Roadmap",
    "desc": "Q2 product delivery board",
    "closed": false,
    "idOrganization": "org-orbit-labs",
    "url": "https://trello.com/b/abc12345/product-roadmap",
    "idMembers": [
      "5f1a000000000000000000a1",
      "5f1a000000000000000000a2",
      "5f1a000000000000000000a3"
    ]
  },
  {
    "id": "60b1000000000000000000b2",
    "name": "Marketing Campaigns",
    "desc": "Campaign planning and execution",
    "closed": false,
    "idOrganization": "org-orbit-labs",
    "url": "https://trello.com/b/def67890/marke
```

**GET get board** — `/1/boards/60b1000000000000000000b1` (status 200)

```
{
  "id": "60b1000000000000000000b1",
  "name": "Product Roadmap",
  "desc": "Q2 product delivery board",
  "closed": false,
  "idOrganization": "org-orbit-labs",
  "url": "https://trello.com/b/abc12345/product-roadmap",
  "idMembers": [
    "5f1a000000000000000000a1",
    "5f1a000000000000000000a2",
    "5f1a000000000000000000a3"
  ]
}
```

**GET list board lists** — `/1/boards/60b1000000000000000000b1/lists` (status 200)

```
[
  {
    "id": "61c1000000000000000000c1",
    "name": "To Do",
    "idBoard": "60b1000000000000000000b1",
    "pos": 16384.0,
    "closed": false
  },
  {
    "id": "61c1000000000000000000c2",
    "name": "Doing",
    "idBoard": "60b1000000000000000000b1",
    "pos": 32768.0,
    "closed": false
  },
  {
    "id": "61c1000000000000000000c3",
    "name": "Done",
    "idBoard": "60b1000000000000000000b1",
    "pos": 49152.0,
    "closed": false
  }
]
```

**GET list cards in list** — `/1/lists/61c1000000000000000000c1/cards` (status 200)

```
[
  {
    "id": "62d1000000000000000000d4",
    "name": "Mobile offline mode",
    "desc": "Spike offline sync for mobile app",
    "idBoard": "60b1000000000000000000b1",
    "idList": "61c1000000000000000000c1",
    "pos": 16384.0,
    "due": null,
    "closed": false,
    "idMembers": [
      "5f1a000000000000000000a3"
    ],
    "labels": [
      {
        "name": "mobile"
      }
    ]
  },
  {
    "id": "62d1000000000000000000d5",
    "name": "Onboarding revamp",
    "desc": "Redesign first-run onboarding flow",
    "idBoard": "60b1000000000000000000b1",
    "idList": "61c1000000000000000
... (truncated)
```

**POST create card** — `/1/cards?idList=61c1000000000000000000c1&name=Investigate%20webhook%20retries&desc=Add%20exponential%20backoff` (status 200)

```
{
  "id": "336d5185aab23846439d8560",
  "name": "Investigate webhook retries",
  "desc": "Add exponential backoff",
  "idBoard": "60b1000000000000000000b1",
  "idList": "61c1000000000000000000c1",
  "pos": 65536.0,
  "due": null,
  "closed": false,
  "idMembers": [],
  "labels": []
}
```

**PUT move card to Doing** — `/1/cards/62d1000000000000000000d4?idList=61c1000000000000000000c2` (status 200)

```
{
  "id": "62d1000000000000000000d4",
  "name": "Mobile offline mode",
  "desc": "Spike offline sync for mobile app",
  "idBoard": "60b1000000000000000000b1",
  "idList": "61c1000000000000000000c1",
  "pos": 16384.0,
  "due": null,
  "closed": false,
  "idMembers": [
    "5f1a000000000000000000a3"
  ],
  "labels": [
    {
      "name": "mobile"
    }
  ]
}
```

**DELETE delete card** — `/1/cards/62d1000000000000000000da` (status 200)

```
{
  "_value": null,
  "deleted": true,
  "id": "62d1000000000000000000da"
}
```

**GET list card checklists** — `/1/cards/62d1000000000000000000d2/checklists` (status 200)

```
[
  {
    "id": "63e1000000000000000000e1",
    "name": "Design doc tasks",
    "idCard": "62d1000000000000000000d2",
    "idBoard": "60b1000000000000000000b1",
    "checkItems": [
      {
        "id": "ci00e100",
        "name": "Threat model",
        "state": "incomplete",
        "pos": 16384
      },
      {
        "id": "ci00e101",
        "name": "API surface",
        "state": "complete",
        "pos": 32768
      },
      {
        "id": "ci00e102",
        "name": "Migration path",
        "state": "incomplete",
        "pos": 49152
      }
    ]
  }
]
```

**POST create checklist** — `/1/checklists?idCard=62d1000000000000000000d4&name=Spike%20tasks` (status 200)

```
{
  "id": "06e41989f407cb8f98a31f36",
  "name": "Spike tasks",
  "idCard": "62d1000000000000000000d4",
  "idBoard": "60b1000000000000000000b1",
  "checkItems": []
}
```

</details>

### twilio-api (port 8026) — server: started

| Result | Method | Path | Status | Endpoint |
|--------|--------|------|--------|----------|
| PASS | GET | /health | 200 | health |
| PASS | GET | /2010-04-01/Accounts/ACXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX/Messages.json?PageSize=10 | 200 | list messages |
| PASS | GET | /2010-04-01/Accounts/ACXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX/Messages.json?Status=received | 200 | list inbound messages |
| PASS | GET | /2010-04-01/Accounts/ACXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX/Messages/SM0a1b2c3d4e5f60718293a4b5c6d7e801.json | 200 | get message |
| PASS | POST | /2010-04-01/Accounts/ACXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX/Messages.json?To=%2B14155557777&From=%2B14155550123&Body=Hello%20from%20the%20mock | 201 | create message |
| PASS | GET | /2010-04-01/Accounts/ACXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX/Calls.json | 200 | list calls |
| PASS | POST | /2010-04-01/Accounts/ACXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX/Calls.json?To=%2B14155557777&From=%2B14155550123 | 201 | create call |
| PASS | GET | /2010-04-01/Accounts/ACXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX/IncomingPhoneNumbers.json | 200 | list incoming phone numbers |
| PASS | GET | /v1/PhoneNumbers/+14155550123 | 200 | lookup phone number |

<details><summary>responses</summary>

**GET health** — `/health` (status 200)

```
{
  "status": "ok"
}
```

**GET list messages** — `/2010-04-01/Accounts/ACXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX/Messages.json?PageSize=10` (status 200)

```
{
  "messages": [
    {
      "sid": "SM0a1b2c3d4e5f60718293a4b5c6d7e808",
      "account_sid": "ACXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
      "from": "+14155550123",
      "to": "+14155557200",
      "body": "Reminder: payment of $49 due tomorrow.",
      "status": "queued",
      "direction": "outbound-api",
      "num_segments": "1",
      "price": null,
      "price_unit": "USD",
      "error_code": null,
      "date_sent": null,
      "date_created": "2026-05-27T08:00:00Z",
      "uri": "/2010-04-01/Accounts/ACXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX/Messages/SM0a1b2c3d4e5f60718293a4b5c6d7e808.json"
... (truncated)
```

**GET list inbound messages** — `/2010-04-01/Accounts/ACXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX/Messages.json?Status=received` (status 200)

```
{
  "messages": [
    {
      "sid": "SM0a1b2c3d4e5f60718293a4b5c6d7e809",
      "account_sid": "ACXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
      "from": "+14155557011",
      "to": "+14155550123",
      "body": "YES confirm",
      "status": "received",
      "direction": "inbound",
      "num_segments": "1",
      "price": "-0.0075",
      "price_unit": "USD",
      "error_code": null,
      "date_sent": "2026-05-26T12:20:00Z",
      "date_created": "2026-05-26T12:20:00Z",
      "uri": "/2010-04-01/Accounts/ACXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX/Messages/SM0a1b2c3d4e5f60718293a4b5c6d7e809.json"
    },
... (truncated)
```

**GET get message** — `/2010-04-01/Accounts/ACXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX/Messages/SM0a1b2c3d4e5f60718293a4b5c6d7e801.json` (status 200)

```
{
  "sid": "SM0a1b2c3d4e5f60718293a4b5c6d7e801",
  "account_sid": "ACXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
  "from": "+14155550123",
  "to": "+14155557001",
  "body": "Your Orbit Labs verification code is 482910.",
  "status": "delivered",
  "direction": "outbound-api",
  "num_segments": "1",
  "price": "-0.0075",
  "price_unit": "USD",
  "error_code": null,
  "date_sent": "2026-05-26T09:01:12Z",
  "date_created": "2026-05-26T09:01:10Z",
  "uri": "/2010-04-01/Accounts/ACXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX/Messages/SM0a1b2c3d4e5f60718293a4b5c6d7e801.json"
}
```

**POST create message** — `/2010-04-01/Accounts/ACXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX/Messages.json?To=%2B14155557777&From=%2B14155550123&Body=Hello%20from%20the%20mock` (status 201)

```
{
  "sid": "SMe6dea88a4ead4093b9bdb8c30e5790fb",
  "account_sid": "ACXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
  "from": "+14155550123",
  "to": "+14155557777",
  "body": "Hello from the mock",
  "status": "queued",
  "direction": "outbound-api",
  "num_segments": "1",
  "price": null,
  "price_unit": "USD",
  "error_code": null,
  "date_sent": null,
  "date_created": "2026-06-17T10:31:44Z",
  "uri": "/2010-04-01/Accounts/ACXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX/Messages/SMe6dea88a4ead4093b9bdb8c30e5790fb.json"
}
```

**GET list calls** — `/2010-04-01/Accounts/ACXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX/Calls.json` (status 200)

```
{
  "calls": [
    {
      "sid": "CA0a1b2c3d4e5f60718293a4b5c6d7e806",
      "account_sid": "ACXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
      "from": "+14155557011",
      "to": "+14155550123",
      "status": "in-progress",
      "direction": "inbound",
      "duration": "0",
      "price": null,
      "price_unit": "USD",
      "answered_by": null,
      "start_time": "2026-05-27T08:30:00Z",
      "end_time": null,
      "date_created": "2026-05-27T08:29:58Z",
      "uri": "/2010-04-01/Accounts/ACXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX/Calls/CA0a1b2c3d4e5f60718293a4b5c6d7e806.json"
    },
    {
      "s
... (truncated)
```

**POST create call** — `/2010-04-01/Accounts/ACXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX/Calls.json?To=%2B14155557777&From=%2B14155550123` (status 201)

```
{
  "sid": "CA9181f68098d24ae7b660ea90862f7a24",
  "account_sid": "ACXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
  "from": "+14155550123",
  "to": "+14155557777",
  "status": "queued",
  "direction": "outbound-api",
  "duration": "0",
  "price": null,
  "price_unit": "USD",
  "answered_by": null,
  "start_time": null,
  "end_time": null,
  "date_created": "2026-06-17T10:31:44Z",
  "uri": "/2010-04-01/Accounts/ACXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX/Calls/CA9181f68098d24ae7b660ea90862f7a24.json"
}
```

**GET list incoming phone numbers** — `/2010-04-01/Accounts/ACXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX/IncomingPhoneNumbers.json` (status 200)

```
{
  "incoming_phone_numbers": [
    {
      "sid": "PNa1b2c3d4e5f60718293a4b5c6d7e8f90",
      "account_sid": "ACXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
      "phone_number": "+14155550123",
      "friendly_name": "Orbit Support Line",
      "iso_country": "US",
      "capabilities": {
        "sms": true,
        "voice": true,
        "mms": true,
        "fax": false
      },
      "date_created": "2025-09-02T09:00:00Z"
    },
    {
      "sid": "PNb2c3d4e5f60718293a4b5c6d7e8f90a1",
      "account_sid": "ACXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
      "phone_number": "+14155550199",
      "friendly_n
... (truncated)
```

**GET lookup phone number** — `/v1/PhoneNumbers/+14155550123` (status 200)

```
{
  "phone_number": "+14155550123",
  "national_format": "+14155550123",
  "country_code": "US",
  "valid": true,
  "caller_name": "Orbit Support Line",
  "url": "/v1/PhoneNumbers/+14155550123"
}
```

</details>

### twitch-api (port 8064) — server: started

| Result | Method | Path | Status | Endpoint |
|--------|--------|------|--------|----------|
| PASS | GET | /health | 200 | health |
| PASS | GET | /helix/users?login=pixelpaladin | 200 | get users |
| PASS | GET | /helix/streams | 200 | get streams (live) |
| PASS | GET | /helix/streams?user_login=sprintqueen | 200 | get streams by login |
| PASS | GET | /helix/channels?broadcaster_id=40001 | 200 | get channel |
| PASS | GET | /helix/channels/followers?broadcaster_id=40003 | 200 | get channel followers |
| PASS | GET | /helix/games/top?first=5 | 200 | get top games |
| PASS | GET | /helix/games?name=Elden Ring | 200 | get game by name |
| PASS | GET | /helix/clips?broadcaster_id=40001 | 200 | get clips by broadcaster |

<details><summary>responses</summary>

**GET health** — `/health` (status 200)

```
{
  "status": "ok"
}
```

**GET get users** — `/helix/users?login=pixelpaladin` (status 200)

```
{
  "data": [
    {
      "id": "40001",
      "login": "pixelpaladin",
      "display_name": "PixelPaladin",
      "type": "",
      "broadcaster_type": "partner",
      "description": "Variety RPG streamer and speedrunner.",
      "view_count": 4210000,
      "created_at": "2016-02-10T18:00:00Z",
      "profile_image_url": "https://static.example.com/pixelpaladin.png"
    }
  ]
}
```

**GET get streams (live)** — `/helix/streams` (status 200)

```
{
  "data": [
    {
      "id": "80001",
      "user_id": "40001",
      "user_login": "pixelpaladin",
      "user_name": "PixelPaladin",
      "game_id": "30003",
      "game_name": "Elden Ring",
      "type": "live",
      "title": "Blind Elden Ring run - no spoilers please",
      "viewer_count": 18400,
      "started_at": "2026-05-27T14:00:00Z",
      "language": "en",
      "is_live": true
    },
    {
      "id": "80002",
      "user_id": "40003",
      "user_login": "sprintqueen",
      "user_name": "SprintQueen",
      "game_id": "30005",
      "game_name": "Speedrunning",
      "type"
... (truncated)
```

**GET get streams by login** — `/helix/streams?user_login=sprintqueen` (status 200)

```
{
  "data": [
    {
      "id": "80002",
      "user_id": "40003",
      "user_login": "sprintqueen",
      "user_name": "SprintQueen",
      "game_id": "30005",
      "game_name": "Speedrunning",
      "type": "live",
      "title": "WR attempts all morning",
      "viewer_count": 9200,
      "started_at": "2026-05-27T13:30:00Z",
      "language": "en",
      "is_live": true
    }
  ]
}
```

**GET get channel** — `/helix/channels?broadcaster_id=40001` (status 200)

```
{
  "data": [
    {
      "broadcaster_id": "40001",
      "broadcaster_login": "pixelpaladin",
      "broadcaster_name": "PixelPaladin",
      "game_id": "30003",
      "game_name": "Elden Ring",
      "title": "Blind Elden Ring run - no spoilers please",
      "broadcaster_language": "en",
      "tags": [
        "RPG",
        "Blind",
        "English"
      ],
      "follower_count": 512000
    }
  ]
}
```

**GET get channel followers** — `/helix/channels/followers?broadcaster_id=40003` (status 200)

```
{
  "data": [],
  "total": 890000
}
```

**GET get top games** — `/helix/games/top?first=5` (status 200)

```
{
  "data": [
    {
      "id": "30001",
      "name": "Just Chatting",
      "box_art_url": "https://static.example.com/box/justchatting.jpg",
      "rank": 1,
      "viewer_count": 420000
    },
    {
      "id": "30002",
      "name": "Software and Game Development",
      "box_art_url": "https://static.example.com/box/gamedev.jpg",
      "rank": 2,
      "viewer_count": 38000
    },
    {
      "id": "30003",
      "name": "Elden Ring",
      "box_art_url": "https://static.example.com/box/eldenring.jpg",
      "rank": 3,
      "viewer_count": 156000
    },
    {
      "id": "30004",
      
... (truncated)
```

**GET get game by name** — `/helix/games?name=Elden Ring` (status 200)

```
{
  "data": [
    {
      "id": "30003",
      "name": "Elden Ring",
      "box_art_url": "https://static.example.com/box/eldenring.jpg",
      "rank": 3,
      "viewer_count": 156000
    }
  ]
}
```

**GET get clips by broadcaster** — `/helix/clips?broadcaster_id=40001` (status 200)

```
{
  "data": [
    {
      "id": "ClipAlpha01",
      "broadcaster_id": "40001",
      "broadcaster_name": "PixelPaladin",
      "creator_id": "40004",
      "creator_name": "TacticalTurtle",
      "game_id": "30003",
      "title": "Insane last-second parry",
      "view_count": 48200,
      "duration": 28.5,
      "created_at": "2026-05-25T19:12:00Z",
      "url": "https://clips.example.com/ClipAlpha01"
    },
    {
      "id": "ClipDelta04",
      "broadcaster_id": "40001",
      "broadcaster_name": "PixelPaladin",
      "creator_id": "40003",
      "creator_name": "SprintQueen",
      "game
... (truncated)
```

</details>

### twitter-api (port 8061) — server: started

| Result | Method | Path | Status | Endpoint |
|--------|--------|------|--------|----------|
| PASS | GET | /health | 200 | health |
| PASS | GET | /2/users/me | 200 | get me |
| PASS | GET | /2/users/2002 | 200 | get user |
| PASS | GET | /2/users/by/username/orbit_labs | 200 | get user by username |
| PASS | GET | /2/users/2001/tweets?max_results=5 | 200 | get user tweets |
| PASS | GET | /2/users/2001/followers | 200 | get followers |
| PASS | GET | /2/tweets?max_results=5 | 200 | list tweets |
| PASS | GET | /2/tweets/3002 | 200 | get tweet |
| PASS | GET | /2/tweets/search/recent?query=SLO | 200 | search recent |
| PASS | POST | /2/tweets | 201 | create tweet |
| PASS | DELETE | /2/tweets/3008 | 200 | delete tweet |
| PASS | POST | /2/users/2001/likes | 200 | like tweet |
| PASS | POST | /2/users/2001/retweets | 200 | retweet |

<details><summary>responses</summary>

**GET health** — `/health` (status 200)

```
{
  "status": "ok"
}
```

**GET get me** — `/2/users/me` (status 200)

```
{
  "data": {
    "id": "2001",
    "username": "maya_dev",
    "name": "Maya Chen",
    "description": "Backend engineer. Distributed systems and coffee.",
    "verified": true,
    "protected": false,
    "location": "Seattle WA",
    "profile_image_url": "https://pbs.example.com/maya.png",
    "created_at": "2018-03-12T09:00:00.000Z",
    "public_metrics": {
      "followers_count": 18432,
      "following_count": 312,
      "tweet_count": 1840
    }
  }
}
```

**GET get user** — `/2/users/2002` (status 200)

```
{
  "data": {
    "id": "2002",
    "username": "orbit_labs",
    "name": "Orbit Labs",
    "description": "Building developer tooling for the modern stack.",
    "verified": true,
    "protected": false,
    "location": "Remote",
    "profile_image_url": "https://pbs.example.com/orbit.png",
    "created_at": "2019-06-01T10:00:00.000Z",
    "public_metrics": {
      "followers_count": 54210,
      "following_count": 128,
      "tweet_count": 920
    }
  }
}
```

**GET get user by username** — `/2/users/by/username/orbit_labs` (status 200)

```
{
  "data": {
    "id": "2002",
    "username": "orbit_labs",
    "name": "Orbit Labs",
    "description": "Building developer tooling for the modern stack.",
    "verified": true,
    "protected": false,
    "location": "Remote",
    "profile_image_url": "https://pbs.example.com/orbit.png",
    "created_at": "2019-06-01T10:00:00.000Z",
    "public_metrics": {
      "followers_count": 54210,
      "following_count": 128,
      "tweet_count": 920
    }
  }
}
```

**GET get user tweets** — `/2/users/2001/tweets?max_results=5` (status 200)

```
{
  "data": [
    {
      "id": "3005",
      "author_id": "2001",
      "text": "Hot take: most observability dashboards measure activity not health. Track SLOs instead.",
      "created_at": "2026-05-23T08:00:00.000Z",
      "lang": "en",
      "reply_to_tweet_id": null,
      "public_metrics": {
        "like_count": 734,
        "retweet_count": 182,
        "reply_count": 67,
        "quote_count": 19
      }
    },
    {
      "id": "3001",
      "author_id": "2001",
      "text": "Shipped a 40% latency cut on our session store today. Turns out the bottleneck was a missing index. Classic
... (truncated)
```

**GET get followers** — `/2/users/2001/followers` (status 200)

```
{
  "data": [
    {
      "id": "2002",
      "username": "orbit_labs",
      "name": "Orbit Labs",
      "description": "Building developer tooling for the modern stack.",
      "verified": true,
      "protected": false,
      "location": "Remote",
      "profile_image_url": "https://pbs.example.com/orbit.png",
      "created_at": "2019-06-01T10:00:00.000Z",
      "public_metrics": {
        "followers_count": 54210,
        "following_count": 128,
        "tweet_count": 920
      }
    },
    {
      "id": "2003",
      "username": "jonas_p",
      "name": "Jonas Pereira",
      "descriptio
... (truncated)
```

**GET list tweets** — `/2/tweets?max_results=5` (status 200)

```
{
  "data": [
    {
      "id": "3010",
      "author_id": "2004",
      "text": "Finally migrated our design tokens to a single source of truth. No more drift between Figma and code.",
      "created_at": "2026-05-25T10:05:00.000Z",
      "lang": "en",
      "reply_to_tweet_id": null,
      "public_metrics": {
        "like_count": 302,
        "retweet_count": 58,
        "reply_count": 22,
        "quote_count": 7
      }
    },
    {
      "id": "3009",
      "author_id": "2002",
      "text": "We are hiring two senior backend engineers. Remote friendly. Apply via the careers page.",
     
... (truncated)
```

**GET get tweet** — `/2/tweets/3002` (status 200)

```
{
  "data": {
    "id": "3002",
    "author_id": "2002",
    "text": "Orbit CLI 2.0 is out. Faster cold starts and a brand new plugin system. Changelog in the thread.",
    "created_at": "2026-05-21T17:30:00.000Z",
    "lang": "en",
    "reply_to_tweet_id": null,
    "public_metrics": {
      "like_count": 1820,
      "retweet_count": 640,
      "reply_count": 140,
      "quote_count": 72
    }
  }
}
```

**GET search recent** — `/2/tweets/search/recent?query=SLO` (status 200)

```
{
  "data": [
    {
      "id": "3007",
      "author_id": "2003",
      "text": "@maya_dev totally agree on the SLO point. We gated our last rollout on p95 and it caught a regression.",
      "created_at": "2026-05-23T08:45:00.000Z",
      "lang": "en",
      "reply_to_tweet_id": "3005",
      "public_metrics": {
        "like_count": 52,
        "retweet_count": 3,
        "reply_count": 2,
        "quote_count": 0
      }
    },
    {
      "id": "3005",
      "author_id": "2001",
      "text": "Hot take: most observability dashboards measure activity not health. Track SLOs instead.",
     
... (truncated)
```

**POST create tweet** — `/2/tweets` (status 201)

```
{
  "data": {
    "id": "287409722031627548",
    "author_id": "2001",
    "text": "Just deployed the new plugin API. No downtime.",
    "created_at": "2026-06-17T10:31:45.000Z",
    "lang": "en",
    "reply_to_tweet_id": null,
    "public_metrics": {
      "like_count": 0,
      "retweet_count": 0,
      "reply_count": 0,
      "quote_count": 0
    }
  }
}
```

**DELETE delete tweet** — `/2/tweets/3008` (status 200)

```
{
  "data": {
    "deleted": true
  }
}
```

**POST like tweet** — `/2/users/2001/likes` (status 200)

```
{
  "data": {
    "liked": true
  }
}
```

**POST retweet** — `/2/users/2001/retweets` (status 200)

```
{
  "data": {
    "retweeted": true
  }
}
```

</details>

### typeform-api (port 8055) — server: started

| Result | Method | Path | Status | Endpoint |
|--------|--------|------|--------|----------|
| PASS | GET | /health | 200 | health |
| PASS | GET | /forms | 200 | list forms |
| PASS | POST | /forms | 201 | create form |
| PASS | GET | /forms/frm-csat-01 | 200 | get form |
| PASS | PUT | /forms/frm-csat-01 | 200 | update form |
| PASS | DELETE | /forms/frm-event-03 | 200 | delete form |
| PASS | GET | /forms/frm-csat-01/responses | 200 | list responses |
| PASS | GET | /forms/frm-csat-01/insights/summary | 200 | insights summary |

<details><summary>responses</summary>

**GET health** — `/health` (status 200)

```
{
  "status": "ok"
}
```

**GET list forms** — `/forms` (status 200)

```
{
  "total_items": 3,
  "page_count": 1,
  "items": [
    {
      "id": "frm-csat-01",
      "title": "Customer Satisfaction Survey",
      "last_updated_at": "2026-05-20T14:00:00Z",
      "_links": {
        "display": "https://orbitlabs.typeform.com/to/frm-csat-01"
      }
    },
    {
      "id": "frm-onboard-02",
      "title": "Product Onboarding Feedback",
      "last_updated_at": "2026-05-18T10:15:00Z",
      "_links": {
        "display": "https://orbitlabs.typeform.com/to/frm-onboard-02"
      }
    },
    {
      "id": "frm-event-03",
      "title": "Event Registration",
      "last_
```

**POST create form** — `/forms` (status 201)

```
{
  "id": "frm-6425cca195",
  "title": "NPS Pulse",
  "language": "en",
  "workspace": {
    "href": "https://api.typeform.com/workspaces/ws-orbit-labs"
  },
  "settings": {
    "is_public": true
  },
  "fields": [],
  "_links": {
    "display": "https://orbitlabs.typeform.com/to/frm-6425cca195"
  },
  "created_at": "2026-06-17T10:31:45Z",
  "last_updated_at": "2026-06-17T10:31:45Z"
}
```

**GET get form** — `/forms/frm-csat-01` (status 200)

```
{
  "id": "frm-csat-01",
  "title": "Customer Satisfaction Survey",
  "language": "en",
  "workspace": {
    "href": "https://api.typeform.com/workspaces/ws-orbit-labs"
  },
  "settings": {
    "is_public": true
  },
  "fields": [
    {
      "id": "fld-csat-name",
      "title": "What is your name?",
      "ref": "name",
      "type": "short_text",
      "required": true
    },
    {
      "id": "fld-csat-rating",
      "title": "How would you rate our service?",
      "ref": "service_rating",
      "type": "rating",
      "required": true
    },
    {
      "id": "fld-csat-recommend",
      
... (truncated)
```

**PUT update form** — `/forms/frm-csat-01` (status 200)

```
{
  "id": "frm-csat-01",
  "title": "Customer Satisfaction Survey (Q2)",
  "language": "en",
  "workspace": {
    "href": "https://api.typeform.com/workspaces/ws-orbit-labs"
  },
  "settings": {
    "is_public": true
  },
  "fields": [
    {
      "id": "fld-csat-name",
      "title": "What is your name?",
      "ref": "name",
      "type": "short_text",
      "required": true
    },
    {
      "id": "fld-csat-rating",
      "title": "How would you rate our service?",
      "ref": "service_rating",
      "type": "rating",
      "required": true
    },
    {
      "id": "fld-csat-recommend",
 
... (truncated)
```

**DELETE delete form** — `/forms/frm-event-03` (status 200)

```
{
  "deleted": true,
  "id": "frm-event-03"
}
```

**GET list responses** — `/forms/frm-csat-01/responses` (status 200)

```
{
  "total_items": 3,
  "page_count": 1,
  "items": [
    {
      "response_id": "resp-csat-1",
      "landed_at": "2026-05-15T10:18:00Z",
      "submitted_at": "2026-05-15T10:20:00Z",
      "answers": [
        {
          "field": {
            "id": "fld-csat-name",
            "type": "short_text",
            "ref": "name"
          },
          "type": "short_text",
          "text": "Maria Chen"
        },
        {
          "field": {
            "id": "fld-csat-rating",
            "type": "rating",
            "ref": "service_rating"
          },
          "type": "rating",
        
... (truncated)
```

**GET insights summary** — `/forms/frm-csat-01/insights/summary` (status 200)

```
{
  "form": {
    "id": "frm-csat-01",
    "title": "Customer Satisfaction Survey"
  },
  "total_responses": 3,
  "completed_responses": 3,
  "completion_rate": 1.0,
  "fields": [
    {
      "field": {
        "id": "fld-csat-name",
        "title": "What is your name?",
        "type": "short_text"
      },
      "answer_count": 3
    },
    {
      "field": {
        "id": "fld-csat-rating",
        "title": "How would you rate our service?",
        "type": "rating"
      },
      "answer_count": 3,
      "average": 4.0
    },
    {
      "field": {
        "id": "fld-csat-recommend",
    
... (truncated)
```

</details>

### uber-api (port 8036) — server: started

| Result | Method | Path | Status | Endpoint |
|--------|--------|------|--------|----------|
| PASS | GET | /health | 200 | health |
| PASS | GET | /v1.2/products?latitude=37.7752&longitude=-122.4180 | 200 | list products |
| PASS | GET | /v1.2/products/uberx | 200 | get product |
| PASS | GET | /v1.2/estimates/price?start_latitude=37.7752&start_longitude=-122.4180&end_latitude=37.7956&end_longitude=-122.3934 | 200 | price estimates |
| PASS | GET | /v1.2/estimates/time?start_latitude=37.7752&start_longitude=-122.4180 | 200 | time estimates |
| PASS | POST | /v1.2/requests | 201 | request ride |
| PASS | GET | /v1.2/requests/req-7f0011aa | 200 | get request |
| WARN | DELETE | /v1.2/requests/req-7f0011aa | 400 | cancel request (400 expected - already-completed ride) |
| PASS | GET | /v1.2/history?limit=10 | 200 | ride history |
| PASS | GET | /v1.2/me | 200 | rider profile |

<details><summary>responses</summary>

**GET health** — `/health` (status 200)

```
{
  "status": "ok"
}
```

**GET list products** — `/v1.2/products?latitude=37.7752&longitude=-122.4180` (status 200)

```
{
  "products": [
    {
      "product_id": "uberx",
      "display_name": "UberX",
      "description": "Affordable everyday rides",
      "capacity": 4,
      "base_fare": 2.55,
      "cost_per_mile": 1.75,
      "cost_per_minute": 0.35,
      "booking_fee": 2.3,
      "minimum_fare": 7.65,
      "image_url": "https://img.example.com/uberx.png",
      "shared": false
    },
    {
      "product_id": "uberxl",
      "display_name": "UberXL",
      "description": "Affordable rides for groups up to 6",
      "capacity": 6,
      "base_fare": 3.85,
      "cost_per_mile": 2.85,
      "cost_per_mi
... (truncated)
```

**GET get product** — `/v1.2/products/uberx` (status 200)

```
{
  "product_id": "uberx",
  "display_name": "UberX",
  "description": "Affordable everyday rides",
  "capacity": 4,
  "base_fare": 2.55,
  "cost_per_mile": 1.75,
  "cost_per_minute": 0.35,
  "booking_fee": 2.3,
  "minimum_fare": 7.65,
  "image_url": "https://img.example.com/uberx.png",
  "shared": false
}
```

**GET price estimates** — `/v1.2/estimates/price?start_latitude=37.7752&start_longitude=-122.4180&end_latitude=37.7956&end_longitude=-122.3934` (status 200)

```
{
  "prices": [
    {
      "product_id": "uberx",
      "display_name": "UberX",
      "currency_code": "USD",
      "distance": 1.95,
      "duration": 510,
      "estimate": "$11.23-14.04",
      "low_estimate": 11.23,
      "high_estimate": 14.04,
      "surge_multiplier": 1.0
    },
    {
      "product_id": "uberxl",
      "display_name": "UberXL",
      "currency_code": "USD",
      "distance": 1.95,
      "duration": 510,
      "estimate": "$15.52-19.41",
      "low_estimate": 15.52,
      "high_estimate": 19.41,
      "surge_multiplier": 1.0
    },
    {
      "product_id": "uberblack
... (truncated)
```

**GET time estimates** — `/v1.2/estimates/time?start_latitude=37.7752&start_longitude=-122.4180` (status 200)

```
{
  "times": [
    {
      "product_id": "uberx",
      "display_name": "UberX",
      "estimate": 180
    },
    {
      "product_id": "uberxl",
      "display_name": "UberXL",
      "estimate": 300
    },
    {
      "product_id": "uberblack",
      "display_name": "Uber Black",
      "estimate": 480
    },
    {
      "product_id": "uberpool",
      "display_name": "Uber Pool",
      "estimate": 240
    }
  ]
}
```

**POST request ride** — `/v1.2/requests` (status 201)

```
{
  "request_id": "req-d1c41ef7",
  "product_id": "uberx",
  "status": "processing",
  "rider_id": "rider-marco",
  "driver_name": "Mei Tanaka",
  "vehicle": "Tesla Model 3 Black",
  "license_plate": "8EVX771",
  "start_latitude": 37.7752,
  "start_longitude": -122.418,
  "start_address": "",
  "end_latitude": 37.7956,
  "end_longitude": -122.3934,
  "end_address": "",
  "distance_miles": 1.95,
  "duration_minutes": 8.5,
  "fare": 11.23,
  "surge_multiplier": 1.0,
  "eta_minutes": 3,
  "requested_at": "2026-06-17T10:31:46Z",
  "completed_at": null
}
```

**GET get request** — `/v1.2/requests/req-7f0011aa` (status 200)

```
{
  "request_id": "req-7f0011aa",
  "product_id": "uberx",
  "status": "completed",
  "rider_id": "rider-marco",
  "driver_name": "Daniela Souza",
  "vehicle": "Toyota Camry Silver",
  "license_plate": "7XYZ221",
  "start_latitude": 37.7752,
  "start_longitude": -122.418,
  "start_address": "1455 Market St San Francisco",
  "end_latitude": 37.7956,
  "end_longitude": -122.3934,
  "end_address": "Ferry Building San Francisco",
  "distance_miles": 2.1,
  "duration_minutes": 11.0,
  "fare": 12.8,
  "surge_multiplier": 1.0,
  "requested_at": "2026-05-10T08:42:00Z",
  "completed_at": "2026-05-10T08
```

**DELETE cancel request (400 expected - already-completed ride)** — `/v1.2/requests/req-7f0011aa` (status 400)

```
{
  "error": "Request req-7f0011aa cannot be canceled (status: completed)"
}
```

**GET ride history** — `/v1.2/history?limit=10` (status 200)

```
{
  "count": 4,
  "limit": 10,
  "offset": 0,
  "history": [
    {
      "request_id": "req-cd778833",
      "product_id": "uberpool",
      "status": "completed",
      "rider_id": "rider-marco",
      "driver_name": "Aisha Khan",
      "vehicle": "Toyota Prius Blue",
      "license_plate": "9POO456",
      "start_latitude": 37.782,
      "start_longitude": -122.409,
      "start_address": "Union Square San Francisco",
      "end_latitude": 37.734,
      "end_longitude": -122.448,
      "end_address": "Mission Dolores San Francisco",
      "distance_miles": 3.3,
      "duration_minutes": 18.0
... (truncated)
```

**GET rider profile** — `/v1.2/me` (status 200)

```
{
  "rider_id": "rider-marco",
  "first_name": "Marco",
  "last_name": "Reyes",
  "email": "marco.reyes@example.com",
  "phone_number": "+14155550142",
  "rating": 4.91,
  "member_since": "2021-03-14",
  "promo_code": "RIDE5OFF",
  "payment_methods": [
    {
      "payment_method_id": "pm-visa-9921",
      "type": "card",
      "brand": "Visa",
      "last_four": "9921",
      "default": true
    },
    {
      "payment_method_id": "pm-ubercash",
      "type": "uber_cash",
      "balance": 18.5,
      "default": false
    }
  ],
  "home_address": "1455 Market St, San Francisco, CA",
  "work_ad
```

</details>

### ups-api (port 8096) — server: started

| Result | Method | Path | Status | Endpoint |
|--------|--------|------|--------|----------|
| PASS | GET | /health | 200 | health |
| PASS | POST | /api/rating/v1/Rate | 200 | rate |
| PASS | POST | /api/shipments/v1/ship | 200 | ship |
| PASS | GET | /api/track/v1/details/1Z999AA10123456784 | 200 | track |

<details><summary>responses</summary>

**GET health** — `/health` (status 200)

```
{
  "status": "ok"
}
```

**POST rate** — `/api/rating/v1/Rate` (status 200)

```
{
  "RateResponse": {
    "Response": {
      "ResponseStatus": {
        "Code": "1",
        "Description": "Success"
      }
    },
    "RatedShipment": [
      {
        "Service": {
          "Code": "03",
          "Description": "UPS Ground"
        },
        "TotalCharges": {
          "CurrencyCode": "USD",
          "MonetaryValue": "16.20"
        },
        "GuaranteedDelivery": {
          "BusinessDaysInTransit": "5",
          "DeliveryByTime": "2026-05-30"
        }
      },
      {
        "Service": {
          "Code": "02",
          "Description": "UPS 2nd Day Air"
       
... (truncated)
```

**POST ship** — `/api/shipments/v1/ship` (status 200)

```
{
  "ShipmentResponse": {
    "Response": {
      "ResponseStatus": {
        "Code": "1",
        "Description": "Success"
      }
    },
    "ShipmentResults": {
      "ShipmentIdentificationNumber": "1Z999AA1013456839",
      "ShipmentCharges": {
        "TotalCharges": {
          "CurrencyCode": "USD",
          "MonetaryValue": "16.20"
        }
      },
      "PackageResults": [
        {
          "TrackingNumber": "1Z999AA1013456839",
          "ShippingLabel": {
            "ImageFormat": {
              "Code": "GIF"
            },
            "GraphicImage": "https://ups.example/la
```

**GET track** — `/api/track/v1/details/1Z999AA10123456784` (status 200)

```
{
  "trackResponse": {
    "shipment": [
      {
        "package": [
          {
            "trackingNumber": "1Z999AA10123456784",
            "currentStatus": {
              "type": "D",
              "code": "011",
              "description": "Delivered"
            },
            "service": {
              "description": "UPS Ground"
            },
            "deliveryDate": [
              {
                "type": "SDD",
                "date": "2026-05-25"
              }
            ],
            "activity": [
              {
                "status": {
                  "type": 
```

</details>

### vimeo-api (port 8099) — server: started

| Result | Method | Path | Status | Endpoint |
|--------|--------|------|--------|----------|
| PASS | GET | /health | 200 | health |
| PASS | GET | /me | 200 | me |
| PASS | GET | /me/videos?page=1&per_page=25 | 200 | my videos |
| PASS | GET | /videos/901000103 | 200 | video by id |
| WARN | GET | /videos/999999999 | 404 | video not found |
| PASS | GET | /users/12000002 | 200 | user by id |
| PASS | GET | /users/12000004/videos?page=1&per_page=25 | 200 | user videos |

<details><summary>responses</summary>

**GET health** — `/health` (status 200)

```
{
  "status": "ok"
}
```

**GET me** — `/me` (status 200)

```
{
  "uri": "/users/12000001",
  "name": "Aiko Tanaka",
  "link": "https://vimeo.com/aikotanaka",
  "location": "Tokyo JP",
  "bio": "Documentary filmmaker and editor.",
  "account": "pro",
  "created_time": "2026-01-12T09:15:00+00:00",
  "websites": [
    {
      "uri": "",
      "link": "https://aiko.example.com"
    }
  ],
  "metadata": {
    "connections": {
      "videos": {
        "uri": "/users/12000001/videos",
        "total": 2
      }
    }
  }
}
```

**GET my videos** — `/me/videos?page=1&per_page=25` (status 200)

```
{
  "total": 2,
  "page": 1,
  "per_page": 25,
  "paging": {
    "next": null,
    "previous": null,
    "first": "?page=1",
    "last": "?page=1"
  },
  "data": [
    {
      "uri": "/videos/901000102",
      "name": "Editing Workflow 2026",
      "description": "My current Resolve color pipeline.",
      "link": "https://vimeo.com/901000102",
      "duration": 1284,
      "width": 1920,
      "height": 1080,
      "created_time": "2026-05-09T13:00:00+00:00",
      "modified_time": "2026-05-09T14:22:00+00:00",
      "privacy": {
        "view": "anybody"
      },
      "status": "available",

... (truncated)
```

**GET video by id** — `/videos/901000103` (status 200)

```
{
  "uri": "/videos/901000103",
  "name": "Neon Streets",
  "description": "Music video shot entirely at night.",
  "link": "https://vimeo.com/901000103",
  "duration": 221,
  "width": 3840,
  "height": 2160,
  "created_time": "2026-05-04T20:15:00+00:00",
  "modified_time": "2026-05-05T01:40:00+00:00",
  "privacy": {
    "view": "anybody"
  },
  "status": "available",
  "stats": {
    "plays": 52310
  },
  "metadata": {
    "connections": {
      "likes": {
        "total": 4120
      }
    }
  },
  "user": {
    "uri": "/users/12000002",
    "name": "Marcus Reed",
    "link": "https://vimeo.c
```

**GET video not found** — `/videos/999999999` (status 404)

```
{
  "error": "The requested video could not be found.",
  "video_id": "999999999"
}
```

**GET user by id** — `/users/12000002` (status 200)

```
{
  "uri": "/users/12000002",
  "name": "Marcus Reed",
  "link": "https://vimeo.com/marcusreed",
  "location": "Brooklyn NY",
  "bio": "Music video director.",
  "account": "plus",
  "created_time": "2026-02-03T14:42:00+00:00",
  "websites": [
    {
      "uri": "",
      "link": "https://marcusreed.example.com"
    }
  ],
  "metadata": {
    "connections": {
      "videos": {
        "uri": "/users/12000002/videos",
        "total": 2
      }
    }
  }
}
```

**GET user videos** — `/users/12000004/videos?page=1&per_page=25` (status 200)

```
{
  "total": 2,
  "page": 1,
  "per_page": 25,
  "paging": {
    "next": null,
    "previous": null,
    "first": "?page=1",
    "last": "?page=1"
  },
  "data": [
    {
      "uri": "/videos/901000107",
      "name": "Color Grading Travel Footage",
      "description": "Grading workflow for warm tropical looks.",
      "link": "https://vimeo.com/901000107",
      "duration": 1020,
      "width": 1920,
      "height": 1080,
      "created_time": "2026-05-15T15:10:00+00:00",
      "modified_time": "2026-05-15T16:05:00+00:00",
      "privacy": {
        "view": "anybody"
      },
      "status":
... (truncated)
```

</details>

### webflow-api (port 8100) — server: started

| Result | Method | Path | Status | Endpoint |
|--------|--------|------|--------|----------|
| PASS | GET | /health | 200 | health |
| PASS | GET | /v2/sites | 200 | list sites |
| PASS | GET | /v2/sites/650a1f0000000000000001a1 | 200 | get site |
| PASS | GET | /v2/sites/650a1f0000000000000001a1/collections | 200 | list collections |
| PASS | GET | /v2/collections/660b2a0000000000000002b1/items?limit=100&offset=0 | 200 | list items |
| PASS | POST | /v2/collections/660b2a0000000000000002b1/items | 202 | create item |

<details><summary>responses</summary>

**GET health** — `/health` (status 200)

```
{
  "status": "ok"
}
```

**GET list sites** — `/v2/sites` (status 200)

```
{
  "sites": [
    {
      "id": "650a1f0000000000000001a1",
      "workspaceId": "ws_000001",
      "displayName": "Northwind Studio",
      "shortName": "northwind-studio",
      "previewUrl": "https://northwind-studio.webflow.io",
      "timeZone": "America/New_York",
      "createdOn": "2026-01-15T10:00:00.000Z",
      "lastPublished": "2026-05-20T14:30:00.000Z",
      "customDomains": [
        {
          "id": "c4050a1ef5b5b4d9",
          "url": "www.northwind.example.com"
        }
      ]
    },
    {
      "id": "650a1f0000000000000001a2",
      "workspaceId": "ws_000001",
      "di
... (truncated)
```

**GET get site** — `/v2/sites/650a1f0000000000000001a1` (status 200)

```
{
  "id": "650a1f0000000000000001a1",
  "workspaceId": "ws_000001",
  "displayName": "Northwind Studio",
  "shortName": "northwind-studio",
  "previewUrl": "https://northwind-studio.webflow.io",
  "timeZone": "America/New_York",
  "createdOn": "2026-01-15T10:00:00.000Z",
  "lastPublished": "2026-05-20T14:30:00.000Z",
  "customDomains": [
    {
      "id": "a3890866a510a050",
      "url": "www.northwind.example.com"
    }
  ]
}
```

**GET list collections** — `/v2/sites/650a1f0000000000000001a1/collections` (status 200)

```
{
  "collections": [
    {
      "id": "660b2a0000000000000002b1",
      "siteId": "650a1f0000000000000001a1",
      "displayName": "Blog Posts",
      "singularName": "Blog Post",
      "slug": "blog-posts",
      "createdOn": "2026-01-16T10:30:00.000Z",
      "lastUpdated": "2026-05-19T12:00:00.000Z"
    },
    {
      "id": "660b2a0000000000000002b2",
      "siteId": "650a1f0000000000000001a1",
      "displayName": "Authors",
      "singularName": "Author",
      "slug": "authors",
      "createdOn": "2026-01-16T10:35:00.000Z",
      "lastUpdated": "2026-05-10T09:00:00.000Z"
    }
  ]
}
```

**GET list items** — `/v2/collections/660b2a0000000000000002b1/items?limit=100&offset=0` (status 200)

```
{
  "items": [
    {
      "id": "770c3b0000000000000003c1",
      "cmsLocaleId": null,
      "lastPublished": null,
      "lastUpdated": "2026-05-02T09:00:00.000Z",
      "createdOn": "2026-05-02T08:00:00.000Z",
      "isArchived": false,
      "isDraft": false,
      "fieldData": {
        "name": "Shipping Faster With Edge Caching",
        "slug": "shipping-faster-with-edge-caching",
        "summary": "How we cut TTFB by 40 percent."
      }
    },
    {
      "id": "770c3b0000000000000003c2",
      "cmsLocaleId": null,
      "lastPublished": null,
      "lastUpdated": "2026-05-09T12:15:0
... (truncated)
```

**POST create item** — `/v2/collections/660b2a0000000000000002b1/items` (status 202)

```
{
  "id": "530f4bba61dfa7be687a28a5",
  "cmsLocaleId": null,
  "lastPublished": null,
  "lastUpdated": "2026-06-17T10:31:48.000Z",
  "createdOn": "2026-06-17T10:31:48.000Z",
  "isArchived": false,
  "isDraft": false,
  "fieldData": {
    "name": "Caching at the Edge, Part 2",
    "slug": "caching-at-the-edge-part-2",
    "summary": "Follow-up on edge cache invalidation."
  }
}
```

</details>

### whatsapp-api (port 8015) — server: started

| Result | Method | Path | Status | Endpoint |
|--------|--------|------|--------|----------|
| PASS | GET | /health | 200 | health |
| PASS | GET | /v17.0/business | 200 | business |
| PASS | GET | /v17.0/contacts?opted_in_only=true | 200 | list contacts opted in |
| PASS | GET | /v17.0/contacts/15551550101 | 200 | get contact |
| PASS | GET | /v17.0/message_templates?status=APPROVED | 200 | list approved templates |
| PASS | GET | /v17.0/message_templates/order_shipped | 200 | get template |
| PASS | GET | /v17.0/conversations | 200 | list conversations |
| PASS | GET | /v17.0/messages?conversation_id=conv-001 | 200 | list messages |
| PASS | POST | /v17.0/messages | 200 | send text |
| PASS | POST | /v17.0/messages | 200 | send template |
| PASS | POST | /v17.0/messages/status | 200 | mark read |

<details><summary>responses</summary>

**GET health** — `/health` (status 200)

```
{
  "status": "ok"
}
```

**GET business** — `/v17.0/business` (status 200)

```
{
  "business_account_id": "wba-orbit-labs",
  "name": "Orbit Labs Support",
  "phone_number_id": "PNI-1551550100",
  "display_phone_number": "+1 555-0100",
  "verified_name": "Orbit Labs",
  "messaging_limit_tier": "TIER_1K"
}
```

**GET list contacts opted in** — `/v17.0/contacts?opted_in_only=true` (status 200)

```
{
  "data": [
    {
      "wa_id": "15551550101",
      "profile_name": "Emily Carson",
      "phone_number": "+15551550101",
      "opted_in": true,
      "last_seen": "2026-05-26T09:00:00Z"
    },
    {
      "wa_id": "15551550102",
      "profile_name": "Daniel Reyes",
      "phone_number": "+15551550102",
      "opted_in": true,
      "last_seen": "2026-05-25T18:30:00Z"
    },
    {
      "wa_id": "15551550103",
      "profile_name": "Priya Shah",
      "phone_number": "+15551550103",
      "opted_in": true,
      "last_seen": "2026-05-22T14:15:00Z"
    },
    {
      "wa_id": "15551550105
```

**GET get contact** — `/v17.0/contacts/15551550101` (status 200)

```
{
  "wa_id": "15551550101",
  "profile_name": "Emily Carson",
  "phone_number": "+15551550101",
  "opted_in": true,
  "last_seen": "2026-05-26T09:00:00Z"
}
```

**GET list approved templates** — `/v17.0/message_templates?status=APPROVED` (status 200)

```
{
  "data": [
    {
      "name": "order_shipped",
      "language": "en_US",
      "category": "UTILITY",
      "status": "APPROVED",
      "body_text": "Hi {{1}}, your order {{2}} has shipped and will arrive by {{3}}.",
      "header_text": "Order update"
    },
    {
      "name": "appointment_reminder",
      "language": "en_US",
      "category": "UTILITY",
      "status": "APPROVED",
      "body_text": "Reminder: your appointment on {{1}} at {{2}} is confirmed.",
      "header_text": ""
    },
    {
      "name": "welcome_offer",
      "language": "en_US",
      "category": "MARKETING",

... (truncated)
```

**GET get template** — `/v17.0/message_templates/order_shipped` (status 200)

```
{
  "name": "order_shipped",
  "language": "en_US",
  "category": "UTILITY",
  "status": "APPROVED",
  "body_text": "Hi {{1}}, your order {{2}} has shipped and will arrive by {{3}}.",
  "header_text": "Order update"
}
```

**GET list conversations** — `/v17.0/conversations` (status 200)

```
{
  "data": [
    {
      "conversation_id": "conv-001",
      "wa_id": "15551550101",
      "started_at": "2026-05-26T08:55:00Z",
      "last_message_at": "2026-05-26T09:00:00Z",
      "origin": "user_initiated",
      "within_24h_window": true
    },
    {
      "conversation_id": "conv-004",
      "wa_id": "15551550105",
      "started_at": "2026-05-26T07:30:00Z",
      "last_message_at": "2026-05-26T07:45:00Z",
      "origin": "user_initiated",
      "within_24h_window": true
    },
    {
      "conversation_id": "conv-002",
      "wa_id": "15551550102",
      "started_at": "2026-05-25T18:
... (truncated)
```

**GET list messages** — `/v17.0/messages?conversation_id=conv-001` (status 200)

```
{
  "data": [
    {
      "message_id": "msg-002",
      "conversation_id": "conv-001",
      "direction": "outbound",
      "from_wa_id": "15551550100",
      "to_wa_id": "15551550101",
      "type": "template",
      "text": "",
      "template_name": "order_shipped",
      "status": "delivered",
      "sent_at": "2026-05-26T09:00:00Z"
    },
    {
      "message_id": "msg-001",
      "conversation_id": "conv-001",
      "direction": "inbound",
      "from_wa_id": "15551550101",
      "to_wa_id": "15551550100",
      "type": "text",
      "text": "Hi \u2014 my order #SF-220 still shows as pr
```

**POST send text** — `/v17.0/messages` (status 200)

```
{
  "messages": [
    {
      "id": "wamid.069A2003FFB6484594426E56",
      "message_status": "accepted"
    }
  ]
}
```

**POST send template** — `/v17.0/messages` (status 200)

```
{
  "messages": [
    {
      "id": "wamid.1D5867CBD6FC415BB87AEACC",
      "message_status": "accepted"
    }
  ]
}
```

**POST mark read** — `/v17.0/messages/status` (status 200)

```
{
  "success": true,
  "message_id": "msg-001"
}
```

</details>

### woocommerce-api (port 8085) — server: started

| Result | Method | Path | Status | Endpoint |
|--------|--------|------|--------|----------|
| PASS | GET | /health | 200 | health |
| PASS | GET | /wp-json/wc/v3/products?per_page=5&page=1 | 200 | list products |
| PASS | GET | /wp-json/wc/v3/products?search=mug | 200 | search products |
| PASS | GET | /wp-json/wc/v3/products/201 | 200 | get product |
| PASS | GET | /wp-json/wc/v3/orders?customer=301 | 200 | list orders |
| PASS | GET | /wp-json/wc/v3/orders/401 | 200 | get order |
| PASS | POST | /wp-json/wc/v3/orders | 200 | create order |
| PASS | GET | /wp-json/wc/v3/customers?email=emma | 200 | list customers |

<details><summary>responses</summary>

**GET health** — `/health` (status 200)

```
{
  "status": "ok"
}
```

**GET list products** — `/wp-json/wc/v3/products?per_page=5&page=1` (status 200)

```
[
  {
    "id": 201,
    "name": "Handcrafted Ceramic Mug",
    "slug": "handcrafted-ceramic-mug",
    "sku": "WC-MUG-201",
    "type": "simple",
    "status": "publish",
    "price": "18.00",
    "regular_price": "22.00",
    "sale_price": "18.00",
    "on_sale": true,
    "stock_quantity": 150,
    "stock_status": "instock",
    "manage_stock": true,
    "categories": [
      {
        "name": "Kitchen",
        "slug": "kitchen"
      },
      {
        "name": "Drinkware",
        "slug": "drinkware"
      }
    ],
    "description": "Stoneware mug glazed by hand",
    "date_created": "202
... (truncated)
```

**GET search products** — `/wp-json/wc/v3/products?search=mug` (status 200)

```
[
  {
    "id": 201,
    "name": "Handcrafted Ceramic Mug",
    "slug": "handcrafted-ceramic-mug",
    "sku": "WC-MUG-201",
    "type": "simple",
    "status": "publish",
    "price": "18.00",
    "regular_price": "22.00",
    "sale_price": "18.00",
    "on_sale": true,
    "stock_quantity": 150,
    "stock_status": "instock",
    "manage_stock": true,
    "categories": [
      {
        "name": "Kitchen",
        "slug": "kitchen"
      },
      {
        "name": "Drinkware",
        "slug": "drinkware"
      }
    ],
    "description": "Stoneware mug glazed by hand",
    "date_created": "202
```

**GET get product** — `/wp-json/wc/v3/products/201` (status 200)

```
{
  "id": 201,
  "name": "Handcrafted Ceramic Mug",
  "slug": "handcrafted-ceramic-mug",
  "sku": "WC-MUG-201",
  "type": "simple",
  "status": "publish",
  "price": "18.00",
  "regular_price": "22.00",
  "sale_price": "18.00",
  "on_sale": true,
  "stock_quantity": 150,
  "stock_status": "instock",
  "manage_stock": true,
  "categories": [
    {
      "name": "Kitchen",
      "slug": "kitchen"
    },
    {
      "name": "Drinkware",
      "slug": "drinkware"
    }
  ],
  "description": "Stoneware mug glazed by hand",
  "date_created": "2026-01-08T09:00:00"
}
```

**GET list orders** — `/wp-json/wc/v3/orders?customer=301` (status 200)

```
[
  {
    "id": 401,
    "number": "401",
    "customer_id": 301,
    "status": "completed",
    "currency": "USD",
    "total": "40.00",
    "subtotal": "36.00",
    "total_tax": "4.00",
    "payment_method": "stripe",
    "payment_method_title": "Credit Card (Stripe)",
    "billing": {
      "first_name": "Emma",
      "last_name": "Wright",
      "email": "emma.wright@example.com"
    },
    "date_created": "2026-04-03T10:05:00"
  },
  {
    "id": 406,
    "number": "406",
    "customer_id": 301,
    "status": "refunded",
    "currency": "USD",
    "total": "42.00",
    "subtotal": "38.18",
... (truncated)
```

**GET get order** — `/wp-json/wc/v3/orders/401` (status 200)

```
{
  "id": 401,
  "number": "401",
  "customer_id": 301,
  "status": "completed",
  "currency": "USD",
  "total": "40.00",
  "subtotal": "36.00",
  "total_tax": "4.00",
  "payment_method": "stripe",
  "payment_method_title": "Credit Card (Stripe)",
  "billing": {
    "first_name": "Emma",
    "last_name": "Wright",
    "email": "emma.wright@example.com"
  },
  "date_created": "2026-04-03T10:05:00"
}
```

**POST create order** — `/wp-json/wc/v3/orders` (status 200)

```
{
  "id": 407,
  "number": "407",
  "customer_id": 302,
  "status": "pending",
  "currency": "USD",
  "total": "75.90",
  "subtotal": "69.00",
  "total_tax": "6.90",
  "payment_method": "stripe",
  "payment_method_title": "Credit Card (Stripe)",
  "billing": {
    "first_name": "Noah",
    "last_name": "Kim",
    "email": "noah.kim@example.com"
  },
  "date_created": "2026-05-28T00:00:00"
}
```

**GET list customers** — `/wp-json/wc/v3/customers?email=emma` (status 200)

```
[
  {
    "id": 301,
    "first_name": "Emma",
    "last_name": "Wright",
    "email": "emma.wright@example.com",
    "username": "emmaw",
    "role": "customer",
    "billing": {
      "city": "Portland",
      "country": "US"
    },
    "is_paying_customer": true,
    "date_created": "2026-01-03T10:00:00"
  }
]
```

</details>

### wordpress-api (port 8065) — server: started

| Result | Method | Path | Status | Endpoint |
|--------|--------|------|--------|----------|
| PASS | GET | /health | 200 | health |
| PASS | GET | /wp-json/wp/v2/posts?per_page=5 | 200 | list posts |
| PASS | GET | /wp-json/wp/v2/posts?categories=11 | 200 | list posts by category |
| PASS | GET | /wp-json/wp/v2/posts/101 | 200 | get post |
| PASS | POST | /wp-json/wp/v2/posts | 201 | create post |
| PASS | PUT | /wp-json/wp/v2/posts/106 | 200 | update post |
| PASS | DELETE | /wp-json/wp/v2/posts/108 | 200 | delete post |
| PASS | GET | /wp-json/wp/v2/pages | 200 | list pages |
| PASS | GET | /wp-json/wp/v2/categories | 200 | list categories |
| PASS | GET | /wp-json/wp/v2/tags | 200 | list tags |
| PASS | GET | /wp-json/wp/v2/comments?post=101 | 200 | list comments for post |
| PASS | POST | /wp-json/wp/v2/comments | 201 | create comment |
| PASS | GET | /wp-json/wp/v2/media | 200 | list media |
| PASS | GET | /wp-json/wp/v2/users | 200 | list users |

<details><summary>responses</summary>

**GET health** — `/health` (status 200)

```
{
  "status": "ok"
}
```

**GET list posts** — `/wp-json/wp/v2/posts?per_page=5` (status 200)

```
[
  {
    "id": 107,
    "title": {
      "rendered": "Hiring senior backend engineers"
    },
    "slug": "hiring-backend-engineers",
    "status": "publish",
    "author": 1,
    "content": {
      "rendered": "We are growing the platform team. Remote-friendly roles across EU and US time zones."
    },
    "excerpt": {
      "rendered": "Join the platform team."
    },
    "categories": [
      13
    ],
    "tags": [],
    "comment_status": "open",
    "date": "2026-05-24T16:00:00",
    "modified": "2026-05-24T16:00:00",
    "type": "post"
  },
  {
    "id": 105,
    "title": {
      "rende
... (truncated)
```

**GET list posts by category** — `/wp-json/wp/v2/posts?categories=11` (status 200)

```
[
  {
    "id": 102,
    "title": {
      "rendered": "Event-driven cleanup beats cron"
    },
    "slug": "event-driven-cleanup",
    "status": "publish",
    "author": 2,
    "content": {
      "rendered": "Replacing our cron-based reaper with an event-driven pipeline flattened our memory graphs."
    },
    "excerpt": {
      "rendered": "Why we ditched cron for events."
    },
    "categories": [
      10,
      11
    ],
    "tags": [
      22,
      25
    ],
    "comment_status": "open",
    "date": "2026-05-22T09:00:00",
    "modified": "2026-05-22T09:10:00",
    "type": "post"
  },
  
... (truncated)
```

**GET get post** — `/wp-json/wp/v2/posts/101` (status 200)

```
{
  "id": 101,
  "title": {
    "rendered": "Cutting session-store latency by 40 percent"
  },
  "slug": "cutting-session-store-latency",
  "status": "publish",
  "author": 1,
  "content": {
    "rendered": "We traced our p95 latency to a missing index. Here is how we found it and what we changed."
  },
  "excerpt": {
    "rendered": "A deep dive into a sneaky indexing bug."
  },
  "categories": [
    10,
    11
  ],
  "tags": [
    20,
    25
  ],
  "comment_status": "open",
  "date": "2026-05-20T15:00:00",
  "modified": "2026-05-20T15:30:00",
  "type": "post"
}
```

**POST create post** — `/wp-json/wp/v2/posts` (status 201)

```
{
  "id": 109,
  "title": {
    "rendered": "Postmortem: the cache stampede"
  },
  "slug": "postmortem:-the-cache-stampede",
  "status": "publish",
  "author": 2,
  "content": {
    "rendered": "What happened and how we fixed it."
  },
  "excerpt": {
    "rendered": ""
  },
  "categories": [
    10,
    11
  ],
  "tags": [
    25
  ],
  "comment_status": "open",
  "date": "2026-06-17T10:31:49",
  "modified": "2026-06-17T10:31:49",
  "type": "post"
}
```

**PUT update post** — `/wp-json/wp/v2/posts/106` (status 200)

```
{
  "id": 106,
  "title": {
    "rendered": "Rethinking our on-call rotation"
  },
  "slug": "rethinking-oncall-rotation",
  "status": "publish",
  "author": 2,
  "content": {
    "rendered": "Early notes on a follow-the-sun on-call model. Not ready to publish yet."
  },
  "excerpt": {
    "rendered": "Work in progress."
  },
  "categories": [
    11
  ],
  "tags": [
    22
  ],
  "comment_status": "closed",
  "date": "2026-05-25T08:00:00",
  "modified": "2026-06-17T10:31:49",
  "type": "post"
}
```

**DELETE delete post** — `/wp-json/wp/v2/posts/108` (status 200)

```
{
  "deleted": true,
  "previous": {
    "id": 108,
    "title": {
      "rendered": "Draft: observability that measures health"
    },
    "slug": "observability-measures-health",
    "status": "draft",
    "author": 3,
    "content": {
      "rendered": "Most dashboards measure activity, not health. Draft on SLO-first observability."
    },
    "excerpt": {
      "rendered": "SLO-first observability draft."
    },
    "categories": [
      11
    ],
    "tags": [
      25
    ],
    "comment_status": "open",
    "date": "2026-05-26T09:00:00",
    "modified": "2026-05-26T09:30:00",
    "type"
```

**GET list pages** — `/wp-json/wp/v2/pages` (status 200)

```
[
  {
    "id": 204,
    "title": {
      "rendered": "Engineering Team"
    },
    "slug": "engineering-team",
    "status": "publish",
    "author": 1,
    "content": {
      "rendered": "Meet the people behind the platform."
    },
    "date": "2025-02-01T11:00:00",
    "modified": "2025-05-20T11:00:00",
    "parent": 201,
    "type": "page"
  },
  {
    "id": 203,
    "title": {
      "rendered": "Privacy Policy"
    },
    "slug": "privacy-policy",
    "status": "publish",
    "author": 1,
    "content": {
      "rendered": "How we handle your data on this blog. Short version: minimally."
... (truncated)
```

**GET list categories** — `/wp-json/wp/v2/categories` (status 200)

```
[
  {
    "id": 10,
    "name": "Engineering",
    "slug": "engineering",
    "description": "Posts about how we build software.",
    "parent": 0,
    "count": 4,
    "taxonomy": "category"
  },
  {
    "id": 11,
    "name": "Reliability",
    "slug": "reliability",
    "description": "On-call, incidents, and SLOs.",
    "parent": 10,
    "count": 2,
    "taxonomy": "category"
  },
  {
    "id": 12,
    "name": "Frontend",
    "slug": "frontend",
    "description": "UI, design systems, and accessibility.",
    "parent": 10,
    "count": 1,
    "taxonomy": "category"
  },
  {
    "id": 13,
   
... (truncated)
```

**GET list tags** — `/wp-json/wp/v2/tags` (status 200)

```
[
  {
    "id": 20,
    "name": "python",
    "slug": "python",
    "description": "Posts mentioning Python.",
    "count": 3,
    "taxonomy": "post_tag"
  },
  {
    "id": 21,
    "name": "rust",
    "slug": "rust",
    "description": "Posts mentioning Rust.",
    "count": 1,
    "taxonomy": "post_tag"
  },
  {
    "id": 22,
    "name": "kubernetes",
    "slug": "kubernetes",
    "description": "Container orchestration.",
    "count": 2,
    "taxonomy": "post_tag"
  },
  {
    "id": 23,
    "name": "accessibility",
    "slug": "accessibility",
    "description": "Inclusive design and a11y.",

... (truncated)
```

**GET list comments for post** — `/wp-json/wp/v2/comments?post=101` (status 200)

```
[
  {
    "id": 301,
    "post": 101,
    "author_name": "Dana Li",
    "author_email": "dana.li@example.com",
    "content": {
      "rendered": "Great write-up. The missing index gotcha bites everyone eventually."
    },
    "status": "approved",
    "date": "2026-05-20T16:10:00",
    "parent": 0
  },
  {
    "id": 302,
    "post": 101,
    "author_name": "Marco Ferri",
    "author_email": "marco.ferri@example.com",
    "content": {
      "rendered": "Did you consider a partial index instead?"
    },
    "status": "approved",
    "date": "2026-05-20T17:00:00",
    "parent": 0
  },
  {
    "i
... (truncated)
```

**POST create comment** — `/wp-json/wp/v2/comments` (status 201)

```
{
  "id": 308,
  "post": 104,
  "author_name": "Reader One",
  "author_email": "reader@example.com",
  "content": {
    "rendered": "Excited to try the new plugin system!"
  },
  "status": "approved",
  "date": "2026-06-17T10:31:49",
  "parent": 0
}
```

**GET list media** — `/wp-json/wp/v2/media` (status 200)

```
[
  {
    "id": 401,
    "title": {
      "rendered": "latency-graph"
    },
    "slug": "latency-graph",
    "media_type": "image",
    "mime_type": "image/png",
    "source_url": "https://cdn.example.com/uploads/latency-graph.png",
    "alt_text": "Graph showing p95 latency dropping",
    "author": 1,
    "post": 101,
    "date": "2026-05-20T14:50:00",
    "type": "attachment"
  },
  {
    "id": 402,
    "title": {
      "rendered": "memory-flat"
    },
    "slug": "memory-flat",
    "media_type": "image",
    "mime_type": "image/png",
    "source_url": "https://cdn.example.com/uploads/memor
... (truncated)
```

**GET list users** — `/wp-json/wp/v2/users` (status 200)

```
[
  {
    "id": 1,
    "name": "Amelia Ortega",
    "slug": "amelia-ortega",
    "description": "Editor in chief and platform lead.",
    "url": "https://blog.example.com/author/amelia",
    "roles": [
      "administrator"
    ],
    "avatar_urls": {
      "96": "https://gravatar.example.com/amelia.png"
    }
  },
  {
    "id": 2,
    "name": "Jonas Pereira",
    "slug": "jonas-pereira",
    "description": "Infrastructure writer and SRE.",
    "url": "https://blog.example.com/author/jonas",
    "roles": [
      "editor"
    ],
    "avatar_urls": {
      "96": "https://gravatar.example.com/jon
... (truncated)
```

</details>

### xero-api (port 8088) — server: started

| Result | Method | Path | Status | Endpoint |
|--------|--------|------|--------|----------|
| PASS | GET | /health | 200 | health |
| PASS | GET | /api.xro/2.0/Invoices | 200 | list invoices |
| PASS | GET | /api.xro/2.0/Invoices?Status=AUTHORISED | 200 | list authorised invoices |
| PASS | GET | /api.xro/2.0/Invoices/i0000001-0000-0000-0000-000000000001 | 200 | get invoice |
| PASS | POST | /api.xro/2.0/Invoices | 200 | create invoice |
| PASS | GET | /api.xro/2.0/Contacts | 200 | list contacts |
| PASS | GET | /api.xro/2.0/Accounts | 200 | list accounts |

<details><summary>responses</summary>

**GET health** — `/health` (status 200)

```
{
  "status": "ok"
}
```

**GET list invoices** — `/api.xro/2.0/Invoices` (status 200)

```
{
  "Invoices": [
    {
      "InvoiceID": "i0000001-0000-0000-0000-000000000001",
      "InvoiceNumber": "INV-2041",
      "Type": "ACCREC",
      "Contact": {
        "ContactID": "c0000001-0000-0000-0000-000000000001",
        "Name": "Vandelay Industries"
      },
      "Date": "2026-04-20",
      "DueDate": "2026-05-05",
      "Status": "AUTHORISED",
      "LineAmountTypes": "Exclusive",
      "SubTotal": 4500.0,
      "TotalTax": 450.0,
      "Total": 4950.0,
      "AmountDue": 4950.0,
      "AmountPaid": 0.0,
      "CurrencyCode": "USD",
      "Reference": "April retainer"
    },
    {

... (truncated)
```

**GET list authorised invoices** — `/api.xro/2.0/Invoices?Status=AUTHORISED` (status 200)

```
{
  "Invoices": [
    {
      "InvoiceID": "i0000001-0000-0000-0000-000000000001",
      "InvoiceNumber": "INV-2041",
      "Type": "ACCREC",
      "Contact": {
        "ContactID": "c0000001-0000-0000-0000-000000000001",
        "Name": "Vandelay Industries"
      },
      "Date": "2026-04-20",
      "DueDate": "2026-05-05",
      "Status": "AUTHORISED",
      "LineAmountTypes": "Exclusive",
      "SubTotal": 4500.0,
      "TotalTax": 450.0,
      "Total": 4950.0,
      "AmountDue": 4950.0,
      "AmountPaid": 0.0,
      "CurrencyCode": "USD",
      "Reference": "April retainer"
    },
    {

... (truncated)
```

**GET get invoice** — `/api.xro/2.0/Invoices/i0000001-0000-0000-0000-000000000001` (status 200)

```
{
  "Invoices": [
    {
      "InvoiceID": "i0000001-0000-0000-0000-000000000001",
      "InvoiceNumber": "INV-2041",
      "Type": "ACCREC",
      "Contact": {
        "ContactID": "c0000001-0000-0000-0000-000000000001",
        "Name": "Vandelay Industries"
      },
      "Date": "2026-04-20",
      "DueDate": "2026-05-05",
      "Status": "AUTHORISED",
      "LineAmountTypes": "Exclusive",
      "SubTotal": 4500.0,
      "TotalTax": 450.0,
      "Total": 4950.0,
      "AmountDue": 4950.0,
      "AmountPaid": 0.0,
      "CurrencyCode": "USD",
      "Reference": "April retainer"
    }
  ]
}
```

**POST create invoice** — `/api.xro/2.0/Invoices` (status 200)

```
{
  "Invoices": [
    {
      "InvoiceID": "cb9be807-847b-41dd-a81e-61b5db58f5da",
      "InvoiceNumber": "INV-2053",
      "Type": "ACCREC",
      "Contact": {
        "ContactID": "c0000003-0000-0000-0000-000000000003",
        "Name": "Globex Corporation"
      },
      "Date": "2026-05-28",
      "DueDate": "2026-06-27",
      "Status": "DRAFT",
      "LineAmountTypes": "Exclusive",
      "SubTotal": 1500.0,
      "TotalTax": 150.0,
      "Total": 1650.0,
      "AmountDue": 1650.0,
      "AmountPaid": 0.0,
      "CurrencyCode": "USD",
      "Reference": "New project"
    }
  ]
}
```

**GET list contacts** — `/api.xro/2.0/Contacts` (status 200)

```
{
  "Contacts": [
    {
      "ContactID": "c0000001-0000-0000-0000-000000000001",
      "Name": "Vandelay Industries",
      "FirstName": "Omar",
      "LastName": "Haddad",
      "EmailAddress": "ap@vandelay.com",
      "IsCustomer": true,
      "IsSupplier": false,
      "ContactStatus": "ACTIVE",
      "AccountNumber": "VAND-001"
    },
    {
      "ContactID": "c0000002-0000-0000-0000-000000000002",
      "Name": "Initech LLC",
      "FirstName": "Bill",
      "LastName": "Lumbergh",
      "EmailAddress": "accounts@initech.com",
      "IsCustomer": true,
      "IsSupplier": false,
      "
... (truncated)
```

**GET list accounts** — `/api.xro/2.0/Accounts` (status 200)

```
{
  "Accounts": [
    {
      "AccountID": "a0000001-0000-0000-0000-000000000001",
      "Code": "200",
      "Name": "Sales",
      "Type": "REVENUE",
      "TaxType": "OUTPUT",
      "Status": "ACTIVE",
      "Description": "Income from any normal business activity",
      "EnablePaymentsToAccount": false
    },
    {
      "AccountID": "a0000002-0000-0000-0000-000000000002",
      "Code": "260",
      "Name": "Other Revenue",
      "Type": "REVENUE",
      "TaxType": "OUTPUT",
      "Status": "ACTIVE",
      "Description": "Any other income that does not relate to normal business",
      "E
... (truncated)
```

</details>

### yelp-api (port 8034) — server: started

| Result | Method | Path | Status | Endpoint |
|--------|--------|------|--------|----------|
| PASS | GET | /health | 200 | health |
| PASS | GET | /v3/businesses/search?location=San Francisco&term=cafe&sort_by=rating&limit=10 | 200 | search businesses |
| PASS | GET | /v3/businesses/search?categories=restaurants&price=3,4&sort_by=review_count | 200 | search by category and price |
| PASS | GET | /v3/businesses/biz-tartine-0002 | 200 | get business |
| PASS | GET | /v3/businesses/biz-tartine-0002/reviews | 200 | get business reviews |
| PASS | GET | /v3/categories | 200 | list categories |

<details><summary>responses</summary>

**GET health** — `/health` (status 200)

```
{
  "status": "ok"
}
```

**GET search businesses** — `/v3/businesses/search?location=San Francisco&term=cafe&sort_by=rating&limit=10` (status 200)

```
{
  "total": 2,
  "businesses": [
    {
      "id": "biz-the-grove-001",
      "alias": "biz-the-grove-001",
      "name": "The Grove Cafe",
      "rating": 4.5,
      "price": "$$",
      "review_count": 1820,
      "is_closed": false,
      "phone": "+14155551001",
      "image_url": "https://img.example.com/grove.jpg",
      "categories": [
        {
          "alias": "cafes",
          "title": "Cafes"
        }
      ],
      "coordinates": {
        "latitude": 37.7825,
        "longitude": -122.4061
      },
      "location": {
        "address1": "2016 Fillmore St",
        "city": "S
... (truncated)
```

**GET search by category and price** — `/v3/businesses/search?categories=restaurants&price=3,4&sort_by=review_count` (status 200)

```
{
  "total": 1,
  "businesses": [
    {
      "id": "biz-zuni-00003",
      "alias": "biz-zuni-00003",
      "name": "Zuni Cafe",
      "rating": 4.0,
      "price": "$$$",
      "review_count": 3100,
      "is_closed": false,
      "phone": "+14155551003",
      "image_url": "https://img.example.com/zuni.jpg",
      "categories": [
        {
          "alias": "restaurants",
          "title": "Restaurants"
        }
      ],
      "coordinates": {
        "latitude": 37.7726,
        "longitude": -122.4218
      },
      "location": {
        "address1": "1658 Market St",
        "city": "Sa
```

**GET get business** — `/v3/businesses/biz-tartine-0002` (status 200)

```
{
  "id": "biz-tartine-0002",
  "alias": "biz-tartine-0002",
  "name": "Tartine Bakery",
  "rating": 4.5,
  "price": "$$",
  "review_count": 5400,
  "is_closed": false,
  "phone": "+14155551002",
  "image_url": "https://img.example.com/tartine.jpg",
  "categories": [
    {
      "alias": "bakeries",
      "title": "Bakeries"
    }
  ],
  "coordinates": {
    "latitude": 37.7614,
    "longitude": -122.4241
  },
  "location": {
    "address1": "600 Guerrero St",
    "city": "San Francisco",
    "state": "CA",
    "display_address": [
      "600 Guerrero St",
      "San Francisco, CA"
    ]
  }
}
```

**GET get business reviews** — `/v3/businesses/biz-tartine-0002/reviews` (status 200)

```
{
  "total": 3,
  "reviews": [
    {
      "id": "rev-0000000004",
      "business_id": "biz-tartine-0002",
      "rating": 5,
      "text": "The morning bun is life-changing. Worth the line.",
      "time_created": "2026-04-20T08:45:00",
      "user": {
        "name": "Helena P"
      }
    },
    {
      "id": "rev-0000000005",
      "business_id": "biz-tartine-0002",
      "rating": 5,
      "text": "Best bakery in the city, hands down.",
      "time_created": "2026-03-30T07:50:00",
      "user": {
        "name": "Jonas R"
      }
    },
    {
      "id": "rev-0000000006",
      "business
... (truncated)
```

**GET list categories** — `/v3/categories` (status 200)

```
{
  "categories": [
    {
      "alias": "cafes",
      "title": "Cafes",
      "parent_aliases": [
        "food"
      ]
    },
    {
      "alias": "bakeries",
      "title": "Bakeries",
      "parent_aliases": [
        "food"
      ]
    },
    {
      "alias": "coffee",
      "title": "Coffee & Tea",
      "parent_aliases": [
        "food"
      ]
    },
    {
      "alias": "restaurants",
      "title": "Restaurants",
      "parent_aliases": [
        "restaurants"
      ]
    },
    {
      "alias": "steak",
      "title": "Steakhouses",
      "parent_aliases": [
        "restaurants"
... (truncated)
```

</details>

### youtube-api (port 8009) — server: started

| Result | Method | Path | Status | Endpoint |
|--------|--------|------|--------|----------|
| PASS | GET | /health | 200 | GET /health |
| PASS | GET | /youtube/v3/channels?id=UC_EquineHealthChannel&part=snippet,contentDetails,statistics,brandingSettings | 200 | GET Channel by ID |
| WARN | GET | /youtube/v3/channels?id=INVALID_CHANNEL_99 | 404 | GET Channel - 404 |
| PASS | GET | /youtube/v3/videos?channelId=UC_EquineHealthChannel&part=snippet,contentDetails,statistics,status&maxResults=5 | 200 | GET Videos by Channel |
| PASS | GET | /youtube/v3/videos?id=vid_001&part=snippet,contentDetails,statistics,status | 200 | GET Video by ID |
| PASS | GET | /youtube/v3/videos?id=INVALID_ID_99999&part=snippet | 200 | GET Video - 404 |
| PASS | GET | /youtube/v3/videos?id=vid_001,vid_002,vid_003&part=snippet,statistics | 200 | GET Multiple Videos by ID |
| PASS | PUT | /youtube/v3/videos?part=snippet,status | 200 | PUT Update Video |
| WARN | PUT | /youtube/v3/videos?part=snippet | 404 | PUT Update Video - 404 |
| PASS | DELETE | /youtube/v3/videos?id=vid_030 | 204 | DELETE Video |
| WARN | DELETE | /youtube/v3/videos?id=INVALID_ID_99999 | 404 | DELETE Video - 404 |
| PASS | GET | /youtube/v3/playlists?channelId=UC_EquineHealthChannel&part=snippet,contentDetails,status&maxResults=10 | 200 | GET Playlists by Channel |
| PASS | GET | /youtube/v3/playlists?id=PL_001&part=snippet,contentDetails,status | 200 | GET Playlist by ID |
| PASS | GET | /youtube/v3/playlists?id=INVALID_PL_99999&part=snippet | 200 | GET Playlist - 404 |
| PASS | POST | /youtube/v3/playlists?part=snippet,status | 201 | POST Create Playlist |
| PASS | PUT | /youtube/v3/playlists?part=snippet,status | 200 | PUT Update Playlist |
| WARN | PUT | /youtube/v3/playlists?part=snippet | 404 | PUT Update Playlist - 404 |
| PASS | DELETE | /youtube/v3/playlists?id=PL_010 | 204 | DELETE Playlist |
| WARN | DELETE | /youtube/v3/playlists?id=INVALID_PL_99999 | 404 | DELETE Playlist - 404 |
| PASS | GET | /youtube/v3/playlistItems?playlistId=PL_001&part=snippet,contentDetails&maxResults=10 | 200 | GET Playlist Items |
| PASS | POST | /youtube/v3/playlistItems?part=snippet | 201 | POST Insert Playlist Item |
| WARN | POST | /youtube/v3/playlistItems?part=snippet | 400 | POST Insert Playlist Item - Invalid Playlist |
| PASS | PUT | /youtube/v3/playlistItems?part=snippet | 200 | PUT Update Playlist Item Position |
| PASS | DELETE | /youtube/v3/playlistItems?id=PLI_025 | 204 | DELETE Playlist Item |
| WARN | DELETE | /youtube/v3/playlistItems?id=INVALID_PLI_99999 | 404 | DELETE Playlist Item - 404 |
| PASS | GET | /youtube/v3/commentThreads?videoId=vid_001&part=snippet,replies&maxResults=10 | 200 | GET Comment Threads for Video |
| PASS | GET | /youtube/v3/commentThreads?videoId=vid_019&part=snippet,replies&moderationStatus=heldForReview | 200 | GET Comment Threads - Held for Review |
| PASS | POST | /youtube/v3/commentThreads?part=snippet | 201 | POST Create Comment Thread |
| PASS | GET | /youtube/v3/comments?parentId=cmt_002&part=snippet | 200 | GET Replies to Comment |
| PASS | POST | /youtube/v3/comments?part=snippet | 201 | POST Reply to Comment |
| WARN | POST | /youtube/v3/comments?part=snippet | 400 | POST Reply - Invalid Parent |
| PASS | PUT | /youtube/v3/comments?part=snippet | 200 | PUT Update Comment |
| WARN | PUT | /youtube/v3/comments?part=snippet | 404 | PUT Update Comment - 404 |
| PASS | DELETE | /youtube/v3/comments?id=cmt_026 | 204 | DELETE Comment |
| WARN | DELETE | /youtube/v3/comments?id=INVALID_CMT_99999 | 404 | DELETE Comment - 404 |
| PASS | POST | /youtube/v3/comments/setModerationStatus?id=cmt_028&moderationStatus=published | 204 | POST Set Moderation Status |
| WARN | POST | /youtube/v3/comments/setModerationStatus?id=INVALID_CMT_99999&moderationStatus=rejected | 404 | POST Set Moderation Status - 404 |
| PASS | GET | /youtube/v3/search?q=python&channelId=UC_EquineHealthChannel&part=snippet&maxResults=10 | 200 | GET Search - by keyword |
| PASS | GET | /youtube/v3/search?q=career&channelId=UC_EquineHealthChannel&part=snippet&order=viewCount&maxResults=5 | 200 | GET Search - order by viewCount |
| PASS | GET | /youtube/v3/search?channelId=UC_EquineHealthChannel&part=snippet&order=date&maxResults=5 | 200 | GET Search - order by date |
| PASS | GET | /youtube/v3/search?q=xyznonexistent123&channelId=UC_EquineHealthChannel&part=snippet | 200 | GET Search - no results |
| PASS | GET | /youtube/v3/videoCategories?regionCode=US&part=snippet | 200 | GET Video Categories |
| PASS | GET | /youtube/v3/captions?videoId=vid_002&part=snippet | 200 | GET Captions for Video |
| WARN | GET | /youtube/v3/captions?videoId=INVALID_VID_99&part=snippet | 404 | GET Captions - Video Not Found |
| PASS | GET | /youtube/v3/channelSections?channelId=UC_EquineHealthChannel&part=snippet,contentDetails | 200 | GET Channel Sections |
| WARN | GET | /youtube/v3/channelSections?channelId=INVALID_CHANNEL_99&part=snippet | 404 | GET Channel Sections - 404 |
| PASS | GET | /youtube/analytics/v2/reports?ids=channel==UC_EquineHealthChannel&metrics=views,estimatedMinutesWatched,subscribersGained&startDate=2025-03-01&endDate=2025-03-31 | 200 | GET Channel Analytics |
| PASS | GET | /youtube/analytics/v2/reports?ids=channel==UC_EquineHealthChannel&filters=video==vid_001&metrics=views,estimatedMinutesWatched,likes&startDate=2025-03-01&endDate=2025-03-31 | 200 | GET Video Analytics |
| WARN | GET | /youtube/analytics/v2/reports?ids=channel==UC_EquineHealthChannel&filters=video==INVALID_VID_99&metrics=views | 404 | GET Video Analytics - 404 |

<details><summary>responses</summary>

**GET GET /health** — `/health` (status 200)

```
{
  "status": "ok"
}
```

**GET GET Channel by ID** — `/youtube/v3/channels?id=UC_EquineHealthChannel&part=snippet,contentDetails,statistics,brandingSettings` (status 200)

```
{
  "kind": "youtube#channelListResponse",
  "pageInfo": {
    "totalResults": 1,
    "resultsPerPage": 1
  },
  "items": [
    {
      "id": "UC_EquineHealthChannel",
      "snippet": {
        "title": "Equine Wellness Academy",
        "description": "Practical horse health education for owners, barn managers, and equine professionals. New videos every Monday and Thursday.\n\nTopics: Skin conditions, lameness, nutrition, dental care, emergency first aid, seasonal management, and preventive care.\n\nBusiness inquiries: equinewellnessacademy@gmail.com",
        "customUrl": "@equinewellnessac
... (truncated)
```

**GET GET Channel - 404** — `/youtube/v3/channels?id=INVALID_CHANNEL_99` (status 404)

```
{
  "error": "Channel INVALID_CHANNEL_99 not found"
}
```

**GET GET Videos by Channel** — `/youtube/v3/videos?channelId=UC_EquineHealthChannel&part=snippet,contentDetails,statistics,status&maxResults=5` (status 200)

```
{
  "kind": "youtube#videoListResponse",
  "pageInfo": {
    "totalResults": 30,
    "resultsPerPage": 5
  },
  "items": [
    {
      "id": "vid_001",
      "snippet": {
        "publishedAt": "2025-04-10T13:00:00Z",
        "channelId": "UC_EquineHealthChannel",
        "title": "Equine Skin Lesions - What Every Owner Should Know",
        "description": "A visual guide to the most common skin conditions in horses. Learn what to watch for and when to call your vet.\\n\\n0:00 Intro\\n1:45 Normal vs Abnormal Skin\\n4:30 Rain Rot (Dermatophilosis)\\n8:15 Ringworm (Dermatophytosis)\\n12:00 Scrat
... (truncated)
```

**GET GET Video by ID** — `/youtube/v3/videos?id=vid_001&part=snippet,contentDetails,statistics,status` (status 200)

```
{
  "kind": "youtube#videoListResponse",
  "pageInfo": {
    "totalResults": 1,
    "resultsPerPage": 25
  },
  "items": [
    {
      "id": "vid_001",
      "snippet": {
        "publishedAt": "2025-04-10T13:00:00Z",
        "channelId": "UC_EquineHealthChannel",
        "title": "Equine Skin Lesions - What Every Owner Should Know",
        "description": "A visual guide to the most common skin conditions in horses. Learn what to watch for and when to call your vet.\\n\\n0:00 Intro\\n1:45 Normal vs Abnormal Skin\\n4:30 Rain Rot (Dermatophilosis)\\n8:15 Ringworm (Dermatophytosis)\\n12:00 Scrat
... (truncated)
```

**GET GET Video - 404** — `/youtube/v3/videos?id=INVALID_ID_99999&part=snippet` (status 200)

```
{
  "kind": "youtube#videoListResponse",
  "pageInfo": {
    "totalResults": 0,
    "resultsPerPage": 25
  },
  "items": []
}
```

**GET GET Multiple Videos by ID** — `/youtube/v3/videos?id=vid_001,vid_002,vid_003&part=snippet,statistics` (status 200)

```
{
  "kind": "youtube#videoListResponse",
  "pageInfo": {
    "totalResults": 3,
    "resultsPerPage": 25
  },
  "items": [
    {
      "id": "vid_001",
      "snippet": {
        "publishedAt": "2025-04-10T13:00:00Z",
        "channelId": "UC_EquineHealthChannel",
        "title": "Equine Skin Lesions - What Every Owner Should Know",
        "description": "A visual guide to the most common skin conditions in horses. Learn what to watch for and when to call your vet.\\n\\n0:00 Intro\\n1:45 Normal vs Abnormal Skin\\n4:30 Rain Rot (Dermatophilosis)\\n8:15 Ringworm (Dermatophytosis)\\n12:00 Scrat
... (truncated)
```

**PUT PUT Update Video** — `/youtube/v3/videos?part=snippet,status` (status 200)

```
{
  "kind": "youtube#video",
  "items": [
    {
      "id": "vid_005",
      "snippet": {
        "publishedAt": "2025-03-13T13:00:00Z",
        "channelId": "UC_EquineHealthChannel",
        "title": "8 VS Code Extensions Senior Devs Use Daily",
        "description": "Updated description with new extensions.",
        "thumbnails": {
          "default": {
            "url": "https://i.ytimg.com/vi/vid_005/default.jpg",
            "width": 120,
            "height": 90
          },
          "medium": {
            "url": "https://i.ytimg.com/vi/vid_005/mqdefault.jpg",
            "width": 
... (truncated)
```

**PUT PUT Update Video - 404** — `/youtube/v3/videos?part=snippet` (status 404)

```
{
  "error": "Video INVALID_ID_99999 not found"
}
```

**DELETE DELETE Video** — `/youtube/v3/videos?id=vid_030` (status 204)

_(empty)_

**DELETE DELETE Video - 404** — `/youtube/v3/videos?id=INVALID_ID_99999` (status 404)

```
{
  "error": "Video INVALID_ID_99999 not found"
}
```

**GET GET Playlists by Channel** — `/youtube/v3/playlists?channelId=UC_EquineHealthChannel&part=snippet,contentDetails,status&maxResults=10` (status 200)

```
{
  "kind": "youtube#playlistListResponse",
  "pageInfo": {
    "totalResults": 10,
    "resultsPerPage": 10
  },
  "items": [
    {
      "id": "PL_001",
      "snippet": {
        "publishedAt": "2021-09-15T10:00:00Z",
        "channelId": "UC_EquineHealthChannel",
        "title": "Equine Skin Conditions",
        "description": "Comprehensive guides to identifying and managing skin problems in horses. From fungal infections to allergic reactions.",
        "thumbnails": {
          "default": {
            "url": "https://i.ytimg.com/vi/playlist_PL_001/default.jpg",
            "width": 12
... (truncated)
```

**GET GET Playlist by ID** — `/youtube/v3/playlists?id=PL_001&part=snippet,contentDetails,status` (status 200)

```
{
  "kind": "youtube#playlistListResponse",
  "pageInfo": {
    "totalResults": 1,
    "resultsPerPage": 25
  },
  "items": [
    {
      "id": "PL_001",
      "snippet": {
        "publishedAt": "2021-09-15T10:00:00Z",
        "channelId": "UC_EquineHealthChannel",
        "title": "Equine Skin Conditions",
        "description": "Comprehensive guides to identifying and managing skin problems in horses. From fungal infections to allergic reactions.",
        "thumbnails": {
          "default": {
            "url": "https://i.ytimg.com/vi/playlist_PL_001/default.jpg",
            "width": 120
... (truncated)
```

**GET GET Playlist - 404** — `/youtube/v3/playlists?id=INVALID_PL_99999&part=snippet` (status 200)

```
{
  "kind": "youtube#playlistListResponse",
  "pageInfo": {
    "totalResults": 0,
    "resultsPerPage": 25
  },
  "items": []
}
```

**POST POST Create Playlist** — `/youtube/v3/playlists?part=snippet,status` (status 201)

```
{
  "kind": "youtube#playlist",
  "items": [
    {
      "id": "PL_011",
      "snippet": {
        "publishedAt": "2026-06-17T10:31:51Z",
        "channelId": "UC_EquineHealthChannel",
        "title": "AI & Machine Learning",
        "description": "Tutorials on AI, ML, and LLMs for developers",
        "thumbnails": {
          "default": {
            "url": "https://i.ytimg.com/vi/playlist_PL_011/default.jpg",
            "width": 120,
            "height": 90
          },
          "medium": {
            "url": "https://i.ytimg.com/vi/playlist_PL_011/mqdefault.jpg",
            "width":
... (truncated)
```

**PUT PUT Update Playlist** — `/youtube/v3/playlists?part=snippet,status` (status 200)

```
{
  "kind": "youtube#playlist",
  "items": [
    {
      "id": "PL_005",
      "snippet": {
        "publishedAt": "2022-06-15T10:00:00Z",
        "channelId": "UC_EquineHealthChannel",
        "title": "Tool Reviews & Comparisons 2025",
        "description": "Updated reviews for the latest developer tools",
        "thumbnails": {
          "default": {
            "url": "https://i.ytimg.com/vi/playlist_PL_005/default.jpg",
            "width": 120,
            "height": 90
          },
          "medium": {
            "url": "https://i.ytimg.com/vi/playlist_PL_005/mqdefault.jpg",
        
... (truncated)
```

**PUT PUT Update Playlist - 404** — `/youtube/v3/playlists?part=snippet` (status 404)

```
{
  "error": "Playlist INVALID_PL_99999 not found"
}
```

**DELETE DELETE Playlist** — `/youtube/v3/playlists?id=PL_010` (status 204)

_(empty)_

**DELETE DELETE Playlist - 404** — `/youtube/v3/playlists?id=INVALID_PL_99999` (status 404)

```
{
  "error": "Playlist INVALID_PL_99999 not found"
}
```

**GET GET Playlist Items** — `/youtube/v3/playlistItems?playlistId=PL_001&part=snippet,contentDetails&maxResults=10` (status 200)

```
{
  "kind": "youtube#playlistItemListResponse",
  "pageInfo": {
    "totalResults": 7,
    "resultsPerPage": 10
  },
  "items": [
    {
      "id": "PLI_001",
      "snippet": {
        "publishedAt": "2025-04-10T13:00:00Z",
        "channelId": "UC_EquineHealthChannel",
        "title": "Equine Skin Lesions - What Every Owner Should Know",
        "playlistId": "PL_001",
        "position": 0,
        "resourceId": {
          "kind": "youtube#video",
          "videoId": "vid_001"
        },
        "thumbnails": {
          "default": {
            "url": "https://i.ytimg.com/vi/vid_001/def
... (truncated)
```

**POST POST Insert Playlist Item** — `/youtube/v3/playlistItems?part=snippet` (status 201)

```
{
  "kind": "youtube#playlistItem",
  "items": [
    {
      "id": "PLI_040",
      "snippet": {
        "publishedAt": "2026-06-17T10:31:51Z",
        "channelId": "UC_EquineHealthChannel",
        "title": "Equine Eye Emergencies - Do Not Wait on These",
        "playlistId": "PL_001",
        "position": 2,
        "resourceId": {
          "kind": "youtube#video",
          "videoId": "vid_020"
        },
        "thumbnails": {
          "default": {
            "url": "https://i.ytimg.com/vi/vid_020/default.jpg",
            "width": 120,
            "height": 90
          },
          "
... (truncated)
```

**POST POST Insert Playlist Item - Invalid Playlist** — `/youtube/v3/playlistItems?part=snippet` (status 400)

```
{
  "error": "Playlist INVALID_PL not found"
}
```

**PUT PUT Update Playlist Item Position** — `/youtube/v3/playlistItems?part=snippet` (status 200)

```
{
  "kind": "youtube#playlistItem",
  "items": [
    {
      "id": "PLI_003",
      "snippet": {
        "publishedAt": "2025-03-27T13:00:00Z",
        "channelId": "UC_EquineHealthChannel",
        "title": "Ringworm in Horses - Identification Treatment and Biosecurity",
        "playlistId": "PL_001",
        "position": 5,
        "resourceId": {
          "kind": "youtube#video",
          "videoId": "vid_003"
        },
        "thumbnails": {
          "default": {
            "url": "https://i.ytimg.com/vi/vid_003/default.jpg",
            "width": 120,
            "height": 90
        
... (truncated)
```

**DELETE DELETE Playlist Item** — `/youtube/v3/playlistItems?id=PLI_025` (status 204)

_(empty)_

**DELETE DELETE Playlist Item - 404** — `/youtube/v3/playlistItems?id=INVALID_PLI_99999` (status 404)

```
{
  "error": "Playlist item INVALID_PLI_99999 not found"
}
```

**GET GET Comment Threads for Video** — `/youtube/v3/commentThreads?videoId=vid_001&part=snippet,replies&maxResults=10` (status 200)

```
{
  "kind": "youtube#commentThreadListResponse",
  "pageInfo": {
    "totalResults": 5,
    "resultsPerPage": 10
  },
  "items": [
    {
      "kind": "youtube#commentThread",
      "id": "cmt_050",
      "snippet": {
        "channelId": "UC_EquineHealthChannel",
        "videoId": "vid_001",
        "topLevelComment": {
          "kind": "youtube#comment",
          "id": "cmt_050",
          "snippet": {
            "authorDisplayName": "GregYarrow_EO",
            "authorChannelId": {
              "value": "UC_user042"
            },
            "textDisplay": "Dr Boyd recommended this ch
... (truncated)
```

**GET GET Comment Threads - Held for Review** — `/youtube/v3/commentThreads?videoId=vid_019&part=snippet,replies&moderationStatus=heldForReview` (status 200)

```
{
  "kind": "youtube#commentThreadListResponse",
  "pageInfo": {
    "totalResults": 0,
    "resultsPerPage": 20
  },
  "items": []
}
```

**POST POST Create Comment Thread** — `/youtube/v3/commentThreads?part=snippet` (status 201)

```
{
  "kind": "youtube#commentThread",
  "items": [
    {
      "kind": "youtube#commentThread",
      "id": "cmt_051",
      "snippet": {
        "channelId": "UC_EquineHealthChannel",
        "videoId": "vid_001",
        "topLevelComment": {
          "kind": "youtube#comment",
          "id": "cmt_051",
          "snippet": {
            "authorDisplayName": "Equine Wellness Academy",
            "authorChannelId": {
              "value": "UC_EquineHealthChannel"
            },
            "textDisplay": "Great video! Thanks for the project ideas.",
            "textOriginal": "Great video!
... (truncated)
```

**GET GET Replies to Comment** — `/youtube/v3/comments?parentId=cmt_002&part=snippet` (status 200)

```
{
  "kind": "youtube#commentListResponse",
  "pageInfo": {
    "totalResults": 1,
    "resultsPerPage": 20
  },
  "items": [
    {
      "kind": "youtube#comment",
      "id": "cmt_003",
      "snippet": {
        "authorDisplayName": "Equine Wellness Academy",
        "authorChannelId": {
          "value": "UC_EquineHealthChannel"
        },
        "textDisplay": "Great question. Tack rub typically shows hair loss without the raised crusty border you see with fungal infections. The location alone does not rule it out though. If it is circular with that classic ring shape definitely get a cu
... (truncated)
```

**POST POST Reply to Comment** — `/youtube/v3/comments?part=snippet` (status 201)

```
{
  "kind": "youtube#comment",
  "items": [
    {
      "kind": "youtube#comment",
      "id": "cmt_052",
      "snippet": {
        "authorDisplayName": "Equine Wellness Academy",
        "authorChannelId": {
          "value": "UC_EquineHealthChannel"
        },
        "textDisplay": "Thanks for asking! I used Next.js with the app router.",
        "textOriginal": "Thanks for asking! I used Next.js with the app router.",
        "likeCount": 0,
        "publishedAt": "2026-06-17T10:31:51Z",
        "updatedAt": "2026-06-17T10:31:51Z",
        "videoId": "vid_001",
        "parentId": "cmt_0
```

**POST POST Reply - Invalid Parent** — `/youtube/v3/comments?part=snippet` (status 400)

```
{
  "error": "Parent comment INVALID_CMT_99999 not found"
}
```

**PUT PUT Update Comment** — `/youtube/v3/comments?part=snippet` (status 200)

```
{
  "kind": "youtube#comment",
  "items": [
    {
      "kind": "youtube#comment",
      "id": "cmt_003",
      "snippet": {
        "authorDisplayName": "Equine Wellness Academy",
        "authorChannelId": {
          "value": "UC_EquineHealthChannel"
        },
        "textDisplay": "Updated reply: Socket.io is great! Also check out the ws library for raw WebSocket support.",
        "textOriginal": "Updated reply: Socket.io is great! Also check out the ws library for raw WebSocket support.",
        "likeCount": 28,
        "publishedAt": "2025-04-11T14:00:00Z",
        "updatedAt": "2026
```

**PUT PUT Update Comment - 404** — `/youtube/v3/comments?part=snippet` (status 404)

```
{
  "error": "Comment INVALID_CMT_99999 not found"
}
```

**DELETE DELETE Comment** — `/youtube/v3/comments?id=cmt_026` (status 204)

_(empty)_

**DELETE DELETE Comment - 404** — `/youtube/v3/comments?id=INVALID_CMT_99999` (status 404)

```
{
  "error": "Comment INVALID_CMT_99999 not found"
}
```

**POST POST Set Moderation Status** — `/youtube/v3/comments/setModerationStatus?id=cmt_028&moderationStatus=published` (status 204)

_(empty)_

**POST POST Set Moderation Status - 404** — `/youtube/v3/comments/setModerationStatus?id=INVALID_CMT_99999&moderationStatus=rejected` (status 404)

```
{
  "error": "No matching comments found"
}
```

**GET GET Search - by keyword** — `/youtube/v3/search?q=python&channelId=UC_EquineHealthChannel&part=snippet&maxResults=10` (status 200)

```
{
  "kind": "youtube#searchListResponse",
  "pageInfo": {
    "totalResults": 0,
    "resultsPerPage": 10
  },
  "items": []
}
```

**GET GET Search - order by viewCount** — `/youtube/v3/search?q=career&channelId=UC_EquineHealthChannel&part=snippet&order=viewCount&maxResults=5` (status 200)

```
{
  "kind": "youtube#searchListResponse",
  "pageInfo": {
    "totalResults": 0,
    "resultsPerPage": 5
  },
  "items": []
}
```

**GET GET Search - order by date** — `/youtube/v3/search?channelId=UC_EquineHealthChannel&part=snippet&order=date&maxResults=5` (status 200)

```
{
  "kind": "youtube#searchListResponse",
  "pageInfo": {
    "totalResults": 29,
    "resultsPerPage": 5
  },
  "items": [
    {
      "kind": "youtube#searchResult",
      "id": {
        "kind": "youtube#video",
        "videoId": "vid_001"
      },
      "snippet": {
        "publishedAt": "2025-04-10T13:00:00Z",
        "channelId": "UC_EquineHealthChannel",
        "title": "Equine Skin Lesions - What Every Owner Should Know",
        "description": "A visual guide to the most common skin conditions in horses. Learn what to watch for and when to call your vet.\\n\\n0:00 Intro\\n1:45 Norm
... (truncated)
```

**GET GET Search - no results** — `/youtube/v3/search?q=xyznonexistent123&channelId=UC_EquineHealthChannel&part=snippet` (status 200)

```
{
  "kind": "youtube#searchListResponse",
  "pageInfo": {
    "totalResults": 0,
    "resultsPerPage": 25
  },
  "items": []
}
```

**GET GET Video Categories** — `/youtube/v3/videoCategories?regionCode=US&part=snippet` (status 200)

```
{
  "kind": "youtube#videoCategoryListResponse",
  "items": [
    {
      "kind": "youtube#videoCategory",
      "id": "1",
      "snippet": {
        "channelId": "UC_EquineHealthChannel",
        "title": "Film & Animation",
        "assignable": true
      }
    },
    {
      "kind": "youtube#videoCategory",
      "id": "2",
      "snippet": {
        "channelId": "UC_EquineHealthChannel",
        "title": "Autos & Vehicles",
        "assignable": true
      }
    },
    {
      "kind": "youtube#videoCategory",
      "id": "10",
      "snippet": {
        "channelId": "UC_EquineHealthChann
... (truncated)
```

**GET GET Captions for Video** — `/youtube/v3/captions?videoId=vid_002&part=snippet` (status 200)

```
{
  "kind": "youtube#captionListResponse",
  "items": [
    {
      "kind": "youtube#caption",
      "id": "cap_002",
      "snippet": {
        "videoId": "vid_002",
        "lastUpdated": "2025-04-03T13:30:00Z",
        "trackKind": "ASR",
        "language": "en",
        "name": "English (auto-generated)",
        "isDraft": false
      }
    }
  ]
}
```

**GET GET Captions - Video Not Found** — `/youtube/v3/captions?videoId=INVALID_VID_99&part=snippet` (status 404)

```
{
  "error": "Video INVALID_VID_99 not found"
}
```

**GET GET Channel Sections** — `/youtube/v3/channelSections?channelId=UC_EquineHealthChannel&part=snippet,contentDetails` (status 200)

```
{
  "kind": "youtube#channelSectionListResponse",
  "items": [
    {
      "kind": "youtube#channelSection",
      "id": "section_001",
      "snippet": {
        "type": "singlePlaylist",
        "channelId": "UC_EquineHealthChannel",
        "title": "Equine Skin Conditions",
        "position": 0
      },
      "contentDetails": {
        "playlists": [
          "PL_001"
        ]
      }
    },
    {
      "kind": "youtube#channelSection",
      "id": "section_002",
      "snippet": {
        "type": "singlePlaylist",
        "channelId": "UC_EquineHealthChannel",
        "title": "Horse 
... (truncated)
```

**GET GET Channel Sections - 404** — `/youtube/v3/channelSections?channelId=INVALID_CHANNEL_99&part=snippet` (status 404)

```
{
  "error": "Channel INVALID_CHANNEL_99 not found"
}
```

**GET GET Channel Analytics** — `/youtube/analytics/v2/reports?ids=channel==UC_EquineHealthChannel&metrics=views,estimatedMinutesWatched,subscribersGained&startDate=2025-03-01&endDate=2025-03-31` (status 200)

```
{
  "kind": "youtubeAnalytics#resultTable",
  "channelId": "UC_EquineHealthChannel",
  "period": "last28Days",
  "metrics": {
    "period": "last28Days",
    "views": 187234,
    "estimatedMinutesWatched": 534678,
    "averageViewDuration": 687,
    "subscribersGained": 1245,
    "subscribersLost": 87,
    "likes": 12567,
    "dislikes": 198,
    "comments": 1890,
    "shares": 4501
  }
}
```

**GET GET Video Analytics** — `/youtube/analytics/v2/reports?ids=channel==UC_EquineHealthChannel&filters=video==vid_001&metrics=views,estimatedMinutesWatched,likes&startDate=2025-03-01&endDate=2025-03-31` (status 200)

```
{
  "kind": "youtubeAnalytics#resultTable",
  "videoId": "vid_001",
  "metrics": {
    "videoId": "vid_001",
    "views": 68234,
    "estimatedMinutesWatched": 145890,
    "averageViewDuration": 1123,
    "likes": 4567,
    "dislikes": 12,
    "comments": 345,
    "shares": 1234,
    "averageViewPercentage": 72.8
  }
}
```

**GET GET Video Analytics - 404** — `/youtube/analytics/v2/reports?ids=channel==UC_EquineHealthChannel&filters=video==INVALID_VID_99&metrics=views` (status 404)

```
{
  "error": "Analytics for video INVALID_VID_99 not found"
}
```

</details>

### zendesk-api (port 8025) — server: started

| Result | Method | Path | Status | Endpoint |
|--------|--------|------|--------|----------|
| PASS | GET | /health | 200 | health |
| PASS | GET | /api/v2/tickets?status=open | 200 | list tickets |
| PASS | GET | /api/v2/tickets/701 | 200 | get ticket |
| PASS | POST | /api/v2/tickets | 201 | create ticket |
| PASS | PUT | /api/v2/tickets/704 | 200 | update ticket (status/assignee/priority) |
| PASS | GET | /api/v2/tickets/701/comments | 200 | list ticket comments |
| PASS | POST | /api/v2/tickets/701/comments | 201 | create comment |
| PASS | GET | /api/v2/users?role=agent | 200 | list users |
| PASS | GET | /api/v2/users/602 | 200 | get user |
| PASS | GET | /api/v2/organizations | 200 | list organizations |

<details><summary>responses</summary>

**GET health** — `/health` (status 200)

```
{
  "status": "ok"
}
```

**GET list tickets** — `/api/v2/tickets?status=open` (status 200)

```
{
  "tickets": [
    {
      "id": 701,
      "subject": "POS terminal not printing receipts",
      "description": "Receipts fail to print after the latest update",
      "status": "open",
      "priority": "high",
      "type": "problem",
      "requester_id": 604,
      "assignee_id": 602,
      "organization_id": 501,
      "tags": [
        "pos",
        "hardware"
      ],
      "created_at": "2026-05-10T09:00:00Z",
      "updated_at": "2026-05-20T12:00:00Z"
    },
    {
      "id": 705,
      "subject": "Refund not received",
      "description": "Refund issued 5 days ago not showing",
... (truncated)
```

**GET get ticket** — `/api/v2/tickets/701` (status 200)

```
{
  "ticket": {
    "id": 701,
    "subject": "POS terminal not printing receipts",
    "description": "Receipts fail to print after the latest update",
    "status": "open",
    "priority": "high",
    "type": "problem",
    "requester_id": 604,
    "assignee_id": 602,
    "organization_id": 501,
    "tags": [
      "pos",
      "hardware"
    ],
    "created_at": "2026-05-10T09:00:00Z",
    "updated_at": "2026-05-20T12:00:00Z"
  }
}
```

**POST create ticket** — `/api/v2/tickets` (status 201)

```
{
  "ticket": {
    "id": 709,
    "subject": "Card reader keeps disconnecting",
    "description": "The reader drops the bluetooth connection every few minutes.",
    "status": "new",
    "priority": "high",
    "type": "problem",
    "requester_id": 604,
    "assignee_id": null,
    "organization_id": null,
    "tags": [],
    "created_at": "2026-06-17T10:31:52Z",
    "updated_at": "2026-06-17T10:31:52Z"
  }
}
```

**PUT update ticket (status/assignee/priority)** — `/api/v2/tickets/704` (status 200)

```
{
  "ticket": {
    "id": 704,
    "subject": "API rate limit too low",
    "description": "We hit 429s during nightly sync",
    "status": "open",
    "priority": "high",
    "type": "task",
    "requester_id": 607,
    "assignee_id": 602,
    "organization_id": 504,
    "tags": [
      "api",
      "rate-limit"
    ],
    "created_at": "2026-05-24T10:00:00Z",
    "updated_at": "2026-06-17T10:31:52Z"
  }
}
```

**GET list ticket comments** — `/api/v2/tickets/701/comments` (status 200)

```
{
  "comments": [
    {
      "id": 801,
      "ticket_id": 701,
      "author_id": 604,
      "body": "The receipts stopped printing right after the v3.2 update.",
      "public": true,
      "created_at": "2026-05-10T09:00:00Z"
    },
    {
      "id": 802,
      "ticket_id": 701,
      "author_id": 602,
      "body": "Thanks for reporting. Can you share the printer model?",
      "public": true,
      "created_at": "2026-05-11T10:00:00Z"
    },
    {
      "id": 803,
      "ticket_id": 701,
      "author_id": 604,
      "body": "It is the Star TSP143 model.",
      "public": true,
      "cr
```

**POST create comment** — `/api/v2/tickets/701/comments` (status 201)

```
{
  "comment": {
    "id": 811,
    "ticket_id": 701,
    "author_id": 602,
    "body": "We shipped a firmware fix; please update and retry.",
    "public": true,
    "created_at": "2026-06-17T10:31:52Z"
  }
}
```

**GET list users** — `/api/v2/users?role=agent` (status 200)

```
{
  "users": [
    {
      "id": 602,
      "name": "Jonas Pereira",
      "email": "jonas.pereira@orbit-labs.com",
      "role": "agent",
      "organization_id": null,
      "active": true,
      "created_at": "2025-09-04T11:30:00Z"
    },
    {
      "id": 603,
      "name": "Helena Park",
      "email": "helena.park@orbit-labs.com",
      "role": "agent",
      "organization_id": null,
      "active": true,
      "created_at": "2025-09-12T14:20:00Z"
    }
  ],
  "count": 2
}
```

**GET get user** — `/api/v2/users/602` (status 200)

```
{
  "user": {
    "id": 602,
    "name": "Jonas Pereira",
    "email": "jonas.pereira@orbit-labs.com",
    "role": "agent",
    "organization_id": null,
    "active": true,
    "created_at": "2025-09-04T11:30:00Z"
  }
}
```

**GET list organizations** — `/api/v2/organizations` (status 200)

```
{
  "organizations": [
    {
      "id": 501,
      "name": "Aurora Bistro LLC",
      "domain_names": [
        "aurorabistro.com"
      ],
      "created_at": "2025-11-02T10:00:00Z"
    },
    {
      "id": 502,
      "name": "Helix Robotics Inc",
      "domain_names": [
        "helixrobotics.io"
      ],
      "created_at": "2025-09-15T09:30:00Z"
    },
    {
      "id": 503,
      "name": "Lumen Design Studio",
      "domain_names": [
        "lumendesign.co"
      ],
      "created_at": "2026-01-10T14:00:00Z"
    },
    {
      "id": 504,
      "name": "Pelagic Freight Co",
      "domain
```

</details>

### zillow-api (port 8011) — server: started

| Result | Method | Path | Status | Endpoint |
|--------|--------|------|--------|----------|
| PASS | GET | /health | 200 | health |
| PASS | GET | /v1/properties/search?city=Bellevue&state=WA&min_beds=4&max_price=2000000 | 200 | search Bellevue family |
| PASS | GET | /v1/properties/84120001 | 200 | get property |
| PASS | GET | /v1/properties/84120001/zestimate | 200 | zestimate |
| PASS | GET | /v1/properties/84120001/price-history | 200 | price history |
| PASS | GET | /v1/agents?city=Bellevue | 200 | list agents |
| PASS | GET | /v1/agents/agent-001 | 200 | get agent |
| PASS | GET | /v1/users/user-buyer-001/saved-searches | 200 | list saved searches |
| PASS | POST | /v1/users/user-buyer-001/saved-searches | 201 | create saved search |
| PASS | DELETE | /v1/saved-searches/search-003 | 200 | delete saved search |

<details><summary>responses</summary>

**GET health** — `/health` (status 200)

```
{
  "status": "ok"
}
```

**GET search Bellevue family** — `/v1/properties/search?city=Bellevue&state=WA&min_beds=4&max_price=2000000` (status 200)

```
{
  "total": 1,
  "count": 1,
  "offset": 0,
  "limit": 25,
  "results": [
    {
      "zpid": 84120001,
      "address": "412 Maple Grove Ct",
      "city": "Bellevue",
      "state": "WA",
      "zipcode": "98004",
      "latitude": 47.6101,
      "longitude": -122.2015,
      "bedrooms": 4,
      "bathrooms": 3.5,
      "living_area_sqft": 2840,
      "lot_size_sqft": 7200,
      "year_built": 2012,
      "home_type": "SingleFamily",
      "list_price": 1495000,
      "zestimate": 1512300,
      "rent_zestimate": 5400,
      "status": "FOR_SALE",
      "days_on_zillow": 18,
      "listing_a
```

**GET get property** — `/v1/properties/84120001` (status 200)

```
{
  "zpid": 84120001,
  "address": "412 Maple Grove Ct",
  "city": "Bellevue",
  "state": "WA",
  "zipcode": "98004",
  "latitude": 47.6101,
  "longitude": -122.2015,
  "bedrooms": 4,
  "bathrooms": 3.5,
  "living_area_sqft": 2840,
  "lot_size_sqft": 7200,
  "year_built": 2012,
  "home_type": "SingleFamily",
  "list_price": 1495000,
  "zestimate": 1512300,
  "rent_zestimate": 5400,
  "status": "FOR_SALE",
  "days_on_zillow": 18,
  "listing_agent_id": "agent-001"
}
```

**GET zestimate** — `/v1/properties/84120001/zestimate` (status 200)

```
{
  "zpid": 84120001,
  "address": "412 Maple Grove Ct",
  "zestimate": 1512300,
  "rent_zestimate": 5400,
  "list_price": 1495000,
  "delta_pct": 1.16
}
```

**GET price history** — `/v1/properties/84120001/price-history` (status 200)

```
{
  "zpid": 84120001,
  "count": 3,
  "history": [
    {
      "zpid": 84120001,
      "event_date": "2026-04-15",
      "event": "Listed for sale",
      "price": 1495000.0,
      "price_per_sqft": 526.0,
      "source": "Zillow"
    },
    {
      "zpid": 84120001,
      "event_date": "2024-08-12",
      "event": "Sold",
      "price": 1280000.0,
      "price_per_sqft": 451.0,
      "source": "County"
    },
    {
      "zpid": 84120001,
      "event_date": "2014-05-20",
      "event": "Sold",
      "price": 725000.0,
      "price_per_sqft": 255.0,
      "source": "County"
    }
  ]
}
```

**GET list agents** — `/v1/agents?city=Bellevue` (status 200)

```
{
  "count": 2,
  "agents": [
    {
      "agent_id": "agent-001",
      "name": "Sarah Whitfield",
      "brokerage": "Cascade Realty Group",
      "phone": "206-555-0118",
      "email": "sarah.whitfield@cascaderealty.com",
      "license_number": "WA-1284991",
      "active_listings": 4,
      "sold_last_12mo": 28,
      "rating": 4.9,
      "reviews": 142
    },
    {
      "agent_id": "agent-002",
      "name": "Daniel Reyes",
      "brokerage": "Evergreen Properties",
      "phone": "425-555-0204",
      "email": "daniel.reyes@evergreenprop.com",
      "license_number": "WA-1300218",
   
```

**GET get agent** — `/v1/agents/agent-001` (status 200)

```
{
  "agent_id": "agent-001",
  "name": "Sarah Whitfield",
  "brokerage": "Cascade Realty Group",
  "phone": "206-555-0118",
  "email": "sarah.whitfield@cascaderealty.com",
  "license_number": "WA-1284991",
  "active_listings": 4,
  "sold_last_12mo": 28,
  "rating": 4.9,
  "reviews": 142,
  "listings": [
    {
      "zpid": 84120001,
      "address": "412 Maple Grove Ct",
      "city": "Bellevue",
      "state": "WA",
      "zipcode": "98004",
      "latitude": 47.6101,
      "longitude": -122.2015,
      "bedrooms": 4,
      "bathrooms": 3.5,
      "living_area_sqft": 2840,
      "lot_size_sqf
... (truncated)
```

**GET list saved searches** — `/v1/users/user-buyer-001/saved-searches` (status 200)

```
{
  "count": 2,
  "results": [
    {
      "search_id": "search-001",
      "user_id": "user-buyer-001",
      "name": "Bellevue family homes",
      "city": "Bellevue",
      "state": "WA",
      "min_price": 800000,
      "max_price": 1600000,
      "min_beds": 4,
      "min_baths": 2.5,
      "home_type": "SingleFamily",
      "created_at": "2026-04-10"
    },
    {
      "search_id": "search-002",
      "user_id": "user-buyer-001",
      "name": "Eastside condos under 700k",
      "city": null,
      "state": "WA",
      "min_price": 400000,
      "max_price": 700000,
      "min_beds": 2,

```

**POST create saved search** — `/v1/users/user-buyer-001/saved-searches` (status 201)

```
{
  "search_id": "search-e6d8afc1",
  "user_id": "user-buyer-001",
  "name": "Sammamish family",
  "city": "Sammamish",
  "state": "WA",
  "min_price": 0,
  "max_price": 2000000,
  "min_beds": 4,
  "min_baths": 0.0,
  "home_type": "SingleFamily",
  "created_at": "2026-06-17"
}
```

**DELETE delete saved search** — `/v1/saved-searches/search-003` (status 200)

```
{
  "deleted": true,
  "search_id": "search-003"
}
```

</details>

### zoom-api (port 8028) — server: started

| Result | Method | Path | Status | Endpoint |
|--------|--------|------|--------|----------|
| PASS | GET | /health | 200 | health |
| PASS | GET | /v2/users/me | 200 | get me |
| PASS | GET | /v2/users/me/meetings?type=scheduled | 200 | list scheduled meetings |
| PASS | GET | /v2/users/me/meetings?type=previous_meetings | 200 | list previous meetings |
| PASS | POST | /v2/users/me/meetings | 201 | create meeting |
| PASS | GET | /v2/meetings/85012345678 | 200 | get meeting |
| PASS | PATCH | /v2/meetings/85012345678 | 200 | update meeting |
| PASS | DELETE | /v2/meetings/85012345680 | 204 | delete meeting |
| PASS | GET | /v2/meetings/85012345670/recordings | 200 | get recordings |
| PASS | GET | /v2/meetings/85012345679/registrants?status=approved | 200 | list registrants |

<details><summary>responses</summary>

**GET health** — `/health` (status 200)

```
{
  "status": "ok"
}
```

**GET get me** — `/v2/users/me` (status 200)

```
{
  "id": "u-amelia-9f4b2e8d",
  "first_name": "Amelia",
  "last_name": "Ortega",
  "email": "amelia.ortega@orbit-labs.com",
  "type": 2,
  "role_name": "Owner",
  "pmi": 4155550123,
  "timezone": "America/Los_Angeles",
  "verified": 1,
  "dept": "Engineering",
  "account_id": "acc-orbit-labs-001",
  "status": "active",
  "created_at": "2025-09-01T10:00:00Z"
}
```

**GET list scheduled meetings** — `/v2/users/me/meetings?type=scheduled` (status 200)

```
{
  "page_count": 1,
  "page_size": 30,
  "total_records": 3,
  "meetings": [
    {
      "id": 85012345678,
      "host_id": "u-amelia-9f4b2e8d",
      "topic": "Weekly Engineering Sync",
      "type": 2,
      "status": "waiting",
      "start_time": "2026-05-29T16:00:00Z",
      "duration": 60,
      "timezone": "America/Los_Angeles",
      "agenda": "Sprint progress and blockers",
      "join_url": "https://zoom.us/j/85012345678",
      "created_at": "2026-05-20T10:00:00Z"
    },
    {
      "id": 85012345679,
      "host_id": "u-amelia-9f4b2e8d",
      "topic": "Q2 Roadmap Review",
      
... (truncated)
```

**GET list previous meetings** — `/v2/users/me/meetings?type=previous_meetings` (status 200)

```
{
  "page_count": 1,
  "page_size": 30,
  "total_records": 3,
  "meetings": [
    {
      "id": 85012345672,
      "host_id": "u-amelia-9f4b2e8d",
      "topic": "All Hands May",
      "type": 8,
      "status": "finished",
      "start_time": "2026-05-16T20:00:00Z",
      "duration": 40,
      "timezone": "America/Los_Angeles",
      "agenda": "Monthly all hands",
      "join_url": "https://zoom.us/j/85012345672",
      "created_at": "2026-05-09T10:00:00Z"
    },
    {
      "id": 85012345671,
      "host_id": "u-amelia-9f4b2e8d",
      "topic": "Architecture Deep Dive",
      "type": 2,
    
... (truncated)
```

**POST create meeting** — `/v2/users/me/meetings` (status 201)

```
{
  "id": 83317368765,
  "host_id": "u-amelia-9f4b2e8d",
  "topic": "Incident Postmortem",
  "type": 2,
  "status": "waiting",
  "start_time": "2026-06-05T17:00:00Z",
  "duration": 50,
  "timezone": "America/Los_Angeles",
  "agenda": "Review the 5/26 outage",
  "join_url": "https://zoom.us/j/83317368765",
  "created_at": "2026-06-17T10:31:53Z"
}
```

**GET get meeting** — `/v2/meetings/85012345678` (status 200)

```
{
  "id": 85012345678,
  "host_id": "u-amelia-9f4b2e8d",
  "topic": "Weekly Engineering Sync",
  "type": 2,
  "status": "waiting",
  "start_time": "2026-05-29T16:00:00Z",
  "duration": 60,
  "timezone": "America/Los_Angeles",
  "agenda": "Sprint progress and blockers",
  "join_url": "https://zoom.us/j/85012345678",
  "created_at": "2026-05-20T10:00:00Z"
}
```

**PATCH update meeting** — `/v2/meetings/85012345678` (status 200)

```
{
  "id": 85012345678,
  "host_id": "u-amelia-9f4b2e8d",
  "topic": "Weekly Engineering Sync",
  "type": 2,
  "status": "waiting",
  "start_time": "2026-05-29T16:00:00Z",
  "duration": 60,
  "timezone": "America/Los_Angeles",
  "agenda": "Sprint progress and blockers",
  "join_url": "https://zoom.us/j/85012345678",
  "created_at": "2026-05-20T10:00:00Z"
}
```

**DELETE delete meeting** — `/v2/meetings/85012345680` (status 204)

_(empty)_

**GET get recordings** — `/v2/meetings/85012345670/recordings` (status 200)

```
{
  "id": 85012345670,
  "uuid": "uuid-85012345670",
  "host_id": "u-amelia-9f4b2e8d",
  "topic": "Sprint Retro 21",
  "start_time": "2026-05-22T16:00:00Z",
  "duration": 55,
  "total_size": 555745280,
  "recording_count": 2,
  "recording_files": [
    {
      "id": "rec-0001",
      "meeting_id": 85012345670,
      "recording_type": "shared_screen_with_speaker_view",
      "file_type": "MP4",
      "file_size": 524288000,
      "recording_start": "2026-05-22T16:01:00Z",
      "recording_end": "2026-05-22T16:55:00Z",
      "play_url": "https://zoom.us/rec/play/aaa111",
      "status": "complet
... (truncated)
```

**GET list registrants** — `/v2/meetings/85012345679/registrants?status=approved` (status 200)

```
{
  "page_count": 1,
  "page_size": 2,
  "total_records": 2,
  "registrants": [
    {
      "id": "reg-0001",
      "meeting_id": 85012345679,
      "email": "jonas.pereira@orbit-labs.com",
      "first_name": "Jonas",
      "last_name": "Pereira",
      "status": "approved",
      "join_time": null,
      "create_time": "2026-05-21T12:00:00Z"
    },
    {
      "id": "reg-0002",
      "meeting_id": 85012345679,
      "email": "helena.park@orbit-labs.com",
      "first_name": "Helena",
      "last_name": "Park",
      "status": "approved",
      "join_time": null,
      "create_time": "2026-05
```

</details>
