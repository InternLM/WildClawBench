# kensei2 Mock API Test Report

- Generated: 2026-05-28 11:27:07 UTC
- Python: 3.9.6
- Environments tested: 20
- Endpoints exercised: 209
- Totals: PASS 209 | WARN(4xx) 0 | FAIL 0 | SKIP 0

Result legend: PASS = 2xx/3xx, WARN = 4xx (error-path or runtime-dependent id), FAIL = 5xx / connection error / server down, SKIP = unresolved `{{variable}}` (not sent).

## Summary by environment

| Environment | Port | Server | Endpoints | PASS | WARN | FAIL | SKIP |
|-------------|------|--------|-----------|------|------|------|------|
| algolia-api | 8067 | started | 10 | 10 | 0 | 0 | 0 |
| amadeus-api | 8076 | started | 7 | 7 | 0 | 0 | 0 |
| bamboohr-api | 8072 | started | 10 | 10 | 0 | 0 | 0 |
| contentful-api | 8066 | started | 12 | 12 | 0 | 0 | 0 |
| figma-api | 8079 | started | 9 | 9 | 0 | 0 | 0 |
| google-analytics-api | 8068 | started | 7 | 7 | 0 | 0 | 0 |
| greenhouse-api | 8073 | started | 11 | 11 | 0 | 0 | 0 |
| gusto-api | 8074 | started | 10 | 10 | 0 | 0 | 0 |
| intercom-api | 8070 | started | 12 | 12 | 0 | 0 | 0 |
| linkedin-api | 8062 | started | 10 | 10 | 0 | 0 | 0 |
| mailchimp-api | 8069 | started | 12 | 12 | 0 | 0 | 0 |
| monday-api | 8080 | started | 12 | 12 | 0 | 0 | 0 |
| nasa-api | 8077 | started | 9 | 9 | 0 | 0 | 0 |
| openlibrary-api | 8078 | started | 10 | 10 | 0 | 0 | 0 |
| servicenow-api | 8071 | started | 12 | 12 | 0 | 0 | 0 |
| telegram-api | 8063 | started | 9 | 9 | 0 | 0 | 0 |
| ticketmaster-api | 8075 | started | 11 | 11 | 0 | 0 | 0 |
| twitch-api | 8064 | started | 9 | 9 | 0 | 0 | 0 |
| twitter-api | 8061 | started | 13 | 13 | 0 | 0 | 0 |
| wordpress-api | 8065 | started | 14 | 14 | 0 | 0 | 0 |

