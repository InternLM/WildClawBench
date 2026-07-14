# Google Sheets API (Mock) Guide

Worked `curl` examples for every endpoint. **All requests target the base URL in `$GOOGLE_SHEETS_API_URL`.** Auth headers are mocked (any token is accepted) and responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `GOOGLE_SHEETS_API_URL` | Base URL for all requests |

## Sheet_Values

```bash
curl -s "$GOOGLE_SHEETS_API_URL/sheet_values"
```

## Spreadsheets

```bash
curl -s "$GOOGLE_SHEETS_API_URL/spreadsheets"
curl -s "$GOOGLE_SHEETS_API_URL/spreadsheets/<item_id>"
curl -s -X POST "$GOOGLE_SHEETS_API_URL/spreadsheets" -H 'Content-Type: application/json' -d '{}'
```

The audit log of every call is available at `$GOOGLE_SHEETS_API_URL/audit/requests` (used for grading).
