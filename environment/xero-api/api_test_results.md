# Xero Mock API — Test Results

Base URL: `http://localhost:8088` (in docker-compose: `http://xero-api:8088`)

## Endpoints covered

| Method | Path                            | Status      |
|--------|---------------------------------|-------------|
| GET    | /health                         | 200         |
| GET    | /api.xro/2.0/Invoices           | 200         |
| GET    | /api.xro/2.0/Invoices/{id}      | 200/404     |
| POST   | /api.xro/2.0/Invoices           | 200/400/404 |
| GET    | /api.xro/2.0/Contacts           | 200         |
| GET    | /api.xro/2.0/Accounts           | 200         |

## Seed data summary

- Invoices: 8 (ACCREC sales + ACCPAY bills) across DRAFT/SUBMITTED/AUTHORISED/PAID with totals, tax, amount due/paid, and 2026-05 dates.
- Contacts: 7 customers and suppliers with name, email, customer/supplier flags, and status.
- Accounts: 8 chart-of-accounts entries (revenue, expense, bank, receivable, payable) with code and type.

## Notes

- Collection responses are wrapped under a PascalCase key like `{"Invoices": [...]}` to match Xero; a single invoice get also returns an `Invoices` array of one.
- `/api.xro/2.0/Invoices` supports `Status` and `Type` filters.
- `POST /api.xro/2.0/Invoices` accepts a Xero envelope (`{"Invoices": [{"Contact": {"ContactID"}, "LineItems": [...]}]}`); SubTotal is summed from line items, tax is computed at 10%. A missing `Contact.ContactID` returns 400, an unknown contact 404.
- Mutations are held in process memory and reset on container restart.
