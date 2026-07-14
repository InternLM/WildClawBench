# Mixpanel Mock API — Test Results

Base URL: `http://localhost:8056` (in docker-compose: `http://mixpanel-api:8056`)

## Endpoints covered

| Method | Path                          | Status |
|--------|-------------------------------|--------|
| GET    | /health                       | 200    |
| POST   | /track                        | 200/400 |
| GET    | /api/2.0/events               | 200    |
| GET    | /api/2.0/funnels/list         | 200    |
| GET    | /api/2.0/funnels              | 200/404 |
| GET    | /api/2.0/segmentation         | 200/400 |
| GET    | /api/2.0/engage               | 200    |

## Seed data summary

- Events: 18 events across `Signup`, `App Open`, `Product Viewed`, `Add to Cart`, `Checkout`
  spanning 2025-05-01 to 2025-05-04, each with `country`, `plan`, `platform`, `utm_source`.
- Funnels: 2 (`7461001` Purchase Funnel with 4 steps, `7461002` Activation Funnel with 3 steps).
- Profiles: 5 user profiles with name/email/country/plan/total_events/last_seen.

## Notes

- Mutations (`/track`) are held in process memory and reset on container restart.
- `/api/2.0/events` returns `{data: {series, values}}` with daily counts per event name.
- `/api/2.0/funnels` returns ordered steps plus per-step and overall conversion ratios.
- `/api/2.0/segmentation` breaks an event down by the `on` property (defaults to `$none` bucket
  when the property is missing).
- `/api/2.0/engage` supports a single `prop==value` filter via `where`.
