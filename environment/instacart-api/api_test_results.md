# Instacart Mock API — Test Results

Base URL: `http://localhost:8012` (docker-compose: `http://instacart-api:8012`)

## Endpoints

| Method | Path                                  | Status   |
|--------|---------------------------------------|----------|
| GET    | /health                               | 200      |
| GET    | /v1/users/me                          | 200      |
| GET    | /v1/retailers                         | 200      |
| GET    | /v1/retailers/{retailer_id}           | 200/404  |
| GET    | /v1/products                          | 200      |
| GET    | /v1/products/{product_id}             | 200/404  |
| POST   | /v1/carts                             | 201/400  |
| GET    | /v1/carts/{cart_id}                   | 200/404  |
| POST   | /v1/carts/{cart_id}/items             | 200/400  |
| PATCH  | /v1/carts/{cart_id}/items/{product_id}| 200/400  |
| POST   | /v1/carts/{cart_id}/checkout          | 201/400  |
| GET    | /v1/orders                            | 200      |
| GET    | /v1/orders/{order_id}                 | 200/404  |
| POST   | /v1/orders/{order_id}/cancel          | 200/400  |

## Seed data

- Retailers: 5 (Safeway, Whole Foods, Costco, Trader Joe's, CVS)
- Products: 17 across the retailers
- User: `user-emily` (Instacart+)
- Orders: 3 (1 in SHOPPING, 2 DELIVERED)

## Notes

- Carts are held in process memory and live only for the container session.
- `POST /v1/carts/{cart_id}/checkout` will reject carts below the retailer's `min_basket`.
- Cancel only works for orders not in `DELIVERED` or `CANCELLED` state.
