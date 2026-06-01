# DoorDash Mock API — Test Results

Base URL: `http://localhost:8037` (docker-compose: `http://doordash-api:8037`)

## Endpoints

| Method | Path                              | Status   |
|--------|-----------------------------------|----------|
| GET    | /health                           | 200      |
| GET    | /v1/stores                        | 200      |
| GET    | /v1/stores/{store_id}             | 200/404  |
| GET    | /v1/stores/{store_id}/menu        | 200/404  |
| POST   | /v1/carts                         | 201/400  |
| GET    | /v1/carts/{cart_id}               | 200/404  |
| POST   | /v1/carts/{cart_id}/items         | 200/400  |
| POST   | /v1/carts/{cart_id}/checkout      | 201/400  |
| GET    | /v1/orders/{order_id}             | 200/404  |

## Seed data

- Stores: 5 (Japanese, Italian, Mexican, Healthy, Chinese)
- Menu items: 14 across the stores
- Orders: 2 (1 delivered, 1 in_progress) with line items

## Notes

- Carts are held in process memory and live only for the container session.
- Adding an item rejects items from another store or marked unavailable.
- Checkout computes a 10% service fee on the subtotal plus the store delivery fee and tip.
- `?cuisine=` filters stores; `latitude`/`longitude` are accepted but not used for ranking.
