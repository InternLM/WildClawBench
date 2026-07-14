---
name: google-contacts-api-connector
description: >
  Google Contacts API (Mock) mock HTTP API. Base URL is provided via the `GOOGLE_CONTACTS_API_URL` environment
  variable. Auth headers are mocked (any token accepted); responses are
  deterministic fixtures backed by the task's mock_data.
metadata: {"clawdbot":{"emoji":"🔌"}}
---

# Google Contacts API (Mock)

Mock HTTP API. **All requests go to the base URL in `$GOOGLE_CONTACTS_API_URL`.**

## Base URL

| Variable | Purpose |
|----------|---------|
| `GOOGLE_CONTACTS_API_URL` | Base URL for all requests (e.g. `http://google-contacts-api:8102`) |

## Endpoints

| Method | Path |
|--------|------|
| GET | `/contacts` |
| GET | `/contacts/{item_id}` |
| POST | `/contacts` |
| GET | `/contact_groups` |

All list endpoints return `{"<resource>": [ ... ]}`. GET-by-id returns the row
or 404. POST creates; PATCH updates by id.
