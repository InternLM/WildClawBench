# Google Maps Mock API — Test Results

Base URL: `http://localhost:8033` (in docker-compose: `http://google-maps-api:8033`)

## Endpoints covered

| Method | Path                                     | Status      |
|--------|------------------------------------------|-------------|
| GET    | /health                                  | 200         |
| GET    | /maps/api/place/textsearch/json          | 200         |
| GET    | /maps/api/place/details/json             | 200/404     |
| GET    | /maps/api/place/nearbysearch/json        | 200/400     |
| GET    | /maps/api/geocode/json                   | 200         |
| GET    | /maps/api/directions/json                | 200/404     |
| GET    | /maps/api/distancematrix/json            | 200         |

## Seed data summary

- Places: 10 San Francisco POIs (cafes, restaurants, parks, museums, markets)
  with `place_id`, lat/lng, rating, types, formatted_address, price_level.
- Geocodes: 7 named localities (San Francisco, Union Square, Oakland, etc.)
  for address -> coordinate resolution used by geocode/directions/matrix.

## Notes

- All responses use Google-style `{"status": "OK", "results": [...]}` envelopes.
- Distances are computed locally with the haversine formula (no external libs);
  ground travel applies a 1.3x factor over straight-line distance.
- `nearbysearch` accepts `location` as `lat,lng` or a known place/locality name,
  filters by `radius` (meters) and optional `type`, sorted nearest-first.
- `directions` / `distancematrix` resolve origin/destination from `lat,lng`,
  locality names, place names, or place_ids. `distancematrix` takes `|`-separated
  origins and destinations.
- Mutations are not applicable; this service is read-only.
