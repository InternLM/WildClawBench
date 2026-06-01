# Google Analytics Mock API — Test Results

Base URL: `http://localhost:8068` (in docker-compose: `http://google-analytics-api:8068`)

## Endpoints covered

| Method | Path                                                  | Status |
|--------|-------------------------------------------------------|--------|
| GET    | /health                                               | 200    |
| GET    | /v1beta/properties/{property_id}                      | 200    |
| GET    | /v1beta/properties/{property_id}/metadata             | 200    |
| POST   | /v1beta/properties/{property_id}:runReport            | 200    |
| POST   | /v1beta/properties/{property_id}:runRealtimeReport    | 200    |
| POST   | /v1beta/properties/{property_id}:batchRunReports      | 200    |

## Seed data summary

- Property: `412233445` (Orbit Labs Website)
- Events dataset: 16 rows across 4 days (2026-05-20..2026-05-23) with dimensions
  date, country, pagePath, deviceCategory and metrics sessions, activeUsers,
  screenPageViews, eventCount
- Realtime dataset: 6 rows with dimensions country, deviceCategory,
  unifiedScreenName and metrics activeUsers, eventCount

## Notes

- `runReport` groups the seed rows by the requested `dimensions` and sums the
  requested `metrics`, returning `{dimensionHeaders, metricHeaders, rows,
  rowCount}`. Unknown dimensions/metrics are ignored; if no valid metric is
  requested the first available metric is used.
- `dateRanges` is accepted and echoed back as metadata but does not filter the
  fixed seed window.
- `batchRunReports` accepts `{requests: [...]}` where each request has the same
  shape as `runReport`; dimensions/metrics may be strings or `{name}` objects.
- `metadata` lists the available dimensions and metrics.
- Mutations are not applicable; this service is read-only over seed data.
