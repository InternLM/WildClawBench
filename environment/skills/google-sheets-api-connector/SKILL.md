---
name: google-sheets-api-connector
description: >
  Google Sheets API (Mock) mock HTTP API. Base URL is provided via the `GOOGLE_SHEETS_API_URL` environment
  variable. Auth headers are mocked (any token accepted); responses are
  deterministic fixtures backed by the task's mock_data.
metadata: {"clawdbot":{"emoji":"🔌"}}
---

# Google Sheets API (Mock)

Mock HTTP API. **All requests go to the base URL in `$GOOGLE_SHEETS_API_URL`.**

## Base URL

| Variable | Purpose |
|----------|---------|
| `GOOGLE_SHEETS_API_URL` | Base URL for all requests (e.g. `http://google-sheets-api:8104`) |

## Endpoints

| Method | Path |
|--------|------|
| GET | `/spreadsheets` |
| GET | `/spreadsheets/{item_id}` |
| POST | `/spreadsheets` |
| GET | `/sheet_values` |

All list endpoints return `{"<resource>": [ ... ]}`. GET-by-id returns the row
or 404. POST creates; PATCH updates by id.