## Details

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
  "taskID": 202231
}
```

**PUT update object** — `/1/indexes/products/prod-004` (status 200)

```
{
  "objectID": "prod-004",
  "updatedAt": "",
  "taskID": 903331
}
```

**DELETE delete object** — `/1/indexes/products/prod-008` (status 200)

```
{
  "objectID": "prod-008",
  "deletedAt": "",
  "taskID": 660524
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
      "workEmail": "amelia.ortega@orbitlabs.com",
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
      "workEmail": "jonas.pereira@orbitlabs.com",
      "department": "Engineering",
      "jobTitle": "Staff Software Engineer",
      "location": "San Franc
... (truncated)
```

**GET get employee** — `/api/gateway.php/orbitlabs/v1/employees/emp-102` (status 200)

```
{
  "id": "emp-102",
  "firstName": "Jonas",
  "lastName": "Pereira",
  "workEmail": "jonas.pereira@orbitlabs.com",
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
  "id": "emp-f3c1e4a6",
  "firstName": "Aisha",
  "lastName": "Khan",
  "workEmail": "aisha.khan@orbitlabs.com",
  "department": "Engineering",
  "jobTitle": "Software Engineer",
  "location": "Remote",
  "hireDate": "2026-05-28",
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
  "id": "tor-0f5e3466",
  "employeeId": "emp-104",
  "type": "Vacation",
  "status": "requested",
  "start": "2026-07-20",
  "end": "2026-07-24",
  "amount": 5,
  "unit": "days",
  "notes": "Conference travel",
  "created": "2026-05-28"
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
      "headcount": 5
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
    "id": "499e2e38d7d54c4f",
    "type": "Entry",
    "createdAt": "2026-05-28T11:27:10.000Z",
    "updatedAt": "2026-05-28T11:27:10.000Z",
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
    "updatedAt": "2026-05-28T11:27:10.000Z",
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
  "id": "cmt-b8557086",
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
  "created_at": "2026-05-28T11:27:10Z"
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
  "id": "cand-dedf27de",
  "first_name": "Priya",
  "last_name": "Sharma",
  "email": "priya.sharma@example.com",
  "phone": "",
  "company": "Vandelay",
  "title": "Backend Engineer",
  "source": "Referral",
  "created_at": "2026-05-28T11:27:12Z"
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
  "last_activity_at": "2026-05-28T11:27:12Z"
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
  "last_activity_at": "2026-05-28T11:27:12Z",
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
    "email": "amelia.ortega@orbitlabs.com",
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
      "effective_date": "2024-0
... (truncated)
```

**GET get employee** — `/v1/employees/gemp-202` (status 200)

```
{
  "id": "gemp-202",
  "company_id": "comp-001",
  "first_name": "Jonas",
  "last_name": "Pereira",
  "email": "jonas.pereira@orbitlabs.com",
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
  "id": "pay-c3056156",
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
  "id": "contact-9ff8f55e2014",
  "role": "lead",
  "name": "Priya Nair",
  "email": "priya@delta-io.com",
  "phone": null,
  "company_id": null,
  "created_at": "2026-05-28T11:27:13.000Z",
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
  "id": "conv-76782431deb0",
  "state": "open",
  "open": true,
  "title": "Inviting teammates",
  "created_at": "2026-05-28T11:27:13.000Z",
  "updated_at": "2026-05-28T11:27:13.000Z",
  "contact_id": "contact-hannah",
  "admin_assignee_id": null,
  "conversation_parts": {
    "type": "conversation_part.list",
    "total_count": 1,
    "conversation_parts": [
      {
        "id": "part-adf089b21017",
        "conversation_id": "conv-76782431deb0",
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
  "updated_at": "2026-05-28T11:27:13.000Z",
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
  "updated_at": "2026-05-28T11:27:13.000Z",
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
  "updated_at": "2026-05-28T11:27:13.000Z",
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
  "id": "1112582439",
  "author_id": "urn:li:person:amelia-ortega",
  "commentary": "Thrilled to share our team shipped the new plugin API today.",
  "visibility": "PUBLIC",
  "created_at": "2026-05-28T11:27:13.000Z",
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

### mailchimp-api (port 8069) — server: started

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
  "timestamp_signup": "2026-05-28T11:27:14+00:00",
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
  "id": "camp-1afc07c8cc",
  "list_id": "list-product",
  "type": "regular",
  "status": "save",
  "emails_sent": 0,
  "send_time": null,
  "create_time": "2026-05-28T11:27:14+00:00",
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
  "id": "item-cc90310f",
  "name": "Add rate limiting to API gateway",
  "board_id": "board-101",
  "group": {
    "id": "grp-todo"
  },
  "created_at": "2026-05-28T11:27:15Z",
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
    "sys_id": "569da35a637547f5bf2e639ffc46fbbb",
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
    "opened_at": "2026-05-28T11:27:17Z",
    "updated_at": "2026-05-28T11:27:17Z"
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
    "updated_at": "2026-05-28T11:27:17Z"
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
      "email": "amelia.ortega@orbitlabs.com",
      "title": "IT Service Manager",
      "department": "IT Service Management",
      "active": true
    },
    {
      "sys_id": "usr-jonas",
      "user_name": "jonas.pereira",
      "name": "Jonas Pereira",
      "email": "jonas.pereira@orbitlabs.com",
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
    "email": "amelia.ortega@orbitlabs.com",
    "title": "IT Service Manager",
    "department": "IT Service Management",
    "active": true
  }
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
    "date": 1779967637,
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
    "date": 1779967637,
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
    "edit_date": 1779967637
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
    "followers_count": "18432",
    "following_count": "312",
    "tweet_count": "1840",
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
    "followers_count": "54210",
    "following_count": "128",
    "tweet_count": "920",
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
    "followers_count": "54210",
    "following_count": "128",
    "tweet_count": "920",
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
      "followers_count": "54210",
      "following_count": "128",
      "tweet_count": "920",
      "public_metrics": {
        "followers_count": 54210,
        "following_count": 128,
        "tweet_count": 920
      }
    },
    {
   
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
    "id": "585247294931525122",
    "author_id": "2001",
    "text": "Just deployed the new plugin API. No downtime.",
    "created_at": "2026-05-28T11:27:19.000Z",
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
  "date": "2026-05-28T11:27:20",
  "modified": "2026-05-28T11:27:20",
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
  "modified": "2026-05-28T11:27:20",
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
  "date": "2026-05-28T11:27:20",
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
