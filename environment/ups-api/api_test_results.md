# UPS Mock API — Test Results

Base URL: `http://localhost:8096` (in docker-compose: `http://ups-api:8096`)

## Endpoints covered

| Method | Path                                       | Status  |
|--------|--------------------------------------------|---------|
| GET    | /health                                    | 200     |
| POST   | /api/rating/v1/Rate                        | 200/404 |
| POST   | /api/shipments/v1/ship                     | 200/400 |
| GET    | /api/track/v1/details/{trackingNumber}     | 200/404 |

## Seed data summary

- Rates: 8 rate cards across services (Ground 03, 2nd Day Air 02, Next Day Air 01, 3 Day Select 12, Worldwide Express 07) keyed by origin/dest zip, dated 2026-05.
- Shipments: 5 created labels with UPS-style 1Z tracking numbers.
- Tracking: 5 tracking records (Delivered, In Transit, Out For Delivery, Label Created) with latest activity.

## Notes

- `POST /api/rating/v1/Rate` posts `origin_zip`, `dest_zip`, `weight_lb` (optional `service_code`) and returns `{"RateResponse": {...}}`.
- `POST /api/shipments/v1/ship` creates a label, allocates the next 1Z tracking number, and returns `{"ShipmentResponse": {...}}`.
- `GET /api/track/v1/details/{trackingNumber}` returns `{"trackResponse": {"shipment": [...]}}`.
- Charges scale linearly with `weight_lb` relative to the seed weight.
- Mutations (created shipments) are held in process memory and reset on container restart.
