# Coinbase Mock API — Test Results

Base URL: `http://localhost:8023` (in docker-compose: `http://coinbase-api:8023`)

## Endpoints covered

| Method | Path                                    | Status   |
|--------|-----------------------------------------|----------|
| GET    | /health                                 | 200      |
| GET    | /v2/user                                | 200      |
| GET    | /v2/accounts                            | 200      |
| GET    | /v2/accounts/{id}                       | 200/404  |
| GET    | /v2/prices/{pair}/spot                  | 200/404  |
| POST   | /v2/accounts/{id}/buys                  | 201/400/404 |
| POST   | /v2/accounts/{id}/sells                 | 201/400/404 |
| GET    | /v2/accounts/{id}/transactions          | 200/404  |

## Seed data summary

- User: `user-orbit-001` (Amelia Ortega), native currency USD
- Accounts: 4 wallets — BTC (`acct-btc-001`, primary), ETH (`acct-eth-002`),
  USD fiat (`acct-usd-003`), SOL (`acct-sol-004`)
- Spot prices: BTC/ETH/SOL in USD plus BTC/ETH in EUR
- Transactions: 7 seeded (buys, a sell, a fiat deposit, one pending ETH buy)

## Notes

- All responses use the Coinbase `{"data": ...}` envelope; list responses
  wrap an array.
- Crypto balances are 8-decimal strings; fiat / `native_balance` are 2-decimal
  USD strings.
- `GET /v2/prices/{pair}/spot` expects a `BASE-QUOTE` pair (e.g. `BTC-USD`);
  unknown pairs return 404.
- `POST .../buys` and `.../sells` price the trade at the current USD spot price,
  mutate the wallet balance, and append a transaction. Selling more than the
  available balance returns 400; an unknown account returns 404.
- Mutations are held in process memory and reset on container restart.
