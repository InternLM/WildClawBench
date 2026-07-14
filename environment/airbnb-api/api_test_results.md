# Airbnb Mock API — Test Results

Base URL: `http://localhost:8038` (docker-compose: `http://airbnb-api:8038`)

## Endpoints

| Method | Path                                   | Status   |
|--------|----------------------------------------|----------|
| GET    | /health                                | 200      |
| GET    | /v2/listings/search                    | 200      |
| GET    | /v2/listings/{id}                      | 200/404  |
| GET    | /v2/listings/{id}/availability         | 200/404  |
| GET    | /v2/listings/{id}/reviews              | 200/404  |
| POST   | /v2/reservations                       | 201/400/404 |
| GET    | /v2/reservations/{id}                  | 200/404  |
| DELETE | /v2/reservations/{id}                  | 200/400/404 |

## Seed data

- Listings: 8 (SF, Sausalito, Lake Tahoe, Santa Cruz) across entire_home/private_room
- Hosts: 3 (2 superhosts)
- Availability windows: 9 (lst-102 has a blocked second half of June)
- Reviews: 7

## Notes

- Reservations are held in process memory and reset on container restart.
- `search` accepts `location`, `checkin`/`checkout` (ISO dates), `guests`,
  `min_price`, `max_price`. When checkin+checkout are supplied, only listings
  available for that window are returned.
- Reservation create validates date order, guest count against `max_guests`,
  and availability before confirming. Total = nightly subtotal + cleaning fee
  + a 14% service fee.
