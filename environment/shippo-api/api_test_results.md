# Shippo Mock API — Test Results

Base URL: `http://localhost:8052` (in docker-compose: `http://shippo-api:8052`)

## Endpoints covered

| Method | Path                                   | Status  |
|--------|----------------------------------------|---------|
| GET    | /health                                | 200     |
| POST   | /addresses                             | 201     |
| GET    | /addresses/{id}                        | 200/404 |
| POST   | /shipments                             | 201/400 |
| GET    | /shipments/{id}                        | 200/404 |
| GET    | /shipments/{id}/rates                  | 200/404 |
| POST   | /transactions                          | 201/400 |
| GET    | /transactions/{id}                     | 200/404 |
| GET    | /tracks/{carrier}/{tracking_number}    | 200/404 |

## Seed data summary

- Addresses: 4 (1 sender + 3 recipients)
- Parcels: 3
- Shipments: 2 (each with carrier rates)
- Rates: 7 across USPS / UPS / FedEx with service levels + amounts
- Transactions (labels): 1 purchased label
- Tracking: histories with PRE_TRANSIT / TRANSIT / DELIVERED statuses

## Notes

- `POST /shipments` returns the shipment object_id plus generated rates across
  USPS / UPS / FedEx. `address_from` / `address_to` / `parcels` accept either an
  existing object_id or an inline object.
- `POST /transactions` buys a label from a rate object_id and returns a
  tracking_number + label_url, seeding an initial PRE_TRANSIT tracking event.
- `GET /tracks/{carrier}/{tracking_number}` returns the latest status plus full
  history ordered newest-first.
- Mutations are held in process memory and reset on container restart.
