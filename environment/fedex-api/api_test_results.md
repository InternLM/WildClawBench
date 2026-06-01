# FedEx Mock API — Test Results

Base URL: `http://localhost:8095` (in docker-compose: `http://fedex-api:8095`)

## Endpoints covered

| Method | Path                          | Status  |
|--------|-------------------------------|---------|
| GET    | /health                       | 200     |
| POST   | /rate/v1/rates/quotes         | 200/404 |
| POST   | /ship/v1/shipments            | 200/400 |
| POST   | /track/v1/trackingnumbers     | 200/404 |

## Seed data summary

- Rates: 8 rate cards across services (Ground, 2Day, Standard/Priority Overnight, Express Saver, International Priority) keyed by origin/dest zip, dated 2026-05.
- Shipments: 5 created labels with FedEx-style 12-digit tracking numbers.
- Tracking: 5 tracking records (Delivered, In transit, Out for delivery, Picked up) with latest scan events.

## Notes

- `POST /rate/v1/rates/quotes` posts `origin_zip`, `dest_zip`, `weight_lb` (optional `service_type`) and returns `{"output": {"rateReplyDetails": [...]}}`.
- `POST /ship/v1/shipments` creates a label, allocates the next tracking number, and returns `{"output": {"transactionShipments": [...]}}`.
- `POST /track/v1/trackingnumbers` posts `tracking_number` and returns `{"output": {"completeTrackResults": [...]}}`.
- Charges scale linearly with `weight_lb` relative to the seed weight.
- Mutations (created shipments) are held in process memory and reset on container restart.
