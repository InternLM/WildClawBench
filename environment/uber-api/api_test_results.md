# Uber Mock API — Test Results

Base URL: `http://localhost:8036` (docker-compose: `http://uber-api:8036`)

## Endpoints

| Method | Path                            | Status   |
|--------|---------------------------------|----------|
| GET    | /health                         | 200      |
| GET    | /v1.2/products                  | 200      |
| GET    | /v1.2/products/{product_id}     | 200/404  |
| GET    | /v1.2/estimates/price           | 200      |
| GET    | /v1.2/estimates/time            | 200      |
| POST   | /v1.2/requests                  | 201/404  |
| GET    | /v1.2/requests/{request_id}     | 200/404  |
| DELETE | /v1.2/requests/{request_id}     | 200/400  |
| GET    | /v1.2/history                   | 200      |
| GET    | /v1.2/me                        | 200      |

## Seed data

- Products: 4 (UberX, UberXL, Uber Black, Uber Pool) with base/per-mile/per-minute pricing
- Rider: `rider-marco` (Marco Reyes, rating 4.91)
- Trips: 5 (4 completed history rides + 1 rider-canceled)

## Notes

- Price estimates use the haversine great-circle distance between start/end
  coordinates (no external libraries) and assume an ~18 mph average for duration.
- Time estimates return a deterministic pickup ETA in seconds per product tier.
- Ride requests and cancellations are held in process memory and reset on restart.
- `GET /v1.2/history` returns only completed trips, newest first.
