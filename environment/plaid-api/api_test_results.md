# Plaid Mock API — Test Results

Base URL: `http://localhost:8022` (in docker-compose: `http://plaid-api:8022`)

## Endpoints covered

| Method | Path                        | Status   |
|--------|-----------------------------|----------|
| GET    | /health                     | 200      |
| POST   | /accounts/get               | 200      |
| POST   | /accounts/balance/get       | 200      |
| POST   | /transactions/get           | 200      |
| POST   | /institutions/get_by_id     | 200/404  |
| POST   | /identity/get               | 200      |

## Seed data summary

- Item: `item_orbit_8a1f2c` linked to institution `ins_109512` (Cascade Federal Bank)
- Accounts: 4 — checking (`acc_chk_001`), savings (`acc_sav_002`),
  credit card (`acc_crd_003`), auto loan (`acc_lon_004`)
- Transactions: 30 spanning 2026-04-01 .. 2026-04-29 (last two are `pending`)
- Identity: owner profiles (name/email/phone/address) for the two depository accounts

## Notes

- Plaid uses POST for reads. The mock accepts `client_id` / `secret` /
  `access_token` in every body and ignores them (no auth enforced).
- `/transactions/get` filters by inclusive `start_date` / `end_date`
  (`YYYY-MM-DD`) and paginates via `options.count` (default 100, max 500)
  and `options.offset`. Response includes `total_transactions` for paging.
- Optional `options.account_ids` narrows accounts/transactions/identity to the
  listed accounts.
- Balances are embedded under each account's `balances` object; loan/credit
  accounts may have a `null` available balance.
- `/institutions/get_by_id` returns 404 for an unknown institution id.
